/* ToggleButton — dds__sandbox__toggle_button. Moved from gallery-toolbar.js.
 *
 * The outline, measure and RTL toggles switch an effect on the sandbox
 * iframe's contentDocument (same-origin). The measure effect loads the
 * script named by the toolbar's data-measure-script into the iframe.
 *
 * initToggles() is called on first load and again after every HTMX swap of
 * #gallery-sandbox-body. Which toggles are on is kept in IIFE-scope state,
 * and re-applied each time the iframe loads.
 */
(function () {
  "use strict";

  /* ---- State preserved across re-inits --------------------------- */

  // On/off toggle states – objects so initToggle can mutate .active and .cleanup in place.
  var outlineState = { active: false, cleanup: null };
  var rtlState = { active: false, cleanup: null };
  var measureState = { active: false, cleanup: null };

  // Resolved once and kept in scope so reapplyToggleEffects can access it.
  var measureScriptSrc = null;

  /* ---- Helpers --------------------------------------------------- */

  function getSandboxIframe() {
    return document.querySelector(".gallery-sandbox__iframe");
  }

  function getIframeDocument() {
    var iframe = getSandboxIframe();
    if (!iframe) return null;
    try {
      return iframe.contentDocument;
    } catch (e) {
      return null;
    }
  }

  /**
   * Wire up a simple on/off toggle button with aria-pressed.
   *
   * @param {string} selector  CSS selector for the toggle button.
   * @param {function} onActivate  Called with (iframeDoc) when toggling on. Should return a cleanup function.
   * @param {{ active: boolean, cleanup: ?function }} state  Shared state object persisted across
   *   re-inits. .active tracks on/off; .cleanup holds the teardown function for the current effect.
   */
  function initToggle(selector, onActivate, state) {
    var btn = document.querySelector(selector);
    if (!btn) return;

    // Restore button visual state after a re-init.
    // iframe effects are re-applied by reapplyToggleEffects() on the iframe load event.
    if (state.active) {
      btn.setAttribute("aria-pressed", "true");
      btn.classList.add("gallery-sandbox-toolbar__btn--active");
    }

    btn.addEventListener("click", function () {
      var doc = getIframeDocument();
      if (!doc) return;

      if (state.active) {
        if (state.cleanup) {
          state.cleanup(doc);
          state.cleanup = null;
        }
        state.active = false;
        btn.setAttribute("aria-pressed", "false");
        btn.classList.remove("gallery-sandbox-toolbar__btn--active");
      } else {
        state.cleanup = onActivate(doc);
        state.active = true;
        btn.setAttribute("aria-pressed", "true");
        btn.classList.add("gallery-sandbox-toolbar__btn--active");
      }
    });
  }

  /* ---- Constants ------------------------------------------------- */

  var OUTLINE_STYLE_ID = "gallery-box-model-outline";
  var outlineCSS =
    ".canvas-wrapper > * { outline: 2px solid rgba(255, 140, 0, 0.5) !important; " +
    "background-color: rgba(65, 105, 225, 0.2) !important; }" +
    ".canvas-wrapper > * * { outline: 2px solid rgba(255, 140, 0, 0.5) !important; " +
    "box-shadow: inset 0 0 0 1000px rgba(50, 205, 50, 0.12) !important; }";

  var MEASURE_STYLE_ID = "gallery-measure-style";
  var measureCSS = [
    ".gallery-measure-overlay { position: absolute; pointer-events: none; z-index: 99999; }",
    ".gallery-measure-margin { background: rgba(255, 165, 0, 0.3); }",
    ".gallery-measure-padding { background: rgba(50, 205, 50, 0.25); }",
    ".gallery-measure-content { background: rgba(65, 105, 225, 0.15); }",
    ".gallery-measure-label {",
    "  position: absolute; pointer-events: none; z-index: 100000;",
    "  background: rgba(35, 35, 50, 0.88); color: #fff;",
    "  font: 600 10px/1 monospace; padding: 2px 4px; border-radius: 2px;",
    "  white-space: nowrap;",
    "}",
  ].join("\n");

  /* ---- reapplyToggleEffects -------------------------------------- */

  /**
   * Re-apply active on/off toggle effects to the newly-loaded iframe document
   * and refresh each state's cleanup reference.
   *
   * Must be called from the iframe 'load' event (not { once: true }) so it
   * fires on every navigation of the iframe, not just the first blank-document
   * load that occurs when the element is inserted into the DOM.
   */
  function reapplyToggleEffects() {
    var doc = getIframeDocument();
    if (!doc || !doc.body) return;

    if (outlineState.active) {
      if (!doc.getElementById(OUTLINE_STYLE_ID)) {
        var outlineStyle = doc.createElement("style");
        outlineStyle.id = OUTLINE_STYLE_ID;
        outlineStyle.textContent = outlineCSS;
        doc.head.appendChild(outlineStyle);
      }
      outlineState.cleanup = function (d) {
        var el = d.getElementById(OUTLINE_STYLE_ID);
        if (el) el.remove();
      };
    }

    if (rtlState.active) {
      doc.documentElement.setAttribute("dir", "rtl");
      rtlState.cleanup = function (d) {
        d.documentElement.removeAttribute("dir");
      };
    }

    if (measureState.active && !doc.getElementById(MEASURE_STYLE_ID)) {
      var measureStyle = doc.createElement("style");
      measureStyle.id = MEASURE_STYLE_ID;
      measureStyle.textContent = measureCSS;
      doc.head.appendChild(measureStyle);

      var measureScript = doc.createElement("script");
      if (measureScriptSrc) {
        measureScript.src = measureScriptSrc;
      }
      doc.body.appendChild(measureScript);

      measureState.cleanup = function (d) {
        var wrapper = d.querySelector(".canvas-wrapper");
        if (wrapper && wrapper._galleryMeasureCleanup) {
          wrapper._galleryMeasureCleanup();
        }
        var el = d.getElementById(MEASURE_STYLE_ID);
        if (el) el.remove();
        var container = d.getElementById("gallery-measure-container");
        if (container) container.remove();
      };
    }
  }

  /* ---- initToggles ----------------------------------------------- */

  /**
   * (Re-)initialise the toggle buttons.
   *
   * Safe to call multiple times: HTMX replaces the buttons and the iframe,
   * discarding any listeners attached to the old elements.
   */
  function initToggles() {
    var sandboxIframe = getSandboxIframe();
    if (sandboxIframe) {
      // Re-apply the toggle effects after every iframe load
      sandboxIframe.addEventListener("load", reapplyToggleEffects);
    }

    /* -- Box model outline -- */

    initToggle(
      ".gallery-sandbox-toolbar__outline-toggle",
      function (doc) {
        var style = doc.createElement("style");
        style.id = OUTLINE_STYLE_ID;
        style.textContent = outlineCSS;
        doc.head.appendChild(style);
        return function (doc) {
          var el = doc.getElementById(OUTLINE_STYLE_ID);
          if (el) el.remove();
        };
      },
      outlineState,
    );

    /* -- RTL direction -- */

    initToggle(
      ".gallery-sandbox-toolbar__rtl-toggle",
      function (doc) {
        doc.documentElement.setAttribute("dir", "rtl");
        return function (doc) {
          doc.documentElement.removeAttribute("dir");
        };
      },
      rtlState,
    );

    /* -- Measure -- */

    var toolbar = document.querySelector(".gallery-sandbox-toolbar");
    measureScriptSrc = toolbar ? toolbar.dataset.measureScript : null;

    initToggle(
      ".gallery-sandbox-toolbar__measure-toggle",
      function (doc) {
        var style = doc.createElement("style");
        style.id = MEASURE_STYLE_ID;
        style.textContent = measureCSS;
        doc.head.appendChild(style);

        var script = doc.createElement("script");
        if (measureScriptSrc) {
          script.src = measureScriptSrc;
        }
        doc.body.appendChild(script);

        return function (doc) {
          // Call the cleanup function registered by the measure script
          var wrapper = doc.querySelector(".canvas-wrapper");
          if (wrapper && wrapper._galleryMeasureCleanup) {
            wrapper._galleryMeasureCleanup();
          }
          var el = doc.getElementById(MEASURE_STYLE_ID);
          if (el) el.remove();
          var container = doc.getElementById("gallery-measure-container");
          if (container) container.remove();
        };
      },
      measureState,
    );
  }

  /* ---- Bootstrap ------------------------------------------------- */

  initToggles();

  // Re-initialise whenever HTMX swaps the gallery sandbox body. Added once at
  // module level (no abort needed) so it survives across multiple swaps.
  document.addEventListener("htmx:afterSwap", function (e) {
    if (e.detail.target.hasAttribute("data-gallery-sandbox-body")) {
      initToggles();
    }
  });
})();
