import { loadPersonnel, initPersonnelForm } from "./personnel.js";
import { loadSections, initSectionForm } from "./section.js";

// Initial load
loadSections();
loadPersonnel();

// Init forms
initPersonnelForm();
initSectionForm();
