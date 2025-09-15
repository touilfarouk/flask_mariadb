import { api } from "./api.js";

let editMode = false;
let editId = null;

document.addEventListener("DOMContentLoaded", () => {
  loadSections();
  initSectionForm && initSectionForm();
});

export const loadSections = async () => {
  try {
    const { data } = await api.get("/section/all");
    const select = document.querySelector("#sectionSelect");
    const tbody = document.querySelector("#sectionTable");

    if (select) select.innerHTML = "";
    if (tbody) tbody.innerHTML = "";

    data?.forEach(({ id, label, type, unit, personnels }) => {
      // Dropdown
      if (select) {
        const opt = new Option(`${label} (${type} - ${unit})`, id);
        select.append(opt);
      }

      // Table
      if (tbody) {
        const tr = document.createElement("tr");
        tr.innerHTML = `
         <tr class="text-xs">
            <td class="p-1 border">${id}</td>
            <td class="p-1 border">${label}</td>
            <td class="p-1 border">${type}</td>
            <td class="p-1 border">${unit}</td>
            <td class="p-1 border">${personnels ?? "-"}</td>
            <td class="p-1 border text-center">
              <button class="editBtn bg-blue-500 text-white px-1 py-0.5 rounded text-xs mr-1" 
                      data-id="${id}" data-label="${label}" data-type="${type}" data-unit="${unit}">
                ✏️
              </button>
              <button class="deleteBtn bg-red-500 text-white px-1 py-0.5 rounded text-xs" 
                      data-id="${id}">
                🗑
              </button>
            </td>
          </tr>

        `;
        tbody.append(tr);
      }
    });

    // Bind Edit buttons
    document.querySelectorAll(".editBtn").forEach((btn) => {
      btn.addEventListener("click", (e) => {
        const { id, label, type, unit } = e.target.dataset;
        const row = e.target.closest('tr');
        const code_section = row.children[0].textContent;
        
        document.querySelector("#code_section").value = code_section;
        document.querySelector("#label").value = label;
        document.querySelector("#unit").value = unit;
        document.querySelector("#type").value = type;
        editMode = true;
        editId = id;
        document.querySelector("#formBtn").textContent = "✏️ Mettre à jour";
      });
    });

    // Bind Delete buttons
    document.querySelectorAll(".deleteBtn").forEach((btn) => {
      btn.addEventListener("click", async (e) => {
        const id = e.target.dataset.id;
        if (confirm("Voulez-vous vraiment supprimer cette section ?")) {
          try {
            await api.delete(`/section/delete/${id}`);
            await loadSections();
          } catch (err) {
            console.error("Erreur lors de la suppression:", err);
          }
        }
      });
    });

  } catch (err) {
    console.error("Erreur lors du chargement des sections:", err);
  }
};

export const initSectionForm = () => {
  document.querySelector("#sectionForm")?.addEventListener("submit", async (e) => {
    e.preventDefault();

    const payload = {
      code_section: document.querySelector("#code_section").value,
      label: document.querySelector("#label").value,
      unit: document.querySelector("#unit").value,
      type: document.querySelector("#type").value,
    };

    try {
      if (editMode && editId) {
        await api.put(`/section/update/${editId}`, payload);
        editMode = false;
        editId = null;
        document.querySelector("#formBtn").textContent = "➕ Ajouter";
      } else {
        await api.post("/section/add", payload);
      }

      await loadSections();
      e.target.reset();
    } catch (err) {
      console.error("Erreur lors de l'opération sur la section:", err);
    }
  });
};
