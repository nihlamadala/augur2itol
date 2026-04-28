def _walk(node, parent=None):
    yield node, parent
    for c in node.get("children", []) or []:
        yield from _walk(c, node)

def _is_leaf(node):
    return not (node.get("children", []) or [])

def _get_attr(node, key):
    na = (node.get("node_attrs") or {})
    x = na.get(key) or {}
    if isinstance(x, dict):
        return x.get("value")
    return None

def _get_confidence_to(node, trait, target):
    """
    Looks for node_attrs[trait].confidence dict and returns confidence for target if present.
    """
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
    focal_country = os.getenv("ITOL_FOCAL_COUNTRY", "UAE").strip() or "UAE"
    trait_key = os.getenv("ITOL_INTRO_TRAIT", "country").strip() or "country"
    min_conf = float(os.getenv("ITOL_INTRO_MIN_CONF", "0.8"))

    # Style controls
    label = os.getenv("ITOL_INTRO_PIE_LABEL", f"Intro to {focal_country} (pie)")
    max_radius = os.getenv("ITOL_INTRO_PIE_MAX_RADIUS", "12")
    ext_pos = os.getenv("ITOL_INTRO_PIE_EXTERNAL", "-1")  # -1 => external
    yes_color = os.getenv("ITOL_INTRO_PIE_YES_COLOR", "#d73027")
    no_color = os.getenv("ITOL_INTRO_PIE_NO_COLOR", "#cccccc")

    lines = []
    lines.append("DATASET_PIECHART")
    lines.append("SEPARATOR\tTAB")
    lines.append(f"DATASET_LABEL\t{label}")
    lines.append("COLOR\t#000000")
    lines.append(f"MAXIMUM_SIZE\t{max_radius}")
    lines.append("FIELD_LABELS\tIntro\tNotIntro")
    lines.append(f"FIELD_COLORS\t{yes_color}\t{no_color}")
    lines.append("LEGEND_TITLE\tIntroductions")
    lines.append("LEGEND_SHAPES\t1\t1")
    lines.append(f"LEGEND_COLORS\t{yes_color}\t{no_color}")
    lines.append("LEGEND_LABELS\tIntro\tNotIntro")
    lines.append("DATA")

    # Strategy:
    # For each leaf, if leaf country == focal -> classify as intro-like with confidence from node confidence map if present.
    # If confidence missing, use 1.0 for direct focal-country leaves.
    # For non-focal leaves => intro=0, notintro=1
    for node, parent in _walk(tree):
        if not _is_leaf(node):
            continue
        nid = node.get("name")
        if not nid:
            continue

        ctry = _get_attr(node, trait_key)
        conf = _get_confidence_to(node, trait_key, focal_country)

        if ctry == focal_country:
            p_intro = conf if conf is not None else 1.0
            if p_intro < min_conf:
                # below threshold: treat as uncertain/non-intro for cleaner interpretation
                p_intro = 0.0
        else:
            p_intro = 0.0

        p_not = max(0.0, 1.0 - p_intro)

        # DATASET_PIECHART row format:
        # ID   position   radius   val1   val2 ...
        # position -1 => external chart
        radius = 1.0 if p_intro > 0 else 0.6
        lines.append(f"{nid}\t{ext_pos}\t{radius}\t{p_intro:.3f}\t{p_not:.3f}")

    return {f"dataset_introductions_{focal_country}_pie.txt": "\n".join(lines) + "\n"}