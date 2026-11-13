# SpatialData specifications

SpatialData is an open and interoperable data framework for spatial omics data.
This repository holds its specification hosted at (spatialdata-spec.scverse.org).
This branch only points to the others:

| Branch name | Branch content | Releases |
| --- | --- | --- |
| [`data-model`](https://github.com/scverse/spatialdata-spec/tree/data-model) | the abstract data model: what a SpatialData dataset is | tags `data-model-<version>` |
| [`storage-format`](https://github.com/scverse/spatialdata-spec/tree/storage-format) | the storage format: how a dataset is stored (Zarr, Parquet, built on OME-NGFF); each version encodes one data model version | tags `storage-format-<version>` |
| `maintenance/storage-format-<version>` | older storage format versions, with the corrections made since their release | |
| [`rfcs`](https://github.com/scverse/spatialdata-spec/tree/rfcs) | the RFCs: proposals for large changes of the data model or the storage format | |
| [`site`](https://github.com/scverse/spatialdata-spec/tree/site) | the website, which builds them together, and the pages of the project: landing page, contributing guide | |

`data-model` and `storage-format` each hold the current version of their part, with the
corrections made since its release; the tags keep the text as first released. The in-memory
formats are specified in the repositories of the implementations.

**Pull requests** go against `data-model`, `storage-format`, `rfcs` or `site`, not against this branch; how
to contribute is in the contributing guide on the website (`site/contributing.md` on the branch
`site`).

The specification text is licensed under CC-BY-4.0, the website code under BSD-3-Clause (see the
`LICENSE` files of the branches).
