from html import escape
from urllib.parse import quote


def generate(ctx):
    leaves = ctx["leaves"]
    get_attr = ctx["get_attr"]
    pdb_baseurl = (ctx.get("pdb_baseurl") or "").strip()
    pdb_map = ctx.get("pdb_map") or {}

    if not pdb_baseurl:
        # We still generate popups, but without a link.
        pdb_baseurl = ""

    # Ensure baseurl ends with /
    if pdb_baseurl and not pdb_baseurl.endswith("/"):
        pdb_baseurl += "/"

    lines = []
    lines.append("POPUP_INFO")
    lines.append("SEPARATOR TAB")
    lines.append("DATA")

    for leaf in leaves:
        leaf_id = leaf["name"]

        region = get_attr(leaf, "region", "NA")
        date = get_attr(leaf, "date", "")
        country = get_attr(leaf, "country", "")
        division = get_attr(leaf, "division", "")
        clade = get_attr(leaf, "clade", "")

        # Mapping rule (5B): leaf_id -> pdb_file via TSV
        pdb_file = pdb_map.get(leaf_id, "")
        pdb_url = ""
        if pdb_baseurl and pdb_file:
            # URL-encode file component
            pdb_url = pdb_baseurl + quote(pdb_file)

        title = f"Sample: {leaf_id}"

        # Keep HTML simple & robust
        link_html = ""
        if pdb_url:
            link_html = f"<p><b>Structure (PDB):</b> <a href='{escape(pdb_url)}' target='_blank'>Download</a></p>"
            link_html += "<p><i>Open in PyMOL:</i> File → Open… (select the downloaded .pdb)</p>"
        else:
            link_html = "<p><b>Structure (PDB):</b> not available for this sample.</p>"

        html = (
            "<div class='tPop'>"
            f"<h1>{escape(leaf_id)}</h1>"
            "<table>"
            f"<tr><th>Region</th><td>{escape(str(region))}</td></tr>"
            f"<tr><th>Date</th><td>{escape(str(date))}</td></tr>"
            f"<tr><th>Country</th><td>{escape(str(country))}</td></tr>"
            f"<tr><th>Division</th><td>{escape(str(division))}</td></tr>"
            f"<tr><th>Clade</th><td>{escape(str(clade))}</td></tr>"
            "</table>"
            f"{link_html}"
            "</div>"
        )

        lines.append(f"{leaf_id}\t{title}\t{html}")

    return {"dataset_popup_info_pymol.txt": "\n".join(lines) + "\n"}