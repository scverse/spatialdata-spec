# Shapes

{bdg-primary}`shapes 0.3` {bdg-light}`Zarr v3` · {bdg-secondary}`shapes 0.2` {bdg-light}`Zarr v2` · {bdg-secondary}`shapes 0.1` {bdg-light}`legacy`

A shapes element is a table of 2D geometries, one row per {term}`instance`: circles, polygons or
multipolygons. It is stored in `shapes/<name>` as a Zarr group whose attributes hold the SpatialData
metadata and whose payload is one [GeoParquet](https://geoparquet.org/releases/v1.0.0/) file.
Shapes are a region and can be annotated by {doc}`tables`.

## Layout

```text
shapes/<name>/
├── zarr.json          encoding-type, axes, coordinateTransformations, spatialdata_attrs
└── shapes.parquet     GeoParquet 1.0.0
```

## Attributes

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
: **MUST** be `["x", "y"]`. Shapes are 2D.

`coordinateTransformations`
: **MUST** be present with at least one entry ({doc}`coordinate-systems`). Input axes are `x, y` in
  this order.

`spatialdata_attrs.version`
: **MUST** be `"0.3"` (Zarr v3) or `"0.2"` (Zarr v2). Version `"0.1"` uses a different payload, see
  below.

The attributes are identical for shapes 0.2 and 0.3; the version tracks the Zarr format of the
container.

## Payload: `shapes.parquet`

A single GeoParquet file. The GeoParquet `geo` metadata **MUST** be present with
`primary_column: "geometry"`.

`geometry`
: **MUST** be present. Encoding **MUST** be `WKB` or the GeoArrow native encoding as defined by
  GeoParquet 1.1; writers default to WKB, readers **MUST** support WKB and **SHOULD** support
  GeoArrow. `crs` **MUST** be `null`: coordinates are in the element's intrinsic coordinate system,
  not in a geographic reference system. Geometries **MUST** be 2D.

Geometry types
: All rows **MUST** be `Point`, or all rows **MUST** be `Polygon` or `MultiPolygon` (the two may
  be mixed). Points and polygons **MUST NOT** be mixed in one element. Other geometry types are not
  allowed.

`radius`
: **MUST** be present when the geometries are `Point`, and **MUST NOT** be present otherwise. A
  numeric column; every value **MUST** be finite and strictly positive. A point plus a radius is a
  circle; the radius is expressed in the same units as the coordinates and is scaled by the
  coordinate transformation.

Row index
: The pandas index is stored following the Parquet/pandas convention: a `RangeIndex` described only
  in the `pandas` schema metadata, or an explicit index column (typically `__index_level_0__`)
  referenced from `pandas.index_columns`. The index values are the instance identifiers used by
  tables; they **MUST** be unique and **MAY** be integers or strings.

Other columns
: **MAY** be present with any Parquet type (string columns **MAY** be Arrow `string` or
  `large_string`). They are per-instance annotations stored with the element. Column names follow
  the naming rules in {doc}`container`.

The file **MUST** contain at least one row.

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
