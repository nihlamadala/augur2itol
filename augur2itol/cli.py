import argparse
from pathlib import Path

from .auspice import load_auspice_tree, iter_nodes, is_leaf
from .export_newick import to_newick
from .itol_datasets import write_region_colorstrip_dataset
from .qc import write_qc_report


def main():
    p = argparse.ArgumentParser(prog="augur2itol")
    p.add_argument("--auspice", required=True, help="Path to auspice.json")
    p.add_argument("--outdir", required=True, help="Output directory")
    args = p.parse_args()

    outdir = Path(args.outdir)
    (outdir / "itol").mkdir(parents=True, exist_ok=True)

    tree = load_auspice_tree(args.auspice)

    # 1) Write Newick (topology only)
    newick = to_newick(tree)
    (outdir / "tree.nwk").write_text(newick + ";\n", encoding="utf-8")

    # 2) Collect leaf nodes (tips)
    leaves = []
    for node in iter_nodes(tree):
        if is_leaf(node):
            leaves.append(node)

    # 3) iTOL dataset: region color strip
    write_region_colorstrip_dataset(leaves, outdir / "itol" / "dataset_region_colorstrip.txt")

    # 4) QC
    write_qc_report(leaves, outdir / "qc_report.tsv")

    print("Done.")
    print(f"Wrote: {outdir / 'tree.nwk'}")
    print(f"Wrote: {outdir / 'itol' / 'dataset_region_colorstrip.txt'}")
    print(f"Wrote: {outdir / 'qc_report.tsv'}")