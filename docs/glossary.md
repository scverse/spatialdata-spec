# Glossary

Terms used across the three specification layers. Chapters link here with {term}`element`-style
references so that each term is defined once.

```{glossary}
store
  A Zarr hierarchy (directory, zip file, or object-store prefix) whose root group carries the
  SpatialData container metadata. One store holds one dataset.

element
  The unit of data in SpatialData. Its type is one of image, labels, shapes, points or table: an
  image, a labels array, a shapes dataframe, a points dataframe, or an annotation table. Each element
  is stored in its own Zarr group and can be read independently.

spatial element
  Any element except a table. Spatial elements carry axes and coordinate transformations. This
  distinction is legacy: there is a strong community push to store centroids in tables, so tables
  may soon also carry spatial information (without being required to).

raster element
  An image or a labels element: an n-dimensional array with named axes, stored as an NGFF
  multiscale image, possibly with a single scale.

instance
  One annotatable entry of a spatial element: a label value, or a row of a shapes or points
  element.

coordinate system
  A named space in which spatial elements can be placed. In
  `spatialdata-container-format-0.2`, elements are *mapped* into coordinate systems by coordinate
  transformations. With the upcoming NGFF 0.6 support, elements that share a coordinate system are
  aligned; this simplifies their use and will be documented in detail when released.

intrinsic coordinate system
  The coordinate system implied by an element's own storage. In `spatialdata-container-format-0.2`
  it is never named, on disk or in memory, and it is often confused. With the upcoming NGFF 0.6
  support it will always be named on disk (the in-memory behaviour will be documented). For vector
  data (points, shapes) it is the space of the stored coordinates, in
  their own units. For raster data it is the space of pixel indices of scale 0 (the highest
  resolution), which all scales map to after applying the scale of each level; per-level
  translations are not supported in `spatialdata-container-format-0.2` and will be with NGFF 0.6
  support. It will be explained in detail once the overhaul of coordinate
  transformations is released with NGFF 0.6 support.

coordinate transformation
  A mapping between coordinate systems. In
  `spatialdata-container-format-0.2` it maps an element's intrinsic coordinate system to a named
  coordinate system; with NGFF 0.6 support it will always be between named coordinate systems.

format version
  A version string attached to the container and to each element on disk. The container format
  version is bumped whenever any version inside it changes; how the versions relate is in the
  {ref}`compatibility matrix <compatibility-matrix>`.

model
  In the Python in-memory format, the classes that parse (construct) and validate one element type,
  for example `Image2DModel`. A model is not the Python type of the element:
  `Image2DModel.parse()` returns an `xarray.DataArray` (single scale) or an `xarray.DataTree`
  (multiscale, more than one scale), and those are the element types.
```
