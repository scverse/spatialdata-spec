"""The main navigation of every page, written when the page is built, so that it works without JavaScript.

Below the entry of the abstract data model: its versions (1.0, ...); below the entry of the storage
format: its versions (0.4, ..., 0.1). Below them, each part links to its implementations and its
version history, which exist once, at the root of the site, and show the latest state for every
version; so do the pages of the project (RFCs, contributing guide).

A storage format page selects its storage format version and the data model version that it
encodes. A data model page (data-model/<version>/) selects only the data model version. The root
of the site selects none, and its entries of the two parts lead to the preferred version. Every
deploy builds every version, so each page lists all versions published at that time.
"""

import posixpath

from bs4 import BeautifulSoup

# the pages below each part that exist once, at the root: (page, title)
LATEST = {
    "data-model": [("implementations", "Implementations"), ("data-model-versions", "Version history")],
    "storage-format": [
        ("storage-format-implementations", "Implementations"),
        ("storage-format-versions", "Version history"),
    ],
}
# pages of the project, which exist once, at the root: (page, title); every other build has no
# toctree entry for them (build.py), so their entries are added here
PROJECT = [("rfcs", "RFCs"), ("contributing", "Contributing")]


class Build:
    """What the navigation needs to know about the build: see conf.py."""

    def __init__(self, versions, site_url, data_model, storage_format, latest):
        self.models = versions["data_models"]
        self.formats = [f for m in self.models for f in m["storage_formats"]]
        self.site_url = site_url
        self.data_model = data_model
        self.storage_format = storage_format
        self.latest = latest

    @property
    def preferred(self):
        return next((f for f in self.formats if f.get("preferred")), None)


def _page_of(href, pagename):
    """The page a relative link of the page pagename points to, or None for other links."""
    if href == "#":
        return pagename
    if "://" in href or not href.split("#")[0].endswith(".html"):
        return None
    path = posixpath.normpath(posixpath.join(posixpath.dirname(pagename), href.split("#")[0]))
    return path.removesuffix(".html")


def _entry(soup, page, pagename):
    for a in soup.select("a.reference.internal"):
        if _page_of(a.get("href", ""), pagename) == page:
            return a
    return None


def _children(soup, link):
    """The list of pages below a navigation entry, created if it has none."""
    li = link.parent
    ul = li.select_one(":scope > details > ul") or li.select_one(":scope > ul")
    if ul is None:
        ul = soup.new_tag("ul")
        li.append(ul)
    return ul


def _mark_current(link):
    link["class"] = list(dict.fromkeys([*link.get("class", []), "current"]))
    for li in link.find_parents("li"):
        li["class"] = list(dict.fromkeys([*li.get("class", []), "current", "active"]))
        details = li.select_one(":scope > details")
        if details is not None:
            details["open"] = "open"


def _versions_row(soup, items):
    row = soup.new_tag("li", attrs={"class": "toctree-l2 spec-versions-row"})
    ul = soup.new_tag("ul", attrs={"class": "spec-versions"})
    for text, url, selected in items:
        li = soup.new_tag("li", attrs={"class": "selected"} if selected else {})
        a = soup.new_tag("a", href=url)
        if selected:
            a["aria-current"] = "true"
        a.string = text
        li.append(a)
        ul.append(li)
    row.append(ul)
    return row


def _part(soup, build, link, part, items, pagename):
    """Below a part: its versions, then the rest, then its pages at the root."""
    ul = _children(soup, link)
    for page, title in LATEST[part]:
        a = _entry(soup, page, pagename)
        if a is None or a.parent.parent is not ul:
            li = soup.new_tag("li", attrs={"class": "toctree-l2"})
            a = soup.new_tag("a", attrs={"class": "reference internal"})
            a.string = title
            li.append(a)
        if not (build.latest and pagename == page):
            a["href"] = f"{build.site_url}{page}.html"
        ul.append(a.parent)  # in the order of LATEST
        if build.latest and pagename == page:
            a["href"] = "#"
            _mark_current(a)  # an orphan page (implementations) is not marked by Sphinx
    ul.insert(0, _versions_row(soup, items))


def navigation(html, pagename, build):
    """The sidebar navigation html of the page pagename, with the versions."""
    soup = BeautifulSoup(html, "html.parser")
    preferred = build.preferred
    model = _entry(soup, "data-model", pagename)
    if model is not None:
        _part(
            soup,
            build,
            model,
            "data-model",
            [(m["version"], f"{m['url']}data-model.html", m["version"] == build.data_model) for m in build.models],
            pagename,
        )
        if build.latest:
            own = next((m for m in build.models if preferred in m["storage_formats"]), None)
            if own and model["href"] != "#":
                model["href"] = f"{own['url']}data-model.html"
    fmt = _entry(soup, "storage-format", pagename)
    if fmt is not None:
        _part(
            soup,
            build,
            fmt,
            "storage-format",
            [
                (
                    f["version"],
                    f"{f['url']}storage-format.html",
                    bool(build.storage_format) and f["version"] == build.storage_format,
                )
                for f in build.formats
            ],
            pagename,
        )
        if not build.storage_format and fmt["href"] != "#":
            # on a data model page or at the root: the newest storage format of this data model,
            # or the preferred one
            own = next((m for m in build.models if m["version"] == build.data_model), None)
            target = next((f for f in own["storage_formats"] if not f.get("draft")), None) if own else None
            target = target or preferred
            if target:
                fmt["href"] = f"{target['url']}storage-format.html"
    # the list of RFCs is collapsed, except on the RFC pages
    rfcs = _entry(soup, "rfcs", pagename)
    if rfcs is not None and not (pagename == "rfcs" or pagename.startswith("rfcs/")):
        details = rfcs.parent.select_one(":scope > details")
        if details is not None and "open" in details.attrs:
            del details["open"]
    # the pages of the project exist once, at the root: the entries of every other build lead there
    if not build.latest and model is not None:
        for page, title in PROJECT:
            li = soup.new_tag("li", attrs={"class": "toctree-l1"})
            a = soup.new_tag("a", attrs={"class": "reference internal"}, href=f"{build.site_url}{page}.html")
            a.string = title
            li.append(a)
            model.parent.parent.append(li)
    return str(soup)
