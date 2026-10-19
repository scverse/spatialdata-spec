# Contributing to the specification

## Process

1. Suggest a change in a [GitHub issue](https://github.com/scverse/spatialdata-spec/issues),
   ideally together with a pull request.
2. A particularly large feature or a big breaking change may be accompanied by an RFC: a Markdown
   file in the `rfcs/` folder, included in the pull request. All RFCs are listed on the RFC page.
3. Once an issue or RFC is approved, the change lands in a new `spatialdata` version and the
   compatibility matrix ({ref}`compatibility-matrix`) is updated.

Everything in the specification has a version attached to it. Content without a version is
labelled *proposed*; it either stays proposed or is assigned to an RFC.

Issues, pull requests and RFCs are labelled by what they touch: `on-disk-format`,
`in-memory-<language>` (for example `in-memory-python`).

```{important}
A pull request or RFC can modify both the storage format and an in-memory format. It then carries
both labels.
```

A change to the in-memory format of one language does not always require changes in the others,
but sometimes it affects several languages. If in doubt, open an issue in the corresponding
implementation repository, or tag its developers, to make them aware:

- Python: [scverse/spatialdata](https://github.com/scverse/spatialdata/issues)
- R: [HelenaLC/spatialdataR](https://github.com/HelenaLC/spatialdataR/issues)
- JavaScript: [Taylor-CCB-Group/SpatialData.js](https://github.com/Taylor-CCB-Group/SpatialData.js/issues)

## Versions and labels

The version of the storage format is the container format, for example
`spatialdata-container-format-0.2`. It is bumped whenever anything inside it is bumped, so it is the single version string of the
format; element formats, Zarr, OME-Zarr and `spatialdata` releases follow from the
{ref}`compatibility matrix <compatibility-matrix>`. The specification page shows versions as
tabs, not as badges. Content without a version is {bdg-warning-line}`proposed`; reserved pages are
{bdg-light}`placeholder`.

## Structure of the specification page

`spec/specification.md` holds the abstract data model and its implementations on one page. Each
data model section (a heading) is followed by one tab set with a tab per implementation:

```text
:::::::::{tab-set}
:sync-group: impl

::::::::{tab-item} Data model only
:sync: model
:class-content: tab-model-only

% intentionally empty: shows the data model without any implementation
::::::::

::::::::{tab-item} Storage format
:sync: storage
:selected:

(storage-<section>)=
...
::::::::

::::::::{tab-item} Python
:sync: python

...
::::::::
:::::::::
```

The navigation entries *Abstract data model*, *& storage format* and *& in-memory formats* select
these tabs on the whole page; the tab rows themselves are hidden.

- **Data model sections** are plain, human-readable English for everyone, without RFC 2119 key
  words. Prefer positive statements. Keep implementation details out; move history and outlook into
  footnotes.
- **Implementation tabs** are normative. They state only what the implementation adds, and link to
  the data model section for the concepts (`{ref}` to the `spec-*` anchors) instead of repeating
  them.
- **Section headings** cannot go inside tabs. Use a rubric with a label, which gets a "¶"
  permalink that also records the selected tabs:

  ````text
  (storage-tables-layout)=
  ```{rubric} Layout
  ```
  ````

- **Figures** go in `docs/_static/img/` and are included with `{figure}`, `:figclass: spec-figure`
  and an `:alt:` text.

## Writing rules

- In implementation tabs, use **MUST**, **SHOULD**, **MAY** per RFC 2119 and mean it.
- Specify only what NGFF, AnnData, Zarr, Parquet or GeoParquet leave open; link to them for the rest.
- The storage format covers all versions. Where versions differ, put them in inline tabs
  (`tab-set`) in the sync group `storage-version`, labelled with the container format, newest
  first, so that selecting a version switches all version tabs on the page. Mark the latest
  released version `:selected:`, so that an incoming version is never shown by default:

  ```text
  ::::{tab-set}
  :sync-group: storage-version
  :::{tab-item} spatialdata-container-format-0.3 (incoming)
  :sync: container-0.3

  Content for container format 0.3.
  :::
  :::{tab-item} spatialdata-container-format-0.2
  :sync: container-0.2
  :selected:

  Content for container format 0.2.
  :::
  :::{tab-item} spatialdata-container-format-0.1
  :sync: container-0.1

  Content for container format 0.1.
  :::
  ::::
  ```

- A whole rubric section that exists only in some versions gets a badge after its heading, for example {bdg-secondary}`container 0.3 only` or
  {bdg-secondary}`removed in 0.3`.

- Use the custom admonitions:
  - *Implementation note* (`implementation-note`, non-normative);
  - *Divergence from NGFF* (`ngff-divergence`);
  - *Open question* (`open-question`).
- JSON examples come from real stores; abbreviate with `...` if needed.
- Cite with `{cite:p}` (entries in `docs/references.bib`). Each citing page ends with its own
  `{bibliography}` with `:filter: docname in docnames`; there is no global references page.
- Short sentences, no filler. If a paragraph does not change what an implementer would do, delete
  it.

## Building the site

See the [README](https://github.com/scverse/spatialdata-spec#building-the-website-locally).

## Hosting

The site is built on [Read the Docs](https://readthedocs.org) (`.readthedocs.yaml`), with a preview
for each pull request; until the repository is public, CI uploads the built site as the `site-html`
artifact.

## Licensing

See the [README](https://github.com/scverse/spatialdata-spec#license).
