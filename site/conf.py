# Configuration file for the Sphinx documentation builder.
# https://www.sphinx-doc.org/page/usage/configuration.html

import dataclasses
import json
import os
import sys
from datetime import datetime
from importlib.metadata import metadata

from docutils import nodes
from markupsafe import Markup
from sphinxcontrib.bibtex.plugin import register_plugin
from sphinxcontrib.bibtex.style.referencing import BracketStyle
from sphinxcontrib.bibtex.style.referencing.author_year import AuthorYearReferenceStyle


# -- Project information -----------------------------------------------------

info = metadata("spatialdata-spec")
project = "SpatialData specifications"
author = info["Author"]
copyright = f"{datetime.now():%Y}, scverse. Specification text CC-BY-4.0, everything else BSD-3-Clause"
version = info["Version"]
release = info["Version"]
urls = dict(pu.split(", ") for pu in info.get_all("Project-URL"))
repository_url = urls["Source"]

# -- Version being built --------------------------------------------------------
# build.py builds each version listed in versions.toml from its own branch or tag and sets these
# variables; a plain sphinx-build of one checkout gets the defaults.
spec_ref = os.environ.get("SPEC_REF", "main")  # branch or tag the content comes from
spec_path = os.environ.get("SPEC_PATH", "preview")  # directory of this version on the site
spec_data_model = os.environ.get("SPEC_DATA_MODEL", "")  # version of the abstract data model
spec_storage_format = os.environ.get("SPEC_STORAGE_FORMAT", "")  # storage format version
spec_latest = os.environ.get("SPEC_LATEST", "0") == "1"  # the root: the latest state, for every version
# all published versions, for the navigation (see build.py and _ext/static_nav.py)
spec_versions = json.loads(os.environ.get("SPEC_VERSIONS", '{"data_models": []}'))
spec_draft = os.environ.get("SPEC_DRAFT", "1") == "1"
spec_preview_pr = os.environ.get("SPEC_PREVIEW_PR", "")  # pull request number of a preview build
site_url = os.environ.get("SITE_URL", "https://spatialdata-spec.scverse.org/")
# directory of the pages in the repository: "docs" on older branches, the top level otherwise
spec_doc_path = os.environ.get("SPEC_DOC_PATH", "docs")
# branch or tag the text of the data model comes from (empty: the content's own)
spec_data_model_ref = os.environ.get("SPEC_DATA_MODEL_REF", "")
DATA_MODEL_PAGES = ("data-model", "data-model-versions")
SPEC_PAGES = (*DATA_MODEL_PAGES, "storage-format", "storage-format-versions", "storage-format-conformance")


def _editable(ref):
    """A tag keeps a version as first released: its pages are not edited, those of a branch are."""
    return not ref.startswith(("storage-format-", "data-model-"))


# Pages generated for main carry their few citations as links and no bibliography file.
bibtex_bibfiles = ["references.bib"]
has_bibliography = os.path.exists(bibtex_bibfiles[0])  # Sphinx runs this file in its directory
bibtex_reference_style = "author_year_round"  # registered at the end of this file
templates_path = ["_templates"]
nitpicky = True  # Warn about broken links
needs_sphinx = "8.0"

html_context = {
    "github_user": "scverse",
    "github_repo": "spatialdata-spec",
    "github_version": spec_ref,
    "doc_path": spec_doc_path,
    "spec_versions": spec_versions,
    "spec_data_model": spec_data_model,
    "spec_storage_format": spec_storage_format,
    "spec_site_url": site_url,
    "spec_latest": spec_latest,
    "default_mode": "light",
}

# -- General configuration ---------------------------------------------------

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "_ext"))

extensions = [
    "myst_parser",
    "sphinx_copybutton",
    "sphinx.ext.intersphinx",
    "sphinx_design",
    "sphinxext.opengraph",
    "scverse_misc.sphinx_ext",
    "footnote_previews",  # _ext/: footnotes shown at their references, without JavaScript
    "data_model_blocks",  # _ext/: data model text included in the storage format, marked
]
if has_bibliography:
    extensions.append("sphinxcontrib.bibtex")

default_role = "literal"
myst_heading_anchors = 4
myst_enable_extensions = [
    "attrs_inline",
    "colon_fence",
    "deflist",
    "dollarmath",
    "fieldlist",
    "html_image",
    "substitution",
    "tasklist",
]
myst_url_schemes = ("http", "https", "mailto")

intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
    "scanpy": ("https://scanpy.scverse.org/en/stable/", None),
}

exclude_patterns = [
    "README.md",
    ".github",
    "CHANGELOG.md",  # on the branch history-draft, not a page
    "LICENSE.md",
    "planning",  # notes on the branch history-draft, not pages
    "_main",  # output of tools/write_history.py --out
    "spec/README.md",
    "_build",
    "Thumbs.db",
    ".DS_Store",
    "**.ipynb_checkpoints",
]
suppress_warnings = [
    "myst.header",  # chapters intentionally start from h1 in every file
    "misc.highlighting_failure",  # JSON examples are deliberately abbreviated with "..."
]

# -- Options for HTML output -------------------------------------------------

html_theme = "sphinx_book_theme"
html_static_path = ["_static"]
html_css_files = ["css/custom.css"]
html_js_files = ["js/tab-permalinks.js"]  # an enhancement; the pages work without it
html_title = "SpatialData specifications"
html_favicon = "_static/img/spatialdata_icon.png"
html_short_title = "SpatialData spec"
html_show_sourcelink = False
html_copy_source = True  # the download button offers the Markdown source
# Canonical URL of this version on the published site.
html_baseurl = f"{site_url}{spec_path}/" if spec_path else site_url

if spec_preview_pr:
    announcement = (
        f"Preview build of pull request #{spec_preview_pr}. Not the published specification. "
        f'<a href="{repository_url}/pull/{spec_preview_pr}">Discussion</a>.'
    )
elif spec_draft:
    announcement = f'Draft under development. <a href="{repository_url}/issues">Report a problem / give feedback</a>.'
else:
    announcement = ""

# no search box: the site is small, and the browser finds text on the one specification page
html_sidebars = {"**": ["navbar-logo.html", "sbt-sidebar-nav.html"]}
html_theme_options = {
    "navbar_persistent": [],
    "repository_url": repository_url,
    "repository_branch": spec_ref,
    "path_to_docs": spec_doc_path,
    "use_repository_button": True,
    "use_edit_page_button": _editable(spec_ref),
    "use_issues_button": True,
    "navigation_with_keys": False,
    "show_navbar_depth": 2,  # the versions and version history below each part
    "max_navbar_depth": 3,
    "show_toc_level": 2,
    "footer_start": [],  # the content footer already holds the author and the copyright
    "footer_end": [],
    "announcement": announcement,
    "logo": {
        "text": "SpatialData specifications",
        "image_light": "_static/img/spatialdata_icon.png",
        "image_dark": "_static/img/spatialdata_icon.png",
    },
    "pygments_light_style": "friendly",
    "pygments_dark_style": "monokai",
}

ogp_site_url = html_baseurl
ogp_description_length = 200

nitpick_ignore = []


def _footnotes_into_notes(app, doctree, docname):
    """Move the footnotes of a page into its "Notes" section, if it has one.

    MyST places footnotes after all sections; they belong in the last section, "Notes", which is
    hidden on screen, where each footnote shows at its reference (_ext/footnote_previews.py), and
    kept in print.
    """
    notes = next((s for s in doctree.findall(nodes.section) if "notes" in s["ids"]), None)
    if notes is None:
        return
    for node in list(doctree.children):
        if isinstance(node, nodes.footnote):
            doctree.remove(node)
            notes.append(node)
        elif isinstance(node, nodes.transition):
            doctree.remove(node)  # the heading separates the notes


def _canonical_url(pagename):
    """The one URL of a page that several builds contain: the root holds the pages of the project
    and the version histories, data-model/<version>/ the data model, each storage format build its
    own pages. None for the build's own copy."""
    models = spec_versions["data_models"]
    formats = [f for m in models for f in m["storage_formats"]]
    if pagename == "data-model":
        model = spec_data_model or next(
            (m["version"] for m in models if any(f.get("preferred") for f in m["storage_formats"])), ""
        )
        url = next((m["url"] for m in models if m["version"] == model), None)
        return f"{url}data-model.html" if url else None
    if pagename in ("storage-format", "storage-format-conformance"):
        if spec_storage_format:
            return None
        own = next((m for m in models if m["version"] == spec_data_model), None)
        target = next((f for f in own["storage_formats"] if not f.get("draft")), None) if own else None
        target = target or next((f for f in formats if f.get("preferred")), None)
        return f"{target['url']}{pagename}.html" if target else None
    return None if spec_latest else f"{site_url}{pagename}.html"


import static_nav  # noqa: E402

_build = static_nav.Build(spec_versions, site_url, spec_data_model, spec_storage_format, spec_latest)


def _edit_button(context, pagename):
    """The theme's "Suggest edit" leads to the page on the branch of the content. Pages of the data
    model are edited on its own branch, pages of the site itself (branch site) and of a tag not at
    all."""
    if pagename in DATA_MODEL_PAGES and spec_data_model_ref:
        ref = spec_data_model_ref
    elif pagename in SPEC_PAGES:
        ref = spec_ref
    else:
        ref = None
    edit = f"/edit/{spec_ref}/"

    def keep(button):
        if edit not in button.get("url", ""):
            return True
        if ref is None or not _editable(ref):
            return False
        button["url"] = button["url"].replace(edit, f"/edit/{ref}/")
        return True

    def walk(buttons):
        for button in buttons:
            if "buttons" in button:
                button["buttons"] = [b for b in button["buttons"] if keep(b)]
                walk(button["buttons"])
        return [b for b in buttons if keep(b)]

    if "header_buttons" in context:
        context["header_buttons"] = walk(context["header_buttons"])


def _page_context(app, pagename, templatename, context, doctree):
    toctree = context.get("generate_toctree_html")
    if toctree is not None:

        def navigation(kind, *args, **kwargs):
            html = toctree(kind, *args, **kwargs)
            if kind != "sidebar":
                return html
            return Markup(static_nav.navigation(str(html), pagename, _build))  # html, not text

        context["generate_toctree_html"] = navigation
    _edit_button(context, pagename)
    if spec_path == "preview":  # a preview of a branch or pull request: not for search engines
        context["metatags"] = context.get("metatags", "") + '<meta name="robots" content="noindex">\n'
        return
    url = _canonical_url(pagename)
    if url:
        context["pageurl"] = url


def setup(app):
    # after the post-transforms, which is where MyST adds the footnotes
    app.connect("doctree-resolved", _footnotes_into_notes)
    app.connect("html-page-context", _page_context, priority=900)  # after the theme adds its functions


@dataclasses.dataclass
class _AuthorYearRound(AuthorYearReferenceStyle):
    """Author-year citations in round brackets: (Marconato et al., 2025)."""

    bracket_parenthetical: BracketStyle = dataclasses.field(default_factory=lambda: BracketStyle(left="(", right=")"))
    bracket_textual: BracketStyle = dataclasses.field(default_factory=lambda: BracketStyle(left="(", right=")"))


register_plugin("sphinxcontrib.bibtex.style.referencing", "author_year_round", _AuthorYearRound)
