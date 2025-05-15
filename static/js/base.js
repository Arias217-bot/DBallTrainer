document.addEventListener("DOMContentLoaded", function () {
    let sidebar = document.getElementById("sidebar");
    let toggleBtn = document.getElementById("toggleSidebar");
    let content = document.getElementById("mainContent");

    toggleBtn.addEventListener("click", function () {
        sidebar.classList.toggle("hidden");
        content.classList.toggle("expanded");

        if (sidebar.classList.contains("hidden")) {
            toggleBtn.style.left = "10px";
        } else {
            toggleBtn.style.left = "130px";
        }
    });
});
