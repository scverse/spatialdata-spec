# SpatialData specifications

> [!WARNING]
> **This branch changes within days.** It now holds the work of the former branch `history-draft`:
> all storage format versions side by side. Until the switch, pull requests that edit the
> specification go against this branch. Then the specification moves to two branches,
> [`data-model`](https://github.com/scverse/spatialdata-spec/tree/data-model) and
> [`storage-format`](https://github.com/scverse/spatialdata-spec/tree/storage-format), each with its
> own tags, and this branch will only point to them. Until then, both are written from this branch
> by `tools/split_branches.py`: do not edit them directly.

[SpatialData](https://github.com/scverse/spatialdata) is an open and interoperable data framework for spatial omics data. This repository specifies it in plain English, independently of any implementation. The abstract data model is in [`data-model.md`](data-model.md); the storage format, in [`storage-format.md`](storage-format.md), repeats each part of the data model and follows it with its storage:

| Part | What it specifies | Status |
| --- | --- | --- |
| Abstract data model | What a SpatialData dataset is: elements, coordinate systems, instances, annotation tables; plain language | first draft |
| Storage format | How a dataset is stored (Zarr, Parquet, built on OME-NGFF); language agnostic, normative | first draft, storage format versions 0.1 to 0.4 |
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
by the community before it is adopted into the specification. The contributing guide and the RFCs
are on the website (branch `site`).

## Roadmap

See the [planning notes](planning) for open questions and next steps.

- [x] **Website**: the abstract data model and the storage format on two pages; the storage format
      includes each data model section, so the data model text exists once.
- [x] **Abstract data model** (first draft).
- [x] **Storage format** (first draft): storage format versions 0.1 to 0.4, as written by
      `spatialdata` up to 0.8, each published as a version of its own.
- [ ] **In-memory formats**: Python first, then R and JavaScript.
- [ ] **Machine-readable spec**: JSON Schemas, examples, and conformance tests.
- [x] **RFCs**: process and list; RFC 1 (coordinate systems and transformations) is planned.
- [ ] **Issue templates** for format changes and RFCs.

## Branches

| Branch | Holds |
| --- | --- |
| `main` (this one, until the switch) | all versions of the storage format side by side (version tabs where versions differ), as Markdown and images, and the tools that write the branches below |
| `data-model` | the abstract data model, tagged `data-model-<version>`; written from this branch until the switch |
| `storage-format`, `maintenance/storage-format-<version>` | the current and the older storage format versions, tagged `storage-format-<version>`; written from this branch until the switch |
| `site` | the website: it builds the storage format versions, each with its data model, into one site with a version switcher |

After a change here is merged, write the branches again (one new commit on each branch whose
text changed, on top of its history; nothing is pushed), then push them:

```bash
python tools/split_branches.py                    # commit on the local branches
python tools/write_history.py --out _main         # only write the files of each version, to _main/<version>/
```

### Editing this branch

The pages of `main` (see `PAGES` in `tools/write_history.py`) are written from this branch; the
landing page, the contributing guide (which describes editing `main`) and the RFCs are on the
branch `site`. Here, all storage format versions sit side by side:

- Where versions differ, put them in inline tabs (`tab-set`) in the sync group `storage-version`,
  newest first, labelled with the storage format versions they apply to and synced with
  `sf-<first>[-<last>]`; mark the newest version `:selected:`. A version without a tab does not
  have the passage. Tabs may be nested if each level uses fewer colons than the one around it:

  ```text
  ::::{tab-set}
  :sync-group: storage-version
  :::{tab-item} Storage format 0.4
  :sync: sf-0.4
  :selected:

  Content for storage format 0.4.
  :::
  :::{tab-item} Storage format 0.1–0.3
  :sync: sf-0.1-0.3

  Content for storage formats 0.1 to 0.3.
  :::
  ::::
  ```

- Write every tab so that it reads as the specification of that version alone: each version is
  written to `main` with only its own tabs. Footnotes that only other versions use are dropped.
- The element version badges (`{bdg-primary}`raster ...``) are rewritten per version from
  `VERSIONS` in the script.

### Previewing

Check out the `site` branch next to this repository and build with
[uv](https://docs.astral.sh/uv/):

```bash
git worktree add ../spatialdata-spec-site site
cd ../spatialdata-spec-site
uv run build.py --source ../spatialdata-spec          # this branch, with all version tabs
uv run build.py --source ../spatialdata-spec/_main/0.4  # one generated version
python -m http.server -d _site                        # then open http://localhost:8000/preview/
```

For the whole site from the generated versions, give each entry of a copy of `versions.toml` a
`source = "<path>/_main/<version>"` and run `uv run build.py --versions <copy>`.

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
