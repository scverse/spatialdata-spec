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

1. **Propose.** Open a pull request against the branch
   [`rfcs`](https://github.com/scverse/spatialdata-spec/tree/rfcs) that adds the RFC as
   `rfcs/<number>-<name>.md`, from the {doc}`template <rfcs/template>`, with the status
   *draft*. Numbers are sequential in order of proposal and never reused (e.g.
   `rfcs/0006-tiling.md`). An RFC that started elsewhere (a discussion, a fork) gets a short file with a link, and its text moves
   into the file when it is presented for review.
2. **Review.** Once the text can be reviewed, the pull request is merged with the status *under
   review*, so that the RFC is on the {doc}`RFC page <rfcs>` while it is discussed. The discussion
   (an issue, a Zulip topic, a GitHub discussion, or elsewhere) is linked from the Discussion
   section of the RFC; revisions are further pull requests to the same file.
3. **Change the specification.** When the design is concrete, open a pull request with the changes
   to the specification pages against `storage-format`, and one against `data-model` if it changes
   the data model (see {ref}`contributing-versions`), and link them from the Implementation section
   of the RFC.
4. **Decide.** The SpatialData developers decide, following the consensus-seeking process of the
   [scverse governance](https://github.com/scverse/governance/blob/main/roles.md#decision-making-process).
   The decision and its reasons are recorded in the Discussion section of the RFC, with the status
   *accepted* or *rejected*; a rejected RFC stays on the RFC page as a record. On acceptance, the
   specification pull requests are merged: into `storage-format`, the draft of the next storage
   format version (see {ref}`storage-next`), and into `data-model`, the draft of the next data model
   version, if it changes the data model; otherwise they are closed.
5. **Release.** The status becomes *implemented* when that version is released, which requires an
   implementation that reads and writes it.

### Template

New RFCs start from the {doc}`RFC template <rfcs/template>`: a short header (authors, status,
type, date of creation) and the sections Abstract, Description, Data model (only when the data
model changes), Storage format, Related work, Implementation, Discussion and References.

(contributing-versions)=
## Versions and releases

The specification has two parts, each with its own versions and its own branch: the abstract data
model on [`data-model`](https://github.com/scverse/spatialdata-spec/tree/data-model), the storage
format on [`storage-format`](https://github.com/scverse/spatialdata-spec/tree/storage-format). Each
storage format version encodes one data model version, and its pages include the text of that data
model version (see {ref}`contributing-structure`): the website builds them together, so that the
data model is written once, for every storage format that encodes it. Releases are tags
`data-model-<version>` and `storage-format-<version>`, the text as first released; they are never
moved.

Each branch holds the current version of its part, with the corrections made since its release:
bug fixes to the prose, clarifications and non-normative additions, which do not open a new version.
They are pull requests against the branch, and the website shows them once merged. Older versions
stay as tagged; a correction to one, if needed, goes into a branch
`maintenance/storage-format-<version>` (or `maintenance/data-model-<version>`) made from its tag,
which the website then shows. A correction that touches both parts is two pull requests, one
against each branch, that link to each other.

A change that needs a new version makes the branch the draft of that version. Before its first such
change, the current version gets its branch `maintenance/storage-format-<version>`
(`maintenance/data-model-<version>`), which the website shows from then on. The pull request also
gives the draft's container format version a `-dev` suffix, marks the version as draft in the version
history, and lists the change in {ref}`storage-next`. Further changes for the same version edit the
draft.

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
3. the commit is tagged `storage-format-<version>` (and `data-model-<version>` on `data-model`, for
   a new data model version), and `versions.toml` on the branch `site` lists it, built from the
   branch, which publishes it on the website.

The normative content of a released version is not changed afterwards; corrections are made as
described above. Implementations adopt the version in their own releases; the
{ref}`compatibility-matrix` records which releases read and write it.

(contributing-structure)=
## Structure of the specification pages

`data-model.md`, on the branch `data-model`, holds the abstract data model. Each section's text, below its heading, sits
between two comment markers named after the section's label:

```text
(spec-tables)=
## Tables

% begin spec-tables
...
% end spec-tables
```

`storage-format.md`, on the branch `storage-format`, has the same sections. Each one repeats the
heading, includes the data model text between the markers, and follows it with the storage format;
the website build puts `data-model.md` next to it:

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

A change to the data model is therefore made once, in `data-model.md`, and appears on the data
model page and on the storage format page of every version that encodes it. Moving or renaming a
marker changes what the storage format pages include: the preview of a pull request against
`data-model` builds them all, so that a broken include shows there.
On the storage format page, the included text is marked *Data model* with a line beside it.

- **Data model sections** are normative, and readability comes first: plain, human-readable English
  for everyone, with RFC 2119 key words only where they make a constraint clearer. Prefer positive
  statements. Keep implementation details out; move history and outlook into
  footnotes (`[^name]`), with the footnote text inside the section's markers so that it is
  included with it. On screen, each footnote shows at its reference on hover or focus; in print,
  the page's last section, *Notes*, lists them.
- **Storage format sections** are normative and must be unambiguous. They state only what the
  storage format adds, and link to the data model for the concepts (`{ref}` to the `spec-*`
  anchors) instead of repeating them. Give every subsection heading a `storage-*` label.
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

- Where key words are used (always in the storage format), use MUST, SHOULD, MAY per RFC 2119, in plain capitals (not bold), and mean it.
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

The website, including this guide, is on the branch
[`site`](https://github.com/scverse/spatialdata-spec/tree/site), which builds every version listed in
its `versions.toml` into one site, and the RFCs, from the branch
[`rfcs`](https://github.com/scverse/spatialdata-spec/tree/rfcs), once, at its root; its README
describes how to build and preview it locally.

## Licensing

The text of the specification, of this guide and of the RFCs is licensed under
[CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/); the code (the website and the tools) under
BSD-3-Clause. A contribution is made under the same licences.
