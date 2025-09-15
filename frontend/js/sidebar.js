// Injecte sidebar.html dans #sidebar et gère le lien actif
document.addEventListener("DOMContentLoaded", async () => {
  const sidebarEl = document.getElementById("sidebar");
  if (!sidebarEl) return;

  try {
    const res = await fetch("sidebar.html");
    const html = await res.text();
    sidebarEl.innerHTML = html;

    // Détection de la page courante
    const current = window.location.pathname.split("/").pop() || "index.html";
    const links = sidebarEl.querySelectorAll("a");

    links.forEach(link => {
      if (link.getAttribute("href") === current) {
        link.classList.add("font-bold", "bg-gray-200", "dark:bg-gray-700");
      } else {
        link.classList.remove("bg-gray-200", "dark:bg-gray-700");
      }
    });
  } catch (err) {
    console.error("Erreur lors du chargement de la sidebar:", err);
  }
});
