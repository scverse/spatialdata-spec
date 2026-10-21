(spec)=
# SpatialData abstract data model

% begin spec-intro
SpatialData ([Marconato et al., 2025](https://doi.org/10.1038/s41592-024-02212-x)) is a data model for spatially resolved, multimodal datasets. It
brings together images, segmentation masks, geometric objects, point clouds, and measurement
tables, and relates them in two distinct ways: spatially, through
{ref}`coordinate systems and transformations <spec-coordinate-systems>` that express the locations
of spatial elements in common coordinates, and by annotation, through
{ref}`tables <spec-tables>` whose observations reference instances of spatial elements.
% end spec-intro

This page describes the abstract data model: the concepts and semantics that all implementations
share, independently of how they represent them. Implementations may use different programming
languages, data structures, metadata locations, and APIs, provided they interpret the data model
consistently. The {doc}`storage format <storage-format>` specifies how datasets are serialized; it
repeats each part of the data model and follows it with its storage.

(spec-datasets)=
## Datasets and elements

% begin spec-datasets
A SpatialData dataset is a collection of **named elements** of five types: images, labels, points,
shapes, and tables. It may contain any number of elements of each type, including none. Element
names must be unique within a dataset, even across different element types.

Elements may exist independently of each other, with their own coordinate systems and without
annotations.

A dataset may also contain user-defined metadata.

```{figure} /img/elements.svg
:alt: The five element types: images and labels (raster), points and shapes (vector), and tables, which annotate labels, points and shapes.
:figclass: spec-figure
:width: 100%

The five element types. Tables annotate instances of labels, points and shapes.
```
% end spec-datasets

## Spatial elements

% begin spec-spatial-elements
Four element types represent spatially located data: images, labels, points, and shapes.

The axes are the spatial axes `x`, `y`, and optionally `z`, and the channel axis `c`. Images and
labels have the spatial axes; images additionally have the channel axis. Points and shapes use
spatial coordinates rather than raster axes.[^units]

Multiscale rasters represent the same spatial data at different resolutions. Their resolution levels
belong to a single spatial element.

[^units]: Units are not part of the current model: stores carry a placeholder unit.
% end spec-spatial-elements

(spec-images)=
### Images

% begin spec-images
Images are two- or three-dimensional raster arrays of measurements, with one or more channels. They
may have multiple resolution levels (*multiscale images*).
% end spec-images

(spec-labels)=
### Labels

% begin spec-labels
Labels are two- or three-dimensional integer-valued raster arrays identifying spatial regions.
Pixels with the same nonzero value belong to the same instance; zero represents the background.
Labels may also be multiscale.
% end spec-labels

(spec-points)=
### Points

% begin spec-points
Points are collections of two- or three-dimensional locations, optionally associated with per-point
values such as gene identity or intensity.
% end spec-points

(spec-shapes)=
### Shapes

% begin spec-shapes
Shapes are collections of two-dimensional geometries: within one shapes element, either all
circles, each given by a centre and a positive radius, or all polygons and multipolygons. Each
geometry represents an individually identifiable instance. A shapes element may also give each
geometry a single z position (2.5D shapes).[^shapes-3d]

[^shapes-3d]: 2.5D shapes are experimental in `spatialdata`. `spatialdata` 0.8 also accepts
    geometries with z coordinates, with a warning, and stores them with axes `x, y, z`; true 3D
    vector data is expected to use a different representation.
% end spec-shapes

(spec-coordinate-systems)=
## Coordinate systems and transformations

% begin spec-coordinate-systems
SpatialData relates spatial elements through **named coordinate systems**, which provide common
reference frames for interpreting their locations.

Each spatial element has an **intrinsic coordinate system**, defined by its spatial axes and
coordinates. This coordinate system is specific to the element and may be unnamed.

A spatial element is associated with one or more named coordinate systems through **coordinate
transformations**. Each transformation maps coordinates from the element's intrinsic coordinate
system to a named coordinate system. An element has at most one transformation to each named
coordinate system.

- Multiple elements may share a named coordinate system; their locations are then expressed in the
  same coordinates.
- An element may be associated with multiple named coordinate systems, representing its location in
  different reference frames.
- Named coordinate systems are identified by their name; they may exist only as a name, without a
  separate object.

```{figure} /img/coordinate_systems.png
:alt: Three spatial elements, each in its own intrinsic (pixel) coordinate system, mapped by coordinate transformations into two named coordinate systems; one element is mapped into both.
:figclass: spec-figure
:width: 100%

Each spatial element has its own intrinsic coordinate system and is mapped into one or more named
coordinate systems by coordinate transformations.
```

Transformations include identity, axis mapping, translation, scaling, affine transformations, and
their composition. They operate on named axes, independently of the order in which those axes are
represented.

Transformations directly associate spatial elements with named coordinate systems, rather than
relating pairs of spatial elements or named coordinate systems.[^cs-to-cs] Further transformations
may be derived through composition and inversion where possible.

Coordinate transformations describe spatial relationships without modifying the underlying data.
Applying transformations to raster or vector data is a separate operation.

```{figure} /img/spatialdata_registration.png
:alt: Top: an element whose raw data is unchanged and whose transformation is a rotation. Bottom: after applying the transformation, the raw data is rotated and the transformation is the identity. Both are placed identically in space.
:figclass: spec-figure
:width: 100%

A transformation places the raw data in space without changing it (top). Applying the transformation
rewrites the data and leaves an identity transformation (bottom); both are positioned identically.
```

Sharing a coordinate system does not imply spatial overlap or biological correspondence between
elements. Elements without a shared coordinate system have no defined spatial relationship unless
one can be established through a chain of transformations.

Tables have no spatial coordinate systems or coordinate transformations of their own.

[^cs-to-cs]: Outlook: with NGFF 0.6 support, transformations will relate named coordinate systems to
    each other, and an element may have more than one path into a coordinate system.
% end spec-coordinate-systems

(spec-instances)=
## Instances and identifiers

% begin spec-instances
Points, labels, and shapes can contain identifiable instances:

- In labels, instances are identified by their nonzero integer values.
- In shapes and points, each geometry or point has an identifier. Identifiers are unique within
  their element.[^points-instance]

Instance identifiers are local to their spatial element. An instance is therefore identified by the
combination of its element name and instance identifier.

Different elements may represent the same biological objects, but matching identifiers or
coordinates do not automatically establish correspondence.

% end spec-instances

(spec-tables)=
## Annotation tables

% begin spec-tables
**Tables** contain observations, variables, measurements, and associated annotations. They support
observation-by-variable matrices, additional measurement layers, observation and variable metadata,
and structured auxiliary data.

A table may annotate instances of points, labels, or shapes. In a table that annotates spatial
elements, each observation references one spatial instance through two columns:

- **Element:** The name of the spatial element being annotated.
- **Instance:** The identifier of the instance within that element.

Together, these values identify the spatial instance referenced by an observation.

A table may annotate multiple spatial elements, and a spatial element may be annotated by multiple
tables. Within a table, each instance is referenced by at most one observation; spatial instances
may have no corresponding observations.

**Dangling references are valid.** A table may refer to elements or instances that are not in the
dataset, for example after subsetting or after deleting an element. Such references are ignored when
the table is related to the dataset.

Tables may also exist without annotating any spatial elements.

Annotation relationships do not depend on coordinate systems or transformations.

[^points-instance]: Points may carry a column naming the instance (for example a cell in a labels or
    shapes element) that each point was assigned to. This is a per-point value like any other.
% end spec-tables

## Notes

% the footnotes are rendered here, at the end of the page
