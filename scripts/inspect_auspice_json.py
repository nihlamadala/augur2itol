import json
from pathlib import Path
from collections import Counter

p = Path("Example/auspice.json")
j = json.loads(p.read_text(encoding="utf-8"))

print("Top-level keys:", sorted(j.keys()))

tree = j.get("tree") or j.get("data", {}).get("tree")
print("Has tree?", bool(tree))
if not tree:
    raise SystemExit("Could not find tree at j['tree'] or j['data']['tree'].")

def walk(n):
    yield n
    for c in n.get("children", []) or []:
        yield from walk(c)

nodes = list(walk(tree))
print("Node count:", len(nodes))

node_attr_keys = Counter()
example_attrs = {}

for n in nodes:
    na = n.get("node_attrs") or {}
    for k, v in na.items():
        node_attr_keys[k] += 1
        if k not in example_attrs:
            example_attrs[k] = v

print("\nMost common node_attrs keys (top 30):")
for k, c in node_attr_keys.most_common(30):
    print(f"  {k}: {c}")

cand = [k for k in example_attrs.keys() if any(x in k.lower() for x in ["country","region","location","division","state"])]
print("\nCandidate location attrs:", cand)

def preview(v):
    if isinstance(v, dict):
        keys = sorted(v.keys())
        head = {k: v[k] for k in keys[:8]}
        return {"keys": keys, "head": head}
    return type(v).__name__

print("\nPreview candidate location attr payloads:")
for k in cand[:10]:
    print(f"\n[{k}] ->", preview(example_attrs[k]))

prob_like = []
for k, v in example_attrs.items():
    if isinstance(v, dict):
        ks = set(v.keys())
        if any(x in ks for x in ["confidence", "prob", "probs", "confidence_by_state", "entropy"]):
            prob_like.append(k)
print("\nnode_attrs with prob/conf-like keys:", prob_like)

mut_counts = Counter()
for n in nodes:
    m = n.get("branch_attrs") or {}
    for k in m.keys():
        mut_counts[k] += 1

print("\nbranch_attrs keys (mutations etc.) top 20:")
for k, c in mut_counts.most_common(20):
    print(f"  {k}: {c}")
