(function () {
    var themeSelect = document.getElementById('gallery-global-theme-select');
    if (!themeSelect) return;

    themeSelect.addEventListener("change", function (e) {
        var themeValue = e.target.value;
        document.cookie = "dds_theme=" + themeValue + "; path=/; max-age=31536000";

        // Update URL params so they persist across shares
        var browserUrl = new URL(window.location.href);
        browserUrl.searchParams.set("theme", themeValue);
        // Full page load to apply the theme everywhere cleanly
        window.location.href = browserUrl.toString();
    });
})();
