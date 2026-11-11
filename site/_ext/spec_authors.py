"""Credit the people of a specification on its page, from the authors.yml of its branch.

Each spec branch (data-model, storage-format) keeps an authors.yml: people with a role (editor or
contributor), a part (specification: worked on this specification; origins: built the design,
format or implementation it is based on) and a description of their contributions, plus groups
acknowledged through a link (the SpatialData paper, the package's code contributors). For the pages
data-model and storage-format, this adds, when the file exists:

- under the title: the editors; if there are authors besides them, the authors (editors and role:
  author, in file order), who are also the authors of the version's citation; the original
  designers (basis: original design, with the reference in original_design), as long as not all
  of them are authors; then "Published by
  scverse; developed by the SpatialData community", linking to the contributors. Each person's
  ORCID and GitHub icons appear at their first mention;
- at the end of the page, a "Contributors and acknowledgements" section: one compact paragraph for
  the contributors to this specification and one for its origins and prior work;
- an explicit page description (og:description and meta description), so that the byline does not
  become the description of the page in search results and link previews.

Names are plain text, followed by an ORCID iD icon and a GitHub icon, each linked. A storage format
build overlays the data model branch (build.py), whose authors.yml arrives as data-model-authors.yml
so that it does not replace the storage format's own. Versions without an authors.yml render as
before.
"""

import re
from pathlib import Path

import yaml

FILES = {"data-model": ("data-model-authors.yml", "authors.yml"), "storage-format": ("authors.yml",)}
DESCRIPTIONS = {
    "data-model": "The SpatialData abstract data model: images, labels, points, shapes and tables, "
    "their coordinate systems and transformations, and how tables annotate spatial elements.",
    "storage-format": "The SpatialData storage format: how a SpatialData dataset is stored as a Zarr "
    "hierarchy with embedded Parquet files, reusing OME-NGFF for raster data.",
}
PUBLISHER = "[scverse](https://scverse.org)"
H1 = re.compile(r"^# .+$", re.M)


def _load(srcdir, docname):
    for name in FILES[docname]:
        path = Path(srcdir) / name
        if path.is_file():
            return yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    return {}


def _icon(src, alt, cls, url):
    return f"[![{alt}](/_static/img/{src}){{.{cls}}}]({url})"


def _name(p):
    """The name, followed by the ORCID iD icon (as journals show it, per ORCID's brand guidelines)
    and the GitHub icon, each linked."""
    name = p["name"]
    if p.get("orcid"):
        name += " " + _icon("orcid.svg", "ORCID iD", "person-icon", f"https://orcid.org/{p['orcid']}")
    if p.get("github"):
        name += " " + _icon("github.svg", "GitHub", "person-icon .github-icon", f"https://github.com/{p['github']}")
    return name


def _entry(name, contributions):
    text = " ".join(str(contributions or "").split()).rstrip(".")
    return f"**{name}**: {text}." if text else f"**{name}**."


def _group_name(g):
    return f"[{g['name']}]({g['url']})" if g.get("url") else g["name"]


def add_credits(app, docname, source):
    if docname not in FILES:
        return
    data = _load(app.srcdir, docname)
    people, groups = data.get("people") or [], data.get("groups") or []
    if not people and not groups:
        return
    label = f"{docname}-contributors"
    shown = set()

    def first(p):  # icons only at a person's first mention under the title
        if p["name"] in shown:
            return p["name"]
        shown.add(p["name"])
        return _name(p)

    editors = [p for p in people if p.get("role") == "editor"]
    authors = [p for p in people if p.get("role") in ("editor", "author")]
    designers = [p for p in people if p.get("basis") == "original design"]
    lines = []
    if editors:
        lines.append(
            "**Editors:** " + ", ".join(p["name"] if len(authors) > len(editors) else first(p) for p in editors)
        )
    if len(authors) > len(editors):  # authors besides the editors: the authors of the citation
        lines.append("**Authors:** " + ", ".join(first(p) for p in authors))
    if any(p.get("role") not in ("editor", "author") for p in designers):  # once all are authors, no line
        ref = data.get("original_design") or {}
        cite = f" ([{ref['citation']}]({ref['url']}))" if ref.get("citation") and ref.get("url") else ""
        lines.append("**Original design:** " + ", ".join(first(p) for p in designers) + cite)
    if lines:
        lines.append(
            f"Published by {PUBLISHER}; developed by the SpatialData community, see "
            f"{{ref}}`contributors and acknowledgements <{label}>`."
        )
        byline = "\n\n:::{container} spec-authors\n" + "\\\n".join(lines) + "\n:::\n"
        source[0] = H1.sub(lambda m: m.group(0) + byline, source[0], count=1)
    spec = [
        _entry(_name(p), p.get("contributions")) for p in people if p.get("part", "specification") == "specification"
    ]
    origins = [_entry(_name(p), p.get("contributions")) for p in people if p.get("part") == "origins"]
    origins += [_entry(_group_name(g), g.get("contributions")) for g in groups]
    section = f"\n\n({label})=\n## Contributors and acknowledgements\n"
    if spec:
        section += "\n**Contributors to this specification.** " + " ".join(spec) + "\n"
    if origins:
        section += "\n**Origins and prior work.** " + " ".join(origins) + "\n"
    source[0] = source[0].rstrip() + section  # compact paragraphs; custom.css sets the sizes
    if docname in DESCRIPTIONS and not source[0].startswith("---"):
        d = DESCRIPTIONS[docname]
        source[0] = f'---\nog:description: "{d}"\nmyst:\n  html_meta:\n    description: "{d}"\n---\n' + source[0]


def setup(app):
    app.connect("source-read", lambda app, docname, source: add_credits(app, docname, source))
    return {"parallel_read_safe": True, "parallel_write_safe": True}
