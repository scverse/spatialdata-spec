# ![](img/spatialdata_icon.png){.heading-icon} SpatialData specifications

SpatialData is a data framework, a schema and a serialization format for uni- and multi-modal spatial omics datasets. It is supported by a growing suite of software libraries for performant access, manipulation and analysis in multiple languages, including Python, R and JavaScript.

This site specifies SpatialData independently of any implementation, so that all implementations
read and write the same datasets and agree on what they mean.

::::{grid} 1 1 2 2
:gutter: 3

:::{grid-item-card} Abstract data model
:link: data-model
:link-type: doc
:class-card: sd-shadow-sm

What a SpatialData dataset is: elements, coordinate systems, instances and annotation tables, in
plain language.
:::

:::{grid-item-card} Storage format
:link: storage-format
:link-type: doc
:class-card: sd-shadow-sm

How a dataset is stored: Zarr and Parquet, built on OME-NGFF. Normative and language agnostic.
:::

::::

## Status and contributing

The specification is being extracted from the `spatialdata` design document and code base and
describes the format as written by `spatialdata` 0.6 to 0.8. Changes are proposed in GitHub issues,
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
