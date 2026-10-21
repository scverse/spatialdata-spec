(storage)=
# SpatialData storage format

:::{include} data-model.md
:start-after: % begin spec-intro
:end-before: % end spec-intro
:::

This page specifies the storage format: how a dataset of the {doc}`abstract data model <data-model>`
is serialized. Each section repeats a part of the data model, in plain language, and then specifies
how it is stored; the storage format parts are normative.

The storage format stores one spatial omics dataset as a Zarr hierarchy with embedded
Parquet files. It reuses [OME-NGFF](https://ngff.openmicroscopy.org) for raster data and for
coordinate transformations, [GeoParquet](https://geoparquet.org) for shapes, Parquet for points,
and the [AnnData on-disk format](https://anndata.readthedocs.io/en/stable/fileformat-prose.html)
for tables. This specification defines only what those standards leave open and where SpatialData
deviates from them.

(storage-intro-versions)=
## Versions

This page covers every version of the storage format, named by its container format. Where
versions differ, synced tabs show them, newest first; `spatialdata-container-format-0.2` is shown
by default, and the navigation shows which version is selected. The versions and what each
contains are listed in {ref}`storage-versions`.

(storage-intro-reading-this-specification)=
## Reading this specification

- The key words **MUST**, **MUST NOT**, **SHOULD**, **SHOULD NOT** and **MAY** are to be
  interpreted as described in [RFC 2119](https://www.rfc-editor.org/rfc/rfc2119). The parts taken
  from the data model use no key words.
- Boxes labelled *Implementation note* are not normative; they help with understanding and
  implementing. Boxes labelled *Divergence from NGFF* flag places where a valid SpatialData store
  is not a valid NGFF 0.4 or 0.5 store.
- "Attributes" of a Zarr group means the `attributes` object of its `zarr.json` (Zarr v3) or the
  content of its `.zattrs` file (Zarr v2).
- JSON examples are taken from stores written by `spatialdata` and are abbreviated where marked with
  `...`.

(storage-datasets)=
## Datasets and elements

:::{include} data-model.md
:start-after: % begin spec-datasets
:end-before: % end spec-datasets
:::

(storage-datasets-a-store-at-a-glance)=
### A store at a glance

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
### Element types

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
### Root group

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
### Element type groups

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
### Element groups and names

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
### Identifying an element

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
### Non-Zarr payloads

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

(storage-spatial-elements)=
## Spatial elements

:::{include} data-model.md
:start-after: % begin spec-spatial-elements
:end-before: % end spec-spatial-elements
:::

(storage-spatial-elements-axes)=
### Axes

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

(storage-images)=
### Images

:::{include} data-model.md
:start-after: % begin spec-images
:end-before: % end spec-images
:::

An image element is an [NGFF multiscale image](https://ngff.openmicroscopy.org/0.5/index.html#multiscale-md)
stored in `images/<name>`, with the axis restrictions and additional attributes listed here.
Everything not mentioned (array layout, chunking, codecs, pyramid construction) is governed by
[NGFF](https://ngff.openmicroscopy.org/specifications/index.html) and [Zarr](https://zarr-specs.readthedocs.io/).

(storage-images-layout)=
#### Layout

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
#### Attributes

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
#### Arrays

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

(storage-labels)=
### Labels

:::{include} data-model.md
:start-after: % begin spec-labels
:end-before: % end spec-labels
:::

{bdg-primary}`raster 0.3` {bdg-light}`Zarr v3` · {bdg-secondary}`raster 0.2, 0.1` {bdg-light}`Zarr v2`

A labels element is stored in `labels/<name>` as an NGFF multiscale image with
[image-label](https://ngff.openmicroscopy.org/0.5/index.html#labels-md) metadata.

Everything in {ref}`Images <spec-images>` applies, with the following differences.

(storage-labels-attributes)=
#### Attributes

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
#### Arrays

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

(storage-points)=
### Points

:::{include} data-model.md
:start-after: % begin spec-points
:end-before: % end spec-points
:::

{bdg-primary}`points 0.2` {bdg-light}`Zarr v3` · {bdg-secondary}`points 0.1` {bdg-light}`Zarr v2`

A points element is stored in `points/<name>` as a Zarr group whose attributes hold the
SpatialData metadata and whose payload is a partitioned Parquet dataset with one row per point.
This layout is designed for large tables (10⁶ to 10⁹ rows) and lazy, partition-wise reading.

(storage-points-layout)=
#### Layout

```text
points/<name>/
├── zarr.json              encoding-type, axes, coordinateTransformations, spatialdata_attrs
└── points.parquet/        Parquet dataset (directory)
    ├── part.0.parquet
    └── part.1.parquet ...
```

(storage-points-attributes)=
#### Attributes

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
#### Payload: points.parquet/

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

(storage-shapes)=
### Shapes

:::{include} data-model.md
:start-after: % begin spec-shapes
:end-before: % end spec-shapes
:::

{bdg-primary}`shapes 0.3` {bdg-light}`Zarr v3` · {bdg-secondary}`shapes 0.2` {bdg-light}`Zarr v2` · {bdg-secondary}`shapes 0.1` {bdg-light}`legacy`

A shapes element is stored in `shapes/<name>` as a Zarr group whose attributes hold the SpatialData
metadata and whose payload is one [GeoParquet](https://geoparquet.org/releases/v1.0.0/) file with
one row per instance.

(storage-shapes-layout)=
#### Layout

```text
shapes/<name>/
├── zarr.json          encoding-type, axes, coordinateTransformations, spatialdata_attrs
└── shapes.parquet     GeoParquet 1.0.0
```

(storage-shapes-attributes)=
#### Attributes

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
#### Payload: shapes.parquet

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

(storage-coordinate-systems)=
## Coordinate systems and transformations

:::{include} data-model.md
:start-after: % begin spec-coordinate-systems
:end-before: % end spec-coordinate-systems
:::

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
### Encoding

:::{warning}
**Divergence from NGFF.** `spatialdata` was created when NGFF 0.4 was current, and it needed
coordinate systems and transformations, which were being specified in NGFF RFC-5. RFC-5 was expected
to be part of the next NGFF release, so `spatialdata` built on a draft of it and marked raster
elements with the version string `"0.4-dev-spatialdata"`. NGFF 0.5 was released without RFC-5;
`spatialdata` adopted NGFF 0.5 but kept its draft encoding of transformations, hence
`"0.5-dev-spatialdata"`. RFC-5 has evolved since, so the encoding below differs from RFC-5 as it
has been released in NGFF 0.6 (see {doc}`ngff-compatibility`). Compared with NGFF:

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
### Where the list lives

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
### Transformation types

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

## Instances and identifiers

:::{include} data-model.md
:start-after: % begin spec-instances
:end-before: % end spec-instances
:::

(storage-tables)=
## Annotation tables

:::{include} data-model.md
:start-after: % begin spec-tables
:end-before: % end spec-tables
:::

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
### Layout

```text
tables/<name>/
├── zarr.json          anndata encoding + region, region_key, instance_key, version
├── X/  obs/  var/  layers/  obsm/  obsp/  varm/  varp/  raw/     (AnnData)
└── uns/
    └── spatialdata_attrs/      region, region_key, instance_key   (copy, see below)
```

(storage-tables-attributes)=
### Attributes

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
### Annotation rules

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
### The uns/spatialdata_attrs copy

The same three keys are also stored inside the table as the AnnData `uns["spatialdata_attrs"]`
mapping (`region`, `region_key`, `instance_key`), because `spatialdata` keeps them there in memory
and AnnData serialises `uns` as-is. Writers **MUST** keep the two copies equal. Readers **MAY** use
either; implementations that do not parse `uns` **SHOULD** use the group attributes.

(storage-tables-naming)=
### Naming

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

## Notes

% the footnotes are rendered here, at the end of the page

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

```{toctree}
:hidden: true

Version history <storage-format-versions>
```
