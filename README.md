# Mind–Body Program Atlas

An interactive survey of 74 popular mind–brain–body programs for chronic pain, ME/CFS, long COVID, fibromyalgia, IBS, MCS, POTS, FND and related conditions.

**Live page:** https://torwager.github.io/mind-body-atlas/

The page has four views: a timeline with popularity estimates, the traditions each program draws on, the conditions it claims to treat, and its proposed mechanisms. It also has a sortable table of all programs and a Methods section.

## Contents
- `programs/`: one review per program, covering mechanisms, treatments, founders, cost, adoption, insurance and trials. `programs/README.md` is an index.
- `data/programs/`: fact-checked structured data for each program.
- `data/`: curation and fact-check logs, popularity calibration, and the combined dataset behind the page.
- `scripts/`: normalization and build scripts. Run `normalize.py`, then `build_atlas_data.py`, then `build_html.py`.

Compiled October 2026 by AI research agents. Each program was researched by one agent and fact-checked by another. Popularity figures are order-of-magnitude estimates; see Methods.
