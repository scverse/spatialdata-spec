---
sd_hide_title: true
---

# SpatialData specification

::::{grid} 1
:class-container: sd-text-center sd-mb-4

:::{grid-item}
:class: sd-fs-2 sd-font-weight-bold sd-mt-4
SpatialData specification
:::
:::{grid-item}
:class: sd-fs-5 sd-text-muted
Three layers of interoperability for spatial omics data: what is on disk, what is in memory, and what it means in biological terms.
:::
::::

::::{grid} 1 1 3 3
:gutter: 3

:::{grid-item-card} On-disk format
:link: spec/on-disk/index
:link-type: doc
:class-card: sd-shadow-sm

Zarr + Parquet, built on OME-NGFF. Language agnostic.
For implementers of readers and writers in any language.
+++
{bdg-primary}`spatialdata-container-format-0.2` {bdg-light}`spatialdata-container-format-0.1` {bdg-light}`0.3 · placeholder`
:::

:::{grid-item-card} In-memory formats
:link: spec/in-memory/index
:link-type: doc
:class-card: sd-shadow-sm

One data model per implementation. Python (`spatialdata`) is documented;
R and JavaScript have placeholders.
+++
{bdg-success}`Python · spatialdata 0.8` {bdg-info}`R · JS · placeholders`
:::

:::{grid-item-card} Semantic conventions
:link: spec/semantic/index
:link-type: doc
:class-card: sd-shadow-sm

How biology (cells, genes, samples) maps onto elements.
Experimental; feedback is highly valuable.
+++
{bdg-warning}`proposed` {bdg-light}`no version yet`
:::
::::

## How this specification evolves

1. **Everything is versioned.** The on-disk format and the Python in-memory model are written down
   exactly as `spatialdata` implements them, each with the version it describes. Content
   without a version is {bdg-warning-line}`proposed`.
2. **Propose changes in the open.** Changes go through GitHub issues, ideally with a pull request;
   large features and big breaking changes are accompanied by an RFC. See
   {doc}`contributing_to_the_spec`. Implementation-specific matters are discussed in the
   implementation's own repository.
3. **Decide and version.** Approved changes land in a new `spatialdata` version and the
   compatibility matrix is updated. Placeholders for upcoming versions exist so that the structure
   is visible before the content.
4. **Detect drift automatically.** A CI mechanism will flag version drift between the
   implementations (across languages), the files they produce, and the specification.
5. **Semantic conventions are entirely open.** Nothing in that layer is decided; the options listed
   there are a starting point for the community.

## Specification documents

**On-disk format**

| Document | Version |
|----------|---------|
| {doc}`Candidate changes <spec/on-disk/next>` | {bdg-warning-line}`proposed` — not yet assigned to a version |
| {doc}`On-disk format 0.3 (incoming) <spec/on-disk/index>` | {bdg-light}`incoming` — 0.3 tabs in the chapters (none yet) |
| {doc}`On-disk format 0.2 <spec/on-disk/index>` | {bdg-dark-line}`spatialdata-container-format-0.2` — 0.2 tabs, shown by default |
| {doc}`On-disk format 0.1 <spec/on-disk/index>` | {bdg-dark-line}`spatialdata-container-format-0.1` — 0.1 tabs |

**In-memory formats**

| Document | Version |
|----------|---------|
| {doc}`In-memory, Python <spec/in-memory/python/index>` | {bdg-dark-line}`spatialdata 0.8` |
| {doc}`In-memory, R <spec/in-memory/r/index>` | {bdg-light}`placeholder` |
| {doc}`In-memory, JavaScript <spec/in-memory/js/index>` | {bdg-light}`placeholder` |

**Semantic conventions**

| Document | Version |
|----------|---------|
| {doc}`Semantic conventions <spec/semantic/index>` | {bdg-warning-line}`proposed` |

Labels: a {bdg-dark-line}`version` badge (a format tag or a software version) marks content that
describes a released version; how versions relate is in the {ref}`compatibility-matrix` ·
{bdg-warning-line}`proposed` has no version yet and no normative force · {bdg-light}`placeholder` is
a reserved page without content.

## Who should read what

| You are | Read |
|---------|------|
| Writing a reader or writer in R, JavaScript, Julia, Rust, ... | {doc}`On-disk format <spec/on-disk/index>` |
| Building an analysis or visualisation tool in Python on `spatialdata` | {doc}`In-memory format, Python <spec/in-memory/python/index>`, then the implementation guide |
| Implementing SpatialData in another language | {doc}`On-disk format <spec/on-disk/index>`, then {doc}`In-memory formats <spec/in-memory/index>` for what to document |
| Producing datasets and want other tools to find your cells, genes and samples | {doc}`Semantic conventions <spec/semantic/index>` (highly experimental at this stage) |
| Checking whether a store is valid | {doc}`Version history and compatibility matrix <spec/on-disk/versions>`, and the linked schemas and examples |

## How the layers relate

```text
┌──────────────────────────────────────────────────────────────┐
│ 1. On-disk format         Zarr + Parquet, NGFF-based         │  language agnostic
├──────────────────────────────────────────────────────────────┤
│ 2. In-memory formats      e.g. Python: spatialdata models    │  one per implementation
├──────────────────────────────────────────────────────────────┤
│ 3. Semantic conventions   e.g. obs column "cell_type"        │  language agnostic, experimental
└──────────────────────────────────────────────────────────────┘
```

Layer 1 defines what every implementation reads and writes. Layer 2 is documented once per
implementation. Layer 3, once it goes beyond the experimental stage, sits on top of both and contains
the only biological vocabulary in the whole stack.

## Status

This specification is being extracted from the `spatialdata` design document and code base. It
describes the format as written by `spatialdata` 0.6 to 0.8 and the Python model of `spatialdata`
0.8. Open decisions are marked with *Open
question* boxes. See {doc}`contributing_to_the_spec` to comment.

```{toctree}
:hidden: true
:maxdepth: 2

spec/on-disk/index
spec/in-memory/index
spec/semantic/index
```

```{toctree}
:hidden: true
:caption: Project
:maxdepth: 1

glossary
contributing_to_the_spec
contributing
changelog
references
```
