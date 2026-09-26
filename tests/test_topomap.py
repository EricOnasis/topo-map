import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from topomap import build_mermaid, parse_neighbor_output

SAMPLE_OUTPUT = (
    ' 0 interface=ether1 address=192.168.88.2 mac-address=AA:BB:CC:DD:EE:FF '
    'identity="core-router" platform="MikroTik" board="CCR2004" version="7.15.2"\n'
    ' 1 interface=ether2 address=192.168.88.5 mac-address=11:22:33:44:55:66 '
    'identity="branch-switch" platform="MikroTik"\n'
)


class ParseNeighborTests(unittest.TestCase):
    def test_parses_all_entries(self):
        neighbors = parse_neighbor_output(SAMPLE_OUTPUT)
        self.assertEqual(len(neighbors), 2)
        self.assertEqual(neighbors[0], {"interface": "ether1", "address": "192.168.88.2",
                                         "identity": "core-router"})

    def test_entry_without_identity_is_skipped(self):
        line = ' 0 interface=ether1 address=192.168.88.2 identity=""\n'
        self.assertEqual(parse_neighbor_output(line), [])

    def test_empty_output(self):
        self.assertEqual(parse_neighbor_output(""), [])


class MermaidTests(unittest.TestCase):
    def test_basic_edge(self):
        edges = [{"from": "core", "to": "branch", "interface": "ether1", "address": "x"}]
        out = build_mermaid(edges)
        self.assertIn("graph LR", out)
        self.assertIn('core["core"] -- "ether1" --> branch["branch"]', out)

    def test_symmetric_link_is_deduplicated(self):
        edges = [
            {"from": "core", "to": "branch", "interface": "ether1", "address": "x"},
            {"from": "branch", "to": "core", "interface": "ether1", "address": "y"},
        ]
        out = build_mermaid(edges)
        self.assertEqual(out.count("-->"), 1)

    def test_names_with_spaces_get_sanitized_ids(self):
        edges = [{"from": "core router", "to": "branch switch", "interface": "ether1", "address": "x"}]
        out = build_mermaid(edges)
        self.assertIn('core_router["core router"]', out)
        self.assertIn('branch_switch["branch switch"]', out)


if __name__ == "__main__":
    unittest.main()
