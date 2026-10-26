"""Mark the data model text that the storage format page includes.

storage-format.md includes each section of data-model.md between its comment markers
(`% begin spec-<name>` / `% end spec-<name>`). When data-model.md is read for such an include, this
wraps the text between each pair of markers in a container with the class `data-model-text`, which
custom.css shows with a side rule and a "Data model" label. The markers and the pages are unchanged;
the data model page itself is not affected. The shared introduction (spec-intro) is not marked.
"""

import re
from pathlib import Path

FENCE = ":" * 12  # longer than any colon fence inside the included text
UNMARKED = {"spec-intro"}


def _wrap(match):
    name, body = match.group(1), match.group(2)
    if name in UNMARKED:
        return match.group(0)
    return f"% begin {name}\n\n{FENCE}{{container}} data-model-text\n{body}\n{FENCE}\n\n% end {name}"


def mark_data_model(app, relative_path, parent_docname, content):
    if Path(relative_path).name != "data-model.md":
        return
    content[0] = re.sub(r"^% begin (\S+)[ \t]*\n(.*?)^% end \1[ \t]*$", _wrap, content[0], flags=re.S | re.M)


def setup(app):
    app.connect("include-read", mark_data_model)
    return {"parallel_read_safe": True, "parallel_write_safe": True}
