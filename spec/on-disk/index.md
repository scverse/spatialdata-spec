# On-disk format

{bdg-primary}`on-disk` {bdg-dark-line}`status quo` {bdg-light}`version 0.2 · Zarr v3` {bdg-light}`written by spatialdata ≥ 0.6, checked against 0.8.0`

This section documents the format **as implemented today**, so that other implementations have a
stable target. Changes are proposed and decided separately; see {doc}`next` for how a new version
starts and which candidates exist. Version 0.1 (Zarr v2) is legacy and shown in tabs where it
differs.

The SpatialData on-disk format stores one spatial omics dataset as a Zarr hierarchy with embedded
Parquet files. It reuses [OME-NGFF](https://ngff.openmicroscopy.org) for raster data and for
coordinate transformations, [GeoParquet](https://geoparquet.org) for shapes, Parquet for points,
and the [AnnData on-disk format](https://anndata.readthedocs.io/en/stable/fileformat-prose.html)
for tables. This specification defines only what those standards leave open and where SpatialData
deviates from them.

## Design principles

- **Elements are independent.** A dataset is a flat collection of {term}`elements <element>`. Any
  element can be read, written or replaced without touching the others.
- **Alignment is by coordinate system, not by reference.** No element points to another. Elements
  that map into the same {term}`coordinate system` are aligned.
- **Reuse before invention.** Whatever NGFF, AnnData, Zarr or Parquet already define is used as is
  and linked, not restated.
- **No biological vocabulary.** The format knows elements, instances and variables, not cells or
  genes. That mapping is the subject of the {doc}`semantic conventions <../semantic/index>`.

## A store at a glance

```text
dataset.zarr/                       Zarr v3 group
├── zarr.json                       spatialdata_attrs.version = "0.2"  (+ consolidated metadata)
├── images/
│   └── <name>/                     NGFF multiscale image, axes cyx or czyx
│       ├── zarr.json               ome.multiscales, ome.omero.channels, spatialdata_attrs
│       ├── s0/                     full resolution array (name given by datasets[0].path)
│       └── s1/ s2/ ...             optional downsampled levels
├── labels/
│   └── <name>/                     NGFF multiscale image-label, axes yx or zyx
├── shapes/
│   └── <name>/
│       ├── zarr.json               encoding-type, axes, coordinateTransformations, spatialdata_attrs
│       └── shapes.parquet          GeoParquet: geometry [, radius] [, extra columns]
├── points/
│   └── <name>/
│       ├── zarr.json               encoding-type, axes, coordinateTransformations, spatialdata_attrs
│       └── points.parquet/         Parquet dataset: x, y [, z] [, extra columns]
│           └── part.0.parquet
└── tables/
    └── <name>/                     AnnData Zarr + region, region_key, instance_key, version
```

## Element types

| Type | Group | Payload | Standard reused | Chapter |
|------|-------|---------|-----------------|---------|
| Image | `images/<name>` | Zarr arrays | NGFF multiscales | {doc}`images` |
| Labels | `labels/<name>` | Zarr arrays | NGFF multiscales + image-label | {doc}`labels` |
| Shapes | `shapes/<name>` | `shapes.parquet` | GeoParquet | {doc}`shapes` |
| Points | `points/<name>` | `points.parquet/` | Parquet | {doc}`points` |
| Table | `tables/<name>` | Zarr arrays | AnnData | {doc}`tables` |

Coordinate systems and transformations apply to the four spatial types and are specified once in
{doc}`coordinate-systems`.

## Reading this specification

- The key words **MUST**, **MUST NOT**, **SHOULD**, **SHOULD NOT** and **MAY** are to be interpreted
  as described in [RFC 2119](https://www.rfc-editor.org/rfc/rfc2119).
- "Attributes" of a Zarr group means the `attributes` object of its `zarr.json` (Zarr v3) or the
  content of its `.zattrs` file (Zarr v2). Where the two Zarr versions differ, the text shows both in
  tabs; the Zarr v3 tab is the current format.
- JSON examples are taken from stores written by `spatialdata` 0.6 and are abbreviated where marked
  with `...`.
- Boxes labelled *Implementation note* are not part of the format. Boxes labelled *Divergence from
  NGFF* flag places where a valid SpatialData store is not a valid NGFF 0.4 or 0.5 store.
- Every component carries its own {term}`format version`. The mapping between component versions,
  container versions and `spatialdata` releases is in {doc}`versions`.

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
