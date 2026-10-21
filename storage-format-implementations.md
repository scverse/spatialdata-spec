(storage-format-implementations)=
# Storage format implementations

Software that reads or writes the {doc}`storage format <storage-format>`, or checks stores against
it. Which releases of `spatialdata` write which storage format is listed in the
{ref}`compatibility matrix <compatibility-matrix>`.

- [`spatialdata`](https://github.com/scverse/spatialdata): Python; reads every storage format
  version and writes the current one by default
  ([documentation](https://spatialdata.scverse.org)).
- [`SpatialData`](https://github.com/HelenaLC/spatialdataR): R, Bioconductor.
- [`SpatialData.js`](https://github.com/Taylor-CCB-Group/SpatialData.js): JavaScript and TypeScript;
  reads stores.
- [Vitessce](https://github.com/vitessce/vitessce): visualizes stores (through `SpatialDataWrapper`
  in its Python API).
- [`SpatialData.validate`](https://github.com/Huber-group-EMBL/SpatialData.validate): R; validates
  the raster metadata of stores against JSON schemas.

Software built on `spatialdata` (see {doc}`implementations`) reads and writes stores through it.
