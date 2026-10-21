"""Build the website: every version in versions.toml, each from its own branch or tag.

Each storage format version is checked out into a temporary git worktree, the website code in
site/ is copied over its pages, and Sphinx builds it into
_site/data-model/<data model>/storage-format/<storage format>/. Each data model version is also
built on its own, from the newest storage format that encodes it, into
_site/data-model/<data model>/, where no storage format is selected. The site root leads to the
preferred version. versions.json at the root lists all versions; the navigation of
every page reads it, so that pages built earlier also list versions released later.

    uv run build.py                                  # all versions, as published
    uv run build.py --ref my-branch                  # one branch or tag, as a preview
    uv run build.py --source ../spatialdata-spec     # a working copy of the content, as a preview
    uv run build.py --site-url http://localhost:8000/ && python -m http.server -d _site
"""

import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
import tomllib
from pathlib import Path

HERE = Path(__file__).resolve().parent
WEB = HERE / "site"
DEFAULT_SITE_URL = "https://scverse.github.io/spatialdata-spec/"


def git(*args, check=True):
    return subprocess.run(["git", *args], cwd=HERE, check=check, capture_output=True, text=True)


def resolve(ref):
    """The commit-ish for a branch or tag; in CI, branches may exist only as origin/<branch>."""
    for candidate in (ref, f"origin/{ref}"):
        if git("rev-parse", "--verify", "--quiet", f"{candidate}^{{commit}}", check=False).returncode == 0:
            return candidate
    sys.exit(f"build.py: no branch or tag named {ref!r}")


def path_of(version):
    if version.get("path"):
        return version["path"]
    if not version.get("storage_format"):  # a data model version on its own
        return f"data-model/{version['data_model']}"
    return f"data-model/{version['data_model']}/storage-format/{version['storage_format']}"


def data_models(versions):
    """One build per data model version, from the newest released storage format that encodes it."""
    builds = {}
    for v in versions:
        if not v.get("draft"):
            builds.setdefault(v["data_model"], {"ref": v["ref"], "data_model": v["data_model"]})
    return list(builds.values())


def tree(versions, site_url):
    """The versions as listed in versions.json: data model versions, each with its storage formats."""
    models = {}
    for v in versions:
        if v.get("path"):  # previews are not listed
            continue
        model = models.setdefault(
            v["data_model"],
            {"version": v["data_model"], "url": f"{site_url}data-model/{v['data_model']}/", "storage_formats": []},
        )
        model["storage_formats"].append(
            {
                "version": v["storage_format"],
                "url": f"{site_url}{path_of(v)}/",
                **({"preferred": True} if v.get("preferred") else {}),
                **({"draft": True} if v.get("draft") else {}),
            }
        )
    return {"data_models": list(models.values())}


def build(version, listed, out, tmp, site_url, strict, preview_pr):
    path = path_of(version)
    src = tmp / path.replace("/", "-")
    if version.get("source"):  # a checkout on disk, e.g. a pull request or a working copy
        shutil.copytree(
            version["source"], src, ignore=shutil.ignore_patterns(".git", ".site", ".venv", "_build", "_site")
        )
    else:
        git("worktree", "add", "--detach", "--quiet", str(src), resolve(version["ref"]))
    try:
        # main and its tags hold the pages at the top level; older branches in docs/
        docs = src / "docs" if (src / "docs" / "index.md").exists() else src
        shutil.copytree(WEB, docs, dirs_exist_ok=True)  # website code wins over anything in the content
        env = {
            **os.environ,
            "SPEC_REF": version["ref"],
            "SPEC_DOC_PATH": docs.relative_to(src).as_posix().strip("."),
            "SPEC_PATH": path,
            "SPEC_DATA_MODEL": version.get("data_model", ""),
            "SPEC_STORAGE_FORMAT": version.get("storage_format", ""),
            "SPEC_VERSIONS": json.dumps(listed),
            "SPEC_DRAFT": "1" if version.get("draft") else "0",
            "SPEC_PREVIEW_PR": preview_pr,
            "SITE_URL": site_url,
        }
        cmd = [sys.executable, "-m", "sphinx", "-b", "html", "-d", str(src / "_doctrees"), str(docs), str(out / path)]
        if strict:
            cmd += ["-W", "--keep-going"]
        print(f"--- {version['ref']} -> {path}/", flush=True)
        subprocess.run(cmd, env=env, check=True)
    finally:
        if not version.get("source"):
            git("worktree", "remove", "--force", str(src))


def redirect(page, url, text):
    page.parent.mkdir(parents=True, exist_ok=True)
    page.write_text(
        f'<!doctype html><meta charset="utf-8"><title>SpatialData specifications</title>'
        f'<meta http-equiv="refresh" content="0; url={url}"><link rel="canonical" href="{url}">'
        f'<a href="{url}">{text}</a>\n'
    )


def write_root(listed, out, site_url):
    (out / "versions.json").write_text(json.dumps(listed, indent=2) + "\n")
    preferred = next(f for m in listed["data_models"] for f in m["storage_formats"] if f.get("preferred"))
    redirect(out / "index.html", preferred["url"], "SpatialData specifications")
    (out / ".nojekyll").touch()  # serve _static/ as is on GitHub Pages


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--versions", type=Path, default=HERE / "versions.toml", help="list of versions to build")
    parser.add_argument("--ref", help="build only this branch or tag, as a preview")
    parser.add_argument("--source", type=Path, help="build only this checkout of the content, as a preview")
    parser.add_argument("--pr", default="", help="pull request number, for the preview banner")
    parser.add_argument("--site-url", default=os.environ.get("SITE_URL", DEFAULT_SITE_URL))
    parser.add_argument("--out", type=Path, default=HERE / "_site")
    parser.add_argument("--no-strict", dest="strict", action="store_false", help="do not fail on Sphinx warnings")
    args = parser.parse_args()
    site_url = args.site_url.rstrip("/") + "/"

    versions = tomllib.loads(args.versions.read_text())["version"]
    if sum(bool(v.get("preferred")) for v in versions) != 1:
        sys.exit("build.py: exactly one version in versions.toml must be preferred")
    listed = tree(versions, site_url)
    preview = args.ref or args.source
    if preview:  # one version, listed next to the published ones
        versions = [{"ref": args.ref or "main", "source": args.source, "path": "preview", "draft": True}]
    else:
        versions = data_models(versions) + versions

    shutil.rmtree(args.out, ignore_errors=True)
    args.out.mkdir(parents=True)
    with tempfile.TemporaryDirectory(prefix="spec-site-") as tmp:
        for version in versions:
            build(version, listed, args.out, Path(tmp), site_url, args.strict, args.pr)
    git("worktree", "prune")
    if not preview:
        write_root(listed, args.out, site_url)


if __name__ == "__main__":
    main()
