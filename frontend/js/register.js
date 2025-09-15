import { api } from "./api.js";

document.addEventListener("DOMContentLoaded", () => {
  // Check if already logged in
  if (localStorage.getItem("token")) {
    window.location.href = "index.html";
    return;
  }

  const form = document.querySelector("#signupForm");
  const notify = document.querySelector("#notification");

  if (!form) return;

  form.addEventListener("submit", async (e) => {
    e.preventDefault();

    const payload = {
      firstname: document.querySelector("#firstname").value.trim(),
      lastname: document.querySelector("#lastname").value.trim(),
      email: document.querySelector("#email").value.trim(),
      password: document.querySelector("#password").value,
      role: document.querySelector("#role").value || "user",
    };

    // Validation des champs requis
    if (!payload.firstname || !payload.lastname || !payload.email || !payload.password || !payload.role) {
      showNotification(notify, "❌ Tous les champs sont obligatoires", "error");
      return;
    }

    const res = await api.post("/auth/signup", payload);

    if (!res.ok) {
      showNotification(notify, "❌ " + (res.error || "Échec de l'inscription"), "error");
      return;
    }

    if (res.token) {
      localStorage.setItem("token", res.token);
      showNotification(notify, "✅ Inscription réussie ! Redirection...", "success");
      setTimeout(() => (window.location.href = "index.html"), 1500);
    } else {
      showNotification(notify, "❌ Échec de l'inscription", "error");
    }
  });
});

function showNotification(el, message, type) {
  if (!el) return;
  el.textContent = message;
  el.className =
    type === "success" ? "text-green-600 font-bold" : "text-red-600 font-bold";
}
