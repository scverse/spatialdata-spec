# Contributing to the specification

Contributions are welcome as GitHub issues and pull requests on
[scverse/spatialdata-spec](https://github.com/scverse/spatialdata-spec) until a formal process is
established. Contributions to the repository tooling follow {doc}`contributing`.

## Process

The specification first records the **status quo**, then evolves through proposals. Pages labelled
{bdg-dark-line}`status quo` describe what `spatialdata` implements; they are corrected when wrong
but not changed by opinion. Changes to what is *specified* go through an issue, a decision, and a
new numbered version of the affected document. The trigger and the steps for a new on-disk version
are on {doc}`spec/on-disk/next`.

## What goes where

| You want to | Do this |
|-------------|---------|
| Report an inconsistency between the text and what `spatialdata` writes | Open an issue here with a minimal store or code snippet |
| Propose a change to the on-disk format | Open an issue here labelled `format-change`: motivation, the bytes that change, the migration path. Changes land together with the `spatialdata` implementation |
| Discuss something that concerns every in-memory implementation | Open an issue here labelled `in-memory-general` |
| Propose a change to the **Python** in-memory model | Go to [scverse/spatialdata](https://github.com/scverse/spatialdata/issues); the page here is updated after release |
| Propose a change to the **R** or **JavaScript** in-memory model | Go to [HelenaLC/spatialdataR](https://github.com/HelenaLC/spatialdataR/issues) or [Taylor-CCB-Group/SpatialData.js](https://github.com/Taylor-CCB-Group/SpatialData.js/issues) |
| Propose or comment on a semantic convention | Open an issue here labelled `semantic-conventions`, naming the question from {doc}`spec/semantic/options` |
| Document another in-memory implementation | Open a pull request adding `spec/in-memory/<language>/` following {doc}`spec/in-memory/index` |
| Fix wording, add an example, add a figure | Open a pull request |

Issue labels used here: `format-change`, `in-memory-general`, `semantic-conventions`, `docs`.

## Labels on pages

Every section index carries two kinds of badges: the **layer** ({bdg-primary}`on-disk`,
{bdg-success}`in-memory · Python`, {bdg-info}`in-memory · R`, {bdg-warning}`semantic`) and the
**status** ({bdg-dark-line}`status quo`, {bdg-secondary-line}`legacy`, {bdg-warning-line}`draft`,
{bdg-warning-line}`under discussion`, {bdg-light}`placeholder`). Chapter pages add the component
version they describe. Keep them accurate when editing.

## Keeping the specification in sync with `spatialdata`

`spatialdata/_io/format.py` is the source of truth for on-disk versions, and the bytes written by
`spatialdata` are the source of truth for the rest. Two checks guard against drift:

- `tools/check_format_versions.py` compares the version tables with `spatialdata._io.format`.
- `conformance/` fingerprints what the installed `spatialdata` writes and exposes (from a fixed
  fixture) and diffs it against `conformance/fingerprints/baseline.json`, the fingerprint of the
  version the spec describes. See `conformance/README.md`.

```bash
hatch run drift:check      # both checks against the spatialdata release installed in the drift env
```

The workflow `.github/workflows/spec-drift.yml` runs the same checks weekly against the latest
PyPI release, or on demand against `main` or any tag (*Actions → Spec drift check → Run workflow*).
On drift it fails, uploads a report, optionally opens an issue, and optionally lets Claude Code
open a draft pull request with proposed edits for human review. After updating the spec for a new
`spatialdata` version, regenerate the baseline with `hatch run drift:baseline` in the same pull
request.

## Writing rules

- Use **MUST**, **SHOULD**, **MAY** per RFC 2119 and mean it.
- Specify only what NGFF, AnnData, Zarr, Parquet or GeoParquet leave open; link to them for the rest.
- When several versions of a component exist, put them in inline tabs (`tab-set`), current version
  first, and use `:sync:` keys so that all tabs on a page switch together.
- Use the custom admonitions: *Implementation note* (`implementation-note`, non-normative),
  *Divergence from NGFF* (`ngff-divergence`), *Open question* (`open-question`).
- JSON examples come from real stores; abbreviate with `...` rather than invent.
- Short sentences, no filler. If a paragraph does not change what an implementer would do, delete
  it.

## Building the site

```bash
hatch run docs:build   # warnings are errors
hatch run docs:open
```

The `spec/` directory is symlinked into `docs/spec/`; edit the files under `spec/`.

## Hosting

The site is built for [Read the Docs](https://readthedocs.org): `.readthedocs.yaml` runs the same
`hatch run docs:build` as CI, and `docs/conf.py` reads the `READTHEDOCS_*` environment variables
to set the canonical URL and to replace the draft banner with a "preview build of pull request #N"
banner on pull request builds. Read the Docs builds only public repositories on its free plan, so
while the repository is private the CI docs job uploads the built site as the `site-html` artifact of
each run (download, unzip, open `index.html`).

Once the repository is public, someone with admin rights on the `scverse` organisation:

1. GitHub → organisation Settings → GitHub Apps → *Read the Docs* → Repository access: add
   `spatialdata-spec` if access is restricted to selected repositories.
2. readthedocs.org → *Add project* → pick `scverse/spatialdata-spec` from the connected
   repositories; default branch `main`; the config file is detected. Note the slug (expected
   `scverse-spatialdata-spec`, matching `scverse-spatialdata`).
3. Project → Settings → enable *Build pull requests for this project*.
4. Push a commit to an open pull request (or close and reopen it): the
   `docs/readthedocs.org:<slug>` check with the preview link appears on the pull request.
5. Update the fallback URL in `docs/conf.py` (`html_baseurl`) and `urls.Documentation` in
   `pyproject.toml` to the real slug, and add the link to the README. A custom domain can be set
   later under Settings → Domains.

## Licensing

The repository is dual-licensed:

- Everything under `spec/` is **prose only** and licensed under **CC-BY-4.0** (`spec/LICENSE`).
- All other content, including tooling, the documentation build, and any future schemas, examples
  and conformance code, is licensed under **BSD-3-Clause** (`LICENSE`).

Do not add code, JSON Schemas or example files under `spec/`. Anything ported from another project
must be licence-compatible and credited in a `README.md` next to it.
