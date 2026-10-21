(implementations)=
# Implementations

Software that represents the {doc}`abstract data model <data-model>` in memory: its elements,
coordinate systems, instances and annotation tables. Which software reads and writes the storage
format is listed in {doc}`storage-format-implementations`.

## Implementations of the data model

Each has its own in-memory format of the whole data model.

- [`spatialdata`](https://github.com/scverse/spatialdata): Python
  ([documentation](https://spatialdata.scverse.org)).
- [`SpatialData`](https://github.com/HelenaLC/spatialdataR): R, Bioconductor.
- [`SpatialData.js`](https://github.com/Taylor-CCB-Group/SpatialData.js): JavaScript and TypeScript.

## Software built on the data model

These packages work with datasets of the data model through the in-memory format of
`spatialdata`:

- [`spatialdata-io`](https://github.com/scverse/spatialdata-io): reads the output of spatial omics
  technologies into datasets of the data model
  ([documentation](https://spatialdata.scverse.org/projects/io/en/stable/)).
- [`spatialdata-plot`](https://github.com/scverse/spatialdata-plot): static plots
  ([documentation](https://spatialdata.scverse.org/projects/plot/en/stable/api.html)).
- [`napari-spatialdata`](https://github.com/scverse/napari-spatialdata): interactive exploration and
  annotation in napari
  ([documentation](https://spatialdata.scverse.org/projects/napari/en/stable/notebooks/spatialdata.html)).
- [Sopa](https://github.com/prism-oncology/sopa): a technology-invariant pipeline for spatial omics
  analysis.
- [Harpy](https://github.com/saeyslab/harpy): spatial transcriptomics and proteomics analysis.
- [Celldega](https://github.com/cornhundred/celldega): spatial omics analysis and visualization.
