// A page-wide implementation switch in the main navigation.
//
// The specification page shows the data model with implementation blocks:
// sphinx-design tab sets in the sync group "impl". Instead of a tab row above
// every block, the navigation entry of that page is replaced by one
// top-level entry per view, with sub-entries for the storage format versions
// (sync group "storage-version") and the in-memory formats (one "impl" tab
// per language). The draft of the next storage version shows the current
// version wherever it has no tab of its own, and marks its changes. The
// entries of the pages about the storage format
// (versions, NGFF compatibility, next version) move below its view.
// Choosing one selects the (hidden) tabs, which syncs all blocks, the URL and
// the "¶" links (see tab-permalinks.js). Each block is labelled with its
// implementation. Without JavaScript, the tab rows stay visible.

(() => {
    "use strict";

    const GROUP = "impl";
    const VERSION_GROUP = "storage-version";
    // the draft of the next version, and the version it starts from
    const DRAFT = "container-0.3";
    const BASE = "container-0.2";
    const SPEC = "Specification of the SpatialData abstract data model";
    const LANGUAGES = [
        ["python", "Python"],
        ["r", "R"],
        ["javascript", "JavaScript"],
    ];
    // tab: the "impl" tab an entry selects; sub: its sub-entries, as
    // [sync group, [[tab id, title], ...]]; pages: other pages of the site
    // (relative to spec/) whose navigation entries move below the entry
    const VIEWS = [
        { title: "Abstract data model", tab: "model" },
        {
            title: "& storage format",
            tab: "storage",
            sub: [
                VERSION_GROUP,
                [
                    [DRAFT, "container-format-0.3 (draft)"],
                    [BASE, "container-format-0.2"],
                    ["container-0.1", "container-format-0.1"],
                ],
            ],
            pages: [
                "storage-format/versions",
                "storage-format/ngff-compatibility",
                "storage-format/next",
            ],
        },
        {
            title: "& in-memory formats",
            tab: "python",
            sub: [GROUP, LANGUAGES],
            pages: ["in-memory/python-guide"],
        },
    ];

    // hide the tab rows only when this script runs (see custom.css)
    document.documentElement.classList.add("view-switch");

    // The URL alone decides the view and version: a link without them opens
    // the defaults, not a choice made earlier in this browser session.
    // Choosing a view writes it into the URL (see tab-permalinks.js), so
    // reloading and sharing keep it. This runs before sphinx-design restores
    // the stored choice (on DOMContentLoaded).
    for (const group of [GROUP, VERSION_GROUP]) {
        if (new URLSearchParams(window.location.search).has(group)) continue;
        try {
            window.sessionStorage.removeItem(`sphinx-design-tab-id-${group}`);
        } catch {
            // storage unavailable (privacy mode): nothing is restored anyway
        }
    }

    function labels(group, id) {
        const sync = id ? `[data-sync-id="${id}"]` : "";
        return [
            ...document.querySelectorAll(
                `.sd-tab-label[data-sync-group="${group}"]${sync}`,
            ),
        ];
    }

    /** The tab shown in a group: stored choice, URL, or default tab. */
    function current(group) {
        try {
            const key = `sphinx-design-tab-id-${group}`;
            const stored = window.sessionStorage.getItem(key);
            if (stored) return stored;
        } catch {
            // storage unavailable (privacy mode)
        }
        const param = new URLSearchParams(window.location.search).get(group);
        if (param) return param;
        const label = labels(group).find(
            (l) => l.previousElementSibling?.checked,
        );
        return label?.getAttribute("data-sync-id") ?? null;
    }

    /** Select a tab on this page: check every tab of that id in the group. */
    function select(group, id) {
        const found = labels(group, id);
        if (!found.length) return;
        for (const label of found) label.previousElementSibling.checked = true;
        // the click syncs sphinx-design's stored choice and updates the URL
        found[0].click();
    }

    /**
     * While the draft is selected, show the base version in every version
     * tab set that has no draft tab (the draft inherits that text).
     */
    function showDraftFallback() {
        if (current(VERSION_GROUP) !== DRAFT) return;
        for (const set of document.querySelectorAll(".sd-tab-set")) {
            const own = [...set.children].filter((el) =>
                el.matches(`.sd-tab-label[data-sync-group="${VERSION_GROUP}"]`),
            );
            if (!own.length) continue;
            if (own.some((l) => l.getAttribute("data-sync-id") === DRAFT))
                continue;
            const base = own.find(
                (l) => l.getAttribute("data-sync-id") === BASE,
            );
            if (base) base.previousElementSibling.checked = true;
        }
    }

    /**
     * The navigation entry of the specification page, if present: the link
     * to the current page when it has implementation blocks, else the link
     * to spec/specification.html.
     */
    function navEntry(onPage) {
        const links = document.querySelectorAll(
            ".bd-docs-nav a.reference.internal",
        );
        for (const a of links) {
            const href = a.getAttribute("href");
            if (onPage && href === "#" && a.classList.contains("current"))
                return a;
            const url = new URL(href, window.location.href);
            if (url.pathname.endsWith("/spec/specification.html")) return a;
        }
        return null;
    }

    /** The navigation item of the page spec/<path>.html, if present. */
    function navItem(path) {
        const links = document.querySelectorAll(
            ".bd-docs-nav li.toctree-l1 > a.reference.internal",
        );
        for (const a of links) {
            const href = a.getAttribute("href");
            // the current page links to "#"
            const url = new URL(href === "#" ? "" : href, window.location.href);
            if (url.pathname.endsWith(`/spec/${path}.html`))
                return a.parentElement;
        }
        return null;
    }

    function headingFor(view) {
        if (view === "model") return SPEC;
        if (view === "storage") return `${SPEC} and storage format`;
        const language = LANGUAGES.find(([id]) => id === view)?.[1];
        return language ? `${SPEC} and ${language} in-memory format` : null;
    }

    /** Name the page after the view: heading and document title. */
    function setHeading(view) {
        const heading = headingFor(view);
        if (!heading) return;
        // the article heading, and the copy the theme prints
        for (const h1 of document.querySelectorAll(
            "article h1, #jb-print-docs-body h1",
        )) {
            const text = h1.firstChild;
            if (text?.nodeType !== Node.TEXT_NODE) continue;
            const old = text.nodeValue.trim();
            text.nodeValue = heading;
            document.title = document.title.replace(old, heading);
        }
    }

    /** Whether a navigation link shows the current selection. */
    function isActive(link, view) {
        const { group, tab, parentTab } = link.dataset;
        if (group === VERSION_GROUP)
            return view === parentTab && current(VERSION_GROUP) === tab;
        if (link.dataset.languages)
            return LANGUAGES.some(([id]) => id === view);
        return view === tab;
    }

    function markActive() {
        // other pages highlight their own entry
        if (!labels(GROUP).length) return;
        const view = current(GROUP);
        setHeading(view);
        showDraftFallback();
        for (const link of document.querySelectorAll(
            ".view-switch-entry > a",
        )) {
            const active = isActive(link, view);
            link.classList.toggle("current", active);
            link.parentElement.classList.toggle("current", active);
            if (active) link.setAttribute("aria-current", "true");
            else link.removeAttribute("aria-current");
        }
    }

    /** A navigation item that selects `tab` of `group` (and `view`). */
    function item(page, onPage, level, title, view, group, tab) {
        const url = new URL(onPage ? window.location.href : page.href);
        url.searchParams.set(GROUP, view);
        if (group !== GROUP) url.searchParams.set(group, tab);
        url.hash = "";
        const link = document.createElement("a");
        link.className = "reference internal";
        Object.assign(link.dataset, { group, tab, parentTab: view });
        link.href = url.href;
        link.textContent = title;
        if (onPage) {
            link.addEventListener("click", (event) => {
                event.preventDefault();
                select(GROUP, view);
                // the draft inherits the base version where it has no tab
                if (tab === DRAFT) select(group, BASE);
                if (group !== GROUP) select(group, tab);
                markActive();
            });
        }
        const li = document.createElement("li");
        li.className = `toctree-l${level} view-switch-entry`;
        li.appendChild(link);
        return li;
    }

    function addNavigation(entry, onPage) {
        const page = new URL(entry.getAttribute("href"), window.location.href);
        for (const view of VIEWS) {
            const li = item(
                page,
                onPage,
                1,
                view.title,
                view.tab,
                GROUP,
                view.tab,
            );
            const list = document.createElement("ul");
            list.className = "view-switch-sub";
            if (view.sub) {
                const [group, entries] = view.sub;
                if (group === GROUP) li.firstChild.dataset.languages = "true";
                for (const [tab, title] of entries) {
                    const parent = group === GROUP ? tab : view.tab;
                    list.appendChild(
                        item(page, onPage, 2, title, parent, group, tab),
                    );
                }
            }
            for (const path of view.pages ?? []) {
                const moved = navItem(path);
                if (!moved) continue;
                moved.classList.replace("toctree-l1", "toctree-l2");
                list.appendChild(moved);
            }
            if (list.children.length) li.appendChild(list);
            entry.parentElement.before(li);
        }
        entry.parentElement.remove();
    }

    /**
     * Label each implementation block with the name of its tab, and mark the
     * passages the draft changes.
     */
    function labelBlocks() {
        for (const label of labels(GROUP)) {
            const content = label.nextElementSibling;
            if (!content?.classList.contains("sd-tab-content")) continue;
            content.classList.add("impl-block");
            content.dataset.implLabel = label.textContent.trim();
        }
        for (const label of labels(VERSION_GROUP, DRAFT)) {
            label.nextElementSibling?.classList.add("draft-change");
        }
    }

    document.addEventListener("DOMContentLoaded", () => {
        const onPage = labels(GROUP).length > 0;
        const entry = navEntry(onPage);
        if (entry) addNavigation(entry, onPage);
        if (!onPage) return;
        labelBlocks();
        // keep the navigation in step with tabs opened elsewhere (permalinks)
        for (const label of document.querySelectorAll(".sd-tab-label")) {
            label.addEventListener("click", () => setTimeout(markActive));
        }
    });
    // after sphinx-design has restored the selection (on DOMContentLoaded)
    window.addEventListener("load", markActive);
})();
