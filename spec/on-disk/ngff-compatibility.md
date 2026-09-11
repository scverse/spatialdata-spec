# NGFF compatibility

SpatialData reuses OME-NGFF where NGFF has a definition and extends it where it has none. Because
the transformations model that SpatialData needs is only available in the NGFF proposal
[RFC-5](https://ngff.openmicroscopy.org/rfc/5/), no released NGFF version is followed exactly. The
plan is to converge on NGFF 0.6, which is expected to include RFC-5.

## Feature matrix

Legend: ✅ used as specified · 🔒 used with restrictions · ➕ extended · ➖ not used · ✗ not defined
by that version.

| Feature | NGFF 0.4 | NGFF 0.5 | NGFF 0.6 (RFC-5 draft) | SpatialData (container 0.2) |
|---------|:--------:|:--------:|:----------------------:|:---------------------------:|
| Zarr format | v2 | v3 | v3 | v3 (v2 for container 0.1) |
| `ome` namespace in group attributes | ✗ | ✅ | ✅ | ✅ (`ome.version` is `"0.5-dev-spatialdata"`) |
| `multiscales` | ✅ | ✅ | ✅ | 🔒 exactly one entry |
| `axes` names and types | ✅ | ✅ | ✅ | 🔒 only `c` (channel), `z`, `y`, `x` (space); no `time`, no custom |
| Per-dataset `scale` / `translation` | ✅ | ✅ | ✅ | 🔒 `scale` only |
| Multiscale-level `coordinateTransformations` | 🔒 scale/translation | 🔒 scale/translation | ✅ typed, named systems | ➕ RFC-5 types with **inlined** `input`/`output` |
| `coordinateSystems` list | ✗ | ✗ | ✅ | ➖ systems are inlined in each transformation |
| Transformation types beyond scale/translation | ✗ | ✗ | ✅ | ➕ identity, affine, mapAxis, sequence |
| `omero.channels[*].label` | ✅ | ✅ | ✅ | ✅ (other `omero` fields ignored) |
| `image-label` | ✅ | ✅ | ✅ | 🔒 only `version` written; `colors`/`properties` tolerated |
| `labels` listing on the labels group | ✅ | ✅ | ✅ | ✅ |
| `plate`, `well` | ✅ | ✅ | ✅ | ➖ |
| `bioformats2raw.layout` | ✅ | ✅ | ✅ | ➖ |
| Shapes | ✗ | ✗ | ✗ | ➕ GeoParquet in a Zarr group |
| Points | ✗ | ✗ | ✗ | ➕ Parquet dataset in a Zarr group |
| Tables | ✗ | ✗ | ✗ | ➕ AnnData + `ngff:regions_table` attributes |
| Container layout (`images/`, `labels/`, …) | ✗ | ✗ | ✗ | ➕ |
| Component versioning (`spatialdata_attrs.version`) | ✗ | ✗ | ✗ | ➕ |

## What an NGFF reader can do with a SpatialData store

- Open any `images/<name>` or `labels/<name>` group as a multiscale image, if it accepts the
  unknown version string and ignores `multiscales[0].coordinateTransformations`. The arrays, axes,
  per-level scales and channel labels are standard.
- Discover labels through the `labels` group listing.
- It will not see shapes, points or tables, and it will not know how elements align.

## What a SpatialData reader must do beyond NGFF

- Read the five type groups and per-element versions ({doc}`container`).
- Parse RFC-5-style transformations with inlined coordinate systems ({doc}`coordinate-systems`).
- Read GeoParquet, Parquet and AnnData payloads.

## Path to convergence

:::{admonition} Open question
:class: open-question

When NGFF 0.6 is released, the intended changes are: adopt the released `ome.version`, move
coordinate systems into a `coordinateSystems` list and reference them by name, and keep shapes,
points and tables as SpatialData extensions until NGFF defines equivalents. Whether the
transformations on shapes and points should also move to a `coordinateSystems`-based encoding is
open. Track progress in the `spatialdata` repository.
:::
