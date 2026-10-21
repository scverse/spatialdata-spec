# Configuration file for the Sphinx documentation builder.
# https://www.sphinx-doc.org/page/usage/configuration.html

import dataclasses
import os
import shutil
from datetime import datetime
from importlib.metadata import metadata

from docutils import nodes
from sphinxcontrib.bibtex.plugin import register_plugin
from sphinxcontrib.bibtex.style.referencing import BracketStyle
from sphinxcontrib.bibtex.style.referencing.author_year import AuthorYearReferenceStyle

from sphinxcontrib import katex

# -- Project information -----------------------------------------------------

info = metadata("spatialdata-spec")
project = "SpatialData specifications"
author = info["Author"]
copyright = f"{datetime.now():%Y}, scverse. Specification text CC-BY-4.0, everything else BSD-3-Clause"
version = info["Version"]
release = info["Version"]
urls = dict(pu.split(", ") for pu in info.get_all("Project-URL"))
repository_url = urls["Source"]

# Version of the storage format that this build of the specification describes.
# Keep in sync with spec/storage-format/versions.md.
ondisk_format_version = "0.2"

# -- Read the Docs awareness --------------------------------------------------
# Read the Docs exposes the build context through environment variables; see
# https://docs.readthedocs.io/en/stable/reference/environment-variables.html.
# Nothing here is required for local or GitHub Actions builds.
on_rtd = os.environ.get("READTHEDOCS") == "True"
rtd_version = os.environ.get("READTHEDOCS_VERSION", "")
rtd_version_type = os.environ.get("READTHEDOCS_VERSION_TYPE", "")  # "branch", "tag", "external" (pull request)
rtd_canonical_url = os.environ.get("READTHEDOCS_CANONICAL_URL", "")
is_pr_preview = on_rtd and rtd_version_type == "external"

bibtex_bibfiles = ["references.bib"]
bibtex_reference_style = "author_year_round"  # registered at the end of this file
templates_path = ["_templates"]
nitpicky = True  # Warn about broken links
needs_sphinx = "8.0"

html_context = {
    "github_user": "scverse",
    "github_repo": "spatialdata-spec",
    "github_version": "main",
    "doc_path": "docs",
    "default_mode": "light",
    "READTHEDOCS": on_rtd,
}

# -- General configuration ---------------------------------------------------

extensions = [
    "myst_parser",
    "sphinx_copybutton",
    "sphinx.ext.intersphinx",
    "sphinxcontrib.bibtex",
    "sphinxcontrib.katex",
    "sphinx_design",
    "sphinxext.opengraph",
    "scverse_misc.sphinx_ext",
]

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
myst_substitutions = {
    "ondisk_version": ondisk_format_version,
}
myst_url_schemes = ("http", "https", "mailto")

intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
    "scanpy": ("https://scanpy.scverse.org/en/stable/", None),
}

exclude_patterns = ["spec/README.md", "_build", "Thumbs.db", ".DS_Store", "**.ipynb_checkpoints"]
suppress_warnings = [
    "myst.header",  # chapters intentionally start from h1 in every file
    "misc.highlighting_failure",  # JSON examples are deliberately abbreviated with "..."
]

# -- Options for HTML output -------------------------------------------------

html_theme = "sphinx_book_theme"
html_static_path = ["_static"]
html_css_files = ["css/custom.css"]
html_js_files = ["js/tab-permalinks.js", "js/view-switch.js", "js/footnote-popups.js"]
html_title = "SpatialData specifications"
html_favicon = "_static/img/spatialdata_icon.png"
html_short_title = "SpatialData spec"
html_show_sourcelink = False
html_copy_source = False
# Canonical URL of the published site; Read the Docs provides it per version and per pull request.
html_baseurl = rtd_canonical_url or "https://spatialdata-spec.readthedocs.io/en/latest/"

if is_pr_preview:
    announcement = (
        f"Preview build of pull request #{rtd_version}. Not the published specification. "
        f'<a href="{repository_url}/pull/{rtd_version}">Discussion</a>.'
    )
else:
    announcement = f'Draft under development. <a href="{repository_url}/issues">Report a problem / give feedback</a>.'

# no search box: the site is small, and the browser finds text on the one specification page
html_sidebars = {"**": ["navbar-logo.html", "icon-links.html", "sbt-sidebar-nav.html"]}
html_theme_options = {
    "navbar_persistent": [],
    "repository_url": repository_url,
    "repository_branch": "main",
    "path_to_docs": "docs/",
    "use_repository_button": True,
    "use_edit_page_button": True,
    "use_issues_button": True,
    "navigation_with_keys": False,
    "show_navbar_depth": 1,
    "max_navbar_depth": 3,
    "show_toc_level": 2,
    "footer_start": ["copyright"],
    "footer_end": ["sphinx-version"],
    "announcement": announcement,
    "icon_links": [
        {
            "name": "GitHub",
            "url": repository_url,
            "icon": "fa-brands fa-github",
        },
        {
            "name": "spatialdata",
            "url": "https://spatialdata.scverse.org",
            "icon": "fa-solid fa-book",
        },
    ],
    "logo": {
        "text": "SpatialData specifications",
        "image_light": "_static/img/spatialdata_icon.png",
        "image_dark": "_static/img/spatialdata_icon.png",
    },
    "pygments_light_style": "friendly",
    "pygments_dark_style": "monokai",
}

katex_prerender = shutil.which(katex.NODEJS_BINARY) is not None

ogp_site_url = html_baseurl
ogp_description_length = 200

nitpick_ignore = []


def _footnotes_into_notes(app, doctree, docname):
    """Move the footnotes of a page into its "Notes" section, if it has one.

    MyST places footnotes after all sections; on the specification page they
    belong in the last section, "Notes" (hidden on screen by
    js/footnote-popups.js, kept in print).
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


def setup(app):
    # after the post-transforms, which is where MyST adds the footnotes
    app.connect("doctree-resolved", _footnotes_into_notes)


@dataclasses.dataclass
class _AuthorYearRound(AuthorYearReferenceStyle):
    """Author-year citations in round brackets: (Marconato et al., 2025)."""

    bracket_parenthetical: BracketStyle = dataclasses.field(default_factory=lambda: BracketStyle(left="(", right=")"))
    bracket_textual: BracketStyle = dataclasses.field(default_factory=lambda: BracketStyle(left="(", right=")"))


register_plugin("sphinxcontrib.bibtex.style.referencing", "author_year_round", _AuthorYearRound)
