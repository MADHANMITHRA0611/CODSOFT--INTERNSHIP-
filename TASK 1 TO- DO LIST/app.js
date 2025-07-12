// app.js - handles dark mode toggle

window.addEventListener("DOMContentLoaded", () => {
  const toggle = document.getElementById("toggle-theme");
  const html = document.documentElement;
  const saved = localStorage.getItem("theme");

  if (saved) {
    html.setAttribute("data-theme", saved);
  }

  toggle?.addEventListener("click", () => {
    const current = html.getAttribute("data-theme") || "light";
    const newTheme = current === "light" ? "dark" : "light";
    html.setAttribute("data-theme", newTheme);
    localStorage.setItem("theme", newTheme);
  });
});
