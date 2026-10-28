# SpatialData specifications

[SpatialData](https://github.com/scverse/spatialdata) is an open and interoperable data framework
for spatial omics data. This repository specifies it in plain English, independently of any
implementation. This branch only points to the others:

| Branch | What it holds | Releases |
| --- | --- | --- |
| [`data-model`](https://github.com/scverse/spatialdata-spec/tree/data-model) | the abstract data model: what a SpatialData dataset is | tags `data-model-<version>` |
| [`storage-format`](https://github.com/scverse/spatialdata-spec/tree/storage-format) | the storage format: how a dataset is stored (Zarr, Parquet, built on OME-NGFF); each version encodes one data model version | tags `storage-format-<version>` |
| `maintenance/storage-format-<version>` | older storage format versions, with the corrections made since their release | |
| [`site`](https://github.com/scverse/spatialdata-spec/tree/site) | the website, which builds them together, and the pages of the project: landing page, contributing guide, RFCs | |

`data-model` and `storage-format` each hold the current version of their part, with the
corrections made since its release; the tags keep the text as first released. The in-memory
formats are specified in the repositories of the implementations.

**Pull requests** go against `data-model`, `storage-format` or `site`, not against this branch; how
to contribute is in the contributing guide on the website (`site/contributing.md` on the branch
`site`).

**History.** Until October 2026 the specification was written with all storage format versions side
by side, first on the branch `history-draft`, then on this branch, and written to the branches above
by `tools/write_history.py` and `tools/split_branches.py`. That history is kept here.

The specification text is licensed under CC-BY-4.0, the website code under BSD-3-Clause (see the
`LICENSE` files of the branches).
