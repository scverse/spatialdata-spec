# SpatialData specification

[SpatialData](https://github.com/scverse/spatialdata) is an open and interoperable data framework for spatial omics data. It unifies vendor-specific data in a common, future-proof format designed for efficient on-disk storage and access.

The SpatialData on-disk format builds on the [NGFF specification](https://github.com/ome/ngff-spec) and its implementation in [OME-Zarr](https://www.openmicroscopy.org/ome-zarr/). It reuses NGFF conventions wherever possible, extends them where spatial omics requirements are not yet covered, and aims to contribute broadly useful extensions and discussions upstream to help evolve NGFF.

Currently, this format is defined primarily by the SpatialData [design document](https://github.com/scverse/spatialdata/blob/main/docs/design_doc.md), the [format and version definitions](https://github.com/scverse/spatialdata/blob/main/src/spatialdata/_io/format.py), and the [on-disk readers and writers](https://github.com/scverse/spatialdata/tree/main/src/spatialdata/_io). As alternative implementations emerge—most notably [spatialdataR](https://github.com/HelenaLC/spatialdataR)—a clear, implementation-independent specification will help adoption and interoperability across languages and ecosystems.

This repository initially aims to capture the current on-disk format, as implemented today, in a plain-English specification. It will later provide a dedicated specification website and serve as a public forum for discussing the format's evolution, initially through GitHub issues.

Its scope may later expand to include the in-memory data model, minimal interoperability APIs, and machine-readable specifications for automated conformance testing.

> [!IMPORTANT]
> This project is a work in progress. Contributions and feedback are welcome!
