---
orphan: true
---

(storage-format-implementations)=
# Storage format implementations

Software that reads or writes the {doc}`storage format <storage-format>` itself, or checks stores
against it. Software built on `spatialdata` (see {doc}`implementations`) reads and writes stores
through it and is not listed here. Which releases of `spatialdata` write which storage format is
listed in the {ref}`compatibility matrix <compatibility-matrix>`.

## Read and write

- [`spatialdata`](https://github.com/scverse/spatialdata): Python; reads every storage format
  version and writes the current one by default
  ([documentation](https://spatialdata.scverse.org)).

## Read only

- [`SpatialData`](https://github.com/HelenaLC/spatialdataR): R, Bioconductor (`readSpatialData`).
- [`SpatialData.js`](https://github.com/Taylor-CCB-Group/SpatialData.js): JavaScript and TypeScript
  (`readZarr`).
- [Vitessce](https://github.com/vitessce/vitessce): visualizes stores with its own loaders
  (`*.spatialdata.zarr` file types for points, shapes, labels, images and tables).

## Validation

- [`SpatialData.validate`](https://github.com/Huber-group-EMBL/SpatialData.validate): R; validates
  the raster metadata of stores against JSON schemas.
