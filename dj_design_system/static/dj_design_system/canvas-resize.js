(function () {
    const wrapper = document.querySelector(".canvas-wrapper");
    if (!wrapper || !window.parent || window.parent === window) return;
    if (!wrapper.classList.contains("canvas-wrapper--basic")) return;
    const ro = new ResizeObserver(function () {
        window.parent.postMessage({
            type: "canvas-resize",
            id: window.name || "",
            height: Math.max(wrapper.scrollHeight, wrapper.offsetHeight)
        }, "*");
    });
    ro.observe(wrapper);
})();
