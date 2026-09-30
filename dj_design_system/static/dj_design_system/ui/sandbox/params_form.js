/* ParamsForm — dds__sandbox__params_form. Moved from gallery-toolbar.js.
 *
 * Drag the drawer's top bar ([data-gallery-resizer]) to resize the drawer.
 * initDrawer() runs on first load and again after every HTMX swap of the
 * sandbox body, which replaces the drawer.
 */
(function () {
  "use strict";

  // Aborted at the start of each re-init to remove stale listeners.
  var currentAbortController = null;

  function initDrawer() {
    if (currentAbortController) {
      currentAbortController.abort();
    }
    currentAbortController = new AbortController();
    var signal = currentAbortController.signal;

    var drawer = document.querySelector("[data-gallery-drawer]");
    var resizer = document.querySelector("[data-gallery-resizer]");
    var container = document.querySelector(".gallery-split__pane-body[data-gallery-sandbox-body]");

    if (drawer && resizer && container) {
      var startY = 0;
      var startHeight = 0;

      resizer.addEventListener("pointerdown", function (e) {
        if (e.button !== 0) return;
        e.preventDefault();
        startY = e.clientY;
        startHeight = drawer.offsetHeight;

        // Capture pointer to prevent iframe from swallowing events
        resizer.setPointerCapture(e.pointerId);

        var onPointerMove = function (ev) {
          var dy = startY - ev.clientY;
          var newHeight = startHeight + dy;
          var minHeight = 48;
          var containerMax = container.offsetHeight - 50;
          
          // Max height is either 30vh or the actual content height, whichever is larger.
          var thirtyVh = window.innerHeight * 0.3;
          var maxAllowedByContent = Math.max(thirtyVh, drawer.scrollHeight);
          var maxHeight = Math.min(containerMax, maxAllowedByContent);

          if (newHeight < minHeight) newHeight = minHeight;
          if (newHeight > maxHeight) newHeight = maxHeight;

          drawer.style.height = newHeight + "px";
          drawer.style.maxHeight = "none";
        };

        var onPointerUp = function (ev) {
          resizer.removeEventListener("pointermove", onPointerMove);
          resizer.removeEventListener("pointerup", onPointerUp);
          document.body.style.cursor = "";
          resizer.releasePointerCapture(ev.pointerId);
        };

        resizer.addEventListener("pointermove", onPointerMove);
        resizer.addEventListener("pointerup", onPointerUp);
        document.body.style.cursor = "ns-resize";
      }, { signal: signal });
    }
  }

  initDrawer();

  document.addEventListener("htmx:afterSwap", function (e) {
    if (e.detail.target.hasAttribute("data-gallery-sandbox-body")) {
      initDrawer();
    }
  });
})();
