def generate(ctx):
    leaves = ctx["leaves"]

    palette = [
        "#447CCD", "#88BB6C", "#CEB541", "#E39B39", "#DC2F24",
        "#7E57C2", "#26A69A", "#8D6E63", "#78909C", "#C2185B",
    ]
    region_to_color = {}

    def color_for(region: str) -> str:
        region = region or "NA"
        if region not in region_to_color:
            region_to_color[region] = palette[len(region_to_color) % len(palette)]
        return region_to_color[region]

    lines = []
    lines.append("TREE_COLORS")
    lines.append("SEPARATOR TAB")
    lines.append("DATA")

    for leaf in leaves:
        leaf_id = leaf["name"]
        region = ctx["get_attr"](leaf, "region", "NA")
        col = color_for(region)
        lines.append(f"{leaf_id}\tbranch\t{col}")

    return {"dataset_tree_colors_by_region.txt": "\n".join(lines) + "\n"}