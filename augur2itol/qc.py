def _get_attr_value(node, key: str) -> str:
    attrs = node.get("node_attrs", {}) or {}
    obj = attrs.get(key)
    if isinstance(obj, dict):
        return obj.get("value") or ""
    return ""


def write_qc_report(leaves, outpath):
    total = len(leaves)
    missing_region = 0

    for leaf in leaves:
        region = _get_attr_value(leaf, "region")
        if not region:
            missing_region += 1

    lines = [
        "metric\tvalue",
        f"tips_total\t{total}",
        f"tips_missing_region\t{missing_region}",
    ]
    outpath.write_text("\n".join(lines) + "\n", encoding="utf-8")