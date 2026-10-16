# Next version (0.3)

{bdg-primary}`on-disk` {bdg-light}`placeholder` {bdg-warning-line}`not started`

This page is reserved for the next on-disk format version. Nothing here is decided. The current
version is **0.2** ({ref}`Specification <spec>`); version 0.1 is legacy and documented inline in tabs.

## When a new version starts

A new on-disk version is opened when at least one of these is true:

- a change to the bytes on disk is needed (new key, new payload, changed meaning of an existing
  key), which in `spatialdata` corresponds to adding a `...FormatVxx` class to
  `spatialdata/_io/format.py`;
- a new element type is introduced;
- an upstream standard the format depends on (NGFF, AnnData, GeoParquet) releases a version worth
  adopting, such as NGFF 0.6 with RFC-5 transformations.

Bug fixes to the prose, clarifications and non-normative additions do not open a new version.

## Candidate changes collected so far

Collected while documenting 0.2; none is agreed. Each needs an issue labelled `format-change`.

| Candidate | Origin | Scope |
|-----------|--------|-------|
| Adopt released NGFF 0.6 / RFC-5: `coordinateSystems` list, transformations referencing systems by name, released `ome.version` | {doc}`ngff-compatibility` | raster; possibly shapes and points |
| Write real axis units instead of the `"unit"` placeholder | {ref}`Coordinate systems and transformations <spec-coordinate-systems>` | all spatial elements |
| Record which element a points `instance_key` refers to (`instance_key_element`) | {doc}`../semantic/options` Q4 | points |
| Move the table `version` under `spatialdata_attrs` like the other element types | {ref}`Tables <spec-tables>` | tables |
| Give the sequence inner `input` / `output` objects meaningful names or drop them | {ref}`Coordinate systems and transformations <spec-coordinate-systems>` | all spatial elements |
| Persist per-element user attributes (needed by semantic conventions option Q1-C) | {doc}`../semantic/options` | all elements |

## Process

1. Open an issue with the label `format-change`: motivation, exact bytes that change, migration
   path, affected implementations.
2. Discussion and a decision recorded in the issue.
3. Draft the text on this page (tabs "0.3 (draft)" next to "0.2"), implement it in `spatialdata`
   behind a non-default format class, regenerate the example stores.
4. When a `spatialdata` release writes the new version by default, this page becomes the current
   specification, the previous one moves to tabs and {doc}`versions`, and the repository is tagged.
