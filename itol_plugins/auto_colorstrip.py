from collections import OrderedDict, Counter

def _get_attr_value(node, key, default="NA"):
    na = (node.get("node_attrs") or {})
    entry = na.get(key) or {}
    if isinstance(entry, dict):
        v = entry.get("value", default)
        if v is None or str(v).strip() == "":
            return default
        return str(v)
    return default

def _palette():
    return [
        "#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd",
        "#8c564b", "#e377c2", "#7f7f7f", "#bcbd22", "#17becf",
        "#393b79", "#637939", "#8c6d31", "#843c39", "#7b4173",
        "#3182bd", "#31a354", "#756bb1", "#636363", "#e6550d",
        "#6baed6", "#fd8d3c", "#74c476", "#fb6a4a", "#9e9ac8"
    ]

def generate(ctx):
    import os

    leaves = ctx["leaves"]
    attr_key = os.getenv("ITOL_COLORSTRIP_ATTR", "country").strip() or "country"
    ds_label = os.getenv("ITOL_COLORSTRIP_LABEL", attr_key).strip() or attr_key
    legend_title = os.getenv("ITOL_COLORSTRIP_TITLE", attr_key).strip() or attr_key
    include_na = os.getenv("ITOL_COLORSTRIP_INCLUDE_NA", "1").strip() != "0"
    top_n = int(os.getenv("ITOL_COLORSTRIP_TOP_N", "20"))  # improve readability
    force_keep = [x.strip() for x in os.getenv("ITOL_COLORSTRIP_FORCE_KEEP", "UAE").split(",") if x.strip()]

    # Collect raw values
    rows_raw = []
    counts = Counter()
    for leaf in leaves:
        leaf_id = leaf.get("name")
        if not leaf_id:
            continue
        val = _get_attr_value(leaf, attr_key, default="NA")
        if val == "NA" and not include_na:
            continue
        rows_raw.append((leaf_id, val))
        counts[val] += 1

    # Decide displayed categories (top N + force_keep)
    top_vals = [v for v, _ in counts.most_common(top_n)]
    keep_set = set(top_vals) | set(force_keep)
    if include_na and "NA" in counts:
        keep_set.add("NA")

    # Map less frequent categories to OTHER
    rows = []
    for leaf_id, val in rows_raw:
        mapped = val if val in keep_set else "OTHER"
        rows.append((leaf_id, mapped))

    # Build ordered categories by first appearance
    categories = OrderedDict()
    for _, val in rows:
        if val not in categories:
            categories[val] = None

    # Assign colors
    pal = _palette()
    for i, cat in enumerate(categories.keys()):
        if cat == "OTHER":
            categories[cat] = "#bdbdbd"
        elif cat == "NA":
            categories[cat] = "#f0f0f0"
        else:
            categories[cat] = pal[i % len(pal)]

    # Build dataset
    lines = []
    lines.append("DATASET_COLORSTRIP")
    lines.append("SEPARATOR\tTAB")
    lines.append(f"DATASET_LABEL\t{ds_label}")
    lines.append("COLOR\t#000000")
    lines.append(f"LEGEND_TITLE\t{legend_title}")

    legend_labels = list(categories.keys())
    legend_colors = [categories[c] for c in legend_labels]
    legend_shapes = ["1"] * len(legend_labels)

    lines.append("LEGEND_SHAPES\t" + "\t".join(legend_shapes))
    lines.append("LEGEND_COLORS\t" + "\t".join(legend_colors))
    lines.append("LEGEND_LABELS\t" + "\t".join(legend_labels))

    lines.append("DATA")
    for leaf_id, cat in rows:
        lines.append(f"{leaf_id}\t{categories[cat]}\t{cat}")

    filename = f"dataset_colorstrip_{attr_key}.txt"
    return {filename: "\n".join(lines) + "\n"}