# Contributing (specifications)

## Process

1. Suggest a change in a [GitHub issue](https://github.com/scverse/spatialdata-spec/issues),
   ideally together with a pull request.
2. A particularly large feature or a big breaking change comes with an RFC (see
   {ref}`contributing-rfcs`).
3. Once an issue or RFC is approved, the change lands in the next version of the specification
   (see {doc}`spec/storage-format/next`); the {ref}`compatibility-matrix` records which implementation
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
   (*container-format-0.3 (draft)*, see {doc}`spec/storage-format/next`) and in the implementations. Its
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
  footnotes (`[^name]`). On screen, footnotes open as popups at their reference; the page's last
  section, *Notes*, holds the footnote list for print and readers without JavaScript.
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
- The storage format covers all versions ({ref}`storage-versions`). Where versions differ, put
  them in inline tabs (`tab-set`) in the sync group `storage-version`, labelled with the container
  format, newest
  first, so that selecting a version switches all version tabs on the page. Mark the latest
  released version `:selected:`, so that the draft of the next version is never shown by default:

  ```text
  ::::{tab-set}
  :sync-group: storage-version
  :::{tab-item} spatialdata-container-format-0.3 (draft)
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

- **Proposing a change for the next version.** The draft of 0.3 is the same as 0.2 except where it
  has a tab of its own, so do not copy unchanged text. Add a `spatialdata-container-format-0.3
  (draft)` tab only to the passages your change touches, starting from a copy of the 0.2 tab; if
  the passage has no version tabs yet, wrap it in a 0.3 (draft) tab and a 0.2 tab (and 0.1, if it
  applies). The diff of the pull request then shows exactly what changes, and readers who select
  *container-format-0.3 (draft)* see the 0.2 text everywhere else and the change marked. List the
  change on {doc}`spec/storage-format/next`.
- A whole rubric section that exists only in some versions gets a badge after its heading, for example {bdg-secondary}`container 0.3 only` or
  {bdg-secondary}`removed in 0.3`.

- **In-memory tabs** describe what one implementation exposes after reading a store: its objects,
  their fields, and the invariants a tool can rely on. So that the languages stay comparable, they
  answer the same questions: which native type represents each element type; where the
  SpatialData metadata lives (transformations, table keys); whether the element knows its name;
  how an object is validated and built from raw data; which storage versions are read and written,
  and what is lost on a round trip; what is loaded lazily; and which release is described. Topics
  specific to one language (API shape, class names, dependencies) are discussed in that
  implementation's repository and reflected here after release.
- Use the custom admonitions:
  - *Implementation note* (`implementation-note`, non-normative);
  - *Divergence from NGFF* (`ngff-divergence`);
  - *Open question* (`open-question`), for decisions that are still open.
- JSON examples come from real stores; abbreviate with `...` if needed.
- Cite with `{cite:p}` (entries in `docs/references.bib`). Each citing page ends with its own
  `{bibliography}` with `:filter: docname in docnames`; there is no global references page.
- Short sentences, no filler. If a paragraph does not change what an implementer would do, delete
  it.

## Building the site

Building, previewing and hosting the site are described in {ref}`docs-building`.

## Licensing

See the [README](https://github.com/scverse/spatialdata-spec#license).
