# Elements

For each element type: the Python object, what a valid instance looks like, and how to build one.
"Valid" means `Model.validate()` passes. Unless stated otherwise, everything below is checked by
validation.

## Images and labels (raster)

A raster element is an `xarray.DataArray` (single scale) or an `xarray.DataTree` (multiscale).

::::{tab-set}
:::{tab-item} DataArray (single scale)
:sync: single

```python
<xarray.DataArray 'image' (c: 2, y: 4, x: 6)>
dask.array<shape=(2, 4, 6), dtype=uint8, chunksize=(2, 4, 6)>
Coordinates:
  * c        (c) <U4 'DAPI' 'CD3'
  * y        (y) float64 0.5 1.5 2.5 3.5
  * x        (x) float64 0.5 1.5 2.5 3.5 4.5 5.5
Attributes:
    transform:  {'global': Identity}
```

- `dims` **MUST** be exactly `("c", "y", "x")` or `("c", "z", "y", "x")` for images, `("y", "x")`
  or `("z", "y", "x")` for labels. Order matters.
- `.data` **MUST** be a `dask.array.Array`. NumPy input is wrapped by `parse()`.
- Labels **MUST** have an integer or boolean dtype; `0` is background. Images accept any numeric
  dtype.
- `attrs["transform"]` **MUST** be a non-empty `dict[str, BaseTransformation]` keyed by coordinate
  system name ({doc}`transformations`).
- `coords["c"]` holds the channel names (any hashable values; default `0 … n-1`). Read them with
  `get_channel_names()`, change them with `set_channel_names()`.
- `coords["x"]`, `coords["y"]`, `coords["z"]` are pixel centres `i + 0.5` in intrinsic units. They
  are derived, recomputed by `parse()`, and **not** a substitute for the transformation.
- `.name` is `"image"` after parsing; it carries no meaning and **MUST NOT** be relied upon.
:::

:::{tab-item} DataTree (multiscale)
:sync: multi

```text
<xarray.DataTree>
Group: /
├── /scale0   image (c, y, x) uint8 (2, 8, 8)   transform = {'global': T}
├── /scale1   image (c, y, x) uint8 (2, 4, 4)   transform = {'global': Sequence[Scale(2, 2), T]}
└── /scale2   image (c, y, x) uint8 (2, 2, 2)   transform = {'global': Sequence[Scale(4, 4), T]}
```

- Children **MUST** be named `scale0`, `scale1`, … in order of decreasing resolution; `scale0` is
  full resolution.
- Each child **MUST** contain exactly one data variable, and the variable name **MUST** be the same
  in every child. The name is arbitrary and code **MUST NOT** depend on it; `spatialdata` uses
  `"image"` and one **MAY** do the same.
- Each variable satisfies the single-scale rules above (dims, Dask backing, dtype, coords).
- The tree's own `attrs` **MUST NOT** contain `"transform"`. Transformations live on the
  per-level variables. Level `0` holds the element's transformations; level `i` holds, for each
  coordinate system, `Sequence([Scale(level_i → level_0), T])`, so that any level maps directly
  into the named coordinate system. `get_transformation(tree)` returns the level-`0` mapping.
- The channel axis is never downsampled.
:::
::::

Building one:

```python
from spatialdata.models import Image2DModel, Labels2DModel

img = Image2DModel.parse(
    array,
    dims=("c", "y", "x"),
    c_coords=["DAPI", "CD3"],
    scale_factors=[2, 2],
    chunks=(1, 1024, 1024),
    transformations={"global": Identity()},
)
lab = Labels2DModel.parse(mask)  # dims default to ("y", "x"); Identity to "global"
```

`parse()` accepts `numpy.ndarray`, `dask.array.Array` or `xarray.DataArray`, transposes to the
model's dims when `dims` is given in another order, wraps NumPy in Dask, and returns a `DataTree`
when `scale_factors` is given (each factor halves, or scales, the spatial axes of the previous
level; `c` is untouched).

## Shapes

A shapes element is a `geopandas.GeoDataFrame`.

```text
            geometry  radius   cell_type      # geometry: GeoSeries; extra columns allowed
n_01  POINT (10 12)     4.5   T cell
n_02  POINT (33 40)     5.0   B cell
attrs = {'transform': {'global': Identity}}
```

- Column `geometry` **MUST** be present and be a `GeoSeries` with at least one row.
- Geometries **MUST** be 2D and of type `Point` (circles) or `Polygon` / `MultiPolygon`. Points and
  polygons **MUST NOT** be mixed. Validation checks the first geometry; call
  `ShapesModel.validate_shapes_not_mixed_types()` for a full check.
- When geometries are points, column `radius` **MUST** be present with finite, strictly positive
  values (in intrinsic units).
- The index holds the {term}`instance` identifiers; values **MUST** be unique and **MAY** be
  integers or strings.
- `attrs["transform"]` **MUST** be a non-empty `dict[str, BaseTransformation]`.
- `crs` is `None`; other columns are free per-instance annotations.

Build from a `GeoDataFrame` (`ShapesModel.parse(gdf)`), from a GeoJSON file path, or from shapely
ragged arrays (`ShapesModel.parse(coords, geometry=..., offsets=..., radius=...)`). Shapes are
loaded eagerly; there is no lazy `GeoDataFrame`.

## Points

A points element is a `dask.dataframe.DataFrame`.

```text
     x      y  gene   cell        # x, y[, z] numeric; extra columns allowed
0  46.0  395.0  ACTB     9
1 334.0  224.0  GAPDH    7
attrs = {'transform': {'global': Identity},
         'spatialdata_attrs': {'feature_key': 'gene', 'instance_key': 'cell'}}
```

- Columns `x`, `y` **MUST** be present, `z` **MAY** be; each **MUST** have dtype `int32`, `int64`,
  `float32` or `float64`.
- `attrs["transform"]` **MUST** be a non-empty `dict[str, BaseTransformation]`.
- `attrs["spatialdata_attrs"]` **MAY** be present with `feature_key` and/or `instance_key`, each
  naming an existing column. The `feature_key` column **SHOULD** be categorical with known
  categories (unknown categories force a full pass over the data).
- Other columns are free per-point annotations. Column order is not guaranteed by `parse()`.

`dask.dataframe.DataFrame` has no native `attrs`; `spatialdata` registers an accessor that provides
one and preserves it across common operations (`assign`, `map_partitions`, `set_index`, …).
Operations that create a new frame without going through that accessor **MAY** drop `attrs`.

Build with `PointsModel.parse(df, coordinates={"x": "x_um", "y": "y_um"}, feature_key="gene")` from a
pandas or Dask frame, or `PointsModel.parse(array, annotation=df)` from an `(n, 2 | 3)` array. Data
is one partition unless `npartitions` or `chunksize` is passed. Reading from disk yields one
partition per Parquet part.

## Tables

A table is an `anndata.AnnData`.

```text
AnnData n_obs × n_vars
    obs: 'region' (category), 'instance_id' (int64), ...
    uns: 'spatialdata_attrs' = {'region': ['cells', 'nuclei'], 'region_key': 'region', 'instance_key': 'instance_id'}
```

- `uns["spatialdata_attrs"]` **MAY** be absent: the table then annotates nothing. When present it
  **MUST** contain all of `region` (`str | list[str]`), `region_key` (`str`), `instance_key` (`str`).
- `obs[region_key]` **MUST** exist and be categorical; every value **MUST** be in `region`.
- `obs[instance_key]` **MUST** exist and contain no nulls; `(region, instance)` pairs **MUST** be
  unique. Its dtype **SHOULD** match the annotated element's instance identifiers (integer for
  labels, the index dtype for shapes and points); a string/non-string mismatch raises when the
  table is added to a `SpatialData`.
- `obs`/`var` column names and `obsm`/`obsp`/`varm`/`varp`/`uns`/`layers` keys **MUST** follow
  the element naming rules; `_index` is reserved.
- Tables **MUST NOT** carry `attrs["transform"]` and cannot be annotated by other tables.

Build with `TableModel.parse(adata, region=["cells"], region_key="region", instance_key="instance_id")`.
Re-target an existing table with `sdata.set_table_annotates_spatialelement(...)`; read the keys with
`get_table_keys(adata)`.

:::{admonition} Implementation note
:class: implementation-note

The instance identifiers of an element are returned by `spatialdata.get_element_instances(element)`:
unique non-zero label values for labels, the index for shapes and points. Matching them against
`obs[instance_key]` is what every element ↔ table join does; the helpers in
{doc}`implementation-guide` wrap this.
:::
