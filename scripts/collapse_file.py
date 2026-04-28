#!/usr/bin/env python3
import argparse
import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple


def get_attr_value(node: Dict[str, Any], attr: str) -> Optional[str]:
    node_attrs = node.get("node_attrs", {}) or {}
    entry = node_attrs.get(attr)
    if isinstance(entry, dict):
        value = entry.get("value")
        if value is not None:
            return str(value)
    return None


def is_match(node: Dict[str, Any], attr: str, value: str) -> bool:
    return get_attr_value(node, attr) == value


def get_node_id(node: Dict[str, Any]) -> Optional[str]:
    return node.get("name")


def collect_matches(node: Dict[str, Any], attr: str, value: str) -> Tuple[bool, Set[str]]:
    """
    Returns:
        (subtree_has_match, collapse_candidates)

    subtree_has_match: True if any descendant leaf matches the condition
    collapse_candidates: internal node IDs that can be collapsed
    """
    children = node.get("children", []) or []

    # Leaf node
    if not children:
        return is_match(node, attr, value), set()

    subtree_has_match = False
    collapse_candidates: Set[str] = set()

    for child in children:
        child_has_match, child_candidates = collect_matches(child, attr, value)
        if child_has_match:
            subtree_has_match = True
        collapse_candidates.update(child_candidates)

    node_id = get_node_id(node)

    # If this whole subtree has no matching descendants, collapse this internal node
    if not subtree_has_match and node_id:
        collapse_candidates.add(node_id)

    return subtree_has_match, collapse_candidates


def generate_collapse_dataset(tree: Dict[str, Any], attr: str, value: str) -> List[str]:
    """
    Produce iTOL COLLAPSE dataset lines.
    """
    _, candidates = collect_matches(tree, attr, value)

    lines = []
    lines.append("COLLAPSE")
    lines.append("SEPARATOR\tTAB")
    lines.append(f"DATASET_LABEL\tCollapsed nodes for {attr}={value}")
    lines.append("COLOR\t#808080")
    lines.append("DATA")

    for node_id in sorted(candidates):
        lines.append(node_id)

    return lines


def main():
    parser = argparse.ArgumentParser(description="Generate iTOL COLLAPSE dataset from Auspice JSON.")
    parser.add_argument("--input", required=True, help="Input Auspice JSON file")
    parser.add_argument("--output", required=True, help="Output COLLAPSE dataset file")
    parser.add_argument("--attr", required=True, help="Attribute to match, e.g. country or clade")
    parser.add_argument("--value", required=True, help="Value to keep, e.g. UAE or 21A")

    args = parser.parse_args()

    input_path = Path(args.input)
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with input_path.open("r", encoding="utf-8") as f:
        data = json.load(f)

    if "tree" not in data:
        raise SystemExit("Error: input JSON does not contain a 'tree' key.")

    tree = data["tree"]
    lines = generate_collapse_dataset(tree, args.attr, args.value)

    with output_path.open("w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")

    print(f"Wrote collapse dataset to: {output_path}")
    print(f"Condition: {args.attr}={args.value}")
    print("Now upload this file to iTOL as a COLLAPSE dataset.")


if __name__ == "__main__":
    main()