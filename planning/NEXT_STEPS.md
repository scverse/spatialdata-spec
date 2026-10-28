# Next steps for contributors

Hand-off document, written 2026-09-11 after the first drafting pass. It lists what exists, what must
be verified by a maintainer before the text can be called authoritative, which figures would help,
and what remains to be done. Delete or move to GitHub issues once triaged.

## What exists

| Layer | Pages | Status |
|-------|-------|--------|
| Website | `docs/index.md`, `docs/glossary.md`, `docs/conf.py`, `docs/_static/css/custom.css` | pydata-sphinx-theme, builds with `-W`, cards / tabs / custom admonitions |
| 1 · On-disk | `spec/on-disk/` — index, container, coordinate-systems, images, labels, shapes, points, tables, ngff-compatibility, versions, next (0.3 placeholder) | complete first draft; derived from `spatialdata` 0.6.0 code and freshly written stores; consistent with `format.py` |
| 2 · In-memory | `spec/in-memory/index.md` (general, what every implementation documents); `python/` — index, elements, transformations, implementation-guide; `r/`, `js/` placeholders | Python first draft complete; R, JS placeholders |
| 3 · Semantic | `spec/semantic/` — index, options (Q1–Q11), prior-art | options for community review; nothing normative |

Build: `hatch run docs:build` (warnings are errors). Open: `hatch run docs:open`.

## Facts a maintainer must verify

Each item is stated in the spec as fact; I derived it from code or observed output, not from a
written source. Wrong ones must be fixed in the text, not worked around.

1. **Pixel-centre convention** (`coordinate-systems.md`): pixel `i` covers `[i, i+1)`, centre
   `i + 0.5`. Derived from `compute_coordinates()` (`np.arange(n) + 0.5`). Confirm this is the intended
   contract and not an xarray display choice.
2. **Labels background** (`labels.md`): "value `0` is background and MUST NOT be treated as an
   instance". Derived from `get_element_instances(return_background=False)` and join behaviour.
   Decide whether MUST or SHOULD.
3. **Boolean labels** (`labels.md`, `elements.md`): allowed because `_validate_labels_dtype` accepts
   `np.bool_`. Keep or restrict to integers?
4. **DataTree variable name** (`elements.md`): stated as arbitrary ("MAY be `image`"), per your
   instruction. But `spatialdata` code reads `["scale0"]["image"]` in `_validate_labels_dtype`,
   `overwrite_channel_names`, `validate_table_in_spatialdata`. Either the spec says MUST be `image`,
   or those call sites are fixed to use the first data variable. Decision needed.
5. **Affine matrix layout on disk** (`coordinate-systems.md`): rows = output axes, columns = input
   axes + translation column, homogeneous row omitted, output axis order may differ from input.
   Derived from one written example (`cyx → cxy`). Verify against `NgffAffine.to_dict`.
6. **Sequence inner `input`/`output` names** are meaningless (observed: inner outputs named
   `"global"` regardless of target). Verify and consider fixing the writer.
7. **Shapes MUST contain ≥ 1 row**: from `ShapesModel.validate`. Intended?
8. **Points `axes` attribute is alphabetically sorted** (`_write_metadata` sorts) — coincides with
   `x, y, z`; spec states the list must match columns. Fine as long as axes stay `x,y,z`.
9. **Table `version` at top level** (not under `spatialdata_attrs`) — inconsistent with other
   elements; documented as-is. Consider harmonising in the next tables version.
10. **Raster 0.1 `channels_metadata`** legacy key: documented from the reader; no 0.1 store was
    generated. Verify field shape.
11. **`image-label.version`** is `"0.5"` in Zarr v3 stores while `ome.version` is
    `"0.5-dev-spatialdata"`. Documented as observed.
12. **Pre-versioned stores** (no root `spatialdata_attrs`) are read as container 0.1 — from
    `read_zarr`.
13. **Table annotating a missing element** only warns in `SpatialData.__init__`; string/non-string
    instance dtype mismatch raises. Documented in `in-memory/python/index.md` as "a mismatch raises";
    tighten wording if needed.
14. **sopa** conventions in `prior-art.md` are described from memory (`sdata.attrs` role keys); the
    constants file could not be fetched. Verify key names before citing precisely.
15. **spatialdata-db** is cited from the Lamin schema you shared locally; the repository is not
    public. Confirm how you want it cited.
16. **RFC-5 status**: `ngff-compatibility.md` says NGFF 0.6 "is expected to include RFC-5". Check
    current status before publishing.

## Decisions pending

See `planning/QUESTIONS.md` (Q1–Q13 answered by defaults; Q14–Q20 added after drafting).

## Figures to add

Suggested schematics, with placement. All can start as SVG in `docs/_static/img/` and be inserted
with `![alt](/_static/img/name.svg)`; the ASCII versions stay as fallback in the source.

| # | Figure | Page and position | Replaces |
|---|--------|-------------------|----------|
| F1 | Three-layer stack (on-disk / in-memory per language / semantic) | `docs/index.md`, "How the layers relate" | ASCII box diagram |
| F2 | Store tree with one element of each type, annotated with where metadata lives | `spec/on-disk/index.md`, "A store at a glance" | ASCII tree (keep both) |
| F3 | Elements mapping into named coordinate systems (arrows from intrinsic to `global`, `micron`) | `spec/on-disk/coordinate-systems.md`, top | ASCII arrows |
| F4 | Half-pixel convention: pixel grid, centres at `i + 0.5`, one scale transform applied | `spec/on-disk/coordinate-systems.md`, "Axes" | none |
| F5 | Multiscale raster: levels, per-level `scale`, element transformation composed | `spec/on-disk/images.md`, "Attributes" | none |
| F6 | Table ↔ regions: `obs[region_key]`, `obs[instance_key]` linking to label values and shape index | `spec/on-disk/tables.md`, "Annotation rules" | ASCII table |
| F7 | `DataTree` with per-level `attrs["transform"]` | `spec/in-memory/python/elements.md`, DataTree tab | ASCII tree |
| F8 | Role map / entities / samples object and what it points to | `spec/semantic/options.md`, Q1 | none |

Decision (Q8 in QUESTIONS.md): hand-drawn SVG vs Mermaid source. Mermaid would cover F1, F3, F6,
F7, F8 well; F2, F4, F5 are better drawn.

## When to start a new spec version

Triggers and procedure are published on `spec/on-disk/next.md`; the operational checklist for
maintainers:

1. **Trigger.** A pull request in `scverse/spatialdata` adds a `...FormatVxx` class to
   `src/spatialdata/_io/format.py`, or an issue labelled `format-change` is accepted, or NGFF /
   AnnData / GeoParquet release a version to adopt (NGFF 0.6 is the known upcoming one).
2. **Open the version.** Rename `spec/on-disk/next.md` content into a "0.3 (draft)" tab set on the
   affected chapters (or a `spec/on-disk/0.3/` directory if the change is large; QUESTIONS.md Q13),
   keep 0.2 as the default tab, mark the new tab {bdg-warning-line}`draft`.
3. **Implement and exercise.** The `spatialdata` implementation ships the new format class as
   non-default; regenerate the example stores; run `tools/check_format_versions.py`.
4. **Promote.** When a `spatialdata` release writes the new version by default: make it the default
   tab, move the previous version's differences into tabs and `versions.md`, update the badges on
   `docs/index.md` and section indexes, tag the repository (`ondisk-0.3`), add a CHANGELOG entry.
5. **Same for the other layers.** In-memory pages are re-synced after each implementation release
   (the version badge names the release). Semantic conventions get their first number (0.1) when
   the first set of options is accepted; until then they stay {bdg-warning-line}`under discussion`.

## Source of truth for on-disk versions

`spatialdata/_io/format.py` (scverse/spatialdata). `tools/check_format_versions.py` verifies that
`spec/on-disk/versions.md` and `images.md` agree with it (versions per component, current versions,
Zarr format per container, allowed combinations, container 0.1 defaults, NGFF version strings). It
passed against `spatialdata` 0.6.0 on 2026-09-11. Consider running it in CI with `spatialdata`
installed (QUESTIONS.md Q23).

## Drift detection (set up, not yet run in CI)

Two-stage system; see `conformance/README.md`.

1. **Deterministic**: `conformance/fixture.py` → `generate_fingerprint.py` → `compare_fingerprints.py`
   against `conformance/fingerprints/baseline.json`; plus `tools/check_format_versions.py`. Runs locally
   with `hatch run drift:check`, and in `.github/workflows/spec-drift.yml` (weekly against PyPI, on
   demand against `main`/any tag). Verified locally: deterministic across runs, and a synthetic change
   (new points version) is reported with the pages to check.
2. **Agent triage (optional)**: the workflow's `agent` job hands the report to
   `anthropics/claude-code-action` to open a *draft* PR. Untested (needs the `ANTHROPIC_API_KEY`
   secret and a run on GitHub). Inputs verified against the action's docs; `gh pr create --draft`
   from inside the action is documented as the intended path but should be confirmed on the first
   run. Keep it opt-in (`draft_pr_with_agent`), never scheduled.

Findings from setting it up (all now reflected in the spec):

- **The detector found real, unversioned drift between 0.6.0 and 0.8.0**: pyramid arrays `s0…`
  instead of `0…`, a per-level `translation` of `(scale − 1)/2`, `multiscales[0].name = "image"`,
  `image-label` added to multiscale labels in Zarr v2, AnnData 0.13 `nullable-string-array` indices.
  `images.md`, `labels.md`, `coordinate-systems.md`, `tables.md`, `shapes.md` were updated and
  `versions.md` gained a "Changes without a version bump" table plus an open question on whether
  such changes should bump the raster version (QUESTIONS.md Q28).

- **Latest `spatialdata` release is 0.8.0 (2026-07-02), not 0.6.** `format.py` is byte-identical
  between 0.6.0 and 0.8.0 apart from an import, so the on-disk chapters hold for 0.6–0.8. The
  in-memory chapters were derived from the `main` checkout (post-0.8.0), which removed the
  `xarray-schema` dependency that 0.6.0 still used; badges now say `spatialdata 0.8`. Re-verify the
  in-memory prose against the 0.8.0 fingerprint (QUESTIONS.md Q24).
- The baseline must be generated with the release the spec describes; `hatch run drift:baseline`
  installs the latest PyPI release into the `drift` env.
- Better still would be to run `spec-drift` from the `spatialdata` repository's CI on every pull
  request (shift-left): a format change would then fail there until the spec is updated. Needs a
  small workflow in scverse/spatialdata that checks out this repo and runs `hatch run drift:check`
  against the PR's build.

## Remaining work

Ordered by value.

1. **Review pass by maintainers** on the facts above, then remove the "draft" announcement banner in
   `docs/conf.py` for the on-disk section.
2. **Schemas**: port `SpatialData.validate` JSON schemas (MIT, Hugo Gruson) into `schemas/<version>/`
   with attribution and a `schemas/README.md`; add schemas for shapes, points, tables, container.
   Link them from each chapter under a "Machine-readable" heading. Keep prose authoritative.
3. **Examples and conformance**: copy or generate small stores into `examples/` (BSD-3) and add a
   `conformance/` runner in the spirit of `ome/ngff-spec` (`ome_zarr_conformance.py`), so R/JS readers
   can self-test. Wire the `spatialdata-notebooks` daily job to push here, or the other way round.
4. **Hosting**: when the repository becomes public, import it on Read the Docs and enable pull
   request builds (five steps in `docs/contributing_to_the_spec.md`, "Hosting"); then fix the slug in
   `docs/conf.py` and `pyproject.toml`. Until then, previews are the `site-html` CI artifact.
5. **Versioning policy** page content (currently an open-question box in `versions.md`) and a
   release procedure: tag `spec-0.2`, publish on Read the Docs with a version switcher.
6. **Contribution process** (`docs/contributing_to_the_spec.md`): an RFC-like flow for format
   changes; issue templates for "format change proposal" and "semantic convention proposal".
7. **Other in-memory implementations**: `spec/in-memory/r/` (spatialdataR) and `spec/in-memory/js/`
   (SpatialData.js / Vitessce loaders) once their maintainers can contribute.
8. **Semantic conventions**: collect feedback (label `semantic-conventions`), then promote the
   agreed options to a normative `spec/semantic/conventions.md` with its own version.
9. **Enable drift detection in CI**: add the `ANTHROPIC_API_KEY` secret (only if the agent job is wanted), create the `spec-drift` issue label, run the workflow once by hand against `pypi` and once against `main`, then propose the shift-left job to scverse/spatialdata.
10. **Link checking** in CI: `sphinx-build -b linkcheck docs docs/_build/linkcheck`.
11. **Housekeeping**: update `.github/ISSUE_TEMPLATE`, `PULL_REQUEST_TEMPLATE.md`; delete
   `planning/` once its content lives in issues; remove the stale `docs/_build` from the working tree
   (it is git-ignored).
