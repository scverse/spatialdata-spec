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
`in-memory-<language>` (for example `in-memory-python`), `semantic`.

```{important}
A pull request or RFC can modify both the on-disk format and an in-memory format. It then carries
both labels.
```

A change to the in-memory format of one language does not always require changes in the others,
but sometimes it affects several languages. If in doubt, open an issue in the corresponding
implementation repository, or tag its developers, to make them aware:

- Python: [scverse/spatialdata](https://github.com/scverse/spatialdata/issues)
- R: [HelenaLC/spatialdataR](https://github.com/HelenaLC/spatialdataR/issues)
- JavaScript: [Taylor-CCB-Group/SpatialData.js](https://github.com/Taylor-CCB-Group/SpatialData.js/issues)

## Labels on pages

Pages carry a **layer** badge ({bdg-primary}`on-disk`, {bdg-success}`in-memory · Python`,
{bdg-info}`in-memory · R`, {bdg-info}`in-memory · JS`, {bdg-warning}`semantic`) and a **version**
badge.

The version is the container format, for example {bdg-dark-line}`spatialdata-container-format-0.2`.
It is bumped whenever anything inside it is bumped, so it is the single version string of the
format; element formats, Zarr, OME-Zarr and `spatialdata` releases follow from the
{ref}`compatibility matrix <compatibility-matrix>`. Content without a version is
{bdg-warning-line}`proposed`; reserved pages are {bdg-light}`placeholder`.

## Writing rules

- Use **MUST**, **SHOULD**, **MAY** per RFC 2119 and mean it.
- Specify only what NGFF, AnnData, Zarr, Parquet or GeoParquet leave open; link to them for the rest.
- On-disk chapters are organised by element type and cover all versions. Where versions differ,
  put them in inline tabs (`tab-set`) labelled with the container format, newest first, with
  `:sync:` keys so that selecting a version switches all tabs on every page. Mark the latest
  released version `:selected:`, so that an incoming version is never shown by default:

  ```text
  ::::{tab-set}
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

- Section headings cannot go inside tabs. A whole section that exists only in some versions gets a
  badge after its heading, for example {bdg-secondary}`container 0.3 only` or
  {bdg-secondary}`removed in 0.3`.

- Use the custom admonitions:
  - *Implementation note* (`implementation-note`, non-normative);
  - *Divergence from NGFF* (`ngff-divergence`);
  - *Open question* (`open-question`).
- JSON examples come from real stores; abbreviate with `...` if needed.
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
