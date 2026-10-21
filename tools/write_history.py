"""Write the versions of the specification from this branch into the branch main.

This branch (history-draft) holds all versions side by side: where versions differ, version tabs
(sync group "storage-version") give the text of each. For every version in tools/history.toml,
oldest first, this script writes the text of that version alone (Markdown and images only, flat
layout) and commits it to main, tagged storage-format-<name>. A draft version is committed
without a tag. Released versions are never rewritten: if the text of a released version changes
here, the script warns and leaves its tag alone. main only moves forward (no force push).

    python tools/write_history.py                 # commit and tag on the local branch main
    python tools/write_history.py --out _main     # only write the files, to _main/<version>/
"""

import argparse
import os
import posixpath
import re
import shutil
import subprocess
import sys
import tempfile
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REPO_URL = "https://github.com/scverse/spatialdata-spec"
SOURCE_BRANCH = "history-draft"
TAG = "storage-format-{}"

# pages on main: docname here (relative to docs/) -> file on main
PAGES = {
    "index": "index.md",
    "spec/data-model": "data-model.md",
    "spec/storage-format": "storage-format.md",
    "spec/storage-format/versions": "versions.md",
    "spec/storage-format/ngff-compatibility": "ngff-compatibility.md",
    "rfcs": "rfcs.md",
}
IMAGES = ROOT / "docs/_static/img"


def source_path(docname):
    """The Markdown file of a docname, relative to the repository root."""
    return f"{docname}.md" if docname.startswith("spec/") else f"docs/{docname}.md"


def page_title(docname):
    text = (ROOT / source_path(docname)).read_text(encoding="utf-8")
    return re.search(r"^# (.+)$", text, flags=re.M).group(1).strip()


def all_docnames():
    names = {p.relative_to(ROOT / "docs").with_suffix("").as_posix() for p in (ROOT / "docs").glob("*.md")}
    return names | {
        f"spec/{p.relative_to(ROOT / 'spec').with_suffix('').as_posix()}" for p in (ROOT / "spec").rglob("*.md")
    }


def labels():
    """label -> (docname, title of the heading that follows it)."""
    found = {}
    for docname in all_docnames():
        lines = (ROOT / source_path(docname)).read_text(encoding="utf-8").split("\n")
        for i, line in enumerate(lines):
            m = re.fullmatch(r"\(([\w-]+)\)=", line)
            if m:
                heading = next((h for h in lines[i + 1 : i + 4] if h.startswith("#")), "")
                found[m.group(1)] = (docname, heading.lstrip("# ").strip())
    return found


def select_version(text, version, base):
    """Keep, of every version tab set, the tab of this version (a draft falls back to its base)."""
    lines, out, i = text.split("\n"), [], 0
    want, fallback = f"container-{version['container']}", base and f"container-{base}"
    while i < len(lines):
        m = re.fullmatch(r"(:{4,})\{tab-set\}", lines[i])
        if not (m and lines[i + 1].strip() == ":sync-group: storage-version"):
            out.append(lines[i])
            i += 1
            continue
        close, item_close = m.group(1), m.group(1)[1:]
        end = lines.index(close, i + 1)
        items, j = {}, i + 2
        while j < end:
            if lines[j].startswith(item_close + "{tab-item}"):
                k = lines.index(item_close, j + 1)
                body = lines[j + 1 : k]
                sync = next(b.split(":", 2)[2].strip() for b in body if b.startswith(":sync:"))
                while body and (body[0].startswith(":") or not body[0].strip()):
                    body = body[1:]
                items[sync] = body
                j = k
            j += 1
        chosen = items.get(want, items.get(fallback))
        if chosen is not None:  # no tab: the passage does not exist in this version
            out += chosen
        i = end + 1
    return "\n".join(out)


def badges(text, version):
    """The version badges of a section, for this version only."""

    def line(m):
        element = m.group(1)
        return f"{{bdg-primary}}`{element} {version['elements'][element]}` {{bdg-light}}`Zarr {version['zarr']}`"

    return re.sub(r"^\{bdg-primary\}`(raster|shapes|points|tables) .*$", line, text, flags=re.M)


def version_note(text, version):
    e = version["elements"]
    note = (
        f"This is version {version['name']} of the SpatialData storage format. It encodes version "
        f"{version['data_model']} of the {{doc}}`abstract data model <data-model>`, in the container format "
        f"`spatialdata-container-format-{version['container']}` (Zarr {version['zarr']}; OME-Zarr "
        f"{version['ngff']}) with raster {e['raster']}, shapes {e['shapes']}, points {e['points']} and tables "
        f"{e['tables']} elements. It is written by `spatialdata` {version['written_by']}. All versions are "
        f"listed in {{ref}}`storage-versions`."
    )
    if version.get("unspecified"):
        items = "\n".join(f"- {line}" for line in version["unspecified"])
        note += (
            "\n\n:::{admonition} Not yet specified in full\n:class: open-question\n\n"
            "This page describes later element versions where these differ:\n\n"
            f"{items}\n:::"
        )
    return re.sub(
        r"(\(storage-intro-versions\)=\n#+ Versions\n\n).*?\n\n(?=\()",
        lambda m: m.group(1) + note + "\n\n",
        text,
        flags=re.S,
    )


def citations(text):
    bib = (ROOT / "docs/references.bib").read_text(encoding="utf-8")

    def cite(m):
        entry = re.search(r"@\w+\{" + re.escape(m.group(1)) + r",(.*?)\n\}", bib, flags=re.S).group(1)
        field = lambda name: re.search(rf"{name}\s*=\s*\{{?(.*?)\}}?,?\n", entry).group(1)
        first = field("author").split(" and ")[0].split()[-1]
        return f"([{first} et al., {field('year')}](https://doi.org/{field('doi')}))"

    text = re.sub(r"\{cite:p\}`([^`]+)`", cite, text)
    return re.sub(r"## References\n\n```\{bibliography\}\n.*?```\n\n", "", text, flags=re.S)


def links(text, docname, label_map):
    """Point references at the flat layout of main, or at this branch on GitHub for other pages."""

    def target(name):
        resolved = (
            name.lstrip("/")
            if name.startswith("/")
            else posixpath.normpath(posixpath.join(posixpath.dirname(docname), name))
        )
        return resolved

    def github(doc):
        return f"{REPO_URL}/blob/{SOURCE_BRANCH}/{source_path(doc)}"

    def doc(m):
        title, name = (m.group(2), m.group(3)) if m.group(3) else (None, m.group(1))
        resolved = target(name)
        if resolved in PAGES:
            new = "/" + PAGES[resolved][:-3]
            return f"{{doc}}`{title} <{new}>`" if title else f"{{doc}}`{new}`"
        return f"[{title or page_title(resolved)}]({github(resolved)})"

    def ref(m):
        title, label = (m.group(2), m.group(3)) if m.group(3) else (None, m.group(1))
        where, heading = label_map[label]
        if where in PAGES:
            return m.group(0)
        return f"[{title or heading}]({github(where)})"

    def toctree(m):
        entries = [PAGES[target(e)][:-3] for e in m.group(2).split("\n") if e and target(e) in PAGES]
        return m.group(1) + "\n".join(entries) + "\n```"

    def card(m):
        name = target(m.group(1))
        return f":link: /{PAGES[name][:-3]}\n:link-type: doc" if name in PAGES else m.group(0)

    text = re.sub(r"^:link: (\S+)\n:link-type: doc", card, text, flags=re.M)
    text = re.sub(r"(```\{toctree\}\n(?::.*\n)*\n)(.*?)\n```", toctree, text, flags=re.S)
    text = re.sub(r"\{doc\}`(([^`<]*?) <([^`>]+)>|[^`<]+)`", doc, text)
    text = re.sub(r"\{ref\}`(([^`<]*?) <([^`>]+)>|[^`<]+)`", ref, text)
    return (
        text.replace("](/_static/img/", "](/img/").replace("/_static/img/", "/img/").replace("](_static/img/", "](img/")
    )


README = """\
# SpatialData specifications: storage format {name}

This branch holds one version of the [SpatialData](https://github.com/scverse/spatialdata)
specification: version {name} of the storage format, which encodes version {data_model} of the
abstract data model (container format `spatialdata-container-format-{container}`).

- [`data-model.md`](data-model.md): the abstract data model
- [`storage-format.md`](storage-format.md): the storage format, with each part of the data model
- [`versions.md`](versions.md): all versions; [`rfcs.md`](rfcs.md): proposals

Every version is a tag `storage-format-<version>` of this branch. The files here are generated
by `tools/write_history.py` from the branch [`{source}`]({repo}/tree/{source}), where all versions
are edited side by side; propose changes there. The website is built by the branch
[`site`]({repo}/tree/site).

The specification text is licensed under CC-BY-4.0 ([LICENSE.md](LICENSE.md)).
"""


def write_version(version, base, dest):
    """Write the files of one version into the directory dest."""
    label_map = labels()
    for docname, name in PAGES.items():
        text = (ROOT / source_path(docname)).read_text(encoding="utf-8")
        text = select_version(text, version, base)
        text = badges(text, version)
        if docname == "spec/storage-format":
            text = version_note(text, version)
        text = citations(links(text, docname, label_map))
        text = re.sub(r"\n{3,}", "\n\n", text)
        (dest / name).write_text(text, encoding="utf-8", newline="\n")
    (dest / "img").mkdir()
    for image in IMAGES.iterdir():
        if image.suffix in (".svg", ".png"):
            shutil.copy(image, dest / "img" / image.name)
    shutil.copy(ROOT / "spec/LICENSE", dest / "LICENSE.md")
    readme = README.format(source=SOURCE_BRANCH, repo=REPO_URL, **version)
    (dest / "README.md").write_text(readme, encoding="utf-8", newline="\n")


def git(*args, env=None, check=True):
    result = subprocess.run(["git", *args], cwd=ROOT, env=env, capture_output=True, text=True)
    if check and result.returncode:
        sys.exit(f"git {' '.join(args)}: {result.stderr.strip()}")
    return result.stdout.strip()


def tree_of(directory, tmp):
    env = {**os.environ, "GIT_INDEX_FILE": str(tmp / "index")}
    git("read-tree", "--empty", env=env)
    git(f"--work-tree={directory}", "add", "--all", "--force", ".", env=env)
    return git("write-tree", env=env)


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--branch", default="main", help="branch to write to (default: main)")
    parser.add_argument("--out", type=Path, help="only write the files of each version to OUT/<version>/")
    args = parser.parse_args()

    versions = tomllib.loads((ROOT / "tools/history.toml").read_text(encoding="utf-8"))["version"]
    drafts = [v for v in versions if v.get("draft")]
    if len(drafts) > 1 or (drafts and versions[-1] is not drafts[0]):
        sys.exit("write_history.py: at most one draft, and it must be the last version")

    if args.out:
        shutil.rmtree(args.out, ignore_errors=True)
        for version in versions:
            (args.out / version["name"]).mkdir(parents=True)
            write_version(version, version.get("base"), args.out / version["name"])
        print(f"wrote {', '.join(v['name'] for v in versions)} to {args.out}")
        return

    ref = f"refs/heads/{args.branch}"
    if f"[{args.branch}]" in git("worktree", "list"):
        sys.exit(f"write_history.py: {args.branch} is checked out in a worktree; this script writes it directly")
    head = git("rev-parse", "--verify", "--quiet", ref, check=False)
    remote = git("rev-parse", "--verify", "--quiet", f"refs/remotes/origin/{args.branch}", check=False)
    behind = (
        head
        and remote
        and subprocess.run(["git", "merge-base", "--is-ancestor", head, remote], cwd=ROOT).returncode == 0
    )
    if remote and (not head or behind):
        head = remote  # the local branch is missing or behind origin: build on origin, so a push fast-forwards
    source = git("rev-parse", "--short", "HEAD")
    with tempfile.TemporaryDirectory(prefix="write-history-") as tmp:
        tmp = Path(tmp)
        for version in versions:
            files = tmp / version["name"]
            files.mkdir()
            write_version(version, version.get("base"), files)
            tree = tree_of(files, tmp)
            tag = TAG.format(version["name"])
            if not version.get("draft") and git("rev-parse", "--verify", "--quiet", f"refs/tags/{tag}", check=False):
                if git("rev-parse", f"{tag}^{{tree}}") != tree:
                    print(f"warning: {tag} is released; its text here has changed and is not rewritten")
                continue
            if git("rev-parse", f"{head}^{{tree}}") != tree:
                kind = "draft of storage format" if version.get("draft") else "storage format"
                message = (
                    f"{kind} {version['name']} (data model {version['data_model']}, container "
                    f"{version['container']})\n\nGenerated by tools/write_history.py from {SOURCE_BRANCH} {source}."
                )
                head = git("commit-tree", tree, "-p", head, "-m", message)
                print(f"committed {kind} {version['name']}: {head[:7]}")
            if not version.get("draft"):
                git("tag", "-a", tag, head, "-m", f"SpatialData storage format {version['name']}")
                print(f"tagged {tag}")
        old = git("rev-parse", "--verify", "--quiet", ref, check=False)
        git("update-ref", ref, head, *([old] if old else []))
    print(f"{args.branch} is at {head[:7]}")


if __name__ == "__main__":
    main()
