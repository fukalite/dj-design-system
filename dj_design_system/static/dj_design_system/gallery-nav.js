/* Expand/collapse folder nodes in the gallery sidebar nav tree. */
(function () {
    var nav = document.getElementById("gallery-nav");
    if (!nav) return;

    nav.addEventListener("click", function (event) {
        var toggle = event.target.closest(".gallery-nav__toggle");
        if (!toggle) return;

        var children = document.getElementById(toggle.getAttribute("aria-controls"));
        if (!children) return;

        var expanded = toggle.getAttribute("aria-expanded") !== "true";
        toggle.setAttribute("aria-expanded", expanded ? "true" : "false");
        children.hidden = !expanded;
        toggle.closest(".gallery-nav__folder").classList.toggle("gallery-nav__folder--open", expanded);
    });
})();
