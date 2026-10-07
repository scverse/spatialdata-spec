# SpatialData specification

[SpatialData](https://github.com/scverse/spatialdata) is an open and interoperable data framework for spatial omics data. This repository specifies it in plain English, independently of any implementation, in three layers:

| Layer | What it specifies | Purpose | Where |
| --- | --- | --- | --- |
| 1. On-disk format | How a SpatialData dataset is stored on-disk (Zarr, Parquet); language agnostic | Any implementation can read and write the same files | [`spec/on-disk/`](https://github.com/scverse/spatialdata-spec/tree/main/spec/on-disk) |
| 2. In-memory model | The in-memory object for each language (Python, R, JavaScript) | Tools within a language can share and operate on the same object | [`spec/in-memory/`](https://github.com/scverse/spatialdata-spec/tree/main/spec/in-memory) |
| 3. Semantic layer (⚠️ **experimental**) | How biological concepts map onto elements | Consistent meaning across datasets and tools | [`spec/semantic/`](https://github.com/scverse/spatialdata-spec/tree/main/spec/semantic) |

The on-disk format builds on the [NGFF specification](https://github.com/ome/ngff-spec) and [OME-Zarr](https://www.openmicroscopy.org/ome-zarr/), reusing their conventions wherever possible and contributing broadly useful extensions upstream.

Before this repository, the format was defined by the SpatialData [design document](https://github.com/scverse/spatialdata/blob/main/docs/design_doc.md), the [format and version definitions](https://github.com/scverse/spatialdata/blob/main/src/spatialdata/_io/format.py), and the [on-disk readers and writers](https://github.com/scverse/spatialdata/tree/main/src/spatialdata/_io). With alternative implementations emerging, most notably [spatialdataR](https://github.com/HelenaLC/spatialdataR), an implementation-independent specification helps interoperability across languages.

This repository documents the format as implemented today and is the public forum, through GitHub issues, for discussing its evolution. Its scope includes minimal interoperability APIs and machine-readable specifications for automated conformance testing.

> [!IMPORTANT]
> This project is a work in progress. Contributions and feedback are warmly welcome!

## Proposing changes

Start with a [GitHub issue](https://github.com/scverse/spatialdata-spec/issues), especially for
smaller changes. Larger changes to the specification, such as new features or breaking changes, are
worked out through RFCs (requests for comments): a written proposal that is discussed and refined
by the community before it is adopted into the specification.

## Roadmap

See the [planning notes](https://github.com/scverse/spatialdata-spec/tree/main/planning) for open questions and next steps.

- [x] **Website** — one section per layer, with status labels.
- [x] **On-disk format** (first draft) — the format written by `spatialdata` 0.6.
- [x] **In-memory model** — Python first draft; R and JavaScript placeholders.
- [x] **Semantic layer** — ⚠️ **EXPERIMENTAL**: options for community review, nothing normative yet.
- [ ] **Machine-readable spec** — JSON Schemas, examples, and conformance tests
      (planned under `schemas/`, `examples/`, `conformance/`).
- [ ] **RFC page** — how RFCs are proposed and reviewed, gathering the two initial RFCs currently
      hosted elsewhere: [spatial tiling of vector data](https://github.com/scverse/spatialdata/discussions/1251)
      and [instance-level linking](https://github.com/LucaMarconato/spatialdata/blob/2619c4ff31a5e6e0a98047be17025d96210c15d0/rfcs/links.md).
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
in `docs/`.

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

### Citing and attributing

When you reuse or adapt specification text, CC-BY-4.0 requires attribution; for example, we suggest:

> (Adapted from the) [SpatialData specification](https://github.com/scverse/spatialdata-spec) by
> scverse, licensed under [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/).

When you refer to SpatialData in a publication, please cite the specification (with the version or
commit you used) together with the SpatialData paper, for example:

> scverse. SpatialData specification, commit `117feca`.
> <https://github.com/scverse/spatialdata-spec/tree/117feca>

> Marconato, L., Palla, G., Yamauchi, K.A. et al. SpatialData: an open and universal data framework
> for spatial omics. *Nat Methods* **22**, 58–62 (2025). <https://doi.org/10.1038/s41592-024-02212-x>
