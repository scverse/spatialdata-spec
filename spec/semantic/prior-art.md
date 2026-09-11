# Prior art

Sources consulted when drafting the {doc}`options`. Licences were checked on 2026-09-11. No text or
schema has been copied; each source is cited as the origin of an idea. Projects under copyleft
licences (GPL) are inspiration only.

| Source | Licence | What it defines that is relevant here |
|--------|---------|----------------------------------------|
| [scanpy](https://github.com/scverse/scanpy) | BSD-3-Clause | De facto AnnData conventions: `var_names` as feature identifiers, `obs` columns for clusters and annotations, `uns["<col>_colors"]`, `obsm["X_<embedding>"]`, `layers["counts"]`, `raw`. |
| [squidpy](https://github.com/scverse/squidpy) | BSD-3-Clause | `obsm["spatial"]`, `obsp["spatial_connectivities"]` / `["spatial_distances"]`, `uns["spatial_neighbors"]`, `library_key` / `library_id` for multi-sample tables. Historically Visium-centric (`uns["spatial"][lib]["images"]`, `scalefactors`). |
| [muon](https://github.com/scverse/muon) / MuData | BSD-3-Clause | One AnnData per modality (`mod["rna"]`, `mod["prot"]`), shared `obs`, modality-prefixed columns. |
| [spatialdata-io](https://github.com/scverse/spatialdata-io) | BSD-3-Clause | Reader defaults: `region` (region key), `instance_id` / `cell_id` (instance key), points `feature_key` = gene column, element names such as `cell_boundaries`, `nucleus_boundaries`, `transcripts`, `<sample>_labels`. Implicit, per-reader conventions. |
| spatialdata-db (scverse, in development, not yet public) | to be confirmed on release | Dataset-level metadata in `sdata.attrs` (assay, organism, tissue, disease, preservation, instrument, software, …) validated by a [Lamin](https://docs.lamin.ai/) schema with ontology-backed fields via `bionty`; `var` index as Ensembl gene IDs. |
| [sopa](https://github.com/gustaveroussy/sopa) | BSD-3-Clause | Element roles recorded in `sdata.attrs` (which image is used for cell segmentation, which points element holds transcripts, which table holds bins, …) so that pipeline steps find their inputs without naming assumptions. |
| [CELLxGENE schema](https://github.com/chanzuckerberg/single-cell-curation) (v7.1) | MIT | Ontology-paired `obs` columns (`cell_type` + `cell_type_ontology_term_id`, `tissue`, `assay`, `disease`, `development_stage`, `sex`, `donor_id`, `suspension_type`, `tissue_type`), `uns["organism_ontology_term_id"]`, `uns["title"]`, Ensembl `var` index, and Visium-specific `obs["in_tissue"]`, `obs["array_row"]`, `obs["array_col"]`, `uns["spatial"]`. Ontologies: CL, UBERON, EFO, MONDO, PATO, NCBITaxon, HsapDv/MmusDv, HANCESTRO. |
| [Vitessce](https://github.com/vitessce/vitessce) | MIT | Entity-type coordination: `obsType` (e.g. cell, spot, molecule), `featureType` (e.g. gene, protein), `featureValueType` (e.g. expression); a viewer must be told what the observations and features *are*. |
| [Giotto](https://github.com/drieslab/Giotto) | MIT | Two orthogonal axes of organisation: *spatial unit* (`cell`, `nucleus`, …) × *feature type* (`rna`, `protein`, …); identifiers `cell_ID`, `feat_ID`. |
| [Seurat](https://github.com/satijalab/seurat) v5 | MIT | `FOV` objects grouping `Segmentation`, `Centroids` and `Molecules` per field of view; images and assays keyed by name. |
| [SpatialExperiment](https://github.com/drighelli/SpatialExperiment) | GPL-3 (ideas only) | `sample_id` column as the multi-sample key; `spatialCoords`; `imgData` table linking images to samples with scale factors; `in_tissue`. |
| [OME data model](https://www.openmicroscopy.org/Schemas/) | CC-BY-4.0 (documentation) | Channel metadata (`Name`, `Fluor`, emission/excitation wavelengths) as the way to say which marker an image channel shows. |
| 10x Genomics feature matrix conventions | vendor documentation | `var["gene_ids"]`, `var["feature_types"]` (`"Gene Expression"`, `"Antibody Capture"`, …) as widely present columns in real data. |

Not consulted, but candidates for a second pass: HuBMAP and HTAN metadata standards, MIxS / MIAME
for sample descriptors, the (unmerged) NGFF tables proposal, Bioconductor `SingleCellExperiment`
`altExps` for multi-modality.
