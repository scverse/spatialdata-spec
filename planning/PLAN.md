# Plan: SpatialData specification website

Working plan for turning `spatialdata-spec` into the home of the three SpatialData specification
layers. Written 2026-09-11. Files in `planning/` are working documents, not part of the spec; delete
or move them once the work is merged.

Companion files:

- `planning/QUESTIONS.md` — decisions I need from you, each with the default I am proceeding with.
- `planning/NEXT_STEPS.md` — hand-off for contributors: open items, figures to add, review checklist
  (written at the end of each milestone).

## Status (2026-09-11, end of first pass)

| Phase | State |
|-------|-------|
| 0 · Website scaffolding | done (pydata-sphinx-theme, landing page, glossary, CSS, custom admonitions) |
| 1 · On-disk format | first draft complete, needs maintainer verification (`NEXT_STEPS.md`) |
| 2 · In-memory format (Python) | first draft complete |
| 3 · Semantic conventions | options Q1–Q11 + prior art written; awaiting community review |
| 4 · Hand-off | `NEXT_STEPS.md`, README, CHANGELOG, contributing guide updated |

Nothing is committed; all changes are in the working tree for review.

## The three layers

| # | Layer | Audience | Language | Status of source of truth today |
|---|-------|----------|----------|----------------------------------|
| 1 | **On-disk format** (Zarr + Parquet, NGFF-based) | R / JS / Python / any implementer | agnostic | design doc + `spatialdata/_io/format.py` + readers/writers |
| 2 | **In-memory format, Python** (`spatialdata` data model) | Python tool authors building on `spatialdata` | Python | design doc + `spatialdata/models/models.py` |
| 3 | **Semantic conventions** (how biology maps onto elements) | Analysis tool authors, data producers | agnostic | none; to be proposed as options for community review |

Milestones are delivered in this order so that partial progress is still useful.

## Sources of truth used

- `spatialdata` 0.6.0 (installed; latest release is 0.8.0 with an identical `format.py`) and local checkout `~/embl/projects/basel/spatialdata` (branch
  `adopt-scverse-template`, 2026-09-11): `_io/format.py`, `_io/io_*.py`, `models/models.py`,
  `transformations/`, `docs/design_doc.md`, `CHANGELOG.md`.
- Freshly written `blobs()` stores in both container formats (`/tmp/sdata_cur.zarr` = container 0.2 /
  Zarr v3, `/tmp/sdata_legacy.zarr` = container 0.1 / Zarr v2) to read the exact metadata.
- `spatialdata-notebooks/notebooks/developers_resources/storage_format` (linked as conformance examples,
  not copied).
- NGFF: `ome/ngff` (site organisation only; content is W3C Software and Document License, we copy no
  text) and `ome/ngff-spec` (spec text; referenced, not copied).
- AnnData on-disk spec (referenced, not copied).
- `Huber-group-EMBL/SpatialData.validate` (MIT, author Hugo Gruson): JSON schemas for format 0.1 and
  0.3 raster metadata; candidates to port under `schemas/` with attribution (see Q7).

## Phase 0 — Website scaffolding

Goal: a modern, navigable site with the section structure of the final product, so that content can
be dropped in chapter by chapter.

1. Switch `docs/conf.py` to `pydata-sphinx-theme` (same theme as ngff.openmicroscopy.org) with a top
   navbar: *On-disk format* · *In-memory (Python)* · *Semantic conventions* · *Contributing*. Keep
   `sphinx-design` (cards, tabs, dropdowns) and `myst-parser` (colon fences). Add `sphinxcontrib-mermaid`
   only if approved (Q8); otherwise diagrams are ASCII trees and tables.
2. Custom CSS: spec-oriented styling (requirement keywords MUST/SHOULD highlighted, compact tables,
   version badges, "implementation note" and "not part of the spec" admonitions).
3. Curated landing page (`docs/index.md`): three cards for the three layers, a "who should read what"
   table, version badge of the current on-disk format, link to the format changelog.
4. `spec/` layout (prose only, CC-BY-4.0):

   ```
   spec/
   ├── README.md                     (unchanged: licensing note)
   ├── on-disk/
   │   ├── index.md                  overview, scope, conventions (RFC 2119), status vs NGFF
   │   ├── container.md              root group, element groups, naming, versioning attrs
   │   ├── coordinate-systems.md     coordinate systems + transformations (as stored today)
   │   ├── images.md
   │   ├── labels.md
   │   ├── shapes.md
   │   ├── points.md
   │   ├── tables.md
   │   ├── ngff-compatibility.md     delta table vs NGFF 0.4 / 0.5 / 0.6-RFC-5
   │   └── versions.md               version history of every format component + migration notes
   ├── in-memory/
   │   └── python/
   │       ├── index.md              scope, the SpatialData object, element naming, get_model()
   │       ├── elements.md           Image/Labels/Shapes/Points/Table models, single vs multiscale
   │       ├── transformations.md    BaseTransformation classes, attrs["transform"], set/get
   │       └── implementation-guide.md   boxes: "if you receive an element, do this"
   └── semantic/
       ├── index.md                  motivation, scope, how to give feedback
       └── options.md                candidate conventions, listed side by side
   ```

   Versions: a single "latest" tree, with differences between on-disk versions shown as inline tabs.
   Per-version directories (as `ome/ngff-spec` does) will be introduced only once the format moves
   again, to avoid duplicating text now (Q2, Q13).

5. Glossary page (`docs/glossary.md`) so that terms (element, coordinate system, instance, region…)
   are defined once and cross-referenced with `{term}` roles.

## Phase 1 — On-disk format (milestone 1)

Chapter contents, all "as implemented in spatialdata 0.6.0", written normatively (MUST/SHOULD/MAY):

- **Overview**: what a SpatialData store is, the Zarr + Parquet split, element types, the
  `spatialdata_attrs.version` scheme (container version vs per-element-type versions), what is NGFF
  and what is a SpatialData extension. One ASCII tree of a full store.
- **Container**: root group attributes; the five fixed top-level groups; element naming rules (from the
  design doc); uniqueness; consolidated metadata; Zarr v2 vs v3 (tabs).
- **Coordinate systems and transformations**: intrinsic vs extrinsic, the `global` default, allowed
  axes, unit handling, JSON encoding of each transformation type (identity, scale, translation, affine,
  sequence, …) with one example each in tabs; where transformations live for each element type;
  differences from RFC-5 in a boxed note.
- **Images / Labels**: point to NGFF multiscales + image-label; specify what SpatialData adds
  (`spatialdata_attrs`, `coordinateTransformations` on the multiscale, version string
  `0.5-dev-spatialdata`), what it restricts (axes `cyx`/`czyx`, `yx`/`zyx`; dtypes), what it does
  not use (omero beyond channel labels, wells, plates, bioformats2raw).
- **Shapes**: GeoParquet file `shapes.parquet`, geometry types, `radius` column for circles, index,
  group attributes (`encoding-type: ngff:shapes`, `axes`, `coordinateTransformations`,
  `spatialdata_attrs`). Legacy 0.1 (`geos` attrs) in a collapsed tab.
- **Points**: Parquet directory `points.parquet/part.*.parquet`, required coordinate columns,
  `feature_key` / `instance_key`, categorical columns, group attributes.
- **Tables**: point to the AnnData on-disk spec; list only the additions:
  `spatialdata-encoding-type: ngff:regions_table`, `region` / `region_key` / `instance_key` attrs and
  their duplication in `uns/spatialdata_attrs`, the annotation rules (one row ↔ one instance of one
  region element), index dtype rules, the `_index` reservation.
- **NGFF compatibility**: table with rows = NGFF features, columns = 0.4 / 0.5 / 0.6 (RFC-5) /
  SpatialData, cells = used as-is / restricted / extended / not supported.
- **Versions**: table of every (component, version) pair, the Zarr format it implies, the
  `spatialdata` release that introduced it, and the migration notes (e.g. shapes 0.1 → 0.2 dropped the
  `geos` attrs; raster 0.1 → 0.2 changed the NGFF version string).
- Optional (Q7): port `SpatialData.validate` schemas to `schemas/` with attribution; link from chapters.

## Phase 2 — In-memory format, Python (milestone 2)

- The `SpatialData` object: element containers, unique names, `attrs`, tables and their targets,
  coordinate systems as the grouping mechanism.
- Element models: exact Python types (`xarray.DataArray` / `xarray.DataTree`, `GeoDataFrame`,
  `dask.dataframe.DataFrame`, `AnnData`), required dims/columns/attrs, the DataTree layout
  (`scale0/…`, one variable per node, its name is arbitrary and MAY be `image`), dtype rules, what
  `parse()` guarantees and `validate()` checks.
- Transformations: `BaseTransformation` subclasses, `attrs["transform"]` dict keyed by coordinate
  system name, axis pass-through semantics.
- Implementation guide boxes (explicitly "not part of the format"): dispatch on `get_model()`,
  single- vs multiscale handling, circles vs polygons, reading tables that annotate an element,
  handling categorical `feature_key`, writing back with the current format.

## Phase 3 — Semantic conventions (milestone 3)

- Motivation: SpatialData has zero biological vocabulary; tooling needs shared conventions to find
  "cells", "genes", "cell types", "samples" without guessing column names.
- Inventory of what exists today, cited with licence checked: scanpy/squidpy/muon conventions,
  `spatialdata-io` defaults (`region`, `instance_id`, `feature_key`), and non-scverse prior art
  (SpatialExperiment, Seurat, cellxgene schema, …) as *inspiration only*.
- Options listed side by side (not mandated), each with: where the information lives (element attrs,
  table `uns`, obs column, naming convention), pros/cons, migration cost, example. Kept technology
  agnostic (no Visium/Xenium bias).
- A feedback section: how to comment (GitHub issues with a label), what a decision would look like.

## Phase 4 — Hand-off

- `planning/NEXT_STEPS.md`: open decisions, list of figures/schematics to add with suggested placement,
  review checklist, how to cut the first spec release.
- Update `README.md` roadmap, `CHANGELOG.md`, `docs/contributing_to_the_spec.md`.
- Verify `hatch run docs:build` (warnings are errors) and pre-commit pass.

## Writing rules applied throughout

- No fluff; one idea per sentence; MUST/SHOULD/MAY per RFC 2119.
- Anything defined elsewhere (NGFF, AnnData, GeoParquet, Parquet, Zarr) is linked, and only the delta
  is specified here.
- Multiple versions of the same thing go into inline tabs; the current version is the default tab.
- Boxes: `note` for context, `implementation-note` for non-normative guidance, `warning` for known
  divergences from NGFF, `dropdown` for legacy versions.
- Every chapter ends with a short "Decisions and figures" list in `NEXT_STEPS.md`, not in the spec.
