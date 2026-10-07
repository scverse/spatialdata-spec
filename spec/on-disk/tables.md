# Tables

{bdg-primary}`tables 0.2` {bdg-light}`Zarr v3` · {bdg-secondary}`tables 0.1` {bdg-light}`Zarr v2`

A table element is an [AnnData](https://anndata.readthedocs.io/en/stable/fileformat-prose.html)
object stored in `tables/<name>` using the AnnData on-disk format for Zarr. It holds observations
(rows) × variables (columns) plus annotations. A table **MAY** annotate {term}`instances <instance>`
of one or more regions (labels, shapes or points elements); this is the only link
between elements that the format defines.

This chapter specifies only what SpatialData adds to AnnData. Encoding of `X`, `obs`, `var`,
`layers`, `obsm`, `obsp`, `varm`, `varp`, `uns` and `raw` is exactly as specified by AnnData and is
not repeated here. The encodings present in a store follow the `anndata` release that wrote it
(for example, string indices are `nullable-string-array` groups since `anndata` 0.13 and were
`string-array` arrays before); readers **MUST** support the encodings of the AnnData specification
version they claim.

## Layout

```text
tables/<name>/
├── zarr.json          anndata encoding + region, region_key, instance_key, version
├── X/  obs/  var/  layers/  obsm/  obsp/  varm/  varp/  raw/     (AnnData)
└── uns/
    └── spatialdata_attrs/      region, region_key, instance_key   (copy, see below)
```

## Attributes

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
  name **MUST** be an existing labels, shapes or points element in the same store.

`region_key`
: A string or `null`. Name of the `obs` column that states, for each row, which element in
  `region` it annotates.

`instance_key`
: A string or `null`. Name of the `obs` column that holds the instance identifier within that
  element.

`region`, `region_key` and `instance_key` **MUST** either all be `null` (a table that annotates
nothing) or all be non-null.

## Annotation rules

When the table annotates elements:

- `obs[region_key]` **MUST** be a categorical column whose values are all contained in `region`.
  Writers **SHOULD** set `region` to exactly the set of values present.
- `obs[instance_key]` **MUST NOT** contain nulls. For labels elements the values are the integer
  label values; for shapes and points they are the row index values of the payload, with matching
  type.
- Each pair `(obs[region_key], obs[instance_key])` **MUST** be unique: one row annotates at most one
  instance.
- Not every instance of a region needs a row, and a row's instance **MAY** be absent from the
  element; readers **SHOULD** match by identifier and tolerate both.
- Tables **MUST NOT** carry coordinate transformations and **MUST NOT** be annotated by other tables.

```text
tables/cells                          labels/cells_labels   shapes/nuclei_shapes
obs.region      obs.instance_id       (pixel values)        (row index)
cells_labels    1        ──────────▶  1
cells_labels    2        ──────────▶  2
nuclei_shapes   "n_07"   ────────────────────────────────▶  "n_07"
```

## The `uns/spatialdata_attrs` copy

The same three keys are also stored inside the table as the AnnData `uns["spatialdata_attrs"]`
mapping (`region`, `region_key`, `instance_key`), because `spatialdata` keeps them there in memory
and AnnData serialises `uns` as-is. Writers **MUST** keep the two copies equal. Readers **MAY** use
either; implementations that do not parse `uns` **SHOULD** use the group attributes.

## Naming

`obs` and `var` column names and the keys of `obsm`, `obsp`, `varm`, `varp`, `uns` and `layers`
**MUST** follow the element naming rules of {doc}`container`. `_index` is reserved by AnnData and
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

NGFF has no table type. This chapter follows the spirit of the (unmerged) NGFF tables proposal, whose
`ngff:regions_table` marker and `region`/`region_key`/`instance_key` fields it reuses.
:::
