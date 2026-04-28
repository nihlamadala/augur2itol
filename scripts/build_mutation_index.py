#!/usr/bin/env python3
import argparse, json, re
from collections import defaultdict

AA_RE = re.compile(r"^[A-Z\*]?(\d+)[A-Z\*]?$")

def walk(node):
    yield node
    for c in node.get("children", []) or []:
        yield from walk(c)

def parse_pos(mut):
    # mut like S145N
    m = AA_RE.match(mut)
    return int(m.group(1)) if m else None

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True, help="Auspice JSON")
    ap.add_argument("--output", required=True, help="Output mutations_index.json")
    ap.add_argument("--gene", default="HA", help="Gene name for aa mutations")
    args = ap.parse_args()

    j = json.load(open(args.input))
    tree = j["tree"]

    out = {}
    for n in walk(tree):
        nid = n.get("name")
        if not nid:
            continue
        aa = (((n.get("branch_attrs") or {}).get("mutations") or {}).get(args.gene) or [])
        positions = []
        aa_full = []
        for m in aa:
            aa_full.append(f"{args.gene}:{m}")
            p = parse_pos(m)
            if p is not None:
                positions.append(p)
        out[nid] = {"aa_mutations": aa_full, "residue_positions": sorted(set(positions)), "gene": args.gene}

    with open(args.output, "w") as f:
        json.dump(out, f, indent=2)

    print(f"Wrote {args.output} with {len(out)} nodes")

if __name__ == "__main__":
    main()