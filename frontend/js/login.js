import { api } from "./api.js";

document.addEventListener("DOMContentLoaded", () => {
  // Si déjà connecté
  if (localStorage.getItem("token")) {
    window.location.href = "";
    return;
  }

  const form = document.querySelector("#loginForm");
  const notify = document.querySelector("#notification");
  if (!form) return;

  form.addEventListener("submit", async (e) => {
    e.preventDefault();

    const payload = {
      email: document.querySelector("#email").value.trim(),
      password: document.querySelector("#password").value
    };

    const res = await api.post("/auth/login", payload);

    if (!res.ok) {
      showNotification(notify, "❌ " + res.error, "error");
      return;
    }

    if (res.token) {
      localStorage.setItem("token", res.token);
      showNotification(notify, "✅ Login successful, redirecting...", "success");
      setTimeout(() => (window.location.href = "index.html"), 1000);
    } else {
      showNotification(notify, "❌ No token received", "error");
    }
  });
});

function showNotification(el, message, type) {
  if (!el) return;
  el.textContent = message;
  el.className =
    type === "success" ? "text-green-600 font-bold" : "text-red-600 font-bold";
}
