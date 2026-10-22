# RFCs

RFCs (requests for comments) are written proposals for large features or big breaking changes of
the SpatialData data model, the storage format, or several in-memory formats at once. When to write
one, the process and a template are in {ref}`contributing-rfcs`.

| No. | RFC | Scope | Targets | Proposed by | Status |
|-----|-----|-------|---------|-------------|--------|
| 1 | Coordinate systems and transformations: adopt NGFF 0.6 ([RFC-5](https://ngff.openmicroscopy.org/rfc/5/)) for all spatial elements (see {ref}`storage-next`) | data model; storage format (new container version); implementations | storage format 0.6; data model 1.1 or unchanged, to be decided | Luca Marconato, Tomaz Vieira, Ajayrama Kumaraswamy (transformations refactoring) | planned |
| 2 | [Instance-level linking (mulink-compatible)](https://github.com/LucaMarconato/spatialdata/blob/2619c4ff31a5e6e0a98047be17025d96210c15d0/rfcs/links.md) | data model; storage format (new container version); Python | data model 1.1; storage format 0.6 | Luca Marconato; base by Yimin Zheng ([Padua hackathon](https://github.com/orgs/scverse/projects/70/views/1?pane=issue&itemId=169148807&issue=scverse%7C2026_04_hackathon_padua%7C6), April 2026); design contributions by Artür Manukyan ([Venice hackathon](https://github.com/BiocCodingCollaborations/VeniceHackathon2026/tree/main/interoperability/relationships)) | draft (in a fork of `spatialdata`) |
| 3 | [Spatial tiling of vector data](https://github.com/scverse/spatialdata/discussions/1251) | storage format; implementations | to be decided: data model 1.1, or unchanged if tiling stays a storage-side index; storage format 0.6 | [@cornhundred](https://github.com/cornhundred) | idea ([discussion](https://github.com/scverse/spatialdata/discussions/1251), September 2026) |
| 4 | [Semantic conventions](https://github.com/scverse/spatialdata-spec/blob/6af066e0764a7ec1124c0c0c1b30633d7993af59/spec/semantic/index.md): which element holds the cells, what an instance or variable represents, which coordinate system is physical ([options](https://github.com/scverse/spatialdata-spec/blob/6af066e0764a7ec1124c0c0c1b30633d7993af59/spec/semantic/options.md)) | data model; storage format | data model 1.1; storage format 0.6 | Luca Marconato | idea (options for community review, September 2026) |

Targets: the data model and storage format versions an RFC changes, as stated in its header
(see the template in {ref}`contributing-rfcs`); RFCs not yet written have proposed targets.

Statuses: *planned* (agreed to be written) · *idea* (a discussion, not yet written up) · *draft* · *under review* · *accepted* ·
*rejected* · *withdrawn* · *implemented*.
