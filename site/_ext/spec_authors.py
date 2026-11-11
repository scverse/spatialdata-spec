"""Credit the people of a specification on its page, from the authors.yml of its branch.

Each spec branch (data-model, storage-format) keeps an authors.yml: people with a role (author or
contributor) and a description of their contributions. For the pages data-model and storage-format,
this adds, when the file exists:

- under the title, a byline with the authors (role: author, in file order), followed by "with
  contributions from others", linking to the acknowledgements;
- at the end of the page, an Acknowledgements section listing everyone with their contributions,
  and where code contributors and the authors of the SpatialData paper are acknowledged.

A storage format build overlays the data model branch (build.py), whose authors.yml arrives as
data-model-authors.yml so that it does not replace the storage format's own. Versions without an
authors.yml render as before.
"""

import re
from pathlib import Path

import yaml

FILES = {"data-model": ("data-model-authors.yml", "authors.yml"), "storage-format": ("authors.yml",)}
CODE_CONTRIBUTORS = "https://github.com/scverse/spatialdata/graphs/contributors"
PAPER = "https://doi.org/10.1038/s41592-024-02212-x"
H1 = re.compile(r"^# .+$", re.M)


def _people(srcdir, docname):
    for name in FILES[docname]:
        path = Path(srcdir) / name
        if path.is_file():
            return yaml.safe_load(path.read_text(encoding="utf-8")).get("people") or []
    return None


def _person(p):
    links = []
    if p.get("orcid"):
        links.append(f"[ORCID](https://orcid.org/{p['orcid']})")
    if p.get("github"):
        links.append(f"[@{p['github']}](https://github.com/{p['github']})")
    extra = f" ({', '.join(links)})" if links else ""
    return f"- **{p['name']}**{extra}: {' '.join(str(p.get('contributions', '')).split())}"


def add_credits(app, docname, source):
    if docname not in FILES:
        return
    people = _people(app.srcdir, docname)
    if not people:
        return
    label = f"{docname}-acknowledgements"
    authors = [p["name"] for p in people if p.get("role") == "author"]
    others = [p for p in people if p.get("role") != "author"]
    if authors:
        tail = f", with {{ref}}`contributions from others <{label}>`" if others else ""
        byline = f"\n\n:::{{container}} spec-authors\n{', '.join(authors)}{tail}\n:::\n"
        source[0] = H1.sub(lambda m: m.group(0) + byline, source[0], count=1)
    section = [
        f"\n\n({label})=\n## Acknowledgements\n",
        "These are the people who contributed to this specification and its design. Everyone who "
        f"contributed code to the SpatialData libraries is acknowledged on the [GitHub contributors "
        f"page]({CODE_CONTRIBUTORS}), and the authors of the [SpatialData paper]({PAPER}) through "
        "its citation.\n",
        *(_person(p) for p in people),
    ]
    source[0] = source[0].rstrip() + "\n".join(section) + "\n"


def setup(app):
    app.connect("source-read", lambda app, docname, source: add_credits(app, docname, source))
    return {"parallel_read_safe": True, "parallel_write_safe": True}
