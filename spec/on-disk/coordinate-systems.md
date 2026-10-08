# Coordinate systems and transformations

{bdg-primary}`spatialdata-container-format-0.2` · {bdg-secondary}`spatialdata-container-format-0.1`

Every {term}`spatial element` is stored in its own {term}`intrinsic coordinate system`:

- **Shapes and points:** the space of the stored coordinates, in their own units.
- **Images and labels:** the space of pixel indices of scale 0 (the highest resolution). Every
  scale maps into it through the scale of its level in the `multiscales` metadata. Per-level
  translations are not supported in container formats 0.1 and 0.2; they will be supported from the
  version that introduces NGFF 0.6 support (see {doc}`next`).

In container formats 0.1 and 0.2 the intrinsic coordinate system is never named, on disk or in
memory.

Alignment between elements
is expressed by mapping each element into one or more named {term}`coordinate systems <coordinate system>`
through {term}`coordinate transformations <coordinate transformation>`. Two elements are aligned
when they map into the same named coordinate system.

```text
                        intrinsic (never shared)             named (shared)
   my_image  cyx ──identity────────────────────────▶ "global"
   my_labels yx  ──scale [0.5, 0.5]────────────────▶ "global"
   my_points xy  ──sequence [scale, translation]───▶ "global"
   my_points xy  ──scale [0.2, 0.2]────────────────▶ "micron"
```

`my_image`, `my_labels` and `my_points` are aligned, because all three map into `"global"`.
`my_points` appears twice: the same element also maps into a second coordinate system, `"micron"`,
with a different transformation.

## Axes

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
addressed in the incoming version, which follows NGFF. Shapes and points store coordinates
directly.

## Encoding

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

Within one `coordinateTransformations` list, `output.name` values **MUST** be unique: an element maps
to a given coordinate system at most once. The JSON schemas do not check this; `spatialdata` writes
unique names by construction (transformations are kept in a mapping keyed by coordinate system name)
and, when reading a list with a repeated name, keeps the last entry. The list **MUST** contain at least one entry. When no
alignment information exists, writers **SHOULD** map the element to `"global"` with an `identity`
transformation. Coordinate system names follow the same rules as element names
({doc}`container`).

## Where the list lives

| Element | Location |
|---------|----------|
| images, labels (Zarr v3) | `attributes.ome.multiscales[0].coordinateTransformations` |
| images, labels (Zarr v2) | `.zattrs` → `multiscales[0].coordinateTransformations` |
| shapes, points | group attribute `coordinateTransformations` |

Raster elements additionally carry the NGFF per-level transformations in
`multiscales[0].datasets[i].coordinateTransformations` (a `scale`, optionally followed by a
`translation`, per pyramid level, relative to level `0`). To place a pixel of level `i` into a named
coordinate system, a reader **MUST** apply the level's transformations first, then the SpatialData
transformation. See {doc}`images`.

## Transformation types

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
