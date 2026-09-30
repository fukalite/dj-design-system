/* Preview auto-height, split out of gallery-tabs.js when the tab syncing
 * moved to the Tabs component. Loaded only on component pages. */
(function () {
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
