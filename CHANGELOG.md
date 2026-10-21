# Changelog

All notable changes to this project are documented in this file.

Entries are split into two categories:

- **Specification** — changes to the specification text under `spec/` and to the storage
  format it describes.
- **Repository** — changes to tooling, CI, documentation infrastructure, and project
  scaffolding that do not affect the specification.

Within each category, the [Keep a Changelog][] subheadings apply
(_Added_, _Changed_, _Deprecated_, _Removed_, _Fixed_, _Security_).

[keep a changelog]: https://keepachangelog.com/

## [Unreleased]

### Specification

#### Added

- `spec/specification.md` split into `spec/data-model.md` (abstract data model) and
  `spec/storage-format.md`, which includes each data model section and follows it with the
  storage format; rubrics in the storage format became headings. The placeholder tabs for the
  in-memory formats and the "Data model only" tab are gone.
- SpatialData specifications on a single page (`spec/specification.md`): the abstract data model
  in plain language (datasets and elements, spatial elements, coordinate systems and
  transformations, instances and identifiers, annotation tables), each part followed
  by its storage format and, later, its in-memory formats. Figures from the SpatialData
  documentation illustrate the element types and coordinate systems.
- Storage format, first draft: container, axes, images, labels, points, shapes, coordinate systems
  and transformations, tables. Describes container 0.2 (Zarr v3) with container 0.1 (Zarr v2)
  differences in synced version tabs. The storage text states only what the storage adds and links
  to the data model for the concepts.
- Version history with compatibility matrix, NGFF compatibility, and a next-version page
  collecting candidate changes (`spec/storage-format/`).
- Draft of container format 0.3: the same as 0.2 except where a tab labelled *0.3 (draft)* holds
  an accepted change; selectable in the navigation, which shows the 0.2 text elsewhere and marks
  the changes.
- Documented the differences between stores written by `spatialdata` 0.6 and 0.8 that carry no
  version bump (pyramid array names, per-level translation, multiscale name, AnnData 0.13 index
  encoding) in the images section and in a "Changes without a version bump" table.

### Repository

#### Changed

- Three branches: `history-draft` (all versions side by side; where changes are made),
  `main` (one version per commit, Markdown and images only, tagged `storage-format-0.1` to
  `storage-format-0.5`, one per row of the compatibility matrix) and `site` (the website).
  `tools/write_history.py` writes `main` from `history-draft`, using `tools/history.toml`.
- Re-scoped from the scverse package template to a specification repository: removed the
  Python package scaffolding, package build/release CI, and API documentation.
- Website code (Sphinx configuration, CSS, JavaScript) moved to the `site` branch, which builds
  every published version of the specification from its own branch or tag into one site with a
  version switcher; every branch and tag here holds one version. Published on GitHub Pages by
  `publish.yaml` instead of Read the Docs (`.readthedocs.yaml` removed); pull request previews
  and local builds use the `site` branch.

#### Added

- `spec/` directory (CC-BY-4.0) to hold the specification prose.
- `docs/contributing_to_the_spec.md` with the contribution paths and writing rules.
- RFC page (`docs/rfcs.md`) listing the RFCs (1 coordinate systems and transformations, 2
  instance-level linking, 3 spatial tiling of vector data); when to write an RFC, the process and a
  template are in the specification contributing guide.
- Documentation site on `sphinx-book-theme` (the scverse default, navigation on the left) with a
  curated landing page, custom admonitions (implementation note, NGFF divergence, open
  question) and synced version tabs.
- Views in the navigation: *Abstract data model*, *& storage format* and *& in-memory formats*
  switch every implementation block of the specification page at once (`js/view-switch.js`).
- Permalinks into tabs: the URL records the selected view and version (`?impl=storage`,
  `&storage-version=container-0.1`), a link to an anchor inside a hidden tab opens that tab, and
  rubrics inside tabs get a "¶" link (`js/tab-permalinks.js`).
- Footnotes as popups on hover, focus or tap (`js/footnote-popups.js`); the footnote list moves into
  a *Notes* section, which is hidden on screen and kept in print.
- `planning/` working documents: plan, open questions, next steps.
- Read the Docs readiness: `docs/conf.py` reads the `READTHEDOCS_*` variables (canonical URL,
  pull-request preview banner); hosting steps documented. The CI docs job uploads the built site as
  the `site-html` artifact as an interim preview while the repository is private.
- Status labels, with a legend and a document table on the landing page.
