import argparse
import importlib
import os
from pathlib import Path
import json
import sys

# Ensure project root is on sys.path so we can import itol_plugins/*
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))



def walk_tree(node):
    yield node
    for c in node.get("children", []) or []:
        yield from walk_tree(c)


def is_leaf(node):
    return not (node.get("children") or [])


def get_attr(node, key, default=""):
    attrs = node.get("node_attrs", {}) or {}
    v = attrs.get(key)
    if isinstance(v, dict):
        vv = v.get("value")
        return default if vv is None else vv
    return default


def load_mapping_tsv(path: Path):
    """
    TSV with header:
      leaf_id\tpdb_file
    """
    mapping = {}
    lines = path.read_text(encoding="utf-8").splitlines()
    if not lines:
        return mapping
    header = lines[0].split("\t")
    try:
        leaf_i = header.index("leaf_id")
        pdb_i = header.index("pdb_file")
    except ValueError:
        raise SystemExit(f"Invalid mapping header in {path}. Expected columns: leaf_id, pdb_file")

    for line in lines[1:]:
        if not line.strip():
            continue
        parts = line.split("\t")
        if len(parts) <= max(leaf_i, pdb_i):
            continue
        leaf_id = parts[leaf_i].strip()
        pdb_file = parts[pdb_i].strip()
        if leaf_id:
            mapping[leaf_id] = pdb_file
    return mapping


def main():
    ap = argparse.ArgumentParser(description="Build iTOL datasets from Auspice JSON via plugins.")
    ap.add_argument("--auspice", required=True, help="Path to Auspice JSON (e.g., Example/auspice.json)")
    ap.add_argument("--outdir", default="out/itol", help="Output directory for iTOL dataset files")
    ap.add_argument("--plugins", nargs="+", required=True, help="Plugins to run (module names in itol_plugins/ without .py)")
    ap.add_argument("--pdb-baseurl", default=os.getenv("ITOL_PDB_BASEURL", ""), help="Base URL for PDB links (or set ITOL_PDB_BASEURL)")
    ap.add_argument("--pdb-map", default=os.getenv("ITOL_PDB_MAP", ""), help="TSV map leaf_id->pdb_file (or set ITOL_PDB_MAP)")
    args = ap.parse_args()

    auspice_path = Path(args.auspice)
    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    data = json.loads(auspice_path.read_text(encoding="utf-8"))
    tree = data["tree"]

    leaves = []
    internals = []
    for n in walk_tree(tree):
        (leaves if is_leaf(n) else internals).append(n)

    pdb_map = {}
    if args.pdb_map:
        pdb_map = load_mapping_tsv(Path(args.pdb_map))

    ctx = {
        "auspice_path": auspice_path,
        "outdir": outdir,
        "data": data,
        "tree": tree,
        "leaves": leaves,
        "internals": internals,
        "get_attr": get_attr,
        "pdb_baseurl": args.pdb_baseurl,
        "pdb_map": pdb_map,
    }

    wrote = []
    for plugin_name in args.plugins:
        mod = importlib.import_module(f"itol_plugins.{plugin_name}")
        results = mod.generate(ctx)
        if not isinstance(results, dict):
            raise SystemExit(f"Plugin {plugin_name} must return dict: filename->text")
        for fname, text in results.items():
            outpath = outdir / fname
            outpath.write_text(text, encoding="utf-8")
            wrote.append(outpath)

    print("Wrote files:")
    for p in wrote:
        print(" -", p)
    print("Leaves:", len(leaves), "Internals:", len(internals))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
