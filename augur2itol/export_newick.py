def _escape_name(name: str) -> str:
    return str(name).replace(" ", "_")


def to_newick(node) -> str:
    name = _escape_name(node.get("name", ""))

    children = node.get("children", []) or []
    if not children:
        return name

    inner = ",".join(to_newick(ch) for ch in children)
    return f"({inner}){name}"