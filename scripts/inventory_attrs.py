#!/usr/bin/env python3
import json, argparse
from collections import defaultdict

def walk(node):
    yield node
    for c in node.get("children", []) or []:
        yield from walk(c)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", required=True)
    args = ap.parse_args()

    data = json.load(open(args.json, "r", encoding="utf-8"))
    tree = data["tree"]

    node_attr_keys = defaultdict(int)
    branch_attr_keys = defaultdict(int)

    for n in walk(tree):
        na = n.get("node_attrs", {}) or {}
        ba = n.get("branch_attrs", {}) or {}

        for k in na.keys():
            node_attr_keys[k] += 1
        for k in ba.keys():
            branch_attr_keys[k] += 1

        # also drill into branch_attrs.mutations
        muts = ba.get("mutations")
        if isinstance(muts, dict):
            for mk in muts.keys():
                branch_attr_keys[f"mutations.{mk}"] += 1

    print("NODE_ATTRS:")
    for k,v in sorted(node_attr_keys.items()):
        print(f"{k}\t{v}")

    print("\nBRANCH_ATTRS:")
    for k,v in sorted(branch_attr_keys.items()):
        print(f"{k}\t{v}")

if __name__ == "__main__":
    main()