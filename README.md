# SpatialData specifications: website

This branch (`site`) holds the website of the
[SpatialData specifications](https://github.com/scverse/spatialdata-spec) and the pages of the
project itself: the landing page, the contributing guide and the RFCs. The specification is on
`main`, one version per commit, tagged `storage-format-<version>`. This branch builds the tags
listed in `versions.toml` into one site, each under its own directory,
`data-model/<version>/storage-format/<version>/`; the navigation of every page lists all versions.

| Path | Purpose |
| --- | --- |
| `versions.toml` | the published versions: tag, data model and storage format version |
| `build.py` | builds each version from its tag, the data model builds and the root; then shares the assets of the root with all builds and writes `sitemap.xml`, `robots.txt` and `versions.json` |
| `site/` | Sphinx configuration, CSS, templates and the pages present in every build: `index.md`, `contributing.md`, `rfcs.md` |
| `site/_ext/static_nav.py` | the version navigation, written into every page when it is built: the site works without JavaScript (one script adds tab permalinks) |
| `site/_ext/footnote_previews.py` | each footnote shown at its reference on hover or focus (CSS only); printing shows the list of footnotes |
| `site/rfcs/` | the RFCs, one file each; `build.py` writes the table on `rfcs.md` from their headers |
| `pages/` | pages only at the root, showing the latest state for every version (implementations) |
| `.github/workflows/site.yaml` | checks, builds and, on a push to this branch, deploys the site to GitHub Pages |

## Building locally

Needs [uv](https://docs.astral.sh/uv/) and a full clone (all branches and tags):

```bash
uv run build.py --site-url http://localhost:8000/   # every version in versions.toml
uv run build.py --ref some-branch                   # one branch or tag, as a preview
uv run build.py --source ../spatialdata-spec        # a working copy, as a preview
python -m http.server -d _site                      # then open http://localhost:8000/
```

An entry of `versions.toml` may also give `source = "<directory>"`, to build it from a directory
instead of its tag (for example the output of `tools/write_history.py --out` on `history-draft`).

## Releasing a version

1. Tag the release commit of `main` as `storage-format-<version>`.
2. Add the tag to `versions.toml` on this branch, above the previous release, and move `preferred`
   to it. Never change the directory of a published version: it is part of every permalink.

## License

The website code is BSD-3-Clause ([LICENSE](LICENSE)). The text of the pages in `site/` and
`pages/` (the landing page, the contributing guide, the RFCs and the implementations) is
CC-BY-4.0 ([LICENSE.md](LICENSE.md)).
