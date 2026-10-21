# SpatialData specifications: website

This branch (`site`) holds only the website of the
[SpatialData specifications](https://github.com/scverse/spatialdata-spec). The specification
itself lives on `main` (the next version, under development) and on one tag per released version.
Every commit there holds exactly one version of the specification; this branch builds all
published versions into one site, each under its own directory, with a version switcher.

| File | Purpose |
| --- | --- |
| `versions.toml` | the published versions: branch or tag, directory, label |
| `build.py` | builds each version from its branch or tag into `_site/<path>/`, plus `versions.json` and a redirect at the root |
| `site/` | Sphinx configuration, CSS, JavaScript and templates, copied over each version's `docs/` before it is built |
| `.github/workflows/site.yaml` | checks changes to this branch and asks `main` to republish the site |

Publishing runs from `publish.yaml` on `main` (on every push to `main`, every tag, and every push
to this branch): it checks out this branch, runs `build.py` and deploys `_site/` to GitHub Pages.

## Building locally

Needs [uv](https://docs.astral.sh/uv/) and a full clone (all branches and tags):

```bash
uv run build.py                                   # every version in versions.toml
uv run build.py --source ../spatialdata-spec      # your working copy of the content, as a preview
uv run build.py --ref some-branch                 # one branch or tag, as a preview
python -m http.server -d _site                    # then open http://localhost:8000/
```

Pass `--site-url http://localhost:8000/` for a version switcher that works locally.

## Releasing a version

1. Tag the commit on `main` (for example `storage-format-0.2`).
2. Add it to `versions.toml` on this branch, above the previous release, and move `preferred`
   to it. Never change the `path` of a published version: it is part of every permalink.

## License

The website code is BSD-3-Clause; see [LICENSE](LICENSE).
