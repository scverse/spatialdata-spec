# Container

{bdg-primary}`spatialdata-container-format-0.2` · {bdg-secondary}`spatialdata-container-format-0.1`

The container is the Zarr hierarchy that holds all elements of one dataset. It fixes where elements
live, how they are named, and how a reader discovers the format version of the store and of each
element.

## Root group

The root of a {term}`store` **MUST** be a Zarr group. Its attributes **MUST** contain a
`spatialdata_attrs` object:

::::{tab-set}
:::{tab-item} spatialdata-container-format-0.2
:sync: container-0.2

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
: **MUST** be present. The container {term}`format version`, for example `"0.2"`; see the {ref}`compatibility-matrix`. It determines the
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

## Element type groups

Elements live in fixed top-level groups named after their element type:

| Group | Holds | Data stored as | Required |
|-------|-------|----------------|----------|
| `images` | {doc}`images` | Zarr arrays | no |
| `labels` | {doc}`labels` | Zarr arrays | no |
| `shapes` | {doc}`shapes` | Parquet (GeoParquet) | no |
| `points` | {doc}`points` | Parquet | no |
| `tables` | {doc}`tables` | Zarr (AnnData) | no |

A group **MAY** be absent when the dataset has no element of that type; it **MAY** also be present
and empty. Each group **MUST** be a Zarr group. Readers **SHOULD** ignore top-level groups and root
members with other names.

The `labels` group is itself an NGFF *labels* group and carries the list of its children:

::::{tab-set}
:::{tab-item} spatialdata-container-format-0.2
:sync: container-0.2
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

## Element groups and names

Each element is one Zarr group, a direct child of its type group, named with the element name.
Element names:

- **MUST NOT** be empty, `.`, or `..`;
- **MUST** consist only of alphanumeric characters (Unicode letters and digits), `-`, `_` and `.`;
  whitespace and `/` are therefore excluded;
- **MUST NOT** start with `__`;
- **MUST** be unique across all element types when compared case-insensitively. `images/Cells` and
  `labels/cells` **MUST NOT** coexist. This keeps stores portable to case-insensitive file systems and
  lets a name identify an element without its type.

The same rules apply to column names of `obs` and `var`, and to keys of `obsm`, `obsp`, `varm`,
`varp`, `uns` and `layers` in tables (see {doc}`tables`).

## Identifying an element

A reader **MAY** take an element's type from the name of its parent group, but it **SHOULD**
determine the type and the {term}`format version` from the element's own metadata, as listed below
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

## Non-Zarr payloads

Shapes and points store their data in Parquet files inside their element group
(`shapes.parquet`, `points.parquet/`). These are not Zarr nodes. Zarr tooling that lists the
hierarchy **MAY** warn about them; readers and validators **MUST** tolerate their presence and
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
