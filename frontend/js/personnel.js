import { api } from "./api.js";
import { loadSections } from "./section.js";

export const loadPersonnel = async () => {
  try {
    const { data } = await api.get("/personnel/all");
    const tbody = document.querySelector("#personnelTable");
    if (!tbody) return;
    tbody.innerHTML = "";

    (data || []).forEach(({ id, matricule, nom, qualification, affectation, sections }) => {
      const tr = document.createElement("tr");

      // 🔹 Normalisation des sections
      let sectionList = "-";
      if (Array.isArray(sections)) {
        sectionList = sections
          .map(s => (typeof s === "object" ? s.label || s.nom || JSON.stringify(s) : s))
          .join(", ");
      } else if (typeof sections === "string" && sections.trim() !== "") {
        sectionList = sections;
      }

      tr.innerHTML = `
        <td class="p-1 border text-xs">${matricule}</td>
        <td class="p-1 border text-xs">${nom}</td>
        <td class="p-1 border text-xs">${qualification}</td>
        <td class="p-1 border text-xs">${affectation}</td>
        <td class="p-1 border text-xs">${sectionList}</td>
        <td class="p-1 border text-xs text-center">
          <button class="editBtn bg-blue-500 hover:bg-blue-600 text-white text-xs px-1 py-0.5 rounded mr-1" data-id="${id}">
            ✏️
          </button>
          <button class="deleteBtn bg-red-500 hover:bg-red-600 text-white text-xs px-1 py-0.5 rounded" data-id="${id}">
            🗑
          </button>
        </td>
      `;

      tbody.append(tr);
    });

    attachPersonnelActions();

  } catch (err) {
    console.error("❌ Erreur lors du chargement du personnel:", err);
  }
};

export const initPersonnelForm = () => {
  const form = document.querySelector("#personnelForm");
  const btnSubmit = document.querySelector("#submitPersonnel");
  const hiddenId = document.querySelector("#personnelId");

  form.addEventListener("submit", async (e) => {
    e.preventDefault();

    const payload = {
      matricule: document.querySelector("#matricule").value.trim(),
      nom: document.querySelector("#nom").value.trim(),
      qualification: document.querySelector("#qualification").value.trim(),
      affectation: document.querySelector("#affectation").value.trim(),
      sections: Array.from(document.querySelector("#sectionSelect").selectedOptions).map(opt => opt.value),
    };

    let res;
    if (btnSubmit.dataset.mode === "update" && hiddenId.value) {
      res = await api.put(`/personnel/${hiddenId.value}`, payload);
    } else {
      res = await api.post("/personnel/add", payload);
    }

    if (!res.ok) {
      alert("❌ " + res.error);
      return;
    }

    form.reset();
    btnSubmit.textContent = "✅ Ajouter";
    btnSubmit.dataset.mode = "add";
    hiddenId.value = "";
    await loadPersonnel();
  });
};

function attachPersonnelActions() {
  // 🔹 Supprimer
  document.querySelectorAll(".deleteBtn").forEach(btn => {
    btn.addEventListener("click", async () => {
      const id = btn.dataset.id;
      if (!confirm("Voulez-vous vraiment supprimer ce personnel ?")) return;

      try {
        const res = await api.delete(`/personnel/${id}`);
        if (!res.ok) {
          alert("❌ " + res.error);
          return;
        }
        await loadPersonnel();
      } catch (err) {
        console.error("❌ Erreur lors de la suppression:", err);
      }
    });
  });

  // 🔹 Modifier → remplir le formulaire
  document.querySelectorAll(".editBtn").forEach(btn => {
    btn.addEventListener("click", () => {
      const id = btn.dataset.id;
      const tr = btn.closest("tr");

      const matricule = tr.children[0].textContent;
      const nom = tr.children[1].textContent;
      const qualification = tr.children[2].textContent;
      const affectation = tr.children[3].textContent;

      document.querySelector("#matricule").value = matricule;
      document.querySelector("#nom").value = nom;
      document.querySelector("#qualification").value = qualification;
      document.querySelector("#affectation").value = affectation;

      document.querySelector("#personnelId").value = id;

      const btnSubmit = document.querySelector("#submitPersonnel");
      btnSubmit.textContent = "🔄 Mettre à jour";
      btnSubmit.dataset.mode = "update";
    });
  });
}

// Charger sections + personnels
document.addEventListener("DOMContentLoaded", () => {
  loadSections();
  loadPersonnel();
  initPersonnelForm();
});
