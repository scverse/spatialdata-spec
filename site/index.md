# ![](_static/img/spatialdata_icon.svg){.heading-icon} SpatialData specifications

SpatialData is an open framework for working with uni- and multi-modal spatial omics datasets. It
defines a common data model and storage format, supported by software libraries for accessing,
manipulating and analyzing spatial omics data in languages including Python, R and JavaScript.

This site provides the normative, language-independent specifications of the SpatialData abstract
data model and storage format.

::::{grid} 1 1 2 2
:gutter: 3

:::{grid-item-card} Abstract data model
:link: data-model
:link-type: doc
:class-card: sd-shadow-sm

What a SpatialData dataset is: elements, coordinate systems, instances and annotation tables.
:::

:::{grid-item-card} Storage format
:link: storage-format
:link-type: doc
:class-card: sd-shadow-sm

How datasets are stored on disk: Zarr and Parquet, building on OME-NGFF.
:::

::::

The storage format implements the data model on disk, and its version identifies the data model
version: storage format 0.1–0.4 all implement data model 1.0
({doc}`version history <storage-format-versions>`).

## Background and contributing

The SpatialData specifications were developed from the design and implementation of the original
Python `spatialdata` package (see the [SpatialData Python documentation](https://spatialdata.scverse.org)
for installation, tutorials and API reference). Their initial release formalized abstract data model 1.0
and storage format 0.4; earlier storage formats (0.1–0.3) are also specified, with the corresponding
`spatialdata` releases listed in the {doc}`version history <storage-format-versions>`.

The specifications are now maintained and developed in the open, independently of any particular
implementation, and contributions are welcome. Found something unclear, incomplete or inconsistent?
Open a [GitHub issue](https://github.com/scverse/spatialdata-spec/issues) or submit a pull request.
Substantial changes and new features can be proposed through an {doc}`RFC <rfcs>`; see
{doc}`contributing` for details.

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
