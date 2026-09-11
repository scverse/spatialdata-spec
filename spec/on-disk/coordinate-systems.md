# Coordinate systems and transformations

Every {term}`spatial element` is stored in its own {term}`intrinsic coordinate system`: pixel
indices for images and labels, coordinate columns for shapes and points. Alignment between elements
is expressed by mapping each element into one or more named {term}`coordinate systems <coordinate system>`
through {term}`coordinate transformations <coordinate transformation>`. Two elements are aligned
when they map into the same named coordinate system.

```text
                 intrinsic (never shared)             named (shared)
   image  cyx ──identity────────────────────────▶ "global"
   labels yx  ──scale [0.5, 0.5]────────────────▶ "global"
   points xy  ──sequence [scale, translation]───▶ "global"
   points xy  ──scale [0.2, 0.2]────────────────▶ "micron"
```

## Axes

An element's axes are fixed by its type:

| Element | Axes (in storage order) |
|---------|-------------------------|
| images | `c`, `y`, `x` or `c`, `z`, `y`, `x` |
| labels | `y`, `x` or `z`, `y`, `x` |
| shapes | `x`, `y` |
| points | `x`, `y` or `x`, `y`, `z` |

Only these four axis names exist. `c` has NGFF type `channel`; `x`, `y`, `z` have type `space`. No
other axis names or types (such as `time`) are allowed in the current version. Coordinates along
`x`, `y`, `z` are real numbers in the same unit within one coordinate system.

For raster elements, the intrinsic coordinate of a pixel with index `i` along an axis covers the
half-open interval `[i, i + 1)`; its centre is `i + 0.5`. Shapes and points store coordinates
directly.

## Encoding

Transformations are stored as a JSON list named `coordinateTransformations`. Each entry maps the
element's intrinsic coordinate system to one named coordinate system:

```json
{
  "type": "scale",
  "scale": [1.0, 0.5, 0.5],
  "input": {
    "name": "zyx",
    "axes": [ { "name": "z", "type": "space", "unit": "unit" }, { "name": "y", ... }, { "name": "x", ... } ]
  },
  "output": {
    "name": "global",
    "axes": [ { "name": "z", "type": "space", "unit": "unit" }, { "name": "y", ... }, { "name": "x", ... } ]
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
for `space` axes, `unit`. Writers that do not know the physical unit **MUST** write the placeholder
string `"unit"`; readers **MUST** accept any string here.

Within one `coordinateTransformations` list, `output.name` values **MUST** be unique: an element maps
to a given coordinate system at most once. The list **MUST** contain at least one entry. When no
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
{ "type": "identity", "input": {...}, "output": {...} }
```
:::

:::{tab-item} scale
`scale`: list of numbers, one per input axis. Output axes equal input axes.
```json
{ "type": "scale", "scale": [1.0, 0.5, 2.0], "input": {...}, "output": {...} }
```
:::

:::{tab-item} translation
`translation`: list of numbers, one per input axis. Output axes equal input axes.
```json
{ "type": "translation", "translation": [0.0, 10.0, -3.0], "input": {...}, "output": {...} }
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
  "input":  { "name": "cyx", "axes": [c, y, x] },
  "output": { "name": "affine", "axes": [c, x, y] }
}
```
The example maps `(c, y, x) ↦ (c, x + 5, 2·y + 6)`.
:::

:::{tab-item} mapAxis
`mapAxis`: object whose keys are output axis names and values are input axis names. Used to permute
axes.
```json
{ "type": "mapAxis", "mapAxis": { "x": "y", "y": "x" },
  "input": { "name": "xy", "axes": [x, y] }, "output": { "name": "global", "axes": [y, x] } }
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
    { "type": "scale", "scale": [1.0, 2.0, 2.0], "input": {...}, "output": {...} },
    { "type": "translation", "translation": [0.0, 1.0, 1.0], "input": {...}, "output": {...} }
  ],
  "input": {...}, "output": {...}
}
```
:::
::::

Readers **MAY** encounter `rotation` and `byDimension` entries defined by the NGFF transformations
proposal; `spatialdata` reads but does not write them. `inverseOf`, `bijection`, `coordinates` and
`displacements` are not supported.

:::{admonition} Implementation note
:class: implementation-note

Every supported type can be reduced to a single affine matrix of shape `(n_out + 1) × (n_in + 1)`.
A reader can convert each entry to that form on load and compose sequences by matrix
multiplication, which is what `spatialdata` does in `BaseTransformation.to_affine_matrix`. Circles
in shapes require care: a non-uniform scale or a shear turns a circle into an ellipse, which the
format cannot represent.
:::

:::{admonition} Divergence from NGFF
:class: ngff-divergence

NGFF 0.4 and 0.5 allow only `scale` and `translation`, only on raster data, and reference no named
coordinate systems. The encoding above follows the NGFF transformations proposal
([RFC-5](https://ngff.openmicroscopy.org/rfc/5/)) with two differences: `input` and `output` are
inlined coordinate system objects instead of names referencing a `coordinateSystems` list, and the
same encoding is applied to shapes and points. Convergence with the final RFC-5 text is planned;
see {doc}`ngff-compatibility`.
:::
