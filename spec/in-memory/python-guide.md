# Python implementation guide

Nothing on this page is normative. It is the shortest path to code that works on any valid
`SpatialData` object, and complements the Python tabs of the {ref}`specification <python-intro>`.
Every snippet uses only the public `spatialdata` API (release 0.8).

## Dispatch on the element type

Do not test Python types directly: a `DataArray` can be an image or labels. Ask the model:

```python
from spatialdata.models import (
    Image2DModel,
    Image3DModel,
    Labels2DModel,
    Labels3DModel,
    PointsModel,
    ShapesModel,
    TableModel,
    get_model,
)


def process(element):
    model = get_model(element)  # validates; validate=False skips this
    if model in (Image2DModel, Image3DModel):
        return process_image(element)
    if model in (Labels2DModel, Labels3DModel):
        return process_labels(element)
    if model is ShapesModel:
        return process_shapes(element)
    if model is PointsModel:
        return process_points(element)
    if model is TableModel:
        return process_table(element)
    raise TypeError(model)
```

## Single scale and multiscale

```python
from xarray import DataArray

from spatialdata import get_pyramid_levels


def full_resolution(raster) -> DataArray:
    if isinstance(raster, DataArray):
        return raster
    return get_pyramid_levels(raster, n=0)  # never hard-code the variable name


def all_levels(raster) -> list[DataArray]:
    return [raster] if isinstance(raster, DataArray) else get_pyramid_levels(raster)
```

To pick a level for a target resolution, compare the scale factors of `get_transformation(level)`;
each level's transformation already includes the scale from that level to level 0.

## Circles and polygons

```python
from shapely import Point


def is_circles(gdf) -> bool:
    return isinstance(gdf.geometry.iloc[0], Point)  # then gdf["radius"] exists
```

`spatialdata.to_polygons(element)` and `spatialdata.to_circles(element)` convert shapes and labels
in either direction (labels to circles uses centroids and radii of equal area).

## Points: stay lazy

```python
pts = sdata["transcripts"]  # dask.dataframe.DataFrame
gene_key = pts.attrs.get("spatialdata_attrs", {}).get("feature_key")
subset = pts[pts[gene_key] == "ACTB"][["x", "y"]] if gene_key else pts[["x", "y"]]
xy = subset.compute()  # load only what you need
```

Select columns before `compute()`. Prefer `bounding_box_query` and `polygon_query` for spatial
subsets.

## Elements and tables

```python
from spatialdata import get_element_instances, get_values, join_spatialelement_table
from spatialdata.models import get_table_keys

region, region_key, instance_key = get_table_keys(sdata["table"])

# instances present in the element (without the background 0 of labels)
ids = get_element_instances(sdata["cells"])

# table rows of the instances of one element, in the element's order
elements, table = join_spatialelement_table(
    sdata=sdata, spatial_element_names="cells", table_name="table", how="right", match_rows="right"
)

# one value per instance, from an obs column, var, obsm, or a column of the element
df = get_values("cell_type", sdata=sdata, element_name="cells", table_name="table")
```

Do not assume that `region_key` is `"region"` or that `instance_key` is `"instance_id"`; read them.

## Coordinate systems

```python
from spatialdata import bounding_box_query, get_extent, transform

cs = "global"
aligned = {
    name: transform(el, to_coordinate_system=cs)
    for _, name, el in sdata.filter_by_coordinate_system(cs).gen_spatial_elements()
}
extent = get_extent(sdata, coordinate_system=cs)  # {'x': (min, max), 'y': (min, max)}
crop = bounding_box_query(
    sdata, axes=("x", "y"), min_coordinate=[0, 0], max_coordinate=[1000, 1000], target_coordinate_system=cs
)
```

Compare or overlay elements only after mapping them into the same coordinate system.

## Channel names

```python
from spatialdata.models import get_channel_names

names = get_channel_names(sdata["he"])  # list of any hashables
sdata.set_channel_names("he", ["R", "G", "B"], write=True)
```

## Producing elements and writing

```python
from spatialdata import SpatialData
from spatialdata.models import Image2DModel, ShapesModel, TableModel

sdata = SpatialData(
    images={"he": Image2DModel.parse(arr, dims=("c", "y", "x"), scale_factors=[2, 2, 2])},
    shapes={"cells": ShapesModel.parse(gdf)},
    tables={"table": TableModel.parse(adata, region="cells", region_key="region", instance_key="cell_id")},
)
sdata.write("out.zarr")  # latest container format
sdata["nuclei"] = ShapesModel.parse(other_gdf)
sdata.write_element("nuclei")  # add a new element to the store
```

Build elements through `parse()`: objects assembled by hand that skip validation are the most
common source of unreadable stores. `write_element` does not replace an element that the object
was read from or last written to.

## Things not to rely on

- The `name` of a `DataArray`, or the name of the data variable inside a `DataTree`.
- The order of columns in points.
- The column names that `spatialdata-io` readers use by default (`region`, `instance_id`, `cell_id`,
  `gene`); they are conventions, not requirements.
- xarray spatial coordinates as a stand-in for transformations.
- `attrs` of points surviving arbitrary Dask operations; set transformations again after reshaping,
  and `parse()` again before writing.
