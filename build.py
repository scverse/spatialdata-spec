"""Build the website: every version in versions.toml, each from its own branch or tag.

Each storage format version is checked out into a temporary git worktree, the website code in
site/ is copied over its pages, and Sphinx builds it into
_site/data-model/<data model>/storage-format/<storage format>/. Each data model version is also
built on its own, from the newest storage format that encodes it, into
_site/data-model/<data model>/, where no storage format is selected. The site root is the
preferred version with the pages of the site itself (pages/): it holds the pages that show the
latest state for every version (version history, implementations). Every page's navigation lists
all versions, written when the page is built (site/_ext/static_nav.py), so that it works without
JavaScript; every deploy builds every version. Afterwards, the pages of all builds share the
assets of the root, and sitemap.xml lists the canonical URL of every page; versions.json lists the
versions for other tools.

    uv run build.py                                  # all versions, as published
    uv run build.py --ref my-branch                  # one branch or tag, as a preview
    uv run build.py --source ../spatialdata-spec     # a working copy of the content, as a preview
    uv run build.py --site-url http://localhost:8000/ && python -m http.server -d _site
"""

import argparse
import hashlib
import json
import os
import posixpath
import re
import shutil
import subprocess
import sys
import tempfile
import tomllib
from pathlib import Path
from urllib.parse import urlparse

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


PAGES = HERE / "pages"  # pages of the site itself, built only at the root (latest)


def path_of(version):
    if version.get("latest"):
        return ""
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
            builds.setdefault(
                v["data_model"], {"ref": v["ref"], "source": v.get("source"), "data_model": v["data_model"]}
            )
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
    src = tmp / (path.replace("/", "-") or "latest")
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
        rfc_table(docs)
        if version.get("latest"):
            shutil.copytree(PAGES, docs, dirs_exist_ok=True)
        env = {
            **os.environ,
            "SPEC_REF": version["ref"],
            "SPEC_DOC_PATH": docs.relative_to(src).as_posix().strip("."),
            "SPEC_PATH": path,
            "SPEC_DATA_MODEL": version.get("data_model", ""),
            "SPEC_STORAGE_FORMAT": version.get("storage_format", ""),
            "SPEC_VERSIONS": json.dumps(listed),
            "SPEC_DRAFT": "1" if version.get("draft") else "0",
            "SPEC_LATEST": "1" if version.get("latest") else "0",
            "SPEC_PREVIEW_PR": preview_pr,
            "SITE_URL": site_url,
        }
        cmd = [sys.executable, "-m", "sphinx", "-b", "html", "-d", str(src / "_doctrees"), str(docs), str(out / path)]
        if strict:
            cmd += ["-W", "--keep-going"]
        print(f"--- {version['ref']} -> {path or '(root)'}/", flush=True)
        subprocess.run(cmd, env=env, check=True)
    finally:
        if not version.get("source"):
            git("worktree", "remove", "--force", str(src))


def rfc_table(docs):
    """The table of RFCs on rfcs.md, from the headers of the files in rfcs/."""
    import yaml

    rows = []
    for path in sorted((docs / "rfcs").glob("*.md")):
        head = yaml.safe_load(path.read_text(encoding="utf-8").split("---\n", 2)[1])
        spec = f" ([specification change]({head['spec-pr']}))" if head.get("spec-pr") else ""
        rows.append(
            f"| {head['rfc']} | {{doc}}`{head['title']} <rfcs/{path.stem}>` | {head['scope']} | {head['targets']} "
            f"| {head['proposed-by']} | {head['status']}{spec} |"
        )
    header = [
        "| No. | RFC | Scope | Targets | Proposed by | Status |",
        "|-----|-----|-------|---------|-------------|--------|",
    ]
    page = docs / "rfcs.md"
    text = page.read_text(encoding="utf-8")
    start, end = "% begin rfc-table\n", "% end rfc-table"
    table = "\n".join(header + rows) + "\n"
    page.write_text(text[: text.index(start) + len(start)] + table + text[text.index(end) :], encoding="utf-8")


ASSET_DIRS = ("_static", "_sphinx_design_static")


def _digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def share_assets(out):
    """Point the pages of every build to the assets of the root build where they are the same file, so
    that browsers load them once for all versions, and remove the copies."""
    builds = sorted(p.parent for p in out.rglob("searchindex.js"))  # one per Sphinx build
    shared = {
        path.relative_to(out).as_posix(): _digest(path)
        for name in ASSET_DIRS
        for path in (out / name).rglob("*")
        if path.is_file()
    }
    link = re.compile(r'((?:href|src)=")((?:\.\./)*)((?:' + "|".join(ASSET_DIRS) + r')/[^"?#]*)')
    for build_dir in builds:
        if build_dir == out:
            continue
        same = {
            rel
            for name in ASSET_DIRS
            for path in (build_dir / name).rglob("*")
            if path.is_file() and shared.get(rel := path.relative_to(build_dir).as_posix()) == _digest(path)
        }
        nested = [b for b in builds if b != build_dir and build_dir in b.parents]
        for page in build_dir.rglob("*.html"):
            rel = page.relative_to(build_dir)
            if rel.parts[0] in ASSET_DIRS or any(b in page.parents for b in nested):
                continue
            depth, to_root = len(rel.parts) - 1, posixpath.relpath(out.as_posix(), page.parent.as_posix())

            def root(m, depth=depth, to_root=to_root, same=same):
                if len(m.group(2)) // 3 != depth or m.group(3) not in same:
                    return m.group(0)  # not one of this build's shared assets
                return f"{m.group(1)}{to_root}/{m.group(3)}"

            page.write_text(link.sub(root, page.read_text(encoding="utf-8")), encoding="utf-8")
        for rel in same:
            (build_dir / rel).unlink()
        for name in ASSET_DIRS:  # remove the directories left empty
            for d in [*sorted((build_dir / name).rglob("*"), reverse=True), build_dir / name]:
                if d.is_dir() and not any(d.iterdir()):
                    d.rmdir()


def write_sitemap(out, site_url):
    """sitemap.xml with the canonical URL of every page, and robots.txt."""
    urls = set()
    for page in out.rglob("*.html"):
        rel = page.relative_to(out).as_posix()
        if rel.startswith(("_", "preview/")) or "/_" in rel or page.name in ("genindex.html", "search.html"):
            continue
        m = re.search(r'<link rel="canonical" href="([^"]+)"', page.read_text(encoding="utf-8"))
        if m and m.group(1).startswith(site_url):
            urls.add(m.group(1))
    entries = "\n".join(f"  <url><loc>{url}</loc></url>" for url in sorted(urls))
    (out / "sitemap.xml").write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        f'<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n{entries}\n</urlset>\n',
        encoding="utf-8",
    )
    # read by crawlers only at the root of a domain: for a site below a path, the sitemap is
    # submitted in the search engine's console instead
    base = urlparse(site_url).path
    (out / "robots.txt").write_text(
        f"User-agent: *\nDisallow: {base}*_sources/\nDisallow: {base}preview/\n\nSitemap: {site_url}sitemap.xml\n",
        encoding="utf-8",
    )


def write_root(listed, out, site_url):
    (out / "versions.json").write_text(json.dumps(listed, indent=2) + "\n")
    (out / ".nojekyll").touch()  # serve _static/ as is on GitHub Pages
    share_assets(out)
    write_sitemap(out, site_url)


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
        # the root: the preferred version with the pages of the site, which show the latest state
        # (version history, implementations) for every version
        preferred = next(v for v in versions if v.get("preferred"))
        latest = {"ref": preferred["ref"], "source": preferred.get("source"), "latest": True}
        versions = [latest, *data_models(versions), *versions]

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
