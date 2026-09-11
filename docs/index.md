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
Three layers of interoperability for spatial omics data: what is on disk, what is in memory, and what it means.
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
{bdg-primary}`0.2 · status quo` {bdg-light}`0.1 · legacy` {bdg-light}`0.3 · placeholder`
:::

:::{grid-item-card} In-memory formats
:link: spec/in-memory/index
:link-type: doc
:class-card: sd-shadow-sm

One data model per implementation. Python (`spatialdata`) is documented;
R and JavaScript have placeholders.
+++
{bdg-success}`Python · status quo` {bdg-info}`R · JS · placeholders`
:::

:::{grid-item-card} Semantic conventions
:link: spec/semantic/index
:link-type: doc
:class-card: sd-shadow-sm

How biology (cells, genes, samples) maps onto elements.
Options for community review; nothing is mandated yet.
+++
{bdg-warning}`under discussion` {bdg-light}`no version yet`
:::
::::

## How this specification evolves

1. **Document the status quo.** The on-disk format and the Python in-memory model are written down
   exactly as `spatialdata` implements them today. Pages carrying {bdg-dark-line}`status quo` are
   descriptive, not proposals.
2. **Propose changes in the open.** Additions, removals and changes go through GitHub issues with
   the labels listed in {doc}`contributing_to_the_spec`. Implementation-specific matters are
   discussed in the implementation's own repository.
3. **Decide and version.** Agreed changes become a new numbered version of the affected document.
   Placeholders for upcoming versions exist so that the structure is visible before the content.
4. **Semantic conventions are entirely open.** Nothing in that layer is decided; the options listed
   there are a starting point for the community.

## Specification documents

| Document | Layer | Version | Status | Discuss changes at |
|----------|-------|---------|--------|--------------------|
| {doc}`On-disk format <spec/on-disk/index>` | {bdg-primary}`on-disk` | 0.2 (Zarr v3) | {bdg-dark-line}`status quo` | [spatialdata-spec](https://github.com/scverse/spatialdata-spec/issues) · label `format-change` |
| On-disk format 0.1 | {bdg-primary}`on-disk` | 0.1 (Zarr v2) | {bdg-secondary-line}`legacy` | in tabs of the 0.2 pages |
| {doc}`On-disk format, next <spec/on-disk/next>` | {bdg-primary}`on-disk` | 0.3 | {bdg-light}`placeholder` | [spatialdata-spec](https://github.com/scverse/spatialdata-spec/issues) · label `format-change` |
| {doc}`In-memory, general <spec/in-memory/index>` | {bdg-success}`in-memory` | — | {bdg-warning-line}`draft` | [spatialdata-spec](https://github.com/scverse/spatialdata-spec/issues) · label `in-memory-general` |
| {doc}`In-memory, Python <spec/in-memory/python/index>` | {bdg-success}`in-memory · Python` | spatialdata 0.8 | {bdg-dark-line}`status quo` | [scverse/spatialdata](https://github.com/scverse/spatialdata/issues) |
| {doc}`In-memory, R <spec/in-memory/r/index>` | {bdg-info}`in-memory · R` | — | {bdg-light}`placeholder` | [HelenaLC/spatialdataR](https://github.com/HelenaLC/spatialdataR/issues) |
| {doc}`In-memory, JavaScript <spec/in-memory/js/index>` | {bdg-info}`in-memory · JS` | — | {bdg-light}`placeholder` | [Taylor-CCB-Group/SpatialData.js](https://github.com/Taylor-CCB-Group/SpatialData.js/issues) |
| {doc}`Semantic conventions <spec/semantic/index>` | {bdg-warning}`semantic` | none yet (first will be 0.1) | {bdg-warning-line}`under discussion` | [spatialdata-spec](https://github.com/scverse/spatialdata-spec/issues) · label `semantic-conventions` |

Labels: {bdg-dark-line}`status quo` describes what is implemented · {bdg-secondary-line}`legacy`
is readable but no longer written · {bdg-warning-line}`draft` / {bdg-warning-line}`under discussion`
is text without normative force · {bdg-light}`placeholder` is a reserved page without content.

## Who should read what

| You are | Read |
|---------|------|
| Writing a reader or writer in R, JavaScript, Julia, Rust, ... | {doc}`On-disk format <spec/on-disk/index>` |
| Building an analysis or visualisation tool in Python on `spatialdata` | {doc}`In-memory format, Python <spec/in-memory/python/index>`, then the implementation guide |
| Implementing SpatialData in another language | {doc}`On-disk format <spec/on-disk/index>`, then {doc}`In-memory formats <spec/in-memory/index>` for what to document |
| Producing datasets and want other tools to find your cells, genes and samples | {doc}`Semantic conventions <spec/semantic/index>` |
| Checking whether a store is valid | {doc}`spec/on-disk/versions` and the linked schemas and examples |

## How the layers relate

```text
┌──────────────────────────────────────────────────────────────┐
│ 3. Semantic conventions        "obs column `cell_type`, ..."  │  language agnostic, draft
├──────────────────────────────────────────────────────────────┤
│ 2. In-memory formats           Python: spatialdata models     │  one per implementation
│                                R, JavaScript: placeholders    │
├──────────────────────────────────────────────────────────────┤
│ 1. On-disk format              Zarr + Parquet, NGFF-based     │  language agnostic
└──────────────────────────────────────────────────────────────┘
```

Layer 1 is the contract every implementation must honour. Layer 2 is documented once per
implementation; only the Python one lives here today. Layer 3 sits on top of both and contains the
only biological vocabulary in the whole stack.

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
