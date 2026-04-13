import json


def load_auspice_tree(path):
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    if "tree" not in data:
        raise ValueError("Missing top-level 'tree' key. This may not be an Auspice JSON.")
    return data["tree"]


def iter_nodes(node):
    yield node
    for child in node.get("children", []) or []:
        yield from iter_nodes(child)


def is_leaf(node):
    return not (node.get("children") or [])