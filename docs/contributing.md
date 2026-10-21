# Contributing (repository tooling)

This page covers the repository tooling: building the website, checks and continuous integration.
For the specification text itself, see {doc}`contributing_to_the_spec`.

## Branches

The repository has three branches, each with one job:

| Branch | Holds | Edited |
| --- | --- | --- |
| `history-draft` | all versions of the specification side by side (version tabs where versions differ), the contributing guides, and `tools/write_history.py` | by pull requests; the default branch |
| `main` | one version of the specification: Markdown and images only, tagged `storage-format-<version>` per version | only by `tools/write_history.py` |
| `site` | the website code (Sphinx configuration, CSS, JavaScript) and the build of all published versions | by pull requests |

`tools/history.toml` lists the storage format versions, one per row of the
{ref}`compatibility matrix <compatibility-matrix>`. On every push to `history-draft`,
`.github/workflows/publish.yaml` runs `tools/write_history.py`, which writes the text of each new
version to `main` as one commit and tags it, and then publishes the website. Released versions are
never rewritten, and `main` only moves forward. To see what would be written, without touching
git:

```bash
python tools/write_history.py --out _main  # the files of each version, in _main/<version>/
```

## Setting up

The website is built with [Sphinx][] from Markdown ([MyST][]). Its code is on the `site` branch.
Check out the `site` branch once, next to this repository, with a git worktree:

```bash
git worktree add ../spatialdata-spec-site site
```

The specification pages are built from the top-level `spec/` directory through the `docs/spec`
symlink. On Windows this requires `git config core.symlinks true` before checkout, otherwise the
build fails.

(docs-building)=

## Building the site locally

This builds your working copy with the website code of the `site` branch, through [hatch][] or
[uv][]:

:::::{tab-set}
::::{tab-item} Hatch
:sync: hatch

```bash
hatch run docs:build
hatch run docs:open
```

::::

::::{tab-item} uv
:sync: uv

```bash
uv run --project ../spatialdata-spec-site ../spatialdata-spec-site/build.py --source . --out _site
```

Then open `_site/preview/index.html`.

::::
:::::

The build treats warnings as errors, as CI does. Set `SITE_DIR` if the `site` branch is checked
out elsewhere. Changes to the website itself go to the `site` branch, which describes its build in
its README.

## Checks

Formatting and linting run as [pre-commit][]-style hooks, best with [prek][]:

```bash
uvx prek install  # once, in the root of the repository
```

Pull requests run two CI jobs (`.github/workflows/test.yaml`): the checks, and the documentation
build with warnings as errors.

## Hosting and previews

The site is published on GitHub Pages by `.github/workflows/publish.yaml`, on every push to
`history-draft` and every change to the `site` branch. Each version listed in `versions.toml` on the
`site` branch (the tags of `main`) has its own directory, which is part of every permalink; a
version switcher links them.

Each pull request builds a preview: CI uploads it as the `site-html` artifact and links it in a
comment on the pull request; download it, unzip it and open `index.html`.

## Site scripts

The specification page relies on a few scripts in `site/_static/js/` on the `site` branch (styles
in `site/_static/css/custom.css`). Each one only enhances the page; without JavaScript, the tabs
and footnotes are shown as built.

- `view-switch.js`: the views in the navigation (abstract data model, storage format versions,
  in-memory formats), the page heading per view, and the fallback of the 0.3 draft to 0.2;
- `tab-permalinks.js`: tab selection in the URL, "¶" links for rubrics inside tabs, and opening the
  tab that holds a linked anchor;
- `footnote-popups.js`: footnotes as popups; `site/conf.py` moves the footnotes into the page's
  *Notes* section at build time.

[Sphinx]: https://www.sphinx-doc.org/
[MyST]: https://myst-parser.readthedocs.io/
[hatch]: https://hatch.pypa.io/latest/
[uv]: https://docs.astral.sh/uv/
[pre-commit]: https://pre-commit.com/
[prek]: https://prek.j178.dev/
