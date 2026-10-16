# Transformations

In memory, a coordinate transformation is an instance of a `spatialdata.transformations`
class. Unlike the on-disk encoding, in-memory transformations do **not** carry coordinate system
objects: they are self-contained and can be applied to any element whose axes they mention.

## Classes

| Class | Constructor | Notes |
|-------|-------------|-------|
| `Identity` | `Identity()` | |
| `Scale` | `Scale([sy, sx], axes=("y", "x"))` | one factor per listed axis |
| `Translation` | `Translation([ty, tx], axes=("y", "x"))` | |
| `Affine` | `Affine(matrix, input_axes=("x", "y"), output_axes=("x", "y"))` | `matrix` is `(n_out + 1) × (n_in + 1)` homogeneous |
| `MapAxis` | `MapAxis({"x": "y", "y": "x"})` | output axis → input axis; can rename, permute, duplicate axes |
| `Sequence` | `Sequence([t1, t2, ...])` | applied left to right |

All inherit from `BaseTransformation` and provide:

- `to_affine_matrix(input_axes, output_axes)` — the homogeneous matrix for the given axes;
- `inverse()`;
- `transform_points(points)` for raw coordinates; the element-level API is
  `spatialdata.transform(element, to_coordinate_system=...)`.

## Axis semantics

A transformation lists the axes it acts on. When applied to an element:

- element axes **not** mentioned by the transformation pass through unchanged (e.g. `c` under a
  `Scale` on `y, x`);
- transformation axes **not** present in the element are ignored (a 3D `Scale` on a 2D element
  drops `z`);
- it is an error when the transformation *produces* an axis the element does not have and that
  axis cannot pass through (an `Affine` `xy → xyz` applied to `xyz` data is ambiguous).

This is why the on-disk form always spells out every element axis while the in-memory form does
not: serialisation expands the transformation to the element's axes.

## Where transformations live

Every spatial element stores `attrs["transform"]`, a `dict[str, BaseTransformation]` mapping a
coordinate system name to the transformation from the element's intrinsic coordinates into that
system. Use the functions, not the dict, so that Dask accessors, multiscale levels and backing
stores stay consistent:

```python
from spatialdata.transformations import (
    get_transformation,
    set_transformation,
    remove_transformation,
    get_transformation_between_coordinate_systems,
)

t = get_transformation(element)  # to "global" (default)
t = get_transformation(element, "micron")  # to a named system
all_t = get_transformation(element, get_all=True)  # dict

set_transformation(element, Scale([0.5, 0.5], axes=("y", "x")), "micron")
set_transformation(element, {"global": Identity(), "micron": ...}, set_all=True)
set_transformation(element, t, "micron", write_to_sdata=sdata)  # also persist to disk
remove_transformation(element, "micron")

t_ab = get_transformation_between_coordinate_systems(sdata, source, target)
```

`get_transformation_between_coordinate_systems` treats elements and coordinate systems as nodes of
a graph and composes (and inverts) transformations along the unique path between two nodes;
ambiguity raises.

## Raster specifics

- For a `DataTree`, level `i` stores `Sequence([Scale(level_i → level_0), T])` per coordinate
  system; `get_transformation` on the tree returns `T` (level `0`).
- xarray coordinates (`coords["x"]`, …) are pixel centres in intrinsic space, derived data only.
  `spatialdata.transform(..., maintain_positioning=True)` re-rasterises; the default resamples
  into the target system and stores the residual transformation.

## Mapping to the on-disk encoding

| In memory | On disk `type` | Direction |
|-----------|----------------|-----------|
| `Identity` | `identity` | both |
| `Scale` | `scale` | both |
| `Translation` | `translation` | both |
| `Affine` | `affine` | both |
| `MapAxis` | `mapAxis` | both |
| `Sequence` | `sequence` | both |
| — | `rotation`, `byDimension` | read only (converted to `Affine`/`Sequence`) |

On write, `BaseTransformation.to_ngff(input_axes, output_axes, output_coordinate_system_name)`
produces the NGFF-style object with inlined coordinate systems described in the
{doc}`on-disk chapter <../../on-disk/coordinate-systems>`; on read the reverse conversion drops the
coordinate system objects and keeps only the `output.name` as the dict key.
