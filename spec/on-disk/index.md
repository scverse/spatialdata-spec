# On-disk format

{bdg-primary}`on-disk`

The SpatialData on-disk format stores one spatial omics dataset as a Zarr hierarchy with embedded
Parquet files. It reuses [OME-NGFF](https://ngff.openmicroscopy.org) for raster data and for
coordinate transformations, [GeoParquet](https://geoparquet.org) for shapes, Parquet for points,
and the [AnnData on-disk format](https://anndata.readthedocs.io/en/stable/fileformat-prose.html)
for tables. This specification defines only what those standards leave open and where SpatialData
deviates from them.

## Versions

The format is versioned by the container format. Each chapter covers all versions: where versions
differ, the chapter shows synced tabs, newest first, so that selecting a version on one page selects
it on all pages. Sections that exist only in some versions carry a badge such as
{bdg-secondary}`container 0.3 only`.

| Version | Status |
|---------|--------|
| `spatialdata-container-format-0.3` | {bdg-light}`incoming`: approved changes appear in the 0.3 tabs of the chapters (none yet) |
| `spatialdata-container-format-0.2` | released; the tab shown by default |
| `spatialdata-container-format-0.1` | released; written only on request (deprecated) |

How element formats, Zarr, OME-Zarr and `spatialdata` releases follow from the container format is
in the {ref}`compatibility-matrix`. Changes not yet assigned to a version are collected in
{doc}`next`.

## Design principles

- **Reuse existing storage formats.** A dataset is a collection of {term}`elements <element>`, and
  each element is stored in an existing format where one is available (OME-Zarr, GeoParquet,
  Parquet, AnnData). The SpatialData format adds only the extra metadata and the coordination
  between the elements and the store.
- **Alignment is by coordinate system, not by reference.** In container formats 0.1 and 0.2, no
  element points to another; elements that map into the same
  {doc}`coordinate system <coordinate-systems>` are aligned. With NGFF 0.6 support, a candidate
  change (see {doc}`next`), elements will *belong to* coordinate systems.
- **Do not restate other specifications.** What the NGFF, AnnData, Zarr and Parquet specifications
  define is linked, not rewritten here.
- **No biological vocabulary.** The format knows elements, instances and variables, not cells or
  genes. That mapping is the subject of the {doc}`semantic conventions <../semantic/index>`.

## A store at a glance

A `spatialdata-container-format-0.2` store:

```text
dataset.zarr/                       Zarr v3 group
├── zarr.json                       spatialdata_attrs.version = "0.2"  (+ consolidated metadata)
├── images/
│   └── <name>/                     NGFF multiscale image, axes cyx or czyx
│       ├── zarr.json               ome.multiscales, ome.omero.channels, spatialdata_attrs
│       ├── s0/                     full resolution array (name given by datasets[0].path)
│       └── s1/ s2/ ...             optional downsampled levels
├── labels/
│   └── <name>/                     NGFF multiscale image with labels metadata, axes yx or zyx
├── shapes/
│   └── <name>/
│       ├── zarr.json               encoding-type, axes, coordinateTransformations, spatialdata_attrs
│       └── shapes.parquet          single GeoParquet file: geometry [, radius] [, extra columns]
├── points/
│   └── <name>/
│       ├── zarr.json               encoding-type, axes, coordinateTransformations, spatialdata_attrs
│       └── points.parquet/         multi-file Parquet dataset: x, y [, z] [, extra columns]
│           └── part.0.parquet
└── tables/
    └── <name>/                     AnnData Zarr + region; region_key, instance_key name obs columns
```

## Element types

| Type | Group | Payload | Standard reused | Chapter |
|------|-------|---------|-----------------|---------|
| Image | `images/<name>` | Zarr arrays | NGFF multiscales | {doc}`images` |
| Labels | `labels/<name>` | Zarr arrays | NGFF multiscales + NGFF labels (`image-label` metadata) | {doc}`labels` |
| Shapes | `shapes/<name>` | `shapes.parquet` (single file) | GeoParquet | {doc}`shapes` |
| Points | `points/<name>` | `points.parquet/` (multi-file dataset) | Parquet | {doc}`points` |
| Table | `tables/<name>` | Zarr arrays | AnnData | {doc}`tables` |

Coordinate systems and transformations apply to the four spatial types and are specified once in
{doc}`coordinate-systems`. They do not apply to tables, although that may change (see
{term}`spatial element`).

## Reading this specification

- The key words **MUST**, **MUST NOT**, **SHOULD**, **SHOULD NOT** and **MAY** are to be interpreted
  as described in [RFC 2119](https://www.rfc-editor.org/rfc/rfc2119).
- "Attributes" of a Zarr group means the `attributes` object of its `zarr.json` (Zarr v3) or the
  content of its `.zattrs` file (Zarr v2). Where versions differ, the text shows them in tabs labelled
  with the container format version.
- JSON examples are taken from stores written by `spatialdata` and are abbreviated where marked with
  `...`.
- Boxes labelled *Implementation note* are not part of the on-disk format; they are kept here to
  make it easier to understand. Boxes labelled *Divergence from
  NGFF* flag places where a valid SpatialData store is not a valid NGFF 0.4 or 0.5 store.

```{toctree}
:maxdepth: 1
:hidden:

container
coordinate-systems
images
labels
shapes
points
tables
ngff-compatibility
versions
next
```
