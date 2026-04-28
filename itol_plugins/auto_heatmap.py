def _get_num(node, key):
    na = (node.get("node_attrs") or {})
    entry = na.get(key) or {}
    if isinstance(entry, dict):
        v = entry.get("value")
        try:
            return float(v)
        except Exception:
            return None
    return None

def generate(ctx):
    import os
    leaves = ctx["leaves"]

    attr = os.getenv("ITOL_HEATMAP_ATTR", "num_date").strip() or "num_date"
    label = os.getenv("ITOL_HEATMAP_LABEL", f"{attr} heatmap").strip() or f"{attr} heatmap"
    color = os.getenv("ITOL_HEATMAP_COLOR", "#3b6fb6").strip() or "#3b6fb6"

    rows = []
    for lf in leaves:
        nid = lf.get("name")
        if not nid:
            continue
        v = _get_num(lf, attr)
        if v is None:
            continue
        rows.append((nid, v))

    lines = []
    lines.append("DATASET_HEATMAP")
    lines.append("SEPARATOR\tTAB")
    lines.append(f"DATASET_LABEL\t{label}")
    lines.append("COLOR\t#000000")
    lines.append(f"FIELD_LABELS\t{attr}")
    lines.append(f"FIELD_COLORS\t{color}")
    lines.append("DATA")

    for nid, v in rows:
        lines.append(f"{nid}\t{v}")

    return {f"dataset_heatmap_{attr}.txt": "\n".join(lines) + "\n"}