// The versions in the main navigation: below the entry of the abstract data model its versions
// (1.0, ...), below the entry of the storage format its versions (0.5, ..., 0.1). Below them, each
// part links to its implementations and its version history, which show the latest state for
// every version and exist once, at the root of the site.
//
// A storage format page selects its storage format version and the data model version that it
// encodes. A data model page (data-model/<version>/) selects only the data model version. The
// root of the site (the latest state) selects none, and its entries of the two parts lead to the
// preferred version. The versions come from templates/spec-versions.html (known when the page
// was built) and are refreshed from versions.json, so that a page built earlier also lists
// versions released later.

(() => {
    "use strict";

    // the pages below each part that exist once, at the root: [page, title]
    const LATEST = {
        "data-model": [
            ["implementations", "Implementations"],
            ["data-model-versions", "Version history"],
        ],
        "storage-format": [
            ["storage-format-implementations", "Implementations"],
            ["storage-format-versions", "Version history"],
        ],
    };

    /** The link of a page in the main navigation. */
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

    /** The list of pages below a navigation entry, created if it has none. */
    function children(link) {
        const li = link.parentElement;
        let ul = li.querySelector(":scope > details > ul, :scope > ul");
        if (!ul) {
            ul = document.createElement("ul");
            li.append(ul);
        }
        return ul;
    }

    function versions(items) {
        const row = document.createElement("li");
        row.className = "toctree-l2 spec-versions-row";
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
        row.append(ul);
        return row;
    }

    /** Below a part: its versions, then its pages at the root. */
    function part(link, part, items, data) {
        const ul = children(link);
        ul.querySelector(".spec-versions-row")?.remove();
        for (const [page, title] of LATEST[part]) {
            const href = `${data.siteUrl}${page}.html`;
            let a =
                ul.querySelector(`a[data-latest-page="${page}"]`) ??
                entry(page, data.page);
            if (!a || a.parentElement.parentElement !== ul) {
                const li = document.createElement("li");
                li.className = "toctree-l2";
                a = document.createElement("a");
                a.className = "reference internal";
                a.textContent = title;
                li.append(a);
            }
            a.dataset.latestPage = page;
            if (!data.latest || a.getAttribute("href") !== "#") a.href = href;
            ul.append(a.parentElement); // in the order of LATEST
        }
        ul.prepend(versions(items));
    }

    function render(listed, data) {
        const { dataModel, storageFormat, page } = data;
        const models = listed.data_models;
        const formats = models.flatMap((m) => m.storage_formats);
        const preferred = formats.find((f) => f.preferred);
        const model = entry("data-model", page);
        if (model) {
            part(
                model,
                "data-model",
                models.map((m) => ({
                    text: m.version,
                    url: `${m.url}data-model.html`,
                    selected: m.version === dataModel,
                })),
                data,
            );
            if (data.latest) {
                const own = models.find((m) =>
                    m.storage_formats.includes(preferred),
                );
                if (own) model.href = `${own.url}data-model.html`;
            }
        }
        const format = entry("storage-format", page);
        if (format) {
            part(
                format,
                "storage-format",
                formats.map((f) => ({
                    text: f.version,
                    url: `${f.url}storage-format.html`,
                    selected: !!storageFormat && f.version === storageFormat,
                })),
                data,
            );
            // on a data model page or at the root, the storage format entry leads to the newest
            // storage format of this data model, or to the preferred one
            if (!storageFormat) {
                const own = models.find((m) => m.version === dataModel);
                const target =
                    own?.storage_formats.find((f) => !f.draft) ?? preferred;
                if (target) format.href = `${target.url}storage-format.html`;
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
