// API wrapper
const API_BASE_URL = "http://127.0.0.1:3000";
// const API_BASE_URL = "http://213.179.181.50/api";

export const api = {
  get:    async (url) =>       request("GET", url),
  post:   async (url, body) => request("POST", url, body),
  put:    async (url, body) => request("PUT", url, body),     // 🔥 update complet
  patch:  async (url, body) => request("PATCH", url, body), // 🔥 update partiel
  delete: async (url) =>       request("DELETE", url),           // 🔥 suppression
};

async function request(method, url, body = null) {
  try {
    const token = localStorage.getItem("token");
    
    // Debug logging
    console.log(`API Request: ${method} ${url}`);
    console.log(`Token exists: ${!!token}`);
    if (token) {
      console.log(`Token preview: ${token.substring(0, 20)}...`);
    }

    const res = await fetch(API_BASE_URL + url, {
      method,
      headers: {
        "Content-Type": "application/json",
        ...(token ? { Authorization: "Bearer " + token } : {})
      },
      body: body ? JSON.stringify(body) : null,
    });

    const data = await res.json().catch(() => ({}));

    if (!res.ok) {
      console.error(`API Error: ${res.status} ${res.statusText}`, data);
      // If unauthorized, clear token and redirect to login
      if (res.status === 401) {
        localStorage.removeItem("token");
        if (window.location.pathname !== "/frontend/login.html") {
          window.location.href = "login.html";
        }
      }
      return { ok: false, error: data.error || res.statusText };
    }

    return { ok: true, ...data };
  } catch (err) {
    console.error("API Request failed:", err);
    return { ok: false, error: err.message };
  }
}




// Exemple d’utilisation

// 👉 Supprimer un utilisateur :

// const res = await api.delete("/users/5");
// if (!res.ok) {
//   console.error("Erreur suppression :", res.error);
// } else {
//   console.log("Utilisateur supprimé !");
// }


// 👉 Mettre à jour un utilisateur (PUT) :

// const payload = { firstname: "Ali", lastname: "Karim" };
// const res = await api.put("/users/5", payload);
// if (!res.ok) {
//   console.error("Erreur update :", res.error);
// } else {
//   console.log("Utilisateur mis à jour :", res);
// }


// 👉 Mettre à jour partiellement (PATCH) :

// const payload = { role: "admin" };
// const res = await api.patch("/users/5", payload);
// if (!res.ok) {
//   console.error("Erreur patch :", res.error);
// } else {
//   console.log("Rôle mis à jour :", res);
// }