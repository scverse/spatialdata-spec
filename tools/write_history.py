"""Write the history of the branch main from this branch: one commit and tag per version.

This branch (history-draft) holds all versions of the storage format side by side: where
versions differ, version tabs (sync group "storage-version") give the text of each. For every
version in VERSIONS, oldest first, this script writes the text of that version alone and commits
it to main, tagged storage-format-<name>. It runs locally, once; afterwards main is edited
directly. Released versions are never rewritten: if the text of a released version changes here,
the script warns and leaves its tag alone. main only moves forward; nothing is pushed.

    python tools/write_history.py                 # commit and tag on the local branch main
    python tools/write_history.py --out _main     # only write the files, to _main/<version>/
"""

import argparse
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TAG = "storage-format-{}"

# The storage format versions, oldest first: one per row of the compatibility matrix
# (storage-format-versions.md). name: storage format version, which selects the version tabs
# (:sync: sf-<first>[-<last>]); data_model: version of the abstract data model it encodes;
# container: container format version; zarr, ngff: the Zarr and OME-Zarr (NGFF) versions;
# elements: element versions; written_by: the spatialdata releases that write it; recorded: whether
# its stores record the container format version ("never", "sometimes"; default: always).
CONTAINER_01 = {"data_model": "1.0", "container": "0.1", "zarr": "v2"}
VERSIONS = [
    {
        **CONTAINER_01,
        "name": "0.1",
        "recorded": "never",
        "ngff": '0.4, written as `"0.4"`',
        "elements": {"raster": "0.1", "shapes": "0.1", "points": "0.1", "tables": "0.1"},
        "written_by": "releases before 0.2.2",
    },
    {
        **CONTAINER_01,
        "name": "0.2",
        "recorded": "sometimes",
        "ngff": '0.4, written as `"0.4"`',
        "elements": {"raster": "0.1", "shapes": "0.2", "points": "0.1", "tables": "0.1"},
        "written_by": "0.2.2 to 0.3.x",
    },
    {
        **CONTAINER_01,
        "name": "0.3",
        "ngff": '0.4, written as `"0.4-dev-spatialdata"`',
        "elements": {"raster": "0.2", "shapes": "0.2", "points": "0.1", "tables": "0.1"},
        "written_by": "0.4.0 to 0.5.x",
    },
    {
        **CONTAINER_01,
        "name": "0.4",
        "ngff": '0.4, written as `"0.4-dev-spatialdata"`',
        "elements": {"raster": "0.2", "shapes": "0.2", "points": "0.1", "tables": "0.1"},
        "written_by": "0.6.0 and later on request (deprecated); the same bytes as storage format 0.3",
    },
    {
        "name": "0.5",
        "data_model": "1.0",
        "container": "0.2",
        "zarr": "v3",
        "ngff": '0.5, written as `"0.5-dev-spatialdata"`',
        "elements": {"raster": "0.3", "shapes": "0.3", "points": "0.2", "tables": "0.2"},
        "written_by": "0.6.0 and later, by default",
    },
]

# the pages on main; the others (CHANGELOG.md, planning/) stay on this branch only
PAGES = [
    "index",
    "data-model",
    "data-model-versions",
    "storage-format",
    "storage-format-conformance",
    "storage-format-versions",
    "rfcs",
    "contributing",
]

# pages written unchanged to every version (their version tabs are examples)
SAME_IN_ALL_VERSIONS = ["contributing"]

README = """\
# SpatialData specifications: storage format {name}

This branch holds one version of the [SpatialData](https://github.com/scverse/spatialdata)
specification: version {name} of the storage format, which encodes version {data_model} of the
abstract data model (container format `spatialdata-container-format-{container}`).

- [`data-model.md`](data-model.md): the abstract data model
- [`storage-format.md`](storage-format.md): the storage format, with each part of the data model
- [`data-model-versions.md`](data-model-versions.md), [`storage-format-versions.md`](storage-format-versions.md):
  all versions; [`rfcs.md`](rfcs.md): proposals

Every version is a tag `storage-format-<version>` of this branch; its history up to storage format
{name} was written by `tools/write_history.py`. The website is built by the branch `site`.

The specification text is licensed under CC-BY-4.0 ([LICENSE.md](LICENSE.md)).
"""


def page_title(name):
    text = (ROOT / f"{name}.md").read_text(encoding="utf-8")
    return re.search(r"^# (.+)$", text, flags=re.M).group(1).strip()


def labels():
    """label -> (page, title of the heading that follows it)."""
    found = {}
    for path in ROOT.glob("*.md"):
        lines = path.read_text(encoding="utf-8").split("\n")
        for i, line in enumerate(lines):
            m = re.fullmatch(r"\(([\w-]+)\)=", line)
            if m:
                heading = next((h for h in lines[i + 1 : i + 4] if h.startswith("#")), "")
                found[m.group(1)] = (path.stem, heading.lstrip("# ").strip())
    return found


def number(name):
    return tuple(int(part) for part in name.split("."))


def covers(sync, version):
    """Whether a version tab, :sync: sf-<first>[-<last>], covers this storage format version."""
    first, _, last = sync.removeprefix("sf-").partition("-")
    return number(first) <= number(version["name"]) <= number(last or first)


def select_version(text, version):
    """Keep, of every version tab set, the tab of this version (tab sets may be nested)."""
    lines, out, i = text.split("\n"), [], 0
    while i < len(lines):
        m = re.fullmatch(r"(:{4,})\{tab-set\}", lines[i])
        if not (m and lines[i + 1].strip() == ":sync-group: storage-version"):
            out.append(lines[i])
            i += 1
            continue
        close, item_close = m.group(1), m.group(1)[1:]
        end = lines.index(close, i + 1)
        kept, j = [], i + 2
        while j < end:
            if lines[j].startswith(item_close + "{tab-item}"):
                k = lines.index(item_close, j + 1)
                body = lines[j + 1 : k]
                sync = next(b.split(":", 2)[2].strip() for b in body if b.startswith(":sync:"))
                while body and (body[0].startswith(":") or not body[0].strip()):
                    body = body[1:]
                if covers(sync, version):
                    if kept:
                        sys.exit(f"write_history.py: two version tabs for {version['name']}: {lines[j]}")
                    kept = select_version("\n".join(body), version).split("\n")
                j = k
            j += 1
        out += kept  # no tab: the passage does not exist in this version
        i = end + 1
    return "\n".join(out)


def badges(text, version):
    """The version badges of a section, for this version only."""

    def line(m):
        element = m.group(1)
        return f"{{bdg-primary}}`{element} {version['elements'][element]}` {{bdg-light}}`Zarr {version['zarr']}`"

    return re.sub(r"^\{bdg-primary\}`(raster|shapes|points|tables) .*$", line, text, flags=re.M)


def version_note(text, version):
    """Replace the Versions section, which explains the version tabs of this branch, with what this
    version is."""
    e = version["elements"]
    recorded = {"never": ", which they do not record,", "sometimes": ", which they may not record,"}.get(
        version.get("recorded"), ""
    )
    note = (
        f"This is version {version['name']} of the storage format. It encodes version "
        f"{version['data_model']} of the abstract data model. Its stores are Zarr {version['zarr']} "
        f"hierarchies of container format `spatialdata-container-format-{version['container']}`{recorded} and hold "
        f"raster {e['raster']}, shapes {e['shapes']}, points {e['points']} and tables {e['tables']} elements; "
        f"raster elements follow OME-Zarr (NGFF) {version['ngff']}.\n\n"
    )
    return re.sub(
        r"\(storage-intro-versions\)=\n#+ Versions\n\n.*?\n\n(?=\()",
        lambda m: note,
        text,
        flags=re.S,
    )


def footnotes(text):
    """Drop the footnotes that only the passages of other versions refer to."""
    used = set(re.findall(r"\[\^([\w-]+)\](?!:)", text))
    out, keep = [], True
    for line in text.split("\n"):
        m = re.match(r"\[\^([\w-]+)\]:", line)
        if m:
            keep = m.group(1) in used
        elif not line.startswith("    "):  # the end of a footnote: a line that does not continue it
            keep = True
        if keep:
            out.append(line)
    text = "\n".join(out)
    if not re.search(r"^\[\^[\w-]+\]:", text, flags=re.M):  # no footnotes left: no section for them
        text = re.sub(r"^## Notes\n\n(?:% .*\n\n)?", "", text, flags=re.M)
    return text


def links(text, label_map):
    """References to pages that are not on main become plain text."""

    def doc(m):
        title, name = (m.group(2), m.group(3)) if m.group(3) else (None, m.group(1))
        name = name.lstrip("/")
        return m.group(0) if name in PAGES else (title or page_title(name))

    def ref(m):
        title, label = (m.group(2), m.group(3)) if m.group(3) else (None, m.group(1))
        if label not in label_map:  # not a reference, e.g. {ref} quoted in inline code
            return m.group(0)
        where, heading = label_map[label]
        return m.group(0) if where in PAGES else (title or heading)

    def toctree(m):
        def target(entry):  # "page" or "Title <page>"
            return entry[entry.rfind("<") + 1 : -1] if entry.endswith(">") else entry

        return m.group(1) + "\n".join(e for e in m.group(2).split("\n") if target(e) in PAGES) + "\n```"

    text = re.sub(r"(```\{toctree\}\n(?::.*\n)*\n)(.*?)\n```", toctree, text, flags=re.S)
    text = re.sub(r"\{doc\}`(([^`<]*?) <([^`>]+)>|[^`<]+)`", doc, text)
    return re.sub(r"\{ref\}`(([^`<]*?) <([^`>]+)>|[^`<]+)`", ref, text)


def write_version(version, dest):
    """Write the files of one version into the directory dest."""
    label_map = labels()
    for name in PAGES:
        text = (ROOT / f"{name}.md").read_text(encoding="utf-8")
        if name not in SAME_IN_ALL_VERSIONS:
            text = footnotes(badges(select_version(text, version), version))
        if name == "storage-format":
            text = version_note(text, version)
        text = re.sub(r"\n{3,}", "\n\n", links(text, label_map))
        (dest / f"{name}.md").write_text(text, encoding="utf-8", newline="\n")
    shutil.copytree(ROOT / "img", dest / "img")
    shutil.copy(ROOT / "LICENSE.md", dest / "LICENSE.md")
    (dest / "README.md").write_text(README.format(**version), encoding="utf-8", newline="\n")


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

    if args.out:
        shutil.rmtree(args.out, ignore_errors=True)
        for version in VERSIONS:
            (args.out / version["name"]).mkdir(parents=True)
            write_version(version, args.out / version["name"])
        print(f"wrote {', '.join(v['name'] for v in VERSIONS)} to {args.out}")
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
        for version in VERSIONS:
            files = tmp / version["name"]
            files.mkdir()
            write_version(version, files)
            tree = tree_of(files, tmp)
            tag = TAG.format(version["name"])
            if git("rev-parse", "--verify", "--quiet", f"refs/tags/{tag}", check=False):
                if git("rev-parse", f"{tag}^{{tree}}") != tree:
                    print(f"warning: {tag} is released; its text here has changed and is not rewritten")
                continue
            if git("rev-parse", f"{head}^{{tree}}") != tree:
                message = (
                    f"storage format {version['name']} (data model {version['data_model']}, container "
                    f"{version['container']})\n\nGenerated by tools/write_history.py from history-draft {source}."
                )
                head = git("commit-tree", tree, "-p", head, "-m", message)
                print(f"committed storage format {version['name']}: {head[:7]}")
            git(
                "tag",
                "-a",
                tag,
                head,
                "-m",
                f"SpatialData storage format {version['name']} (data model {version['data_model']})",
            )
            print(f"tagged {tag}")
        old = git("rev-parse", "--verify", "--quiet", ref, check=False)
        git("update-ref", ref, head, *([old] if old else []))
    print(f"{args.branch} is at {head[:7]}")


if __name__ == "__main__":
    main()
