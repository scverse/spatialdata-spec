# SpatialData specifications: data model 1.0

This branch holds the abstract data model of the [SpatialData](https://github.com/scverse/spatialdata)
specification, version 1.0: what a SpatialData dataset is, independently of how it is stored or
represented in memory.

- [`data-model.md`](data-model.md): the abstract data model
- [`data-model-versions.md`](data-model-versions.md): all data model versions
- [`img/`](img/): its figures

Its encodings are specified elsewhere, each referring to the data model version it encodes: the
storage format on the branch `storage-format`, whose pages include the parts of the data model
they encode; the in-memory formats in the repositories of the implementations. The website
(branch `site`) builds them together.

Every data model version is a tag `data-model-<version>`, the text as first released. This branch
holds the current version, with the editorial corrections made since; how to contribute is in
[`.github/CONTRIBUTING.md`](.github/CONTRIBUTING.md).

The specification text is licensed under CC-BY-4.0 ([LICENSE.md](LICENSE.md)).
