# Labels

{bdg-primary}`raster 0.3` {bdg-light}`Zarr v3` · {bdg-secondary}`raster 0.2, 0.1` {bdg-light}`Zarr v2`

A labels element is a segmentation mask: an integer array in which each distinct non-zero value
identifies one {term}`instance`. It is stored in `labels/<name>` as an NGFF multiscale image with
[image-label](https://ngff.openmicroscopy.org/0.5/index.html#labels-md) metadata. Labels are a
{term}`region` and can be annotated by {doc}`tables`.

Everything in {doc}`images` applies, with the following differences.

## Attributes

::::{tab-set}
:::{tab-item} Zarr v3 (raster 0.3)
:sync: v3

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
:::{tab-item} Zarr v2 (raster 0.2 / 0.1)
:sync: v2

```json
{
  "multiscales": [{ "version": "0.4-dev-spatialdata", "name": "blobs_labels", "axes": [ ... ], "datasets": [ ... ], "coordinateTransformations": [ ... ] }],
  "image-label": { "version": "0.4" },
  "spatialdata_attrs": { "version": "0.2" }
}
```
:::
::::

`multiscales[0].axes`
: **MUST** be exactly `y, x` or `z, y, x`, all of type `space`. There is no channel axis.

`image-label`
: **MUST** be present. `version` **SHOULD** match the NGFF version the store follows (`"0.5"` in
  Zarr v3 stores, `"0.4"` in Zarr v2 stores). The NGFF `colors`, `properties` and `source` fields
  **MAY** be present; SpatialData does not write or interpret them. Multiscale labels written by
  `spatialdata` 0.6 in Zarr v2 stores lack this key; readers **SHOULD** tolerate its absence.

`omero`
: **MUST NOT** be present.

The parent `labels` group lists the element in its `labels` attribute ({doc}`container`).

## Arrays

- The data type **MUST** be an integer type (signed or unsigned) or boolean.
- The value `0` is background. Readers **MUST NOT** treat it as an instance. Every other distinct
  value is one instance, and that value is its instance identifier for table annotation.
- Instance identifiers need not be contiguous.
- Downsampled levels **SHOULD** be produced without interpolation (nearest neighbour or
  majority), so that no new label values appear.

:::{admonition} Implementation note
:class: implementation-note

To join a labels element with a table: read `instance_key` from the table, then match the integer
values of the label array against the table's `obs[instance_key]` column for rows whose
`obs[region_key]` equals this element's name. See {doc}`tables`.
:::
