import { api } from "./api.js";

document.addEventListener("DOMContentLoaded", async () => {
  const currentPage = window.location.pathname.split("/").pop();
  const unprotectedPages = ["login.html", "index.html"];

  // 🚨 Protection automatique
  const token = localStorage.getItem("token");
  if (!unprotectedPages.includes(currentPage) && !token) {
    window.location.href = "login.html";
    return;
  }

  // 📌 Sidebar dynamique
  const sidebar = document.getElementById("sidebar");
  if (sidebar) {
    sidebar.innerHTML = `
      <div class="p-6 border-b border-gray-200 dark:border-gray-700">
        <h1 onclick="window.location.href='index.html'"  
            class="text-xl font-bold text-orange-600 dark:text-orange-400 cursor-pointer">
          ⚙️ Gestion
        </h1>
      </div>
      <nav class="flex-1 p-4 space-y-3">
        <a href="personnel.html" 
           class="flex items-center gap-3 p-3 rounded-lg text-blue-600 dark:text-blue-400 font-medium hover:bg-blue-100 dark:hover:bg-gray-700">
          👨‍💼 <span>Personnel</span>
        </a>
        <a href="section.html" 
           class="flex items-center gap-3 p-3 rounded-lg text-green-600 dark:text-green-400 font-medium hover:bg-green-100 dark:hover:bg-gray-700">
          🏢 <span>Sections</span>
        </a>
        <a href="register.html" 
           class="flex items-center gap-3 p-3 rounded-lg text-purple-600 dark:text-purple-400 font-medium hover:bg-purple-100 dark:hover:bg-gray-700">
          📝 <span>Register</span>
        </a>
        <a href="#" id="logoutLink"
           class="flex items-center gap-3 p-3 rounded-lg text-red-600 dark:text-red-400 font-medium hover:bg-red-100 dark:hover:bg-gray-700">
          🚪 <span>Logout</span>
        </a>
      </nav>
      <footer class="p-4 text-sm text-gray-500 dark:text-gray-400">
        © 2025 MonApp
      </footer>
    `;
  }

  // 🔐 Vérification côté API (optionnel)
  if (!unprotectedPages.includes(currentPage)) {
    try {
      const res = await api.get("/protected");
      if (!res.ok) throw new Error(res.error || "Unauthorized");
    } catch (err) {
      setTimeout(() => (window.location.href = "login.html"), 500);
    }
  }

  // 🚪 Logout
  const logoutLink = document.querySelector("#logoutLink");
  if (logoutLink) {
    logoutLink.addEventListener("click", (e) => {
      e.preventDefault();
      localStorage.removeItem("token");
      alert("✅ Déconnexion réussie !");
      window.location.href = "login.html";
    });
  }
});
