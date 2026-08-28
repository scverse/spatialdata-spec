# SpatialData specification

[SpatialData](https://github.com/scverse/spatialdata) is an open and interoperable data framework for spatial omics data. It unifies vendor-specific data in a common, future-proof format designed for efficient on-disk storage and access.

The SpatialData on-disk format builds on the [NGFF specification](https://github.com/ome/ngff-spec) and its implementation in [OME-Zarr](https://www.openmicroscopy.org/ome-zarr/). It reuses NGFF conventions wherever possible, extends them where spatial omics requirements are not yet covered, and aims to contribute broadly useful extensions and discussions upstream to help evolve NGFF.

Currently, this format is defined primarily by the SpatialData [design document](https://github.com/scverse/spatialdata/blob/main/docs/design_doc.md), the [format and version definitions](https://github.com/scverse/spatialdata/blob/main/src/spatialdata/_io/format.py), and the [on-disk readers and writers](https://github.com/scverse/spatialdata/tree/main/src/spatialdata/_io). As alternative implementations emerge—most notably [spatialdataR](https://github.com/HelenaLC/spatialdataR)—a clear, implementation-independent specification will help adoption and interoperability across languages and ecosystems.

This repository initially aims to capture the current on-disk format, as implemented today, in a plain-English specification. It will later provide a dedicated specification website and serve as a public forum for discussing the format's evolution, initially through GitHub issues.

Its scope may later expand to include the in-memory data model, minimal interoperability APIs, and machine-readable specifications for automated conformance testing.

> [!IMPORTANT]
> This project is a work in progress. Contributions and feedback are welcome!

## Roadmap

This repository is still being bootstrapped. The following pieces are stubbed out and
still need to be written:

- [ ] **Specification text** — the plain-English spec chapters, to live under
      [`spec/`](https://github.com/scverse/spatialdata-spec/tree/main/spec)
      (so far only [`spec/README.md`](https://github.com/scverse/spatialdata-spec/blob/main/spec/README.md)).
- [ ] **Spec contribution workflow** — how to propose and review specification changes:
      [`docs/contributing_to_the_spec.md`](https://github.com/scverse/spatialdata-spec/blob/main/docs/contributing_to_the_spec.md).
- [ ] **Pull request checklist** —
      [`.github/PULL_REQUEST_TEMPLATE.md`](https://github.com/scverse/spatialdata-spec/blob/main/.github/PULL_REQUEST_TEMPLATE.md).
- [ ] **Issue template** — expand
      [`.github/ISSUE_TEMPLATE/bug_report.yml`](https://github.com/scverse/spatialdata-spec/blob/main/.github/ISSUE_TEMPLATE/bug_report.yml)
      once the workflow above is defined.
- [ ] **Machine-readable spec** — JSON Schemas, examples, and conformance tests
      (planned under `schemas/`, `examples/`, `conformance/`; not started).

## License

This repository is dual-licensed:

- The specification prose under [`spec/`](https://github.com/scverse/spatialdata-spec/tree/main/spec)
  is licensed under [CC-BY-4.0](https://github.com/scverse/spatialdata-spec/blob/main/spec/LICENSE).
- Everything else — repository tooling, the documentation build, and any future
  JSON Schemas, examples, and conformance code — is licensed under
  [BSD-3-Clause](https://github.com/scverse/spatialdata-spec/blob/main/LICENSE).

The `spec/` directory is intentionally limited to prose. Code, schemas, and example
files must not be placed there or otherwise licensed under CC-BY-4.0, so that
downstream implementations can reuse them without attribution overhead.
