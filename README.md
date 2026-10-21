# SpatialData specifications

[SpatialData](https://github.com/scverse/spatialdata) is an open and interoperable data framework for spatial omics data. This repository specifies it in plain English, independently of any implementation. The abstract data model is in [`data-model.md`](data-model.md); the storage format, in [`storage-format.md`](storage-format.md), repeats each part of the data model and follows it with its storage:

| Part | What it specifies | Status |
| --- | --- | --- |
| Abstract data model | What a SpatialData dataset is: elements, coordinate systems, instances, annotation tables; plain language | first draft |
| Storage format | How a dataset is stored (Zarr, Parquet, built on OME-NGFF); language agnostic, normative | first draft, storage format versions 0.1 to 0.5 |
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
describes both; the RFCs so far are listed in [`rfcs.md`](rfcs.md).

## Roadmap

See the [planning notes](planning) for open questions and next steps.

- [x] **Website**: the abstract data model and the storage format on two pages; the storage format
      includes each data model section, so the data model text exists once.
- [x] **Abstract data model** (first draft).
- [x] **Storage format** (first draft): container formats 0.1 and 0.2, as written by `spatialdata`
      up to 0.8; a draft of 0.3 for accepted changes.
- [ ] **In-memory formats**: Python first, then R and JavaScript.
- [ ] **Machine-readable spec**: JSON Schemas, examples, and conformance tests
      (planned under `schemas/`, `examples/`, `conformance/`).
- [x] **RFCs**: process and list; RFC 1 (coordinate systems and transformations) is planned.
- [ ] **Issue templates** for format changes and RFCs.

## Branches

| Branch | Holds |
| --- | --- |
| `history-draft` (this one) | all versions of the storage format side by side (version tabs where versions differ), as Markdown and images, and `tools/write_history.py`. Temporary: it exists to write the history of `main` once |
| `main` | one version of the specification per commit, tagged `storage-format-<version>`; after the history is written, the source of truth to work with |
| `site` | the website: it builds the tags of `main` into one site with a version switcher |

Run locally, once, to write the history of `main` (one commit and tag per storage format
version, oldest first, on top of `origin/main`; nothing is pushed):

```bash
python tools/write_history.py              # commit and tag on the local branch main
python tools/write_history.py --out _main  # only write the files of each version, to _main/<version>/
```

To preview this branch or a generated version as a website, check out the `site` branch next to
this repository and build with [uv](https://docs.astral.sh/uv/):

```bash
git worktree add ../spatialdata-spec-site site
cd ../spatialdata-spec-site
uv run build.py --source ../spatialdata-spec          # this branch, as a preview
uv run build.py --source ../spatialdata-spec/_main/0.5
python -m http.server -d _site                        # then open http://localhost:8000/preview/
```

## License

This repository is dual-licensed:

- The specification text (the Markdown files and images) is licensed under
  [CC-BY-4.0](LICENSE.md).
- `tools/` and any future JSON Schemas, examples, and conformance code are licensed under
  [BSD-3-Clause](LICENSE).

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
