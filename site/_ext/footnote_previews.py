"""Footnotes as previews next to their references, without JavaScript.

Each footnote reference gets a copy of its footnote's text beside it, which custom.css shows on
hover or keyboard focus. On screen the previews replace the list of footnotes; printing hides them
and shows the list, at the end of the page. The source stays ordinary MyST footnotes.
"""

from docutils import nodes


def _preview(footnote):
    """The text of a footnote as inline content: its paragraphs, without the label, joined by spaces."""
    preview = nodes.inline(classes=["footnote-preview"], role="note")
    for child in footnote.children:
        if isinstance(child, nodes.label):
            continue
        if isinstance(child, nodes.paragraph):
            if len(preview):
                preview += nodes.Text(" ")
            preview.extend(c.deepcopy() for c in child.children)  # the subtree only, not its parents
        else:
            preview += nodes.inline("", child.astext())
    for node in preview.findall(nodes.Element):
        node["ids"] = []  # the anchors stay with the footnote itself
    return preview


def add_previews(app, doctree, docname):
    footnotes = {id_: f for f in doctree.findall(nodes.footnote) for id_ in f["ids"]}
    for ref in list(doctree.findall(nodes.footnote_reference)):
        footnote = footnotes.get(ref.get("refid"))
        if footnote is None:
            continue
        anchor = nodes.inline(classes=["footnote-anchor"])
        ref.replace_self(anchor)
        anchor["ids"] = []  # replace_self moves the reference's ids to its replacement
        anchor += ref
        anchor += _preview(footnote)
    # a section that holds only the footnotes ("Notes") is hidden on screen with them
    for section in doctree.findall(nodes.section):
        rest = [
            c
            for c in section.children
            if not isinstance(c, (nodes.title, nodes.footnote, nodes.transition, nodes.target, nodes.comment))
            and not (isinstance(c, nodes.compound) and not c.astext().strip())  # a hidden toctree
        ]
        if not rest and any(isinstance(c, nodes.footnote) for c in section.children):
            section["classes"].append("footnote-section")


def setup(app):
    # after conf.py has moved the footnotes into their section
    app.connect("doctree-resolved", add_previews, priority=600)
    return {"parallel_read_safe": True, "parallel_write_safe": True}
