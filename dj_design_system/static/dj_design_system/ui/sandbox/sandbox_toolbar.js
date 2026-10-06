/* SandboxToolbar — dds__sandbox__sandbox_toolbar. Moved from gallery-toolbar.js.
 *
 * Applies the toolbar's background, viewport and zoom choices (the popouts
 * named bg, viewport and zoom by data-gallery-panel) to the sandbox iframe.
 * Communicates with the iframe via contentDocument (same-origin).
 *
 * initToolbar() is called on first load and again after every HTMX swap of
 * #gallery-sandbox-body, so the toolbar stays functional when component
 * parameters change without a full page reload.
 *
 * All user selections are stored in IIFE-scope state and restored each time
 * the toolbar and iframe are recreated after an HTMX swap.
 */
(function () {
  "use strict";

  /* ---- State preserved across re-inits --------------------------- */

  // Aborted at the start of each re-init to remove stale document listeners.
  var currentAbortController = null;

  // Toolbar selections – null means "use default / not yet chosen".
  var currentBg = null; // e.g. "white", "grey"
  var currentTheme = null; // e.g. "default", "dark"
  var currentZoom = null; // integer percent, e.g. 100
  var currentViewportWidth = null; // px integer, null = responsive

  /* ---- Helpers --------------------------------------------------- */

  function getSandboxIframe() {
    return document.querySelector(".gallery-sandbox__iframe");
  }

  function getCanvasWrapper(iframe) {
    try {
      return iframe.contentDocument.querySelector(".canvas-wrapper");
    } catch (e) {
      return null;
    }
  }

  /**
   * Apply viewport scaling.
   * When the chosen viewport width exceeds the container, scale the iframe
   * down using CSS transform so media queries still fire at the true width.
   */
  function applyViewportScale() {
    var iframe = getSandboxIframe();
    if (!iframe) return;

    var container = iframe.closest(".gallery-sandbox__canvas");
    if (!container) return;

    if (!currentViewportWidth) {
      // Responsive: fill the container
      iframe.style.width = "";
      iframe.style.maxWidth = "";
      iframe.style.transform = "";
      iframe.style.transformOrigin = "";
      container.style.height = "";
      container.classList.remove("gallery-sandbox__canvas--viewport");
      return;
    }

    var paneWidth = container.clientWidth;
    iframe.style.width = currentViewportWidth + "px";
    iframe.style.maxWidth = "none";
    container.classList.add("gallery-sandbox__canvas--viewport");

    if (currentViewportWidth > paneWidth) {
      var scale = paneWidth / currentViewportWidth;
      iframe.style.transform = "scale(" + scale + ")";
      iframe.style.transformOrigin = "top left";
      // Correct container height for the scaled iframe
      container.style.height = iframe.offsetHeight * scale + "px";
    } else {
      iframe.style.transform = "";
      iframe.style.transformOrigin = "";
      container.style.height = "";
    }
  }

  /* ---- applyIframeEffects ---------------------------------------- */

  /**
   * Re-apply bg and zoom state to the sandbox iframe's contentDocument.
   *
   * Called each time the iframe finishes loading. ToggleButton's script
   * re-applies its own effects (outline, RTL, measure) on the same event.
   */
  function applyIframeEffects() {
    var iframe = getSandboxIframe();
    var doc = iframe ? iframe.contentDocument : null;
    if (!doc || !doc.body) return;

    var wrapper = getCanvasWrapper(iframe);

    if (wrapper) {
      // Restore background colour selection
      if (currentBg !== null) {
        wrapper.className =
          wrapper.className.replace(/\bcanvas-bg-\S+/g, "").trim() +
          " canvas-bg-" +
          currentBg;
      }

      // Restore zoom level
      if (currentZoom !== null) {
        wrapper.style.zoom = currentZoom / 100;
      }
    }
  }

  /* ---- initToolbar ----------------------------------------------- */

  /**
   * (Re-)initialise all toolbar event listeners.
   *
   * Safe to call multiple times: document-level listeners from the previous
   * call are removed via AbortController before new ones are added.
   * Element-level listeners are naturally cleaned up because HTMX replaces
   * the DOM nodes, discarding any listeners attached to the old elements.
   */
  function initToolbar() {
    if (currentAbortController) {
      currentAbortController.abort();
    }
    currentAbortController = new AbortController();
    var signal = currentAbortController.signal;

    /* -- Variant preset selector -- */

    var variantSelect = document.querySelector("[data-gallery-variant-select]");
    if (variantSelect && variantSelect.form) {
      var isKeyNav = false;
      var lastValue = variantSelect.value;

      variantSelect.addEventListener(
        "keydown",
        function (e) {
          if (
            e.key === "ArrowDown" ||
            e.key === "ArrowUp" ||
            e.key === "ArrowLeft" ||
            e.key === "ArrowRight" ||
            e.key === "PageUp" ||
            e.key === "PageDown" ||
            e.key === "Home" ||
            e.key === "End"
          ) {
            isKeyNav = true;
          } else if (e.key === "Enter") {
            isKeyNav = false;
            if (variantSelect.value !== lastValue) {
              lastValue = variantSelect.value;
              variantSelect.form.submit();
            }
          }
        },
        { signal: signal },
      );

      variantSelect.addEventListener(
        "change",
        function () {
          if (!isKeyNav) {
            lastValue = variantSelect.value;
            variantSelect.form.submit();
          }
        },
        { signal: signal },
      );

      variantSelect.addEventListener(
        "blur",
        function () {
          if (isKeyNav) {
            isKeyNav = false;
            if (variantSelect.value !== lastValue) {
              lastValue = variantSelect.value;
              variantSelect.form.submit();
            }
          }
        },
        { signal: signal },
      );
    }

    /* -- Background colour -- */

    var bgToggle = document.querySelector(
      ".gallery-sandbox-toolbar__bg-toggle",
    );
    var bgPanel = document.querySelector('[data-gallery-panel="bg"]');

    if (bgPanel) {
      // Restore active selection in the newly-created panel
      var activeBg = currentBg !== null ? currentBg : bgPanel.dataset.initialBg;
      if (activeBg) {
        bgPanel
          .querySelectorAll(".gallery-sandbox-toolbar__bg-option")
          .forEach(function (opt) {
            opt.classList.toggle(
              "gallery-sandbox-toolbar__popout-option--active",
              opt.dataset.bg === activeBg,
            );
          });
        var activeChip = bgPanel.querySelector(
          "[data-bg='" + activeBg + "'] .gallery-sandbox-toolbar__bg-chip",
        );
        var swatch = bgToggle
          ? bgToggle.querySelector(".gallery-sandbox-toolbar__bg-swatch")
          : null;
        if (activeChip && swatch) {
          swatch.style.background =
            window.getComputedStyle(activeChip).background;
        }
      }

      bgPanel.addEventListener("click", function (e) {
        var btn = e.target.closest("[data-bg]");
        if (!btn) return;

        var bgValue = btn.dataset.bg;
        currentBg = bgValue;
        var iframe = getSandboxIframe();
        if (!iframe) return;

        var wrapper = getCanvasWrapper(iframe);
        if (wrapper) {
          wrapper.className =
            wrapper.className.replace(/\bcanvas-bg-\S+/g, "").trim() +
            " canvas-bg-" +
            bgValue;
        }

        // Update swatch colour
        var swatch = bgToggle
          ? bgToggle.querySelector(".gallery-sandbox-toolbar__bg-swatch")
          : null;
        if (swatch) {
          var chip = btn.querySelector(".gallery-sandbox-toolbar__bg-chip");
          if (chip) {
            swatch.style.background = window.getComputedStyle(chip).background;
          }
        }

        // Update active state
        bgPanel
          .querySelectorAll(".gallery-sandbox-toolbar__bg-option")
          .forEach(function (opt) {
            opt.classList.toggle(
              "gallery-sandbox-toolbar__popout-option--active",
              opt === btn,
            );
          });
      });
    }

    /* -- Theme selector -- */

    document.addEventListener("dds-theme-changed", function(e) {
      if (currentTheme !== e.detail) {
        currentBg = null;
      }
      currentTheme = e.detail;
    }, { signal: signal });

    /* -- Zoom -- */

    var zoomPanel = document.querySelector('[data-gallery-panel="zoom"]');
    var zoomValueEl = document.querySelector(
      ".gallery-sandbox-toolbar__zoom-value",
    );

    if (zoomPanel) {
      // Restore zoom label and active state
      if (currentZoom !== null && zoomValueEl) {
        zoomValueEl.textContent = currentZoom + "%";
        zoomPanel
          .querySelectorAll(".gallery-sandbox-toolbar__zoom-btn")
          .forEach(function (b) {
            b.classList.toggle(
              "gallery-sandbox-toolbar__popout-option--active",
              parseInt(b.dataset.zoom, 10) === currentZoom,
            );
          });
      }

      zoomPanel.addEventListener("click", function (e) {
        var btn = e.target.closest("[data-zoom]");
        if (!btn) return;

        currentZoom = parseInt(btn.dataset.zoom, 10);
        var zoomLevel = currentZoom / 100;
        var iframe = getSandboxIframe();
        if (!iframe) return;

        var wrapper = getCanvasWrapper(iframe);
        if (wrapper) {
          wrapper.style.zoom = zoomLevel;
        }

        // Update toggle label
        if (zoomValueEl) {
          zoomValueEl.textContent = btn.dataset.zoom + "%";
        }

        // Update active state
        zoomPanel
          .querySelectorAll(".gallery-sandbox-toolbar__zoom-btn")
          .forEach(function (b) {
            b.classList.toggle(
              "gallery-sandbox-toolbar__popout-option--active",
              b === btn,
            );
          });
      });
    }

    /* -- Viewport -- */

    var viewportPanel = document.querySelector(
      '[data-gallery-panel="viewport"]',
    );
    var viewportValueEl = document.querySelector(
      ".gallery-sandbox-toolbar__viewport-value",
    );

    // Restore viewport label and active state in the newly-created toolbar
    if (viewportValueEl) {
      viewportValueEl.textContent =
        currentViewportWidth === null
          ? "Responsive"
          : currentViewportWidth + "px";
    }
    if (viewportPanel && currentViewportWidth !== null) {
      viewportPanel
        .querySelectorAll(".gallery-sandbox-toolbar__viewport-btn")
        .forEach(function (b) {
          b.classList.toggle(
            "gallery-sandbox-toolbar__popout-option--active",
            parseInt(b.dataset.viewport, 10) === currentViewportWidth,
          );
        });
    }

    // Recalculate on pane resize and iframe load
    var sandboxIframe = getSandboxIframe();
    if (sandboxIframe) {
      var canvasContainer = sandboxIframe.closest(".gallery-sandbox__canvas");

      // Re-apply bg, zoom and viewport after every iframe load
      sandboxIframe.addEventListener("load", function () {
        applyViewportScale();
        applyIframeEffects();
      });

      if (canvasContainer && typeof ResizeObserver !== "undefined") {
        new ResizeObserver(function () {
          if (currentViewportWidth) {
            applyViewportScale();
          }
        }).observe(canvasContainer);
      }
    }

    if (viewportPanel) {
      viewportPanel.addEventListener("click", function (e) {
        var btn = e.target.closest("[data-viewport]");
        if (!btn) return;

        var value = btn.dataset.viewport;
        if (value === "responsive") {
          currentViewportWidth = null;
        } else {
          currentViewportWidth = parseInt(value, 10);
        }

        // Update toggle label
        if (viewportValueEl) {
          viewportValueEl.textContent =
            value === "responsive" ? "Responsive" : value + "px";
        }

        // Update active state
        viewportPanel
          .querySelectorAll(".gallery-sandbox-toolbar__viewport-btn")
          .forEach(function (b) {
            b.classList.toggle(
              "gallery-sandbox-toolbar__popout-option--active",
              b === btn,
            );
          });

        applyViewportScale();
      });
    }
  }

  /* ---- Bootstrap ------------------------------------------------- */

  initToolbar();

  // Re-initialise whenever HTMX swaps the gallery sandbox body. Added once at
  // module level (no abort needed) so it survives across multiple swaps.
  document.addEventListener("htmx:afterSwap", function (e) {
    if (e.detail.target.hasAttribute("data-gallery-sandbox-body")) {
      initToolbar();
    }
  });
})();
