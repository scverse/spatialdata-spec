# SpatialData specifications

[SpatialData](https://github.com/scverse/spatialdata) is an open and interoperable data framework for spatial omics data. This repository specifies it in plain English, independently of any implementation. All of it is on one page, [`spec/specification.md`](spec/specification.md), where every part of the data model is followed by its implementations:

| Part | What it specifies | Status |
| --- | --- | --- |
| Abstract data model | What a SpatialData dataset is: elements, coordinate systems, instances, annotation tables; plain language | first draft |
| Storage format | How a dataset is stored (Zarr, Parquet, built on OME-NGFF); language agnostic, normative | first draft, container formats 0.1 and 0.2; 0.3 draft |
| In-memory formats | How each implementation (Python, R, JavaScript) represents the data model | not yet documented |

The storage format builds on the [NGFF specification](https://github.com/ome/ngff-spec) and [OME-Zarr](https://www.openmicroscopy.org/ome-zarr/), reusing their conventions wherever possible and contributing broadly useful extensions upstream.

Before this repository, the format was defined by the SpatialData [design document](https://github.com/scverse/spatialdata/blob/main/docs/design_doc.md), the [format and version definitions](https://github.com/scverse/spatialdata/blob/main/src/spatialdata/_io/format.py), and the [readers and writers](https://github.com/scverse/spatialdata/tree/main/src/spatialdata/_io). With alternative implementations emerging, most notably [spatialdataR](https://github.com/HelenaLC/spatialdataR), an implementation-independent specification helps interoperability across languages.

This repository describes the format as written by `spatialdata` 0.6 to 0.8, with explicit versions, and is where new versions are proposed and decided. Its scope includes minimal interoperability APIs and machine-readable specifications for automated conformance testing.

> [!IMPORTANT]
> This project is a work in progress. Contributions and feedback are warmly welcome!

## Proposing changes

Start with a [GitHub issue](https://github.com/scverse/spatialdata-spec/issues), especially for
smaller changes. Larger changes to the specification, such as new features or breaking changes, are
worked out through RFCs (requests for comments): a written proposal that is discussed and refined
by the community before it is adopted into the specification. The contributing guide on the website
describes both; the RFCs so far are listed in [`docs/rfcs.md`](docs/rfcs.md).

## Roadmap

See the [planning notes](planning) for open questions and next steps.

- [x] **Website**: one specification page with switchable views (abstract data model, storage
      format versions, in-memory formats).
- [x] **Abstract data model** (first draft).
- [x] **Storage format** (first draft): container formats 0.1 and 0.2, as written by `spatialdata`
      up to 0.8; a draft of 0.3 for accepted changes.
- [ ] **In-memory formats**: Python first, then R and JavaScript.
- [ ] **Machine-readable spec**: JSON Schemas, examples, and conformance tests
      (planned under `schemas/`, `examples/`, `conformance/`).
- [x] **RFCs**: process and list; RFC 1 (coordinate systems and transformations) is planned.
- [ ] **Issue templates** for format changes and RFCs.

## Building the website locally

The website code is on the `site` branch, which builds every published version of the
specification into one site; every branch and tag here holds one version. To build your working
copy, check out the `site` branch next to this repository once and build with
[hatch](https://hatch.pypa.io/):

```bash
git worktree add ../spatialdata-spec-site site
hatch run docs:build   # build to _site/preview; warnings are errors, as in CI
hatch run docs:open    # open the built site in a browser
hatch run docs:clean   # remove build artefacts
```

Specification text lives in `spec/` (symlinked into `docs/spec/`); the other pages of the site are
in `docs/`. See the contributing guide on the website for details.

## License

This repository is dual-licensed:

- The specification prose under [`spec/`](spec)
  is licensed under [CC-BY-4.0](spec/LICENSE).
- Everything else — repository tooling, the documentation build, and any future
  JSON Schemas, examples, and conformance code — is licensed under
  [BSD-3-Clause](LICENSE).

The `spec/` directory is intentionally limited to prose. Code, schemas, and example
files must not be placed there or otherwise licensed under CC-BY-4.0, so that
downstream implementations can reuse them without attribution overhead.

### Citing and attributing

When you reuse or adapt specification text, CC-BY-4.0 requires attribution; for example, we suggest:

> (Adapted from the) [SpatialData specifications](https://github.com/scverse/spatialdata-spec) by
> scverse, licensed under [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/).

When you refer to SpatialData in a publication, please cite the specification (with the version or
commit you used) together with the SpatialData paper, for example:

> scverse. SpatialData specifications, commit `117feca`.
> <https://github.com/scverse/spatialdata-spec/tree/117feca>

> Marconato, L., Palla, G., Yamauchi, K.A. et al. SpatialData: an open and universal data framework
> for spatial omics. *Nat Methods* **22**, 58–62 (2025). <https://doi.org/10.1038/s41592-024-02212-x>
