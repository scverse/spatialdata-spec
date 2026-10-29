# SpatialData specifications: RFCs

This branch holds the RFCs (requests for comments) of the
[SpatialData specifications](https://github.com/scverse/spatialdata-spec): written proposals for
large features or big breaking changes of the data model, the storage format, or several in-memory
formats at once.

- [`rfcs.md`](rfcs.md): the RFC page, with the table of all RFCs
- [`rfcs/`](rfcs/): the RFCs, one file each (`<number>-<name>.md`), and their figures (`rfcs/img/`)

An RFC proposes; the change it proposes lands on the branch of the specification it changes,
`data-model` or `storage-format`, once the RFC is accepted. The RFCs have no versions: this branch
holds their current state. The website (branch `site`) builds them once, at the site root
(`rfcs.html`); its `build.py` writes the table on `rfcs.md` from the headers of the RFCs. How to
write and propose one is in [`.github/CONTRIBUTING.md`](.github/CONTRIBUTING.md).

The text of the RFCs is licensed under CC-BY-4.0 ([LICENSE.md](LICENSE.md)).
