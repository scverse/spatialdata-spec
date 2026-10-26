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

The notebook
[`multiple_elements.ipynb`](https://github.com/scverse/spatialdata-tutorials/blob/fabc79abd1e02ca231b2d6983ef8cf6e43f8930f/notebooks/developers_resources/storage_format/multiple_elements.ipynb)
in `spatialdata-tutorials` (formerly `spatialdata-notebooks`; revision `fabc79a`, run with
`spatialdata` 0.7.0a1.dev2 in January 2026) writes an illustrative example store of this version,
`multiple_elements.zarr`. The repository commits its array chunks and Parquet files but not its
`zarr.json` metadata; run the notebook to get the complete store. The store holds 2D elements of
every type: a single-scale and a multiscale image, a single-scale and a multiscale labels element,
points, circles, polygons and multipolygons, and a table that annotates the labels. The labels
element has `identity`, `scale`, `translation`, `affine` and `sequence` transformations.

The store does not cover 3D elements, `mapAxis` transformations, tables that annotate points or
shapes, several tables, string instance identifiers or invalid stores. A reader that handles it
can still fail on other stores of this version.
:::
:::{tab-item} Storage format 0.1–0.4
:sync: sf-0.1-0.4

No pinned example stores of this version are published.
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
