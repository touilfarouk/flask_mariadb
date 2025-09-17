import { api } from "./api.js";

let mode = "add"; // add | update

document.addEventListener("DOMContentLoaded", () => {
  // Charger la liste des utilisateurs
  loadUsers();

  // Initialiser le formulaire
  initUserForm();
});

export async function loadUsers() {
  try {
    const res = await api.get("/auth/users");
    const tbody = document.querySelector("#userTable");
    if (!tbody) return;
    tbody.innerHTML = "";

    if (!res.ok) {
      console.error("Erreur chargement utilisateurs:", res.error);
      tbody.innerHTML = `<tr><td colspan="6" class="p-2 text-center text-red-600 text-sm">❌ ${res.error || "Erreur de chargement"}</td></tr>`;
      return;
    }

    (res.data || []).forEach(({ id, firstname, lastname, email, role }) => {
      const tr = document.createElement("tr");
      tr.innerHTML = `
        <td class="p-1 border text-xs">${id}</td>
        <td class="p-1 border text-xs">${firstname}</td>
        <td class="p-1 border text-xs">${lastname}</td>
        <td class="p-1 border text-xs">${email}</td>
        <td class="p-1 border text-xs">${role}</td>
        <td class="p-1 border text-xs text-center">
          <button class="editBtn bg-blue-500 hover:bg-blue-600 text-white text-xs px-1 py-0.5 rounded mr-1" 
                  data-id="${id}" data-firstname="${firstname}" data-lastname="${lastname}" data-email="${email}" data-role="${role}">✏️</button>
          <button class="deleteBtn bg-red-500 hover:bg-red-600 text-white text-xs px-1 py-0.5 rounded" data-id="${id}">🗑</button>
        </td>
      `;
      tbody.append(tr);
    });

    attachUserActions();
  } catch (err) {
    console.error("❌ Exception chargement utilisateurs:", err);
  }
}

function initUserForm() {
  const form = document.querySelector("#userForm");
  const btn = document.querySelector("#submitUser");
  const notify = document.querySelector("#notification");
  const hiddenId = document.querySelector("#userId");

  if (!form) return;

  form.addEventListener("submit", async (e) => {
    e.preventDefault();

    const firstname = document.querySelector("#firstname").value.trim();
    const lastname = document.querySelector("#lastname").value.trim();
    const email = document.querySelector("#email").value.trim();
    const password = document.querySelector("#password").value;
    const role = document.querySelector("#role").value || "user";

    if (mode === "add") {
      if (!firstname || !lastname || !email || !password || !role) {
        return showNotification(notify, "❌ Tous les champs sont obligatoires (mot de passe requis à la création)", "error");
      }
      const res = await api.post("/auth/signup", { firstname, lastname, email, password, role });
      if (!res.ok) {
        return showNotification(notify, "❌ " + (res.error || "Échec de la création"), "error");
      }
      // Ne pas stocker le token renvoyé ici (création par un admin)
      showNotification(notify, "✅ Utilisateur créé avec succès", "success");
    } else {
      if (!hiddenId.value) return;
      if (!firstname || !lastname || !role) {
        return showNotification(notify, "❌ Prénom, nom et rôle sont requis pour la mise à jour", "error");
      }
      const res = await api.put(`/auth/users/${hiddenId.value}`, { firstname, lastname, role });
      if (!res.ok) {
        return showNotification(notify, "❌ " + (res.error || "Échec de la mise à jour"), "error");
      }
      showNotification(notify, "✅ Utilisateur mis à jour avec succès", "success");
    }

    // Reset
    form.reset();
    hiddenId.value = "";
    btn.dataset.mode = "add";
    btn.textContent = "✅ Créer l'utilisateur";
    mode = "add";

    await loadUsers();
  });
}

function attachUserActions() {
  document.querySelectorAll(".editBtn").forEach((btn) => {
    btn.addEventListener("click", () => {
      const { id, firstname, lastname, email, role } = btn.dataset;
      document.querySelector("#firstname").value = firstname || "";
      document.querySelector("#lastname").value = lastname || "";
      document.querySelector("#email").value = email || "";
      document.querySelector("#role").value = role || "user";
      document.querySelector("#password").value = ""; // password not needed for update
      document.querySelector("#userId").value = id;

      const submitBtn = document.querySelector("#submitUser");
      submitBtn.dataset.mode = "update";
      submitBtn.textContent = "🔄 Mettre à jour";
      mode = "update";
    });
  });

  document.querySelectorAll(".deleteBtn").forEach((btn) => {
    btn.addEventListener("click", async (e) => {
      e.preventDefault();
      e.stopPropagation();
      const id = btn.dataset.id;
      if (!id) return;
      if (!confirm("Voulez-vous vraiment supprimer cet utilisateur ?")) return;
      const res = await api.delete(`/auth/users/${id}`);
      if (!res.ok) {
        alert("❌ " + (res.error || "Échec de la suppression"));
        return;
      }
      alert("✅ Utilisateur supprimé avec succès");
      await loadUsers();
    });
  });
}

function showNotification(el, message, type) {
  if (!el) return;
  el.textContent = message;
  el.className = type === "success" ? "text-green-600 font-bold" : "text-red-600 font-bold";
}
