# Contributing (repository tooling)

This page covers the repository tooling: building the website, checks and continuous integration.
For the specification text itself, see {doc}`contributing_to_the_spec`.

## Setting up

The website is built with [Sphinx][] from Markdown ([MyST][]). The repository is set up for the
project manager [hatch][], which creates the documentation environment on first use; [uv][] works
as well.

The specification pages are built from the top-level `spec/` directory through the `docs/spec`
symlink. On Windows this requires `git config core.symlinks true` before checkout, otherwise the
build fails.

(docs-building)=

## Building the site locally

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
uv run --group doc sphinx-build -M html docs docs/_build -W
```

Then open `docs/_build/html/index.html`.

::::
:::::

The build treats warnings as errors, as CI does. After changing `docs/conf.py`, delete
`docs/_build` first: Sphinx does not rebuild pages for changes to the setup code.

## Checks

Formatting and linting run as [pre-commit][]-style hooks, best with [prek][]:

```bash
uvx prek install  # once, in the root of the repository
```

Pull requests run two CI jobs (`.github/workflows/test.yaml`): the checks, and the documentation
build with warnings as errors.

## Hosting

The site is built on [Read the Docs](https://readthedocs.org) (`.readthedocs.yaml`), with a preview
for each pull request; until the repository is public, CI uploads the built site as the `site-html`
artifact.

## Site scripts

The specification page relies on a few scripts in `docs/_static/js/` (styles in
`docs/_static/css/custom.css`). Each one only enhances the page; without JavaScript, the tabs and
footnotes are shown as built.

- `view-switch.js`: the views in the navigation (abstract data model, storage format versions,
  in-memory formats), the page heading per view, and the fallback of the 0.3 draft to 0.2;
- `tab-permalinks.js`: tab selection in the URL, "¶" links for rubrics inside tabs, and opening the
  tab that holds a linked anchor;
- `footnote-popups.js`: footnotes as popups; `docs/conf.py` moves the footnotes into the page's
  *Notes* section at build time.

[Sphinx]: https://www.sphinx-doc.org/
[MyST]: https://myst-parser.readthedocs.io/
[hatch]: https://hatch.pypa.io/latest/
[uv]: https://docs.astral.sh/uv/
[pre-commit]: https://pre-commit.com/
[prek]: https://prek.j178.dev/
