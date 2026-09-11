# Glossary

Terms used across the three specification layers. Chapters link here with {term}`element`-style
references so that each term is defined once.

```{glossary}
store
  A Zarr hierarchy (directory, zip file, or object-store prefix) whose root group carries the
  SpatialData container metadata. One store holds one dataset.

element
  The unit of data in SpatialData: an image, a labels array, a shapes table, a points table, or an
  annotation table. Each element is stored in its own Zarr group and can be read independently.

element type
  One of `images`, `labels`, `shapes`, `points`, `tables`. Also the name of the top-level Zarr group
  that holds elements of that type.

spatial element
  Any element except a table. Spatial elements carry axes and coordinate transformations.

raster element
  An image or a labels element: an n-dimensional array with named axes, stored as an NGFF
  multiscale image.

region
  A spatial element whose entries can be annotated by a table: labels (one region per integer value)
  or shapes (one region per row). Points are also annotatable in the current implementation.

instance
  One annotatable entry of a region: a label value, or a row of a shapes or points element.

coordinate system
  A named space in which spatial elements can be placed. Elements are mapped into coordinate
  systems by coordinate transformations. Elements that share a coordinate system are aligned.

intrinsic coordinate system
  The coordinate system implied by an element's own storage: pixel indices for raster elements, the
  coordinate columns for points and shapes. It is never named on disk.

coordinate transformation
  A mapping from an element's intrinsic coordinate system to a named coordinate system.

format version
  A version string attached to the container and to each element on disk. Component versions evolve
  independently; see the version history.

model
  In the Python in-memory format, the class that validates and constructs one element type
  (for example `Image2DModel`).
```
