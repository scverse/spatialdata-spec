// The versions in the navigation (templates/spec-versions.html): each data model version, with
// the storage formats that encode it. The page lists the versions known when it was built; this
// script replaces them with the current versions.json, so that a page built earlier also lists
// versions released later, and points each link at the same page in that version.

(() => {
    "use strict";

    function item(text, url, current) {
        const li = document.createElement("li");
        if (current) li.classList.add("current");
        const a = document.createElement("a");
        a.href = url;
        a.textContent = text;
        li.append(a);
        return li;
    }

    async function render(nav) {
        const { dataModel, storageFormat, page } = nav.dataset;
        let listed;
        try {
            const response = await fetch(nav.dataset.versionsUrl);
            if (!response.ok) return;
            listed = await response.json();
        } catch {
            return; // offline or a preview: keep the versions known at build time
        }
        const list = document.createElement("ul");
        list.className = "spec-versions-list";
        for (const model of listed.data_models) {
            const li = item(
                `Data model ${model.version}`,
                model.url,
                model.version === dataModel,
            );
            li.classList.add("spec-versions-model");
            const formats = document.createElement("ul");
            for (const format of model.storage_formats) {
                const here =
                    model.version === dataModel &&
                    format.version === storageFormat;
                // the same page in that version
                formats.append(
                    item(
                        `Storage format ${format.version}`,
                        `${format.url}${page}.html`,
                        here,
                    ),
                );
            }
            li.append(formats);
            list.append(li);
        }
        nav.querySelector(".spec-versions-list").replaceWith(list);
    }

    document.addEventListener("DOMContentLoaded", () => {
        for (const nav of document.querySelectorAll(".spec-versions"))
            render(nav);
    });
})();
