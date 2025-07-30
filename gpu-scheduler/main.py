import logging
import json
from dataclasses import dataclass
from kubernetes import client, config, watch

logging.basicConfig(level=logging.DEBUG)
logging.info("Loading Kubernetes configuration...")

config.load_incluster_config()
v1 = client.CoreV1Api()
scheduler_name = "gpu-scheduler"


@dataclass
class Placement:
    node_name: str
    cuda_visible_devices: str


PLACEMENT_MAP: dict[str, Placement] = {
    "0": Placement(node_name="node1", cuda_visible_devices="0,1"),
    "1": Placement(node_name="node2", cuda_visible_devices="2"),
    "2": Placement(node_name="node3", cuda_visible_devices="0,1,2"),
    "3": Placement(node_name="node4", cuda_visible_devices="3"),
    "4": Placement(node_name="node4", cuda_visible_devices="3"),
}


def nodes_available() -> list[str]:
    ready_nodes = []

    for n in v1.list_node().items:
        for status in n.status.conditions:
            if status.status == "True" and status.type == "Ready":
                ready_nodes.append(n.metadata.name)

    return ready_nodes


def get_node_name(index: str) -> str:
    if index not in PLACEMENT_MAP:
        raise ValueError(f"Index {index} not found in placement map.")

    return PLACEMENT_MAP[index].node_name


def schedule(name: str, index: str, namespace: str = "default"):
    logging.debug(f"Scheduling pod with index {index}")
    target = client.V1ObjectReference()
    target.kind = "Node"
    target.apiVersion = "v1"
    node_name = get_node_name(index)
    logging.info(f"Target node for pod {name} is {node_name}")
    target.name = node_name

    meta = client.V1ObjectMeta()
    meta.name = name

    body = client.V1Binding(metadata=meta, target=target)

    return v1.create_namespaced_binding(namespace, body)


def get_index(pod) -> str:
    return pod.metadata.labels.get("apps.kubernetes.io/pod-index", "")


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
                _ = schedule(event["object"].metadata.name, index)
            except client.rest.ApiException as e:
                logging.error(json.loads(e.body)["message"])


if __name__ == "__main__":
    main()
