(function () {
    var wrapper = document.querySelector(".canvas-wrapper");
    if (!wrapper || !window.parent || window.parent === window) return;
    if (!wrapper.classList.contains("canvas-wrapper--basic")) return;
    var ro = new ResizeObserver(function () {
        window.parent.postMessage({
            type: "canvas-resize",
            id: window.name || "",
            height: document.documentElement.scrollHeight
        }, "*");
    });
    ro.observe(wrapper);
})();
