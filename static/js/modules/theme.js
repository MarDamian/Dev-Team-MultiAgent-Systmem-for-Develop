export function initTheme() {
    const themeToggle = document.getElementById("theme-toggle");

    function setTheme(theme) {
        document.body.classList.toggle("dark-mode", theme === "dark");
        localStorage.setItem("theme", theme);
        themeToggle.checked = (theme === "dark");
    }

    const savedTheme = localStorage.getItem("theme");
    if (savedTheme) {
        setTheme(savedTheme);
    } else if (window.matchMedia && window.matchMedia("(prefers-color-scheme: dark)").matches) {
        setTheme("dark");
    } else {
        setTheme("light");
    }

    themeToggle.addEventListener("change", () => {
        setTheme(themeToggle.checked ? "dark" : "light");
    });
}