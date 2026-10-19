# RFCs

RFCs (requests for comments) are written proposals for large features or big breaking changes of
the SpatialData data model, the storage format, or several in-memory formats at once. When to write
one, the process and a template are in {ref}`contributing-rfcs`.

| No. | RFC | Scope | Proposed by | Status |
|-----|-----|-------|-------------|--------|
| 1 | Coordinate systems and transformations: adopt NGFF 0.6 ([RFC-5](https://ngff.openmicroscopy.org/rfc/5/)) for all spatial elements (see {doc}`spec/storage-format/ngff-compatibility` and {doc}`spec/storage-format/next`) | data model; storage format (new container version); implementations | spatialdata core team | planned |
| 2 | [Instance-level linking (mulink-compatible)](https://github.com/LucaMarconato/spatialdata/blob/2619c4ff31a5e6e0a98047be17025d96210c15d0/rfcs/links.md) | data model; storage format (new container version); Python | Luca Marconato | draft (in a fork of `spatialdata`) |
| 3 | [Spatial tiling of vector data](https://github.com/scverse/spatialdata/discussions/1251) | storage format; implementations | [@cornhundred](https://github.com/cornhundred) | idea ([discussion](https://github.com/scverse/spatialdata/discussions/1251), September 2026) |

Statuses: *planned* (agreed to be written) · *idea* (a discussion, not yet written up) · *draft* · *under review* · *accepted* ·
*rejected* · *withdrawn* · *implemented*.
