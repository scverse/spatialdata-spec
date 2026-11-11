"""Credit the people of a specification on its page, from the authors.yml of its branch.

Each spec branch (data-model, storage-format) keeps an authors.yml: people with a role (author or
contributor) and a description of their contributions. For the pages data-model and storage-format,
this adds, when the file exists:

- under the title, a byline with the authors (role: author, in file order), followed by "with
  contributions from others", linking to the acknowledgements;
- at the end of the page, an Acknowledgements section listing everyone with their contributions in one compact paragraph,
  then the groups of authors.yml (e.g. the SpatialData paper, the package's code contributors),
  each linked.

A storage format build overlays the data model branch (build.py), whose authors.yml arrives as
data-model-authors.yml so that it does not replace the storage format's own. Versions without an
authors.yml render as before.
"""

import re
from pathlib import Path

import yaml

FILES = {"data-model": ("data-model-authors.yml", "authors.yml"), "storage-format": ("authors.yml",)}
H1 = re.compile(r"^# .+$", re.M)


def _load(srcdir, docname):
    for name in FILES[docname]:
        path = Path(srcdir) / name
        if path.is_file():
            data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
            return data.get("people") or [], data.get("groups") or []
    return [], []


def _name(p):
    """The name, linked to the person's GitHub profile, followed by the ORCID iD icon linked to their
    ORCID record (as journals show it, per ORCID's brand guidelines)."""
    name = f"[{p['name']}](https://github.com/{p['github']})" if p.get("github") else p["name"]
    if p.get("orcid"):
        name += f" [![ORCID iD](/_static/img/orcid.svg){{.orcid-id}}](https://orcid.org/{p['orcid']})"
    return name


def _entry(name, contributions):
    text = " ".join(str(contributions or "").split()).rstrip(".")
    return f"**{name}**: {text}." if text else f"**{name}**."


def _person(p):
    return _entry(_name(p), p.get("contributions"))


def _group(g):
    return _entry(f"[{g['name']}]({g['url']})" if g.get("url") else g["name"], g.get("contributions"))


def add_credits(app, docname, source):
    if docname not in FILES:
        return
    people, groups = _load(app.srcdir, docname)
    if not people and not groups:
        return
    label = f"{docname}-acknowledgements"
    authors = [_name(p) for p in people if p.get("role") == "author"]
    others = [p for p in people if p.get("role") != "author"] + groups
    if authors:
        tail = f", with {{ref}}`contributions from others <{label}>`" if others else ""
        byline = f"\n\n:::{{container}} spec-authors\n{', '.join(authors)}{tail}\n:::\n"
        source[0] = H1.sub(lambda m: m.group(0) + byline, source[0], count=1)
    entries = [*(_person(p) for p in people), *(_group(g) for g in groups)]
    source[0] = (  # one compact paragraph; custom.css sets a smaller heading and text
        source[0].rstrip()
        + f"\n\n({label})=\n## Acknowledgements\n\n"
        + "The people who contributed to this specification and its design: "
        + " ".join(entries)
        + "\n"
    )


def setup(app):
    app.connect("source-read", lambda app, docname, source: add_credits(app, docname, source))
    return {"parallel_read_safe": True, "parallel_write_safe": True}
