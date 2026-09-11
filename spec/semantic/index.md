# Semantic conventions

{bdg-warning}`semantic` {bdg-warning-line}`under discussion` {bdg-light}`no version yet` {bdg-light}`language agnostic`

The on-disk and in-memory formats contain no biological vocabulary. They know *elements*,
*instances* and *variables*; they do not know *cells*, *nuclei*, *genes*, *proteins*, *samples* or
*donors*. That is deliberate: it keeps the formats stable while assays change. It also means that
today every tool has to guess, or ask the user, which labels element holds the cells, which `obs`
column is the cell type, which `var` index is a gene identifier, and which coordinate system is in
microns.

This section is the place to agree on such conventions. Unlike the other two layers it does not
specify anything yet and is entirely open: the options below are a starting point for discussion,
not a proposal by the maintainers. The first normative version will be numbered 0.1. It lists the questions a convention has to answer and, for each, the
candidate answers with their trade-offs and the prior art they come from, so that the community can
review them side by side.

## Scope

A semantic convention answers questions like:

- Which element is the cell segmentation? The nucleus segmentation? The tissue image?
- What does one instance of a region represent (cell, nucleus, spot, bin, molecule, ROI)?
- What do the variables of a table measure (gene, protein, peak, …), and which identifier system do
  they use?
- Which `obs` columns carry sample, donor, tissue, disease, cell type, and which ontologies?
- Which coordinate system is the physical one, and in which unit?
- Which image channels correspond to which markers?
- Which elements were derived from which?

It does **not** define analysis outputs beyond the entry points above, and it does not restrict
what else a dataset may contain.

## Guiding principles for evaluating options

1. **Persisted.** A convention that lives only in Python memory is not a convention. Anything
   proposed must map to something the {doc}`on-disk format <../on-disk/index>` already stores
   (`sdata.attrs`, table `obs` / `var` / `uns`, element names, points `spatialdata_attrs`) or be
   explicitly flagged as requiring a format extension.
2. **Discoverable, not guessed.** Prefer an explicit key over a naming pattern. `attrs["roles"]["cell_segmentation"] = "cells"`
   beats "the labels element whose name contains `cell`".
3. **Optional and layered.** A dataset without any convention is still valid. Tools **SHOULD**
   degrade gracefully when a key is absent.
4. **Technology agnostic.** No convention may assume spots, fields of view, a particular vendor's
   column names, or 2D only.
5. **Ontology friendly.** Where a controlled vocabulary exists (Cell Ontology, UBERON, EFO,
   NCBITaxon, MONDO, …) the convention should allow, and preferably pair, a human-readable label
   with an ontology term identifier.
6. **Minimal.** Reuse existing scverse and community conventions where they are already de facto
   standards, and do not invent a second name for the same thing.

## How to read the options

{doc}`options` is organised by question. Each question has a short summary matrix and one tab per
option with: where the information is stored, an example, what it costs, and where the idea comes
from. {doc}`prior-art` lists the sources consulted, with their licences; nothing has been copied from
them, and GPL-licensed projects are cited for ideas only.

## How to give feedback

- Open an issue in [scverse/spatialdata-spec](https://github.com/scverse/spatialdata-spec/issues)
  with the label `semantic-conventions`, naming the question (e.g. "Q3 feature identifiers") and
  the option you support or a new one.
- Describe the data you work with. Conventions that only fit one technology will be rejected.
- Once an option gathers consensus it is promoted to a normative page with `MUST` / `SHOULD`
  language and a version number, and `spatialdata`, `spatialdata-io` and `spatialdata-plot` adopt
  it.

```{toctree}
:maxdepth: 1
:hidden:

options
prior-art
```
