def _walk(node, parent=None):
    yield node, parent
    for c in node.get("children", []) or []:
        yield from _walk(c, node)

def _get_attr(node, key):
    na = (node.get("node_attrs") or {})
    x = na.get(key) or {}
    if isinstance(x, dict):
        return x.get("value")
    return None

def _get_confidence(node, trait, target):
    na = (node.get("node_attrs") or {})
    x = na.get(trait) or {}
    if isinstance(x, dict):
        conf = x.get("confidence")
        if isinstance(conf, dict):
            v = conf.get(target)
            try:
                return float(v)
            except Exception:
                return None
    return None

def generate(ctx):
    import os

    tree = ctx["tree"]
    focal = os.getenv("ITOL_FOCAL_COUNTRY", "UAE").strip() or "UAE"
    trait = os.getenv("ITOL_INTRO_TRAIT", "country").strip() or "country"
    min_conf = float(os.getenv("ITOL_INTRO_MIN_CONF", "0.8"))

    label = os.getenv("ITOL_INTRO_PIE_LABEL", f"Introductions into {focal}")
    max_size = os.getenv("ITOL_INTRO_PIE_MAX_RADIUS", "30")
    pos = os.getenv("ITOL_INTRO_PIE_POSITION", "1")  # on-node
    yes_color = os.getenv("ITOL_INTRO_PIE_YES_COLOR", "#d73027")
    no_color = os.getenv("ITOL_INTRO_PIE_NO_COLOR", "#d9d9d9")

    lines = []
    lines.append("DATASET_PIECHART")
    lines.append("SEPARATOR\tTAB")
    lines.append(f"DATASET_LABEL\t{label}")
    lines.append("COLOR\t#000000")
    lines.append(f"MAXIMUM_SIZE\t{max_size}")
    lines.append("FIELD_LABELS\tIntroConfidence\tResidual")
    lines.append(f"FIELD_COLORS\t{yes_color}\t{no_color}")
    lines.append("LEGEND_TITLE\tIntroduction nodes")
    lines.append("LEGEND_SHAPES\t1")
    lines.append(f"LEGEND_COLORS\t{yes_color}")
    lines.append(f"LEGEND_LABELS\t{focal} introduction")
    lines.append("DATA")

    intro_count = 0

    for node, parent in _walk(tree):
        if parent is None:
            continue

        nid = node.get("name")
        if not nid:
            continue

        node_country = _get_attr(node, trait)
        parent_country = _get_attr(parent, trait)

        if node_country != focal:
            continue
        if parent_country == focal:
            continue  # not a transition; already within focal-country clade

        conf = _get_confidence(node, trait, focal)
        if conf is None:
            conf = 1.0  # fallback if confidence map absent

        if conf < min_conf:
            continue

        residual = max(0.0, 1.0 - conf)
        radius = 2.2  # visible pie at intro node
        lines.append(f"{nid}\t{pos}\t{radius}\t{conf:.3f}\t{residual:.3f}")
        intro_count += 1

    # if no intro found, still return valid file (empty DATA section)
    return {f"dataset_introductions_{focal}_pie_intro_nodes.txt": "\n".join(lines) + "\n"}