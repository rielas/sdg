from dataclasses import dataclass


@dataclass
class Placement:
    node_name: str
    cuda_visible_devices: str

    @property
    def node(self) -> str:
        return self.node_name

    @property
    def cuda(self) -> str:
        return self.cuda_visible_devices


class Annotation:
    def __init__(self, text: str):
        self.mapping = {}

        for line in text.strip().splitlines():
            if not line.strip():
                continue

            idx, rest = line.split("=")
            node, devices = rest.split(":")
            self.mapping[idx.strip()] = Placement(
                node_name=node.strip(), cuda_visible_devices=devices.strip()
            )

    def get_placement(self, index: str) -> Placement:
        return self.mapping[index]

    def get_node_name(self, index: str) -> str:
        if index not in self.mapping:
            raise ValueError(f"Index {index} not found in annotation mapping.")
        return self.mapping[index].node_name

    def get_cuda_variable(self, index: str) -> str:
        if index not in self.mapping:
            raise ValueError(f"Index {index} not found in annotation mapping.")
        return self.mapping[index].cuda_visible_devices


default = Annotation(
    """
0=node1:0,1
1=node2:2
2=node3:0,1,2
3=node4:3
4=node4:3
"""
)
