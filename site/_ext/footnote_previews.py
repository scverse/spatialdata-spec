"""Footnotes as previews next to their references, without JavaScript.

Each footnote reference gets a copy of its footnote's text beside it, which custom.css shows on
hover or keyboard focus. On screen the previews replace the list of footnotes; printing hides them
and shows the list, at the end of the page. Footnotes referenced from a table instead show below
that table, as table notes, on screen and in print: a preview there would be clipped by the
table's scroll container. The source stays ordinary MyST footnotes.
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


def _table(node):
    """The table a node is in, or None."""
    while node is not None and not isinstance(node, nodes.table):
        node = node.parent
    return node


def add_previews(app, doctree, docname):
    footnotes = {id_: f for f in doctree.findall(nodes.footnote) for id_ in f["ids"]}
    for ref in list(doctree.findall(nodes.footnote_reference)):
        footnote = footnotes.get(ref.get("refid"))
        if footnote is None:
            continue
        table = _table(ref)
        if table is not None:
            # a preview would be clipped by the table's scroll container (wide tables scroll
            # sideways), so a footnote of a table shows below it, as a table note
            if "table-note" not in footnote["classes"]:
                footnote.parent.remove(footnote)
                table.parent.insert(table.parent.index(table) + 1, footnote)
                footnote["classes"].append("table-note")
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
        # ("Notes" may have lost all its footnotes to table notes)
        if not rest and (any(isinstance(c, nodes.footnote) for c in section.children) or "notes" in section["ids"]):
            section["classes"].append("footnote-section")


def setup(app):
    # after conf.py has moved the footnotes into their section
    app.connect("doctree-resolved", add_previews, priority=600)
    return {"parallel_read_safe": True, "parallel_write_safe": True}
