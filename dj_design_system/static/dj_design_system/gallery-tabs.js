(function () {
    var docs = document.getElementById("gallery-tab-docs");
    var sandbox = document.getElementById("gallery-tab-sandbox");
    var split = document.querySelector(".gallery-split");

    if (docs && sandbox && split) {
        function showPane(isSandbox, updateHash) {
            if (isSandbox) {
                sandbox.checked = true;
            } else {
                docs.checked = true;
            }
            split.classList.toggle("gallery-split--show-sandbox", isSandbox);
            if (updateHash) {
                if (isSandbox) {
                    history.replaceState(null, "", "#pane-sandbox");
                } else {
                    history.replaceState(null, "", window.location.pathname + window.location.search);
                }
            }
        }

        docs.addEventListener("change", function () { showPane(false, true); });
        sandbox.addEventListener("change", function () { showPane(true, true); });

        /* Sync from hash on load and hashchange */
        function syncFromHash() {
            var isSandbox = window.location.hash === "#pane-sandbox";
            // If there's no hash but we have query params, default to sandbox
            // so deeplinks work smoothly on mobile.
            if (!window.location.hash && window.location.search && window.location.search !== "?") {
                isSandbox = true;
            }
            showPane(isSandbox, false);
        }
        syncFromHash();
        window.addEventListener("hashchange", syncFromHash);

        /* Preserve #pane-sandbox hash when HTMX replaces URL history */
        document.body.addEventListener("htmx:replacedInHistory", function (evt) {
            var isSandbox = sandbox.checked;
            if (isSandbox && window.location.hash !== "#pane-sandbox") {
                history.replaceState(null, "", window.location.pathname + window.location.search + "#pane-sandbox");
            }
        });
    }

    /* Auto-height: listen for resize messages from basic-mode iframes */
    window.addEventListener("message", function (event) {
        if (!event.data || event.data.type !== "canvas-resize") return;
        var iframes = document.querySelectorAll(
            "iframe.gallery-doc-preview__iframe, iframe.gallery-md-canvas__iframe"
        );
        iframes.forEach(function (iframe) {
            if (event.data.id && iframe.dataset.canvasId === event.data.id) {
                iframe.style.height = event.data.height + "px";
            } else if (iframe.contentWindow === event.source) {
                iframe.style.height = event.data.height + "px";
            }
        });
    });
})();
