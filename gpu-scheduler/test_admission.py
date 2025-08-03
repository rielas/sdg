import unittest
from admission_webhook import get_annotation, get_index

EVENT = {
    "kind": "AdmissionReview",
    "apiVersion": "admission.k8s.io/v1",
    "request": {
        "uid": "08ff0c88-656d-4f61-ac08-45ffad527399",
        "kind": {"group": "", "version": "v1", "kind": "Pod"},
        "resource": {"group": "", "version": "v1", "resource": "pods"},
        "requestKind": {"group": "", "version": "v1", "kind": "Pod"},
        "requestResource": {"group": "", "version": "v1", "resource": "pods"},
        "name": "gpu-scheduler-check-2",
        "namespace": "default",
        "operation": "CREATE",
        "userInfo": {
            "username": "system:serviceaccount:kube-system:statefulset-controller",
            "uid": "a5c16a56-d792-4f3a-b291-3df8acbd9420",
            "groups": [
                "system:serviceaccounts",
                "system:serviceaccounts:kube-system",
                "system:authenticated",
            ],
            "extra": {
                "authentication.kubernetes.io/credential-id": [
                    "JTI=e9f0bde3-2b2f-4913-87a5-b0131b7e87fc"
                ]
            },
        },
        "object": {
            "kind": "Pod",
            "apiVersion": "v1",
            "metadata": {
                "name": "gpu-scheduler-check-2",
                "generateName": "gpu-scheduler-check-",
                "namespace": "default",
                "creationTimestamp": None,
                "labels": {
                    "app": "gpu-scheduler-check",
                    "apps.kubernetes.io/pod-index": "2",
                    "controller-revision-hash": "gpu-scheduler-check-77b4864975",
                    "statefulset.kubernetes.io/pod-name": "gpu-scheduler-check-2",
                },
                "annotations": {
                    "gpu-scheduling-map": "0=node1:0,1\n1=node2:2\n2=node3:0,1,2\n3=node4:3\n4=node4:3\n"
                },
                "ownerReferences": [
                    {
                        "apiVersion": "apps/v1",
                        "kind": "StatefulSet",
                        "name": "gpu-scheduler-check",
                        "uid": "245057f3-4519-4d99-ad2a-82a9c51982d3",
                        "controller": True,
                        "blockOwnerDeletion": True,
                    }
                ],
                "managedFields": [
                    {
                        "manager": "kube-controller-manager",
                        "operation": "Update",
                        "apiVersion": "v1",
                        "time": "2025-08-03T15:30:04Z",
                        "fieldsType": "FieldsV1",
                        "fieldsV1": {
                            "f:metadata": {
                                "f:annotations": {".": {}, "f:gpu-scheduling-map": {}},
                                "f:generateName": {},
                                "f:labels": {
                                    ".": {},
                                    "f:app": {},
                                    "f:apps.kubernetes.io/pod-index": {},
                                    "f:controller-revision-hash": {},
                                    "f:statefulset.kubernetes.io/pod-name": {},
                                },
                                "f:ownerReferences": {
                                    ".": {},
                                    'k:{"uid":"245057f3-4519-4d99-ad2a-82a9c51982d3"}': {},
                                },
                            },
                            "f:spec": {
                                "f:containers": {
                                    'k:{"name":"gpu-check"}': {
                                        ".": {},
                                        "f:args": {},
                                        "f:command": {},
                                        "f:env": {
                                            ".": {},
                                            'k:{"name":"NODE_NAME"}': {
                                                ".": {},
                                                "f:name": {},
                                                "f:valueFrom": {
                                                    ".": {},
                                                    "f:fieldRef": {},
                                                },
                                            },
                                        },
                                        "f:image": {},
                                        "f:imagePullPolicy": {},
                                        "f:name": {},
                                        "f:resources": {},
                                        "f:terminationMessagePath": {},
                                        "f:terminationMessagePolicy": {},
                                    }
                                },
                                "f:dnsPolicy": {},
                                "f:enableServiceLinks": {},
                                "f:hostname": {},
                                "f:restartPolicy": {},
                                "f:schedulerName": {},
                                "f:securityContext": {},
                                "f:subdomain": {},
                                "f:terminationGracePeriodSeconds": {},
                            },
                        },
                    }
                ],
            },
            "spec": {
                "volumes": [
                    {
                        "name": "kube-api-access-tc6gn",
                        "projected": {
                            "sources": [
                                {
                                    "serviceAccountToken": {
                                        "expirationSeconds": 3607,
                                        "path": "token",
                                    }
                                },
                                {
                                    "configMap": {
                                        "name": "kube-root-ca.crt",
                                        "items": [{"key": "ca.crt", "path": "ca.crt"}],
                                    }
                                },
                                {
                                    "downwardAPI": {
                                        "items": [
                                            {
                                                "path": "namespace",
                                                "fieldRef": {
                                                    "apiVersion": "v1",
                                                    "fieldPath": "metadata.namespace",
                                                },
                                            }
                                        ]
                                    }
                                },
                            ],
                            "defaultMode": 420,
                        },
                    }
                ],
                "containers": [
                    {
                        "name": "gpu-check",
                        "image": "bash",
                        "command": ["bash"],
                        "args": [
                            "-c",
                            'while true; do\n  echo "Node Name: $NODE_NAME"\n  echo "CUDA_VISIBLE_DEVICES: $CUDA_VISIBLE_DEVICES"\n  echo "---"\n  sleep 5\ndone\n',
                        ],
                        "env": [
                            {
                                "name": "NODE_NAME",
                                "valueFrom": {
                                    "fieldRef": {
                                        "apiVersion": "v1",
                                        "fieldPath": "spec.nodeName",
                                    }
                                },
                            }
                        ],
                        "resources": {},
                        "volumeMounts": [
                            {
                                "name": "kube-api-access-tc6gn",
                                "readOnly": True,
                                "mountPath": "/var/run/secrets/kubernetes.io/serviceaccount",
                            }
                        ],
                        "terminationMessagePath": "/dev/termination-log",
                        "terminationMessagePolicy": "File",
                        "imagePullPolicy": "Always",
                    }
                ],
                "restartPolicy": "Always",
                "terminationGracePeriodSeconds": 30,
                "dnsPolicy": "ClusterFirst",
                "serviceAccountName": "default",
                "serviceAccount": "default",
                "securityContext": {},
                "hostname": "gpu-scheduler-check-2",
                "subdomain": "gpu-scheduler-check",
                "schedulerName": "gpu-scheduler",
                "tolerations": [
                    {
                        "key": "node.kubernetes.io/not-ready",
                        "operator": "Exists",
                        "effect": "NoExecute",
                        "tolerationSeconds": 300,
                    },
                    {
                        "key": "node.kubernetes.io/unreachable",
                        "operator": "Exists",
                        "effect": "NoExecute",
                        "tolerationSeconds": 300,
                    },
                ],
                "priority": 0,
                "enableServiceLinks": True,
                "preemptionPolicy": "PreemptLowerPriority",
            },
            "status": {},
        },
        "oldObject": None,
        "dryRun": False,
        "options": {"kind": "CreateOptions", "apiVersion": "meta.k8s.io/v1"},
    },
}


class TestAnnotation(unittest.TestCase):
    def test_get_annotation(self):
        pod = EVENT["request"]["object"]
        self.assertEqual(
            get_annotation(pod),
            "0=node1:0,1\n1=node2:2\n2=node3:0,1,2\n3=node4:3\n4=node4:3\n",
        )

    def test_get_index(self):
        pod = EVENT["request"]["object"]
        self.assertEqual(get_index(pod), "2")


if __name__ == "__main__":
    unittest.main()
