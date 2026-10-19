# Next version (0.3)

Candidate changes for the next storage format version, 0.3. The current version is **0.2**
({ref}`Specification <spec>`). Accepted changes appear on the specification page in the draft of
0.3: select *container-format-0.3 (draft)* in the navigation. How to propose a change is in
{doc}`../../contributing_to_the_spec`; large changes come with an {doc}`RFC <../../rfcs>`.

## When a new version starts

A new version is opened when at least one of these is true:

- a change to the stored bytes is needed (new key, new payload, changed meaning of an existing
  key), which in `spatialdata` corresponds to adding a `...FormatVxx` class to
  `spatialdata/_io/format.py`;
- a new element type is introduced;
- an upstream standard the format depends on (NGFF, AnnData, GeoParquet) releases a version worth
  adopting, such as NGFF 0.6 with RFC-5 transformations.

Bug fixes to the prose, clarifications and non-normative additions do not open a new version.

## Candidate changes collected so far

Collected while documenting 0.2; none is agreed yet.

| Candidate | Origin | Scope |
|-----------|--------|-------|
| Adopt released NGFF 0.6 / RFC-5: `coordinateSystems` list, transformations referencing systems by name, released `ome.version` | {doc}`ngff-compatibility` | raster; possibly shapes and points |
| Write real axis units instead of the `"unit"` placeholder | {ref}`Coordinate systems and transformations <spec-coordinate-systems>` | all spatial elements |
| Record which element a points `instance_key` refers to (`instance_key_element`) | semantic conventions draft ([#6](https://github.com/scverse/spatialdata-spec/pull/6)) | points |
| Move the table `version` under `spatialdata_attrs` like the other element types | {ref}`Tables <spec-tables>` | tables |
| Give the sequence inner `input` / `output` objects meaningful names or drop them | {ref}`Coordinate systems and transformations <spec-coordinate-systems>` | all spatial elements |
| Persist per-element user attributes | semantic conventions draft ([#6](https://github.com/scverse/spatialdata-spec/pull/6)) | all elements |

## Release

Accepted changes are implemented in `spatialdata` behind a non-default format class, and the
example stores are regenerated. When a `spatialdata` release writes the new version by default, the draft becomes the current
version: "(draft)" is dropped from the tab labels, the 0.2 tabs become the previous version,
{doc}`versions` is updated, and the repository is tagged.
