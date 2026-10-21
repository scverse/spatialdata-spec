// The versions in the main navigation: below the entry of the abstract data model its versions
// (1.0, ...), below the entry of the storage format its versions (0.5, ..., 0.1).
//
// A storage format page selects its storage format version and the data model version that it
// encodes. A data model page (data-model/<version>/) selects only the data model version. The
// versions come from templates/spec-versions.html (known when the page was built) and are
// refreshed from versions.json, so that a page built earlier also lists versions released later.

(() => {
    "use strict";

    /** The navigation entry of a page: its link in the main navigation. */
    function entry(page, current) {
        for (const a of document.querySelectorAll(
            ".bd-docs-nav a.reference.internal",
        )) {
            const href = a.getAttribute("href");
            const name =
                href === "#" ? current : href.replace(/\.html(#.*)?$/, "");
            if (name === page) return a;
        }
        return null;
    }

    function list(after, items) {
        const ul = document.createElement("ul");
        ul.className = "spec-versions";
        for (const { text, url, selected } of items) {
            const li = document.createElement("li");
            const a = document.createElement("a");
            a.href = url;
            a.textContent = text;
            if (selected) {
                li.classList.add("selected");
                a.setAttribute("aria-current", "true");
            }
            li.append(a);
            ul.append(li);
        }
        const entry = after.parentElement;
        entry.querySelector(".spec-versions-row")?.remove();
        const row = document.createElement("li");
        row.className = "toctree-l2 spec-versions-row";
        row.append(ul);
        // first below the entry, above its pages (the version history)
        const children = entry.querySelector(":scope > details > ul");
        if (children) children.prepend(row);
        else {
            const wrapper = document.createElement("ul");
            wrapper.append(row);
            after.after(wrapper);
        }
    }

    function render(listed, data) {
        const { dataModel, storageFormat, page } = data;
        const models = listed.data_models;
        const formats = models.flatMap((m) => m.storage_formats);
        const model = entry("data-model", page);
        if (model)
            list(
                model,
                models.map((m) => ({
                    text: m.version,
                    url: `${m.url}data-model.html`,
                    selected: m.version === dataModel,
                })),
            );
        const format = entry("storage-format", page);
        if (format) {
            list(
                format,
                formats.map((f) => ({
                    text: f.version,
                    url: `${f.url}storage-format.html`,
                    selected: !!storageFormat && f.version === storageFormat,
                })),
            );
            // on a data model page, the storage format entry leads to the newest storage format
            // of this data model
            if (!storageFormat) {
                const own = models.find((m) => m.version === dataModel);
                const newest = own?.storage_formats.find((f) => !f.draft);
                if (newest) format.href = `${newest.url}storage-format.html`;
            }
        }
    }

    document.addEventListener("DOMContentLoaded", async () => {
        const data = document.querySelector("script.spec-versions");
        if (!data) return;
        render(JSON.parse(data.textContent), data.dataset);
        try {
            const response = await fetch(data.dataset.versionsUrl);
            if (response.ok) render(await response.json(), data.dataset);
        } catch {
            // offline or a preview: keep the versions known at build time
        }
    });
})();
