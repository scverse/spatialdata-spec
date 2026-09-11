# Options for review

Each question below lists candidate conventions. Options are not mutually exclusive unless stated.
"Storage" says where the information would live in the current format; options marked
{bdg-danger}`format change` need an extension of the on-disk format and are therefore more costly.

Vocabulary used in the examples: *role* = the function an element plays in the dataset;
*entity* = what one instance of a region represents; *feature type* = what one variable measures.

## Q1 — Which element plays which role?

Typical roles: `cell_segmentation`, `nucleus_segmentation`, `cell_boundaries`, `tissue_image`,
`transcripts`, `bins`, `tissue_segmentation`, `landmarks`.

| Option | Storage | Discoverable | Format change | Prior art |
|--------|---------|:------------:|:-------------:|-----------|
| A. Role map in `sdata.attrs` | root attributes | ✅ | no | sopa |
| B. Element naming pattern | element names | ✗ | no | spatialdata-io readers |
| C. Per-element role attribute | element attributes | ✅ | **yes** | — |

::::{tab-set}
:::{tab-item} A · role map in attrs
```json
"spatialdata_semantic": {
  "version": "0.1",
  "roles": {
    "cell_segmentation": ["cells_labels"],
    "nucleus_segmentation": ["nuclei_labels"],
    "tissue_image": ["he_image"],
    "transcripts": ["transcripts"]
  }
}
```
One namespaced object at the root, roles as keys, element names as values (lists, to allow several
samples). Cheap, language agnostic, survives element renaming only if updated together (the
`SpatialData` object can do that). Roles need a controlled list with an escape hatch for custom
roles (`x-` prefix).
:::
:::{tab-item} B · naming pattern
Element names such as `cell_boundaries`, `nucleus_boundaries`, `transcripts` (what `spatialdata-io`
writes today). Zero cost and already widespread, but not discoverable: multi-sample datasets need
prefixes, names collide, and tools end up with regular expressions. At most a **SHOULD** recommend
default names when Option A is absent.
:::
:::{tab-item} C · per-element attribute
`labels/cells_labels` attributes gain `"spatialdata_semantic": {"role": "cell_segmentation"}`.
The role travels with the element when it is copied between stores, and needs no central registry.
Costs an on-disk extension for every element type (raster attributes today carry only NGFF metadata
and `spatialdata_attrs.version`; GeoDataFrame and DataArray `attrs` are not persisted).
:::
::::

## Q2 — What does an instance represent?

Values (draft, extensible): `cell`, `nucleus`, `spot`, `bin`, `molecule`, `roi`, `tissue_region`,
`fov`, `bead`.

| Option | Storage | Granularity | Format change | Prior art |
|--------|---------|-------------|:-------------:|-----------|
| A. Entity per region element in the role map | `sdata.attrs` | element | no | Vitessce `obsType`, Giotto `spat_unit` |
| B. Entity in table `uns` | table `uns["spatialdata_semantic"]["entity"]` | table | no | — |
| C. Entity column in `obs` | table `obs` | row | no | CELLxGENE `suspension_type` (analogous) |

::::{tab-set}
:::{tab-item} A · in the role map
```json
"spatialdata_semantic": {
  "elements": {
    "cells_labels":  { "entity": "cell" },
    "nuclei_labels": { "entity": "nucleus" },
    "bins_008um":    { "entity": "bin", "bin_size": { "value": 8, "unit": "micrometer" } }
  }
}
```
Same place as Q1-A; one object per element name. A viewer can label its legend "cells" instead of
"instances" without opening a table.
:::
:::{tab-item} B · in table uns
```python
adata.uns["spatialdata_semantic"] = {"entity": "cell"}
```
Natural when the table is the unit of analysis, but a table may annotate several regions with
different entities, and shapes/points elements without a table would have no entity.
:::
:::{tab-item} C · obs column
An `obs["entity"]` categorical column. Maximal flexibility (mixed tables), minimal discoverability,
and redundant with `region_key` in almost all real datasets. Listed for completeness.
:::
::::

## Q3 — What do variables measure, and which identifiers?

| Option | Storage | Format change | Prior art |
|--------|---------|:-------------:|-----------|
| A. `var` columns: `feature_type` + identifier columns | table `var` | no | 10x `feature_types`, CELLxGENE Ensembl index |
| B. One table per modality, feature type in `uns` | tables + `uns` | no | muon, Giotto `feat_type` |
| C. Feature type per element in the role map | `sdata.attrs` | no | Vitessce `featureType` |

::::{tab-set}
:::{tab-item} A · var columns
```text
var index      feature_type    gene_symbol   ensembl_id
ENSG00000075624  gene          ACTB          ENSG00000075624
CD3E_protein     protein       CD3E          —
```
Recommend `var["feature_type"]` categorical from a small vocabulary (`gene`, `transcript`, `protein`,
`peak`, `metabolite`, `other`), and identifier columns named after the identifier system
(`ensembl_id`, `gene_symbol`, `uniprot_id`, `hgnc_id`). Leave the index free (Ensembl IDs recommended
for genes, following CELLxGENE and spatialdata-db) but never *required*, since many assays use panel
names.
:::
:::{tab-item} B · one table per modality
`tables["rna"]`, `tables["protein"]`, each with `uns["spatialdata_semantic"]["feature_type"]`. Clean
for multi-omics and matches muon; requires the same `region`/`instance_key` in each table to join
modalities, and a naming or role convention (Q1) to find them.
:::
:::{tab-item} C · in the role map
`"elements": {"table": {"feature_type": "gene"}}`. Discoverable without opening the table, but
cannot describe mixed tables; complements A.
:::
::::

## Q4 — Points: what is the feature, what is the parent instance?

Points already carry `feature_key` and `instance_key` in `spatialdata_attrs`. What is missing is
*which element* the `instance_key` values refer to.

| Option | Storage | Format change | Prior art |
|--------|---------|:-------------:|-----------|
| A. `instance_key_element` next to `instance_key` | points `spatialdata_attrs` | **yes** (small) | — |
| B. Link recorded in the role map | `sdata.attrs` | no | — |
| C. Convention: refers to the element named in the role `cell_segmentation` | none | no | implicit today |

::::{tab-set}
:::{tab-item} A · extend spatialdata_attrs
```json
"spatialdata_attrs": { "version": "0.3", "feature_key": "gene", "instance_key": "cell_id",
                       "instance_key_element": "cells_labels" }
```
Most precise; also lets points be annotated by tables the way regions are. Needs a points format
bump and the same discussion as the `instance_key` deprecation proposal in `spatialdata`.
:::
:::{tab-item} B · in the role map
`"links": [{"from": "transcripts", "column": "cell_id", "to": "cells_labels"}]`. General (works for
any column of any element) and needs no format change; less local.
:::
:::{tab-item} C · implicit
Tools assume `instance_key` refers to the `cell_segmentation` role of Q1. Works for the common case
only.
:::
::::

## Q5 — Dataset- and sample-level metadata

Organism, tissue, assay, disease, development stage, sex, donor, preservation, instrument, software,
publication.

| Option | Storage | Multi-sample | Format change | Prior art |
|--------|---------|:------------:|:-------------:|-----------|
| A. Structured object in `sdata.attrs`, ontology-paired | root attributes | via a `samples` list | no | spatialdata-db, CELLxGENE `uns` |
| B. `obs` columns, ontology-paired | table `obs` | per row | no | CELLxGENE |
| C. Both: A for the dataset, B for per-instance overrides | both | ✅ | no | — |

::::{tab-set}
:::{tab-item} A · in attrs
```json
"spatialdata_semantic": {
  "dataset": {
    "title": "Human breast cancer, immunology panel",
    "organism": { "label": "Homo sapiens", "ontology_term_id": "NCBITaxon:9606" },
    "assay":    { "label": "Visium",       "ontology_term_id": "EFO:0010961" },
    "tissue":   { "label": "breast",       "ontology_term_id": "UBERON:0000310" },
    "disease":  { "label": "invasive lobular carcinoma", "ontology_term_id": "MONDO:0005224" }
  },
  "samples": [ { "id": "S1", "coordinate_system": "S1", "donor_id": "D1", "elements": ["S1_image", "S1_cells"] } ]
}
```
Every ontology-backed field is a `{label, ontology_term_id}` pair (CELLxGENE style). Ontologies as in
CELLxGENE: NCBITaxon, UBERON, CL, EFO, MONDO, PATO, HsapDv/MmusDv. The `samples` list is the only
place that would say which elements and coordinate system belong to which sample.
:::
:::{tab-item} B · obs columns
`obs["donor_id"]`, `obs["tissue"]`, `obs["tissue_ontology_term_id"]`, `obs["sample_id"]` …
Required when a single table mixes samples with different metadata; verbose and repetitive
otherwise, and invisible to tools that never open the table.
:::
:::{tab-item} C · both
Dataset defaults in `attrs`, per-row exceptions in `obs`; a reader resolves row → sample → dataset.
The most complete option and the one most in line with how CELLxGENE and spatialdata-db already
differ.
:::
::::

## Q6 — Cell type and other per-instance annotations

| Option | Storage | Format change | Prior art |
|--------|---------|:-------------:|-----------|
| A. Reserved column names with ontology pairs | table `obs` | no | CELLxGENE |
| B. Registry of "annotation columns" in `uns` | table `uns` | no | scanpy `_colors` pattern |
| C. Free, discover categoricals | — | no | spatialdata-plot, napari-spatialdata |

::::{tab-set}
:::{tab-item} A · reserved names
`obs["cell_type"]` (categorical label) paired with `obs["cell_type_ontology_term_id"]` (CL term or
`"unknown"`). Same pattern for `tissue_region`, `niche`, `phenotype`. Colours in
`uns["cell_type_colors"]` (scanpy). Simple and already what most people write.
:::
:::{tab-item} B · registry
`uns["spatialdata_semantic"]["annotations"] = {"cell_type": {"ontology": "CL", "column": "celltype_v2"}}`
decouples the semantic role from the column name so existing datasets need not be renamed.
:::
:::{tab-item} C · free
Tools treat every categorical `obs` column as a candidate annotation and let the user pick. Status
quo; nothing to agree on, nothing to rely on.
:::
::::

## Q7 — Spatial graphs

Squidpy's `obsp["spatial_connectivities"]`, `obsp["spatial_distances"]` and
`uns["spatial_neighbors"]` are the de facto standard and need no change. The open point is
recording **in which coordinate system** the graph was built:

- A. `uns["spatial_neighbors"]["coordinate_system"] = "global"` (extend the existing `uns` entry).
- B. Encode it in the key: `obsp["spatial_connectivities_global"]`.

## Q8 — Multiple samples

| Option | Storage | Format change | Prior art |
|--------|---------|:-------------:|-----------|
| A. One coordinate system per sample, named after it | coordinate system names | no | spatialdata practice |
| B. `samples` list in `attrs` (see Q5-A) | root attributes | no | SpatialExperiment `sample_id`, squidpy `library_id` |
| C. `obs["sample_id"]` column | table `obs` | no | SpatialExperiment, CELLxGENE `donor_id` |

These combine: A places elements, B lists samples and their elements, C tags rows. A alone is
ambiguous (a coordinate system may also be a registration target). The proposal is B as the
authoritative list, with A and C as recommended practice.

## Q9 — Physical units of coordinate systems

Today every axis unit on disk is the placeholder `"unit"`. Two levels:

- A. **Format fix**: write the real unit (UDUNITS/NGFF vocabulary, e.g. `micrometer`) in the axis
  objects, and expose it in Python. {bdg-danger}`format change` (small; NGFF-compatible).
- B. **Convention**: name the physical coordinate system after the unit or the sample (`"microns"`,
  `"S1_um"`) and record it in the `samples` list (`"coordinate_system": "S1_um"`).

A is the right long-term answer; B is what people do now.

## Q10 — Image channels and markers

- A. Channel names (`omero.channels[*].label`) **are** the marker names (`"DAPI"`, `"CD3"`,
  `"PanCK"`), as today. Recommend a `var`-like lookup: `attrs["spatialdata_semantic"]["channels"]["he_image"] = [{"label": "CD3", "target": {"label": "CD3E", "uniprot_id": "P07766"}}]`.
- B. Reuse OME `omero.channels[*]` fields (`color`, `window`) for display and add nothing.
- C. RGB convention: labels `r`, `g`, `b` (`, a`) mean a colour photograph, not markers (already
  a practice in `spatialdata`).

## Q11 — Provenance between elements

Which labels were computed from which image, which table from which segmentation.

- A. `"derived_from": {"cells_labels": ["he_image"], "table": ["cells_labels"]}` in the role map.
- B. Nothing; rely on coordinate systems and documentation (status quo).

## Summary matrix

| Question | Leading option (for discussion) | Needs format change |
|----------|--------------------------------|:-------------------:|
| Q1 roles | A · role map in `sdata.attrs["spatialdata_semantic"]` | no |
| Q2 entity | A · per element in the same object | no |
| Q3 features | A · `var["feature_type"]` + identifier columns | no |
| Q4 points parent | A · `instance_key_element` | yes (small) |
| Q5 metadata | C · dataset in `attrs`, overrides in `obs` | no |
| Q6 annotations | A · reserved names + ontology pairs | no |
| Q7 graphs | A · record coordinate system in `uns` | no |
| Q8 samples | B (+ A, C) | no |
| Q9 units | A · real units on disk | yes (small) |
| Q10 channels | A · channel labels + target lookup | no |
| Q11 provenance | A · `derived_from` | no |

:::{admonition} Open question
:class: open-question

Should all of the above live under one root object `sdata.attrs["spatialdata_semantic"]` with its
own version, or be split (roles/entities/samples in `attrs`, everything about variables and
annotations in the tables)? One object is easier to validate with a single JSON schema; the split
keeps table conventions usable by plain AnnData tools.
:::
