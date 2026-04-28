from collections import OrderedDict

def _get_attr_value(node, key, default="NA"):
    na = (node.get("node_attrs") or {})
    entry = na.get(key) or {}
    if isinstance(entry, dict):
        v = entry.get("value", default)
        if v is None or str(v).strip() == "":
            return default
        return str(v)
    return default

def generate(ctx):
    """
    Symbol dataset with category-specific shapes for interpretability.
    Default mapping (for ARI.SARI):
      ARI  -> circle
      SARI -> square
      NA   -> triangle
    """
    import os

    leaves = ctx["leaves"]
    attr_key = os.getenv("ITOL_SYMBOL_ATTR", "ARI.SARI").strip() or "ARI.SARI"
    ds_label = os.getenv("ITOL_SYMBOL_LABEL", f"{attr_key} symbols").strip()
    legend_title = os.getenv("ITOL_SYMBOL_TITLE", attr_key).strip()
    size = os.getenv("ITOL_SYMBOL_SIZE", "4").strip()  # slightly larger

    # iTOL symbol codes (commonly used):
    # 1 circle, 2 square, 3 triangle, 4 star, etc. (template-dependent but these are standard)
    shape_map = {
        "ARI": "1",    # circle
        "SARI": "2",   # square
        "NA": "3",     # triangle
    }

    color_map = {
        "ARI": "#1f77b4",   # blue
        "SARI": "#d62728",  # red
        "NA": "#9e9e9e",    # gray
    }

    # collect categories in stable order
    categories = OrderedDict()
    rows = []

    for leaf in leaves:
        nid = leaf.get("name")
        if not nid:
            continue
        val = _get_attr_value(leaf, attr_key, default="NA")
        if val not in categories:
            categories[val] = True
        rows.append((nid, val))

    # fallback for unseen categories
    fallback_shapes = ["4", "5", "6", "7", "8"]
    fallback_colors = ["#2ca02c", "#9467bd", "#ff7f0e", "#17becf", "#8c564b"]
    unk_idx = 0

    assigned_shape = {}
    assigned_color = {}

    for cat in categories.keys():
        c = cat.upper()
        if c in shape_map:
            assigned_shape[cat] = shape_map[c]
            assigned_color[cat] = color_map[c]
        else:
            assigned_shape[cat] = fallback_shapes[unk_idx % len(fallback_shapes)]
            assigned_color[cat] = fallback_colors[unk_idx % len(fallback_colors)]
            unk_idx += 1

    lines = []
    lines.append("DATASET_SYMBOL")
    lines.append("SEPARATOR\tTAB")
    lines.append(f"DATASET_LABEL\t{ds_label}")
    lines.append("COLOR\t#000000")
    lines.append(f"LEGEND_TITLE\t{legend_title}")

    legend_shapes = [assigned_shape[c] for c in categories.keys()]
    legend_colors = [assigned_color[c] for c in categories.keys()]
    legend_labels = [str(c) for c in categories.keys()]

    lines.append("LEGEND_SHAPES\t" + "\t".join(legend_shapes))
    lines.append("LEGEND_COLORS\t" + "\t".join(legend_colors))
    lines.append("LEGEND_LABELS\t" + "\t".join(legend_labels))

    lines.append("DATA")
    # ID SHAPE SIZE COLOR FILL POSITION LABEL
    for nid, val in rows:
        sh = assigned_shape[val]
        col = assigned_color[val]
        lines.append(f"{nid}\t{sh}\t{size}\t{col}\t1\t1\t{val}")

    filename = f"dataset_symbol_{attr_key}.txt"
    return {filename: "\n".join(lines) + "\n"}