---
rfc: 3
title: "Tiled and multiscale points"
authors: "Luca Marconato ([@LucaMarconato](https://github.com/LucaMarconato)); input from Nicolas Fernandez ([@cornhundred](https://github.com/cornhundred)), Arne Defauw, Jonas Windhager, Ilan Gold, Ignatius Jenie, Mark Keller, Christian La France, Tim Treis"
status: "draft"
type: "data model; storage format"
created: 2026-09-17
---

# RFC 3: Tiled and multiscale points

## Abstract

Specification for spatially indexing points, enabling optional multiscale subsampled levels, spatially chunked storage: a regular
2-D or 3-D grid of tiles, with the points stored both in tile order and in feature-major order. This enables viewers to load only the points in view, or only those of the genes shown; zoomed out, they load a
density-preserving sample. Shapes are in [RFC 4](0004-tiled-shapes.md).

## Description

The key words MUST, MUST NOT, SHOULD, SHOULD NOT and MAY are to be interpreted as described in
[RFC 2119](https://www.rfc-editor.org/rfc/rfc2119). Key words have this meaning only in capitals
([RFC 8174](https://www.rfc-editor.org/rfc/rfc8174)).

### Scope

- In scope: points, 2-D and 3-D; spatial indexing via chunking and sorting; tile order and feature-major order; sampled levels.
- Out of scope: shapes ([RFC 4](0004-tiled-shapes.md)), the matrix of a table annotating the shapes and its sparse storage (CSR/CSC, RFC 4), aggregation to cells or bins (square/hexagonal), ordering inside tiles (Morton, Hilbert), ordering of the tiles other than C order (e.g. Morton).

## Data model

This RFC adds to the abstract data model of points: levels, a grid of tiles at each level, the
order of the tiles, and the sampling of the levels. These concepts do not depend on how the points
are stored ([Storage format](#storage-format)).

### Levels

Points are organized in one or more levels. To load all the points, a reader loads the
highest-resolution level (level 0). Each other level is a subsampled version of the points of the previous level. I.e. a point present at level N, is also present in levels 0, ..., N - 1. 

While one could design the storage so that each point is stored exactly once, this specification favors simplificity over size on disk and, shown below, will also store multiple indexes (motivations: storage of points is generally cheap, and cheaper than that of raster data such as images; clients such as viewers can fetch the data faster and more easily; readers never need to merge levels). When storing several copies of the points is not acceptable, for instance for very large datasets, aggregated data is a better choice than sampled levels (out of scope for this RFC).

### Grid and tiles

A grid is defined for a specific *points element* (the SpatialData term for a 2D/3D points cloud) and for a specific named coordinate system. The metadata for the grid specifies this information pair.

Different elements, even if in the same coordinate system, use different grids: reusing the same grid for 2 or more elements is out of scope for this RFC ([RFC 4](0004-tiled-shapes.md) will discuss reusing the same grid for points (transcripts) and shapes (cells)).

An axis $a$ is one of the spatial axes $x$, $y$ and $z$ (not the channel axis $c$). The grid has, per axis $a$,
an arbitrary origin $o_a$ (for instance the corner with the minimum coordinates of the bounding box
of all the points), one tile size $s_a$ (square tiles are a special case), and an arbitrary number of
tiles $n_a$: the number of intervals into which the grid divides axis $a$, not the total number of
tiles of the grid, which is $N = \prod_a n_a$. All the tiles are identical. The tiles cover all the points.
Each tile is to be interpreted as a semi-open hyper-interval, with the interval closed for the lowest
value, and open for the highest. For example, in 2 dimensions, the tile

$$
[\, x_{\min},\ x_{\max} \,) \times [\, y_{\min},\ y_{\max} \,)
$$

contains the points $(x, y)$ that satisfy $x_{\min} \le x < x_{\max}$ and $y_{\min} \le y < y_{\max}$.

The grid of each lower level is built deterministically from the grid of the previous level: it is
merged by a factor of 2 along one or more axes, keeping the tiles as isotropic as possible.
Therefore the initial grid determines the granularity of the spatial index at the first level and
at each subsequent level.

:::{figure} img/0003-levels.svg
:alt: Three levels of a 2-D grid: level 0 with 4 × 4 tiles and all the points, level 1 with 2 × 2 tiles and fewer points, level 2 with a single tile and fewer points still.

Three levels of a 2-D grid, with the points kept at each level.
:::

Below are two examples of a merging step that keeps the tiles as isotropic as possible: one merges
along one axis, the other along two.

:::{figure} img/0003-merge-one-axis.svg
:alt: Two tiles of size 2 × 2 × 1, stacked along z, become one tile of size 2 × 2 × 2.

Merging along one axis (z). Tile sizes along (x, y, z).
:::

:::{figure} img/0003-merge-two-axes.svg
:alt: Four tiles of size 1 × 1 × 2, side by side along x and y, become one tile of size 2 × 2 × 2.

Merging along two axes (x and y). Tile sizes along (x, y, z).
:::

:::{dropdown} The rule in formulas

Let $s_a^{(l)}$ and $n_a^{(l)}$ be the tile size $s_a$ and the number of tiles $n_a$ along axis $a$
at level $l$. At level $l$:

- $A^{(l)}$ are the axes that still have more than one tile at level $l - 1$;
- $m^{(l)}$ is the smallest tile size among them;
- $M^{(l)}$ are the axes that will be merged at level $l$: those of $A^{(l)}$ whose tile size is less than twice
  $m^{(l)}$.

$$
\begin{aligned}
A^{(l)} &= \{\, a : n_a^{(l-1)} > 1 \,\} \\
m^{(l)} &= \min_{a \in A^{(l)}} s_a^{(l-1)} \\
M^{(l)} &= \{\, a \in A^{(l)} : s_a^{(l-1)} < 2\, m^{(l)} \,\} \\
s_a^{(l)} &= \begin{cases} 2\, s_a^{(l-1)} & a \in M^{(l)} \\ s_a^{(l-1)} & \text{otherwise} \end{cases}
\qquad
n_a^{(l)} = \begin{cases} \lceil n_a^{(l-1)} / 2 \rceil & a \in M^{(l)} \\ n_a^{(l-1)} & \text{otherwise} \end{cases}
\end{aligned}
$$

:::

Applied to the end, the procedure stops at the first level with $n_a = 1$ along every axis (a single
tile). A writer may also stop earlier, so the lowest-resolution level may still contain multiple
tiles.

Examples. First, a simple one: a volume of 256 × 256 × 200 along (x, y, z), origin 0.

:::{dropdown} Volume 256 × 256 × 200: initial tile size 32 × 32 × 32

Starting from "# tiles along axis" 7 × 8 × 8 along (z, y, x), the tiles are isotropic, so all three
axes are merged at every level, until a single tile is left:

```text
level  tile size (z, y, x)  # tiles along axis (z, y, x)  merged
0       32 ×  32 ×  32      7 × 8 × 8                     -
1       64 ×  64 ×  64      4 × 4 × 4                     z, y, x
2      128 × 128 × 128      2 × 2 × 2                     z, y, x
3      256 × 256 × 256      1 × 1 × 1                     z, y, x
```

:::

Then an anisotropic extent, 10 × 100 × 1000 along (z, y, x), origin 0, with two initial tilings.

:::{dropdown} Anisotropic tiles: initial tile size 1 × 10 × 100

Starting from "# tiles along axis" 10 × 10 × 10, the thin axes are merged first; z then stops at a
single tile, and x is merged last:

```text
level  tile size (z, y, x)  # tiles along axis (z, y, x)  merged
0         1 ×  10 ×  100    10 × 10 × 10                  -
1         2 ×  10 ×  100     5 × 10 × 10                  z
2         4 ×  10 ×  100     3 × 10 × 10                  z
3         8 ×  10 ×  100     2 × 10 × 10                  z
4        16 ×  20 ×  100     1 ×  5 × 10                  z, y
5        16 ×  40 ×  100     1 ×  3 × 10                  y
6        16 ×  80 ×  100     1 ×  2 × 10                  y
7        16 × 160 ×  200     1 ×  1 ×  5                  y, x
8        16 × 160 ×  400     1 ×  1 ×  3                  x
9        16 × 160 ×  800     1 ×  1 ×  2                  x
10       16 × 160 × 1600     1 ×  1 ×  1                  x
```

:::

:::{dropdown} Isotropic tiles: initial tile size 10 × 10 × 10

Starting from "# tiles along axis" 1 × 10 × 100, z has a single tile from the start; y and x are
merged together until y has a single tile, then x alone:

```text
level  tile size (z, y, x)  # tiles along axis (z, y, x)  merged
0        10 ×  10 ×   10     1 × 10 × 100                 -
1        10 ×  20 ×   20     1 ×  5 ×  50                 y, x
2        10 ×  40 ×   40     1 ×  3 ×  25                 y, x
3        10 ×  80 ×   80     1 ×  2 ×  13                 y, x
4        10 × 160 ×  160     1 ×  1 ×   7                 y, x
5        10 × 160 ×  320     1 ×  1 ×   4                 x
6        10 × 160 ×  640     1 ×  1 ×   2                 x
7        10 × 160 × 1280     1 ×  1 ×   1                 x
```

:::

### Tiles ordering

At each level, the tiles are indexed by their coordinates along the axes and ordered by a single
tile id, in C order (row-major): the last axis declared in the metadata varies fastest.

:::{figure} img/0003-tile-order.svg
:alt: A grid of 3 × 4 tiles with axes (y, x); each tile shows its coordinates (t_y, t_x) and its id, 0 to 11, increasing along x first and then along y.

Tile ids on a 2-D grid with axes (y, x) and 3 × 4 tiles: $k = 4\, t_y + t_x$.
:::

:::{dropdown} The tile id in formulas

At a given level, with the origin $o_a$, the tile size $s_a$ and the number of tiles along axis $a$, $n_a$, as in
[Grid and tiles](#grid-and-tiles), the tile containing a position $p$ has, along each axis $a$, the
coordinate

$$
t_a(p) = \left\lfloor \frac{p_a - o_a}{s_a} \right\rfloor, \qquad 0 \le t_a < n_a .
$$

With the axes $a_1, \dots, a_d$ in the order declared in the metadata, its id is

$$
k(p) = \sum_{j=1}^{d} t_{a_j}(p) \prod_{i = j + 1}^{d} n_{a_i},
$$

i.e. each coordinate is multiplied by the number of tiles along all the axes that come after it.
For the usual axis orders:

$$
\begin{aligned}
\text{2-D, axes } (y, x):\quad & k = t_y\, n_x + t_x \\
\text{3-D, axes } (z, y, x):\quad & k = (t_z\, n_y + t_y)\, n_x + t_x
\end{aligned}
$$

With $N = \prod_a n_a$ tiles, $0 \le k < N$.

:::

One could instead order the tiles by Morton code (Z-order), which keeps tiles that are close in
space close in the order. This is not done in this version and is left for future versions.

### Tile order and feature-major order

At each level, the points are written in two orders, each a copy of the points with all their
columns:

- tile order, required: sorted by tile id, with the order inside a tile unspecified;
- feature-major order, written by default (a writer may opt out): sorted by feature, then by tile
  id.

The feature is a categorical column chosen when writing and named in the metadata: for spatial
transcriptomics, the gene id. A writer may choose several feature columns, for instance the gene id
and the cell type, each with its own feature-major copy. It is recommended to choose only one, the
column used most often to select points, for the best performance at the lowest storage cost. Any
other column can still be used to select points, from the tile-order copy: faster than without a
spatial index, with some performance penalty compared with a feature-major copy.

Only the tile order is required: a dataset may have no feature-major copy at all. A client looking
for the points of a feature looks for a feature-major copy of the corresponding column and, if there
is none, falls back to the tile order.

:::{dropdown} Falling back to the tile order: what changes at sampled levels

The two orders are sampled differently (see [Sampling](#sampling)). The feature-major order
preserves densities within each feature. The tile order preserves only the global density: it
treats all the points as equal, whatever their category.

At level 0 the two orders hold all the points of every tile, so they are fully equivalent, except
for performance. At sampled levels they differ: the tile order keeps a feature with the same
fraction as all the others, so a client that falls back to it is less useful for showing rare
categories, which may keep very few points or none.

To address this at the root, aggregation (e.g. counting the points of each category per bin) can be
a better alternative to sampling. It is out of scope for this RFC.

:::

The two orders answer two different questions with a contiguous range of rows:

- Tile order: *which points are in this region?* The points of a tile are one row range, whatever
  their gene. A client showing the region reads the tiles in view.
- Feature-major order: *where are the points of this gene?* The points of a gene are one row range,
  and inside it the points of each tile are again one range, sorted by tile id. A client showing a
  few genes reads only their points.

Without the feature-major copy, showing one gene means reading every point of the tiles in view and
discarding the other genes: the cost grows with all the points in view, not with the points of the
gene. With it, the cost grows only with the points of the genes shown. The price is a second copy of
the points. Per-tile statistics (e.g. which features a tile contains, or how many points of each)
could let a client skip tiles without the feature it shows and improve performance; they are out of scope for this RFC.

:::{figure} img/0003-orders.svg
:alt: Two levels. Level 0: twelve points of genes A (6), B (4) and C (2) on a 2 × 2 grid, stored grouped by tile and grouped by gene and then by tile. Level 1, a single tile: the tile-order copy keeps 4 points (P = 1/3); the feature-major copy keeps 4 points of A (P = 2/3), 2 of B (P = 2/3) and both points of C (P = 1).

The points of two levels, each in the two orders. In tile order each tile is one row range; in
feature-major order each gene is one row range, sorted by tile inside it. At level 1 the tile-order
copy is sampled over all the points, with one fraction $P$, the feature-major copy per gene, with
one fraction per gene: the rare gene C keeps all its points. How the fractions $P$ are chosen is
explained in [Sampling](#sampling).
:::

### Sampling

Sampling chooses the subset of points of each level (see [Levels](#levels)). It is
density-preserving, as in Neuroglancer
([annotation spatial index](https://github.com/google/neuroglancer/blob/master/src/datasource/precomputed/annotations.md#spatial-index)):
at each level, every point is kept with the same
probability, chosen so that the densest tile holds about `limit` points. Dense regions stay denser
than sparse ones. Each level is sampled from the level below it, which makes the levels nested.

The two copies of the points (see
[Tile order and feature-major order](#tile-order-and-feature-major-order)) are sampled differently:

- Tile order: over all the points. At a level, every feature is kept with the same fraction $P^{(l)}$.
- Feature-major order: per feature. Each feature $g$ is sampled on its own, with its own fraction
  $P_g^{(l)}$, so that the densest tile holds about `limit` points of $g$. A rare feature keeps
  all its points at coarse levels instead of vanishing; an abundant one is thinned. When the
  feature-major copy is written, every level has one.

The sampling is binomial thinning, as in Neuroglancer: each point of level $l - 1$ is kept at level
$l$ or not, independently of the others and with the same probability, so no point appears twice in
a level. The `limit` is therefore met on average, not exactly: a tile can end up with slightly more
than `limit` points. For example, if the densest tile holds 10,100 points and `limit` is 10,000,
each point is kept with probability about 0.99. The tile then keeps 10,000 points on average, but by
chance more than 10,000 about half of the time (typically about 10 more). Such small excesses do not
matter: `limit` is a budget for a comfortable display, not a hard bound.
No random value or hash used to keep or reject a point is stored with the points. The metadata stores the fractions of both copies (see
[Metadata](#metadata)).

How to choose `limit`, and the tile size of level 0 with it, is explained in
[When the spatial index helps](#when-the-spatial-index-helps).

:::{dropdown} Sampling in formulas

Let $c^{(l)}$ be the largest number of points of level $l - 1$ in any tile of level $l$; $p^{(l)}$ the fraction of
the points of level $l - 1$ kept at level $l$; and $P^{(l)}$ the fraction of all points kept at
level $l$:

$$
\begin{aligned}
c^{(l)} &= \max_{\text{tiles } T \text{ of level } l} \bigl|\{\, i \in \text{level } l - 1 : i \in T \,\}\bigr| \\
p^{(l)} &= \min\!\left(1, \frac{\texttt{limit}}{c^{(l)}}\right) \\
P^{(0)} &= 1, \qquad P^{(l)} = P^{(l-1)}\, p^{(l)}
\end{aligned}
$$

Each point of level $l - 1$ is kept at level $l$ independently with probability $p^{(l)}$, so each
point of level 0 is in level $l$ with probability $P^{(l)}$, and the densest tile keeps
$p^{(l)} c^{(l)} = \texttt{limit}$ points on average.

For the feature-major copy, the same formulas are applied to the points of each feature $g$
separately, giving $c_g^{(l)}$, $p_g^{(l)}$ and $P_g^{(l)}$, : each point of feature $g$ is in level $l$ of the feature-major copy with
probability $P_g^{(l)}$.

Storage bound: if each level keeps at most $1/2^d$ of the points of the level below (merged along
all $d$ axes), the levels hold at most

$$
N \sum_{l \ge 0} 2^{-d\,l} = N \, \frac{2^d}{2^d - 1}
$$

points in total, for $N$ points at level 0: $1.33\,N$ in 2-D, as for a 2-D image pyramid, and
$1.14\,N$ in 3-D. The bound holds for each copy.

The bound shows that the data does not grow much, even though the same point appears again at
several levels: the sampled levels add at most a third of the points in 2-D. The storage is
dominated by the multiple copies (the tile order and the feature-major order), which double it and
are generally affordable (see [Levels](#levels)).

:::

#### Showing several features together

At level 0 every fraction is 1 and both copies hold every point, so any view is exact, independently
of whether it is read from the tile order or from the feature-major order. The
difference matters only when a client shows a sampled level ($l \ge 1$) of the feature-major copy.
There, features are kept with different fractions, so showing several features together distorts
their relative abundance. For example, if an abundant feature keeps $P_A^{(l)} = 1\%$ of its points
and a rare one keeps $P_B^{(l)} = 100\%$, a region with 10,000 points of A and 100 of B shows 100 of
each. Within each feature the view stays density-preserving.

To show a set $S$ of features consistently, a client should sample and keep each point of a feature
$g \in S$ independently with probability

$$
\frac{P_S^{(l)}}{P_g^{(l)}}, \qquad P_S^{(l)} = \min_{g \in S} P_g^{(l)},
$$

which gives every feature in $S$ the same fraction $P_S^{(l)}$ of its points. The client should use
a fixed seed (e.g. derived from the coordinates of each point), so that the same points stay shown
when the view moves or reloads. Clients SHOULD do this when they show several
features together; it is not required. A client may also show each feature at its own fraction on
purpose, e.g. to compare the spatial patterns of the features rather than their abundance.

A client MAY support only level 0 and ignore the sampled levels, and show zoomed-out views with
other strategies, such as aggregation (see [RFC 4](0004-tiled-shapes.md#levels)).

### When the spatial index helps

Holding every point at level 0 does not by itself make reading fast. The spatial index helps only
if the tile size of level 0 and the `limit` suit the data and each other.

The `limit` is the number of points a client can comfortably load and display for one tile. The
suggested default is `limit` = 10,000, for now, while this RFC is a draft; it will be adjusted
from user feedback. The reasoning: with the coordinates and a feature code, about 16 bytes per
point, a tile is about 160 kB before compression, a comfortable size for one request, and a view of
4 × 4 tiles shows about 160,000 points, which a browser renders easily.

The tile size of level 0 should then be chosen so that the densest tile of level 0 holds about
`limit` points. If the densest region has $\rho$ points per unit of area (2-D) or volume (3-D), the
tile size along each of the $d$ axes is about

$$
s \approx \left( \frac{\texttt{limit}}{\rho} \right)^{1/d}.
$$

This estimate assumes that the points are roughly uniformly distributed at the scale of a tile, and
that the tiles are isotropic. Larger-scale variations are taken into account by using the density of
the densest region; a hotspot smaller than a tile is not (see case (d) below). In practice, a writer
can also pick a tile size, count the points of the densest tile, and adjust.

Then a client loads about `limit` points per tile at every level: at level 0 because the tiles are
small, at the coarser levels because the points are sampled. The cost of a view stays the same as
the client zooms in and out.

:::{figure} img/0003-tile-size.svg
:alt: Four panels with the same limit of 40 points per tile. (a) 4 × 4 tiles on uniform points, densest tile 37 points. (b) 2 × 2 tiles, densest tile 127 points, all tiles above the limit. (c) 16 × 16 tiles, densest tile 6 points. (d) 4 × 4 tiles with a hotspot, one tile of 220 points, the others at most 16.

The tile size of level 0 for a limit of 40 points per tile, on 400 points.
:::

The figure shows the edge cases:

- (a) Tiles that fit: the densest tile holds about `limit` points.
- (b) Tiles too large: the tiles of level 0 hold far more than `limit` points, and level 0 is not
  sampled, so a client zoomed in loads more points than it can comfortably display. Level 0 needs a
  finer grid.
- (c) Tiles too small: many tiles with few points each, so a view needs many small requests and the
  index is large. Moreover, the first coarser levels still hold fewer than `limit` points per tile,
  so they are not sampled ($p^{(l)} = 1$): they are copies of level 0 on a coarser grid, which cost
  storage without reducing the points to load.
- (d) Hotspot: a region much denser than the rest puts many points in a few tiles. A tile size
  chosen for the hotspot is too small elsewhere, as in (c); one chosen for the rest is too large in
  the hotspot, as in (b). A future extension could address this with an adaptive grid, if the
  community identifies it as a need.

## Storage format

The data model above can be implemented both in Parquet and in Zarr, and this RFC describes both.
SpatialData already stores points in Parquet, so the Parquet format is to be interpreted as the
default. Whether the Zarr format replaces it or the two coexist will be determined from user
feedback and real usage; Zarr would also be more flexible for 3-D shapes (meshes, see
[RFC 4](0004-tiled-shapes.md)).

The format is self-contained: compatible with the way OME-NGFF stores coordinate systems, but usable
on its own, even outside an OME-Zarr store, because its metadata is defined as a Zarr convention.
Parquet has no equivalent of Zarr conventions, so the Parquet format reuses the same syntax for its
metadata.

### Points as a tall table

In both formats, each copy of a level (tile order or feature-major order) is a tall table: one row
per point, one column per attribute. Each tile is stored in one logical unit, a row group in Parquet
(one row group per tile, as in Celldega) and a chunk in Zarr, and the units are grouped into files: the part files of a multi-file Parquet
dataset, and shards in Zarr. Zarr chunks are regular, so each tile's chunk is padded to the size of
the largest tile; this costs little, since the tiles hold similar numbers of points (see
[When the spatial index helps](#when-the-spatial-index-helps)).

An alternative storage in Zarr would be a sparse tensor in which each entry is a point. It comes with
other compromises and is left for possible future exploration. Another option would come if Zarr
allowed chunks of different sizes in an array (variable chunk grids have been proposed for Zarr):
each tile would then be one chunk of its own size, without padding.

### Metadata

The metadata is a Zarr convention, `spatial_index`, in the attributes of the points element, next
to the existing ones. The levels follow the
[zarr-conventions `multiscales`](https://github.com/zarr-conventions/multiscales) convention: its
`layout` lists the levels, and each level object carries the grid and the sampling of that level
under the key `spatial_index`, as the convention allows additional properties. Both formats use
this metadata, in the `zarr.json` of the element:

> ⚠️ **Work in progress.** The specification is not reviewed after this point.

```json
{
  "zarr_conventions": [
    {
      "name": "multiscales",
      "uuid": "d35379db-88df-4056-af3a-620245f8e347",
      "schema_url": "https://raw.githubusercontent.com/zarr-conventions/multiscales/refs/tags/v0.1/schema.json",
      "spec_url": "https://github.com/zarr-conventions/multiscales/blob/v0.1/README.md"
    },
    {"name": "spatial_index", "uuid": "…", "schema_url": "…", "spec_url": "…"}
  ],
  "spatial_index": {
    "coordinate_system": "global",
    "axes": ["x", "y", "z"],
    "feature_key": "gene",
    "orders": ["spatial", "feature"]
  },
  "multiscales": {
    "resampling_method": "density_preserving",
    "layout": [
      {
        "asset": "0",
        "spatial_index": {"origin": [0.0, 0.0, 0.0], "tile_size": [100.0, 100.0, 10.0], "grid_shape": [120, 80, 3], "n_rows": 812345678}
      },
      {
        "asset": "1",
        "derived_from": "0",
        "transform": {"scale": [2.0, 2.0, 2.0]},
        "spatial_index": {"origin": [0.0, 0.0, 0.0], "tile_size": [200.0, 200.0, 20.0], "grid_shape": [60, 40, 2], "n_rows": 203086419,
                          "sampling": {"limit": 10000, "P": 0.25, "P_feature": [1.0, 0.8, 0.25]}}
      }
    ]
  }
}
```

The `transform` of a level gives, per axis, the factor by which its tiles are larger than those of
the level it is derived from: 2 along the merged axes, 1 along the others. `P` is the fraction
$P^{(l)}$ of the tile-order copy; `P_feature` lists the fractions $P_g^{(l)}$ of the feature-major
copy, one per feature, in the order of the feature categories.

> **TODO(Luca):** register the `spatial_index` convention (uuid, schema and spec URLs); align the
> `asset` paths with the file layout of each format; follow up with the OME-Zarr community.

### File layout

Parquet (backward compatible: level 0 in spatial order sits where readers look today):

```text
points/<name>/
├── zarr.json                      # attrs incl. spatial_index
├── points.parquet/                # level 0, spatial order, part.0.parquet, part.1.parquet, …
├── index/0/tile_offsets           # Zarr int64 array
├── feature/0/points.parquet/      # optional, level 0, feature order
├── index/0/feature_offsets
├── levels/1/points.parquet/       # optional, level 1, spatial order
├── index/1/tile_offsets
└── …
```

Zarr (dataframe as 1-D arrays, `df:` convention):

```text
points/<name>/
├── zarr.json                      # attrs incl. spatial_index
├── 0/
│   ├── spatial/{x,y,z,gene,…}     # 1-D arrays, same length
│   ├── spatial/tile_offsets
│   ├── feature/{x,y,z,gene,…}     # optional
│   └── feature/feature_offsets
└── 1/ …
```

> **TODO(Luca):** pick one layout per format, or prototype both (proposal 4.3). Where the offsets
> live in the Parquet case (Zarr arrays as above, Parquet key-value metadata, or a sidecar Parquet).

### Columns

- `x`, `y`, `z`: float32, absolute, in the element's coordinate system. (Spacing of float32 at
  10 cm in µm units is about 8 nm, well below localization error.)
- Feature: integer codes with the category list stored once (dictionary / categorical).
- Any other columns, unchanged.

### Tile index

To find the points of a tile, a reader uses the tile index of the tile-order copy of the level. Since
the rows are sorted by tile id, the points of each tile are consecutive rows. The index records where
each tile starts: an integer array `tile_offsets` ($O$, int64) with one entry per tile plus one, for
the $N$ tiles of the level. The points of tile $k$ are the rows

$$
[\, O_k,\ O_{k+1} \,), \qquad O_0 = 0, \quad O_N = \text{number of rows},
$$

so tile $k$ holds $O_{k+1} - O_k$ points, and an empty tile has $O_k = O_{k+1}$. The reader then reads
the storage unit of the tile: in Parquet, the row group of tile $k$; in Zarr, chunk $k$ of each
column, whose first $O_{k+1} - O_k$ entries are the points and the rest padding.

### Feature index

The feature-major copy of each level has:

```text
feature_offsets: int64[n_features + 1]
rows of feature g          = [feature_offsets[g], feature_offsets[g + 1])
rows of feature g, tile k  = [feature_tile_offsets[g, k], feature_tile_offsets[g, k + 1])   # optional
```

> **TODO(Luca):** Ilan suggests writing both orders by default, configurable; the proposal said
> "recommended but optional". Pending his answer on the Google Doc comment (transcripts or cell
> matrix?). Also: is `feature_tile_offsets` (n_features × n_tiles, can be large) worth having, or is
> `feature_offsets` enough?

### Reading

```python
for k in tiles_intersecting(box):           # tile ids, see "Tiles ordering"
    yield rows(tile_offsets[k], tile_offsets[k + 1])
# zoomed out: choose the finest level whose expected rows in view ≤ budget
```

### Compatibility

- Without `spatial_index` an element reads as today.
- Old readers of a tiled Parquet element read level 0 in spatial order (all points, different row
  order) and ignore the rest.

> **TODO(Luca):** confirm the current Parquet path (`points.parquet/`) and whether the extra
> directories break current readers.

## Related work

| Format | Grid | Index | Levels | Second order |
| :- | :- | :- | :- | :- |
| Celldega ([#1251](https://github.com/scverse/spatialdata/discussions/1251), [PR #423](https://github.com/scverse/spatialdata-io/pull/423)) | square 2-D, image pixels, origin (0, 0) | one row group per tile | none | none |
| merfisheyes ([spec](https://github.com/kresnajenie/merfisheyes/blob/main/docs/points-zarr-spec.md)) | square 2-D, 100 µm doubling | row numbers | nested, uniform 1/4 | feature-major |
| spatiato ([cache format](https://github.com/vibspatial/spatiato/blob/main/src/spatiato/core/multi_scale_cache_points_zarr/CACHE_FORMAT.md)) | square 2-D | row numbers per level | nested, per-tile cap | feature-major (xy + id) |
| Neuroglancer ([annotations](https://github.com/google/neuroglancer/blob/master/src/datasource/precomputed/annotations.md)) | per-axis chunk size, any origin | sharded by Morton code | disjoint, density-preserving | by id, by relationship (all fields) |
| Luxar ([format contract](https://github.com/royerlab/luxar/tree/main/format-contract)) | chunk bounds | Hilbert order | disjoint, additive | none |
| zarr-vectors ([docs](https://zarr-vectors-py.readthedocs.io/)) | chunks + bins | chunk | centroid pyramid | none |

Considered and not chosen:

- Image-pixel grid: SpatialData has no pixel space, and points can exist without an image.
- Row groups by formula only: ties the index to Parquet.
- Tile-relative float32 or uint16 coordinates: can come later as a codec without changing the type.

## Implementation

> **TODO:** spatialdata (read/write), spatialdata-io (Celldega PR #423), tissue-map-tools (sampling),
> a viewer (Celldega, Vitessce, TissUUmaps, merfisheyes, spatiato).

## Discussion

- [Original proposal by Celldega](https://github.com/scverse/spatialdata/discussions/1251), September 2026.
- [Options and proposal (Google Doc)](https://docs.google.com/document/d/1-lX85Qzm88qIprGJIW_IjUoi8LrCTZC8XXF22RZjqDk/edit)
- Open: the TODO notes above; where CSR/CSC belongs (separate spec, Ilan).

## References

- [RFC 4: Tiled and multiscale shapes](0004-tiled-shapes.md)
- [zarr-conventions multiscales](https://github.com/zarr-conventions/multiscales)
