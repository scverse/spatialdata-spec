// A page-wide implementation switch in the main navigation.
//
// The specification page shows the data model with implementation blocks:
// sphinx-design tab sets in the sync group "impl". Instead of a tab row above
// every block, the navigation entry of that page gets one sub-entry per view.
// Choosing one selects the (hidden) tabs, which syncs all blocks, the URL and
// the "¶" links (see tab-permalinks.js). Each block is labelled with its
// implementation. Without JavaScript, the tab rows stay visible.

(() => {
    "use strict";

    const GROUP = "impl";
    const VIEWS = [
        ["model", "Data model"],
        ["storage", "Storage format"],
        ["python", "Python"],
    ];

    // hide the tab rows only when this script runs (see custom.css)
    document.documentElement.classList.add("view-switch");

    function implLabels() {
        return [
            ...document.querySelectorAll(
                `.sd-tab-label[data-sync-group="${GROUP}"]`,
            ),
        ];
    }

    /** The view shown on this page: stored choice, URL, or default tab. */
    function currentView() {
        try {
            const key = `sphinx-design-tab-id-${GROUP}`;
            const stored = window.sessionStorage.getItem(key);
            if (stored) return stored;
        } catch {
            // storage unavailable (privacy mode)
        }
        const param = new URLSearchParams(window.location.search).get(GROUP);
        if (param) return param;
        const label = implLabels().find(
            (l) => l.previousElementSibling?.checked,
        );
        return label?.getAttribute("data-sync-id") ?? null;
    }

    /** Select a view on this page: check every tab of that id. */
    function select(id) {
        const labels = implLabels().filter(
            (l) => l.getAttribute("data-sync-id") === id,
        );
        if (!labels.length) return;
        for (const label of labels) label.previousElementSibling.checked = true;
        // the click syncs sphinx-design's stored choice and updates the URL
        labels[0].click();
        markActive();
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

    function markActive() {
        const view = currentView();
        for (const link of document.querySelectorAll(".view-switch-nav a")) {
            const active = link.dataset.view === view;
            link.classList.toggle("current", active);
            link.parentElement.classList.toggle("current", active);
            if (active) link.setAttribute("aria-current", "true");
            else link.removeAttribute("aria-current");
        }
    }

    function addNavigation(entry, onPage) {
        const page = new URL(entry.getAttribute("href"), window.location.href);
        const list = document.createElement("ul");
        list.className = "view-switch-nav";
        for (const [id, title] of VIEWS) {
            const url = new URL(onPage ? window.location.href : page.href);
            url.searchParams.set(GROUP, id);
            url.hash = "";
            const link = document.createElement("a");
            link.className = "reference internal";
            link.dataset.view = id;
            link.href = url.href;
            link.textContent = title;
            if (onPage) {
                link.addEventListener("click", (event) => {
                    event.preventDefault();
                    select(id);
                });
            }
            const item = document.createElement("li");
            item.className = "toctree-l2";
            item.appendChild(link);
            list.appendChild(item);
        }
        entry.parentElement.appendChild(list);
    }

    /** Label each implementation block with the name of its tab. */
    function labelBlocks() {
        for (const label of implLabels()) {
            const content = label.nextElementSibling;
            if (!content?.classList.contains("sd-tab-content")) continue;
            content.classList.add("impl-block");
            content.dataset.implLabel = label.textContent.trim();
        }
    }

    document.addEventListener("DOMContentLoaded", () => {
        const onPage = implLabels().length > 0;
        const entry = navEntry(onPage);
        if (entry) addNavigation(entry, onPage);
        if (!onPage) return;
        labelBlocks();
        // keep the navigation in step with tabs opened elsewhere (permalinks)
        for (const label of implLabels()) {
            label.addEventListener("click", () => setTimeout(markActive));
        }
    });
    // after sphinx-design has restored the selection (on DOMContentLoaded)
    window.addEventListener("load", markActive);
})();
