import unittest
from annotation import Placement, Annotation


class TestPlacement(unittest.TestCase):
    def test_fields(self):
        p = Placement(node_name="nodeX", cuda_visible_devices="0,1")
        self.assertEqual(p.node_name, "nodeX")
        self.assertEqual(p.cuda_visible_devices, "0,1")


class TestAnnotation(unittest.TestCase):
    def test_get_placement(self):
        annotation = Annotation(
            """
0=node1:0,1
1=node2:2
2=node3:0,1,2
3=node4:3
4=node4:3
"""
        )
        self.assertEqual(
            annotation.get_placement("0"),
            Placement(node_name="node1", cuda_visible_devices="0,1"),
        )
        self.assertEqual(
            annotation.get_placement("4"),
            Placement(node_name="node4", cuda_visible_devices="3"),
        )
        self.assertEqual(
            annotation.get_placement("2"),
            Placement(node_name="node3", cuda_visible_devices="0,1,2"),
        )


if __name__ == "__main__":
    unittest.main()
