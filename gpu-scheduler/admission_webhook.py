from flask import Flask, request, jsonify
import base64
import json
import logging
import annotation

logging.basicConfig(level=logging.DEBUG)
logging.info("Starting admission webhook server...")

scheduler_name = "gpu-scheduler"


def get_annotation(pod: dict) -> str | None:
    return pod.get("metadata", {}).get("annotations", {}).get("gpu-scheduling-map")


def get_index(pod: dict) -> str | None:
    return pod.get("metadata", {}).get("labels", {}).get("apps.kubernetes.io/pod-index")


app = Flask(__name__)


@app.before_request
def log_request():
    logging.info(f"Incoming request: {request.method} {request.url}")


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "healthy"}), 200


@app.route("/mutate", methods=["POST"])
def mutate():
    logging.info("Received a mutation request")
    logging.debug(f"Request headers: {dict(request.headers)}")
    logging.debug(f"Request body: {request.data.decode('utf-8')}")
    req = request.get_json()
    pod = req["request"]["object"]
    uid = req["request"]["uid"]

    if pod.get("spec", {}).get("schedulerName", "") != scheduler_name:
        admission_response = {
            "apiVersion": "admission.k8s.io/v1",
            "kind": "AdmissionReview",
            "response": {"uid": uid, "allowed": True},
        }

        return jsonify(admission_response)

    patch = []
    annotation_text = get_annotation(pod)

    if annotation_text:
        logging.info(f"Using annotation: {annotation_text}")
        annotation_obj = annotation.Annotation(annotation_text)
        index = get_index(pod)
        placement = annotation_obj.get_placement(index)

        for i, _ in enumerate(pod.get("spec", {}).get("containers", [])):
            patch.append(
                {
                    "op": "add",
                    "path": f"/spec/containers/{i}/env/-",
                    "value": {
                        "name": "CUDA_VISIBLE_DEVICES",
                        "value": placement.cuda_visible_devices,
                    },
                }
            )

    patch_bytes = json.dumps(patch).encode("utf-8")
    patch_b64 = base64.b64encode(patch_bytes).decode("utf-8")

    admission_response = {
        "apiVersion": "admission.k8s.io/v1",
        "kind": "AdmissionReview",
        "response": {
            "uid": uid,
            "allowed": True,
            "patchType": "JSONPatch",
            "patch": patch_b64,
        },
    }

    return jsonify(admission_response)


@app.errorhandler(404)
def not_found(error):
    logging.warning(f"404 Not Found: {request.path}")
    return jsonify({"error": "Not found", "path": request.path}), 404


@app.errorhandler(405)
def method_not_allowed(error):
    logging.warning(f"405 Method Not Allowed: {request.method} {request.path}")
    return (
        jsonify(
            {
                "error": "Method not allowed",
                "method": request.method,
                "path": request.path,
            }
        ),
        405,
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=443, ssl_context=("/app/tls.crt", "/app/tls.key"))
