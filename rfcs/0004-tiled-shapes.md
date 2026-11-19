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

Sort shapes (cells) by tile, using a grid as in [RFC 3](0003-tiled-points.md) on their centroids, and
store the geometry as GeoArrow. For the table annotating the shapes, keep its rows in the order of the
shapes and store the expression matrix as CSR and CSC. Together this gives viewers like Celldega and
Vitessce what they need to load cells by tile and color them by gene. The index is optional, and only
suited to small shapes.

## Description

### Scope

- In: 2-D shapes (polygons, multipolygons, circles) much smaller than a tile, such as cells or nuclei;
  the table annotating them.
- Out: large shapes (tissue regions, anatomical annotations), see [When to use it](#when-to-use-it);
  multiscale levels: this version has a single level (see [Levels](#levels)).

### When to use it

This index is optional, and only suited to small shapes, such as cells or nuclei. It is not
recommended for shapes that are large compared to the tiles, such as anatomical structures or tissue
regions: their centroid says little about where they are, the margin (the largest overhang outside the
tile of the centroid, see [Spatial order](#spatial-order)) becomes large, and every query then reads
many tiles. Rule of thumb: use the index only if the shapes are smaller than a tile and more than 50% of
them lie entirely within the tile of their centroid; otherwise do not. Writers SHOULD check this and
choose the tile size accordingly.

For example, for the 399,000 cells of a 10x Atera kidney section (median width 8.7 µm, 90th percentile
14.2 µm), the fraction of cells entirely within the tile of their centroid is:

| Tile size | 6.7 µm | 13.4 µm | 26.7 µm | 53.5 µm | 107 µm |
| :- | :- | :- | :- | :- | :- |
| Cells within their tile | 0.8% | 13% | 43% | 68% | 83% |

Tiles of 53.5 µm or more suit these cells; tiles of the size used for the transcripts of the same
dataset (27 µm, see RFC 3) are borderline, and smaller ones do not.

### Spatial order

The grid, the metadata (`spatial_index`) and the tile index (`tile_offsets`) are those of RFC 3, with a
single level, applied to the centroids of the shapes:

```text
c_i = centroid(geometry_i)                 # circles: the center
k_i = ravel(floor((c_i − origin) / tile_size), grid_shape)
rows sorted by k_i
rows of tile k = [tile_offsets/0[k], tile_offsets/0[k + 1])
```

A shape may extend outside its tile. The writer records the largest overhang per axis, the *margin*,
in `spatial_index`, and readers grow the query box by it:

```text
margin_a = max_i max(c_i,a − bbox_min_i,a, bbox_max_i,a − c_i,a)     # per axis, in spatial_index
tiles to read = tiles intersecting [box_min − margin, box_max + margin]
```

`margin` is one value per axis, in the order of `axes`, in the coordinates of the element, like `origin`
and `tile_size`. Writers MUST NOT record a margin smaller than the largest overhang (readers would miss
shapes at the edges of a view); a larger margin is allowed, and only makes queries slower.

```json
"spatial_index": {
  "version": "0.1.0-draft",
  "axes": ["x", "y"],
  "levels": [{"origin": [0.0, 0.0], "tile_size": [53.5, 53.5], "grid_shape": [226, 132], "P": 1.0}],
  "margin": [30.8, 21.9],
  "table": "table",
  "parquet": "spatial_index.parquet.json"
}
```

**The grid of the shapes.** Each element has its own grid (RFC 3), chosen for its own data: the shapes
by the rule of [When to use it](#when-to-use-it), the points by their density (RFC 3, "Choosing the tile
size and the rates"). The two usually want different tile sizes (in the example above, about 27 µm for
the transcripts and 53.5 µm for the cells), and the grid of each element covers its own bounding box.
When a client loads points and shapes tile by tile, writers SHOULD choose nested grids: the same origin,
and a tile size of the shapes equal to that of a level of the points (with the merge rule, a power of 2
times the tile size of level 0), so that each tile of the shapes is a union of tiles of the points.
Several tiles can share a row group (Parquet) or a shard (Zarr).

### Geometry

GeoArrow in Parquet (`geometry_encoding="geoarrow"`) instead of WKB. A column that mixes Polygon and
MultiPolygon is written as MultiPolygon: code that handles MultiPolygon keeps working, and viewers
SHOULD draw all the parts of a MultiPolygon, not only the largest.

The commonly used columns SHOULD come first, the geometry, then the instance id and the columns used to
color or select the shapes, as in RFC 3 ("Order of the columns").

### Table annotating the shapes

```text
table.X               CSR (cells × genes)       # as today
table.layers["X_csc"] CSC (same values)         # gene-major: one gene for all cells in one read
```

Celldega needs CSC to color cells by gene. Vitessce uses it for DotPlot without memory spikes. The name
of the CSC layer SHOULD be `X_csc` (other names, such as `csc_counts` in spatialdata-db, are allowed).

The table MUST annotate the shapes (its `region` is the shapes element, its `instance_key` the index of
the shapes); if it does not, this section does not apply, and making sure it does is the responsibility
of the user. When the shapes are indexed, the rows of the table SHOULD be in the order of the shapes, so
that the tile index also slices the table: the rows of tile $k$ in the table are
`[tile_offsets/0[k], tile_offsets/0[k + 1])`. `spatial_index` then names the table (`"table"`, above);
without it, readers join on the instance id.

> **TODO(Luca):** CSR + CSC both by default and configurable (Ilan), or CSC optional? Is this a
> SpatialData rule, or an AnnData convention (Ilan)? An API in spatialdata, called by spatialdata-io
> readers?

### Levels

This version has a single level, the grid of level 0: zoomed out, a client shows fewer shapes by other
means. Options for a future version:

- none (Celldega aggregates when zoomed out: cells via CSC, hexagonal bins);
- simplified geometries per level;
- the centroids as points, with the levels of RFC 3.

### Limitations and possible extensions

The margin is a single maximum over all the shapes: a few large shapes make every query read more
tiles (in the kidney example with 6.7 µm tiles, a margin of 30.8 × 21.9 µm, 4 to 5 extra tiles on each
side). Possible extensions, not part of this version:

- shapes larger than a few tiles in a separate range of rows, or in a coarser level, with their own
  margin;
- a margin per tile;
- indexing by the overlap of the bounding box (each shape in the tile of the minimum corner of its
  bounding box, with a margin equal to the largest bounding box).

### File layout

As in RFC 3, the same in Parquet and in Zarr; in Parquet with the Parquet sidecar (part files in
order and the first row of each):

```text
shapes/<name>/
├── zarr.json                      # attrs incl. spatial_index (+ margin)
├── spatial_index.parquet.json     # Parquet only
└── spatial/
    ├── shapes.parquet/            # rows sorted by tile, GeoArrow geometry, part files
    └── tile_offsets/0             # as in RFC 3
tables/<name>/
├── X/                             # CSR
└── layers/X_csc/                  # CSC
```

### Compatibility

Without `spatial_index` an element reads as today. An element with `spatial_index` is a new version of
the shapes format, not readable by older readers. GeoArrow needs a recent GeoPandas/pyarrow.

> **TODO(Luca):** the GeoArrow reader versions to require.

## Related work

- Celldega ([#1251](https://github.com/scverse/spatialdata/discussions/1251),
  [PR #423](https://github.com/scverse/spatialdata-io/pull/423)): the same tile-major grid for
  transcripts and cells, `geoarrow.polygon`, `layers["X_csc"]`.
- TissUUmaps: reads only CSC.

Considered and not chosen:

- One grid shared by the points and the shapes of a dataset, with a "leftover" tile for the shapes
  whose centroid falls outside the grid of the points: the two elements want different tile sizes,
  every reader would have to read the leftover tile, and avoiding it would require the grid of the
  points to cover the shapes. Nested grids give the same alignment.
- A rule to find the table rows of shapes annotated only indirectly (e.g. a table annotating the cell
  labels, matched to the boundaries through a column): out of scope, the table must annotate the shapes.

## Implementation

An experimental implementation (sorting by tile, GeoArrow, margin, table in the order of the shapes
with a CSC layer, a napari-spatialdata reader of the shapes in view) was tested on the 399,000 cells of
a 10x Atera kidney dataset: a box of 1 mm reads its cells in 21 ms instead of 0.22 s, and one gene for
all the cells takes 5 ms from CSC instead of 2.3 s from CSR.

> **TODO:** spatialdata (write sorted shapes, GeoArrow, CSC layer), spatialdata-io (PR #423), Celldega,
> Vitessce.

## Discussion

- [Options and proposal (Google Doc)](https://docs.google.com/document/d/1-lX85Qzm88qIprGJIW_IjUoi8LrCTZC8XXF22RZjqDk/edit),
  decisions 12 and 13 and the comment thread on shape tiling.

## References

- [RFC 3: Tiled and multiscale points](0003-tiled-points.md)
