"""Write the branches of the specification from this branch, which holds all versions side by side.

Until the switch to them, the specification is edited here and written to its branches: the
newest storage format version to storage-format, each older one to
maintenance/storage-format-<version>, the data model to data-model (an older data model version to
maintenance/data-model-<version>). Each version is written as tools/write_history.py writes it, and
its files are split: the data model text (data-model.md, data-model-versions.md, img/) goes to the
data model's branch, written once for every storage format version that encodes it, the storage
format text to the storage format's. A branch whose text changed gets one new commit on top of its
history; nothing is rewritten, no tag is moved and nothing is pushed. Each branch keeps its own
.github/ (its workflows).

    python tools/split_branches.py            # commit on the local branches, then push them
    python tools/split_branches.py --dry-run  # only say which branches change
"""

import argparse
import os
import shutil
import subprocess
import sys
import tarfile
import tempfile
from io import BytesIO
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import write_history

ROOT = write_history.ROOT
DATA_MODEL_FILES = ["data-model.md", "data-model-versions.md", "img"]
STORAGE_FORMAT_FILES = ["storage-format.md", "storage-format-versions.md", "storage-format-conformance.md"]
COMMON_FILES = ["LICENSE.md"]

CONTRIBUTING = """# Contributing

How to propose a change to the specification, and the RFCs, are described in the contributing
guide on the website (branch `site`, `site/contributing.md`). Changes to the {what} are pull
requests against this branch; a change that also needs the {other} changed goes with a pull
request against the branch `{other_branch}`.
"""

DATA_MODEL_README = """# SpatialData specifications: data model {dm}

This branch holds the abstract data model of the [SpatialData](https://github.com/scverse/spatialdata)
specification, version {dm}: what a SpatialData dataset is, independently of how it is stored or
represented in memory.

- [`data-model.md`](data-model.md): the abstract data model
- [`data-model-versions.md`](data-model-versions.md): all data model versions
- [`img/`](img/): its figures

Its encodings are specified elsewhere, each referring to the data model version it encodes: the
storage format on the branch `storage-format`, whose pages include the parts of the data model
they encode; the in-memory formats in the repositories of the implementations. The website
(branch `site`) builds them together.

Every data model version is a tag `data-model-<version>`, the text as first released. This branch
holds the current version, with the editorial corrections made since; how to contribute is in
[`.github/CONTRIBUTING.md`](.github/CONTRIBUTING.md).

The specification text is licensed under CC-BY-4.0 ([LICENSE.md](LICENSE.md)).
"""

STORAGE_FORMAT_README = """# SpatialData specifications: storage format {sf}

This branch holds the storage format of the [SpatialData](https://github.com/scverse/spatialdata)
specification, version {sf}: how a dataset is stored (Zarr, Parquet, built on OME-NGFF). It encodes
version {dm} of the abstract data model (container format {container}), which is on the branch
`data-model`: each part of the storage format follows the part of the data model it encodes,
included from there when the website (branch `site`) builds the pages.

- [`storage-format.md`](storage-format.md): the storage format
- [`storage-format-conformance.md`](storage-format-conformance.md): example stores and validation
- [`storage-format-versions.md`](storage-format-versions.md): all storage format versions

Every storage format version is a tag `storage-format-<version>`, the text as first released. This
branch holds the current version, with the editorial corrections made since; how to contribute is
in [`.github/CONTRIBUTING.md`](.github/CONTRIBUTING.md).

The specification text is licensed under CC-BY-4.0 ([LICENSE.md](LICENSE.md)).
"""


def git(*args, env=None, check=True, text=True):
    result = subprocess.run(["git", *args], cwd=ROOT, env=env, capture_output=True, text=text)
    if check and result.returncode:
        sys.exit(f"git {' '.join(args)}: {result.stderr}")
    return result.stdout.strip() if text else result.stdout


def tree_of(directory, tmp):
    env = {**os.environ, "GIT_INDEX_FILE": str(Path(tmp) / f"index-{directory.name}")}
    git("read-tree", "--empty", env=env)
    git(f"--work-tree={directory}", "add", "--all", "--force", ".", env=env)
    return git("write-tree", env=env)


def keep_github(branch, dest):
    """The branch's own .github/ (its workflows), which is not written from here."""
    archive = git("archive", f"refs/heads/{branch}", "--", ".github", check=False, text=False)
    if archive:
        with tarfile.open(fileobj=BytesIO(archive)) as tar:
            tar.extractall(dest, filter="data")


def stage(written, files, branch, readme, contributing, dest):
    dest.mkdir()
    for name in files + COMMON_FILES:
        src = written / name
        (shutil.copytree if src.is_dir() else shutil.copy2)(src, dest / name)
    keep_github(branch, dest)
    (dest / "README.md").write_text(readme, encoding="utf-8")
    (dest / ".github").mkdir(exist_ok=True)
    (dest / ".github" / "CONTRIBUTING.md").write_text(contributing, encoding="utf-8")


def commit(branch, directory, message, tmp, dry_run):
    head = git("rev-parse", "--verify", "--quiet", f"refs/heads/{branch}", check=False)
    if not head:
        sys.exit(f"split_branches.py: no local branch {branch}; fetch it first (git fetch origin {branch}:{branch})")
    tree = tree_of(directory, tmp)
    if tree == git("rev-parse", f"{head}^{{tree}}"):
        print(f"{branch}: unchanged")
        return
    if dry_run:
        print(f"{branch}: would change")
        return
    new = git("commit-tree", tree, "-p", head, "-m", message)
    git("update-ref", f"refs/heads/{branch}", new, head)
    print(f"{branch}: {head[:7]} -> {new[:7]}")


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--dry-run", action="store_true", help="only say which branches change")
    args = parser.parse_args()
    source = git("rev-parse", "--short", "HEAD")
    versions = write_history.VERSIONS
    newest = versions[-1]
    newest_model = newest["data_model"]
    with tempfile.TemporaryDirectory(prefix="split-") as tmp:
        tmp = Path(tmp)
        for version in versions:
            (tmp / "out" / version["name"]).mkdir(parents=True)
            write_history.write_version(version, tmp / "out" / version["name"])
        models = {}  # each data model version from the newest storage format version that encodes it
        for version in versions:
            models[version["data_model"]] = version
        for model, version in models.items():
            branch = "data-model" if model == newest_model else f"maintenance/data-model-{model}"
            readme = DATA_MODEL_README.format(dm=model)
            contributing = CONTRIBUTING.format(what="data model", other="storage format", other_branch="storage-format")
            dest = tmp / f"dm-{model}"
            stage(tmp / "out" / version["name"], DATA_MODEL_FILES, branch, readme, contributing, dest)
            commit(branch, dest, f"data model {model}: written from {source} of main", tmp, args.dry_run)
        for version in versions:
            name, model, container = version["name"], version["data_model"], version["container"]
            branch = "storage-format" if version is newest else f"maintenance/storage-format-{name}"
            readme = STORAGE_FORMAT_README.format(sf=name, dm=model, container=container)
            contributing = CONTRIBUTING.format(what="storage format", other="data model", other_branch="data-model")
            dest = tmp / f"sf-{name}"
            stage(tmp / "out" / name, STORAGE_FORMAT_FILES, branch, readme, contributing, dest)
            message = (
                f"storage format {name} (data model {model}, container {container}): written from {source} of main"
            )
            commit(branch, dest, message, tmp, args.dry_run)


if __name__ == "__main__":
    main()
