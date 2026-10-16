# Changelog

All notable changes to this project are documented in this file.

Entries are split into two categories:

- **Specification** — changes to the specification text under `spec/` and to the on-disk
  format it describes.
- **Repository** — changes to tooling, CI, documentation infrastructure, and project
  scaffolding that do not affect the specification.

Within each category, the [Keep a Changelog][] subheadings apply
(_Added_, _Changed_, _Deprecated_, _Removed_, _Fixed_, _Security_).

[keep a changelog]: https://keepachangelog.com/

## [Unreleased]

### Specification

#### Added

- On-disk format, first draft (`spec/on-disk/`): container, coordinate systems and
  transformations, images, labels, shapes, points, tables, NGFF compatibility matrix, version
  history. Describes container 0.2 (Zarr v3) with container 0.1 (Zarr v2) differences in tabs.
- On-disk next-version placeholder (`spec/on-disk/next.md`) collecting candidate changes.
- Documented the differences between stores written by `spatialdata` 0.6 and 0.8 that carry no
  version bump (pyramid array names, per-level translation, multiscale name, AnnData 0.13 index
  encoding) in the raster chapters and in a new "Changes without a version bump" table.
- Semantic conventions (`spec/semantic/`): motivation, eleven questions with candidate options, and
  a prior-art survey with licences. Draft for community review.

### Repository

#### Changed

- Re-scoped from the scverse package template to a specification repository: removed the
  Python package scaffolding, package build/release CI, and API documentation.

#### Added

- `spec/` directory (CC-BY-4.0) to hold the specification prose.
- `docs/contributing_to_the_spec.md` with the contribution paths and writing rules.
- Documentation site on `pydata-sphinx-theme` with a curated landing page, glossary, custom
  admonitions (implementation note, NGFF divergence, open question) and synced version tabs.
- `planning/` working documents: plan, open questions, next steps.
- Read the Docs readiness: `docs/conf.py` reads the `READTHEDOCS_*` variables (canonical URL,
  pull-request preview banner); hosting steps documented. The CI docs job uploads the built site as
  the `site-html` artifact as an interim preview while the repository is private.
- Layer and status labels on all section pages, with a legend and a document table on the landing
  page.
