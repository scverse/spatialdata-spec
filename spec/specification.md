(spec)=
# Specification of the SpatialData abstract data model and storage format

SpatialData {cite:p}`Marconato_2025` is a data model for spatially resolved, multimodal datasets. It
brings together images, segmentation masks, geometric objects, point clouds, and measurement
tables, and relates them in two distinct ways: spatially, through
{ref}`coordinate systems and transformations <spec-coordinate-systems>` that express the locations
of spatial elements in common coordinates, and by annotation, through
{ref}`tables <spec-tables>` whose observations reference instances of spatial elements.

This page describes the abstract data model: the concepts and semantics that all implementations
share, independently of how they represent them. Implementations may use different programming
languages, data structures, metadata locations, and APIs, provided they interpret the data model
consistently. After each part of the data model, the implementations specify their representation:
the storage format, which defines how datasets are serialized, and the in-memory formats of the
individual programming languages.

:::::::::{tab-set}
:sync-group: impl

::::::::{tab-item} Data model only
:sync: model
:class-content: tab-model-only

% intentionally empty: shows the data model without any implementation
::::::::

::::::::{tab-item} Storage format
:sync: storage
:selected:

(storage-intro)=

The storage format stores one spatial omics dataset as a Zarr hierarchy with embedded
Parquet files. It reuses [OME-NGFF](https://ngff.openmicroscopy.org) for raster data and for
coordinate transformations, [GeoParquet](https://geoparquet.org) for shapes, Parquet for points,
and the [AnnData on-disk format](https://anndata.readthedocs.io/en/stable/fileformat-prose.html)
for tables. This specification defines only what those standards leave open and where SpatialData
deviates from them.

(storage-intro-versions)=
```{rubric} Versions
```

This page covers every version of the storage format, named by its container format. Where
versions differ, synced tabs show them, newest first; `spatialdata-container-format-0.2` is shown
by default, and the navigation shows which version is selected. The versions and what each
contains are listed in {ref}`storage-versions`.

(storage-intro-reading-this-specification)=
```{rubric} Reading this specification
```

Key words and boxes are explained in {ref}`reading-the-specification`. In addition:

- "Attributes" of a Zarr group means the `attributes` object of its `zarr.json` (Zarr v3) or the
  content of its `.zattrs` file (Zarr v2).
- JSON examples are taken from stores written by `spatialdata` and are abbreviated where marked with
  `...`.
::::::::

::::::::{tab-item} Python
:sync: python

(python-intro)=

The Python in-memory format is the one exposed by
[`spatialdata`](https://github.com/scverse/spatialdata) after reading a store or building a dataset
in code: which Python object represents each element, which dimensions, columns and attributes it
carries, and which invariants hold once it passes validation. It describes `spatialdata` 0.8 as
released; changes are discussed in [scverse/spatialdata](https://github.com/scverse/spatialdata/issues)
and reflected here after release. A tool that follows it can consume and produce SpatialData
objects without depending on `spatialdata` internals; a non-normative
{doc}`implementation guide <in-memory/python-guide>` collects common recipes.

Every element is a standard scientific-Python object, not a subclass: a `spatialdata` image *is* an
`xarray.DataArray`. The SpatialData metadata (transformations, table keys) lives in the object's
`attrs` or, for tables, `uns`.

(python-intro-elements-at-a-glance)=
```{rubric} Elements at a glance
```

| Element | Python type | Model class(es) | SpatialData metadata |
|---------|-------------|-----------------|----------------------|
| images | `xarray.DataArray` or `xarray.DataTree` | `Image2DModel`, `Image3DModel` | `attrs["transform"]` |
| labels | `xarray.DataArray` or `xarray.DataTree` | `Labels2DModel`, `Labels3DModel` | `attrs["transform"]` |
| points | `dask.dataframe.DataFrame` | `PointsModel` | `attrs["transform"]`, `attrs["spatialdata_attrs"]` |
| shapes | `geopandas.GeoDataFrame` | `ShapesModel` | `attrs["transform"]` |
| tables | `anndata.AnnData` | `TableModel` | `uns["spatialdata_attrs"]` |

(python-intro-models)=
```{rubric} Models: parse and validate
```

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

In the Python tabs, "valid" means that `Model.validate()` passes. Validation checks every
requirement unless the text says otherwise.

(python-intro-versions)=
```{rubric} Versions
```

The Python format has been stable since `spatialdata` 0.1, which replaced the earlier `SpatialImage`
and `MultiscaleSpatialImage` subclasses with plain `xarray.DataArray` and `xarray.DataTree` objects
and allowed several tables. It changes with the `spatialdata` releases, independently of the storage
format version.
::::::::

::::::::{tab-item} R
:sync: r

*The R in-memory format ([spatialdataR](https://github.com/HelenaLC/spatialdataR)) is not yet documented here.*
::::::::

::::::::{tab-item} JavaScript
:sync: javascript

*The JavaScript in-memory format ([SpatialData.js](https://github.com/Taylor-CCB-Group/SpatialData.js)) is not yet documented here.*
::::::::
:::::::::

(spec-datasets)=
## Datasets and elements

A SpatialData dataset is a collection of **named elements** of five types: images, labels, points,
shapes, and tables. It may contain any number of elements of each type, including none. Element
names must be unique within a dataset, even across different element types.

Elements may exist independently of each other, with their own coordinate systems and without
annotations.

A dataset may also contain user-defined metadata.

```{figure} /_static/img/elements.svg
:alt: The five element types: images and labels (raster), points and shapes (vector), and tables, which annotate labels, points and shapes.
:figclass: spec-figure
:width: 100%

The five element types. Tables annotate instances of labels, points and shapes.
```

:::::::::{tab-set}
:sync-group: impl

::::::::{tab-item} Data model only
:sync: model
:class-content: tab-model-only

% intentionally empty: shows the data model without any implementation
::::::::

::::::::{tab-item} Storage format
:sync: storage
:selected:

(storage-datasets)=

(storage-datasets-a-store-at-a-glance)=
```{rubric} A store at a glance
```

A `spatialdata-container-format-0.2` store:

```text
dataset.zarr/                       Zarr v3 group
├── zarr.json                       spatialdata_attrs.version = "0.2"  (+ consolidated metadata)
├── images/
│   └── <name>/                     NGFF multiscale image, axes cyx or czyx
│       ├── zarr.json               ome.multiscales, ome.omero.channels, spatialdata_attrs
│       ├── s0/                     full resolution array (name given by datasets[0].path)
│       └── s1/ s2/ ...             optional downsampled levels
├── labels/
│   └── <name>/                     NGFF multiscale image with labels metadata, axes yx or zyx
├── shapes/
│   └── <name>/
│       ├── zarr.json               encoding-type, axes, coordinateTransformations, spatialdata_attrs
│       └── shapes.parquet          single GeoParquet file: geometry [, radius] [, extra columns]
├── points/
│   └── <name>/
│       ├── zarr.json               encoding-type, axes, coordinateTransformations, spatialdata_attrs
│       └── points.parquet/         multi-file Parquet dataset: x, y [, z] [, extra columns]
│           └── part.0.parquet
└── tables/
    └── <name>/                     AnnData Zarr + region; region_key, instance_key name obs columns
```

(storage-datasets-element-types)=
```{rubric} Element types
```

| Type | Group | Payload | Standard reused | Section |
|------|-------|---------|-----------------|---------|
| Image | `images/<name>` | Zarr arrays | NGFF multiscales | {ref}`Images <spec-images>` |
| Labels | `labels/<name>` | Zarr arrays | NGFF multiscales + NGFF labels (`image-label` metadata) | {ref}`Labels <spec-labels>` |
| Shapes | `shapes/<name>` | `shapes.parquet` (single file) | GeoParquet | {ref}`Shapes <spec-shapes>` |
| Points | `points/<name>` | `points.parquet/` (multi-file dataset) | Parquet | {ref}`Points <spec-points>` |
| Table | `tables/<name>` | Zarr arrays | AnnData | {ref}`Tables <spec-tables>` |

The container is the Zarr hierarchy that holds all elements of one dataset. It fixes where elements
live, how they are named, and how a reader discovers the format version of the store and of each
element.

(storage-datasets-root-group)=
```{rubric} Root group
```

The root of a store **MUST** be a Zarr group. Its attributes **MUST** contain a
`spatialdata_attrs` object:

::::{tab-set}
:sync-group: storage-version
:::{tab-item} spatialdata-container-format-0.2
:sync: container-0.2
:selected:

```json
// dataset.zarr/zarr.json
{
  "zarr_format": 3,
  "node_type": "group",
  "attributes": {
    "spatialdata_attrs": {
      "version": "0.2",
      "spatialdata_software_version": "0.6.0"
    },
    "my_metadata": { "sample": "xyz" }
  },
  "consolidated_metadata": { "kind": "inline", "must_understand": false, "metadata": { ... } }
}
```
:::
:::{tab-item} spatialdata-container-format-0.1
:sync: container-0.1

```json
// dataset.zarr/.zattrs
{
  "spatialdata_attrs": {
    "version": "0.1",
    "spatialdata_software_version": "0.6.0"
  },
  "my_metadata": { "sample": "xyz" }
}
```
:::
::::

`spatialdata_attrs.version`
: **MUST** be present. The container format version, for example `"0.2"`; see {ref}`storage-versions`. It determines the
  Zarr format of the whole store: `"0.1"` implies Zarr v2, `"0.2"` implies Zarr v3. Stores written
  before container versioning existed have no `spatialdata_attrs`; readers **SHOULD** treat them as
  version `"0.1"`.

`spatialdata_attrs.spatialdata_software_version`
: **SHOULD** be present when written by `spatialdata`. Informational only; readers **MUST NOT**
  depend on it.

Any other root attribute is user metadata (the `SpatialData.attrs` mapping in Python). It **MUST** be
JSON-serialisable and is otherwise unconstrained. A tool that reads a store and writes it again
(in place or to a new location) **MUST** keep root attributes it does not recognise, so that user
metadata is not lost.

Consolidated metadata **SHOULD** be written (`consolidated_metadata` in Zarr v3, `.zmetadata` in
Zarr v2) so that the store can be listed with one request on object storage. Readers **MUST NOT**
require it. Some Zarr v2 stores, including stores written by `spatialdata`, contain `zmetadata`
(without the leading dot) because of a bug in zarr-python's `FSStore`
([zarr-python#1121](https://github.com/zarr-developers/zarr-python/issues/1121)); readers that use
consolidated metadata **SHOULD** accept both names.

(storage-datasets-element-type-groups)=
```{rubric} Element type groups
```

Elements live in fixed top-level groups named after their element type (see
{ref}`Element types <storage-datasets-element-types>`). A group **MAY** be absent when the dataset has no element of that type; it **MAY** also be present
and empty. Each group **MUST** be a Zarr group. Readers **SHOULD** ignore top-level groups and root
members with other names.

The `labels` group is itself an NGFF *labels* group and carries the list of its children:

::::{tab-set}
:sync-group: storage-version
:::{tab-item} spatialdata-container-format-0.2
:sync: container-0.2
:selected:
```json
// labels/zarr.json → attributes
{ "ome": { "labels": ["blobs_labels", "blobs_multiscale_labels"] } }
```
:::
:::{tab-item} spatialdata-container-format-0.1
:sync: container-0.1
```json
// labels/.zattrs
{ "labels": ["blobs_labels", "blobs_multiscale_labels"] }
```
:::
::::

Writers **MUST** keep this list in sync with the child groups. Readers **SHOULD** enumerate the
child groups when the storage system supports listing. Listing is not always available (for example
plain HTTP, or an S3 bucket without list permission); this is why consolidated metadata is written,
and the list in `labels` is redundant with it. When the store is not listable, readers **SHOULD**
use the consolidated metadata rather than the list. The other four type groups carry no attributes.

(storage-datasets-element-groups-and-names)=
```{rubric} Element groups and names
```

Each element is one Zarr group, a direct child of its type group, named with the element name.
Element names:

- **MUST NOT** be empty, `.`, or `..`;
- **MUST** consist only of alphanumeric characters (Unicode letters and digits), `-`, `_` and `.`;
  whitespace and `/` are therefore excluded;
- **MUST NOT** start with `__`;
- **MUST** be unique across all element types, as in the {ref}`data model <spec-datasets>`, and
  also when compared case-insensitively: `images/Cells` and `labels/cells` **MUST NOT** coexist.
  This keeps stores portable to case-insensitive file systems.

The same rules apply to column names of `obs` and `var`, and to keys of `obsm`, `obsp`, `varm`,
`varp`, `uns` and `layers` in tables (see {ref}`Tables <spec-tables>`).

(storage-datasets-identifying-an-element)=
```{rubric} Identifying an element
```

A reader **MAY** take an element's type from the name of its parent group, but it **SHOULD**
determine the type and the format version from the element's own metadata, as listed below
(attribute paths are relative to the element group's attributes):

| Element type | Type marker | Version location |
|--------------|-------------|------------------|
| images | `ome.multiscales` (container 0.2) or `multiscales` (container 0.1), without `image-label` | `spatialdata_attrs.version` |
| labels | as images, plus `ome.image-label` (container 0.2) or `image-label` (container 0.1) | `spatialdata_attrs.version` |
| shapes | `encoding-type: "ngff:shapes"` | `spatialdata_attrs.version` |
| points | `encoding-type: "ngff:points"` | `spatialdata_attrs.version` |
| tables | `spatialdata-encoding-type: "ngff:regions_table"` | `version`, directly in the attributes (next to `encoding-type`), not inside `spatialdata_attrs` |

Element versions are constrained by the container version; the allowed combinations are listed in
the {ref}`compatibility-matrix`. A reader **SHOULD** skip an element whose version it does not
implement, and **MAY** warn. A reader **MAY** also warn about an element whose version it supports
but that is not allowed by the container version of the store.

(storage-datasets-non-zarr-payloads)=
```{rubric} Non-Zarr payloads
```

Shapes and points store their data in Parquet files inside their element group
(`shapes.parquet`, `points.parquet/`). These are not Zarr nodes. Zarr tooling that lists the
hierarchy may warn about them; readers and validators **MUST** tolerate their presence and
**MUST NOT** treat them as Zarr arrays or groups.

:::{admonition} Implementation note
:class: implementation-note

To read a store from scratch: open the root group, read `spatialdata_attrs.version`, then for each
of the five type groups that exist, iterate over child groups (skipping hidden entries such as
`.zgroup` and `.zmetadata` in Zarr v2), and dispatch on the metadata of each element (see
"Identifying an element"); `spatialdata.read_zarr` (container formats 0.1 and 0.2) dispatches on
the type group name instead. Read each element's `version` before parsing its payload.
:::

:::{admonition} Divergence from NGFF
:class: ngff-divergence

NGFF defines no top-level layout for a collection of images, shapes, points and tables. The five
type groups, the `spatialdata_attrs` object and the `encoding-type` markers on shapes and points are
SpatialData extensions, and so is storing Parquet files inside a Zarr hierarchy. NGFF *plate*,
*well* and *bioformats2raw.layout* metadata are not used.
:::
::::::::

::::::::{tab-item} Python
:sync: python

(python-datasets)=

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
- Element names follow the {ref}`naming rules of the storage format <storage-datasets-element-groups-and-names>`.
  `spatialdata` checks the characters and rejects a name used by two elements. It does not reject
  two names that differ only in case when they belong to different element types; code that writes
  stores **SHOULD** check this itself.
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
::::::::

::::::::{tab-item} R
:sync: r

*The R in-memory format ([spatialdataR](https://github.com/HelenaLC/spatialdataR)) is not yet documented here.*
::::::::

::::::::{tab-item} JavaScript
:sync: javascript

*The JavaScript in-memory format ([SpatialData.js](https://github.com/Taylor-CCB-Group/SpatialData.js)) is not yet documented here.*
::::::::
:::::::::

## Spatial elements

Four element types represent spatially located data: images, labels, points, and shapes.

The axes are the spatial axes `x`, `y`, and optionally `z`, and the channel axis `c`. Images and
labels have the spatial axes; images additionally have the channel axis. Points and shapes use
spatial coordinates rather than raster axes.[^units]

Multiscale rasters represent the same spatial data at different resolutions. Their resolution levels
belong to a single spatial element.

:::::::::{tab-set}
:sync-group: impl

::::::::{tab-item} Data model only
:sync: model
:class-content: tab-model-only

% intentionally empty: shows the data model without any implementation
::::::::

::::::::{tab-item} Storage format
:sync: storage
:selected:

(storage-spatial-elements)=

(storage-spatial-elements-axes)=
```{rubric} Axes
```

An element's axes are fixed by its type:

| Element | Axes (in storage order) |
|---------|-------------------------|
| images | `c`, `y`, `x` or `c`, `z`, `y`, `x` |
| labels | `y`, `x` or `z`, `y`, `x` |
| shapes | `x`, `y` or `x`, `y`, `z` |
| points | `x`, `y` or `x`, `y`, `z` |

Shapes are 2D or 2.5D: the geometry column holds `x` and `y`, and 2.5D shapes add a separate `z`
column. Writers **MUST NOT** store `z` inside the geometries; GeoPandas allows it, but some GeoPandas
operations are incompatible with it, so it is not part of the format.

Only these four axis names exist. `c` has NGFF type `channel`; `x`, `y`, `z` have type `space`. No
other axis names or types (such as `time`) are allowed in container formats 0.1 and 0.2. Coordinates
along `x`, `y`, `z` are real numbers in the same unit within one coordinate system.

:::{admonition} Divergence from NGFF
:class: ngff-divergence

NGFF allows other axes, such as `time`, and custom axis types. Container formats 0.1 and 0.2 do not
support them, so a valid NGFF image with such axes is not a valid SpatialData raster element.
:::

For raster elements, container formats 0.1 and 0.2 do not fix whether the integer coordinate `i`
is the centre or the corner of pixel `i`, and `spatialdata` is not consistent:
`spatialdata.transform` treats `(0, 0)` as the centre of the first pixel (the NGFF convention),
while parts of rasterization treat it as a corner. This is a known bug and legacy behaviour
([scverse/spatialdata#165](https://github.com/scverse/spatialdata/issues/165)); it will be
addressed in the next version, which follows NGFF. Shapes and points store coordinates
directly.
::::::::

::::::::{tab-item} Python
:sync: python

(python-spatial-elements)=

The four spatial types are exported together as `spatialdata.models.SpatialElement`
(`DataArray | DataTree | GeoDataFrame | DaskDataFrame`); tables are not part of it.

Axes are the xarray dims of raster elements, in the order of the
{ref}`storage format <storage-spatial-elements-axes>`, and the coordinate columns of points and
shapes. A `DataArray` alone does not say whether it is an image or labels; code **SHOULD** dispatch
on `get_model()` rather than on the Python type.
::::::::

::::::::{tab-item} R
:sync: r

*The R in-memory format ([spatialdataR](https://github.com/HelenaLC/spatialdataR)) is not yet documented here.*
::::::::

::::::::{tab-item} JavaScript
:sync: javascript

*The JavaScript in-memory format ([SpatialData.js](https://github.com/Taylor-CCB-Group/SpatialData.js)) is not yet documented here.*
::::::::
:::::::::

(spec-images)=
### Images

Images are two- or three-dimensional raster arrays of measurements, with one or more channels. They
may have multiple resolution levels (*multiscale images*).

:::::::::{tab-set}
:sync-group: impl

::::::::{tab-item} Data model only
:sync: model
:class-content: tab-model-only

% intentionally empty: shows the data model without any implementation
::::::::

::::::::{tab-item} Storage format
:sync: storage
:selected:

(storage-images)=

An image element is an [NGFF multiscale image](https://ngff.openmicroscopy.org/0.5/index.html#multiscale-md)
stored in `images/<name>`, with the axis restrictions and additional attributes listed here.
Everything not mentioned (array layout, chunking, codecs, pyramid construction) is governed by
[NGFF](https://ngff.openmicroscopy.org/specifications/index.html) and [Zarr](https://zarr-specs.readthedocs.io/).

(storage-images-layout)=
```{rubric} Layout
```

```text
images/<name>/
├── zarr.json          multiscales, omero, spatialdata_attrs
├── s0/                level 0: full resolution, shape (c, y, x) or (c, z, y, x)
├── s1/                optional coarser levels ...
└── s2/
```

- **Names.** Each level's array is found through `multiscales[0].datasets[*].path`. As in NGFF,
  `path` is any string giving the array's location relative to the image group; the names carry no
  meaning. Readers **MUST** resolve arrays through `path` and **MUST NOT** assume a naming scheme.
- **Order.** Levels are ordered by their position in `datasets`, from the highest resolution to the
  lowest, as NGFF requires; the resolution of each level is given by its `scale` (see `datasets`
  below).

:::{admonition} Implementation note
:class: implementation-note

Stores in the wild use two naming schemes. `spatialdata` writes raster elements with ome-zarr-py,
which named levels `0`, `1`, … up to version 0.13 and `s0`, `s1`, … from version 0.14
([ome-zarr-py#544](https://github.com/ome/ome-zarr-py/pull/544)). `spatialdata` requires only a
minimum ome-zarr-py version, so the names depend on the ome-zarr-py installed when the store was
written: for example `0`, `1`, … with `spatialdata` 0.6 and ome-zarr-py 0.12, and `s0`, `s1`, … with
`spatialdata` 0.8 and ome-zarr-py 0.19.
:::

(storage-images-attributes)=
```{rubric} Attributes
```

The examples below were written by `spatialdata` 0.8 for the same image `my_image` (two channels,
two levels); `multiscales[0].coordinateTransformations` is specified in {ref}`Coordinate systems and transformations <spec-coordinate-systems>`
and elided here.

::::::{tab-set}
:sync-group: storage-version
::::{tab-item} spatialdata-container-format-0.2
:sync: container-0.2
:selected:

Raster format 0.3, in `images/<name>/zarr.json` → `attributes`:

```json
{
  "ome": {
    "version": "0.5-dev-spatialdata",
    "multiscales": [
      {
        "datasets": [
          {
            "path": "s0",
            "coordinateTransformations": [
              { "type": "scale", "scale": [1.0, 1.0, 1.0] },
              { "type": "translation", "translation": [0.0, 0.0, 0.0] }
            ]
          },
          {
            "path": "s1",
            "coordinateTransformations": [
              { "type": "scale", "scale": [1.0, 2.0, 2.0] },
              { "type": "translation", "translation": [0.0, 0.5, 0.5] }
            ]
          }
        ],
        "name": "/images/my_image",
        "axes": [
          { "name": "c", "type": "channel" },
          { "name": "y", "type": "space" },
          { "name": "x", "type": "space" }
        ],
        "coordinateTransformations": [ ... ]
      }
    ],
    "omero": {
      "channels": [
        { "label": "DAPI" },
        { "label": "CD3" }
      ]
    }
  },
  "spatialdata_attrs": { "version": "0.3" }
}
```
::::
::::{tab-item} spatialdata-container-format-0.1
:sync: container-0.1

Raster format 0.2, in `images/<name>/.zattrs`:

```json
{
  "multiscales": [
    {
      "datasets": [
        {
          "path": "s0",
          "coordinateTransformations": [
            { "type": "scale", "scale": [1.0, 1.0, 1.0] },
            { "type": "translation", "translation": [0.0, 0.0, 0.0] }
          ]
        },
        {
          "path": "s1",
          "coordinateTransformations": [
            { "type": "scale", "scale": [1.0, 2.0, 2.0] },
            { "type": "translation", "translation": [0.0, 0.5, 0.5] }
          ]
        }
      ],
      "name": "/images/my_image",
      "axes": [
        { "name": "c", "type": "channel" },
        { "name": "y", "type": "space" },
        { "name": "x", "type": "space" }
      ],
      "version": "0.4-dev-spatialdata",
      "coordinateTransformations": [ ... ]
    }
  ],
  "omero": {
    "channels": [
      { "label": "DAPI" },
      { "label": "CD3" }
    ]
  },
  "spatialdata_attrs": { "version": "0.2" }
}
```

Raster format 0.1, in `images/<name>/.zattrs`:

```json
{
  "multiscales": [
    {
      "datasets": [
        {
          "path": "s0",
          "coordinateTransformations": [
            { "type": "scale", "scale": [1.0, 1.0, 1.0] },
            { "type": "translation", "translation": [0.0, 0.0, 0.0] }
          ]
        },
        {
          "path": "s1",
          "coordinateTransformations": [
            { "type": "scale", "scale": [1.0, 2.0, 2.0] },
            { "type": "translation", "translation": [0.0, 0.5, 0.5] }
          ]
        }
      ],
      "name": "/images/my_image",
      "axes": [
        { "name": "c", "type": "channel" },
        { "name": "y", "type": "space" },
        { "name": "x", "type": "space" }
      ],
      "version": "0.4",
      "coordinateTransformations": [ ... ]
    }
  ],
  "omero": {
    "channels": [
      { "label": "DAPI" },
      { "label": "CD3" }
    ]
  },
  "spatialdata_attrs": { "version": "0.1" }
}
```

Older writers of raster format 0.1 stored the channel names in a legacy `channels_metadata` key
instead of `omero`; readers **SHOULD** accept it.

:::{admonition} One container version, several element versions
:class: note

Before the container format was bumped together with the formats inside it, container format 0.1
was kept while the raster format went from 0.1 to 0.2. A container 0.1 store can therefore hold
either raster version; see the {ref}`compatibility-matrix`.
:::
::::
::::::

`ome.version` / `multiscales[0].version`
: **MUST** be `"0.5-dev-spatialdata"` for raster 0.3, `"0.4-dev-spatialdata"` for raster 0.2,
  `"0.4"` for raster 0.1. The `-dev-spatialdata` suffix signals that the metadata follows an NGFF
  draft (the transformations proposal) and is not a released NGFF version.

`multiscales`
: **MUST** contain exactly one entry.

`multiscales[0].axes`
: **MUST** be exactly `c, y, x` or `c, z, y, x` with types `channel`, `space`, `space`(, `space`).
  Axes carry no `unit` here; units live in the coordinate system objects of the transformations.

`multiscales[0].datasets`
: One entry per pyramid level, ordered from full resolution to coarsest. `path` **MUST** be the name
  of the child array. Each entry **MUST** contain a `coordinateTransformations` list whose first
  entry is a `scale` with the ratio between the level-0 shape and this level's shape (`1.0` for
  `c`). It **MAY** be followed by a `translation`, which carries no meaning: readers **MUST** place
  each level using its `scale` alone, as `spatialdata` does.[^level-translation] Single-scale images
  have one dataset.

`multiscales[0].coordinateTransformations`
: **MUST** be present with at least one entry, as specified in {ref}`Coordinate systems and transformations <spec-coordinate-systems>`. Maps
  level-0 pixel space to named coordinate systems.

`multiscales[0].name`
: **MAY** be present. Informational; readers **MUST NOT** interpret it. `spatialdata` writes the
  group path (for example `"/images/my_image"`) for multiscale images; for single-scale images, it leaves the
  name to ome-zarr-py, which writes `"image"` from version 0.18
  ([ome-zarr-py#515](https://github.com/ome/ome-zarr-py/pull/515)) and the group path before (for
  example with `spatialdata` 0.6 and ome-zarr-py 0.12).

`omero.channels`
: **SHOULD** be present with one object per `c` index, in order. `label` is the channel name and
  **MAY** be a string or a number. Readers **SHOULD** fall back to `0 … n-1` when absent. Other
  `omero` fields defined by NGFF (`window`, `color`, `rdefs`, …) **MAY** be present and are not
  interpreted by SpatialData.

`spatialdata_attrs.version`
: **MUST** be present: `"0.3"`, `"0.2"` or `"0.1"`.

(storage-images-arrays)=
```{rubric} Arrays
```

- Level `0` **MUST** hold the full-resolution data. Every level **MUST** have the same number of
  dimensions, in the axes order above.
- Any numeric Zarr data type is allowed.
- Chunk shape and codecs are free. Writers **SHOULD** keep chunks well below 2 GiB.
- Three- or four-channel images whose channel labels are `r, g, b` (`, a`) **MAY** be rendered as
  RGB(A) by viewers; this is a convention, not a requirement.

:::{admonition} Implementation note
:class: implementation-note

A minimal reader needs `axes`, `datasets[*].path`, the per-level `scale` in
`datasets[*].coordinateTransformations`, `coordinateTransformations`, and `omero.channels[*].label`. Everything else in the group can be
ignored. To read only a region at a given resolution, pick the coarsest level whose scale meets the
requested resolution and compose its per-level `scale` with the element transformation.
:::

:::{admonition} Divergence from NGFF
:class: ngff-divergence

Relative to NGFF 0.4 / 0.5: the `version` string is not a released version; `axes` are restricted to
`c(z)yx` and `time` is not allowed; `multiscales[0].coordinateTransformations` uses the RFC-5-style
encoding with named output coordinate systems rather than the released `scale`/`translation`-only
form; `spatialdata_attrs` is an extension. A conforming NGFF 0.5 reader can still open the arrays
and per-level scales if it ignores the version string.
:::
::::::::

::::::::{tab-item} Python
:sync: python

(python-images)=

An image is an `xarray.DataArray` (single scale) or an `xarray.DataTree` (multiscale).

(python-images-single-scale)=
```{rubric} Single scale
```

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

- `dims` **MUST** be exactly `("c", "y", "x")` or `("c", "z", "y", "x")`, in this order.
- `.data` **MUST** be a `dask.array.Array`; `parse()` wraps NumPy input.
- Any numeric dtype is allowed.
- `attrs["transform"]` **MUST** be a non-empty `dict[str, BaseTransformation]`, keyed by
  coordinate system name (see {ref}`transformations <python-coordinate-systems>`).
- `coords["c"]` holds the channel names (any hashable values; by default `0 … n-1`). Read them with
  `get_channel_names()` and change them with `set_channel_names()`.
- `coords["x"]`, `coords["y"]` and `coords["z"]` are the pixel centres `i + 0.5` in intrinsic
  units. They are derived, recomputed by `parse()`, and no substitute for the transformation.
- `.name` is `"image"` after parsing; it carries no meaning and code **MUST NOT** rely on it.

(python-images-multiscale)=
```{rubric} Multiscale
```

```text
<xarray.DataTree>
Group: /
├── /scale0   image (c, y, x) uint8 (2, 8, 8)   transform = {'global': T}
├── /scale1   image (c, y, x) uint8 (2, 4, 4)   transform = {'global': Sequence[Scale(2, 2), T]}
└── /scale2   image (c, y, x) uint8 (2, 2, 2)   transform = {'global': Sequence[Scale(4, 4), T]}
```

- Children **MUST** be named `scale0`, `scale1`, … in order of decreasing resolution; `scale0` is
  the full resolution.
- Each child **MUST** contain exactly one data variable, with the same name in every child. The
  name is arbitrary and code **MUST NOT** depend on it; `spatialdata` uses `"image"`.
- Each variable satisfies the single-scale rules.
- The tree's own `attrs` **MUST NOT** contain `"transform"`. Level `0` holds the element's
  transformations; level `i` holds, for each coordinate system,
  `Sequence([Scale(level i → level 0), T])`, so that every level maps directly into the
  coordinate system. `get_transformation(tree)` returns the transformations of level `0`.
- The channel axis is never downsampled.

(python-images-building)=
```{rubric} Building an image
```

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
::::::::

::::::::{tab-item} R
:sync: r

*The R in-memory format ([spatialdataR](https://github.com/HelenaLC/spatialdataR)) is not yet documented here.*
::::::::

::::::::{tab-item} JavaScript
:sync: javascript

*The JavaScript in-memory format ([SpatialData.js](https://github.com/Taylor-CCB-Group/SpatialData.js)) is not yet documented here.*
::::::::
:::::::::

(spec-labels)=
### Labels

Labels are two- or three-dimensional integer-valued raster arrays identifying spatial regions.
Pixels with the same nonzero value belong to the same instance; zero represents the background.
Labels may also be multiscale.

:::::::::{tab-set}
:sync-group: impl

::::::::{tab-item} Data model only
:sync: model
:class-content: tab-model-only

% intentionally empty: shows the data model without any implementation
::::::::

::::::::{tab-item} Storage format
:sync: storage
:selected:

(storage-labels)=

{bdg-primary}`raster 0.3` {bdg-light}`Zarr v3` · {bdg-secondary}`raster 0.2, 0.1` {bdg-light}`Zarr v2`

A labels element is stored in `labels/<name>` as an NGFF multiscale image with
[image-label](https://ngff.openmicroscopy.org/0.5/index.html#labels-md) metadata.

Everything in {ref}`Images <spec-images>` applies, with the following differences.

(storage-labels-attributes)=
```{rubric} Attributes
```

::::{tab-set}
:sync-group: storage-version
:::{tab-item} spatialdata-container-format-0.2
:sync: container-0.2
:selected:

Raster format 0.3 (Zarr v3):

```json
{
  "ome": {
    "version": "0.5-dev-spatialdata",
    "multiscales": [{
      "name": "image",
      "axes": [ { "name": "y", "type": "space" }, { "name": "x", "type": "space" } ],
      "datasets": [ { "path": "s0", "coordinateTransformations": [
          { "type": "scale", "scale": [1.0, 1.0] }, { "type": "translation", "translation": [0.0, 0.0] } ] } ],
      "coordinateTransformations": [ ... ]
    }],
    "image-label": { "version": "0.5" }
  },
  "spatialdata_attrs": { "version": "0.3" }
}
```
:::
:::{tab-item} spatialdata-container-format-0.1
:sync: container-0.1

Raster format 0.2 (Zarr v2; raster 0.1 differs as for images):

```json
{
  "multiscales": [{ "version": "0.4-dev-spatialdata", "name": "blobs_labels", "axes": [ ... ], "datasets": [ ... ], "coordinateTransformations": [ ... ] }],
  "image-label": { "version": "0.4" },
  "spatialdata_attrs": { "version": "0.2" }
}
```
:::
::::

`multiscales[0].axes`
: **MUST** be exactly `y, x` or `z, y, x`, all of type `space`. There is no channel axis.

`image-label`
: **MUST** be present. `version` **SHOULD** match the NGFF version the store follows (`"0.5"` in
  Zarr v3 stores, `"0.4"` in Zarr v2 stores). The NGFF `colors`, `properties` and `source` fields
  **MAY** be present; SpatialData does not write or interpret them. Multiscale labels written by
  `spatialdata` 0.6 in Zarr v2 stores lack this key; readers **SHOULD** tolerate its absence.

`omero`
: **MUST NOT** be present.

The parent `labels` group lists the element in its `labels` attribute ({ref}`Datasets and elements <spec-datasets>`).

(storage-labels-arrays)=
```{rubric} Arrays
```

- The data type **MUST** be an integer type (signed or unsigned) or boolean (`False` = 0, `True` = 1).
- The array values are the instance identifiers of the {ref}`data model <spec-instances>`.
  Readers **MUST NOT** treat the background value `0` as an instance.
- Downsampled levels **SHOULD** be produced without interpolation (nearest neighbour or
  majority), so that no new label values appear.

:::{admonition} Implementation note
:class: implementation-note

To join a labels element with a table: read `instance_key` from the table, then match the integer
values of the label array against the table's `obs[instance_key]` column for rows whose
`obs[region_key]` equals this element's name. See {ref}`Tables <spec-tables>`.
:::
::::::::

::::::::{tab-item} Python
:sync: python

(python-labels)=

Labels are represented like {ref}`images <python-images>`, single scale or multiscale, with these
differences:

- `dims` **MUST** be exactly `("y", "x")` or `("z", "y", "x")`; there is no `c` axis.
- The dtype **MUST** be an integer or boolean type. The value `0` is the background.

```python
from spatialdata.models import Labels2DModel

lab = Labels2DModel.parse(mask)  # dims ("y", "x"); Identity to "global"
```

The instances of a labels element are its nonzero values; see {ref}`tables <python-tables>`.
::::::::

::::::::{tab-item} R
:sync: r

*The R in-memory format ([spatialdataR](https://github.com/HelenaLC/spatialdataR)) is not yet documented here.*
::::::::

::::::::{tab-item} JavaScript
:sync: javascript

*The JavaScript in-memory format ([SpatialData.js](https://github.com/Taylor-CCB-Group/SpatialData.js)) is not yet documented here.*
::::::::
:::::::::

(spec-points)=
### Points

Points are collections of two- or three-dimensional locations, optionally associated with per-point
values such as gene identity or intensity.

:::::::::{tab-set}
:sync-group: impl

::::::::{tab-item} Data model only
:sync: model
:class-content: tab-model-only

% intentionally empty: shows the data model without any implementation
::::::::

::::::::{tab-item} Storage format
:sync: storage
:selected:

(storage-points)=

{bdg-primary}`points 0.2` {bdg-light}`Zarr v3` · {bdg-secondary}`points 0.1` {bdg-light}`Zarr v2`

A points element is stored in `points/<name>` as a Zarr group whose attributes hold the
SpatialData metadata and whose payload is a partitioned Parquet dataset with one row per point.
This layout is designed for large tables (10⁶ to 10⁹ rows) and lazy, partition-wise reading.

(storage-points-layout)=
```{rubric} Layout
```

```text
points/<name>/
├── zarr.json              encoding-type, axes, coordinateTransformations, spatialdata_attrs
└── points.parquet/        Parquet dataset (directory)
    ├── part.0.parquet
    └── part.1.parquet ...
```

(storage-points-attributes)=
```{rubric} Attributes
```

```json
{
  "encoding-type": "ngff:points",
  "axes": ["x", "y", "z"],
  "coordinateTransformations": [ { "type": "identity", "input": {...}, "output": { "name": "global", ... } } ],
  "spatialdata_attrs": {
    "version": "0.2",
    "feature_key": "gene",
    "instance_key": "cell"
  }
}
```

`encoding-type`
: **MUST** be `"ngff:points"`.

`axes`
: **MUST** be `["x", "y"]` or `["x", "y", "z"]`, and **MUST** match the coordinate columns present
  in the payload.

`coordinateTransformations`
: **MUST** be present with at least one entry ({ref}`Coordinate systems and transformations <spec-coordinate-systems>`). Input axes are in the
  order given by `axes`.

`spatialdata_attrs.version`
: **MUST** be `"0.2"` (Zarr v3) or `"0.1"` (Zarr v2). The two versions differ only in the Zarr
  format of the group.

`spatialdata_attrs.feature_key`
: **MAY** be present. Name of the column that holds the feature each point measures (e.g. a gene or
  protein identifier). When present, the column **SHOULD** exist and **SHOULD** be dictionary
  encoded (categorical).

`spatialdata_attrs.instance_key`
: **MAY** be present. Name of the column that holds the identifier of the instance each point belongs
  to (e.g. a cell). The format does not define which element those identifiers refer to.

(storage-points-payload-points-parquet)=
```{rubric} Payload: points.parquet/
```

A directory containing one or more Parquet files named `part.<i>.parquet`. Readers **MUST**
concatenate all parts in ascending `<i>` order. All parts **MUST** share one schema.

Coordinate columns
: `x` and `y` **MUST** be present; `z` **MUST** be present when `axes` lists it. Type **MUST** be
  `int32`, `int64`, `float32` or `float64`.

Other columns
: **MAY** be present with any Parquet type. Column names follow the naming rules in
  {ref}`Datasets and elements <spec-datasets>`.

Row index
: Writers **MUST** store the dataframe index as a column referenced from the `pandas.index_columns`
  schema metadata (`spatialdata` names an unnamed index `__null_dask_index__`). Its values are the
  row identifiers, the instance identifiers of the {ref}`data model <spec-instances>`; readers
  **MUST** use them, not row positions, and **MUST NOT** treat the column as data. Row identifiers
  **MUST** be unique within the element.[^points-index]

:::{admonition} Implementation note
:class: implementation-note

`points.parquet/` is a standard Hive-less Parquet dataset: `pyarrow.parquet.read_table`,
`arrow::open_dataset` in R, `dask.dataframe.read_parquet` and `parquet-wasm` all read it directly.
For spatial queries, read the Parquet row-group statistics of `x`, `y` (and `z`) to skip row groups
outside the query box before loading data.
:::

:::{admonition} Divergence from NGFF
:class: ngff-divergence

NGFF has no points type. The group attributes, the `ngff:points` marker and the Parquet payload are
SpatialData definitions.
:::
::::::::

::::::::{tab-item} Python
:sync: python

(python-points)=

Points are a `dask.dataframe.DataFrame`.

```text
     x      y  gene   cell        # x, y[, z] numeric; extra columns allowed
0  46.0  395.0  ACTB     9
1 334.0  224.0  GAPDH    7
attrs = {'transform': {'global': Identity},
         'spatialdata_attrs': {'feature_key': 'gene', 'instance_key': 'cell'}}
```

- Columns `x` and `y` **MUST** be present and `z` **MAY** be; each **MUST** have the dtype
  `int32`, `int64`, `float32` or `float64`.
- The index holds the point identifiers.
- `attrs["transform"]` **MUST** be a non-empty `dict[str, BaseTransformation]`.
- `attrs["spatialdata_attrs"]` **MAY** hold `feature_key` and `instance_key`, each naming an
  existing column. `parse()` makes the `feature_key` column categorical; it **SHOULD** have known
  categories, as unknown categories force a full pass over the data.
- Other columns are free per-point annotations. `parse()` does not guarantee the column order.

Dask data frames have no `attrs` of their own. `spatialdata` registers an `attrs` accessor and keeps
it through `__getitem__`, `copy`, `drop`, `map_partitions`, `sample`, `set_index`, `compute`, `.loc`
and `.iloc`. Other operations, `assign` among them, return a data frame with empty `attrs`; code
**MUST** set the transformations again before adding such a data frame to a dataset.

Build with `PointsModel.parse(df, coordinates={"x": "x_um", "y": "y_um"}, feature_key="gene")` from
a pandas or Dask data frame, or with `PointsModel.parse(array, annotation=df)` from an `(n, 2)` or
`(n, 3)` array. The data is one partition unless `npartitions` or `chunksize` is passed; reading a
store gives one partition per Parquet part.
::::::::

::::::::{tab-item} R
:sync: r

*The R in-memory format ([spatialdataR](https://github.com/HelenaLC/spatialdataR)) is not yet documented here.*
::::::::

::::::::{tab-item} JavaScript
:sync: javascript

*The JavaScript in-memory format ([SpatialData.js](https://github.com/Taylor-CCB-Group/SpatialData.js)) is not yet documented here.*
::::::::
:::::::::

(spec-shapes)=
### Shapes

Shapes are collections of two-dimensional geometries: within one shapes element, either all
circles, each given by a centre and a positive radius, or all polygons and multipolygons. Each
geometry represents an individually identifiable instance. A shapes element may also give each
geometry a single z position (2.5D shapes).[^shapes-3d]

:::::::::{tab-set}
:sync-group: impl

::::::::{tab-item} Data model only
:sync: model
:class-content: tab-model-only

% intentionally empty: shows the data model without any implementation
::::::::

::::::::{tab-item} Storage format
:sync: storage
:selected:

(storage-shapes)=

{bdg-primary}`shapes 0.3` {bdg-light}`Zarr v3` · {bdg-secondary}`shapes 0.2` {bdg-light}`Zarr v2` · {bdg-secondary}`shapes 0.1` {bdg-light}`legacy`

A shapes element is stored in `shapes/<name>` as a Zarr group whose attributes hold the SpatialData
metadata and whose payload is one [GeoParquet](https://geoparquet.org/releases/v1.0.0/) file with
one row per instance.

(storage-shapes-layout)=
```{rubric} Layout
```

```text
shapes/<name>/
├── zarr.json          encoding-type, axes, coordinateTransformations, spatialdata_attrs
└── shapes.parquet     GeoParquet 1.0.0
```

(storage-shapes-attributes)=
```{rubric} Attributes
```

```json
{
  "encoding-type": "ngff:shapes",
  "axes": ["x", "y"],
  "coordinateTransformations": [ { "type": "identity", "input": {...}, "output": { "name": "global", ... } } ],
  "spatialdata_attrs": { "version": "0.3" }
}
```

`encoding-type`
: **MUST** be `"ngff:shapes"`.

`axes`
: **MUST** be `["x", "y"]`, or `["x", "y", "z"]` if and only if the payload has a `z` column
  (2.5D shapes).

`coordinateTransformations`
: **MUST** be present with at least one entry ({ref}`Coordinate systems and transformations <spec-coordinate-systems>`). Input axes are `x, y` in
  this order.

`spatialdata_attrs.version`
: **MUST** be `"0.3"` (Zarr v3) or `"0.2"` (Zarr v2). Version `"0.1"` uses a different payload, see
  below.

The attributes are identical for shapes 0.2 and 0.3; the version tracks the Zarr format of the
container.

(storage-shapes-payload-shapes-parquet)=
```{rubric} Payload: shapes.parquet
```

A single GeoParquet file. The GeoParquet `geo` metadata **MUST** be present with
`primary_column: "geometry"`.

`geometry`
: **MUST** be present. Encoding **MUST** be `WKB` or the GeoArrow native encoding as defined by
  GeoParquet 1.1; writers default to WKB, readers **MUST** support WKB and **SHOULD** support
  GeoArrow. `crs` **MUST** be `null`: coordinates are in the element's intrinsic coordinate system,
  not in a geographic reference system. Geometries **MUST** be 2D. Readers **SHOULD** accept
  geometries with z coordinates and axes `x, y, z`, which `spatialdata` 0.8 writes with a warning.

Geometry types
: All rows **MUST** be `Point`, or all rows **MUST** be `Polygon` or `MultiPolygon` (the two may
  be mixed). Other geometry types are not allowed.

`radius`
: **MUST** be present when the geometries are `Point`, and **MUST NOT** be present otherwise. A
  numeric column; every value **MUST** be finite and strictly positive. A point plus a radius is a
  circle; the radius is expressed in the same units as the coordinates and is scaled by the
  coordinate transformation.

`z`
: **MAY** be present: a numeric column with the z position of each geometry (2.5D shapes). When
  present, `axes` lists `z`.

Row index
: The pandas index is stored following the Parquet/pandas convention: a `RangeIndex` described only
  in the `pandas` schema metadata, or an explicit index column (typically `__index_level_0__`)
  referenced from `pandas.index_columns`. The index values are the instance identifiers of the
  {ref}`data model <spec-instances>`; they **MUST** be unique and **MAY** be integers or strings.

Other columns
: **MAY** be present with any Parquet type (string columns **MAY** be Arrow `string` or
  `large_string`). They are per-instance annotations stored with the element. Column names follow
  the naming rules in {ref}`Datasets and elements <spec-datasets>`.

The file **MUST** contain at least one row.[^empty-shapes]

:::{admonition} Implementation note
:class: implementation-note

Read the whole file with any GeoParquet-capable library (`geopandas`, `sf` + `arrow`, `geoarrow-js`,
…). Decide between circles and polygons by checking `geo.columns.geometry.geometry_types` or the
first geometry. Do not use `shapes.parquet` metadata to find transformations: they live only in the
Zarr group attributes.
:::

:::{dropdown} Legacy shapes 0.1 (Zarr v2, ragged arrays)
:icon: history

Before GeoParquet was adopted (`spatialdata` < 0.2.2), geometries were stored as Zarr arrays in the
element group following the shapely ragged-array layout:

```text
shapes/<name>/
├── .zattrs           encoding-type, axes, coordinateTransformations,
│                     spatialdata_attrs: { version: "0.1", geos: { name: "POLYGON", type: 3 } }
├── coords            (n_vertices, 2) float array
├── offset0           ring offsets (polygons, multipolygons)
├── offset1           part offsets (multipolygons only)
├── Index             instance identifiers
└── radius            only when geos.name == "POINT"
```

`spatialdata_attrs.geos.name` is the GEOS geometry type name (`POINT`, `POLYGON`, `MULTIPOLYGON`)
and `geos.type` its integer code. `spatialdata` still reads this version and rewrites it as 0.3.
:::

:::{admonition} Divergence from NGFF
:class: ngff-divergence

NGFF has no shapes type. The group attributes, the `ngff:shapes` marker and the use of GeoParquet are
SpatialData definitions.
:::
::::::::

::::::::{tab-item} Python
:sync: python

(python-shapes)=

Shapes are a `geopandas.GeoDataFrame`.

```text
            geometry  radius   cell_type      # geometry: GeoSeries; extra columns allowed
n_01  POINT (10 12)     4.5   T cell
n_02  POINT (33 40)     5.0   B cell
attrs = {'transform': {'global': Identity}}
```

- The column `geometry` **MUST** be a `GeoSeries` with at least one row.
- Geometries **MUST** be 2D and either all `Point` (circles) or all `Polygon` or `MultiPolygon`.
  Validation checks only the first geometry; `ShapesModel.validate_shapes_not_mixed_types()`
  checks all of them.
- For circles, the column `radius` **MUST** be present, with finite, strictly positive values in
  intrinsic units.
- The index holds the instance identifiers, integers or strings. They **MUST** be unique;
  validation does not check this.
- `attrs["transform"]` **MUST** be a non-empty `dict[str, BaseTransformation]`.
- `crs` is `None`. Other columns are free per-instance annotations.

Build from a `GeoDataFrame` (`ShapesModel.parse(gdf)`), from a GeoJSON file, or from shapely ragged
arrays (`ShapesModel.parse(coords, geometry=..., offsets=..., radius=...)`). Shapes are loaded
eagerly.
::::::::

::::::::{tab-item} R
:sync: r

*The R in-memory format ([spatialdataR](https://github.com/HelenaLC/spatialdataR)) is not yet documented here.*
::::::::

::::::::{tab-item} JavaScript
:sync: javascript

*The JavaScript in-memory format ([SpatialData.js](https://github.com/Taylor-CCB-Group/SpatialData.js)) is not yet documented here.*
::::::::
:::::::::

(spec-coordinate-systems)=
## Coordinate systems and transformations

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

```{figure} /_static/img/coordinate_systems.png
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

```{figure} /_static/img/spatialdata_registration.png
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

:::::::::{tab-set}
:sync-group: impl

::::::::{tab-item} Data model only
:sync: model
:class-content: tab-model-only

% intentionally empty: shows the data model without any implementation
::::::::

::::::::{tab-item} Storage format
:sync: storage
:selected:

(storage-coordinate-systems)=

The {ref}`intrinsic coordinate system <spec-coordinate-systems>` of a stored element is:

- **Shapes and points:** the space of the stored coordinates, in their own units.
- **Images and labels:** the space of pixel indices of scale 0 (the highest resolution). Every
  scale maps into it through the scale of its level in the `multiscales` metadata; per-level
  translations carry no meaning ({ref}`Images <spec-images>`).

In container formats 0.1 and 0.2 the intrinsic coordinate system is never named, on disk or in
memory.

In the example below, three elements share the named coordinate system `"global"`, and
`my_points` also maps into `"micron"`:

```text
                        intrinsic (never shared)             named (shared)
   my_image  cyx ──identity────────────────────────▶ "global"
   my_labels yx  ──scale [0.5, 0.5]────────────────▶ "global"
   my_points xy  ──sequence [scale, translation]───▶ "global"
   my_points xy  ──scale [0.2, 0.2]────────────────▶ "micron"
```

(storage-coordinate-systems-encoding)=
```{rubric} Encoding
```

:::{warning}
**Divergence from NGFF.** `spatialdata` was created when NGFF 0.4 was current, and it needed
coordinate systems and transformations, which were being specified in NGFF RFC-5. RFC-5 was expected
to be part of the next NGFF release, so `spatialdata` built on a draft of it and marked raster
elements with the version string `"0.4-dev-spatialdata"`. NGFF 0.5 was released without RFC-5;
`spatialdata` adopted NGFF 0.5 but kept its draft encoding of transformations, hence
`"0.5-dev-spatialdata"`. RFC-5 has evolved since, so the encoding below differs from RFC-5 as it
has been released in NGFF 0.6 (see {doc}`storage-format/ngff-compatibility`). Compared with NGFF:

- NGFF 0.4 and 0.5 allow only `scale` and `translation`, only on raster data, and reference no
  named coordinate systems;
- compared with [RFC-5](https://ngff.openmicroscopy.org/rfc/5/), `input` and `output` are inlined
  coordinate system objects instead of names referencing a `coordinateSystems` list, and the same
  encoding is applied to shapes and points.

RFC-5 has been included in NGFF 0.6, and support for NGFF 0.6 in `spatialdata` is being actively
developed. From then on, most of the description of coordinate systems and
transformations will be delegated to NGFF, and implementations will be able to rely on OME-Zarr
libraries instead of reimplementing SpatialData-specific transformations.
:::

:::{admonition} Implementation note
:class: implementation-note

Because the encoding diverges from NGFF, generic OME-Zarr libraries cannot read these
transformations. In practice, an implementation can:

1. rely on `spatialdata` (Python) to read and write them;
2. outside Python, validate against the JSON schemas of
   [SpatialData.validate](https://github.com/Huber-group-EMBL/SpatialData.validate/tree/main/inst/extdata),
   which cover the raster metadata, including the transformations;
3. wait for the `spatialdata` release with NGFF 0.6 support, which delegates the description of
   coordinate systems and transformations entirely to the NGFF specification.
:::

Transformations are stored as a JSON list named `coordinateTransformations`. Each entry maps the
element's intrinsic coordinate system to one named coordinate system:

```json
{
  "type": "scale",
  "scale": [1.0, 0.5, 0.5],
  "input": {
    "name": "zyx",
    "axes": [
      { "name": "z", "type": "space", "unit": "unit" },
      { "name": "y", "type": "space", "unit": "unit" },
      { "name": "x", "type": "space", "unit": "unit" }
    ]
  },
  "output": {
    "name": "global",
    "axes": [
      { "name": "z", "type": "space", "unit": "unit" },
      { "name": "y", "type": "space", "unit": "unit" },
      { "name": "x", "type": "space", "unit": "unit" }
    ]
  }
}
```

`type`
: **MUST** be one of the types below.

`input`
: **MUST** be a coordinate system object describing the element's own axes, in storage order. Its
  `name` carries no meaning (writers use the concatenated axis names, e.g. `"cyx"`); readers
  **MUST NOT** rely on it.

`output`
: **MUST** be a coordinate system object. Its `name` is the name of the target coordinate system.
  Its `axes` list the output axes in the order produced by the transformation.

A coordinate system object has a `name` (string) and `axes` (list). Each axis has `name`, `type` and,
for `space` axes, `unit`:

```json
{
  "name": "global",
  "axes": [
    { "name": "z", "type": "space", "unit": "unit" },
    { "name": "y", "type": "space", "unit": "unit" },
    { "name": "x", "type": "space", "unit": "unit" }
  ]
}
```

 Writers that do not know the physical unit **MUST** write the placeholder
string `"unit"`; readers **MUST** accept any string here.

:::{admonition} Implementation note
:class: implementation-note

In memory, the Python `spatialdata` framework does not use coordinate system objects: it keeps only
the `output.name` of each transformation, which is sufficient for container formats 0.1 and 0.2. NGFF 0.6 support will
bring full alignment with NGFF coordinate systems and transformations.
:::

Within one `coordinateTransformations` list, `output.name` values **MUST** be unique, since an
element has at most one transformation to each named coordinate system. The JSON schemas do not check this; `spatialdata` writes
unique names by construction (transformations are kept in a mapping keyed by coordinate system name)
and, when reading a list with a repeated name, keeps the last entry. The list **MUST** contain at least one entry. When no
alignment information exists, writers **SHOULD** map the element to `"global"` with an `identity`
transformation. Coordinate system names follow the same rules as element names
({ref}`Datasets and elements <spec-datasets>`).

(storage-coordinate-systems-where-the-list-lives)=
```{rubric} Where the list lives
```

| Element | Location |
|---------|----------|
| images, labels (Zarr v3) | `attributes.ome.multiscales[0].coordinateTransformations` |
| images, labels (Zarr v2) | `.zattrs` → `multiscales[0].coordinateTransformations` |
| shapes, points | group attribute `coordinateTransformations` |

Raster elements additionally carry the NGFF per-level transformations in
`multiscales[0].datasets[i].coordinateTransformations` (a `scale` per pyramid level, relative to
level `0`). To place a pixel of level `i` into a named coordinate system, a reader **MUST** apply the
level's `scale` first, then the SpatialData transformation. See {ref}`Images <spec-images>`.

(storage-coordinate-systems-transformation-types)=
```{rubric} Transformation types
```

All arrays and matrices are ordered like the `input.axes` (and `output.axes`) they refer to, and
**MUST** cover every input axis of the element. Axes that a transformation does not affect (typically
`c`) are written explicitly with a neutral value (`1.0` for scale, `0.0` for translation).

::::{tab-set}

:::{tab-item} identity
No additional fields. Output axes equal input axes.
```json
{
  "type": "identity",
  "input": {
    "name": "cyx",
    "axes": [
      { "name": "c", "type": "channel" },
      { "name": "y", "type": "space", "unit": "unit" },
      { "name": "x", "type": "space", "unit": "unit" }
    ]
  },
  "output": {
    "name": "global",
    "axes": [
      { "name": "c", "type": "channel" },
      { "name": "y", "type": "space", "unit": "unit" },
      { "name": "x", "type": "space", "unit": "unit" }
    ]
  }
}
```
:::

:::{tab-item} scale
`scale`: list of numbers, one per input axis. Output axes equal input axes.
```json
{
  "type": "scale",
  "scale": [1.0, 0.5, 2.0],
  "input": {
    "name": "cyx",
    "axes": [
      { "name": "c", "type": "channel" },
      { "name": "y", "type": "space", "unit": "unit" },
      { "name": "x", "type": "space", "unit": "unit" }
    ]
  },
  "output": {
    "name": "global",
    "axes": [
      { "name": "c", "type": "channel" },
      { "name": "y", "type": "space", "unit": "unit" },
      { "name": "x", "type": "space", "unit": "unit" }
    ]
  }
}
```
:::

:::{tab-item} translation
`translation`: list of numbers, one per input axis. Output axes equal input axes.
```json
{
  "type": "translation",
  "translation": [0.0, 10.0, -3.0],
  "input": {
    "name": "cyx",
    "axes": [
      { "name": "c", "type": "channel" },
      { "name": "y", "type": "space", "unit": "unit" },
      { "name": "x", "type": "space", "unit": "unit" }
    ]
  },
  "output": {
    "name": "global",
    "axes": [
      { "name": "c", "type": "channel" },
      { "name": "y", "type": "space", "unit": "unit" },
      { "name": "x", "type": "space", "unit": "unit" }
    ]
  }
}
```
:::

:::{tab-item} affine
`affine`: matrix with one row per output axis and one column per input axis plus a final column for
the translation. The homogeneous row `[0, ..., 0, 1]` is omitted. Output axes **MAY** differ in
order from input axes; the row order follows `output.axes`.
```json
{
  "type": "affine",
  "affine": [
    [1.0, 0.0, 0.0, 0.0],
    [0.0, 0.0, 1.0, 5.0],
    [0.0, 2.0, 0.0, 6.0]
  ],
  "input": {
    "name": "cyx",
    "axes": [
      { "name": "c", "type": "channel" },
      { "name": "y", "type": "space", "unit": "unit" },
      { "name": "x", "type": "space", "unit": "unit" }
    ]
  },
  "output": {
    "name": "global",
    "axes": [
      { "name": "c", "type": "channel" },
      { "name": "x", "type": "space", "unit": "unit" },
      { "name": "y", "type": "space", "unit": "unit" }
    ]
  }
}
```
The example maps `(c, y, x) ↦ (c, x + 5, 2·y + 6)`.
:::

:::{tab-item} mapAxis
`mapAxis`: object whose keys are output axis names and values are input axis names. Used to permute
axes.
```json
{
  "type": "mapAxis",
  "mapAxis": { "x": "y", "y": "x" },
  "input": {
    "name": "cyx",
    "axes": [
      { "name": "c", "type": "channel" },
      { "name": "y", "type": "space", "unit": "unit" },
      { "name": "x", "type": "space", "unit": "unit" }
    ]
  },
  "output": {
    "name": "global",
    "axes": [
      { "name": "c", "type": "channel" },
      { "name": "x", "type": "space", "unit": "unit" },
      { "name": "y", "type": "space", "unit": "unit" }
    ]
  }
}
```
:::

:::{tab-item} sequence
`transformations`: list of transformations applied in order. Each inner entry has its own `type`,
fields, `input` and `output`; the inner `input.name` and `output.name` **MUST** be ignored by readers
and only the axes used. The output axes of entry *i* **MUST** equal the input axes of entry *i+1*.
```json
{
  "type": "sequence",
  "transformations": [
    {
      "type": "scale",
      "scale": [1.0, 2.0, 2.0],
      "input": {
        "name": "cyx",
        "axes": [
          { "name": "c", "type": "channel" },
          { "name": "y", "type": "space", "unit": "unit" },
          { "name": "x", "type": "space", "unit": "unit" }
        ]
      },
      "output": {
        "name": "global",
        "axes": [
          { "name": "c", "type": "channel" },
          { "name": "y", "type": "space", "unit": "unit" },
          { "name": "x", "type": "space", "unit": "unit" }
        ]
      }
    },
    {
      "type": "translation",
      "translation": [0.0, 1.0, 1.0],
      "input": {
        "name": "cyx",
        "axes": [
          { "name": "c", "type": "channel" },
          { "name": "y", "type": "space", "unit": "unit" },
          { "name": "x", "type": "space", "unit": "unit" }
        ]
      },
      "output": {
        "name": "global",
        "axes": [
          { "name": "c", "type": "channel" },
          { "name": "y", "type": "space", "unit": "unit" },
          { "name": "x", "type": "space", "unit": "unit" }
        ]
      }
    }
  ],
  "input": {
    "name": "cyx",
    "axes": [
      { "name": "c", "type": "channel" },
      { "name": "y", "type": "space", "unit": "unit" },
      { "name": "x", "type": "space", "unit": "unit" }
    ]
  },
  "output": {
    "name": "global",
    "axes": [
      { "name": "c", "type": "channel" },
      { "name": "y", "type": "space", "unit": "unit" },
      { "name": "x", "type": "space", "unit": "unit" }
    ]
  }
}
```
:::
::::

No other transformation types are part of container formats 0.1 and 0.2. In particular,
`rotation`, `byDimension`, `inverseOf`, `bijection`, `coordinates` and `displacements`, defined by
NGFF RFC-5, are not supported: `spatialdata` fails to read an element that uses them (or skips
the element with `on_bad_files="warn"`).

:::{admonition} Implementation note
:class: implementation-note

Every supported type can be reduced to a single affine matrix of shape `(n_out + 1) × (n_in + 1)`.
A reader can convert each entry to that form on load and compose sequences by matrix
multiplication, which is what `spatialdata` does in `BaseTransformation.to_affine_matrix`. Circles
in shapes require care: a non-uniform scale or a shear turns a circle into an ellipse, which the
format cannot represent. In such cases `spatialdata` warns and scales the radius by the mean of the
moduli of the eigenvalues of the linear part; to transform such shapes exactly, approximate the
circles with polygons first (`spatialdata.to_polygons`).
:::
::::::::

::::::::{tab-item} Python
:sync: python

(python-coordinate-systems)=

A transformation is an instance of a `spatialdata.transformations` class. Unlike the stored
encoding, it carries no coordinate system objects: it is self-contained and applies to any element
whose axes it mentions.

(python-coordinate-systems-classes)=
```{rubric} Classes
```

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
```{rubric} Axes
```

When a transformation is applied to an element:

- element axes that the transformation does not mention pass through unchanged (for example `c`
  under a `Scale` on `y`, `x`);
- transformation axes that the element does not have are ignored (a `Scale` on `z`, `y`, `x`
  applied to a 2D element drops `z`);
- a transformation that produces an axis the element does not have, and that cannot pass through,
  raises.

The stored form spells out every axis of the element; writing expands the transformation to them.

(python-coordinate-systems-where)=
```{rubric} Where transformations live
```

Every spatial element has `attrs["transform"]`, a `dict[str, BaseTransformation]` from coordinate
system name to the transformation from the element's intrinsic coordinates into that system. Code
**SHOULD** use the functions below rather than the dict, so that Dask accessors, multiscale levels
and the backing store stay consistent:

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
```{rubric} Mapping to the storage format
```

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
objects and keeps the name of the output coordinate system as the dict key. Other stored types
raise when read (see {ref}`storage-coordinate-systems-transformation-types`).
::::::::

::::::::{tab-item} R
:sync: r

*The R in-memory format ([spatialdataR](https://github.com/HelenaLC/spatialdataR)) is not yet documented here.*
::::::::

::::::::{tab-item} JavaScript
:sync: javascript

*The JavaScript in-memory format ([SpatialData.js](https://github.com/Taylor-CCB-Group/SpatialData.js)) is not yet documented here.*
::::::::
:::::::::

(spec-instances)=
## Instances and identifiers

Points, labels, and shapes can contain identifiable instances:

- In labels, instances are identified by their nonzero integer values.
- In shapes and points, each geometry or point has an identifier. Identifiers are unique within
  their element.[^points-instance]

Instance identifiers are local to their spatial element. An instance is therefore identified by the
combination of its element name and instance identifier.

Different elements may represent the same biological objects, but matching identifiers or
coordinates do not automatically establish correspondence.

(spec-tables)=
## Annotation tables

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

:::::::::{tab-set}
:sync-group: impl

::::::::{tab-item} Data model only
:sync: model
:class-content: tab-model-only

% intentionally empty: shows the data model without any implementation
::::::::

::::::::{tab-item} Storage format
:sync: storage
:selected:

(storage-tables)=

{bdg-primary}`tables 0.2` {bdg-light}`Zarr v3` · {bdg-secondary}`tables 0.1` {bdg-light}`Zarr v2`

A table element is an [AnnData](https://anndata.readthedocs.io/en/stable/fileformat-prose.html)
object stored in `tables/<name>` using the AnnData on-disk format for Zarr. Observations are the
rows of `obs`; the *element* and *instance* columns of the {ref}`data model <spec-tables>` are the
`obs` columns named by `region_key` and `instance_key`.

This section specifies only what SpatialData adds to AnnData. Encoding of `X`, `obs`, `var`,
`layers`, `obsm`, `obsp`, `varm`, `varp`, `uns` and `raw` is exactly as specified by AnnData and is
not repeated here. The encodings present in a store follow the `anndata` release that wrote it
(for example, string indices are `nullable-string-array` groups since `anndata` 0.13 and were
`string-array` arrays before); readers **MUST** support the encodings of the AnnData specification
version they claim.

(storage-tables-layout)=
```{rubric} Layout
```

```text
tables/<name>/
├── zarr.json          anndata encoding + region, region_key, instance_key, version
├── X/  obs/  var/  layers/  obsm/  obsp/  varm/  varp/  raw/     (AnnData)
└── uns/
    └── spatialdata_attrs/      region, region_key, instance_key   (copy, see below)
```

(storage-tables-attributes)=
```{rubric} Attributes
```

The group attributes are the AnnData ones plus five SpatialData keys at the same level:

```json
{
  "encoding-type": "anndata",
  "encoding-version": "0.1.0",
  "spatialdata-encoding-type": "ngff:regions_table",
  "region": ["cells_labels", "nuclei_shapes"],
  "region_key": "region",
  "instance_key": "instance_id",
  "version": "0.2"
}
```

`spatialdata-encoding-type`
: **MUST** be `"ngff:regions_table"`.

`version`
: **MUST** be `"0.2"` (Zarr v3) or `"0.1"` (Zarr v2). Note that, unlike other element types, the
  version is a top-level attribute and not nested under `spatialdata_attrs`.

`region`
: A string, a list of strings, or `null`. The name(s) of the elements this table annotates. Each
  name **SHOULD** be a labels, shapes or points element in the same store. Readers **MUST NOT**
  reject a table whose `region` names an absent element, and **MAY** warn.

`region_key`
: A string or `null`. Name of the `obs` column that states, for each row, which element in
  `region` it annotates.

`instance_key`
: A string or `null`. Name of the `obs` column that holds the instance identifier within that
  element.

`region`, `region_key` and `instance_key` **MUST** either all be `null` (a table that annotates
nothing) or all be non-null.

(storage-tables-annotation-rules)=
```{rubric} Annotation rules
```

When the table annotates elements:

- `obs[region_key]` **MUST** be a categorical column whose set of values equals `region`.
- `obs[instance_key]` **MUST NOT** contain nulls. For labels elements the values are the integer
  label values; for shapes and points they are the row index values of the payload, with matching
  type.
- Each pair `(obs[region_key], obs[instance_key])` **MUST** be unique: each instance is referenced
  by at most one row.
- Readers **SHOULD** match rows to instances by identifier, and tolerate instances without a row
  and dangling references.
- Tables **MUST NOT** carry coordinate transformations.

```text
tables/cells                          labels/cells_labels   shapes/nuclei_shapes
obs.region      obs.instance_id       (pixel values)        (row index)
cells_labels    1        ──────────▶  1
cells_labels    2        ──────────▶  2
nuclei_shapes   "n_07"   ────────────────────────────────▶  "n_07"
```

(storage-tables-the-uns-spatialdata-attrs-copy)=
```{rubric} The uns/spatialdata_attrs copy
```

The same three keys are also stored inside the table as the AnnData `uns["spatialdata_attrs"]`
mapping (`region`, `region_key`, `instance_key`), because `spatialdata` keeps them there in memory
and AnnData serialises `uns` as-is. Writers **MUST** keep the two copies equal. Readers **MAY** use
either; implementations that do not parse `uns` **SHOULD** use the group attributes.

(storage-tables-naming)=
```{rubric} Naming
```

`obs` and `var` column names and the keys of `obsm`, `obsp`, `varm`, `varp`, `uns` and `layers`
**MUST** follow the element naming rules of {ref}`Datasets and elements <spec-datasets>`. `_index` is reserved by AnnData and
**MUST NOT** be used as a column name.

:::{admonition} Implementation note
:class: implementation-note

AnnData readers exist for Python, R (`anndataR`, `zellkonverter`), Julia (`Muon.jl`) and
JavaScript (`vitessce`'s zarr loaders). Read the table with one of those, then read the five
attributes above from the group. The `spatialdata` default column names written by `spatialdata-io`
are `region` for `region_key` and `instance_id` for `instance_key`; these are conventions, not
requirements.
:::

:::{admonition} Divergence from NGFF
:class: ngff-divergence

NGFF has no table type. SpatialData tables follow the spirit of the (unmerged) NGFF tables proposal, whose
`ngff:regions_table` marker and `region`/`region_key`/`instance_key` fields it reuses.
:::
::::::::

::::::::{tab-item} Python
:sync: python

(python-tables)=

A table is an `anndata.AnnData`.

```text
AnnData n_obs × n_vars
    obs: 'region' (category), 'instance_id' (int64), ...
    uns: 'spatialdata_attrs' = {'region': ['cells', 'nuclei'], 'region_key': 'region', 'instance_key': 'instance_id'}
```

- `uns["spatialdata_attrs"]` **MAY** be absent; the table then annotates nothing. When present, it
  **MUST** contain `region` (`str` or `list[str]`), `region_key` (`str`) and `instance_key` (`str`).
- `obs[region_key]` **MUST** be categorical, and its values **MUST** match `region`.
- `obs[instance_key]` **MUST NOT** contain nulls, and each `(region, instance)` pair **MUST** be
  unique.
- The dtype of `obs[instance_key]` **SHOULD** match the instance identifiers of the annotated
  element: integers for labels, the index dtype for points and shapes. A string versus non-string
  mismatch raises when the table is added to a `SpatialData`.
- Column names of `obs` and `var` and keys of `obsm`, `obsp`, `varm`, `varp`, `uns` and `layers`
  **MUST** follow the {ref}`naming rules <storage-tables-naming>`.
- Tables have no transformations and cannot annotate other tables.

Build with `TableModel.parse(adata, region=["cells"], region_key="region", instance_key="instance_id")`.
Re-target an existing table with `sdata.set_table_annotates_spatialelement(...)` and read the keys
with `get_table_keys(adata)`.

:::{admonition} Implementation note
:class: implementation-note

`spatialdata.get_element_instances(element)` returns the instance identifiers of an element: the
unique nonzero values of labels, the index of points and shapes. Every element–table join matches
them against `obs[instance_key]`; the {doc}`implementation guide <in-memory/python-guide>` shows the
helpers that do this.
:::
::::::::

::::::::{tab-item} R
:sync: r

*The R in-memory format ([spatialdataR](https://github.com/HelenaLC/spatialdataR)) is not yet documented here.*
::::::::

::::::::{tab-item} JavaScript
:sync: javascript

*The JavaScript in-memory format ([SpatialData.js](https://github.com/Taylor-CCB-Group/SpatialData.js)) is not yet documented here.*
::::::::
:::::::::

## References

```{bibliography}
:filter: docname in docnames
```

## Notes

% the footnotes are rendered here, at the end of the page

[^shapes-3d]: 2.5D shapes are experimental in `spatialdata`. `spatialdata` 0.8 also accepts
    geometries with z coordinates, with a warning, and stores them with axes `x, y, z`; true 3D
    vector data is expected to use a different representation.
[^points-index]: `spatialdata` always stores the index. A dataset without it has no usable row
    identifiers: Parquet readers such as dask number the rows of each part file from 0.
[^level-translation]: ome-zarr-py ≥ 0.18, which `spatialdata` uses to write raster elements,
    writes a `translation` of `(scale − 1) / 2` after each per-level `scale`; whether a store has it
    depends on the installed ome-zarr-py. NGFF readers that apply it place downsampled levels half a
    coarse pixel away from where `spatialdata` places them. Outlook: per-level translations are
    expected to gain a meaning together with NGFF 0.6 and a fixed pixel-centre convention.
[^empty-shapes]: Not a property of the data model: `spatialdata` infers from the first geometry
    whether an element holds circles or polygons and how many axes it has, and an empty file records
    neither. Points, labels and tables may be empty. Spatial queries in `spatialdata` drop elements
    that would become empty instead of storing them.
[^units]: Units are not part of the current model: stores carry a placeholder unit.
[^cs-to-cs]: Outlook: with NGFF 0.6 support, transformations will relate named coordinate systems to
    each other, and an element may have more than one path into a coordinate system.
[^points-instance]: Points may carry a column naming the instance (for example a cell in a labels or
    shapes element) that each point was assigned to. This is a per-point value like any other.
