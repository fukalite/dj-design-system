/* Popout — dds__sandbox__popout. Moved from gallery-toolbar.js.
 *
 * Clicking a popout's button (the element whose aria-controls names the
 * panel) opens its panel and closes any other. Clicking outside the panel,
 * choosing an option in it, or pressing Escape closes it again.
 *
 * initPopouts() runs on first load and again after every HTMX swap of the
 * sandbox body, which replaces the toolbar.
 */
(function () {
  "use strict";

  // Aborted at the start of each re-init to remove stale document listeners.
  var currentAbortController = null;

  /**
   * Wire up a toggle button + popout panel pair.
   * Handles open/close, outside-click dismissal, and closing sibling popouts.
   *
   * @param {Element} toggle
   * @param {Element} panel
   * @param {AbortSignal} signal  Used to remove the document click listener on re-init.
   */
  function initPopout(toggle, panel, signal) {
    if (!toggle || !panel) return;

    toggle.addEventListener("click", function () {
      var opening = panel.hidden;
      closeAllPopouts();
      if (opening) {
        panel.hidden = false;
        toggle.setAttribute("aria-expanded", "true");
      }
    });

    document.addEventListener(
      "click",
      function (e) {
        if (
          !panel.hidden &&
          !toggle.contains(e.target) &&
          !panel.contains(e.target)
        ) {
          panel.hidden = true;
          toggle.setAttribute("aria-expanded", "false");
        }
      },
      { signal: signal },
    );

    document.addEventListener(
      "keydown",
      function (e) {
        if (e.key === "Escape" && !panel.hidden) {
          panel.hidden = true;
          toggle.setAttribute("aria-expanded", "false");
          toggle.focus();
        }
      },
      { signal: signal },
    );

    // Choosing an option closes the popout. This listens on the document so
    // that it runs after the option's own handlers on the panel.
    document.addEventListener(
      "click",
      function (e) {
        if (
          !panel.hidden &&
          panel.contains(e.target) &&
          e.target.closest(".gallery-sandbox-toolbar__popout-option")
        ) {
          closeAllPopouts();
        }
      },
      { signal: signal },
    );
  }

  /** Close every popout on the toolbar. */
  function closeAllPopouts() {
    document
      .querySelectorAll(".gallery-sandbox-toolbar__popout")
      .forEach(function (p) {
        p.hidden = true;
      });
    document.querySelectorAll("[aria-expanded]").forEach(function (btn) {
      btn.setAttribute("aria-expanded", "false");
    });
  }

  /**
   * (Re-)initialise every popout on the page.
   *
   * Safe to call multiple times: document-level listeners from the previous
   * call are removed via AbortController before new ones are added.
   * Element-level listeners are naturally cleaned up because HTMX replaces
   * the DOM nodes, discarding any listeners attached to the old elements.
   */
  function initPopouts() {
    if (currentAbortController) {
      currentAbortController.abort();
    }
    currentAbortController = new AbortController();
    var signal = currentAbortController.signal;

    document
      .querySelectorAll(".gallery-sandbox-toolbar__popout")
      .forEach(function (panel) {
        var toggle = panel.id
          ? document.querySelector(
              '[aria-controls="' + CSS.escape(panel.id) + '"]',
            )
          : null;
        initPopout(toggle, panel, signal);
      });
  }

  initPopouts();

  // Re-initialise whenever HTMX swaps the gallery sandbox body. Added once at
  // module level (no abort needed) so it survives across multiple swaps.
  document.addEventListener("htmx:afterSwap", function (e) {
    if (e.detail.target.hasAttribute("data-gallery-sandbox-body")) {
      initPopouts();
    }
  });
})();
