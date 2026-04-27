# augur2itol  
**From Augur/Nextstrain JSON to iTOL-ready annotations and 3D mutation visualization**

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](#license)
[![Python](https://img.shields.io/badge/Python-3.9%2B-informational)](#requirements)

---

## Overview

`augur2itol` is a phylogeny annotation pipeline that converts **Nextstrain/Augur Auspice JSON** into:

1. **iTOL-compatible annotation datasets** (labels, color strips, tree colors, symbols, heatmaps, popup info)
2. **Node mutation index files** for structure-linked interpretation
3. **Interactive 3D structure links** (3Dmol.js) directly from iTOL popups

This enables a complete workflow from phylogenetic inference to publication-quality iTOL trees and structure-aware mutation interpretation.

---

## Who this is for

- Genomic epidemiology researchers
- Virology and influenza surveillance labs
- Students and biologists using Augur/Nextstrain + iTOL
- Users who need reproducible, automated annotation generation

---

## Repository structure

- `augur2itol/` — packaged core CLI (`augur2itol`)
- `scripts/` — workflow scripts (dataset build, mutation index, iTOL upload)
- `itol_plugins/` — modular annotation generators for iTOL
- `docs/` — GitHub Pages assets (`protein_viewer_3dmol.html`, `mutations_index.json`, `pdb/`)
- `Example/` — sample Auspice JSON input
- `out/` — generated outputs

---

## Requirements

- Python 3.9+
- `itolapi` Python package (for automatic iTOL upload)
- iTOL API key (for upload automation)

---

## Quick start (minimal, production workflow)

### 1) Clone and prepare environment

```bash
git clone https://github.com/nihlamadala/augur2itol.git
cd augur2itol

python -m venv .venv
source .venv/bin/activate   # Linux/macOS
# .venv\Scripts\activate    # Windows PowerShell

pip install -U pip
pip install itolapi
```

---

### 2) Prepare input JSON

Obtain Auspice JSON from your Nextstrain/Augur workflow (e.g., output of `augur export v2`), then place it at:

`Example/auspice.json`

(Or use another path and pass it in commands below.)

---

### 3) Build mutation index for structure viewer

```bash
python scripts/build_mutation_index.py \
  --input Example/auspice.json \
  --output docs/mutations_index.json \
  --gene HA
```

---

### 4) Build iTOL annotation datasets (plugins)

```bash
python scripts/itol_build.py \
  --auspice Example/auspice.json \
  --outdir out/itol \
  --plugins labels tree_colors_region auto_colorstrip auto_heatmap auto_symbol introductions_country introductions_pie introductions_piechart popup_pymol_links
```

This generates iTOL datasets such as:
- `dataset_labels.txt`
- `dataset_tree_colors_by_region.txt`
- `dataset_colorstrip_<attr>.txt`
- `dataset_popup_info_pymol.txt`

---

### 5) Build Newick tree file

```bash
augur2itol --auspice Example/auspice.json --outdir out
```

This writes:
- `out/tree.nwk`
- region colorstrip + QC report

---

### 6) Automatic upload to iTOL (itolapi)

Set API key:

```bash
export ITOL_APIKEY="YOUR_ITOL_API_KEY"
```

Current uploader expects `out/tree.tree.txt`. If your output is `out/tree.nwk`, copy once:

```bash
cp out/tree.nwk out/tree.tree.txt
```

Run uploader:

```bash
python scripts/upload_itol.py
```

If upload succeeds, script prints:
- iTOL tree ID
- iTOL web page URL
- server warnings/output

---

## Visualization workflow in iTOL

After upload (or manual upload), load:
- tree file (`tree.nwk` / `tree.tree.txt`)
- generated datasets (`out/itol/*.txt`)

For popup-enabled dataset:
- click any annotated sample node
- click **Open 3D Structure + Mutations**
- browser opens 3Dmol viewer with node-specific mutation highlights

---

## 3D structure viewer

Hosted viewer page:

`https://nihlamadala.github.io/augur2itol/protein_viewer_3dmol.html`

Expected URL parameters:
- `pdb`
- `node`
- `index`
- `offset`

Residue mapping rule:
`PDB_residue = mutation_position + offset`

---

## Optional plugins

Additional plugins in `itol_plugins/` support:
- `auto_heatmap` — numeric trait heatmap
- `auto_symbol` — categorical symbol overlays
- `introductions_country` — inferred country introduction events
- `introductions_pie` / `introductions_piechart` — intro confidence visualizations

---

## Notes and caveats

- Designed primarily for Auspice JSON (`tree` present at top level).
- Ensure IDs in datasets match IDs in Newick tree.
- Validate residue offset biologically for your gene/structure mapping.
- For automated upload, align uploader tree filename expectation (`tree.tree.txt` vs `tree.nwk`).

---

## Citation

If you use this repository in research outputs, please cite the repository URL and commit/version used for reproducibility.

---

## License

MIT License.