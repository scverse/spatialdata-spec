# Questions

Answer inline (edit this file) or reply in chat. Each question states the default I am proceeding
with; if you are happy with the default you can leave it blank.

## Q1 — Website theme

`ome/ngff` uses `pydata-sphinx-theme` (top navbar with one entry per section). scverse packages use
`sphinx-book-theme` (left sidebar, already configured here).

- [x] **Default:** switch to `pydata-sphinx-theme`, one navbar entry per layer, custom CSS.
- [ ] Keep `sphinx-book-theme` for consistency with scverse docs.
- [ ] Other: ______

Answer:

## Q2 — Which on-disk versions to specify in full

Components and versions written by `spatialdata` 0.6.0:

| component | versions | current | Zarr |
|-----------|----------|---------|------|
| container | 0.1, 0.2 | 0.2 | 0.1 → v2, 0.2 → v3 |
| raster (images, labels) | 0.1, 0.2, 0.3 | 0.3 | 0.1/0.2 → v2, 0.3 → v3 |
| shapes | 0.1, 0.2, 0.3 | 0.3 | 0.1/0.2 → v2, 0.3 → v3 |
| points | 0.1, 0.2 | 0.2 | 0.1 → v2, 0.2 → v3 |
| tables | 0.1, 0.2 | 0.2 | 0.1 → v2, 0.2 → v3 |

- [x] **Default:** specify container 0.2 (Zarr v3) in full as "current"; show container 0.1 (Zarr v2)
  differences as a second inline tab wherever they differ; describe raster 0.1 and shapes 0.1 only in
  the version-history table (with the field names), not as full chapters.
- [ ] Specify every version in full.
- [ ] Current only, legacy versions mentioned in history only.

Answer:

## Q3 — Version label of the spec

- [x] **Default:** the spec version equals the container format version ("SpatialData on-disk
  format 0.2"). Per-element-type versions appear inside the spec as sub-versions.
- [ ] Independent spec version (e.g. 1.0) with a mapping table to component versions.

Answer:

## Q4 — Name of the format

- [x] **Default:** "SpatialData on-disk format" (short: "the format"); a store is "a SpatialData
  store" / "a SpatialData Zarr store".
- [ ] Other: ______

Answer:

## Q5 — NGFF divergence chapter

- [x] **Default:** one page `ngff-compatibility.md` with a matrix (NGFF 0.4 / 0.5 / 0.6-RFC-5 vs
  SpatialData) plus a boxed warning in each chapter where SpatialData diverges (e.g. `0.5-dev-spatialdata`
  version string, inline coordinate-system objects in `input`/`output`, transformations on shapes/points).
- [ ] Only the matrix, no per-chapter boxes.

Answer:

## Q6 — Scope of the in-memory (Python) spec

- [x] **Default:** data model of `spatialdata` 0.6 only (types, dims, attrs, invariants) plus
  implementation-guide boxes that name the minimal public API (`get_model`, `get_transformation`,
  `SpatialData.write`, …). No API reference duplication.
- [ ] Also include a stable "minimal interoperability API" list that other Python packages promise to
  support.

Answer:

## Q7 — Porting JSON schemas from SpatialData.validate

`Huber-group-EMBL/SpatialData.validate` is MIT-licensed (author: Hugo Gruson, EMBL). It ships JSON
schemas for raster metadata of format 0.1 and 0.3 (`image.schema`, `coordinate_transformations_ome-v0.6.schema`,
`_version.schema`).

- [x] **Default:** port them to `schemas/<version>/` (BSD-3 part of the repo) with an attribution
  header and a `schemas/README.md` crediting the author and the MIT licence; link them from the raster
  and coordinate-systems chapters; do this at the end of milestone 1 so prose stays the source of truth.
- [ ] Do not port; link to the R package only.
- [ ] Port and also write new schemas for shapes/points/tables/container.

Answer:

## Q8 — Diagrams

- [x] **Default:** ASCII trees + tables now; hand-written SVG schematics only where a picture
  materially helps (coordinate systems, element ↔ table annotation, store layout). I list each proposed
  figure with placement in `planning/NEXT_STEPS.md` for you to decide.
- [ ] Add `sphinxcontrib-mermaid` and draw diagrams as Mermaid source (renders in browser, editable).
- [ ] Produce SVGs myself right away.

Answer:

## Q9 — Name of layer 3

- [x] **Default:** "Semantic conventions" (subtitle: "how biology maps onto SpatialData elements";
  labelled *draft for community review*).
- [ ] "Biological annotations"
- [ ] "Domain conventions"
- [ ] Other: ______

Answer:

## Q10 — Prior art to survey for layer 3

I plan to cite (inspiration only, licence checked, no text copied): scanpy/squidpy/muon conventions,
`spatialdata-io` defaults, Bioconductor SpatialExperiment / SingleCellExperiment, Seurat, cellxgene
schema, OME metadata for channels, MIxS/MIAME-style sample metadata.

Add or remove anything?

Answer:

## Q11 — Landing page copy

Should the landing page keep including `README.md` (current behaviour) or get its own curated copy
(cards, "who should read what")? **Default:** curated copy; README stays GitHub-oriented.

Answer:

## Q12 — Reference to the developer notebooks

Should the spec link `spatialdata-notebooks/.../storage_format` as the official conformance examples,
or should examples be copied into this repo under `examples/` (BSD-3)? **Default:** link for now;
`examples/` listed as a next step.

Answer:

## Q13 — Where to put per-version spec text later

When the format changes next, do you want `spec/on-disk/<version>/` directories (as `ome/ngff-spec`)
or a single tree with tabs + git tags per spec release? **Default:** single tree + tags until a
breaking change makes duplication necessary.

Answer:

---

Questions that came up while drafting (see `planning/NEXT_STEPS.md` for the full list of facts to
verify).

## Q14 — DataTree data-variable name

You said the name is arbitrary and code must not rely on it. Three `spatialdata` code paths read
`["scale0"]["image"]` directly. **Default in the text:** "arbitrary; MAY be `image`". Alternative:
"MUST be `image`" until the code is fixed.

Answer:

## Q15 — Pixel-centre convention

The spec states pixel `i` covers `[i, i+1)` with centre `i + 0.5`. Confirm this is the intended
contract for the on-disk format (and not just how `spatialdata` fills xarray coords).

Answer:

## Q16 — Labels background

"`0` is background and MUST NOT be treated as an instance." MUST or SHOULD?

Answer:

## Q17 — Root key for semantic conventions

Options use `sdata.attrs["spatialdata_semantic"]` as the namespaced root. Alternatives:
`"semantic"`, `"scverse"`, `"spatialdata_conventions"`. Also: one object vs split between `attrs`
and table `uns` (open-question box at the end of `options.md`).

Answer:

## Q18 — Where should the planning files live?

`planning/` is committed for your review. After triage: delete, move to GitHub issues, or keep a
`docs/roadmap.md`?

Answer:

## Q19 — spatialdata-db citation

The repository is not public; the prior-art table cites it without a link and with "licence to be
confirmed". OK, or remove until public?

Answer:

## Q20 — Draft banner

The site shows an announcement banner "Draft under development…". Keep until the maintainer review
is done, or drop now?

Answer:

## Q21 — R and JavaScript implementations named in placeholders

Placeholders point to `HelenaLC/spatialdataR` and `Taylor-CCB-Group/SpatialData.js` (the latter
from the remote of your local checkout). Correct repositories? Others to add (e.g. Vitessce loaders,
Julia)?

Answer:

## Q22 — Label scheme

Layer badges: on-disk (primary), in-memory · Python (success), in-memory · R / JS (info), semantic
(warning). Status badges: status quo, legacy, draft, under discussion, placeholder. Legend on the
landing page. OK, or different wording (e.g. "as implemented" instead of "status quo")?

Answer:

## Q23 — Run the format.py consistency check in CI?

`tools/check_format_versions.py` needs `spatialdata` installed. Options: a separate optional CI
job installing `spatialdata` from PyPI; run it only in the `spatialdata` repository's CI against
this repo; manual only.

Answer:

## Q24 — Which spatialdata release does the spec describe?

Latest PyPI release is 0.8.0 (July 2026); locally 0.6.0 was installed. `format.py` is unchanged
between the two, so the on-disk text holds for both. The in-memory text was derived from the `main`
checkout (post-0.8.0). **Default applied:** on-disk badges say "spatialdata ≥ 0.6, checked against
0.8.0"; in-memory badges say "spatialdata 0.8"; the drift baseline is generated with 0.8.0. OK?

Answer:

## Q25 — Drift detection: enable the agent stage?

The `agent` job in `spec-drift.yml` is opt-in and needs an `ANTHROPIC_API_KEY` repository secret.
Enable it, keep it opt-in only, or remove it and rely on issues + humans?

Answer:

## Q26 — Drift detection cadence and targets

Default: weekly (Mondays) against the latest PyPI release, plus on-demand runs against `main` or a
tag. Alternatives: daily against `main`; trigger from the `spatialdata` release workflow via
`repository_dispatch`; or the shift-left job inside scverse/spatialdata CI (recommended long term).

Answer:

## Q27 — Where should the fixture stores live?

`conformance/fixture.py` produces a small dataset covering the whole format. Should the written
stores also be committed under `examples/` (BSD-3) for R/JS developers, or only generated on demand?

Answer:

## Q28 — Should unversioned byte changes bump a format version?

Between spatialdata 0.6 and 0.8 the pyramid array names (`0` → `s0`), the per-level `translation`,
and `multiscales[0].name` changed without a raster version bump (the changes come from ome-zarr-py).
The spec now documents them as allowed variation and tells readers to follow `path`. Should the
policy be "any byte change bumps the component version", or "only changes that break a
spec-following reader bump it" (current practice)?

Answer:

## Q29 — Fingerprint normalisation policy

The detector ignores dependency-driven differences (see `conformance/README.md`, "Not drift"). Is
that list right? In particular, AnnData encoding changes (anndata 0.13) are currently *reported*
because readers must handle them, even though the spec defers to AnnData. Keep reporting them?

Answer:
