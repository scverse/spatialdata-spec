# Storage format version history

Each **storage format version** is one row of the {ref}`compatibility-matrix`: the container
format, the element versions and the Zarr and OME-Zarr versions that a `spatialdata` release
writes. Each storage format version encodes one version of the **abstract data model**
({doc}`data model versions <data-model-versions>`); a change to the data model always comes with a
new storage format version.

Within a store, the storage format is identified by its **container format** version, which a store
records in its root attributes as `spatialdata_attrs.version`, for example `"0.2"` (from `spatialdata`
0.3.0; stores without it are read as container 0.1). The store records the version number, not a
format name. The container version selects the Zarr format and
fixes which element versions can appear. Each element also records its own version, which changes
only when its stored bytes change. Since container 0.2, the container version changes whenever an
element version does, so it is the single version string of a store; within container 0.1, element
versions changed on their own (see the {ref}`compatibility-matrix`).

Several version numbers are involved. A store records the container format, element and NGFF
versions (and optionally the writing software's version), but not the storage format or data
model version.

| Version | Identifies | Recorded in a store as | Storage format 0.5 |
|---------|------------|------------------------|--------------------|
| Storage format (= specification) | one version of this specification: container format, element versions, Zarr and NGFF versions | not recorded; the specification is tagged `storage-format-<version>` | 0.5 |
| Data model | the {doc}`abstract data model <data-model-versions>` the storage format encodes | not recorded | 1.0 |
| Container format | the store layout, the Zarr format and the allowed element versions | root `spatialdata_attrs.version` | `"0.2"` |
| Element | the encoding of one element type | the element's `spatialdata_attrs.version` (raster: from storage format 0.2); for tables, the top-level `version` | raster `"0.3"`, shapes `"0.3"`, points `"0.2"`, tables `"0.2"` |
| NGFF version string | the NGFF metadata of a raster element | `ome.version` (Zarr v3) or `multiscales[0].version` (Zarr v2) | `"0.5-dev-spatialdata"` |
| `spatialdata` release | the software that wrote the store; informational only | root `spatialdata_attrs.spatialdata_software_version`, if present | for example `"0.6.0"` |

(storage-next)=
## Upcoming version (0.6)

Candidate changes for storage format 0.6 (container format 0.3); none is agreed yet.
[Propose a change](https://github.com/scverse/spatialdata-spec/issues/new), discuss it on
[Zulip](https://scverse.zulipchat.com/#narrow/channel/443514-spatialdata-dev), or see {doc}`how to contribute <contributing>`.

| Candidate | Origin | Scope |
|-----------|--------|-------|
| Adopt released NGFF 0.6 / RFC-5: `coordinateSystems` list, transformations referencing systems by name, released `ome.version` | {doc}`RFC 1 <rfcs>` (planned) | raster; possibly shapes and points |
| Write real axis units instead of the `"unit"` placeholder | {ref}`Coordinate systems and transformations <storage-coordinate-systems-encoding>` | all spatial elements |
| Record which element a points `instance_key` refers to (`instance_key_element`) | semantic conventions draft ([#6](https://github.com/scverse/spatialdata-spec/pull/6)) | points |
| Move the table `version` under `spatialdata_attrs` like the other element types | {ref}`Tables <storage-tables-attributes>` | tables |
| Give the sequence inner `input` / `output` objects meaningful names or drop them | {ref}`Coordinate systems and transformations <storage-coordinate-systems-transformation-types>` | all spatial elements |
| Decide whether byte-level changes that readers following the specification do not notice (such as the pyramid array names) bump the element version; today they do not | {ref}`Changes without a version bump <storage-changes-without-bump>` | all elements |
| Persist per-element user attributes | semantic conventions draft ([#6](https://github.com/scverse/spatialdata-spec/pull/6)) | all elements |

(storage-versions)=
## Versions

| Storage format | Data model | Container format (`spatialdata_attrs.version`) | Status |
|----------------|------------|---------------------------------------------------|--------|
| 0.6 | 1.0 (provisional) | `"0.3"` | upcoming: no accepted changes yet; its data model version depends on the RFCs it adopts; see {ref}`storage-next` |
| **0.5** | **1.0** | `"0.2"` | current; written by `spatialdata` ≥ 0.6 by default |
| 0.4 | 1.0 | `"0.1"` | deprecated; written by `spatialdata` ≥ 0.6 on request |
| 0.3 | 1.0 | `"0.1"` | deprecated; written by `spatialdata` 0.4.0 – 0.5.x |
| 0.2 | 1.0 | `"0.1"`, or absent | deprecated; written by `spatialdata` 0.2.2 – 0.3.x |
| 0.1 | 1.0 | absent, read as `"0.1"` | deprecated; written by `spatialdata` < 0.2.2 |

(compatibility-matrix)=
## Compatibility matrix

Each row is a storage format version: what a `spatialdata` release writes, and the version of the
abstract data model it encodes.

| Storage format | Data model | `spatialdata` writes | container | raster | shapes | points | tables | Zarr | OME-Zarr (NGFF) |
|----------------|------------|----------------------|-----------|--------|--------|--------|--------|------|-----------------|
| **0.5** | **1.0** | ≥ 0.6.0 (default) | **0.2** | **0.3** | **0.3** | **0.2** | **0.2** | v3 | 0.5 (`"0.5-dev-spatialdata"`) |
| 0.4 | 1.0 | ≥ 0.6.0 (container 0.1 on request, deprecated) | 0.1 | 0.2 | 0.2 | 0.1 | 0.1 | v2 | 0.4 (`"0.4-dev-spatialdata"`) |
| 0.3 | 1.0 | 0.4.0 – 0.5.x | 0.1 | 0.2 | 0.2 | 0.1 | 0.1 | v2 | 0.4 (`"0.4-dev-spatialdata"`) |
| 0.2 | 1.0 | 0.2.2 – 0.3.x | 0.1 (recorded from 0.3.0) | 0.1 | 0.2 | 0.1 | 0.1 | v2 | 0.4 (`"0.4"`) |
| 0.1 | 1.0 | < 0.2.2 | 0.1 (not recorded) | 0.1 | 0.1 | 0.1 | 0.1 | v2 | 0.4 (`"0.4"`) |

A container 0.2 store holds only the element versions in the first row. A container 0.1 store can
hold any of the element versions in the other rows; stores without a container version are read as
container 0.1. `spatialdata` reads every combination listed here.

## Element versions

| Component | Version | Introduced in | What changed |
|-----------|---------|---------------|--------------|
| raster | 0.1 | initial | NGFF 0.4 layout, `multiscales[0].version = "0.4"`; channel names in `channels_metadata` (up to 0.1.2) or `omero.channels` (from 0.2.0); `spatialdata_attrs.version` from 0.2.2 |
| raster | 0.2 | 0.4.0 (April 2025) | `multiscales[0].version = "0.4-dev-spatialdata"` to signal the RFC-5-style transformations |
| raster | **0.3** | 0.6.0 (November 2025) | Zarr v3; metadata under the `ome` key; `ome.version = "0.5-dev-spatialdata"`; `image-label.version = "0.5"` |
| shapes | 0.1 | initial | geometries as ragged Zarr arrays (`coords`, `offset*`, `Index`, `radius`) with `spatialdata_attrs.geos` |
| shapes | 0.2 | 0.2.2 (August 2024) | geometries in `shapes.parquet` (GeoParquet 1.0.0, WKB) |
| shapes | **0.3** | 0.6.0 | Zarr v3 group; payload unchanged |
| points | 0.1 | initial | `points.parquet/` Parquet dataset |
| points | **0.2** | 0.6.0 | Zarr v3 group; payload unchanged |
| tables | 0.1 | initial | AnnData Zarr v2 + `ngff:regions_table` attributes; a single table in `table/table` up to 0.0.16, `tables/<name>` from 0.1.0 |
| tables | **0.2** | 0.6.0 | AnnData Zarr v3 (`anndata` ≥ 0.12); attributes unchanged |

The version of each element is read from `spatialdata_attrs.version` (raster, shapes, points) or
from the top-level `version` attribute (tables); see
{ref}`Element type and version <storage-datasets-element-type-and-version>`.

(storage-changes-without-bump)=
## Changes without a version bump

Some differences between stores come from `spatialdata` releases or their dependencies without a
change of any format version. They are within what this specification allows, but implementers
should know them:

| Written by | Difference |
|------------|------------|
| `spatialdata` 0.8 (ome-zarr-py 0.19) vs 0.6 (ome-zarr-py 0.12) | pyramid arrays named `s0`, `s1`, … instead of `0`, `1`, …; a `translation` of `(scale − 1) / 2` follows each per-level `scale`; `multiscales[0].name` is `"image"` instead of the group path; multiscale labels in Zarr v2 stores gain the missing `image-label` key |
| `spatialdata` ≥ 0.7.0 | shapes 0.2 and 0.3 may use the GeoArrow geometry encoding (on request; WKB by default) |
| `spatialdata` 0.6 and later vs earlier | per-level `translation` and `s0`, `s1`, … names depend on the installed ome-zarr-py (0.14 for the names, 0.18 for the translation) |
| `anndata` ≥ 0.13 vs 0.12 | string indices and string columns use the `nullable-string-array` encoding (a group with `values` and `mask`) instead of `string-array` |
| `pyarrow` / `pandas` releases | string columns in Parquet payloads are `large_string` instead of `string` |
