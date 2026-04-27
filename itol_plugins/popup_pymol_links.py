from html import escape
from urllib.parse import quote
import json
import os


def _load_mut_index(path):
    if not path:
        return {}
    if not os.path.exists(path):
        return {}
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def _resistance_hits(aa_muts):
    # Expand this list as needed for your pathogen/gene context
    resistance_db = {
        "H275Y": "Oseltamivir resistance (NA inhibitor)",
        "E119V": "Reduced susceptibility (NA inhibitor)",
        "R292K": "Reduced susceptibility (NA inhibitor)",
        "N294S": "Reduced susceptibility (NA inhibitor)",
        "I223R": "Reduced susceptibility (NA inhibitor)",
    }
    hits = []
    for m in aa_muts:
        key = str(m).strip().upper()
        if key in resistance_db:
            hits.append((key, resistance_db[key]))
    return hits


def _risk_level(n_res_hits, n_mut):
    if n_res_hits >= 2:
        return "High"
    if n_res_hits == 1:
        return "Medium"
    if n_mut >= 8:
        return "Elevated"
    return "Low"


def generate(ctx):
    leaves = ctx["leaves"]
    get_attr = ctx["get_attr"]

    # Optional mapped PDB download
    pdb_baseurl = (ctx.get("pdb_baseurl") or "").strip()
    pdb_map = ctx.get("pdb_map") or {}

    # Interactive viewer config
    viewer_baseurl = (ctx.get("viewer_baseurl") or "https://nihlamadala.github.io/augur2itol/protein_viewer_3dmol.html").strip()
    viewer_pdb_path = (ctx.get("viewer_pdb_path") or "pdb/4fku.pdb").strip()
    viewer_index_path = (ctx.get("viewer_index_path") or "mutations_index.json").strip()
    viewer_offset = str(ctx.get("viewer_offset", -16)).strip()

    # Mutation index for popup text
    mutation_index_file = (ctx.get("mutation_index_file") or "out/web/mutations_index.json").strip()
    mut_index = _load_mut_index(mutation_index_file)

    if pdb_baseurl and not pdb_baseurl.endswith("/"):
        pdb_baseurl += "/"

    lines = ["POPUP_INFO", "SEPARATOR TAB", "DATA"]

    for leaf in leaves:
        leaf_id = leaf["name"]

        region = get_attr(leaf, "region", "NA")
        date = get_attr(leaf, "date", "")
        country = get_attr(leaf, "country", "")
        division = get_attr(leaf, "division", "")
        clade = get_attr(leaf, "clade", "")

        # Optional sample-specific downloadable PDB
        pdb_file = pdb_map.get(leaf_id, "")
        pdb_url = ""
        if pdb_baseurl and pdb_file:
            pdb_url = pdb_baseurl + quote(pdb_file)

        # Viewer link
        viewer_link = (
            f"{viewer_baseurl}"
            f"?pdb={quote(viewer_pdb_path)}"
            f"&node={quote(leaf_id)}"
            f"&index={quote(viewer_index_path)}"
            f"&offset={quote(viewer_offset)}"
        )

        # Mutation summary for popup
        rec = mut_index.get(leaf_id, {})
        aa_muts = rec.get("aa_mutations", []) or []
        res_pos = rec.get("residue_positions", []) or []

        # Resistance summary
        res_hits = _resistance_hits(aa_muts)
        risk = _risk_level(len(res_hits), len(aa_muts))
        if res_hits:
            res_text = "; ".join([f"{m} ({desc})" for m, desc in res_hits])
        else:
            res_text = "None detected in current marker panel"

        if aa_muts:
            shown = aa_muts[:8]
            extra = len(aa_muts) - len(shown)
            mut_text = ", ".join(escape(str(m)) for m in shown)
            if extra > 0:
                mut_text += f", +{extra} more"
        else:
            mut_text = "No listed AA mutations"

        title = f"Sample: {leaf_id}"

        download_row = ""
        if pdb_url:
            download_row = (
                "<div style='margin-top:6px; font-size:12px;'>"
                f"<span style='color:#555;'>Optional download:</span> "
                f"<a href='{escape(pdb_url)}' target='_blank' style='color:#2563eb; text-decoration:none;'>PDB file</a>"
                "</div>"
            )

        html = (
            "<div style='font-family:Arial,sans-serif; max-width:460px; line-height:1.28;'>"

            f"<div style='font-size:13px; color:#6b7280; margin-bottom:2px;'>Sample</div>"
            f"<div style='font-size:20px; font-weight:700; color:#111827; margin-bottom:10px;'>{escape(leaf_id)}</div>"

            "<table style='width:100%; border-collapse:collapse; font-size:14px;'>"
            f"<tr><td style='padding:4px 0; color:#6b7280; width:125px;'><b>Region</b></td><td style='padding:4px 0; color:#111827;'>{escape(str(region))}</td></tr>"
            f"<tr><td style='padding:4px 0; color:#6b7280;'><b>Date</b></td><td style='padding:4px 0; color:#111827;'>{escape(str(date))}</td></tr>"
            f"<tr><td style='padding:4px 0; color:#6b7280;'><b>Country</b></td><td style='padding:4px 0; color:#111827;'>{escape(str(country))}</td></tr>"
            f"<tr><td style='padding:4px 0; color:#6b7280;'><b>Division</b></td><td style='padding:4px 0; color:#111827;'>{escape(str(division))}</td></tr>"
            f"<tr><td style='padding:4px 0; color:#6b7280;'><b>Clade</b></td><td style='padding:4px 0; color:#111827;'>{escape(str(clade))}</td></tr>"
            f"<tr><td style='padding:4px 0; color:#6b7280;'><b>Mutation count</b></td><td style='padding:4px 0; color:#111827;'>{len(aa_muts)} (mapped residues: {len(res_pos)})</td></tr>"
            f"<tr><td style='padding:4px 0; color:#6b7280; vertical-align:top;'><b>AA mutations</b></td><td style='padding:4px 0; color:#111827;'>{mut_text}</td></tr>"
            f"<tr><td style='padding:4px 0; color:#6b7280;'><b>Risk level</b></td><td style='padding:4px 0; color:#111827;'>{escape(risk)}</td></tr>"
            f"<tr><td style='padding:4px 0; color:#6b7280; vertical-align:top;'><b>Resistance</b></td><td style='padding:4px 0; color:#111827;'>{escape(res_text)}</td></tr>"
            "</table>"

            "<div style='margin:12px 0; border-top:1px solid #e5e7eb;'></div>"

            "<div style='font-size:13px; color:#6b7280; margin-bottom:6px;'><b>Structure View</b></div>"
            "<div>"
            f"<a href='{escape(viewer_link)}' target='_blank' "
            "style='display:inline-block; background:#2563eb; color:white; padding:7px 11px; border-radius:8px; text-decoration:none; font-size:13px; font-weight:600;'>"
            "Open 3D Structure + Mutations"
            "</a>"
            "</div>"

            f"{download_row}"

            "</div>"
        )

        lines.append(f"{leaf_id}\t{title}\t{html}")

    return {"dataset_popup_info_pymol.txt": "\n".join(lines) + "\n"}
