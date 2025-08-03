import logging
import json
from kubernetes import client, config, watch
import annotation
from annotation import Placement

logging.basicConfig(level=logging.DEBUG)
logging.info("Loading Kubernetes configuration...")

config.load_incluster_config()
v1 = client.CoreV1Api()
scheduler_name = "gpu-scheduler"


def schedule(name: str, index: str, placement: Placement, namespace: str = "default"):
    logging.debug(f"Scheduling pod with index {index}")
    target = client.V1ObjectReference()
    target.kind = "Node"
    target.apiVersion = "v1"
    node_name = placement.node_name

    assert node_name is not None

    logging.info(f"Target node for pod {name} is {node_name}")
    target.name = node_name

    meta = client.V1ObjectMeta()
    meta.name = name

    body = client.V1Binding(metadata=meta, target=target)

    try:
        binding_result = v1.create_namespaced_binding(namespace, body)
    except ValueError as e:
        logging.error(f"Failed to bind pod {name} to node {node_name}: {e}")
        return None

    return binding_result


def get_index(pod) -> str:
    return pod.metadata.labels.get("apps.kubernetes.io/pod-index", "")


def get_annotation(pod: client.V1Pod) -> str | None:
    return pod.metadata.annotations.get("gpu-scheduling-map")


def main():
    logging.info(f"{scheduler_name} started!")
    w = watch.Watch()

    for event in w.stream(v1.list_namespaced_pod, "default"):
        logging.debug(f"Event: {event['type']} {event['object'].metadata.name}")

        if (
            event["object"].status.phase == "Pending"
            and event["object"].spec.scheduler_name == scheduler_name
        ):
            try:
                logging.info("Scheduling " + event["object"].metadata.name)
                index = get_index(event["object"])
                annotation_text = get_annotation(event["object"])

                if annotation_text:
                    logging.info(f"Using annotation: {annotation_text}")
                    annotation_obj = annotation.Annotation(annotation_text)
                    placement = annotation_obj.get_placement(index)
                    schedule(event["object"].metadata.name, index, placement)
            except client.rest.ApiException as e:
                logging.error(json.loads(e.body)["message"])


if __name__ == "__main__":
    main()
