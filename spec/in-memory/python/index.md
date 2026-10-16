# In-memory format (Python)

{bdg-success}`in-memory · Python` {bdg-dark-line}`status quo` {bdg-light}`spatialdata 0.8` {bdg-light}`xarray · dask · geopandas · anndata`

This page documents the model as implemented; it is not a proposal. Changes to the Python model are
discussed in [scverse/spatialdata](https://github.com/scverse/spatialdata/issues) and reflected here
once released. Topics that concern every implementation go to {doc}`../index`.

This section specifies the data model that the `spatialdata` Python package exposes: which Python
objects represent each {term}`element`, which dimensions, columns and attributes they carry, and
which invariants hold for an element that passes validation. It is what a Python tool needs to know
to consume or produce SpatialData objects without depending on `spatialdata` internals.

The in-memory model is a faithful image of the {doc}`on-disk format <../../on-disk/index>`:
every element on disk becomes one standard scientific-Python object in memory, and the SpatialData
metadata (transformations, table keys) lives in that object's `attrs` or `uns`. Elements are
**not** subclasses; a `spatialdata` image *is* an `xarray.DataArray`.

## Elements at a glance

| Element | Python type | Model class(es) | Shape | SpatialData metadata |
|---------|-------------|-----------------|-------|----------------------|
| image | `xarray.DataArray` or `xarray.DataTree` | `Image2DModel`, `Image3DModel` | dims `(c, y, x)` / `(c, z, y, x)` | `attrs["transform"]` |
| labels | `xarray.DataArray` or `xarray.DataTree` | `Labels2DModel`, `Labels3DModel` | dims `(y, x)` / `(z, y, x)` | `attrs["transform"]` |
| shapes | `geopandas.GeoDataFrame` | `ShapesModel` | one row per instance; `geometry` [, `radius`] | `attrs["transform"]` |
| points | `dask.dataframe.DataFrame` | `PointsModel` | one row per point; `x`, `y` [, `z`] | `attrs["transform"]`, `attrs["spatialdata_attrs"]` |
| table | `anndata.AnnData` | `TableModel` | obs × var | `uns["spatialdata_attrs"]` |

The union of the four spatial types is exported as `spatialdata.models.SpatialElement`. Details per
type are in {doc}`elements`; the transformation objects in {doc}`transformations`.

## The `SpatialData` object

`spatialdata.SpatialData` is the in-memory counterpart of a {term}`store`: a container of named
elements plus free-form metadata.

```python
from spatialdata import SpatialData

sdata = SpatialData(
    images={"he": image},  # dict[str, DataArray | DataTree]
    labels={"cells": labels},  # dict[str, DataArray | DataTree]
    shapes={"nuclei": gdf},  # dict[str, GeoDataFrame]
    points={"transcripts": ddf},  # dict[str, dask.dataframe.DataFrame]
    tables={"table": adata},  # dict[str, AnnData]
    attrs={"sample": "S1"},  # any JSON-serialisable mapping
)
```

Invariants that hold for every `SpatialData` object:

- **Five typed containers.** `sdata.images`, `sdata.labels`, `sdata.shapes`, `sdata.points`,
  `sdata.tables` are dict-like, keyed by element name. Assigning into one of them validates the
  value with the matching model and raises otherwise.
- **Names are unique across types.** The same rules as on disk apply: allowed characters, no
  leading `__`, and case-insensitive uniqueness across all five containers. `sdata["name"]`,
  `"name" in sdata`, `sdata.get("name")` and `del sdata["name"]` therefore work without stating the
  type; `sdata["name"] = element` dispatches on the element's model.
- **Element names are not stored in the element.** An `xarray.DataArray` does not know it is called
  `"he"`. Use `sdata.locate_element(element)` to find the `type/name` path(s) of an object.
- **Elements are valid.** Every element satisfies its model's `validate()`; in particular every
  spatial element has at least one coordinate transformation.
- **Tables reference elements by name.** A table with `uns["spatialdata_attrs"]` annotates the
  elements named in `region`; those names are expected to exist in the same object when the table
  is added, and a mismatch raises.
- **`attrs`** is a plain `dict` of user metadata and round-trips to the root group attributes on
  disk. `spatialdata_attrs` is reserved.
- **`path`** is the path of the backing store when the object was read from disk or written, else
  `None`. Dask-backed elements load lazily from that store.

Useful introspection: `sdata.coordinate_systems` (names of all coordinate systems referenced by any
element), `sdata.gen_elements()` (yields `(element_type, name, element)` including tables),
`sdata.gen_spatial_elements()` (excludes tables), `sdata.elements_paths_in_memory()`.

## Models: parse and validate

Each model class has two class methods:

`Model.parse(data, ...)`
: Builds a valid element from raw inputs (NumPy/Dask arrays, pandas or GeoPandas frames, AnnData)
  and returns the standard object. Parsing transposes dimensions, converts arrays to Dask, attaches
  channel names, builds pyramids, sets a default `Identity` transformation to `"global"` when none is
  given, and finally validates.

`Model.validate(element)`
: Checks an existing object against the model and raises `ValueError` with the reason. It never
  modifies the object.

`spatialdata.models.get_model(element)` returns the model class that describes an element,
validating it on the way (pass `validate=False` to skip). For raster elements the model is derived
from the dims: a `c` axis means image, a `z` axis means 3D. This is the entry point for writing
generic code; see {doc}`implementation-guide`.

## Versioning of the in-memory model

The model described here has been stable since `spatialdata` 0.1 (plain `xarray.DataArray` /
`xarray.DataTree` instead of the earlier `SpatialImage` / `MultiscaleSpatialImage` subclasses,
multiple tables). Changes to the model follow the `spatialdata` release notes; this page tracks
release 0.8.

```{toctree}
:maxdepth: 1
:hidden:

elements
transformations
implementation-guide
```
