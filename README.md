# SpatialData specification

[SpatialData](https://github.com/scverse/spatialdata) is an open and interoperable data framework for spatial omics data. It unifies vendor-specific data in a common, future-proof format designed for efficient on-disk storage and access.

The SpatialData on-disk format builds on the [NGFF specification](https://github.com/ome/ngff-spec) and its implementation in [OME-Zarr](https://www.openmicroscopy.org/ome-zarr/). It reuses NGFF conventions wherever possible, extends them where spatial omics requirements are not yet covered, and aims to contribute broadly useful extensions and discussions upstream to help evolve NGFF.

Currently, this format is defined primarily by the SpatialData [design document](https://github.com/scverse/spatialdata/blob/main/docs/design_doc.md), the [format and version definitions](https://github.com/scverse/spatialdata/blob/main/src/spatialdata/_io/format.py), and the [on-disk readers and writers](https://github.com/scverse/spatialdata/tree/main/src/spatialdata/_io). As alternative implementations emerge—most notably [spatialdataR](https://github.com/HelenaLC/spatialdataR)—a clear, implementation-independent specification will help adoption and interoperability across languages and ecosystems.

This repository initially aims to capture the current on-disk format, as implemented today, in a plain-English specification. It will later provide a dedicated specification website and serve as a public forum for discussing the format's evolution, initially through GitHub issues.

Its scope may later expand to include the in-memory data model, minimal interoperability APIs, and machine-readable specifications for automated conformance testing.

> [!IMPORTANT]
> This project is a work in progress. Contributions and feedback are welcome!

## Roadmap

The specification website is being drafted; see the
[planning notes](https://github.com/scverse/spatialdata-spec/tree/main/planning) for open questions
and next steps.

- [x] **Website scaffolding** — `pydata-sphinx-theme`, one section per specification layer, layer
      and status labels on every section, placeholders for upcoming versions and implementations.
- [x] **On-disk format** (first draft) — [`spec/on-disk/`](https://github.com/scverse/spatialdata-spec/tree/main/spec/on-disk):
      container, coordinate systems, images, labels, shapes, points, tables, NGFF compatibility,
      version history. Describes the format written by `spatialdata` 0.6.
- [x] **In-memory formats** — [`spec/in-memory/`](https://github.com/scverse/spatialdata-spec/tree/main/spec/in-memory):
      general page (what every implementation documents), Python first draft (`spatialdata` data
      model plus a non-normative implementation guide), R and JavaScript placeholders.
      Implementation-specific discussions happen in the implementation repositories.
- [x] **Semantic conventions** (options for review) — [`spec/semantic/`](https://github.com/scverse/spatialdata-spec/tree/main/spec/semantic):
      how biology maps onto elements; nothing normative yet.
- [x] **Consistency check** with `spatialdata/_io/format.py`, the source of truth for on-disk
      versions: `tools/check_format_versions.py`.
- [x] **Drift detection** — `conformance/` fingerprints what `spatialdata` writes and exposes and
      diffs it against the version the spec describes; `.github/workflows/spec-drift.yml` runs it
      weekly and on demand, with an optional agent-drafted pull request (see `conformance/README.md`).
- [ ] **Maintainer review** of the drafted facts (see `planning/NEXT_STEPS.md`).
- [ ] **Machine-readable spec** — JSON Schemas, examples, and conformance tests
      (planned under `schemas/`, `examples/`, `conformance/`).
- [ ] **Spec contribution workflow** and issue templates.
- [ ] **Other in-memory implementations** (R, JavaScript).

## Building the website locally

The site is built with Sphinx through [hatch](https://hatch.pypa.io/) (install it once with
`uv tool install hatch` or `pipx install hatch`). Hatch creates the environment on first use.

```bash
hatch run docs:build   # build to docs/_build/html; warnings are errors, as in CI
hatch run docs:open    # open the built site in a browser
hatch run docs:clean   # remove build artefacts
```

Specification text lives in `spec/` (symlinked into `docs/spec/`); everything else about the site is
in `docs/`. To check the specification against the installed `spatialdata` release (version tables
and a fingerprint of what it writes), run `hatch run drift:check`; see `conformance/README.md`.

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
