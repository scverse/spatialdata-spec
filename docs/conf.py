# Configuration file for the Sphinx documentation builder.
# https://www.sphinx-doc.org/page/usage/configuration.html

import shutil
from datetime import datetime
from importlib.metadata import metadata

from sphinxcontrib import katex

# -- Project information -----------------------------------------------------

info = metadata("spatialdata-spec")
project = "SpatialData specification"
author = info["Author"]
copyright = f"{datetime.now():%Y}, scverse. Specification text CC-BY-4.0, everything else BSD-3-Clause"
version = info["Version"]
release = info["Version"]
urls = dict(pu.split(", ") for pu in info.get_all("Project-URL"))
repository_url = urls["Source"]

# Version of the on-disk format that this build of the specification describes.
# Keep in sync with spec/on-disk/versions.md.
ondisk_format_version = "0.2"

bibtex_bibfiles = ["references.bib"]
templates_path = ["_templates"]
nitpicky = True  # Warn about broken links
needs_sphinx = "8.0"

html_context = {
    "github_user": "scverse",
    "github_repo": "spatialdata-spec",
    "github_version": "main",
    "doc_path": "docs",
    "default_mode": "light",
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

html_theme = "pydata_sphinx_theme"
html_static_path = ["_static"]
html_css_files = ["css/custom.css"]
html_title = "SpatialData specification"
html_short_title = "SpatialData spec"
html_show_sourcelink = False
html_copy_source = False

html_theme_options = {
    "header_links_before_dropdown": 3,
    "navbar_start": ["navbar-logo"],
    "navbar_center": ["navbar-nav"],
    "navbar_end": ["theme-switcher", "navbar-icon-links"],
    "navbar_persistent": ["search-button"],
    "secondary_sidebar_items": ["page-toc", "edit-this-page"],
    "show_nav_level": 1,
    "navigation_depth": 3,
    "show_toc_level": 2,
    "use_edit_page_button": True,
    "footer_start": ["copyright"],
    "footer_end": ["sphinx-version"],
    "announcement": (
        "Draft under development. Content reflects the format written by spatialdata 0.6 to 0.8. "
        f'<a href="{repository_url}/issues">Feedback welcome</a>.'
    ),
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
        "text": "SpatialData specification",
    },
    "pygments_light_style": "friendly",
    "pygments_dark_style": "monokai",
}

katex_prerender = shutil.which(katex.NODEJS_BINARY) is not None

ogp_site_url = "https://spatialdata-spec.readthedocs.io/"
ogp_description_length = 200

nitpick_ignore = []
