from __future__ import annotations

from typing import Dict, Optional, Tuple


def _country_value(node) -> Optional[str]:
    na = node.get("node_attrs") or {}
    c = na.get("country") or {}
    return c.get("value")


def _country_confidence_map(node) -> Dict[str, float]:
    na = node.get("node_attrs") or {}
    c = na.get("country") or {}
    conf = c.get("confidence") or {}
    out: Dict[str, float] = {}
    for k, v in conf.items():
        try:
            out[k] = float(v)
        except Exception:
            continue
    return out


def _confidence_for(node, focal_country: str) -> Optional[float]:
    conf = _country_confidence_map(node)
    return conf.get(focal_country)


def _node_name(node) -> Optional[str]:
    return node.get("name")


def generate(ctx):
    """
    iTOL COLORSTRIP dataset marking nodes that are introductions into a focal country
    based on inferred country changes and confidence threshold.

    Parameters via environment variables (optional):
      - ITOL_FOCAL_COUNTRY (default: UAE)
      - ITOL_INTRO_MIN_CONF (default: 0.8)
    """
    data = ctx["data"]
    tree = ctx["tree"]

    focal_country = (ctx.get("focal_country") or "").strip() or "UAE"
    # allow env override without changing CLI for now
    try:
        import os

        focal_country = os.getenv("ITOL_FOCAL_COUNTRY", focal_country)
        min_conf = float(os.getenv("ITOL_INTRO_MIN_CONF", "0.8"))
    except Exception:
        min_conf = 0.8

    strip_color = "#e41a1c"
    dataset_name = f"Introductions to {focal_country}"

    introductions: Dict[str, Tuple[float, Optional[str]]] = {}

    stack = [(tree, None)]
    while stack:
        node, parent = stack.pop()
        for ch in node.get("children", []) or []:
            stack.append((ch, node))

        name = _node_name(node)
        if not name:
            continue

        c = _country_value(node)
        if c != focal_country:
            continue

        parent_c = _country_value(parent) if parent else None
        if parent_c == focal_country:
            continue  # not a new intro

        conf = _confidence_for(node, focal_country)
        if conf is None or conf < min_conf:
            continue

        introductions[name] = (conf, parent_c)

    # Build iTOL dataset text
    lines = []
    lines.append("DATASET_COLORSTRIP")
    lines.append("SEPARATOR TAB")
    lines.append(f"DATASET_LABEL\tIntroductions to UAE")
    lines.append(f"COLOR\t#e41a1c")
    lines.append("LEGEND_TITLE\tIntroductions")
    lines.append("LEGEND_SHAPES\t1")
    lines.append(f"LEGEND_COLORS\t{strip_color}")
    lines.append(f"LEGEND_LABELS\tIntro to UAE (conf>=0.8)")
    lines.append("DATA")

    for node_id, (conf, parent_c) in sorted(introductions.items()):
        label = f"Intro (from {parent_c or 'NA'}, conf={conf:.3f})"
        lines.append(f"{node_id}\t{strip_color}\t{label}")

    fname = f"dataset_introductions_{focal_country}.txt"
    return {fname: "\n".join(lines) + "\n"}
