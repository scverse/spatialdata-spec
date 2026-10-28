---
rfc: 4
title: "Tiled and multiscale shapes"
authors: "Nicolas Fernandez ([@cornhundred](https://github.com/cornhundred)), Luca Marconato ([@LucaMarconato](https://github.com/LucaMarconato)); input from Ilan Gold, Marco Varrone, Mark Keller"
status: "draft"
type: "storage format"
created: 2026-10-27
---

# RFC 4: Tiled and multiscale shapes

> ⚠️ **Work in progress.** This RFC is not reviewed yet.

## Abstract

Sort shapes (cells) by tile, using the grid of [RFC 3](0003-tiled-points.md) on their centroids, and
store the geometry as GeoArrow. For the table annotating the shapes, store the expression matrix as
CSR and CSC. Together this gives viewers like Celldega and Vitessce what they need to load cells by
tile and color them by gene.

## Description

### Scope

- In: 2-D shapes (polygons, multipolygons, circles) much smaller than a tile; the table annotating
  them.
- Out: large shapes (tissue regions, anatomical annotations), for which the centroid says little
  and which would have to be split across tiles; multiscale levels (see TODO below).

### Spatial order

Same grid, metadata (`spatial_index`) and `tile_offsets` as RFC 3, applied to centroids:

```text
c_i = centroid(geometry_i)                 # circles: the center
k_i = ravel(floor((c_i − origin) / tile_size), grid_shape)
rows sorted by k_i
rows of tile k = [tile_offsets[k], tile_offsets[k + 1])
```

A shape may extend outside its tile. The writer records the largest overhang, and readers grow the
query box by it:

```text
margin_a = max_i max(c_i,a − bbox_min_i,a, bbox_max_i,a − c_i,a)     # per axis, in metadata
tiles to read = tiles(box_min − margin, box_max + margin)
```

Shapes and points of the same dataset should use the same grid (origin and tile size), so one tile
request loads both. Fewer shapes than points per tile is fine. Several tiles can share a row group
(Parquet) or a shard (Zarr).

> **TODO(Luca):** require the same grid as the points, or only recommend it?

### Geometry

GeoArrow in Parquet (`geometry_encoding="geoarrow"`) instead of WKB. A column that mixes Polygon and
MultiPolygon is written as MultiPolygon. Code that already handles MultiPolygon keeps working.

### Table annotating the shapes

```text
table.X               CSR (cells × genes)       # as today
table.layers["X_csc"] CSC (same values)         # gene-major: one gene for all cells in one read
```

Celldega needs CSC to color cells by gene. Vitessce uses it for DotPlot without memory spikes.

> **TODO(Luca):** CSR + CSC both by default and configurable (Ilan), or CSC optional? Is this a
> SpatialData rule, or an AnnData convention (Ilan)? Name of the layer. An API in spatialdata,
> called by spatialdata-io readers?

> **TODO(Luca):** require the table rows in the same order as the shapes, so that `tile_offsets`
> also slices the table? Otherwise readers join on the instance id.

### Levels

> **TODO(Luca):** Celldega has no levels; zoomed out it aggregates (cells via CSC, hexagonal bins).
> Options: none in this RFC; simplified geometries per level; centroids only (as points, RFC 3).

### File layout

```text
shapes/<name>/
├── zarr.json                     # attrs incl. spatial_index (+ margin)
├── shapes.parquet/               # rows sorted by tile, GeoArrow geometry, part.0.parquet, …
└── index/0/tile_offsets          # as in RFC 3
tables/<name>/
├── X/                            # CSR
└── layers/X_csc/                 # CSC
```

### Compatibility

Without `spatial_index` an element reads as today. Old readers read tiled shapes in a different row
order. GeoArrow needs a recent GeoPandas/pyarrow.

> **TODO(Luca):** the GeoArrow reader versions to require.

## Related work

- Celldega ([#1251](https://github.com/scverse/spatialdata/discussions/1251),
  [PR #423](https://github.com/scverse/spatialdata-io/pull/423)): the same tile-major grid for
  transcripts and cells, `geoarrow.polygon`, `layers["X_csc"]`.
- TissUUmaps: reads only CSC.

## Implementation

> **TODO:** spatialdata (write sorted shapes, GeoArrow, CSC layer), spatialdata-io (PR #423), Celldega,
> Vitessce.

## Discussion

- [Options and proposal (Google Doc)](https://docs.google.com/document/d/1-lX85Qzm88qIprGJIW_IjUoi8LrCTZC8XXF22RZjqDk/edit),
  decisions 12 and 13 and the comment thread on shape tiling.

## References

- [RFC 3: Tiled and multiscale points](0003-tiled-points.md)
