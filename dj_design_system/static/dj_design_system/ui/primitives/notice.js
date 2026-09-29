(function () {
    var notice = document.getElementById("static-snapshot-notice");
    if (!notice) return;
    if (location.hostname !== "localhost" && location.hostname !== "127.0.0.1") {
        notice.style.display = "block";
    }
})();
