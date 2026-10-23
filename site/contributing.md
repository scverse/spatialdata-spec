# Contributing

SpatialData is shaped by the people who use it. Whether you write a reader in another language,
build a viewer, run into a dataset the format cannot represent yet, or just find a sentence here
unclear: your experience is what makes this specification better, and every contribution counts,
from a typo fix to a new element type. You do not need to be a SpatialData developer to take
part; questions and half-formed ideas are welcome.

The quickest way in is to say hello on the
[#spatialdata-dev channel](https://scverse.zulipchat.com/#narrow/channel/443514-spatialdata-dev)
of the scverse Zulip, where the developers discuss the specification and its implementations.

## How to take part

1. Discuss an idea on [Zulip](https://scverse.zulipchat.com/#narrow/channel/443514-spatialdata-dev),
   or suggest a change in a [GitHub issue](https://github.com/scverse/spatialdata-spec/issues),
   ideally together with a pull request.
2. A particularly large feature or a big breaking change comes with an RFC (see
   {ref}`contributing-rfcs`).
3. Once an issue or RFC is approved, the change lands in the next version of the specification
   (see {ref}`storage-next`); the {ref}`compatibility-matrix` records which implementation
   releases support it.

A change to the in-memory format of one language does not always require changes in the others,
but sometimes it affects several languages. If in doubt, open an issue in the corresponding
implementation repository, or tag its developers, to make them aware:

- Python: [scverse/spatialdata](https://github.com/scverse/spatialdata/issues)
- R: [HelenaLC/spatialdataR](https://github.com/HelenaLC/spatialdataR/issues)
- JavaScript: [Taylor-CCB-Group/SpatialData.js](https://github.com/Taylor-CCB-Group/SpatialData.js/issues)

(contributing-rfcs)=
## RFCs

An RFC (request for comments) is a written proposal that is discussed and refined in the open
before anything is decided. Smaller changes go through an issue and a pull request alone. All RFCs
are listed on the {doc}`RFC page <rfcs>`.

### When to write an RFC

- The change adds a concept to the abstract data model, or changes the meaning of an existing one.
- The change needs a new storage format version and affects several element types, or affects
  readers and writers in more than one language.
- There are several reasonable designs, and the choice needs input from the community.

### Steps

An RFC and the change it proposes are two pull requests:

1. **Propose.** Open a pull request against the branch `site` that adds the RFC as
   `site/rfcs/<number>-<name>.md`, from the template below, with the status *draft*. Numbers are
   sequential in order of proposal and never reused (e.g. `site/rfcs/0005-tiling.md`). An RFC
   that started elsewhere (a discussion, a fork) gets a short file with a link, and its text moves
   into the file when it is presented for review.
2. **Review.** Once the text can be reviewed, the pull request is merged with the status *under
   review*, so that the RFC is on the {doc}`RFC page <rfcs>` while it is discussed. Discussion
   goes to an issue linked from the RFC; revisions are further pull requests to the same file.
3. **Change the specification.** When the design is concrete, open a second pull request, against
   `main`, with the changes to the specification pages, and put its link in the RFC's `spec-pr`.
4. **Decide.** The SpatialData developers decide, following the consensus-seeking process of the
   [scverse governance](https://github.com/scverse/governance/blob/main/roles.md#decision-making-process).
   The decision and its reasons are recorded in the RFC, with the status *accepted* or *rejected*;
   a rejected RFC stays on the RFC page as a record. On acceptance, the specification pull request
   is merged into `main`, the draft of the next storage format version (see {ref}`storage-next`)
   and, if it changes the data model, of the next data model version; otherwise it is closed.
5. **Release.** The status becomes *implemented* when that version is released, which requires an
   implementation that reads and writes it.

### Template

```text
---
rfc: <number>
title: "<title>"
scope: "data model; storage format; implementations"
targets: "data model 1.1 (or: data model unchanged); storage format 0.6"
proposed-by: "<names>"
status: "draft"
spec-pr: <link to the pull request against main, once it exists>
---

# RFC <number>: <title>

Based on: <link to the tag of the specification it changes, e.g. storage-format-0.5>

## Authors and acknowledgements
## Summary            one paragraph: what changes, for whom
## Motivation         the problem, with concrete use cases
## Proposal
### Data model        new or changed concepts, in plain language
### Storage format    the bytes that change; new storage format and container version
### In-memory formats per language, where affected
## Compatibility      reading old stores, writing new ones, migration
## Alternatives       designs considered and why they were not chosen
## Open questions
## Decision           filled in when the RFC is accepted or rejected
## References
```

(contributing-versions)=
## Versions and releases

Each commit of the branch `main` holds one version of the specification: one storage format
version and the data model version it encodes. Changes to the specification are pull requests
against `main`. A change that needs a new version makes `main` the draft of that version: its pull
request also gives the draft's container format version a `-dev` suffix, marks the version as
draft in the version history, and lists the change in {ref}`storage-next`. Further changes for the
same version edit the draft; corrections that change no version are made the same way. Releases
are tags `storage-format-<version>` of `main` and are never moved.

### When a new version starts

The specification decides when a version starts and when it is released, following the
{ref}`decision process <contributing-rfcs>`, independently of any implementation. A new version is
opened when at least one of these is true:

- a change to the stored bytes is needed (new key, new payload, changed meaning of an existing
  key);
- a new element type is introduced;
- an upstream standard the format depends on (NGFF, AnnData, GeoParquet) releases a version worth
  adopting, such as NGFF 0.6 with RFC-5 transformations.

Bug fixes to the prose, clarifications and non-normative additions do not open a new version.

### Release

A version is released once its accepted changes are complete and implemented in at least one
implementation, with regenerated example stores. Then, in one pull request:

1. its container format version loses the `-dev` suffix;
2. {doc}`storage-format-versions` (and {doc}`data-model-versions`, if the data model changes) list
   it as current, and the previous version as deprecated;
3. the commit is tagged `storage-format-<version>` and the tag is added to `versions.toml` on the branch
   `site`, which publishes it on the website.

Released versions are not changed afterwards: corrections go into `main` and are published with
the next release. Implementations adopt the version in their own releases; the
{ref}`compatibility-matrix` records which releases read and write it.

## Structure of the specification pages

`data-model.md` holds the abstract data model. Each section's text, below its heading, sits
between two comment markers named after the section's label:

```text
(spec-tables)=
## Tables

% begin spec-tables
...
% end spec-tables
```

`storage-format.md` has the same sections. Each one repeats the heading, includes the data
model text between the markers, and follows it with the storage format:

````text
(storage-tables)=
## Tables

:::{include} data-model.md
:start-after: % begin spec-tables
:end-before: % end spec-tables
:::

(storage-tables-layout)=
### Layout
...
````

A change to the data model is therefore made once, in `data-model.md`, and appears on both pages.

- **Data model sections** are plain, human-readable English for everyone, without RFC 2119 key
  words. Prefer positive statements. Keep implementation details out; move history and outlook into
  footnotes (`[^name]`), with the footnote text inside the section's markers so that it is
  included with it. On screen, each footnote shows at its reference on hover or focus; in print,
  the page's last section, *Notes*, lists them.
- **Storage format sections** are normative. They state only what the storage format adds, and
  link to the data model for the concepts (`{ref}` to the `spec-*` anchors) instead of repeating
  them. Give every subsection heading a `storage-*` label.
- **Section headings** cannot go inside tabs (such as the transformation types). There, use a
  rubric with a label, which gets a "¶" permalink that also records the selected tabs:

  ````text
  (storage-tables-layout)=
  ```{rubric} Layout
  ```
  ````

- **Figures** go in `img/` and are included with `{figure}`, `:figclass: spec-figure`
  and an `:alt:` text.

## Writing rules

- In the storage format, use MUST, SHOULD, MAY per RFC 2119, in plain capitals (not bold), and mean it.
- Specify only what NGFF, AnnData, Zarr, Parquet or GeoParquet leave open; link to them for the rest.
- Write the pages as the specification of their version alone, without referring to other
  versions; the {doc}`version history <storage-format-versions>` is the only place that compares
  versions.
- The normative text specifies the format, not an implementation: name the `spatialdata` package
  (or another implementation) only in implementation notes and footnotes.

- Use the custom admonitions:
  - *Implementation note* (`implementation-note`, non-normative);
  - *Divergence from NGFF* (`ngff-divergence`).
- The pages state what is decided. Open questions go into an issue or an RFC, and candidate changes
  into {ref}`storage-next`.
- JSON examples come from real stores; abbreviate with `...` if needed.
- Cite as a link, for example `([Marconato et al., 2025](https://doi.org/10.1038/s41592-024-02212-x))`.
- Short sentences, no filler. If a paragraph does not change what an implementer would do, delete
  it.

## Building the site

The website, including this guide and the RFCs, is on the branch
[`site`](https://github.com/scverse/spatialdata-spec/tree/site), which builds every tagged version
into one site; its README describes how to build and preview it locally.

## Licensing

The text of the specification, of this guide and of the RFCs is licensed under
[CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/); the code (the website and the tools) under
BSD-3-Clause. A contribution is made under the same licences.
