# Points

{bdg-primary}`points 0.2` {bdg-light}`Zarr v3` · {bdg-secondary}`points 0.1` {bdg-light}`Zarr v2`

A points element is a table of 2D or 3D point coordinates with optional per-point columns, for
example transcript locations with a gene column. It is stored in `points/<name>` as a Zarr group
whose attributes hold the SpatialData metadata and whose payload is a partitioned Parquet dataset.
Points are designed for large tables (10⁶ to 10⁹ rows) and lazy, partition-wise reading.

## Layout

```text
points/<name>/
├── zarr.json              encoding-type, axes, coordinateTransformations, spatialdata_attrs
└── points.parquet/        Parquet dataset (directory)
    ├── part.0.parquet
    └── part.1.parquet ...
```

## Attributes

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
: **MUST** be present with at least one entry ({doc}`coordinate-systems`). Input axes are in the
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
  to (e.g. a cell). The format does not define which element those identifiers refer to; see the
  {doc}`semantic conventions <../semantic/index>`.

## Payload: `points.parquet/`

A directory containing one or more Parquet files named `part.<i>.parquet`. Readers **MUST**
concatenate all parts in ascending `<i>` order. All parts **MUST** share one schema.

Coordinate columns
: `x` and `y` **MUST** be present; `z` **MUST** be present when `axes` lists it. Type **MUST** be
  `int32`, `int64`, `float32` or `float64`.

Other columns
: **MAY** be present with any Parquet type. Column names follow the naming rules in
  {doc}`container`.

Row index
: Writers **MAY** store the dataframe index (for example as `__null_dask_index__`, referenced from
  the `pandas.index_columns` schema metadata). Readers **SHOULD** treat it as the row identifier when
  present and **MUST NOT** treat it as data otherwise.

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
