---
rfc: 3
title: "Tiled and multiscale points"
authors: "Luca Marconato ([@LucaMarconato](https://github.com/LucaMarconato)); input from Nicolas Fernandez ([@cornhundred](https://github.com/cornhundred)), Arne Defauw, Jonas Windhager, Ilan Gold, Ignatius Jenie, Mark Keller, Christian La France, Tim Treis, Marco Varrone, Sonja Stockhaus, Brian Long, Clarence Mah"
status: "draft"
type: "data model; storage format"
created: 2026-09-17
---

# RFC 3: Tiled and multiscale points

## Abstract

Specification for spatially indexing points, enabling optional multiscale subsampled levels, spatially chunked storage: a regular
2-D or 3-D grid of tiles, with the points stored in tile-major order and, optionally, in feature-major order. Each point carries a
random value $p$, which defines the levels. This enables viewers and other processing applications to load only the points
in view, or only those of the genes shown; zoomed out, they load a density-preserving sample, with as many points as the
resources they have available allow (memory, bandwidth, rendering time). Shapes are in [RFC 4](0004-tiled-shapes.md).

:::{figure} img/0003-summary.svg
:alt: Overview of the spatial index. Top: 44 points of genes A and B and of a rare gene C (3 points, one kept at level 1, none at level 2) on a rectangular support, shown at three levels; level 0 on a grid of 8 × 4 rectangular tiles holds all the points (p < 1), level 1 on 4 × 2 tiles holds those with p < 0.3, level 2 on 2 × 1 tiles holds those with p < 0.1. Each point has a random value p in [0, 1), shown on a ruler split into bands 2, 1 and 0 at 0.1 and 0.3. Bottom: the tile-major table holds every point once, as bands (coarsest first), tiles inside each band and rows sorted by p; tile_offsets point at the first row of each tile, and the row groups follow the tiles, with small tiles of a band sharing one row group. Two queries are shown. View 1 (dashed red), one tile of level 1 with all genes: it reads level 1, so the tile-major table reads two compact ranges, the rows of band 2 in the tile of level 2 that contains it and the rows of that tile in band 1 (5 rows). The feature-major table holds the same points sorted by gene, then band, then tile, then p: the 3 points of the rare gene C are one short range at its end. Inside each gene and band the rows are again grouped by tile, shown by separators in both tables. Its tile_offsets point at the start of each tile inside each gene's band, and its row groups follow one gene in one band, with small ones sharing a row group. For view 1 the feature-major table reads the same 5 rows, but as one range per gene and band, found through its tile_offsets. View 2 (dashed green), another region with only the rare gene C selected, drawn on all three levels: it fits, so all its bands are read, at every level. The tile-major table reads all the rows of the tiles of view 2 in every band (6 rows in 4 ranges) and discards the other genes, drawn faded, to keep 1 row of gene C; the feature-major table reads only that row.

Overview of the spatial index; each part is described in the text.
:::

## Description

The key words MUST, MUST NOT, SHOULD, SHOULD NOT and MAY are to be interpreted as described in
[RFC 2119](https://www.rfc-editor.org/rfc/rfc2119). Key words have this meaning only in capitals
([RFC 8174](https://www.rfc-editor.org/rfc/rfc8174)).

### Scope

- In scope: points, 2-D and 3-D; spatial indexing via chunking and sorting; tile-major order and feature-major order; sampled levels; a per-point random value $p$.
- Out of scope: shapes ([RFC 4](0004-tiled-shapes.md)), the matrix of a table annotating the shapes and its sparse storage (CSR/CSC, RFC 4), aggregation to cells or bins (square/hexagonal), spatial orders inside tiles (Morton, Hilbert), ordering of the tiles other than C order (e.g. Morton).

## Data model

The data model does not depend on how the points are stored, in Parquet or in Zarr
([Storage format](#storage-format)).

### Overview

This section is an overview: it lists all the terms of the spatial index and how they relate. Each
is defined in the sections that follow, starting from the tiles, then $p$, which defines levels and
bands on top of them; [Summary](#summary) lists them again in a table, with which are required. The
terms are in three layers: the data, the data model and the storage format.

**Data.** The points with their columns (coordinates, feature, any other) are always there, as
today. The data model and the storage format of the spatial index are optional: an element may have
no spatial index at all. If it has one, some of its parts MUST be present, others SHOULD or MAY be.

**Data model.** It says which tile and which level each point belongs to:

- grid parameters: the axes; per axis, the origin $o_a$ and the tile size
  $s_a$ of level 0; the grid of every coarser level, which refines the next one (recommended recipe:
  the merge rule) ([Grid and tiles](#grid-and-tiles));
- sampling parameters: a random value $p$ per point, and the fraction $P^{(l)}$ of each level, a
  fixed rate, by default the ratio of the tile volumes of level 0 and level $l$ ($1/2^d$ per level
  when all $d$ axes are merged); level $l$ holds the points with
  $p < P^{(l)}$ ([Priority](#priority), [Levels and bands](#levels-and-bands), [Sampling](#sampling));
- derived from these, the number of points per tile at each level, which guides the choice of the
  tile size and the rates together ([Choosing the tile size and the rates](#choosing-the-tile-size-and-the-rates));
- the feature column (e.g. the gene), which sorts the feature-major order
  ([Tile-major order and feature-major order](#tile-major-order-and-feature-major-order)).

**Storage format.** It says how the points are written ([Storage format](#storage-format)), in
Parquet or in Zarr:

- the metadata declares which parts are present: the orders (tile-major and feature-major), the
  levels, and the grid and sampling of each level;
- each order is one table, with the levels as bands of rows, with offsets that address rows:
  `tile_offsets` in the tile-major table (the tile index) and in each feature-major table (the
  feature index), and the column `__spatialdata_p__`, which stores $p$;
  the row groups (Parquet) or chunks (Zarr) are a choice of the writer.

### Grid and tiles

A grid is defined for a specific *points element* (the SpatialData term for a 2D/3D points cloud), in the coordinates of its points. The metadata MUST specify the axes of the grid.

Different elements use different grids: reusing the same grid for 2 or more elements is out of scope for this RFC ([RFC 4](0004-tiled-shapes.md) will discuss reusing the same grid for points (transcripts) and shapes (cells)).

An axis $a$ is one of the spatial axes $x$, $y$ and $z$ (not the channel axis $c$). The grid has, per axis $a$,
an arbitrary origin $o_a$, which MUST be given (for instance the corner with the minimum coordinates of the bounding box
of all the points), one tile size $s_a$, which MUST be given (square tiles are a special case), and an arbitrary number of
tiles $n_a$: the number of intervals into which the grid divides axis $a$, not the total number of
tiles of the grid, which is $N = \prod_a n_a$. All the tiles are identical. The tiles MUST cover all the points.
Each tile is to be interpreted as a semi-open hyper-interval, with the interval closed for the lowest
value, and open for the highest. For example, in 2 dimensions, the tile

$$
[\, x_{\min},\ x_{\max} \,) \times [\, y_{\min},\ y_{\max} \,)
$$

contains the points $(x, y)$ that satisfy $x_{\min} \le x < x_{\max}$ and $y_{\min} \le y < y_{\max}$.

The grid of every level present, $0, \dots, L$, MUST be given in the metadata (see
[Metadata](#metadata)); since level 0 is always present, so is its grid. The grids of the coarser
levels are the writer's choice, with one constraint: the grid of each level $l$ MUST refine the grid
of level $l + 1$, that is every tile of level $l$ MUST lie inside a single tile of level $l + 1$, so
that no tile of a finer level overlaps several tiles of a coarser level. The grids SHOULD get coarser
with the level, but a level MAY keep the grid of the level below, since a grid refines itself: at the
limit, a single tile for the whole dataset at every level, or the same grid at all the levels, which
avoids the many small, almost empty tiles of the coarse levels of a rare feature.

A recommended recipe, the *merge rule*, builds the grid of each coarser level from the grid of the
previous level: it is merged by a factor of 2 along one or more axes, keeping the tiles as isotropic
as possible. It satisfies the constraint, since the origin stays the same and each tile size is
either kept or doubled, and the initial grid then determines the granularity of the spatial index at
every level. Below are two merging steps that keep the tiles as isotropic as possible: in the first, by merging
along one axis; in the second, by merging along two axes.

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

Applied to the end, the merge rule stops at the first level with $n_a = 1$ along every axis (a
single tile). A writer may also stop earlier, so the lowest-resolution level may still contain multiple
tiles.

Example: an anisotropic extent, 10 × 100 × 1000 along (z, y, x), origin 0.

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

### Priority

Every point $i$ MUST have a uniformly sampled random value $p_i \in [0, 1)$, termed *priority*, adapted
from the continuous level of detail of [van Oosterom et al., 2022](#references) and
[Schütz et al., 2019](#references). It is drawn once when the points are written and MUST be
stored with them, as a column (see [Columns](#columns)). Any uniform random generator may be used, and $p$ may
be derived from a hash of the point. The priority is fixed: it defines which points are in which
level, and the order of the rows inside a tile, in both orders of the points.

### Levels and bands

Every point belongs to exactly one *band* $l \in \{0, \dots, L\}$, $L \ge 0$, given by its $p$ and
by fractions $1 = P^{(0)} > P^{(1)} > \dots > P^{(L)}$ (see [Sampling](#sampling)):

$$
\text{band } L = \{\, i : p_i < P^{(L)} \,\}, \qquad
\text{band } l = \{\, i : P^{(l+1)} \le p_i < P^{(l)} \,\} \quad (l < L)
$$

With $L = 0$ there is a single band, with all the points; bands $1, \dots, L$ MAY be present. The
tiles of band $l$ are those of the grid of level $l$. Level $l$ is the union of the bands
$L, L - 1, \dots, l$, the points with $p < P^{(l)}$; level 0 holds all the points.

:::{figure} img/0003-levels-bands.svg
:alt: The axis of p from 0 to 1, cut at P(2) and P(1) into three disjoint bands, 2, 1 and 0. Below, level 2 covers band 2; level 1 covers bands 2 and 1; level 0 covers all three bands.

A level is the union of its band and all coarser bands.
:::

This is the priority-band (continuous level of detail) organization of
[van Oosterom et al., 2022](#references), with discrete bands on a grid.

### Tile-major order and feature-major order

An *order* is a table with all the points and all their columns, sorted in a given way. The points
are written in exactly one tile-major order and in zero, one or more feature-major orders, one per
feature column chosen by the writer and named in the metadata:

- tile-major order, which MUST be written: sorted by band (coarsest first, see
  [Levels and bands](#levels-and-bands)), then by tile id on the grid of the band, then by $p$;
- feature-major order, optional, for a given feature column named in the metadata: sorted by
  feature, then by band, then by tile id, then by $p$. The feature is a categorical column chosen
  when writing: for spatial transcriptomics, usually the gene id. A writer MAY choose several feature
  columns, for instance the gene id and the cell type, each with its own feature-major table; it
  SHOULD choose at most one, the column used most often to select points, for the best performance
  at the lowest storage cost.

Both orders hold exactly the same points at every level; only the order of the rows differs, so a
client gets the same result from either, at a different cost. Since each order is sorted by band,
coarsest first (see [Levels and bands](#levels-and-bands)):

- each point is stored once per order: the levels need no extra storage (up to 1.33× in 2-D if each
  level were a table of its own);
- going to a finer level reads only the next band; the points already loaded stay valid;
- with the rows of each tile sorted by $p$, a client can stop reading at any budget $b$, not only
  at the $P^{(l)}$ of the levels (see [Reading with a budget](#reading-with-a-budget)).

The two orders answer two different questions with a contiguous range of rows:

- Tile-major order: *which points are in this region?* The points of a tile are one row range, whatever
  their gene. A client showing the region reads the tiles in view.
- Feature-major order: *where are the points of this gene?* The points of a gene are one row range;
  inside it, the points of each band are one range, and inside a band the points of each tile. A client showing a
  few genes reads only their points.

A client looking for the points of a feature uses the feature-major table of that column if there
is one. Otherwise it falls back to the tile-major table, as for any other column: it reads every
point of the tiles in view and discards the other features, so the cost grows with all the points
in view, not with the points of the feature; zoomed out, this can be most of the data. The price of
the feature-major table is a second table of the points. Per-tile statistics (e.g. which features a tile contains, or how many points of each)
could let a client skip tiles without the feature it shows and improve performance; they are out of scope for this RFC.

:::{figure} img/0003-orders.svg
:alt: Eight points of genes A and B in two tiles, each with its p. Level 1 is a single tile with the points p < 0.25 (A5, B2, A3), which form band 1; the other five form band 0. Tile-major table: band 1 (A5, B2, A3), then band 0 by tile (tile 0: A1, B8; tile 1: A7, B6, B4). Feature-major table: gene A (band 1: A5, A3; band 0: A1, A7), then gene B (band 1: B2; band 0: B8, B6, B4); a second row of brackets shows the tiles inside each band of each gene (band 1: tile 0 of level 1; band 0: tiles 0 and 1).

The two orders, as bands. Each table holds every point once, in the band of the coarsest level that
holds it: band 1 is level 1 ($p < 0.25$), and both bands together are level 0.
:::

### Sampling

Sampling chooses the fractions $P^{(l)}$ of the levels (see [Levels and bands](#levels-and-bands)). The fractions are
fixed rates: they do not depend on how many points the tiles hold, and the same $P^{(l)}$ applies to
all the points, whatever their feature, and to both orders. Level $l$ keeps the points with
$p < P^{(l)}$.

By default, the fraction of a level is the ratio of the tile volumes (areas in 2-D) of level 0 and
of that level:

$$
P^{(l)} = \frac{V^{(0)}}{V^{(l)}}, \qquad V^{(l)} = \prod_a s_a^{(l)} .
$$

A tile of level $l$ then covers $V^{(l)} / V^{(0)}$ tiles of level 0 and keeps that fraction of
their points, so it holds on average as many points as a tile of level 0 in the same region,
whatever axes were merged. With the merge rule, each level divides the fraction by 2 per merged
axis: $1 / 2^d$ per level when all $d$ axes are merged (1/4 in 2-D, 1/8 in 3-D), more when only
some are. A writer MAY choose any other rates, as long as they strictly decrease with $l$. When a
level keeps the grid of the level below, the tile volume does not change and the default would keep
the same fraction; the writer then chooses the rates, e.g. $1/2^d$ per level. Dense
regions stay denser than sparse ones: the sample is density-preserving.

Because $p$ is uniform, keeping the points with $p < P^{(l)}$ keeps each point with probability
$P^{(l)}$, independently of the others.

The $P^{(l)}$ of every level present, including $P^{(0)} = 1$, MUST be given in the metadata (see
[Metadata](#metadata)); a
reader uses the values of the metadata, whatever rates the writer chose.

:::{dropdown} Sampling in formulas

A tile of level $l$ with volume $V^{(l)}$ (area in 2-D) in a region of density $\rho$ holds on
average

$$
n^{(l)} = \rho\, V^{(l)}\, P^{(l)}
$$

points. With the default rates $P^{(l)} = V^{(0)} / V^{(l)}$ the two factors cancel, and
$n^{(l)} = \rho\, V^{(0)} = n^{(0)}$ at every level. With the merge rule and all $d$ axes merged at
every level, $V^{(l)} = 2^{d\,l}\, V^{(0)}$ and $P^{(l)} = 2^{-d\,l}$. For example, in 2-D with tiles of 10 × 10 at level 0 and of 40 × 40 at
level 2, a tile of level 2 covers 16 tiles of level 0 and keeps 1 point in 16.

:::

A client MAY support only level 0 and ignore the sampled levels, and show zoomed-out views with
other strategies, such as aggregation (see [RFC 4](0004-tiled-shapes.md#levels)).

### Choosing the tile size and the rates

The levels and the tiles let a client read only a part of the data: the tiles in view, at a level
coarse enough for the view. This works well only if the tile size and the rates suit the data and
each other. There is no parameter for this in the format: the number of points per tile at each
level, $n^{(l)}$, follows from the density of the points, the tile size and the rates (see
[Sampling](#sampling)), and guides the choice of the two.

A good target is the number of points a client can comfortably load and display at once from one
tile, for now about 10,000, while this RFC is a draft; it will be adjusted from user feedback. The
reasoning: with the coordinates and a feature code, about 16 bytes per point, a tile is about
160 kB before compression, a comfortable size for one request, and a view of 4 × 4 tiles shows
about 160,000 points, which a browser renders easily. The target is not stored in the metadata and
is not a cap: level 0 holds all the points, and a tile may hold any number of them.

The tile size of level 0 should then be chosen so that the densest tile of level 0 holds about the
target number of points: $n^{(0)}$, the number of points per tile of level 0 (see
[Sampling](#sampling)), about equal to the target in the densest region. If the densest region has $\rho$ points per unit of area (2-D) or
volume (3-D), the tile size along each of the $d$ axes is about

$$
s \approx \left( \frac{n^{(0)}}{\rho} \right)^{1/d}.
$$

This estimate assumes that the points are roughly uniformly distributed at the scale of a tile, and
that the tiles are isotropic. Larger-scale variations are taken into account by using the density of
the densest region; a hotspot smaller than a tile is not (see case (d) below). In practice, a writer
can also pick a tile size, count the points of the densest tile, and adjust.

With the default rates, $n^{(l)} = n^{(0)}$: the densest tiles then hold about the target number of
points at every level (see [Sampling](#sampling)). What is stored per tile is a band, a part of its level: band $l$ holds a
fraction $1 - P^{(l+1)} / P^{(l)}$ of the level-$l$ points of the tile (3/4 in 2-D with all axes
merged).

The cost of a view stays about the same as the client zooms in and out, plus one cost of the bands:
to show a small region at full detail, a client also needs the points of the coarser bands in that
region. These are stored in the larger tiles of the coarser levels, so the client reads those
larger tiles and discards the points outside the view.

:::{figure} img/0003-tile-size.svg
:alt: Four panels with the same target of 40 points per tile. (a) 4 × 4 tiles on uniform points, densest tile 37 points. (b) 2 × 2 tiles, densest tile 127 points, all tiles above the target. (c) 16 × 16 tiles, densest tile 6 points. (d) 4 × 4 tiles with a hotspot, one tile of 220 points, the others at most 16.

The tile size of level 0 for a target of 40 points per tile, on 400 points.
:::

The figure shows the edge cases:

- (a) Tiles that fit: the densest tile holds about the target number of points.
- (b) Tiles too large: the tiles of level 0 hold far more points than the target. Level 0 is not
  sampled, but a client zoomed in does not have to load a whole tile: its rows are sorted by $p$,
  so the first rows are a fair sample of it (see [Reading with a budget](#reading-with-a-budget)), and
  the storage can split it into several row groups or chunks (see
  [Points as a tall table](#points-as-a-tall-table)). The cost is coarser spatial selection: a
  client still reads tiles that are only partly in view. A finer grid is better.
- (c) Tiles too small: many tiles with few points each, so a view needs many small requests and the
  index is large. With the default rates, each level keeps about as many points per tile as the level below, so the
  tiles of the coarser levels hold few points too, and a view needs many small requests at every
  level.
- (d) Hotspot: a region much denser than the rest puts many points in a few tiles. A tile size
  chosen for the hotspot is too small elsewhere, as in (c); one chosen for the rest is too large in
  the hotspot, as in (b), and handled as in (b). A future extension could address this with an
  adaptive grid, if the community identifies it as a need.

The grid and the rates are the same for all the features, so a rare feature has few points per
tile, and at the coarser levels few or none: in the feature-major table most of its tiles are empty.
This is not a problem: an empty tile holds no rows and costs only its entry in
the `tile_offsets` of the feature-major table, and the rows of a feature are contiguous, sorted by band, so a client showing
a rare feature reads all its levels, down to level 0, as one contiguous range.

#### Reading with a budget

Sometimes a client does not have the resources to read all the points of the tiles in view, even at
the right level: for instance with tiles that are too large, as in case (b). Here $p$ comes into
play. With a *budget* $b \in (0, 1]$, the client reads only the points with $p < b$: since $p$ is
uniform, a representative sample of a fraction $b$ of the points, and since the rows of each tile
are sorted by $p$, the first rows of each tile. The budget is not limited to the fractions
$P^{(l)}$ of the levels: the client reads the coarsest level with $P^{(l)} \ge b$, the bands
coarser than $l$ in full and band $l$ up to $p < b$.

## Storage format

The data model above can be implemented both in Parquet and in Zarr, and this RFC describes both.
SpatialData already stores points in Parquet, so the Parquet format is to be interpreted as the
default, and the Zarr format as experimental. Whether the Zarr format replaces it or the two coexist will be determined from user
feedback and real usage; Zarr would also be more flexible for 3-D shapes (meshes, see
[RFC 4](0004-tiled-shapes.md)) and closer to zarr-vectors (see [Related work](#related-work)).

The format is self-contained: compatible with the way OME-NGFF stores coordinate systems, but usable
on its own, even outside an OME-Zarr store, because its metadata is defined as a Zarr convention.
Compatible means that this storage of points could in the future be proposed as an OME-NGFF
extension, with the extensibility mechanism of
[NGFF RFC-8](https://ngff.openmicroscopy.org/rfc/8/index.html), and later, through an NGFF RFC, as
part of the OME-NGFF specification. This is not a goal for now: for the time being this
specification remains part of SpatialData, and is neither an official OME-NGFF extension nor
OME-NGFF compliant.
Parquet has no equivalent of Zarr conventions, so the Parquet format reuses the same syntax for its
metadata.

The spatial index is optional (see [Overview](#overview)). Without it, an element is stored as today
(see [Compatibility](#compatibility)). With it, the metadata declares which parts are present (see
[Metadata](#metadata)).

### Points as a tall table

In both formats, each table of points is a tall table: one row per point, one column per attribute.
The tile index and the feature index address rows (see [Tile index](#tile-index),
[Feature index](#feature-index)). How the rows are split into row groups (Parquet) or chunks (Zarr)
is a choice of the writer, not declared by this convention: Parquet row groups may have any size,
and the footers of the files give their row counts; Zarr chunks have the chunk length of the array,
given in its metadata. A reader maps a range of rows to the row groups or chunks that overlap it: in
Zarr, with chunk length $c$, the rows $[\,a, b\,)$ are in the chunks $\lfloor a / c \rfloor, \dots,
\lfloor (b - 1) / c \rfloor$. A row group or chunk may hold several small tiles, and a large tile may
span several. The row groups are grouped into the part files of a multi-file Parquet dataset; the
chunks into shards in Zarr.

To read a tile with few requests:

- Parquet writers SHOULD align the boundaries of the row groups with those of the tiles: one row
  group per tile of a band when the tile is large enough, several small tiles in one row group to
  avoid tiny row groups, and a large tile split into several. In the feature-major table, the same
  with the groups of rows of one feature in one band.
- Zarr writers SHOULD choose a chunk length close to the typical number of rows of a tile.

These are recommendations and not requirements because no single layout fits all the data, and the
index addresses rows, so any layout is readable. In the tile-major table, one row group per tile
would give tiny row groups in sparse regions and in the coarse bands, and huge ones in hotspots. In
the feature-major table, one row group per feature, band and tile would give up to
$n_\text{features} \times N_\text{tiles} \times (L + 1)$ row groups, e.g. 500 genes × $10^5$
tiles = up to $5 \cdot 10^7$, almost all tiny; one per feature and band gives a few thousand.

Another option in Zarr is rectilinear chunk grids, an experimental Zarr feature that allows chunks
of different sizes along an array: each tile would then be one chunk of its own size.

A spatial index without a spatial subdivision is a special case of this format, not a separate one:
a grid with a single tile covering all the points, the same at every level (see
[Grid and tiles](#grid-and-tiles)). Each band is then one range of rows sorted by $p$, so any first
rows of a band are a uniform sample of it, which a reader can load progressively.

### Metadata

Both formats store the metadata in the `zarr.json` of the Zarr group of the points element. In the
Zarr format the points are Zarr arrays inside that group; in the Parquet format they are Parquet
files inside that group (see [File layout](#file-layout)):

```text
points/<name>/
├── zarr.json        # the metadata, in both formats
└── …                # the points: Zarr arrays, or Parquet files
```

The metadata is a Zarr convention, `spatial_index`, next to the existing attributes of the element.
It is registered in `zarr_conventions` with its name and the URL of this specification; the uuid and
a JSON schema are optional and will be added when the convention is released. `levels` lists the
levels present, level 0 first, each with its grid and, for the coarser levels, its fraction:

```json
{
  "zarr_conventions": [
    {
      "name": "spatial_index",
      "spec_url": "https://spatialdata-spec.scverse.org/rfcs/0003-tiled-points.html",
      "description": "Tiled and multiscale points"
    }
  ],
  "spatial_index": {
    "version": "0.1.0-draft",
    "axes": ["x", "y", "z"],
    "feature_keys": ["gene", "cell_type"],
    "levels": [
      {
        "origin": [0.0, 0.0, 0.0],
        "tile_size": [100.0, 100.0, 10.0],
        "grid_shape": [120, 80, 3],
        "P": 1.0
      },
      {
        "origin": [0.0, 0.0, 0.0],
        "tile_size": [200.0, 200.0, 20.0],
        "grid_shape": [60, 40, 2],
        "P": 0.125
      }
    ]
  }
}
```

`version` is the version of this specification that the element follows; it MUST be given, so that
readers can tell future versions (e.g. with tiles in Morton order) apart. While this RFC is a draft,
the version carries the suffix `-draft`. Following the versioning of Zarr conventions, a released
version will also be referenced by a `spec_url` (and `schema_url`) pinned to that version, e.g. a
tagged URL. `levels[l]` gives the grid of level $l$: `origin`, `tile_size` and `grid_shape` (the
number of tiles $n_a$ along each axis). `P` is the fraction $P^{(l)}$ of the level (here 1/8, the
default in 3-D), the same for both orders: level $l$ holds the points whose value of $p$ (column
`__spatialdata_p__`) is below `P`. The `P` of level 0 MUST be 1: level 0 holds all the points.
`feature_keys` lists the feature columns, here two, the gene and the cell type: each has its own
feature-major table (see [File layout](#file-layout)), and it is empty if there is none. The
tile-major table is always present. The tile index of level $l$ is `tile_offsets/<l>` (see
[File layout](#file-layout)).

### File layout

Parquet (backward compatible: the tile-major table, with every point once, sits where readers look
today, so unlike in Zarr it is not put inside a new group `spatial/`):

```text
points/<name>/
├── zarr.json                      # attrs incl. spatial_index
├── points.parquet/                # tile-major, all bands: part.0.parquet, part.1.parquet, …
├── tile_offsets/                  # Zarr int64 arrays, the tile index of each band
│   ├── 0
│   ├── 1
│   └── …
└── feature/                       # optional: one feature-major table per entry of feature_keys
    ├── gene/
    │   ├── points.parquet/
    │   └── tile_offsets/          # the feature index: start of each tile of each feature, per band: 0, 1, …
    └── cell_type/
        └── …
```

Zarr (the points as a dataframe, see [Columns](#columns)):

```text
points/<name>/
├── zarr.json                      # attrs incl. spatial_index
├── spatial/                       # tile-major, all bands
│   ├── points/                    # df: convention
│   │   ├── columns                # ["x", "y", "z", "gene", "__spatialdata_p__", …]
│   │   ├── column_0               # x
│   │   ├── column_1               # y
│   │   ├── column_2               # z
│   │   ├── column_3/              # gene, enum: convention
│   │   │   ├── codes
│   │   │   └── enum_values
│   │   ├── column_4               # __spatialdata_p__
│   │   └── …                      # the other columns
│   └── tile_offsets/              # the tile index of each band: 0, 1, …
└── feature/                       # optional: one feature-major table per entry of feature_keys
    ├── gene/
    │   ├── points/
    │   └── tile_offsets/          # the feature index: start of each tile of each feature, per band: 0, 1, …
    └── cell_type/
        └── …
```

In both formats, the offsets (`tile_offsets`, of the tile-major and of the feature-major tables) are Zarr
arrays, the same in Parquet and in Zarr: chunked, so a reader fetches only the chunks of the offsets
it needs. They SHOULD be chunked so that a lookup reads one small chunk: e.g. chunks of 65,536
entries for the 1-D arrays, and of one feature × 65,536 tiles for the 2-D `tile_offsets` of the feature-major tables, so that
the offsets of one feature are one read. In Zarr, they sit next to the dataframe, not inside it: the `df:` convention requires all
the members of the group to be columns of the same length.

### Columns

- `x`, `y`, `z`: float32, absolute, in the element's coordinate system. (Spacing of float32 at
  10 cm in µm units is about 8 nm, well below localization error.)
- Feature: integer codes with the category list stored once. In Zarr, the column follows the
  [`enum:` convention](https://github.com/scverse/zarr-convention-enum): the arrays `codes` and
  `enum_values`, the categories; the number of features is the length of `enum_values`. In
  Parquet, a dictionary-encoded column.
- $p$: float32 in $[0, 1)$, uniform, in the column `__spatialdata_p__`, a name reserved by
  SpatialData, the same in every element. Ties between equal values (float32 has $2^{24}$ values in $[0, 1)$) are harmless:
  levels compare $p$ with $P^{(l)}$, and ties may be in any order inside a tile.
- Any other columns, unchanged.

In Zarr, each table of points is a dataframe following the
[`df:` convention](https://github.com/scverse/zarr-convention-dataframe): one 1-D array, or a group
read as one, such as an `enum:` column, per column, all of the same length.

#### Order of the columns

Within a row group, Parquet stores the values column by column: a row group holds
the values of the first column, then those of the second, and so on, in the order of the schema.
The coordinate columns SHOULD come first and next to each other, in the order of `axes`, followed by
the feature column(s) and `__spatialdata_p__`, then by the other columns. A client reading the coordinates and the feature
of a tile then reads one contiguous byte range instead of one per column.

In Zarr, each column is an array of its own, all with the same chunk length, so the same chunks of
each array hold the same rows: a client reads a tile with one request per column and per chunk that
overlaps the tile, whatever the order of the columns. The coordinate and
feature columns SHOULD still come first, in the same order as in Parquet.

:::{figure} img/0003-columns.svg
:alt: A tall table of three columns x, y, z (blue, red, green) and three tiles of 4, 2 and 3 rows. In Parquet, row group 0 holds tile 0 and row group 1 holds tiles 1 and 2; each row group holds all its x values, then all y, then all z, in one byte range. In Zarr each column is an array of its own, column_0 to column_2, cut into chunks of 4 rows independently of the tiles: chunk 0 is tile 0, chunk 1 holds tile 1 and the start of tile 2, chunk 2 the end of tile 2.

The tiles are row ranges. In Parquet the row groups follow the tiles; in Zarr the chunks have a
fixed length and may cut a tile.
:::

### Tile index

To find the points of a tile, a reader uses the tile index of a band of the tile-major table. Since
the rows of a band are sorted by tile id, the points of each tile are consecutive rows. The index of
band $l$, which MUST be written, records where each tile starts: an integer array `tile_offsets/<l>` ($O$, int64) with one entry
per tile plus one, for the $N$ tiles of the grid of level $l$, in rows of the table. The points of
tile $k$ in the band are the rows

$$
[\, O_k,\ O_{k+1} \,), \qquad O_0 = \text{first row of the band}, \quad O_N = \text{end of the band},
$$

so tile $k$ holds $n_k = O_{k+1} - O_k$ points, and an empty tile has $O_k = O_{k+1}$. The rows of
the band are $[\, O_0, O_N \,)$: the range of each band follows from its tile index. A reader
reads these rows from the row groups or chunks that overlap them (see
[Points as a tall table](#points-as-a-tall-table)). A client with a budget $b$
reads the first rows of the tile, until it reaches a row with $p \ge b$.

### Feature index

Each feature-major table MUST have its own `tile_offsets`, one array per band, as the tile-major
table, but with one row per feature, since inside a band the rows are grouped by feature first:

```text
tile_offsets/<l>: int64[n_features, N_tiles(l) + 1]   # per band l: where each tile of feature g starts
rows of feature g, band l, tile k  = [tile_offsets[l][g, k], tile_offsets[l][g, k + 1])
rows of feature g, band l          = [tile_offsets[l][g, 0], tile_offsets[l][g, -1])
rows of feature g, level l         = [tile_offsets[L][g, 0], tile_offsets[l][g, -1])   # bands L..l, one range
```

The table is sorted by feature, then by band, so the bands $L, \dots, l$ of a feature are one range
of rows: from the first offset of its coarsest band to the last offset of band $l$. In the example
of the orders figure (see
[Tile-major order and feature-major order](#tile-major-order-and-feature-major-order)), with bands 1
and 0 and the 2 tiles of level 0, gene A has `tile_offsets` [0, 2] in band 1 and [2, 3, 4] in band
0: level 1 is rows $[\,0, 2\,)$ and level 0 rows $[\,0, 4\,)$. Gene B has [4, 5] and [5, 6, 8].

These offsets give the rows of a feature in the tiles in view, the number of points of a selection
in view, and let a client skip the tiles where a feature is absent. They have about
$n_\text{features} \times N_\text{tiles}$ entries per band: large for band 0, e.g. about 400 MB as
int64 for 500 genes and $10^5$ tiles, and small for the coarser bands.

> **TODO(Luca):** Ilan suggests writing both orders by default, configurable; the proposal said
> "recommended but optional". Pending his answer on the Google Doc comment (transcripts or cell
> matrix?).

### Reading

```python
b, l = budget(view, selection)                   # see "Reading with a budget"
for band in range(L, l - 1, -1):                 # coarsest band first
    for k in tiles_intersecting(view, level=band):   # tile ids, see "Tiles ordering"
        rows = range(tile_offsets[band][k], tile_offsets[band][k + 1])
        yield prefix(rows, p < b)                # rows sorted by p: all of a coarser band; a prefix of band l
```

### Compatibility

- Without `spatial_index` an element reads as today.
- Old readers of a tiled Parquet element read the tile-major table: every point once, in a
  different row order, with an extra column `__spatialdata_p__`. They ignore the rest.

> **TODO(Luca):** confirm the current Parquet path (`points.parquet/`) and whether the extra
> directories break current readers.

### Summary

The terms of this RFC in three layers. The data is always there. The data model and the storage
format of the spatial index are optional; the requirements below apply only to an element that has
a spatial index.

| Layer | Term | Requirement | Section |
| :- | :- | :- | :- |
| Data | the points, one row each, with their coordinates, feature and other columns | always present, as today | [Columns](#columns) |
| Data model | axes | MUST | [Grid and tiles](#grid-and-tiles) |
| | origin $o_a$ and tile size $s_a$ of level 0, per axis | MUST | [Grid and tiles](#grid-and-tiles) |
| | bands $0, \dots, L$ ($L \ge 0$): band 0 always, bands $1, \dots, L$; level $l$ = bands $L, \dots, l$ | MAY | [Levels and bands](#levels-and-bands) |
| | grid of every level present, $0, \dots, L$ | MUST | [Grid and tiles](#grid-and-tiles) |
| | grid of each level refines the grid of the next coarser level (recommended recipe: the merge rule) | MUST |
| | grids get coarser with the level (a level may keep the grid of the level below) | SHOULD | [Grid and tiles](#grid-and-tiles) |
| | tile order: C order of the tile ids | MUST | [Tiles ordering](#tiles-ordering) |
| | random value $p$ per point | MUST | [Priority](#priority) |
| | fraction $P^{(l)}$ of every level present ($P^{(0)} = 1$), a fixed rate (default: ratio of the tile volumes of level 0 and level $l$; any strictly decreasing rates allowed) | MUST | [Sampling](#sampling) |
| | feature column(s) | MAY; at most one SHOULD | [Tile-major order and feature-major order](#tile-major-order-and-feature-major-order) |
| Storage format | metadata: `spatial_index` convention, with its `version` and its `levels` | MUST | [Metadata](#metadata) |
| | Parquet (default) or Zarr (experimental) | MUST, one of them | [Storage format](#storage-format) |
| | column `__spatialdata_p__` | MUST | [Columns](#columns) |
| | tile-major table, levels as bands | MUST | [Levels and bands](#levels-and-bands) |
| | tile index: `tile_offsets` of every band | MUST | [Tile index](#tile-index) |
| | row groups aligned with the tiles (Parquet); chunk length close to the rows of a tile (Zarr) | SHOULD | [Points as a tall table](#points-as-a-tall-table) |
| | feature-major table, one per feature column | MUST, for each feature column | [Tile-major order and feature-major order](#tile-major-order-and-feature-major-order) |
| | feature index: `tile_offsets`, per band, feature and tile | MUST, with a feature-major table | [Feature index](#feature-index) |
| | offsets chunked for small reads (e.g. 65,536 entries; one feature per chunk row) | SHOULD | [File layout](#file-layout) |
| | coordinate and feature columns first | SHOULD | [Order of the columns](#order-of-the-columns) |

## Related work

| Format | Grid | Index | Levels | Second order |
| :- | :- | :- | :- | :- |
| Celldega ([#1251](https://github.com/scverse/spatialdata/discussions/1251), [PR #423](https://github.com/scverse/spatialdata-io/pull/423)) | square 2-D, image pixels, origin (0, 0) | one row group per tile | none | none |
| merfisheyes ([spec](https://github.com/kresnajenie/merfisheyes/blob/main/docs/points-zarr-spec.md)) | square 2-D, 100 µm doubling | row numbers | nested, uniform 1/4 | feature-major |
| spatiato ([cache format](https://github.com/vibspatial/spatiato/blob/main/src/spatiato/core/multi_scale_cache_points_zarr/CACHE_FORMAT.md)) | square 2-D | row numbers per level | nested, per-tile cap | feature-major (xy + id) |
| Neuroglancer ([annotations](https://github.com/google/neuroglancer/blob/master/src/datasource/precomputed/annotations.md)) | per-axis chunk size, any origin | sharded by Morton code | disjoint, density-preserving | by id, by relationship (all fields) |
| Luxar ([format contract](https://github.com/royerlab/luxar/tree/main/format-contract)) | chunk bounds | Hilbert order | disjoint, additive | none |
| zarr-vectors ([docs](https://zarr-vectors-py.readthedocs.io/)) | chunks + bins | row ranges per bin (fragments) | centroid pyramid | one attribute as chunk key |
| cLoD ([van Oosterom et al., 2022](#references)) | Morton key over (x, y, cLoD) | B+-tree (database) | continuous, random per point, each point once | none |

Considered and not chosen:

- Image-pixel grid: SpatialData has no pixel space, and points can exist without an image.
- The [zarr-conventions `multiscales`](https://github.com/zarr-conventions/multiscales) convention
  for the levels: it adds a dependency on an external convention without adding information. Its
  per-level transformations would be the same for every grid: the scale is not used, and its
  translation is the `origin` of each level, which is more explicit and fits the scope of this
  specification.
- Zarr, a sparse tensor in which each entry is a point: it comes with other compromises and is left
  for possible future exploration.
- Row groups by formula only, with one row group per tile, empty tiles included, as in Celldega: the
  row counts in the Parquet footers are then the tile offsets, and no offsets need to be stored.
  But it ties the index to Parquet, each row group adds to the footer, which is read whole on every
  open, and does not scale to grids of $10^5$–$10^6$ tiles per band or to the feature-major table
  (one row group per feature, band and tile); a large tile cannot be split either.
- The offsets of the Parquet format in the Parquet key-value metadata: they would be strings
  (e.g. base64) in the footer, read and decoded whole on every open, without random access, one
  footer per file of a multi-file dataset.
- The offsets of the Parquet format in a sidecar Parquet table: possible, with random access through
  the page index, but coarser and less uniformly supported by readers than Zarr chunks, and a
  second index format next to the Zarr one.
- Tile-relative float32 or uint16 coordinates: can come later as a codec without changing the type.
- Zarr, one 2-D array with the columns first, chunked by tile: a chunk would hold the columns of a
  tile column by column, as a Parquet row group, in one request. But a Zarr array has a single data
  type, and such an array is not a dataframe; the `df:` convention is used instead.
- zarr-vectors (v0.9, under active development) for points. Its model groups the points of a chunk
  into bins and indexes each bin by a row range, close to the tile index here, and supports 3-D and
  per-axis chunk sizes. What it lacks for this use case:
  - sampled levels of the original points: its point-cloud pyramid replaces the points of a bin by
    their centroid, and its core does not aggregate the attributes (gene, other columns) of the
    merged points; point thinning exists only in a separate tools package;
  - a priority per point, or any order inside a bin that supports progressive loading;
  - a second, feature-major order next to the spatial one: attribute chunking makes one attribute
    (e.g. the gene) part of the chunk key instead, with one key prefix per distinct value (thousands
    for genes) and a rechunk to add values;
  - Parquet, which SpatialData uses for points today, and a plain dataframe: the vertices of a chunk
    are stored as ragged arrays, not as `df:` columns;
  - a Zarr convention: its metadata is a set of top-level attributes with its own version. This
    specification is meant to be a self-contained Zarr convention, usable on its own or next to other
    conventions (see [Storage format](#storage-format)).
- One table per level, each holding again the points of the coarser levels (Neuroglancer stores each
  point once; merfisheyes and spatiato repeat them): no bands to combine, but up to 1.33× the points
  in 2-D, and switching to a finer level reads the points already shown again.
- $p$ computed from a hash of the point id when reading, instead of stored: reproducible without
  storing $p$, but ties the levels to the id and to the hash function; storing $p$ is simpler and
  costs 4 bytes per point. A writer may still derive the stored $p$ from a hash (see
  [Priority](#priority)).
- A fraction per feature in the feature-major order (each feature sampled on its own): shows rare
  features at coarse levels, but distorts relative abundance when several features are shown
  together and needs a correction in the client. With one $p$, a client shows a rare feature
  completely by reading its finer levels from the feature-major table (see
  [Choosing the tile size and the rates](#choosing-the-tile-size-and-the-rates)).

## Implementation

> **TODO:** spatialdata (read/write), spatialdata-io (Celldega PR #423), tissue-map-tools (sampling),
> a viewer (Celldega, Vitessce, TissUUmaps, merfisheyes, spatiato).

## Discussion

- [Original proposal by Celldega](https://github.com/scverse/spatialdata/discussions/1251), September 2026.
- [Options and proposal (Google Doc)](https://docs.google.com/document/d/1-lX85Qzm88qIprGJIW_IjUoi8LrCTZC8XXF22RZjqDk/edit)
- Open: the TODO notes above; where CSR/CSC belongs (separate spec, Ilan).

## References

- [RFC 4: Tiled and multiscale shapes](0004-tiled-shapes.md)
- P. van Oosterom, S. van Oosterom, H. Liu, R. Thompson, M. Meijers, E. Verbree, "Organizing and
  visualizing point clouds with continuous levels of detail", *ISPRS Journal of Photogrammetry and
  Remote Sensing* 194 (2022) 119–131, [doi:10.1016/j.isprsjprs.2022.10.004](https://doi.org/10.1016/j.isprsjprs.2022.10.004)
  ([PDF](https://www.gdmc.nl/publications/2022/cLoD_ISPRS_Journal.pdf), open access, CC BY 4.0).
  The cLoD value of a point is drawn from a continuous distribution through a uniform random number,
  $l = F^{-1}(U)$; it is a monotone function of $U$, so thresholds on the cLoD value are thresholds
  on a uniform priority, as here. The paper declares no patent and no competing interests.
- M. Schütz, K. Krösl, M. Wimmer, "Real-Time Continuous Level of Detail Rendering of Point Clouds",
  IEEE VR 2019 ([page](https://cg.tuwien.ac.at/research/publications/2019/schuetz-2019-CLOD)): a
  fixed uniform random value per point, to avoid flicker.
