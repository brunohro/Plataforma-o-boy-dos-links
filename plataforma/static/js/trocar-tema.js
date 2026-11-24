document.addEventListener("DOMContentLoaded", function () {

    const themeToggle = document.getElementById("themeToggle");
    const icon = themeToggle.querySelector("i");

    // Recupera o tema salvo
    const savedTheme = localStorage.getItem("theme") || "dark";

    document.documentElement.setAttribute("data-theme", savedTheme);

    updateIcon(savedTheme);

    // Alternar tema
    themeToggle.addEventListener("click", function () {

        const currentTheme = document.documentElement.getAttribute("data-theme");

        const newTheme = currentTheme === "dark" ? "light" : "dark";

        document.documentElement.setAttribute("data-theme", newTheme);

        localStorage.setItem("theme", newTheme);

        updateIcon(newTheme);

    });

    // Atualiza o ícone
    function updateIcon(theme) {

        if (theme === "dark") {
            icon.classList.remove("fa-sun");
            icon.classList.add("fa-moon");
        } else {
            icon.classList.remove("fa-moon");
            icon.classList.add("fa-sun");
        }

    }

});