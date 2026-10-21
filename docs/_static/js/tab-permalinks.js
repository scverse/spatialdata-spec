// Permalinks into tabbed content (sphinx-design tab sets).
//
// sphinx-design already selects tabs from URL parameters
// (`?impl=storage&storage-version=container-0.1`). This script adds the two
// missing pieces:
// - a link to an anchor inside a hidden tab opens that tab (and every
//   enclosing tab) and scrolls to it;
// - rubrics inside tabs get a "¶" link that records the selected tab of every
//   synced group in the URL, so the link opens the page as the reader sees it;
// - selecting a tab updates the address bar the same way.

(() => {
    "use strict";

    /** Tab contents enclosing `el`, outermost first. */
    function enclosingTabs(el) {
        const tabs = [];
        for (let node = el.parentElement; node; node = node.parentElement) {
            if (node.classList.contains("sd-tab-content")) tabs.unshift(node);
        }
        return tabs;
    }

    /** The label of a tab content: sphinx-design renders input, label and content as siblings. */
    function labelOf(content) {
        const label = content.previousElementSibling;
        return label?.classList.contains("sd-tab-label") ? label : null;
    }

    /** The reader's last choice in a group, as stored by sphinx-design. */
    function storedChoice(group) {
        try {
            const key = `sphinx-design-tab-id-${group}`;
            return window.sessionStorage.getItem(key);
        } catch {
            return null; // storage unavailable (privacy mode)
        }
    }

    /**
     * URL (query and fragment) that points to `id` and reproduces the
     * reader's tab selection: the selected tab of every synced group, with
     * the tabs enclosing `el` taking precedence.
     */
    function permalink(el, id) {
        const params = new URLSearchParams();
        for (const label of document.querySelectorAll(
            ".sd-tab-label[data-sync-group]",
        )) {
            const group = label.getAttribute("data-sync-group");
            if (params.has(group)) continue;
            const stored = storedChoice(group);
            if (stored) params.set(group, stored);
            else if (label.previousElementSibling?.checked)
                params.set(group, label.getAttribute("data-sync-id"));
        }
        for (const content of enclosingTabs(el)) {
            const label = labelOf(content);
            const group = label?.getAttribute("data-sync-group");
            const sync = label?.getAttribute("data-sync-id");
            if (group && sync) params.set(group, sync);
        }
        const query = params.toString();
        return `${query ? `?${query}` : ""}#${id}`;
    }

    /** Open the tabs that contain the element with this id, then scroll to it. */
    function reveal(id) {
        const target = id && document.getElementById(decodeURIComponent(id));
        if (!target) return;
        const tabs = enclosingTabs(target);
        if (!tabs.length) return;
        for (const content of tabs) {
            const label = labelOf(content);
            const input = label?.previousElementSibling;
            // clicking the label also syncs all tab sets of its group
            if (input && !input.checked) label.click();
        }
        target.scrollIntoView();
    }

    const RUBRICS = ".sd-tab-content .rubric[id]";

    function addPermalinks() {
        for (const el of document.querySelectorAll(RUBRICS)) {
            const link = document.createElement("a");
            link.className = "headerlink";
            link.href = permalink(el, el.id);
            link.title = "Link to this part, with the selected tabs";
            link.textContent = "¶";
            el.appendChild(link);
        }
    }

    /** Keep the "¶" links in step with the tabs the reader selects. */
    function refreshPermalinks() {
        const links = document.querySelectorAll(`${RUBRICS} > a.headerlink`);
        for (const link of links) {
            link.href = permalink(link.parentElement, link.parentElement.id);
        }
    }

    /**
     * Record a tab choice in the address bar, so that the URL always shows
     * the selected tabs. Replaces the history entry instead of adding one per
     * click; the fragment is kept.
     */
    function updateUrl(label) {
        const group = label.getAttribute("data-sync-group");
        const sync = label.getAttribute("data-sync-id");
        if (!group || !sync) return;
        const url = new URL(window.location.href);
        url.searchParams.set(group, sync);
        window.history.replaceState(window.history.state, "", url);
    }

    // run after sphinx-design has restored the tab selection (on DOMContentLoaded)
    window.addEventListener("load", () => {
        addPermalinks();
        for (const label of document.querySelectorAll(".sd-tab-label")) {
            label.addEventListener("click", () => {
                updateUrl(label);
                setTimeout(refreshPermalinks);
            });
        }
        reveal(window.location.hash.slice(1));
    });
    window.addEventListener("hashchange", () =>
        reveal(window.location.hash.slice(1)),
    );
})();
