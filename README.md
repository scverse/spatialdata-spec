# SpatialData specifications: storage format 0.4

This branch holds one version of the [SpatialData](https://github.com/scverse/spatialdata)
specification: version 0.4 of the storage format, which encodes version 1.0 of the
abstract data model (container format 0.2).

- [`data-model.md`](data-model.md): the abstract data model
- [`storage-format.md`](storage-format.md): the storage format, with each part of the data model
- [`storage-format-conformance.md`](storage-format-conformance.md): example stores and validation
- [`data-model-versions.md`](data-model-versions.md), [`storage-format-versions.md`](storage-format-versions.md):
  all versions

How to contribute, and the RFCs, are on the website (branch `site`); see
[`.github/CONTRIBUTING.md`](.github/CONTRIBUTING.md).

Every version is a tag `storage-format-<version>` of this branch; its history up to storage format
0.4 was written by `tools/write_history.py`. The website is built by the branch `site`.

The specification text is licensed under CC-BY-4.0 ([LICENSE.md](LICENSE.md)).
