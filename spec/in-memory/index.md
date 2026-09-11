# In-memory formats

{bdg-success}`in-memory` {bdg-dark-line}`general` {bdg-warning-line}`draft`

An in-memory format is what one implementation exposes after reading a store: the objects, their
fields, and the invariants a tool can rely on. There is one per implementation language, and each is
documented on its own page. This page holds only what is common to all of them and the list of
implementations.

## Implementations

| Implementation | Page | Describes | Status | Discuss changes at |
|----------------|------|-----------|--------|--------------------|
| Python · `spatialdata` | {doc}`python/index` | `spatialdata` 0.8 | {bdg-dark-line}`status quo` documented | [scverse/spatialdata](https://github.com/scverse/spatialdata/issues) |
| R · `spatialdataR` | {doc}`r/index` | — | {bdg-light}`placeholder` | [HelenaLC/spatialdataR](https://github.com/HelenaLC/spatialdataR/issues) |
| JavaScript · `SpatialData.js` | {doc}`js/index` | — | {bdg-light}`placeholder` | [Taylor-CCB-Group/SpatialData.js](https://github.com/Taylor-CCB-Group/SpatialData.js/issues) |

Only topics that concern **all** implementations are discussed in this repository. Anything
specific to one language (API shape, class names, laziness strategy, dependency choices) belongs to
that implementation's repository, and its page here is updated afterwards.

## What every implementation page documents

So that pages are comparable, each implementation page answers the same questions:

1. **Object per element type.** Which native type represents images, labels, shapes, points and
   tables, and whether single- and multiscale rasters differ.
2. **Where the SpatialData metadata lives.** Transformations, table keys, points `feature_key` /
   `instance_key`, user `attrs`.
3. **Names.** Whether the element name is stored in the object (in Python it is not) and how the
   container enforces uniqueness.
4. **Validity.** The entry point that checks an object (`validate`) and the one that constructs a
   valid object from raw data (`parse`).
5. **Round trip.** Which on-disk versions are read and written, and any loss (for example, extra
   Zarr attributes that are dropped).
6. **Laziness.** Which element types are loaded lazily and what triggers loading.
7. **Version described.** The implementation release the page reflects.

## Principles common to all implementations

These follow from the {doc}`on-disk format <../on-disk/index>` and are expected to hold in every
language:

- **Elements are standard objects of the host ecosystem**, not bespoke classes: the image type is
  whatever the language uses for labelled n-dimensional arrays, the shapes type is its geodata
  frame, the table type is its AnnData equivalent.
- **The element name is external to the element.** It is the key in the container, exactly as it
  is the Zarr group name on disk.
- **Transformations are attached to the element**, keyed by coordinate system name, and are
  self-contained (no coordinate system objects) in memory.
- **Tables reference regions by name and instance identifier**; nothing else links elements.
- **Validation is explicit** and available to third-party code, so that generic tools can check
  inputs without re-implementing the rules.

:::{admonition} Open question
:class: open-question

Should this page grow into a minimal cross-language interoperability contract (a list of operations
every implementation must support, such as "read a store", "list elements", "get transformation to
coordinate system X"), or stay descriptive? Comment in
[spatialdata-spec](https://github.com/scverse/spatialdata-spec/issues) with the label
`in-memory-general`.
:::

```{toctree}
:maxdepth: 1
:hidden:

python/index
r/index
js/index
```
