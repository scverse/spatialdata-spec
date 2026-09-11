# Implementation guide

{bdg-secondary}`non-normative`

Nothing on this page is part of the format. It is the shortest path to writing code that works on
any valid `SpatialData` object. Every snippet uses only public `spatialdata` API.

## Dispatch on the element type

Do not test Python types directly (`DataArray` is both image and labels). Ask the model:

```python
from spatialdata.models import (
    get_model,
    Image2DModel,
    Image3DModel,
    Labels2DModel,
    Labels3DModel,
    PointsModel,
    ShapesModel,
    TableModel,
)


def process(element):
    model = get_model(element)  # validates; use validate=False to skip
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

## Single scale vs multiscale

```python
from xarray import DataArray, DataTree
from spatialdata import get_pyramid_levels


def full_resolution(raster) -> DataArray:
    if isinstance(raster, DataArray):
        return raster
    assert isinstance(raster, DataTree)
    return get_pyramid_levels(raster, n=0)  # level 0; never hard-code the variable name


def all_levels(raster) -> list[DataArray]:
    return [raster] if isinstance(raster, DataArray) else get_pyramid_levels(raster)
```

To pick a level for a target resolution, compare `get_transformation(level)` scale factors (each
level's transformation already includes the level → level 0 scale).

## Circles vs polygons

```python
from shapely import Point


def is_circles(gdf) -> bool:
    return isinstance(gdf.geometry.iloc[0], Point)  # then gdf["radius"] exists


def to_polygons_if_needed(gdf):
    return gdf.assign(geometry=gdf.geometry.buffer(gdf["radius"])) if is_circles(gdf) else gdf
```

`spatialdata.to_polygons(element)` and `spatialdata.to_circles(element)` convert shapes and labels
in either direction (labels → circles uses centroids and equivalent-area radii).

## Points: stay lazy

```python
pts = sdata["transcripts"]  # dask.dataframe.DataFrame
gene_key = pts.attrs.get("spatialdata_attrs", {}).get("feature_key")
subset = pts[pts[gene_key] == "ACTB"][["x", "y"]] if gene_key else pts[["x", "y"]]
xy = subset.compute()  # materialise only what you need
```

Select columns before `compute()`. Prefer `bounding_box_query` / `polygon_query` for spatial
subsets; they push the filter into partition-wise reading.

## Elements ↔ tables

```python
from spatialdata import get_element_instances, join_spatialelement_table, get_values
from spatialdata.models import get_table_keys

region, region_key, instance_key = get_table_keys(sdata["table"])

# instances present in the element (background 0 excluded for labels)
ids = get_element_instances(sdata["cells"])

# filter table rows to the instances of one element, keeping the element's order
elements, table = join_spatialelement_table(
    sdata=sdata, spatial_element_names="cells", table_name="table", how="right", match_rows="right"
)

# pull one value per instance from wherever it lives (obs column, var, obsm, or element column)
df = get_values("cell_type", sdata=sdata, element_name="cells", table_name="table")
```

Never assume `region_key == "region"` or `instance_key == "instance_id"`; read them.

## Coordinate systems

```python
from spatialdata import transform, get_extent, bounding_box_query
from spatialdata.transformations import get_transformation

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

Only compare or overlay elements after mapping them into the same coordinate system.

## Channel names

```python
from spatialdata.models import get_channel_names, set_channel_names

names = get_channel_names(sdata["he"])  # list, any hashables
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
sdata.write("out.zarr")  # current format; Zarr v3
sdata.write_element("cells")  # add or overwrite one element in the backing store
```

Always build elements through `parse()`; hand-assembled objects that skip validation are the most
common source of unreadable stores.

## Things not to rely on

- The `name` of a `DataArray` or the data-variable name inside a `DataTree`.
- The order of columns in a points frame.
- Default column names (`region`, `instance_id`, `cell_id`, `gene`) used by `spatialdata-io` readers;
  they are conventions, see {doc}`../../semantic/index`.
- xarray spatial coordinates as a stand-in for transformations.
- `attrs` surviving arbitrary Dask or pandas operations; re-set transformations after heavy
  reshaping and re-`parse()` before writing.
