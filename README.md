# SpatialData specifications: website

This branch (`site`) holds only the website of the
[SpatialData specifications](https://github.com/scverse/spatialdata-spec). The specification
itself is edited on `history-draft`, with all versions side by side; its `tools/write_history.py`
writes each version to `main` as one commit, tagged `storage-format-<version>`, with Markdown and
images only. This branch builds the tags listed in `versions.toml` into one site, each under its
own directory, `data-model/<version>/storage-format/<version>/`; the navigation of every page
lists all versions.

| File | Purpose |
| --- | --- |
| `versions.toml` | the published versions: branch or tag, directory, label |
| `build.py` | builds each version from its branch or tag into `_site/data-model/<version>/storage-format/<version>/`, plus `versions.json` and redirects |
| `site/` | Sphinx configuration, CSS, JavaScript, templates and the logo, copied over each version's pages before it is built (the top level on `main`, `docs/` on older branches) |
| `.github/workflows/site.yaml` | checks changes to this branch and asks the default branch to republish the site |

Publishing runs from `publish.yaml` on `history-draft`, the default branch (on every push to it and
every push to this branch): it writes new versions to `main`, checks out this branch, runs
`build.py` and deploys `_site/` to GitHub Pages.

## Building locally

Needs [uv](https://docs.astral.sh/uv/) and a full clone (all branches and tags):

```bash
uv run build.py                                   # every version in versions.toml
uv run build.py --source ../spatialdata-spec      # a working copy of history-draft, as a preview
uv run build.py --ref some-branch                 # one branch or tag, as a preview
python -m http.server -d _site                    # then open http://localhost:8000/
```

Pass `--site-url http://localhost:8000/` for version links that work locally.

## Releasing a version

1. Add the version to `tools/history.toml` on `history-draft`; on merge, `publish.yaml` writes
   and tags it on `main`.
2. Add the tag to `versions.toml` on this branch, above the previous release, and move `preferred`
   to it. Never change the `path` of a published version: it is part of every permalink.

## License

The website code is BSD-3-Clause; see [LICENSE](LICENSE).
