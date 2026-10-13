(function () {
    const wrapper = document.querySelector(".canvas-wrapper");
    if (!wrapper || !window.parent || window.parent === window) return;
    if (!wrapper.classList.contains("canvas-wrapper--basic")) return;

    let lastHeight = -1;
    function sendResize() {
        const height = Math.max(
            wrapper.scrollHeight,
            wrapper.offsetHeight
        );
        if (height !== lastHeight) {
            lastHeight = height;
            window.parent.postMessage({
                type: "canvas-resize",
                id: window.name || "",
                height: height
            }, "*");
        }
    }

    const ro = new ResizeObserver(sendResize);
    ro.observe(wrapper);

    const mo = new MutationObserver(sendResize);
    mo.observe(document.body, {
        attributes: true,
        childList: true,
        subtree: true
    });

    window.addEventListener("load", sendResize);
    document.addEventListener("DOMContentLoaded", sendResize);
})();

