(storage-conformance)=
# Examples and validation

Resources for testing an implementation of the {doc}`storage format <storage-format>`.

(storage-conformance-examples)=
## Example stores

::::{tab-set}
:sync-group: storage-version
:::{tab-item} Storage format 0.5
:sync: sf-0.5
:selected:

The `spatialdata-notebooks` repository regenerates small stores covering every element type and
transformation type daily from the `main` branch of `spatialdata`:
[`notebooks/developers_resources/storage_format`](https://github.com/scverse/spatialdata-notebooks/tree/main/notebooks/developers_resources/storage_format).
A reader that handles those stores handles any store of the same version.
:::
:::{tab-item} Storage format 0.1–0.4
:sync: sf-0.1-0.4

No example stores of this version are published.
:::
::::

(storage-conformance-schemas)=
## JSON schemas

::::{tab-set}
:sync-group: storage-version
:::{tab-item} Storage format 0.5
:sync: sf-0.5
:selected:

[SpatialData.validate](https://github.com/Huber-group-EMBL/SpatialData.validate) (R package, MIT
licence, author Hugo Gruson, EMBL) ships JSON schemas for the metadata of raster elements of this
version, including their transformations. Porting them into this repository is planned.
:::
:::{tab-item} Storage format 0.3–0.4
:sync: sf-0.3-0.4

No JSON schemas for this version are published.
:::
:::{tab-item} Storage format 0.1–0.2
:sync: sf-0.1-0.2

[SpatialData.validate](https://github.com/Huber-group-EMBL/SpatialData.validate) (R package, MIT
licence, author Hugo Gruson, EMBL) ships JSON schemas for the metadata of raster elements of this
version, including their transformations. Porting them into this repository is planned.
:::
::::
