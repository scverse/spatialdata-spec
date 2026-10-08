# Images

{bdg-primary}`spatialdata-container-format-0.2` · {bdg-secondary}`spatialdata-container-format-0.1`

An image element is an [NGFF multiscale image](https://ngff.openmicroscopy.org/0.5/index.html#multiscale-md)
stored in `images/<name>`, with the axis restrictions and additional attributes listed here.
Everything not mentioned (array layout, chunking, codecs, pyramid construction) is governed by
[NGFF](https://ngff.openmicroscopy.org/specifications/index.html) and [Zarr](https://zarr-specs.readthedocs.io/).

## Layout

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

## Attributes

The examples below were written by `spatialdata` 0.8 for the same image `my_image` (two channels,
two levels); `multiscales[0].coordinateTransformations` is specified in {doc}`coordinate-systems`
and elided here.

::::::{tab-set}
::::{tab-item} spatialdata-container-format-0.2
:sync: container-0.2

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
  `c`). It **MAY** be followed by a `translation` equal to `(scale − 1) / 2` per spatial axis
  (`0.0` for `c`), which keeps the pixel centres of a downsampled level aligned with level 0 under
  the pixel-centre convention. `spatialdata` 0.8 writes the translation; 0.6 did not. Readers
  **MUST** apply every entry, in order. Single-scale images have one dataset.

`multiscales[0].coordinateTransformations`
: **MUST** be present with at least one entry, as specified in {doc}`coordinate-systems`. Maps
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

## Arrays

- Level `0` **MUST** hold the full-resolution data. Every level **MUST** have the same number of
  dimensions, in the axes order above.
- Any numeric Zarr data type is allowed.
- Chunk shape and codecs are free. Writers **SHOULD** keep chunks well below 2 GiB.
- Three- or four-channel images whose channel labels are `r, g, b` (`, a`) **MAY** be rendered as
  RGB(A) by viewers; this is a convention, not a requirement.

:::{admonition} Implementation note
:class: implementation-note

A minimal reader needs `axes`, `datasets[*].path`, `datasets[*].coordinateTransformations`
(scale and optional translation), `coordinateTransformations`, and `omero.channels[*].label`. Everything else in the group can be
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
