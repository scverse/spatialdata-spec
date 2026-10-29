(python)=
# SpatialData Python in-memory format

:::{include} data-model.md
:start-after: % begin spec-intro
:end-before: % end spec-intro
:::

This page specifies the Python in-memory format: how the Python implementation,
[`spatialdata`](https://github.com/scverse/spatialdata), represents a dataset of the
{doc}`abstract data model <data-model>` after reading a store or building it in code. Each section
repeats a part of the data model, in plain language, and then specifies the Python objects that
represent it: their dimensions, columns and attributes, and the invariants that hold once they pass
validation. A tool that follows it can consume and produce SpatialData objects without depending on
`spatialdata` internals; the {doc}`implementation guide <in-memory-python-guide>` collects common
recipes.

This version describes `spatialdata` 0.8 and represents version 1.0 of the abstract data model.
Changes are discussed in [scverse/spatialdata](https://github.com/scverse/spatialdata/issues) and
written down here after release.

(python-reading-this-specification)=
## Reading this specification

- The key words MUST, MUST NOT, SHOULD, SHOULD NOT and MAY are to be
  interpreted as described in [RFC 2119](https://www.rfc-editor.org/rfc/rfc2119). Key words have
  this meaning only in capitals ([RFC 8174](https://www.rfc-editor.org/rfc/rfc8174)).
- The parts taken from the data model are normative for every implementation. The Python parts add
  the requirements for representing them in Python.
- "Valid" means that `Model.validate()` passes (see {ref}`python-models`). Validation checks every
  requirement unless the text says otherwise.
- Boxes labelled *Implementation note* are not normative.

(python-objects)=
## Python objects

Every element is a standard scientific-Python object, not a subclass: a `spatialdata` image *is* an
`xarray.DataArray`. The SpatialData metadata (transformations, table keys) lives in the object's
`attrs` or, for tables, `uns`.

| Element | Python type | Model class(es) | SpatialData metadata |
|---------|-------------|-----------------|----------------------|
| images | `xarray.DataArray` or `xarray.DataTree` | `Image2DModel`, `Image3DModel` | `attrs["transform"]` |
| labels | `xarray.DataArray` or `xarray.DataTree` | `Labels2DModel`, `Labels3DModel` | `attrs["transform"]` |
| points | `dask.dataframe.DataFrame` | `PointsModel` | `attrs["transform"]`, `attrs["spatialdata_attrs"]` |
| shapes | `geopandas.GeoDataFrame` | `ShapesModel` | `attrs["transform"]` |
| tables | `anndata.AnnData` | `TableModel` | `uns["spatialdata_attrs"]` |

(python-models)=
### Models: parse and validate

A *model* is the class that constructs and checks one element type, for example `Image2DModel`. It
is not the type of the element: `Image2DModel.parse()` returns an `xarray.DataArray` or an
`xarray.DataTree`. Each model has two class methods:

`Model.parse(data, ...)`
: Builds a valid element from raw inputs (NumPy or Dask arrays, pandas or GeoPandas data frames,
  AnnData) and returns the standard object. Parsing transposes dimensions, wraps arrays in Dask,
  attaches channel names, builds pyramids, sets an `Identity` transformation to `"global"` when
  none is given, and finally validates.

`Model.validate(element)`
: Checks an existing object against the model and raises `ValueError` with the reason. It never
  modifies the object.

`spatialdata.models.get_model(element)` returns the model of an element and validates the element
on the way (`validate=False` skips this). For raster elements the model follows from the dims: a
`c` axis means image, a `z` axis means 3D.

The Python format has been stable since `spatialdata` 0.1, which replaced the earlier `SpatialImage`
and `MultiscaleSpatialImage` subclasses with plain `xarray.DataArray` and `xarray.DataTree` objects
and allowed several tables.

(python-datasets)=
## Datasets and elements

:::{include} data-model.md
:start-after: % begin spec-datasets
:end-before: % end spec-datasets
:::

(python-datasets-spatialdata-object)=
### The SpatialData object

A dataset is a `spatialdata.SpatialData` object: five typed containers of named elements, plus
user metadata.

```python
from spatialdata import SpatialData

sdata = SpatialData(
    images={"he": image},  # dict[str, DataArray | DataTree]
    labels={"cells": labels},  # dict[str, DataArray | DataTree]
    points={"transcripts": ddf},  # dict[str, dask.dataframe.DataFrame]
    shapes={"nuclei": gdf},  # dict[str, GeoDataFrame]
    tables={"table": adata},  # dict[str, AnnData]
    attrs={"sample": "S1"},  # JSON-serialisable mapping
)
```

- `sdata.images`, `sdata.labels`, `sdata.points`, `sdata.shapes` and `sdata.tables` are dict-like
  and keyed by element name. Assigning into one of them validates the value with the matching model
  and raises otherwise, also when the value is a valid element of another type.
- Element names follow the naming rules of the storage format: not empty, `.` or `..`; only
  letters, digits, `-`, `_` and `.`; not starting with `__`; unique across all element types, also
  when compared case-insensitively. `spatialdata` checks the characters and rejects a name used by
  two elements. It does not reject two names that differ only in case when they belong to
  different element types; code that writes stores SHOULD check this itself.
- Because names are unique, `sdata["name"]`, `"name" in sdata`, `sdata.get("name")` and
  `del sdata["name"]` work without stating the type; `sdata["name"] = element` dispatches on the
  element's model.
- **The element name is not stored in the element.** An `xarray.DataArray` does not know that it is
  called `"he"`. `sdata.locate_element(element)` returns the `type/name` path(s) of an object.
- `sdata.attrs` is a `dict` of user metadata and round-trips to the root group attributes. The key
  `spatialdata_attrs` is reserved.
- `sdata.path` is the store the object was read from or last written to, else `None`. Dask-backed
  elements load lazily from it.

Introspection: `sdata.coordinate_systems` (names of the coordinate systems of all elements),
`sdata.gen_elements()` (yields `(element_type, name, element)`, including tables),
`sdata.gen_spatial_elements()` (without tables) and `sdata.elements_paths_in_memory()`.

(python-spatial-elements)=
## Spatial elements

:::{include} data-model.md
:start-after: % begin spec-spatial-elements
:end-before: % end spec-spatial-elements
:::

(python-spatial-elements-axes)=
### Axes

The four spatial types are exported together as `spatialdata.models.SpatialElement`
(`DataArray | DataTree | GeoDataFrame | DaskDataFrame`); tables are not part of it.

Axes are the xarray dims of raster elements, in the order `c`, `z`, `y`, `x`, and the coordinate
columns of points and shapes. A `DataArray` alone does not say whether it is an image or labels;
code SHOULD dispatch on `get_model()` rather than on the Python type.

(python-images)=
### Images

:::{include} data-model.md
:start-after: % begin spec-images
:end-before: % end spec-images
:::

An image is an `xarray.DataArray` (single scale) or an `xarray.DataTree` (multiscale).

(python-images-single-scale)=
#### Single scale

```text
<xarray.DataArray 'image' (c: 2, y: 4, x: 6)>
dask.array<shape=(2, 4, 6), dtype=uint8, chunksize=(2, 4, 6)>
Coordinates:
  * c        (c) <U4 'DAPI' 'CD3'
  * y        (y) float64 0.5 1.5 2.5 3.5
  * x        (x) float64 0.5 1.5 2.5 3.5 4.5 5.5
Attributes:
    transform:  {'global': Identity}
```

- `dims` MUST be exactly `("c", "y", "x")` or `("c", "z", "y", "x")`, in this order.
- `.data` MUST be a `dask.array.Array`; `parse()` wraps NumPy input.
- Any numeric dtype is allowed.
- `attrs["transform"]` MUST be a non-empty `dict[str, BaseTransformation]`, keyed by coordinate
  system name (see {ref}`python-coordinate-systems`).
- `coords["c"]` holds the channel names (any hashable values; by default `0 … n-1`). Read them with
  `get_channel_names()` and change them with `set_channel_names()`.
- `coords["x"]`, `coords["y"]` and `coords["z"]` are the pixel centres `i + 0.5` in intrinsic
  units. They are derived, recomputed by `parse()`, and no substitute for the transformation.
- `.name` is `"image"` after parsing; it carries no meaning and code MUST NOT rely on it.

(python-images-multiscale)=
#### Multiscale

```text
<xarray.DataTree>
Group: /
├── /scale0   image (c, y, x) uint8 (2, 8, 8)   transform = {'global': T}
├── /scale1   image (c, y, x) uint8 (2, 4, 4)   transform = {'global': Sequence[Scale(2, 2), T]}
└── /scale2   image (c, y, x) uint8 (2, 2, 2)   transform = {'global': Sequence[Scale(4, 4), T]}
```

- Children MUST be named `scale0`, `scale1`, … in order of decreasing resolution; `scale0` is the
  full resolution.
- Each child MUST contain exactly one data variable, with the same name in every child. The name
  is arbitrary and code MUST NOT depend on it; `spatialdata` uses `"image"`.
- Each variable satisfies the single-scale rules.
- The tree's own `attrs` MUST NOT contain `"transform"`. Level `0` holds the element's
  transformations; level `i` holds, for each coordinate system,
  `Sequence([Scale(level i → level 0), T])`, so that every level maps directly into the
  coordinate system. `get_transformation(tree)` returns the transformations of level `0`.
- The channel axis is never downsampled.

(python-images-building)=
#### Building an image

```python
from spatialdata.models import Image2DModel
from spatialdata.transformations import Identity

img = Image2DModel.parse(
    array,
    dims=("c", "y", "x"),
    c_coords=["DAPI", "CD3"],
    scale_factors=[2, 2],
    chunks=(1, 1024, 1024),
    transformations={"global": Identity()},
)
```

`parse()` accepts a `numpy.ndarray`, a `dask.array.Array` or an `xarray.DataArray`, transposes to
the model's dims when `dims` names them in another order, and returns a `DataTree` when
`scale_factors` is given; each factor downsamples the spatial axes of the previous level.

(python-labels)=
### Labels

:::{include} data-model.md
:start-after: % begin spec-labels
:end-before: % end spec-labels
:::

Labels are represented like {ref}`images <python-images>`, single scale or multiscale, with these
differences:

- `dims` MUST be exactly `("y", "x")` or `("z", "y", "x")`; there is no `c` axis.
- The dtype MUST be an integer type. `spatialdata` also accepts a boolean dtype.

```python
from spatialdata.models import Labels2DModel

lab = Labels2DModel.parse(mask)  # dims ("y", "x"); Identity to "global"
```

(python-points)=
### Points

:::{include} data-model.md
:start-after: % begin spec-points
:end-before: % end spec-points
:::

Points are a `dask.dataframe.DataFrame`.

```text
     x      y  gene   cell        # x, y[, z] numeric; extra columns allowed
0  46.0  395.0  ACTB     9
1 334.0  224.0  GAPDH    7
attrs = {'transform': {'global': Identity},
         'spatialdata_attrs': {'feature_key': 'gene', 'instance_key': 'cell'}}
```

- Columns `x` and `y` MUST be present and `z` MAY be; each MUST have the dtype `int32`, `int64`,
  `float32` or `float64`.
- The index holds the point identifiers.
- `attrs["transform"]` MUST be a non-empty `dict[str, BaseTransformation]`.
- `attrs["spatialdata_attrs"]` MAY hold `feature_key` and `instance_key`, each naming an existing
  column. `parse()` makes the `feature_key` column categorical; it SHOULD have known categories, as
  unknown categories force a full pass over the data.
- Other columns are free per-point annotations. `parse()` does not guarantee the column order.

Dask data frames have no `attrs` of their own. `spatialdata` registers an `attrs` accessor and keeps
it through `__getitem__`, `copy`, `drop`, `map_partitions`, `sample`, `set_index`, `compute`, `.loc`
and `.iloc`. Other operations, `assign` among them, return a data frame with empty `attrs`; code
MUST set the transformations again before adding such a data frame to a dataset.

Build with `PointsModel.parse(df, coordinates={"x": "x_um", "y": "y_um"}, feature_key="gene")` from
a pandas or Dask data frame, or with `PointsModel.parse(array, annotation=df)` from an `(n, 2)` or
`(n, 3)` array. The data is one partition unless `npartitions` or `chunksize` is passed; reading a
store gives one partition per Parquet part.

(python-shapes)=
### Shapes

:::{include} data-model.md
:start-after: % begin spec-shapes
:end-before: % end spec-shapes
:::

Shapes are a `geopandas.GeoDataFrame`.

```text
            geometry  radius   cell_type      # geometry: GeoSeries; extra columns allowed
n_01  POINT (10 12)     4.5   T cell
n_02  POINT (33 40)     5.0   B cell
attrs = {'transform': {'global': Identity}}
```

- The column `geometry` MUST be a `GeoSeries` with at least one row.
- Geometries MUST be either all `Point` (circles) or all `Polygon` or `MultiPolygon`. Validation
  checks only the first geometry; `ShapesModel.validate_shapes_not_mixed_types()` checks all of
  them.
- Geometries MUST be 2D. `spatialdata` accepts geometries with z coordinates with a warning.
- For circles, the column `radius` MUST be present, with finite, strictly positive values in
  intrinsic units.
- The index holds the instance identifiers, integers or strings. They MUST be unique; validation
  does not check this.
- `attrs["transform"]` MUST be a non-empty `dict[str, BaseTransformation]`.
- `crs` is `None`. Other columns are free per-instance annotations.

Build from a `GeoDataFrame` (`ShapesModel.parse(gdf)`), from a GeoJSON file, or from shapely ragged
arrays (`ShapesModel.parse(coords, geometry=..., offsets=..., radius=...)`). Shapes are loaded
eagerly.

(python-coordinate-systems)=
## Coordinate systems and transformations

:::{include} data-model.md
:start-after: % begin spec-coordinate-systems
:end-before: % end spec-coordinate-systems
:::

A transformation is an instance of a `spatialdata.transformations` class. Unlike the stored
encoding, it carries no coordinate system objects: it is self-contained and applies to any element
whose axes it mentions.

(python-coordinate-systems-classes)=
### Classes

| Class | Constructor | Notes |
|-------|-------------|-------|
| `Identity` | `Identity()` | |
| `Scale` | `Scale([sy, sx], axes=("y", "x"))` | one factor per listed axis |
| `Translation` | `Translation([ty, tx], axes=("y", "x"))` | |
| `Affine` | `Affine(matrix, input_axes=("x", "y"), output_axes=("x", "y"))` | homogeneous `(n_out + 1) × (n_in + 1)` matrix |
| `MapAxis` | `MapAxis({"x": "y", "y": "x"})` | output axis → input axis; renames, permutes or duplicates axes |
| `Sequence` | `Sequence([t1, t2, ...])` | applied left to right |

All inherit from `BaseTransformation` and provide `to_affine_matrix(input_axes, output_axes)` and
`inverse()`. Elements are transformed with `spatialdata.transform(element, to_coordinate_system=...)`.

(python-coordinate-systems-axes)=
### Axes

When a transformation is applied to an element:

- element axes that the transformation does not mention pass through unchanged (for example `c`
  under a `Scale` on `y`, `x`);
- transformation axes that the element does not have are ignored (a `Scale` on `z`, `y`, `x`
  applied to a 2D element drops `z`);
- a transformation that produces an axis the element does not have, and that cannot pass through,
  raises.

The stored form spells out every axis of the element; writing expands the transformation to them.

(python-coordinate-systems-where)=
### Where transformations live

Every spatial element has `attrs["transform"]`, a `dict[str, BaseTransformation]` from coordinate
system name to the transformation from the element's intrinsic coordinates into that system. Code
SHOULD use the functions below rather than the dict, so that Dask accessors, multiscale levels and
the backing store stay consistent:

```python
from spatialdata.transformations import (
    get_transformation,
    get_transformation_between_coordinate_systems,
    remove_transformation,
    set_transformation,
)

t = get_transformation(element)  # to "global"
t = get_transformation(element, "micron")
all_t = get_transformation(element, get_all=True)  # dict

set_transformation(element, Scale([0.5, 0.5], axes=("y", "x")), "micron")
set_transformation(element, {"global": Identity(), "micron": t}, set_all=True)
set_transformation(element, t, "micron", write_to_sdata=sdata)  # also update the store
remove_transformation(element, "micron")

t_ab = get_transformation_between_coordinate_systems(sdata, source, target)
```

`get_transformation_between_coordinate_systems` treats elements and coordinate systems as nodes of
a graph and composes, and inverts, the transformations along the path between two nodes; it raises
when the path is not unique.

Multiscale rasters store a transformation per level (see {ref}`python-images-multiscale`).
`spatialdata.transform(..., maintain_positioning=True)` keeps the element in place and changes its
transformations; the default resamples raster data into the target system.

(python-coordinate-systems-storage)=
### Mapping to the storage format

| Python | Stored `type` |
|--------|---------------|
| `Identity` | `identity` |
| `Scale` | `scale` |
| `Translation` | `translation` |
| `Affine` | `affine` |
| `MapAxis` | `mapAxis` |
| `Sequence` | `sequence` |

Writing calls `BaseTransformation.to_ngff(input_axes, output_axes, unit, output_coordinate_system_name)`
to produce the stored object with its coordinate systems; reading drops the coordinate system
objects and keeps the name of the output coordinate system as the dict key. Reading an element with
another stored type (`rotation`, `byDimension`, and the other types of NGFF RFC-5) raises.

(python-instances)=
## Instances and identifiers

:::{include} data-model.md
:start-after: % begin spec-instances
:end-before: % end spec-instances
:::

`spatialdata.get_element_instances(element)` returns the instance identifiers of an element: the
unique nonzero values of labels, the index of points and shapes. Every element–table join matches
them against `obs[instance_key]`; the {doc}`implementation guide <in-memory-python-guide>` shows the
helpers that do this.

(python-tables)=
## Annotation tables

:::{include} data-model.md
:start-after: % begin spec-tables
:end-before: % end spec-tables
:::

A table is an `anndata.AnnData`.

```text
AnnData n_obs × n_vars
    obs: 'region' (category), 'instance_id' (int64), ...
    uns: 'spatialdata_attrs' = {'region': ['cells', 'nuclei'], 'region_key': 'region', 'instance_key': 'instance_id'}
```

- `uns["spatialdata_attrs"]` MAY be absent; the table then annotates nothing. When present, it
  MUST contain `region` (`str` or `list[str]`), `region_key` (`str`) and `instance_key` (`str`).
- `obs[region_key]` MUST be categorical, and its values MUST match `region`.
- `obs[instance_key]` MUST NOT contain nulls, and each `(region, instance)` pair MUST be unique.
- The dtype of `obs[instance_key]` SHOULD match the instance identifiers of the annotated element:
  integers for labels, the index dtype for points and shapes. A string versus non-string mismatch
  raises when the table is added to a `SpatialData`.
- Column names of `obs` and `var` and keys of `obsm`, `obsp`, `varm`, `varp`, `uns` and `layers`
  MUST follow the element naming rules (see {ref}`python-datasets-spatialdata-object`); `_index`
  is reserved.
- Tables have no transformations and cannot annotate other tables.

Build with `TableModel.parse(adata, region=["cells"], region_key="region", instance_key="instance_id")`.
Re-target an existing table with `sdata.set_table_annotates_spatialelement(...)` and read the keys
with `get_table_keys(adata)`.

## Notes

% the footnotes are rendered here, at the end of the page

```{toctree}
:hidden: true

Implementation guide <in-memory-python-guide>
```
