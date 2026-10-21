# RFCs

RFCs (requests for comments) are written proposals for large features or big breaking changes of
the SpatialData data model, the storage format, or several in-memory formats at once. When to write
one, the process and a template are in {ref}`contributing-rfcs`.

| No. | RFC | Scope | Proposed by | Status |
|-----|-----|-------|-------------|--------|
| 1 | Coordinate systems and transformations: adopt NGFF 0.6 ([RFC-5](https://ngff.openmicroscopy.org/rfc/5/)) for all spatial elements (see {doc}`next`) | data model; storage format (new container version); implementations | Luca Marconato, Tomaz Vieira, Ajayrama Kumaraswamy (transformations refactoring) | planned |
| 2 | [Instance-level linking (mulink-compatible)](https://github.com/LucaMarconato/spatialdata/blob/2619c4ff31a5e6e0a98047be17025d96210c15d0/rfcs/links.md) | data model; storage format (new container version); Python | Luca Marconato | draft (in a fork of `spatialdata`) |
| 3 | [Spatial tiling of vector data](https://github.com/scverse/spatialdata/discussions/1251) | storage format; implementations | [@cornhundred](https://github.com/cornhundred) | idea ([discussion](https://github.com/scverse/spatialdata/discussions/1251), September 2026) |
| 4 | [Semantic conventions](https://github.com/scverse/spatialdata-spec/blob/6af066e0764a7ec1124c0c0c1b30633d7993af59/spec/semantic/index.md): which element holds the cells, what an instance or variable represents, which coordinate system is physical ([options](https://github.com/scverse/spatialdata-spec/blob/6af066e0764a7ec1124c0c0c1b30633d7993af59/spec/semantic/options.md)) | data model; storage format | Luca Marconato | idea (options for community review, September 2026) |

Statuses: *planned* (agreed to be written) · *idea* (a discussion, not yet written up) · *draft* · *under review* · *accepted* ·
*rejected* · *withdrawn* · *implemented*.

## Acknowledgements

- **RFC 2:** Yimin Zheng built the base for the RFC at the
  [Padua hackathon](https://github.com/orgs/scverse/projects/70/views/1?pane=issue&itemId=169148807&issue=scverse%7C2026_04_hackathon_padua%7C6)
  (April 2026); Artür Manukyan contributed to the design at the
  [Venice hackathon](https://github.com/BiocCodingCollaborations/VeniceHackathon2026/tree/main/interoperability/relationships).
