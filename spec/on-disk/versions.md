# Version history

Every component of a store carries its own {term}`format version`. The **container version**
selects the Zarr format and constrains which element versions can appear. Element versions evolve
independently and are bumped only when the bytes on disk change.

## Container versions

| Container | Zarr | First `spatialdata` release | Allowed element versions |
|-----------|------|-----------------------------|--------------------------|
| **0.2** (current) | v3 | 0.6.0 (September 2025) | raster 0.3 · shapes 0.3 · points 0.2 · tables 0.2 |
| 0.1 | v2 | pre-versioned stores are read as 0.1 | raster 0.1, 0.2 · shapes 0.1, 0.2 · points 0.1 · tables 0.1 |

Writing container 0.1 is deprecated in `spatialdata` and emits a warning. Reading it is supported.

## Element versions

| Component | Version | Introduced in | What changed |
|-----------|---------|---------------|--------------|
| raster | 0.1 | initial | NGFF 0.4 layout, `multiscales[0].version = "0.4"`, channel names in a legacy `channels_metadata` key |
| raster | 0.2 | 0.4.0 (February 2025) | `multiscales[0].version = "0.4-dev-spatialdata"` to signal the RFC-5-style transformations; channel names in `omero.channels` |
| raster | **0.3** | 0.6.0 (September 2025) | Zarr v3; metadata under the `ome` key; `ome.version = "0.5-dev-spatialdata"`; `image-label.version = "0.5"` |
| shapes | 0.1 | initial | geometries as ragged Zarr arrays (`coords`, `offset*`, `Index`, `radius`) with `spatialdata_attrs.geos` |
| shapes | 0.2 | 0.2.2 (July 2024) | geometries in `shapes.parquet` (GeoParquet 1.0.0, WKB) |
| shapes | **0.3** | 0.6.0 | Zarr v3 group; payload unchanged; GeoArrow encoding allowed as an option |
| points | 0.1 | initial | `points.parquet/` Parquet dataset |
| points | **0.2** | 0.6.0 | Zarr v3 group; payload unchanged |
| tables | 0.1 | initial | AnnData Zarr v2 + `ngff:regions_table` attributes |
| tables | **0.2** | 0.6.0 | AnnData Zarr v3 (`anndata` ≥ 0.12); attributes unchanged |

The version of each element is read from `spatialdata_attrs.version` (raster, shapes, points) or
from the top-level `version` attribute (tables); see {doc}`container`.

## Source of truth

The authoritative list of versions is the set of format classes in
[`spatialdata/_io/format.py`](https://github.com/scverse/spatialdata/blob/main/src/spatialdata/_io/format.py).
This page must agree with it. The classes, as of `spatialdata` 0.6:

| Class | Component | Version | Zarr | NGFF base | Version string written |
|-------|-----------|---------|------|-----------|------------------------|
| `RasterFormatV01` | raster | 0.1 | v2 | `FormatV04` | `"0.4"` |
| `RasterFormatV02` | raster | 0.2 | v2 | `FormatV04` | `"0.4-dev-spatialdata"` |
| `RasterFormatV03` | raster | 0.3 | v3 | `FormatV05` | `"0.5-dev-spatialdata"` |
| `ShapesFormatV01` | shapes | 0.1 | v2 | `FormatV04` | — |
| `ShapesFormatV02` | shapes | 0.2 | v2 | `FormatV04` | — |
| `ShapesFormatV03` | shapes | 0.3 | v3 | `FormatV05` | — |
| `PointsFormatV01` | points | 0.1 | v2 | `FormatV04` | — |
| `PointsFormatV02` | points | 0.2 | v3 | `FormatV05` | — |
| `TablesFormatV01` | tables | 0.1 | v2 | `FormatV04` | — |
| `TablesFormatV02` | tables | 0.2 | v3 | `FormatV05` | — |
| `SpatialDataContainerFormatV01` | container | 0.1 | v2 | `FormatV04` | — |
| `SpatialDataContainerFormatV02` | container | 0.2 | v3 | `FormatV05` | — |

"NGFF base" is the `ome-zarr-py` format class each SpatialData class derives from; it fixes the Zarr
format. Only raster elements write an NGFF version string. When `spatialdata` writes container 0.1
on request, the element versions default to raster 0.2 · shapes 0.2 · points 0.1 · tables 0.1.

## Changes without a version bump

Some differences between stores come from `spatialdata` releases or their dependencies without a
change of any format version. They are within what this specification allows, but implementers
should know them:

| Written by | Difference |
|------------|------------|
| `spatialdata` 0.8 (ome-zarr-py 0.19) vs 0.6 (ome-zarr-py 0.12) | pyramid arrays named `s0`, `s1`, … instead of `0`, `1`, …; a `translation` of `(scale − 1) / 2` follows each per-level `scale`; `multiscales[0].name` is `"image"` instead of the group path; multiscale labels in Zarr v2 stores gain the missing `image-label` key |
| `anndata` ≥ 0.13 vs 0.12 | string indices and string columns use the `nullable-string-array` encoding (a group with `values` and `mask`) instead of `string-array` |
| `pyarrow` / `pandas` releases | string columns in Parquet payloads are `large_string` instead of `string` |

:::{admonition} Open question
:class: open-question

Should byte-level changes such as the pyramid array names bump the raster format version, even when
readers that follow `path` are unaffected? Today they do not.
:::

## Migrating a store

`spatialdata` reads every version listed above. Reading a store and writing it to a new location
produces the current versions:

```python
import spatialdata as sd

sdata = sd.read_zarr("old.zarr")  # any container/element version
sdata.write("new.zarr")  # container 0.2, Zarr v3
```

No in-place migration is defined; a migrated store is a new store.

## Next version

Candidate changes and the procedure for opening version 0.3 are on {doc}`next`.

## Versioning policy

:::{admonition} Open question
:class: open-question

The rules for bumping versions, for how long old versions stay readable, and for how this
specification is versioned relative to the container version are not yet written. The proposal
under discussion: the specification version equals the container version; element versions are
listed inside it; a specification release is tagged in this repository when `spatialdata` ships
the corresponding writer.
:::

## Conformance resources

- **Example stores.** The `spatialdata-notebooks` repository regenerates small stores covering every
  element type and transformation type daily from the `main` branch of `spatialdata`:
  [`notebooks/developers_resources/storage_format`](https://github.com/scverse/spatialdata-notebooks/tree/main/notebooks/developers_resources/storage_format).
  A reader that handles those stores handles any store of the same version.
- **JSON schemas.** [SpatialData.validate](https://github.com/Huber-group-EMBL/SpatialData.validate)
  (R package, MIT licence, author Hugo Gruson, EMBL) ships JSON schemas for the raster metadata of
  format 0.1 and 0.3. Porting them into this repository is planned.
