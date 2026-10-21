// Footnotes as popups.
//
// A footnote reference shows its footnote in a box next to it: on hover, on
// keyboard focus, and on click or tap (touch devices cannot hover). The
// footnote list at the end of the page is hidden on screen while this script
// runs (see custom.css); printing and readers without JavaScript keep it.

(() => {
    "use strict";

    const HIDE_DELAY = 200; // ms, time to move the pointer into the box

    // hide the footnote list only when this script runs (see custom.css)
    document.documentElement.classList.add("footnote-popups");

    let popup = null;
    let owner = null; // the reference whose footnote is shown
    let pinned = false; // opened by a click; stays until dismissed
    let hideTimer = null;

    /** The footnote a reference points to. */
    function footnoteOf(ref) {
        const id = decodeURIComponent(ref.getAttribute("href").slice(1));
        const note = document.getElementById(id);
        return note?.matches("aside.footnote") ? note : null;
    }

    function ensurePopup() {
        if (popup) return popup;
        popup = document.createElement("div");
        popup.className = "footnote-popup";
        popup.id = "footnote-popup";
        popup.setAttribute("role", "tooltip");
        popup.hidden = true;
        popup.addEventListener("mouseenter", () => clearTimeout(hideTimer));
        popup.addEventListener("mouseleave", () => scheduleHide());
        document.body.appendChild(popup);
        return popup;
    }

    /** Place the box below the reference, inside the viewport. */
    function place(ref) {
        const box = ref.getBoundingClientRect();
        const margin = 8;
        popup.style.left = "0px";
        popup.style.top = "0px";
        const width = popup.offsetWidth;
        const left = Math.min(
            Math.max(margin, box.left + box.width / 2 - width / 2),
            document.documentElement.clientWidth - width - margin,
        );
        let top = box.bottom + margin;
        // above the reference when there is no room below
        if (top + popup.offsetHeight > window.innerHeight - margin)
            top = box.top - popup.offsetHeight - margin;
        popup.style.left = `${left + window.scrollX}px`;
        popup.style.top = `${Math.max(margin, top) + window.scrollY}px`;
    }

    function show(ref, pin = false) {
        const note = footnoteOf(ref);
        if (!note) return;
        clearTimeout(hideTimer);
        ensurePopup();
        if (owner !== ref) {
            popup.replaceChildren(
                ...[...note.children]
                    .filter((el) => !el.matches("span.label"))
                    .map((el) => el.cloneNode(true)),
            );
            owner?.removeAttribute("aria-describedby");
            owner = ref;
            ref.setAttribute("aria-describedby", popup.id);
        }
        pinned = pin;
        popup.hidden = false;
        place(ref);
    }

    function hide() {
        clearTimeout(hideTimer);
        if (!popup) return;
        popup.hidden = true;
        owner?.removeAttribute("aria-describedby");
        owner = null;
        pinned = false;
    }

    function scheduleHide() {
        if (pinned) return;
        clearTimeout(hideTimer);
        hideTimer = setTimeout(hide, HIDE_DELAY);
    }

    /**
     * Mark the section that holds only the footnote list (and its entry in
     * the page contents), so that it is hidden with the list.
     */
    function markNotesSection() {
        for (const list of document.querySelectorAll("aside.footnote-list")) {
            const section = list.closest("section");
            if (!section?.id) continue;
            // a hidden toctree at the end of the page leaves an empty wrapper here
            const other = [...section.children].filter(
                (el) =>
                    !el.matches(
                        "h1, h2, h3, hr.footnotes, aside.footnote-list, span[id]",
                    ) &&
                    !(el.matches(".toctree-wrapper") && !el.textContent.trim()),
            );
            if (other.length) continue;
            section.classList.add("footnote-section");
            for (const a of document.querySelectorAll(
                `.bd-toc a[href="#${section.id}"]`,
            ))
                a.closest("li")?.classList.add("footnote-section");
        }
    }

    document.addEventListener("DOMContentLoaded", () => {
        markNotesSection();
        for (const ref of document.querySelectorAll("a.footnote-reference")) {
            if (!footnoteOf(ref)) continue;
            ref.addEventListener("mouseenter", () => show(ref, pinned));
            ref.addEventListener("mouseleave", () => scheduleHide());
            ref.addEventListener("focus", () => show(ref));
            ref.addEventListener("blur", () => scheduleHide());
            ref.addEventListener("click", (event) => {
                // the footnote list is hidden, so do not jump to it
                event.preventDefault();
                if (owner === ref && pinned) hide();
                else show(ref, true);
            });
        }
        document.addEventListener("click", (event) => {
            if (!popup || popup.hidden) return;
            if (popup.contains(event.target) || owner?.contains(event.target))
                return;
            hide();
        });
        document.addEventListener("keydown", (event) => {
            if (event.key === "Escape") hide();
        });
        window.addEventListener("resize", () => owner && place(owner));
    });
})();
