def _get_attr_value(node, key: str) -> str:
    attrs = node.get("node_attrs", {}) or {}
    obj = attrs.get(key)
    if isinstance(obj, dict):
        return obj.get("value") or ""
    return ""


def write_region_colorstrip_dataset(leaves, outpath):
    """
    iTOL DATASET_COLORSTRIP formatted like the official templates:

    - SEPARATOR SPACE
    - DATA rows: <ID> <COLOR> <LABEL>
      Example: 160232 #caf390 COL#caf390

    We use leaf "name" as the ID (must match the IDs in the Newick tree).
    """
    lines = []
    lines.append("DATASET_COLORSTRIP")
    lines.append("SEPARATOR SPACE")
    lines.append("DATASET_LABEL Region")
    lines.append("COLOR #000000")
    lines.append("STRIP_WIDTH 25")
    lines.append("MARGIN 0")
    lines.append("BORDER_WIDTH 1")
    lines.append("BORDER_COLOR #000000")
    lines.append("SHOW_INTERNAL 0")
    lines.append("DATA")

    region_to_color = {}
    palette = [
        "#447CCD", "#88BB6C", "#CEB541", "#E39B39", "#E56C2F",
        "#DC2F24", "#7E57C2", "#26A69A", "#8D6E63", "#78909C"
    ]

    def color_for(region: str) -> str:
        if region not in region_to_color:
            region_to_color[region] = palette[len(region_to_color) % len(palette)]
        return region_to_color[region]

    for leaf in leaves:
        leaf_id = leaf.get("name", "")
        region = _get_attr_value(leaf, "region") or "NA"
        color = color_for(region)

        # 3rd column is a label shown in legend; template uses "COL#xxxxxx".
        # We'll include region as well so it’s readable.
        label = f"{region}"

        # SPACE-separated line
        lines.append(f"{leaf_id} {color} {label}")

    outpath.write_text("\n".join(lines) + "\n", encoding="utf-8")
