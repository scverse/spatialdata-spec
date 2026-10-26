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

This page covers every version of the storage format, 0.1 to 0.5. Where versions differ, synced
tabs show them, newest first, labelled with the storage format versions they apply to; storage
format 0.5 is shown by default. The versions and what each contains are listed in
{ref}`storage-versions`. On the website, each version has a page of its own, without tabs.

(storage-intro-reading-this-specification)=
## Reading this specification

- The key words MUST, MUST NOT, SHOULD, SHOULD NOT and MAY are to be
  interpreted as described in [RFC 2119](https://www.rfc-editor.org/rfc/rfc2119). The parts taken
  from the data model use no key words.
- Boxes labelled *Implementation note* are not normative; they help with understanding and
  implementing. Boxes labelled *Divergence from NGFF* flag places where a valid SpatialData store
  is not a valid NGFF store.

::::{tab-set}
:sync-group: storage-version
:::{tab-item} Storage format 0.5
:sync: sf-0.5
:selected:

- "Attributes" of a Zarr group means the `attributes` object of its `zarr.json`.
:::
:::{tab-item} Storage format 0.1–0.4
:sync: sf-0.1-0.4

- "Attributes" of a Zarr group means the content of its `.zattrs` file.
:::
::::

- JSON examples are abbreviated where marked with `...`.

(storage-datasets)=
## Datasets and elements

:::{include} data-model.md
:start-after: % begin spec-datasets
:end-before: % end spec-datasets
:::

(storage-datasets-layout)=
### Layout

::::{tab-set}
:sync-group: storage-version
:::{tab-item} Storage format 0.5
:sync: sf-0.5
:selected:

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
:::
:::{tab-item} Storage format 0.2–0.4
:sync: sf-0.2-0.4

```text
dataset.zarr/                       Zarr v2 group
├── .zgroup
├── .zattrs                         spatialdata_attrs.version = "0.1"
├── .zmetadata                      consolidated metadata
├── images/
│   └── <name>/                     NGFF multiscale image, axes cyx or czyx
│       ├── .zattrs                 multiscales, omero.channels, spatialdata_attrs
│       ├── 0/                      full resolution array (name given by datasets[0].path)
│       └── 1/ 2/ ...               optional downsampled levels
├── labels/
│   └── <name>/                     NGFF multiscale image with labels metadata, axes yx or zyx
├── shapes/
│   └── <name>/
│       ├── .zattrs                 encoding-type, axes, coordinateTransformations, spatialdata_attrs
│       └── shapes.parquet          single GeoParquet file: geometry [, radius] [, extra columns]
├── points/
│   └── <name>/
│       ├── .zattrs                 encoding-type, axes, coordinateTransformations, spatialdata_attrs
│       └── points.parquet/         multi-file Parquet dataset: x, y [, z] [, extra columns]
│           └── part.0.parquet
└── tables/
    └── <name>/                     AnnData Zarr + region; region_key, instance_key name obs columns
```
:::
:::{tab-item} Storage format 0.1
:sync: sf-0.1

```text
dataset.zarr/                       Zarr v2 group, without SpatialData attributes
├── .zgroup
├── .zmetadata                      consolidated metadata
├── images/
│   └── <name>/                     NGFF multiscale image, axes cyx or czyx
│       ├── .zattrs                 multiscales, omero.channels or channels_metadata
│       ├── 0/                      full resolution array (name given by datasets[0].path)
│       └── 1/ 2/ ...               optional downsampled levels
├── labels/
│   └── <name>/                     NGFF multiscale image with labels metadata, axes yx or zyx
├── shapes/
│   └── <name>/
│       ├── .zattrs                 encoding-type, axes, coordinateTransformations, spatialdata_attrs
│       ├── coords                  vertex coordinates
│       ├── offset0/ offset1 ...    ragged offsets (polygons, multipolygons)
│       ├── Index                   instance identifiers
│       └── radius                  circles only
├── points/
│   └── <name>/
│       ├── .zattrs                 encoding-type, axes, coordinateTransformations, spatialdata_attrs
│       └── points.parquet/         multi-file Parquet dataset: x, y [, z] [, extra columns]
│           └── part.0.parquet
└── tables/
    └── <name>/                     AnnData Zarr + region; region_key, instance_key name obs columns
```
:::
::::

(storage-datasets-element-types)=
### Element types

::::{tab-set}
:sync-group: storage-version
:::{tab-item} Storage format 0.2–0.5
:sync: sf-0.2-0.5
:selected:

| Type | Group | Payload | Standard reused | Section |
|------|-------|---------|-----------------|---------|
| Image | `images/<name>` | Zarr arrays | NGFF multiscales | {ref}`Images <spec-images>` |
| Labels | `labels/<name>` | Zarr arrays | NGFF multiscales + NGFF labels (`image-label` metadata) | {ref}`Labels <spec-labels>` |
| Shapes | `shapes/<name>` | `shapes.parquet` (single file) | GeoParquet | {ref}`Shapes <spec-shapes>` |
| Points | `points/<name>` | `points.parquet/` (multi-file dataset) | Parquet | {ref}`Points <spec-points>` |
| Table | `tables/<name>` | Zarr arrays | AnnData | {ref}`Tables <spec-tables>` |
:::
:::{tab-item} Storage format 0.1
:sync: sf-0.1

| Type | Group | Payload | Standard reused | Section |
|------|-------|---------|-----------------|---------|
| Image | `images/<name>` | Zarr arrays | NGFF multiscales | {ref}`Images <spec-images>` |
| Labels | `labels/<name>` | Zarr arrays | NGFF multiscales + NGFF labels (`image-label` metadata) | {ref}`Labels <spec-labels>` |
| Shapes | `shapes/<name>` | Zarr arrays (ragged arrays) | — | {ref}`Shapes <spec-shapes>` |
| Points | `points/<name>` | `points.parquet/` (multi-file dataset) | Parquet | {ref}`Points <spec-points>` |
| Table | `tables/<name>` | Zarr arrays | AnnData | {ref}`Tables <spec-tables>` |
:::
::::

The container is the Zarr hierarchy that holds all elements of one dataset. It fixes where elements
live, how they are named, and how a reader discovers the format version of the store and of each
element.

(storage-datasets-root-group)=
### Root group

::::{tab-set}
:sync-group: storage-version
:::{tab-item} Storage format 0.5
:sync: sf-0.5
:selected:

The root of a store MUST be a Zarr v3 group. Its attributes MUST contain a
`spatialdata_attrs` object:

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

`spatialdata_attrs.version`
: MUST be `"0.2"`, the version of the container format. It implies Zarr v3 for the whole
  store.

`spatialdata_attrs.spatialdata_software_version`
: MAY be present: the version of the software that wrote the store. Informational only;
  readers MUST NOT depend on it.
:::
:::{tab-item} Storage format 0.4
:sync: sf-0.4

The root of a store MUST be a Zarr v2 group. Its attributes MUST contain a
`spatialdata_attrs` object:

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

`spatialdata_attrs.version`
: MUST be `"0.1"`, the version of the container format. It implies Zarr v2 for the whole
  store.

`spatialdata_attrs.spatialdata_software_version`
: MAY be present: the version of the software that wrote the store. Informational only;
  readers MUST NOT depend on it.
:::
:::{tab-item} Storage format 0.3
:sync: sf-0.3

The root of a store MUST be a Zarr v2 group. Its attributes MUST contain a
`spatialdata_attrs` object:

```json
// dataset.zarr/.zattrs
{
  "spatialdata_attrs": {
    "version": "0.1",
    "spatialdata_software_version": "0.5.0"
  },
  "my_metadata": { "sample": "xyz" }
}
```

`spatialdata_attrs.version`
: MUST be `"0.1"`, the version of the container format. It implies Zarr v2 for the whole
  store.

`spatialdata_attrs.spatialdata_software_version`
: MAY be present: the version of the software that wrote the store. Informational only;
  readers MUST NOT depend on it.
:::
:::{tab-item} Storage format 0.2
:sync: sf-0.2

The root of a store MUST be a Zarr v2 group. Its attributes MAY contain a
`spatialdata_attrs` object:[^root-attrs]

```json
// dataset.zarr/.zattrs
{
  "spatialdata_attrs": {
    "version": "0.1",
    "spatialdata_software_version": "0.3.0"
  },
  "my_metadata": { "sample": "xyz" }
}
```

`spatialdata_attrs.version`
: MUST be `"0.1"` when present, the version of the container format. Readers MUST treat
  a store without `spatialdata_attrs` as version `"0.1"`.

`spatialdata_attrs.spatialdata_software_version`
: MAY be present: the version of the software that wrote the store. Informational only;
  readers MUST NOT depend on it.
:::
:::{tab-item} Storage format 0.1
:sync: sf-0.1

The root of a store MUST be a Zarr v2 group. It carries no SpatialData attributes: there is
no `spatialdata_attrs` object and no container format version.[^root-attrs] Readers MUST
treat a store without `spatialdata_attrs` as container format version `"0.1"`.
:::
::::

Any other root attribute is user metadata. It MUST be
JSON-serialisable and is otherwise unconstrained. A tool that reads a store and writes it again
(in place or to a new location) MUST keep root attributes it does not recognise, so that user
metadata is not lost.

::::{tab-set}
:sync-group: storage-version
:::{tab-item} Storage format 0.5
:sync: sf-0.5
:selected:

Consolidated metadata (`consolidated_metadata` in the root `zarr.json`) SHOULD be written so
that the store can be listed with one request on object storage. Readers MUST NOT require it.
:::
:::{tab-item} Storage format 0.1–0.4
:sync: sf-0.1-0.4

Consolidated metadata (`.zmetadata` in the root group) SHOULD be written so that the store
can be listed with one request on object storage. Readers MUST NOT require it. Some stores
contain `zmetadata` (without the leading dot) because of a bug in zarr-python's `FSStore`
([zarr-python#1121](https://github.com/zarr-developers/zarr-python/issues/1121)); readers that use
consolidated metadata SHOULD accept both names.
:::
::::

(storage-datasets-element-type-groups)=
### Element type groups

Elements live in fixed top-level groups named after their element type (see
{ref}`Element types <storage-datasets-element-types>`). A group MAY be absent when the dataset has no element of that type; it MAY also be present
and empty. Each group MUST be a Zarr group. Readers SHOULD ignore top-level groups and root
members with other names.

The `labels` group is itself an NGFF *labels* group and carries the list of its children:

::::{tab-set}
:sync-group: storage-version
:::{tab-item} Storage format 0.5
:sync: sf-0.5
:selected:
```json
// labels/zarr.json → attributes
{ "ome": { "labels": ["blobs_labels", "blobs_multiscale_labels"] } }
```
:::
:::{tab-item} Storage format 0.1–0.4
:sync: sf-0.1-0.4
```json
// labels/.zattrs
{ "labels": ["blobs_labels", "blobs_multiscale_labels"] }
```
:::
::::

Writers MUST keep this list in sync with the child groups. Readers SHOULD enumerate the
child groups when the storage system supports listing. Listing is not always available (for example
plain HTTP, or an S3 bucket without list permission); this is why consolidated metadata is written,
and the list in `labels` is redundant with it. When the store is not listable, readers SHOULD
use the consolidated metadata rather than the list. The other four type groups carry no attributes.

(storage-datasets-element-groups-and-names)=
### Element groups and names

Each element is one Zarr group, a direct child of its type group, named with the element name.
Element names:

- MUST NOT be empty, `.`, or `..`;
- MUST consist only of alphanumeric characters (Unicode letters and digits), `-`, `_` and `.`;
  whitespace and `/` are therefore excluded;
- MUST NOT start with `__`;
- MUST be unique across all element types, as in the {ref}`data model <spec-datasets>`, and
  also when compared case-insensitively: `images/Cells` and `labels/cells` MUST NOT coexist.
  This keeps stores portable to case-insensitive file systems.

The same rules apply to column names of `obs` and `var`, and to keys of `obsm`, `obsp`, `varm`,
`varp`, `uns` and `layers` in tables (see {ref}`Tables <spec-tables>`).

::::{tab-set}
:sync-group: storage-version
:::{tab-item} Storage format 0.1–0.2
:sync: sf-0.1-0.2

Stores of this version may contain names that break these rules.[^name-rules] Readers SHOULD
accept them; a writer that adds elements to such a store MUST follow the rules for the new
elements.
:::
::::

(storage-datasets-element-type-and-version)=
### Element type and version

A reader MAY take an element's type from the name of its parent group, but it SHOULD
determine the type and the format version from the element's own metadata, as listed below
(attribute paths are relative to the element group's attributes):

::::{tab-set}
:sync-group: storage-version
:::{tab-item} Storage format 0.5
:sync: sf-0.5
:selected:

| Element type | Type marker | Version location | Version |
|--------------|-------------|------------------|---------|
| images | `ome.multiscales`, without `ome.image-label` | `spatialdata_attrs.version` | `"0.3"` |
| labels | as images, plus `ome.image-label` | `spatialdata_attrs.version` | `"0.3"` |
| shapes | `encoding-type: "ngff:shapes"` | `spatialdata_attrs.version` | `"0.3"` |
| points | `encoding-type: "ngff:points"` | `spatialdata_attrs.version` | `"0.2"` |
| tables | `spatialdata-encoding-type: "ngff:regions_table"` | `version`, directly in the attributes (next to `encoding-type`), not inside `spatialdata_attrs` | `"0.2"` |

:::
:::{tab-item} Storage format 0.3–0.4
:sync: sf-0.3-0.4

| Element type | Type marker | Version location | Version |
|--------------|-------------|------------------|---------|
| images | `multiscales`, without `image-label` | `spatialdata_attrs.version` | `"0.2"` |
| labels | as images, plus `image-label` | `spatialdata_attrs.version` | `"0.2"` |
| shapes | `encoding-type: "ngff:shapes"` | `spatialdata_attrs.version` | `"0.2"` |
| points | `encoding-type: "ngff:points"` | `spatialdata_attrs.version` | `"0.1"` |
| tables | `spatialdata-encoding-type: "ngff:regions_table"` | `version`, directly in the attributes (next to `encoding-type`), not inside `spatialdata_attrs` | `"0.1"` |

:::
:::{tab-item} Storage format 0.2
:sync: sf-0.2

| Element type | Type marker | Version location | Version |
|--------------|-------------|------------------|---------|
| images | `multiscales`, without `image-label` | `spatialdata_attrs.version` | `"0.1"` |
| labels | as images, plus `image-label` | `spatialdata_attrs.version` | `"0.1"` |
| shapes | `encoding-type: "ngff:shapes"` | `spatialdata_attrs.version` | `"0.2"` |
| points | `encoding-type: "ngff:points"` | `spatialdata_attrs.version` | `"0.1"` |
| tables | `spatialdata-encoding-type: "ngff:regions_table"` | `version`, directly in the attributes (next to `encoding-type`), not inside `spatialdata_attrs` | `"0.1"` |

:::
:::{tab-item} Storage format 0.1
:sync: sf-0.1

| Element type | Type marker | Version location | Version |
|--------------|-------------|------------------|---------|
| images | `multiscales`, without `image-label` | none: raster elements have no `spatialdata_attrs` | `"0.1"`, with `multiscales[0].version` `"0.4"` |
| labels | as images, plus `image-label` | none: raster elements have no `spatialdata_attrs` | `"0.1"`, with `multiscales[0].version` `"0.4"` |
| shapes | `encoding-type: "ngff:shapes"` | `spatialdata_attrs.version` | `"0.1"` |
| points | `encoding-type: "ngff:points"` | `spatialdata_attrs.version` | `"0.1"` |
| tables | `spatialdata-encoding-type: "ngff:regions_table"` | `version`, directly in the attributes (next to `encoding-type`), not inside `spatialdata_attrs` | `"0.1"` |

:::
::::

(storage-datasets-versions)=
### Versions

Readers:

- A reader MUST NOT claim to have read an element whose type or version it does not implement. It
  SHOULD skip such an element, warn, and read the others.
- A reader that meets a container format version it does not know, with a major version it
  implements, MAY read the elements whose versions it implements, and SHOULD warn. It MUST NOT
  modify such a store.
- A reader MUST NOT read a store whose container format major version it does not implement: a
  new major container format version marks a store that readers of earlier ones would misread.
- A reader SHOULD ignore attributes it does not know.
- A reader SHOULD read every version of the storage format that encodes the current major version
  of the data model or the previous one.

Writers:

- A writer MUST NOT write a version it does not implement in full.
- A writer MUST write released versions by default. It MAY write a draft version when asked to
  explicitly, and then MUST mark the container format version with a `-dev` suffix.
- A writer that adds elements to an existing store MUST write them in the element versions of that
  store, or refuse.
- A writer that copies a store MUST keep root attributes it does not know.

(storage-datasets-non-zarr-payloads)=
### Non-Zarr payloads

Shapes and points store their data in Parquet files inside their element group
(`shapes.parquet`, `points.parquet/`). These are not Zarr nodes. Zarr tooling that lists the
hierarchy may warn about them; readers and validators MUST tolerate their presence and
MUST NOT treat them as Zarr arrays or groups.

:::{admonition} Implementation note
:class: implementation-note

To read a store from scratch: open the root group, read `spatialdata_attrs.version` if present, then for each
of the five type groups that exist, iterate over child groups (skipping hidden entries such as
`.zgroup` and `.zmetadata` in Zarr v2), and dispatch on the metadata of each element (see
"Element type and version"); `spatialdata.read_zarr` dispatches on the type group name instead. Read each element's `version` before parsing its payload.
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
column. Writers MUST NOT store `z` inside the geometries; GeoPandas allows it, but some GeoPandas
operations are incompatible with it, so it is not part of the format.

Only these four axis names exist. `c` has NGFF type `channel`; `x`, `y`, `z` have type `space`. No
other axis names or types (such as `time`) are allowed. Coordinates
along `x`, `y`, `z` are real numbers in the same unit within one coordinate system.

:::{admonition} Divergence from NGFF
:class: ngff-divergence

NGFF allows other axes, such as `time`, and custom axis types. SpatialData does not support them, so a valid NGFF image with such axes is not a valid SpatialData raster element.
:::

For raster elements, the storage format does not fix whether the integer coordinate `i` is the
centre or the corner of pixel `i`.[^pixel-centre] Shapes and points store coordinates directly.

(storage-images)=
### Images

:::{include} data-model.md
:start-after: % begin spec-images
:end-before: % end spec-images
:::

{bdg-primary}`raster 0.3` {bdg-light}`Zarr v3` · {bdg-secondary}`raster 0.2, 0.1` {bdg-light}`Zarr v2`

::::{tab-set}
:sync-group: storage-version
:::{tab-item} Storage format 0.5
:sync: sf-0.5
:selected:

An image element is an [NGFF 0.5 multiscale image](https://ngff.openmicroscopy.org/0.5/index.html#multiscale-md)
stored in `images/<name>`, with the axis restrictions and additional attributes listed here.
Everything not mentioned (array layout, chunking, codecs, pyramid construction) is governed by
[NGFF 0.5](https://ngff.openmicroscopy.org/0.5/index.html) and [Zarr](https://zarr-specs.readthedocs.io/).
:::
:::{tab-item} Storage format 0.1–0.4
:sync: sf-0.1-0.4

An image element is an [NGFF 0.4 multiscale image](https://ngff.openmicroscopy.org/0.4/index.html#multiscale-md)
stored in `images/<name>`, with the axis restrictions and additional attributes listed here.
Everything not mentioned (array layout, chunking, codecs, pyramid construction) is governed by
[NGFF 0.4](https://ngff.openmicroscopy.org/0.4/index.html) and [Zarr](https://zarr-specs.readthedocs.io/).
:::
::::

(storage-images-layout)=
#### Layout

::::{tab-set}
:sync-group: storage-version
:::{tab-item} Storage format 0.5
:sync: sf-0.5
:selected:

```text
images/<name>/
├── zarr.json          multiscales, omero, spatialdata_attrs
├── s0/                level 0: full resolution, shape (c, y, x) or (c, z, y, x)
└── s1/                optional coarser levels ...
```
:::
:::{tab-item} Storage format 0.1–0.4
:sync: sf-0.1-0.4

```text
images/<name>/
├── .zattrs            multiscales, omero, spatialdata_attrs
├── 0/                 level 0: full resolution, shape (c, y, x) or (c, z, y, x)
└── 1/                 optional coarser levels ...
```
:::
::::

- **Names.** Each level's array is found through `multiscales[0].datasets[*].path`. As in NGFF,
  `path` is any string giving the array's location relative to the image group; the names carry no
  meaning. Readers MUST resolve arrays through `path` and MUST NOT assume a naming scheme.
- **Order.** Levels are ordered by their position in `datasets`, from the highest resolution to the
  lowest, as NGFF requires; the resolution of each level is given by its `scale` (see `datasets`
  below).

:::::{admonition} Implementation note
:class: implementation-note

::::{tab-set}
:sync-group: storage-version
:::{tab-item} Storage format 0.4–0.5
:sync: sf-0.4-0.5
:selected:

Stores of this version use two naming schemes: `0`, `1`, … and `s0`, `s1`, ….[^level-names]
:::
:::{tab-item} Storage format 0.1–0.3
:sync: sf-0.1-0.3

Stores of this version name the levels `0`, `1`, ….[^level-names]
:::
::::

:::::

(storage-images-attributes)=
#### Attributes

The examples below show the same image `my_image` (two channels, two levels);
`multiscales[0].coordinateTransformations` is specified in {ref}`Coordinate systems and transformations <spec-coordinate-systems>`
and elided here.

::::{tab-set}
:sync-group: storage-version
:::{tab-item} Storage format 0.5
:sync: sf-0.5
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
:::
:::{tab-item} Storage format 0.3–0.4
:sync: sf-0.3-0.4

Raster format 0.2, in `images/<name>/.zattrs`:

```json
{
  "multiscales": [
    {
      "datasets": [
        {
          "path": "0",
          "coordinateTransformations": [
            { "type": "scale", "scale": [1.0, 1.0, 1.0] }
          ]
        },
        {
          "path": "1",
          "coordinateTransformations": [
            { "type": "scale", "scale": [1.0, 2.0, 2.0] }
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
:::
:::{tab-item} Storage format 0.2
:sync: sf-0.2

Raster format 0.1, in `images/<name>/.zattrs`:

```json
{
  "multiscales": [
    {
      "datasets": [
        {
          "path": "0",
          "coordinateTransformations": [
            { "type": "scale", "scale": [1.0, 1.0, 1.0] }
          ]
        },
        {
          "path": "1",
          "coordinateTransformations": [
            { "type": "scale", "scale": [1.0, 2.0, 2.0] }
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
:::
:::{tab-item} Storage format 0.1
:sync: sf-0.1

Raster format 0.1, in `images/<name>/.zattrs`:

```json
{
  "multiscales": [
    {
      "datasets": [
        {
          "path": "0",
          "coordinateTransformations": [
            { "type": "scale", "scale": [1.0, 1.0, 1.0] }
          ]
        },
        {
          "path": "1",
          "coordinateTransformations": [
            { "type": "scale", "scale": [1.0, 2.0, 2.0] }
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
  }
}
```

Some stores of this version hold the channel names in a `channels_metadata` key, with the same
content as `omero`, instead of `omero`.[^channels-metadata]
:::
::::

::::{tab-set}
:sync-group: storage-version
:::{tab-item} Storage format 0.5
:sync: sf-0.5
:selected:

`ome.version`
: MUST be `"0.5-dev-spatialdata"`. The `-dev-spatialdata` suffix signals that the metadata
  follows an NGFF draft (the transformations proposal) and is not a released NGFF version.

`ome`
: Holds the NGFF metadata, as in NGFF 0.5. The keys below (`multiscales`, `omero`) are inside it.
:::
:::{tab-item} Storage format 0.3–0.4
:sync: sf-0.3-0.4

`multiscales[0].version`
: MUST be `"0.4-dev-spatialdata"`. The `-dev-spatialdata` suffix signals that the metadata
  follows an NGFF draft (the transformations proposal) and is not a released NGFF version.
:::
:::{tab-item} Storage format 0.1–0.2
:sync: sf-0.1-0.2

`multiscales[0].version`
: MUST be `"0.4"`. The metadata does not follow NGFF 0.4 in full: its transformations follow
  an NGFF draft (see {ref}`Coordinate systems and transformations <spec-coordinate-systems>`).
:::
::::

`multiscales`
: MUST contain exactly one entry.

`multiscales[0].axes`
: MUST be exactly `c, y, x` or `c, z, y, x` with types `channel`, `space`, `space`(, `space`).
  Axes carry no `unit` here; units live in the coordinate system objects of the transformations.

::::{tab-set}
:sync-group: storage-version
:::{tab-item} Storage format 0.4–0.5
:sync: sf-0.4-0.5
:selected:

`multiscales[0].datasets`
: One entry per pyramid level, ordered from full resolution to coarsest. `path` MUST be the name
  of the child array. Each entry MUST contain a `coordinateTransformations` list whose first
  entry is a `scale` with the ratio between the level-0 shape and this level's shape (`1.0` for
  `c`). It MAY be followed by a `translation`, which carries no meaning: readers MUST place
  each level using its `scale` alone.[^level-translation] Single-scale images have one dataset.
:::
:::{tab-item} Storage format 0.1–0.3
:sync: sf-0.1-0.3

`multiscales[0].datasets`
: One entry per pyramid level, ordered from full resolution to coarsest. `path` MUST be the name
  of the child array. Each entry MUST contain a `coordinateTransformations` list with exactly
  one entry, a `scale` with the ratio between the level-0 shape and this level's shape (`1.0` for
  `c`). Single-scale images have one dataset.
:::
::::

`multiscales[0].coordinateTransformations`
: MUST be present with at least one entry, as specified in {ref}`Coordinate systems and transformations <spec-coordinate-systems>`. Maps
  level-0 pixel space to named coordinate systems.

`multiscales[0].name`
: MAY be present. Informational; readers MUST NOT interpret it.[^multiscales-name]

::::{tab-set}
:sync-group: storage-version
:::{tab-item} Storage format 0.2–0.5
:sync: sf-0.2-0.5
:selected:

`omero.channels`
: SHOULD be present with one object per `c` index, in order. `label` is the channel name and
  MAY be a string or a number. Readers SHOULD fall back to `0 … n-1` when absent. Other
  `omero` fields defined by NGFF (`window`, `color`, `rdefs`, …) MAY be present and are not
  interpreted by SpatialData.
:::
:::{tab-item} Storage format 0.1
:sync: sf-0.1

`omero.channels` or `channels_metadata.channels`
: One of the two SHOULD be present with one object per `c` index, in order. `label` is the
  channel name and MAY be a string or a number. Readers MUST accept both keys and
  SHOULD prefer `omero` when both are present; they SHOULD fall back to `0 … n-1` when
  neither is. Other `omero` fields defined by NGFF (`window`, `color`, `rdefs`, …) MAY be
  present and are not interpreted by SpatialData.
:::
::::

::::{tab-set}
:sync-group: storage-version
:::{tab-item} Storage format 0.5
:sync: sf-0.5
:selected:

`spatialdata_attrs.version`
: MUST be `"0.3"`.
:::
:::{tab-item} Storage format 0.3–0.4
:sync: sf-0.3-0.4

`spatialdata_attrs.version`
: MUST be `"0.2"`.
:::
:::{tab-item} Storage format 0.2
:sync: sf-0.2

`spatialdata_attrs.version`
: MUST be `"0.1"`.
:::
:::{tab-item} Storage format 0.1
:sync: sf-0.1

`spatialdata_attrs`
: Not present: raster elements of this version carry no SpatialData attributes. The raster
  version, 0.1, follows from `multiscales[0].version` being `"0.4"`.
:::
::::

(storage-images-arrays)=
#### Arrays

- Level `0` MUST hold the full-resolution data. Every level MUST have the same number of
  dimensions, in the axes order above.
- Any numeric Zarr data type is allowed.
- Chunk shape and codecs are free. Writers SHOULD keep chunks well below 2 GiB.
- Three- or four-channel images whose channel labels are `r, g, b` (`, a`) MAY be rendered as
  RGB(A) by viewers; this is a convention, not a requirement.

:::{admonition} Implementation note
:class: implementation-note

A minimal reader needs `axes`, `datasets[*].path`, the per-level `scale` in
`datasets[*].coordinateTransformations`, `coordinateTransformations`, and `omero.channels[*].label`. Everything else in the group can be
ignored. To read only a region at a given resolution, pick the coarsest level whose scale meets the
requested resolution and compose its per-level `scale` with the element transformation.
:::

:::::{admonition} Divergence from NGFF
:class: ngff-divergence

::::{tab-set}
:sync-group: storage-version
:::{tab-item} Storage format 0.5
:sync: sf-0.5
:selected:

Relative to NGFF 0.5: the `version` string is not a released version; `axes` are restricted to
`c(z)yx` and `time` is not allowed; `multiscales[0].coordinateTransformations` uses the RFC-5-style
encoding with named output coordinate systems rather than the released `scale`/`translation`-only
form; `spatialdata_attrs` is an extension. A conforming NGFF 0.5 reader can still open the arrays
and per-level scales if it ignores the version string.
:::
:::{tab-item} Storage format 0.3–0.4
:sync: sf-0.3-0.4

Relative to NGFF 0.4: the `version` string is not a released version; `axes` are restricted to
`c(z)yx` and `time` is not allowed; `multiscales[0].coordinateTransformations` uses the RFC-5-style
encoding with named output coordinate systems rather than the released `scale`/`translation`-only
form; `spatialdata_attrs` is an extension. A conforming NGFF 0.4 reader can still open the arrays
and per-level scales if it ignores the version string.
:::
:::{tab-item} Storage format 0.1–0.2
:sync: sf-0.1-0.2

Relative to NGFF 0.4: the `version` string claims NGFF 0.4, but
`multiscales[0].coordinateTransformations` uses the RFC-5-style encoding with named output
coordinate systems rather than the `scale`/`translation`-only form of NGFF 0.4, so a conforming
NGFF 0.4 reader may reject the metadata or misread the transformations; `axes` are restricted to
`c(z)yx` and `time` is not allowed. The arrays and per-level scales are valid NGFF 0.4.
:::
::::
:::::

(storage-labels)=
### Labels

:::{include} data-model.md
:start-after: % begin spec-labels
:end-before: % end spec-labels
:::

{bdg-primary}`raster 0.3` {bdg-light}`Zarr v3` · {bdg-secondary}`raster 0.2, 0.1` {bdg-light}`Zarr v2`

::::{tab-set}
:sync-group: storage-version
:::{tab-item} Storage format 0.5
:sync: sf-0.5
:selected:

A labels element is stored in `labels/<name>` as an NGFF 0.5 multiscale image with
[image-label](https://ngff.openmicroscopy.org/0.5/index.html#labels-md) metadata.
:::
:::{tab-item} Storage format 0.1–0.4
:sync: sf-0.1-0.4

A labels element is stored in `labels/<name>` as an NGFF 0.4 multiscale image with
[image-label](https://ngff.openmicroscopy.org/0.4/index.html#labels-md) metadata.
:::
::::

Everything in {ref}`Images <spec-images>` applies, with the following differences.

(storage-labels-attributes)=
#### Attributes

::::{tab-set}
:sync-group: storage-version
:::{tab-item} Storage format 0.5
:sync: sf-0.5
:selected:

Raster format 0.3, in `labels/<name>/zarr.json` → `attributes`:

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
:::{tab-item} Storage format 0.3–0.4
:sync: sf-0.3-0.4

Raster format 0.2, in `labels/<name>/.zattrs`:

```json
{
  "multiscales": [{ "version": "0.4-dev-spatialdata", "name": "blobs_labels", "axes": [ ... ], "datasets": [ ... ], "coordinateTransformations": [ ... ] }],
  "image-label": { "version": "0.4" },
  "spatialdata_attrs": { "version": "0.2" }
}
```
:::
:::{tab-item} Storage format 0.2
:sync: sf-0.2

Raster format 0.1, in `labels/<name>/.zattrs`:

```json
{
  "multiscales": [{ "version": "0.4", "name": "blobs_labels", "axes": [ ... ], "datasets": [ ... ], "coordinateTransformations": [ ... ] }],
  "image-label": { "version": "0.4" },
  "spatialdata_attrs": { "version": "0.1" }
}
```
:::
:::{tab-item} Storage format 0.1
:sync: sf-0.1

Raster format 0.1, in `labels/<name>/.zattrs`:

```json
{
  "multiscales": [{ "version": "0.4", "name": "blobs_labels", "axes": [ ... ], "datasets": [ ... ], "coordinateTransformations": [ ... ] }],
  "image-label": { "version": "0.4" }
}
```
:::
::::

`multiscales[0].axes`
: MUST be exactly `y, x` or `z, y, x`, all of type `space`. There is no channel axis.

::::{tab-set}
:sync-group: storage-version
:::{tab-item} Storage format 0.5
:sync: sf-0.5
:selected:

`image-label`
: MUST be present, inside `ome`. `version` SHOULD be `"0.5"`. The NGFF `colors`,
  `properties` and `source` fields MAY be present; SpatialData does not write or interpret
  them.
:::
:::{tab-item} Storage format 0.1–0.4
:sync: sf-0.1-0.4

`image-label`
: MUST be present. `version` SHOULD be `"0.4"`. The NGFF `colors`, `properties` and
  `source` fields MAY be present; SpatialData does not write or interpret them. Some
  multiscale labels lack this key;[^image-label] readers SHOULD tolerate its absence.
:::
::::

`omero`
: MUST NOT be present.

The parent `labels` group lists the element in its `labels` attribute ({ref}`Datasets and elements <spec-datasets>`).

(storage-labels-arrays)=
#### Arrays

- The data type MUST be an integer type (signed or unsigned) or boolean (`False` = 0, `True` = 1).
- The array values are the instance identifiers of the {ref}`data model <spec-instances>`.
  Readers MUST NOT treat the background value `0` as an instance.
- Downsampled levels SHOULD be produced without interpolation (nearest neighbour or
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

::::{tab-set}
:sync-group: storage-version
:::{tab-item} Storage format 0.5
:sync: sf-0.5
:selected:

```text
points/<name>/
├── zarr.json              encoding-type, axes, coordinateTransformations, spatialdata_attrs
└── points.parquet/        Parquet dataset (directory)
    ├── part.0.parquet
    └── part.1.parquet ...
```
:::
:::{tab-item} Storage format 0.1–0.4
:sync: sf-0.1-0.4

```text
points/<name>/
├── .zattrs                encoding-type, axes, coordinateTransformations, spatialdata_attrs
└── points.parquet/        Parquet dataset (directory)
    ├── part.0.parquet
    └── part.1.parquet ...
```
:::
::::

(storage-points-attributes)=
#### Attributes

::::{tab-set}
:sync-group: storage-version
:::{tab-item} Storage format 0.5
:sync: sf-0.5
:selected:

In `points/<name>/zarr.json` → `attributes`:

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
:::
:::{tab-item} Storage format 0.2–0.4
:sync: sf-0.2-0.4

In `points/<name>/.zattrs`:

```json
{
  "encoding-type": "ngff:points",
  "axes": ["x", "y", "z"],
  "coordinateTransformations": [ { "type": "identity", "input": {...}, "output": { "name": "global", ... } } ],
  "spatialdata_attrs": {
    "version": "0.1",
    "feature_key": "gene",
    "instance_key": "cell"
  }
}
```
:::
:::{tab-item} Storage format 0.1
:sync: sf-0.1

In `points/<name>/.zattrs`:

```json
{
  "encoding-type": "ngff:points",
  "axes": null,
  "coordinateTransformations": [ { "type": "identity", "input": {...}, "output": { "name": "global", ... } } ],
  "spatialdata_attrs": {
    "version": "0.1",
    "feature_key": "gene",
    "instance_key": "cell"
  }
}
```
:::
::::

`encoding-type`
: MUST be `"ngff:points"`.

::::{tab-set}
:sync-group: storage-version
:::{tab-item} Storage format 0.2–0.5
:sync: sf-0.2-0.5
:selected:

`axes`
: MUST be `["x", "y"]` or `["x", "y", "z"]`, and MUST match the coordinate columns present
  in the payload.
:::
:::{tab-item} Storage format 0.1
:sync: sf-0.1

`axes`
: MAY be `null`;[^null-axes] otherwise it MUST be `["x", "y"]` or `["x", "y", "z"]`, and
  MUST match the coordinate columns present in the payload. When it is `null`, the axes are
  the coordinate columns present in the payload, in the order `x`, `y`, `z`.
:::
::::

`coordinateTransformations`
: MUST be present with at least one entry ({ref}`Coordinate systems and transformations <spec-coordinate-systems>`). Input axes are in the
  order given by `axes`.

::::{tab-set}
:sync-group: storage-version
:::{tab-item} Storage format 0.5
:sync: sf-0.5
:selected:

`spatialdata_attrs.version`
: MUST be `"0.2"`.
:::
:::{tab-item} Storage format 0.1–0.4
:sync: sf-0.1-0.4

`spatialdata_attrs.version`
: MUST be `"0.1"`.
:::
::::

`spatialdata_attrs.feature_key`
: MAY be present. Name of the column that holds the feature each point measures (e.g. a gene or
  protein identifier). When present, the column SHOULD exist and SHOULD be dictionary
  encoded (categorical).

`spatialdata_attrs.instance_key`
: MAY be present. Name of the column that holds the identifier of the instance each point belongs
  to (e.g. a cell). The format does not define which element those identifiers refer to.

(storage-points-payload-points-parquet)=
#### Payload: points.parquet/

A directory containing one or more Parquet files named `part.<i>.parquet`. Readers MUST
concatenate all parts in ascending `<i>` order. All parts MUST share one schema.

Coordinate columns
: `x` and `y` MUST be present; `z` MUST be present when `axes` lists it. Type MUST be
  `int32`, `int64`, `float32` or `float64`.

Other columns
: MAY be present with any Parquet type. Column names follow the naming rules in
  {ref}`Datasets and elements <spec-datasets>`.

Row index
: Writers MUST store the dataframe index as a column referenced from the `pandas.index_columns`
  schema metadata. Its values are the
  row identifiers, the instance identifiers of the {ref}`data model <spec-instances>`; readers
  MUST use them, not row positions, and MUST NOT treat the column as data. Row identifiers
  MUST be unique within the element.[^points-index]

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

::::{tab-set}
:sync-group: storage-version
:::{tab-item} Storage format 0.2–0.5
:sync: sf-0.2-0.5
:selected:

A shapes element is stored in `shapes/<name>` as a Zarr group whose attributes hold the SpatialData
metadata and whose payload is one [GeoParquet](https://geoparquet.org/) file with one row per
instance.
:::
:::{tab-item} Storage format 0.1
:sync: sf-0.1

A shapes element is stored in `shapes/<name>` as a Zarr group whose attributes hold the SpatialData
metadata and whose arrays hold the geometries in the ragged-array layout of
[shapely](https://shapely.readthedocs.io/en/stable/reference/shapely.to_ragged_array.html), with
one instance per geometry.
:::
::::

(storage-shapes-layout)=
#### Layout

::::{tab-set}
:sync-group: storage-version
:::{tab-item} Storage format 0.5
:sync: sf-0.5
:selected:

```text
shapes/<name>/
├── zarr.json          encoding-type, axes, coordinateTransformations, spatialdata_attrs
└── shapes.parquet     GeoParquet
```
:::
:::{tab-item} Storage format 0.2–0.4
:sync: sf-0.2-0.4

```text
shapes/<name>/
├── .zattrs            encoding-type, axes, coordinateTransformations, spatialdata_attrs
└── shapes.parquet     GeoParquet
```
:::
:::{tab-item} Storage format 0.1
:sync: sf-0.1

```text
shapes/<name>/
├── .zattrs           encoding-type, axes, coordinateTransformations, spatialdata_attrs
├── coords            vertex coordinates
├── offset0           offsets (polygons and multipolygons only)
├── offset1 ...
├── Index             instance identifiers
└── radius            circles only
```
:::
::::

(storage-shapes-attributes)=
#### Attributes

::::{tab-set}
:sync-group: storage-version
:::{tab-item} Storage format 0.5
:sync: sf-0.5
:selected:

In `shapes/<name>/zarr.json` → `attributes`:

```json
{
  "encoding-type": "ngff:shapes",
  "axes": ["x", "y"],
  "coordinateTransformations": [ { "type": "identity", "input": {...}, "output": { "name": "global", ... } } ],
  "spatialdata_attrs": { "version": "0.3" }
}
```
:::
:::{tab-item} Storage format 0.2–0.4
:sync: sf-0.2-0.4

In `shapes/<name>/.zattrs`:

```json
{
  "encoding-type": "ngff:shapes",
  "axes": ["x", "y"],
  "coordinateTransformations": [ { "type": "identity", "input": {...}, "output": { "name": "global", ... } } ],
  "spatialdata_attrs": { "version": "0.2" }
}
```
:::
:::{tab-item} Storage format 0.1
:sync: sf-0.1

In `shapes/<name>/.zattrs`:

```json
{
  "encoding-type": "ngff:shapes",
  "axes": null,
  "coordinateTransformations": [ { "type": "identity", "input": {...}, "output": { "name": "global", ... } } ],
  "spatialdata_attrs": { "version": "0.1", "geos": { "name": "POLYGON", "type": 3 } }
}
```
:::
::::

`encoding-type`
: MUST be `"ngff:shapes"`.

::::{tab-set}
:sync-group: storage-version
:::{tab-item} Storage format 0.2–0.5
:sync: sf-0.2-0.5
:selected:

`axes`
: MUST be `["x", "y"]`, or `["x", "y", "z"]` if and only if the payload has a `z` column
  (2.5D shapes).
:::
:::{tab-item} Storage format 0.1
:sync: sf-0.1

`axes`
: MAY be `null`;[^null-axes] otherwise it MUST be `["x", "y"]`. Shapes of this version
  are 2D: their axes are `x, y`.
:::
::::

`coordinateTransformations`
: MUST be present with at least one entry ({ref}`Coordinate systems and transformations <spec-coordinate-systems>`). Input axes are `x, y` in
  this order.

::::{tab-set}
:sync-group: storage-version
:::{tab-item} Storage format 0.5
:sync: sf-0.5
:selected:

`spatialdata_attrs.version`
: MUST be `"0.3"`.
:::
:::{tab-item} Storage format 0.2–0.4
:sync: sf-0.2-0.4

`spatialdata_attrs.version`
: MUST be `"0.2"`.
:::
:::{tab-item} Storage format 0.1
:sync: sf-0.1

`spatialdata_attrs.version`
: MUST be `"0.1"`.

`spatialdata_attrs.geos`
: MUST be present: the geometry type of all rows, with `name` the GEOS geometry type name
  (`"POINT"`, `"POLYGON"` or `"MULTIPOLYGON"`) and `type` its integer code (`0`, `3` or `6`).
:::
::::

(storage-shapes-payload)=
#### Payload

::::::{tab-set}
:sync-group: storage-version
:::::{tab-item} Storage format 0.2–0.5
:sync: sf-0.2-0.5
:selected:

`shapes.parquet` is a single GeoParquet file. The GeoParquet `geo` metadata MUST be present with
`primary_column: "geometry"`.

::::{tab-set}
:sync-group: storage-version
:::{tab-item} Storage format 0.4–0.5
:sync: sf-0.4-0.5
:selected:

`geometry`
: MUST be present. Encoding MUST be `WKB` or the GeoArrow native encoding as defined by
  GeoParquet 1.1; writers default to WKB, readers MUST support WKB and SHOULD support
  GeoArrow.[^geoarrow] `crs` MUST be `null`: coordinates are in the element's intrinsic
  coordinate system, not in a geographic reference system. Geometries MUST be 2D. Readers
  SHOULD accept geometries with z coordinates and axes `x, y, z`.[^shapes-z]
:::
:::{tab-item} Storage format 0.2–0.3
:sync: sf-0.2-0.3

`geometry`
: MUST be present. Encoding MUST be `WKB`. `crs` MUST be `null`: coordinates are in the
  element's intrinsic coordinate system, not in a geographic reference system. Geometries MUST
  be 2D.
:::
::::

Geometry types
: All rows MUST be `Point`, or all rows MUST be `Polygon` or `MultiPolygon` (the two may
  be mixed). Other geometry types are not allowed.

`radius`
: MUST be present when the geometries are `Point`, and MUST NOT be present otherwise. A
  numeric column; every value MUST be finite and strictly positive. A point plus a radius is a
  circle; the radius is expressed in the same units as the coordinates and is scaled by the
  coordinate transformation.

`z`
: MAY be present: a numeric column with the z position of each geometry (2.5D shapes). When
  present, `axes` lists `z`.

Row index
: The pandas index is stored following the Parquet/pandas convention: a `RangeIndex` described only
  in the `pandas` schema metadata, or an explicit index column (typically `__index_level_0__`)
  referenced from `pandas.index_columns`. The index values are the instance identifiers of the
  {ref}`data model <spec-instances>`; they MUST be unique and MAY be integers or strings.

Other columns
: MAY be present with any Parquet type (string columns MAY be Arrow `string` or
  `large_string`). They are per-instance annotations stored with the element. Column names follow
  the naming rules in {ref}`Datasets and elements <spec-datasets>`.

The file MUST contain at least one row.[^empty-shapes]

:::{admonition} Implementation note
:class: implementation-note

Read the whole file with any GeoParquet-capable library (`geopandas`, `sf` + `arrow`, `geoarrow-js`,
…). Decide between circles and polygons by checking `geo.columns.geometry.geometry_types` or the
first geometry. Do not use `shapes.parquet` metadata to find transformations: they live only in the
Zarr group attributes.
:::
:::::
:::::{tab-item} Storage format 0.1
:sync: sf-0.1

The arrays hold the output of `shapely.to_ragged_array` for the geometries of all rows:

`coords`
: MUST be present: a float array of shape `(n_vertices, 2)` with the `x, y` coordinates of all
  vertices (of the centres, for circles).

`offset0`, `offset1`, …
: MUST be present for polygons and multipolygons, and MUST NOT be present for circles:
  the offset arrays of the ragged-array layout, in order (`offset0` into `coords`, each following
  one into the previous one): two for polygons, three for multipolygons.

`Index`
: MUST be present: one value per row, the instance identifiers of the
  {ref}`data model <spec-instances>`. They MUST be unique and MAY be integers or strings
  (variable-length UTF-8).

`radius`
: MUST be present for circles (`geos.name` is `"POINT"`), and MUST NOT be present
  otherwise: one numeric value per row, finite and strictly positive. A point plus a radius is a
  circle; the radius is expressed in the same units as the coordinates and is scaled by the
  coordinate transformation.

All rows MUST have the geometry type given by `geos`. No other columns are stored. The element
MUST contain at least one row.[^empty-shapes]
:::::
::::::

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

The intrinsic coordinate system is never named, on disk or in memory.

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

::::::{warning}
::::{tab-set}
:sync-group: storage-version
:::{tab-item} Storage format 0.5
:sync: sf-0.5
:selected:

**Divergence from NGFF.** SpatialData was created when NGFF 0.4 was current, and it needed
coordinate systems and transformations, which were being specified in NGFF RFC-5. RFC-5 was
expected to be part of the next NGFF release, so SpatialData built on a draft of it. NGFF 0.5 was
released without RFC-5; this storage format follows NGFF 0.5 but keeps the draft encoding of
transformations, and marks raster elements with the version string `"0.5-dev-spatialdata"`.

Compared with NGFF:

- NGFF 0.5 allows only `scale` and `translation`, only on raster data, and references no named
  coordinate systems;
- compared with [RFC-5](https://ngff.openmicroscopy.org/rfc/5/), as released in NGFF 0.6, `input`
  and `output` are inlined coordinate system objects instead of names referencing a
  `coordinateSystems` list, and the same encoding is applied to shapes and points.
:::
:::{tab-item} Storage format 0.3–0.4
:sync: sf-0.3-0.4

**Divergence from NGFF.** SpatialData was created when NGFF 0.4 was current, and it needed
coordinate systems and transformations, which were being specified in NGFF RFC-5. RFC-5 was
expected to be part of the next NGFF release, so SpatialData built on a draft of it. This storage format
follows NGFF 0.4 with the draft encoding of transformations, and marks raster elements with the
version string `"0.4-dev-spatialdata"`.

Compared with NGFF:

- NGFF 0.4 allows only `scale` and `translation`, only on raster data, and references no named
  coordinate systems;
- compared with [RFC-5](https://ngff.openmicroscopy.org/rfc/5/), as released in NGFF 0.6, `input`
  and `output` are inlined coordinate system objects instead of names referencing a
  `coordinateSystems` list, and the same encoding is applied to shapes and points.
:::
:::{tab-item} Storage format 0.1–0.2
:sync: sf-0.1-0.2

**Divergence from NGFF.** SpatialData was created when NGFF 0.4 was current, and it needed
coordinate systems and transformations, which were being specified in NGFF RFC-5. RFC-5 was
expected to be part of the next NGFF release, so SpatialData built on a draft of it. This storage format
follows NGFF 0.4 with the draft encoding of transformations, but marks raster elements with the
version string `"0.4"` of the released NGFF.

Compared with NGFF:

- NGFF 0.4 allows only `scale` and `translation`, only on raster data, and references no named
  coordinate systems;
- compared with [RFC-5](https://ngff.openmicroscopy.org/rfc/5/), as released in NGFF 0.6, `input`
  and `output` are inlined coordinate system objects instead of names referencing a
  `coordinateSystems` list, and the same encoding is applied to shapes and points.
:::
::::
::::::

:::{admonition} Implementation note
:class: implementation-note

Because the encoding diverges from NGFF, generic OME-Zarr libraries cannot read these
transformations. In practice, an implementation can:

1. rely on `spatialdata` (Python) to read and write them;
2. outside Python, validate against the JSON schemas listed in
   {doc}`Examples and validation <storage-format-conformance>`, where they exist for this version.
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
: MUST be one of the types below.

`input`
: MUST be a coordinate system object describing the element's own axes, in storage order. Its
  `name` carries no meaning (writers use the concatenated axis names, e.g. `"cyx"`); readers
  MUST NOT rely on it.

`output`
: MUST be a coordinate system object. Its `name` is the name of the target coordinate system.
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

 Writers that do not know the physical unit MUST write the placeholder
string `"unit"`; readers MUST accept any string here.

:::{admonition} Implementation note
:class: implementation-note

In memory, the Python `spatialdata` framework does not use coordinate system objects: it keeps only
the `output.name` of each transformation, which is sufficient for this storage format.
:::

Within one `coordinateTransformations` list, `output.name` values MUST be unique, since an
element has at most one transformation to each named coordinate system. [^unique-cs] The list MUST contain at least one entry. When no
alignment information exists, writers SHOULD map the element to `"global"` with an `identity`
transformation. Coordinate system names follow the same rules as element names
({ref}`Datasets and elements <spec-datasets>`).

The list is stored in the element group:

::::{tab-set}
:sync-group: storage-version
:::{tab-item} Storage format 0.5
:sync: sf-0.5
:selected:

| Element | Location |
|---------|----------|
| images, labels | `ome.multiscales[0].coordinateTransformations` |
| shapes, points | group attribute `coordinateTransformations` |
:::
:::{tab-item} Storage format 0.1–0.4
:sync: sf-0.1-0.4

| Element | Location |
|---------|----------|
| images, labels | `multiscales[0].coordinateTransformations` |
| shapes, points | group attribute `coordinateTransformations` |
:::
::::

Raster elements additionally carry the NGFF per-level transformations in
`multiscales[0].datasets[i].coordinateTransformations` (a `scale` per pyramid level, relative to
level `0`). To place a pixel of level `i` into a named coordinate system, a reader MUST apply the
level's `scale` first, then the SpatialData transformation. See {ref}`Images <spec-images>`.

(storage-coordinate-systems-transformation-types)=
### Transformation types

All arrays and matrices are ordered like the `input.axes` (and `output.axes`) they refer to, and
MUST cover every input axis of the element. Axes that a transformation does not affect (typically
`c`) are written explicitly with a neutral value (`1.0` for scale, `0.0` for translation).

Each transformation maps a point `p` with coordinates on its input axes to a point `q` with
coordinates on its output axes. `p[a]` is the coordinate of `p` on the axis named `a`:

| Type | Definition |
|------|------------|
| `identity` | `q[a] = p[a]` for every axis `a` |
| `scale` | `q[a] = s[a] · p[a]`, where `s[a]` is the entry of `scale` for axis `a` |
| `translation` | `q[a] = p[a] + t[a]`, where `t[a]` is the entry of `translation` for axis `a` |
| `affine` | `q = A · p + b`, where `A` is `affine` without its last column, with one row per output axis in the order of `output.axes` and one column per input axis in the order of `input.axes`, and `b` is the last column |
| `mapAxis` | `q[k] = p[mapAxis[k]]` if `k` is a key, otherwise `q[k] = p[k]` |
| `sequence` | `q = Tₙ(… T₂(T₁(p)))`, where `T₁, …, Tₙ` are the entries of `transformations` in order: the first entry is applied first. `T₁` takes the outer `input.axes` and `Tₙ` produces the outer `output.axes` |

Scale factors and affine matrices are not restricted: a negative factor mirrors an axis, and a zero
factor or a singular matrix is valid but has no inverse; readers MAY fail on operations that need
the inverse. The `c` entries SHOULD be neutral: scale `1`, translation `0`, identity row and column
in `affine`, `c` mapped to `c`. Readers MAY ignore the `c` entries of a transformation.

:::{admonition} Implementation note
:class: implementation-note

`spatialdata` accepts zero and negative scale factors and singular affine matrices when setting,
writing and reading transformations; `get_extent` and transforming points work with them.
`spatialdata.transform` of a raster element uses the inverse and fails for a zero scale factor or a
singular matrix. `spatialdata` does not check how a transformation treats `c`: points have no `c`,
`get_extent` ignores it, and `spatialdata.transform` of an image resamples the array along `c` too,
so a transformation whose `c` entries are not neutral mixes or shifts channels.
:::

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
the translation. The homogeneous row `[0, ..., 0, 1]` is omitted. Output axes MAY differ in
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
fields, `input` and `output`; the inner `input.name` and `output.name` MUST be ignored by readers
and only the axes used. The output axes of entry *i* MUST equal the input axes of entry *i+1*.
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

No other transformation types are part of the storage format. In particular,
`rotation`, `byDimension`, `inverseOf`, `bijection`, `coordinates` and `displacements`, defined by
NGFF RFC-5, are not supported.[^other-types]

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
`string-array` arrays before); readers MUST support the encodings of the AnnData specification
version they claim.

(storage-tables-layout)=
### Layout

::::{tab-set}
:sync-group: storage-version
:::{tab-item} Storage format 0.5
:sync: sf-0.5
:selected:

```text
tables/<name>/
├── zarr.json          anndata encoding + region, region_key, instance_key, version
├── X/  obs/  var/  layers/  obsm/  obsp/  varm/  varp/  raw/     (AnnData)
└── uns/
    └── spatialdata_attrs/      region, region_key, instance_key   (copy, see below)
```
:::
:::{tab-item} Storage format 0.2–0.4
:sync: sf-0.2-0.4

```text
tables/<name>/
├── .zattrs            anndata encoding + region, region_key, instance_key, version
├── X/  obs/  var/  layers/  obsm/  obsp/  varm/  varp/  raw/     (AnnData)
└── uns/
    └── spatialdata_attrs/      region, region_key, instance_key   (copy, see below)
```
:::
:::{tab-item} Storage format 0.1
:sync: sf-0.1

```text
tables/<name>/
├── .zattrs            anndata encoding + region, region_key, instance_key, version
├── X/  obs/  var/  layers/  obsm/  obsp/  varm/  varp/  raw/     (AnnData)
└── uns/
    └── spatialdata_attrs/      region, region_key, instance_key   (copy, see below)
```

Some stores of this version hold a single table in the group `table/table` instead of
`tables/<name>`.[^single-table] Readers SHOULD read it as a table named `table`.
:::
::::

(storage-tables-attributes)=
### Attributes

The group attributes are the AnnData ones plus five SpatialData keys at the same level:

::::{tab-set}
:sync-group: storage-version
:::{tab-item} Storage format 0.5
:sync: sf-0.5
:selected:

In `tables/<name>/zarr.json` → `attributes`:

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
:::
:::{tab-item} Storage format 0.1–0.4
:sync: sf-0.1-0.4

In `tables/<name>/.zattrs`:

```json
{
  "encoding-type": "anndata",
  "encoding-version": "0.1.0",
  "spatialdata-encoding-type": "ngff:regions_table",
  "region": ["cells_labels", "nuclei_shapes"],
  "region_key": "region",
  "instance_key": "instance_id",
  "version": "0.1"
}
```
:::
::::

`spatialdata-encoding-type`
: MUST be `"ngff:regions_table"`.

::::{tab-set}
:sync-group: storage-version
:::{tab-item} Storage format 0.5
:sync: sf-0.5
:selected:

`version`
: MUST be `"0.2"`. Note that, unlike other element types, the version is a top-level attribute
  and not nested under `spatialdata_attrs`.
:::
:::{tab-item} Storage format 0.1–0.4
:sync: sf-0.1-0.4

`version`
: MUST be `"0.1"`. Note that, unlike other element types, the version is a top-level attribute
  and not nested under `spatialdata_attrs`.
:::
::::

`region`
: A string, a list of strings, or `null`. The name(s) of the elements this table annotates. Each
  name SHOULD be a labels, shapes or points element in the same store. Readers MUST NOT
  reject a table whose `region` names an absent element, and MAY warn.

`region_key`
: A string or `null`. Name of the `obs` column that states, for each row, which element in
  `region` it annotates.

`instance_key`
: A string or `null`. Name of the `obs` column that holds the instance identifier within that
  element.

`region`, `region_key` and `instance_key` MUST either all be `null` (a table that annotates
nothing) or all be non-null.

The same three keys are also stored inside the table as the AnnData `uns["spatialdata_attrs"]`
mapping (`region`, `region_key`, `instance_key`), because AnnData serialises `uns` as-is and in-memory
implementations keep them there.[^uns-copy] Writers MUST keep the two copies equal. Readers MAY use
either; implementations that do not parse `uns` SHOULD use the group attributes.

(storage-tables-annotation-rules)=
### Annotation rules

When the table annotates elements:

- `obs[region_key]` MUST be a categorical column whose set of values equals `region`.
- `obs[instance_key]` MUST NOT contain nulls. For labels elements the values are the integer
  label values; for shapes and points they are the row index values of the payload, with matching
  type.
- Each pair `(obs[region_key], obs[instance_key])` MUST be unique: each instance is referenced
  by at most one row.
- Readers SHOULD match rows to instances by identifier, and tolerate instances without a row
  and dangling references.
- Tables MUST NOT carry coordinate transformations.

```text
tables/cells                          labels/cells_labels   shapes/nuclei_shapes
obs.region      obs.instance_id       (pixel values)        (row index)
cells_labels    1        ──────────▶  1
cells_labels    2        ──────────▶  2
nuclei_shapes   "n_07"   ────────────────────────────────▶  "n_07"
```

(storage-tables-naming)=
### Naming

`obs` and `var` column names and the keys of `obsm`, `obsp`, `varm`, `varp`, `uns` and `layers`
MUST follow the element naming rules of {ref}`Datasets and elements <spec-datasets>`. `_index` is reserved by AnnData and
MUST NOT be used as a column name.

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

[^root-attrs]: `spatialdata` writes the root `spatialdata_attrs` from release 0.3.0.
[^name-rules]: `spatialdata` checks element names from release 0.2.0 (alphanumeric characters,
    `_` and `-`) and applies the rules above, including case-insensitive uniqueness, from release
    0.3.0.
[^pixel-centre]: `spatialdata` is not consistent here: `spatialdata.transform` treats `(0, 0)` as
    the centre of the first pixel (the NGFF convention), while parts of rasterization treat it as a
    corner. This is a known bug and legacy behaviour
    ([scverse/spatialdata#165](https://github.com/scverse/spatialdata/issues/165)).
[^unique-cs]: The JSON schemas of SpatialData.validate do not check this. `spatialdata` writes unique
    names by construction (it keeps transformations in a mapping keyed by coordinate system name)
    and, when reading a list with a repeated name, keeps the last entry.
[^uns-copy]: `spatialdata` keeps the three keys in `uns["spatialdata_attrs"]` of the in-memory
    AnnData object.
[^multiscales-name]: `spatialdata` writes the group path (for example `"/images/my_image"`) for
    multiscale images. For single-scale images it leaves the name to ome-zarr-py, which writes
    `"image"` from version 0.18 ([ome-zarr-py#515](https://github.com/ome/ome-zarr-py/pull/515))
    and the group path before.
[^shapes-z]: `spatialdata` 0.8 writes them, with a warning.
[^other-types]: `spatialdata` fails to read an element that uses them, or skips the element with
    `on_bad_files="warn"`.
[^points-index]: `spatialdata` always stores the index, and names an unnamed index
    `__null_dask_index__`. A dataset without it has no usable row
    identifiers: Parquet readers such as dask number the rows of each part file from 0.
[^level-names]: `spatialdata` writes raster elements with ome-zarr-py, which names levels `0`, `1`, …
    up to version 0.13 and `s0`, `s1`, … from version 0.14
    ([ome-zarr-py#544](https://github.com/ome/ome-zarr-py/pull/544)). `spatialdata` up to 0.5
    requires zarr-python 2 and therefore ome-zarr-py 0.11 or earlier; from 0.6 it requires only a
    minimum ome-zarr-py version, so the names depend on the ome-zarr-py installed when the store
    was written.
[^channels-metadata]: `spatialdata` up to 0.1.2 writes `channels_metadata`; from 0.2.0 it writes
    `omero` and reads both.
[^image-label]: For example multiscale labels written by `spatialdata` 0.6.
[^null-axes]: `spatialdata` up to 0.2.1 writes `"axes": null` for shapes and points: ome-zarr-py
    drops the axes for the format version `"0.1"`.
[^geoarrow]: `spatialdata` writes GeoArrow on request from release 0.7.0.
[^single-table]: `spatialdata` up to 0.0.16 writes a single table in `table/table`.
[^level-translation]: ome-zarr-py ≥ 0.18, which `spatialdata` uses to write raster elements,
    writes a `translation` of `(scale − 1) / 2` after each per-level `scale`; whether a store has it
    depends on the installed ome-zarr-py. NGFF readers that apply it place downsampled levels half a
    coarse pixel away from where `spatialdata` places them.
[^empty-shapes]: Not a property of the data model: `spatialdata` infers from the first geometry
    whether an element holds circles or polygons and how many axes it has, and an empty file records
    neither. Points, labels and tables may be empty. Spatial queries in `spatialdata` drop elements
    that would become empty instead of storing them.

```{toctree}
:hidden: true

Examples and validation <storage-format-conformance>
Version history <storage-format-versions>
```
