import { api } from "./api.js";

let editingId = null; // 🔹 savoir si on est en mode édition

// Charger au DOM
document.addEventListener("DOMContentLoaded", () => {
  initSignupForm();
  loadUsers();
});

// ✅ Formulaire inscription / mise à jour
export const initSignupForm = () => {
  const form = document.querySelector("#signupForm");
  const notify = document.querySelector("#notification");
  const formBtn = document.querySelector("#formBtn");

  if (!form) return;

form.addEventListener("submit", async (e) => {
  e.preventDefault();

  const payload = {
    firstname: document.querySelector("#firstname").value.trim(),
    lastname: document.querySelector("#lastname").value.trim(),
    email: document.querySelector("#email").value.trim(),
    password: document.querySelector("#password").value, // ⚠️ facultatif en update
    role: document.querySelector("#role").value || "customer",
  };

  const id = document.querySelector("#userId").value;
  const mode = document.querySelector("#submitUser").dataset.mode;

  let res;
  if (mode === "update" && id) {
    delete payload.password; // pas de mot de passe si update
    res = await api.put(`/auth/users/${id}`, payload);
  } else {
    res = await api.post("/auth/signup", payload);
  }

  if (!res.ok) {
    alert("❌ " + res.error);
    return;
  }

  // ✅ Réinitialiser formulaire et bouton
  form.reset();
  const btnSubmit = document.querySelector("#submitUser");
  btnSubmit.textContent = "✅ Enregistrer";
  btnSubmit.dataset.mode = "add";
  document.querySelector("#userId").value = "";

  await loadUsers();
});

};

// ✅ Liste utilisateurs
export const loadUsers = async () => {
  try {
    const { data } = await api.get("/auth/users");
    const tbody = document.querySelector("#usersTable");
    if (!tbody) return;

    tbody.innerHTML = "";

    (data || []).forEach(({ id, firstname, lastname, email, role }) => {
      const tr = document.createElement("tr");

      tr.innerHTML = `
        <td class="px-2 py-1 border text-sm">${firstname}</td>
        <td class="px-2 py-1 border text-sm">${lastname}</td>
        <td class="px-2 py-1 border text-sm">${email}</td>
        <td class="px-2 py-1 border text-sm">${role}</td>
        <td class="px-2 py-1 border text-sm text-center">
          <button class="editBtn bg-blue-500 hover:bg-blue-600 text-white text-xs px-2 py-1 rounded mr-1" data-id="${id}">
            ✏
          </button>
          <button class="deleteBtn bg-red-500 hover:bg-red-600 text-white text-xs px-2 py-1 rounded" data-id="${id}">
            🗑
          </button>
        </td>
      `;

      tbody.appendChild(tr);
    });

    attachUserActions();
  } catch (err) {
    console.error("❌ Erreur lors du chargement des utilisateurs:", err);
  }
};

// ✅ Actions
function attachUserActions() {
  // Supprimer
  document.querySelectorAll(".deleteBtn").forEach((btn) => {
    btn.addEventListener("click", async () => {
      const id = btn.dataset.id;
      if (!confirm("Voulez-vous vraiment supprimer cet utilisateur ?")) return;

      try {
        const res = await api.delete(`/auth/users/${id}`);
        if (!res.ok) {
          alert("❌ " + res.error);
          return;
        }
        await loadUsers();
      } catch (err) {
        console.error("❌ Erreur lors de la suppression:", err);
      }
    });
  });

  // Modifier → remplir formulaire

document.querySelectorAll(".editBtn").forEach((btn) => {
  btn.addEventListener("click", async () => {
    const id = btn.dataset.id;

    const tr = btn.closest("tr");
    const firstname = tr.children[0].textContent;
    const lastname = tr.children[1].textContent;
    const email = tr.children[2].textContent;
    const role = tr.children[3].textContent;

    // Remplir le formulaire
    document.querySelector("#firstname").value = firstname;
    document.querySelector("#lastname").value = lastname;
    document.querySelector("#email").value = email;
    document.querySelector("#role").value = role;

    // Stocker l'ID
    document.querySelector("#userId").value = id;

    // Changer le bouton
    const btnSubmit = document.querySelector("#submitUser");
    btnSubmit.textContent = "🔄 Mettre à jour";
    btnSubmit.dataset.mode = "update";
  });
});

}

// ✅ Notifications
function showNotification(el, message, type) {
  if (!el) return;
  el.textContent = message;
  el.className =
    type === "success"
      ? "text-green-500 break-all"
      : "text-red-500";
}
