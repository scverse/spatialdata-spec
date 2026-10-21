# Contributing (specifications)

## Process

1. Suggest a change in a [GitHub issue](https://github.com/scverse/spatialdata-spec/issues),
   ideally together with a pull request.
2. A particularly large feature or a big breaking change comes with an RFC (see
   {ref}`contributing-rfcs`).
3. Once an issue or RFC is approved, the change lands in the next version of the specification
   (see {doc}`next`); the {ref}`compatibility-matrix` records which implementation
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

### Process

1. **Propose.** Open a pull request that adds the RFC as a Markdown file `rfcs/<number>-<name>.md`,
   based on the template below. Numbers are sequential in order of proposal, assigned when an RFC
   is listed on the {doc}`RFC page <rfcs>`, and never reused (e.g. `rfcs/0001-transformations.md`).
   An RFC that started elsewhere (a discussion, a fork) is listed there with a link and moves into
   `rfcs/` when it is formally presented for review.
2. **Discuss.** Comments go to the pull request. The RFC is revised until the discussion converges.
3. **Decide.** The SpatialData developers decide, following the consensus-seeking process of the
   [scverse governance](https://github.com/scverse/governance/blob/main/roles.md#decision-making-process).
   The decision and its reasons are recorded in the RFC, which is then merged with the status
   *accepted* or *rejected*, so that the record stays.
4. **Implement.** An accepted RFC lands in the specification as tabs of the next storage version
   (*container-format-0.3 (draft)*, see {doc}`next`) and in the implementations. Its
   status becomes *implemented* with the release that writes the new version.

### Template

```text
# RFC: <title>

## Authors and acknowledgements
## Summary            one paragraph: what changes, for whom
## Motivation         the problem, with concrete use cases
## Proposal
### Data model        new or changed concepts, in plain language
### Storage format    the bytes that change; new container version
### In-memory formats per language, where affected
## Compatibility      reading old stores, writing new ones, migration
## Alternatives       designs considered and why they were not chosen
## Open questions
## Decision           filled in when the RFC is accepted or rejected
## References
```

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
  included with it. On screen, footnotes open as popups at their reference; each page's last
  section, *Notes*, holds the footnote list for print and readers without JavaScript.
- **Storage format sections** are normative. They state only what the storage format adds, and
  link to the data model for the concepts (`{ref}` to the `spec-*` anchors) instead of repeating
  them. Give every subsection heading a `storage-*` label.
- **Section headings** cannot go inside tabs. There, use a rubric with a label, which gets a "¶"
  permalink that also records the selected tabs:

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
- The storage format covers all versions ({ref}`storage-versions`). Where versions differ, put
  them in inline tabs (`tab-set`) in the sync group `storage-version`, newest first, labelled with
  the storage format versions they apply to and synced with `sf-<first>[-<last>]`. Mark the latest
  released version `:selected:`, so that the draft of the next version is never shown by default.
  A version without a tab does not have the passage. Tabs may be nested if each level uses fewer
  colons than the one around it:

  ```text
  ::::{tab-set}
  :sync-group: storage-version
  :::{tab-item} Storage format 0.6 (draft)
  :sync: sf-0.6

  Content for storage format 0.6.
  :::
  :::{tab-item} Storage format 0.5
  :sync: sf-0.5
  :selected:

  Content for storage format 0.5.
  :::
  :::{tab-item} Storage format 0.1–0.4
  :sync: sf-0.1-0.4

  Content for storage formats 0.1 to 0.4.
  :::
  ::::
  ```

  Each version is published as a page of its own, with only its tabs; write every tab so that it
  reads as the specification of that version alone, without referring to other versions.
- **Proposing a change for the next version.** The draft is the same as the latest release except
  where it has a tab of its own, so do not copy unchanged text. Add a `Storage format 0.6 (draft)`
  tab only to the passages your change touches, starting from a copy of the tab of the latest
  release; if the passage has no version tabs yet, wrap it in a draft tab and a tab for the
  released versions. The diff of the pull request then shows exactly what changes. List the
  change on {doc}`next`.
- The normative text specifies the format, not an implementation: name the `spatialdata` package
  (or another implementation) only in implementation notes and footnotes.

- Use the custom admonitions:
  - *Implementation note* (`implementation-note`, non-normative);
  - *Divergence from NGFF* (`ngff-divergence`);
  - *Open question* (`open-question`), for decisions that are still open.
- JSON examples come from real stores; abbreviate with `...` if needed.
- Cite as a link, for example `([Marconato et al., 2025](https://doi.org/10.1038/s41592-024-02212-x))`.
- Short sentences, no filler. If a paragraph does not change what an implementer would do, delete
  it.

## Building the site

The website code is on the branch [`site`](https://github.com/scverse/spatialdata-spec/tree/site),
which builds every tagged version into one site; its README describes how to build and preview it
locally.

## Licensing

See the [README](https://github.com/scverse/spatialdata-spec#license).
