def generate(ctx):
    leaves = ctx["leaves"]

    lines = []
    lines.append("LABELS")
    lines.append("SEPARATOR TAB")
    lines.append("DATA")

    for leaf in leaves:
        leaf_id = leaf["name"]
        region = ctx["get_attr"](leaf, "region", "")
        date = ctx["get_attr"](leaf, "date", "")

        short = leaf_id.split("_")[0]
        label = short
        if date:
            label = f"{label} | {date}"
        if region:
            label = f"{label} | {region}"

        lines.append(f"{leaf_id}\t{label}")

    return {"dataset_labels.txt": "\n".join(lines) + "\n"}
