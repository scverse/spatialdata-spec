# SpatialData specifications: storage format 0.3

This branch holds the storage format of the [SpatialData](https://github.com/scverse/spatialdata)
specification, version 0.3: how a dataset is stored (Zarr, Parquet, built on OME-NGFF). It encodes
version 1.0 of the abstract data model (container format 0.1), which is on the branch
`data-model`: each part of the storage format follows the part of the data model it encodes,
included from there when the website (branch `site`) builds the pages.

- [`storage-format.md`](storage-format.md): the storage format
- [`storage-format-conformance.md`](storage-format-conformance.md): example stores and validation
- [`storage-format-versions.md`](storage-format-versions.md): all storage format versions

Every storage format version is a tag `storage-format-<version>`, the text as first released. This
branch holds the current version, with the editorial corrections made since; how to contribute is
in [`.github/CONTRIBUTING.md`](.github/CONTRIBUTING.md).

The specification text is licensed under CC-BY-4.0 ([LICENSE.md](LICENSE.md)).
