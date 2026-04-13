import os
import sys
from pathlib import Path

from itolapi import Itol


def main():
    api_key = os.getenv("ITOL_APIKEY")
    if not api_key:
        print("ERROR: ITOL_APIKEY environment variable is not set.", file=sys.stderr)
        print('Set it like: export ITOL_APIKEY="YOUR_KEY"', file=sys.stderr)
        return 2

    root = Path(__file__).resolve().parents[1]
    outdir = root / "out"
    itol_dir = outdir / "itol"

    tree_file = outdir / "tree.tree.txt"
    dataset_region = itol_dir / "dataset_region_colorstrip.txt"

    dataset_labels = itol_dir / "dataset_labels.txt"
    dataset_tree_colors_region = itol_dir / "dataset_tree_colors_by_region.txt"
    dataset_popup_pymol = itol_dir / "dataset_popup_info_pymol.txt"

    # Optional files (only add if they exist)
    labels_file = root / "labels.txt"
    tree_colors_file = root / "ranges.txt"
    popup_file = root / "popup_info_template.txt"

    missing = [p for p in [tree_file, dataset_region] if not p.exists()]
    if missing:
        print("ERROR: Missing required file(s):", file=sys.stderr)
        for p in missing:
            print(f"  - {p}", file=sys.stderr)
        print("Run augur2itol first to generate outputs.", file=sys.stderr)
        return 2

    itol = Itol()

    # Add required
    itol.add_file(tree_file)
    itol.add_file(dataset_region)

    # Add optional (only if present)
    for opt in [labels_file, tree_colors_file, popup_file, dataset_labels, dataset_popup_pymol]:
        if opt.exists():
            itol.add_file(opt)

    itol.params["APIkey"] = api_key
    itol.params["treeName"] = "Augur2iTOL upload"
    itol.params["projectName"] = "augur2itol"

    print("Uploading to iTOL...")
    good = itol.upload()
    if not good:
        print("Upload failed.")
        print("Server output:")
        print(itol.comm.upload_output)
        return 1

    print("Upload OK.")
    print("Tree ID:", itol.comm.tree_id)
    print("Tree Web Page URL:", itol.get_webpage())
    print("Warnings:", itol.comm.warnings)
    print("Raw iTOL output:")
    print(itol.comm.upload_output)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
PY
