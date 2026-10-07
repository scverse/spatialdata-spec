# Container

The container is the Zarr hierarchy that holds all elements of one dataset. It fixes where elements
live, how they are named, and how a reader discovers the format version of the store and of each
element.

## Root group

The root of a {term}`store` **MUST** be a Zarr group. Its attributes **MUST** contain a
`spatialdata_attrs` object:

::::{tab-set}
:::{tab-item} Zarr v3 (container 0.2)
:sync: v3

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
:::{tab-item} Zarr v2 (container 0.1)
:sync: v2

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
: **MUST** be present. The container {term}`format version`, currently `"0.2"`. It determines the
  Zarr format of the whole store: `"0.1"` implies Zarr v2, `"0.2"` implies Zarr v3. Stores written
  before container versioning existed have no `spatialdata_attrs`; readers **SHOULD** treat them as
  version `"0.1"`.

`spatialdata_attrs.spatialdata_software_version`
: **SHOULD** be present when written by `spatialdata`. Informational only; readers **MUST NOT**
  depend on it.

Any other root attribute is user metadata (the `SpatialData.attrs` mapping in Python). It **MUST** be
JSON-serialisable and is otherwise unconstrained. Readers **MUST** preserve unknown root attributes
when rewriting a store.

Consolidated metadata **SHOULD** be written (`consolidated_metadata` in Zarr v3, `.zmetadata` in
Zarr v2) so that the store can be listed with one request on object storage. Readers **MUST NOT**
require it.

## Element type groups

Elements live in fixed top-level groups named after their element type:

| Group | Holds | Required |
|-------|-------|----------|
| `images` | {doc}`images` | no |
| `labels` | {doc}`labels` | no |
| `shapes` | {doc}`shapes` | no |
| `points` | {doc}`points` | no |
| `tables` | {doc}`tables` | no |

A group **MAY** be absent when the dataset has no element of that type; it **MAY** also be present
and empty. Each group **MUST** be a Zarr group. Readers **SHOULD** ignore top-level groups and root
members with other names.

The `labels` group is itself an NGFF *labels* group and carries the list of its children:

::::{tab-set}
:::{tab-item} Zarr v3
:sync: v3
```json
// labels/zarr.json → attributes
{ "ome": { "labels": ["blobs_labels", "blobs_multiscale_labels"] } }
```
:::
:::{tab-item} Zarr v2
:sync: v2
```json
// labels/.zattrs
{ "labels": ["blobs_labels", "blobs_multiscale_labels"] }
```
:::
::::

Writers **SHOULD** keep this list in sync with the child groups. Readers **SHOULD** enumerate the
child groups rather than rely on the list. The other four type groups carry no attributes.

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

A reader that opens an element group determines its type from the parent group name and its
{term}`format version` from a per-type location:

| Element type | Type marker | Version location |
|--------------|-------------|------------------|
| images | parent group `images`; `ome.multiscales` present (v3) or `multiscales` (v2) | `spatialdata_attrs.version` |
| labels | parent group `labels`; additionally `ome.image-label` (v3) or `image-label` (v2) | `spatialdata_attrs.version` |
| shapes | `encoding-type: "ngff:shapes"` | `spatialdata_attrs.version` |
| points | `encoding-type: "ngff:points"` | `spatialdata_attrs.version` |
| tables | `spatialdata-encoding-type: "ngff:regions_table"` | `version` (top level of the group attributes) |

Element versions are constrained by the container version; the allowed combinations are listed in
{doc}`versions`. A reader **MUST** refuse, or warn and skip, an element whose version it does not
implement.

## Non-Zarr payloads

Shapes and points store their data in Parquet files inside their element group
(`shapes.parquet`, `points.parquet/`). These are not Zarr nodes. Zarr tooling that lists the
hierarchy **MAY** warn about them; readers and validators **MUST** tolerate their presence and
**MUST NOT** treat them as Zarr arrays or groups.

:::{admonition} Implementation note
:class: implementation-note

To read a store from scratch: open the root group, read `spatialdata_attrs.version`, then for each
of the five type groups that exist, iterate over child groups (skipping hidden entries such as
`.zgroup` and `.zmetadata` in Zarr v2), and dispatch on the type group name. Read each element's
`version` before parsing its payload. This is exactly what `spatialdata.read_zarr` does.
:::

:::{admonition} Divergence from NGFF
:class: ngff-divergence

NGFF defines no top-level layout for a collection of images, shapes, points and tables. The five
type groups, the `spatialdata_attrs` object and the `encoding-type` markers on shapes and points are
SpatialData extensions. NGFF *plate*, *well* and *bioformats2raw.layout* metadata are not used.
:::
