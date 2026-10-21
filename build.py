"""Build the website: every version in versions.toml, each from its own branch or tag.

Each version is checked out into a temporary git worktree, the website code in site/ is copied
over its docs/ directory, and Sphinx builds it into _site/<path>/. The site root gets
versions.json (read by the version switcher) and an index.html that redirects to the preferred
version.

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


def build(version, out, tmp, site_url, strict, preview_pr):
    src = tmp / version["path"]
    if version.get("source"):  # a checkout on disk, e.g. a pull request or a working copy
        shutil.copytree(version["source"], src, ignore=shutil.ignore_patterns(".git", ".venv", "_build", "_site"))
    else:
        git("worktree", "add", "--detach", "--quiet", str(src), resolve(version["ref"]))
    try:
        docs = src / "docs"
        shutil.copytree(WEB, docs, dirs_exist_ok=True)  # website code wins over anything in the content
        env = {
            **os.environ,
            "SPEC_REF": version["ref"],
            "SPEC_PATH": version["path"],
            "SPEC_LABEL": version["label"],
            "SPEC_DRAFT": "1" if version.get("draft") else "0",
            "SPEC_PREVIEW_PR": preview_pr,
            "SITE_URL": site_url,
        }
        cmd = [
            sys.executable,
            "-m",
            "sphinx",
            "-b",
            "html",
            "-d",
            str(src / "_doctrees"),
            str(docs),
            str(out / version["path"]),
        ]
        if strict:
            cmd += ["-W", "--keep-going"]
        print(f"--- {version['label']} ({version['ref']}) -> {version['path']}/", flush=True)
        subprocess.run(cmd, env=env, check=True)
    finally:
        if not version.get("source"):
            git("worktree", "remove", "--force", str(src))


def write_root(versions, out, site_url):
    switcher = [
        {
            "name": v["label"],
            "version": v["path"],
            "url": f"{site_url}{v['path']}/",
            **({"preferred": True} if v.get("preferred") else {}),
        }
        for v in versions
    ]
    (out / "versions.json").write_text(json.dumps(switcher, indent=2) + "\n")
    preferred = next((v for v in versions if v.get("preferred")), versions[0])
    target = f"{preferred['path']}/"
    (out / "index.html").write_text(
        f'<!doctype html><meta charset="utf-8"><title>SpatialData specifications</title>'
        f'<meta http-equiv="refresh" content="0; url={target}"><link rel="canonical" href="{site_url}{target}">'
        f'<a href="{target}">SpatialData specifications</a>\n'
    )
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

    if args.ref or args.source:
        ref = args.ref or "main"  # for a checkout, the branch its "edit" links point to
        label = f"preview of {args.ref or args.source}"
        versions = [{"ref": ref, "source": args.source, "path": "preview", "label": label, "draft": True}]
    else:
        versions = tomllib.loads(args.versions.read_text())["version"]
        if sum(bool(v.get("preferred")) for v in versions) != 1:
            sys.exit("build.py: exactly one version in versions.toml must be preferred")

    shutil.rmtree(args.out, ignore_errors=True)
    args.out.mkdir(parents=True)
    with tempfile.TemporaryDirectory(prefix="spec-site-") as tmp:
        for version in versions:
            build(version, args.out, Path(tmp), site_url, args.strict, args.pr)
    git("worktree", "prune")
    write_root(versions, args.out, site_url)


if __name__ == "__main__":
    main()
