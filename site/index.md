# ![](img/spatialdata_icon.png){.heading-icon} SpatialData specifications

SpatialData is an open framework for working with uni- and multi-modal spatial omics datasets. It
defines a common data model and storage format, supported by software libraries for accessing,
manipulating and analyzing spatial omics data in languages including Python, R and JavaScript.

This site provides the normative, language-independent specifications of the SpatialData abstract
data model and storage format.

::::::{grid} 1 1 2 2
:gutter: 3
:class-container: landing-cards

:::::{grid-item}
:class: sd-d-flex-column

::::{card} Abstract data model
:link: data-model
:link-type: doc
:class-card: sd-shadow-sm

What a SpatialData dataset is: elements, coordinate systems, instances and annotation tables.
::::

For anyone working with SpatialData datasets.
:::::

:::::{grid-item}
:class: sd-d-flex-column

::::{card} Storage format
:link: storage-format
:link-type: doc
:class-card: sd-shadow-sm

How datasets are stored on disk: Zarr and Parquet, building on OME-NGFF.
::::

For developers of readers and writers.
:::::

::::::

The storage format implements the abstract data model on disk. A change to the data model requires
a new storage format version, but the storage format can evolve without changing the data model:
storage format versions 0.1–0.4 all implement data model 1.0 (see the
{doc}`version history <storage-format-versions>`).

SpatialData originated as the Python `spatialdata` package. For installation, tutorials and Python
API documentation, see the [SpatialData Python documentation](https://spatialdata.scverse.org).

## Status and contributing

The specification is being extracted from the `spatialdata` design document and code base. Each
storage format version describes the format as written by the `spatialdata` releases listed for it
in the {doc}`version history <storage-format-versions>`. Changes are proposed in GitHub issues,
ideally with a pull request; large features and breaking changes come with an {doc}`RFC <rfcs>`. See
{doc}`contributing`.

To cite SpatialData, please see our
[publication](https://doi.org/10.1038/s41592-024-02212-x).

## Funding

SpatialData is part of the scverse® project ([website](https://scverse.org),
[governance](https://scverse.org/about/roles)) and is fiscally sponsored by
[NumFOCUS](https://numfocus.org/). If you like scverse® and want to support our mission, please
consider making a tax-deductible [donation](https://numfocus.org/donate-to-scverse) to help the
project pay for developer time, professional services, travel, workshops, and a variety of other
needs.

The SpatialData project also received support by the Chan Zuckerberg Initiative.

SpatialData is an approved de.NBI service, your feedback helps us improve it. We would appreciate it
if you could take a moment to complete
[our short user survey](https://www.surveymonkey.de/r/denbi-service?sc=hd-hub&tool=spatialdata) (2 minutes).

<div class="funding-logos">
  <a href="https://numfocus.org/project/scverse"><img height="60" alt="NumFOCUS"
     src="https://raw.githubusercontent.com/numfocus/templates/master/images/numfocus-logo.png"></a>
  <a href="https://www.denbi.de/"><img height="60" alt="de.NBI"
     src="https://www.denbi.de/templates/nbimaster/img/denbi-logo-color.svg"></a>
</div>

```{toctree}
:hidden: true
:maxdepth: 2

data-model
storage-format
rfcs
contributing
```
