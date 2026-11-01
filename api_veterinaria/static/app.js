const state = {
  owners: [],
  pets: [],
  accessories: [],
  products: [],
  foods: [],
  treatments: [],
  appointments: [],
  vaccines: [],
  veterinarians: [],
  lots: [],
  users: [],
  report: {},
  user: null,
  view: "dashboard",
  pharmacyLowStockOnly: false,
  inventoryCategoryFilters: { accessory: "", product: "", food: "" },
  treatmentSpeciesFilter: "",
};

const $ = (selector) => document.querySelector(selector);
function setTheme(theme) {
  document.documentElement.dataset.theme = theme;
  $("#theme-dark-button").setAttribute("aria-pressed", String(theme === "dark"));
  $("#theme-light-button").setAttribute("aria-pressed", String(theme === "light"));
  document.querySelector('meta[name="theme-color"]').content =
    theme === "dark" ? "#111d2b" : "#edf4fc";
  try {
    window.localStorage.setItem("zeus-vet-theme", theme);
  } catch (error) {
    console.warn("No se pudo guardar la preferencia de apariencia.", error);
  }
}

let savedTheme = "light";
try {
  const preference = window.localStorage.getItem("zeus-vet-theme");
  if (preference === "dark" || preference === "light") savedTheme = preference;
} catch (error) {
  console.warn("No se pudo leer la preferencia de apariencia.", error);
}
document.documentElement.dataset.theme = savedTheme;

const speciesLabels = {
  perro: "Perro", gato: "Gato", ave: "Ave", gallina: "Gallina",
  caballo: "Caballo", vaca: "Vaca", otro: "Otro",
};
const speciesStyleClasses = {
  perro: "dog", gato: "cat", ave: "bird", gallina: "chicken",
  caballo: "horse", vaca: "cow", otro: "other",
};
const petIllustrations = {
  perro: ["🐕", "🐶", "🐩", "🦮", "🐕‍🦺"],
  gato: ["🐈", "🐈‍⬛", "😺", "😸", "😻"],
  ave: ["🐦", "🐤", "🦜", "🕊️"],
  gallina: ["🐔", "🐣"],
  caballo: ["🐎", "🐴"],
  vaca: ["🐄", "🐮"],
  otro: ["🐾", "🐢", "🐇", "🦊"],
};
const inventoryResources = {
  accessory: { key: "accessories", collection: "/accesorios/", label: "accesorio" },
  product: { key: "products", collection: "/productos-veterinarios/", label: "producto" },
  food: { key: "foods", collection: "/alimentos/", label: "alimento" },
  treatment: { key: "treatments", collection: "/tratamientos/", label: "tratamiento" },
};
const categoryLabels = {
  collar: "Collar", correa: "Correa", juguete: "Juguete", ropa: "Ropa",
  cama: "Cama", transporte: "Transporte", medicamento: "Medicamento",
  pastilla: "Pastilla", shampoo: "Shampoo", higiene: "Higiene", otro: "Otro",
  concentrado: "Concentrado", humedo: "Húmedo", premio: "Premio",
  suplemento: "Suplemento", dieta_especial: "Dieta especial",
};
const inventoryCategoryOrder = {
  accessory: ["collar", "correa", "juguete", "ropa", "cama", "transporte", "otro"],
  product: ["medicamento", "pastilla", "shampoo", "higiene", "otro"],
  food: ["concentrado", "humedo", "premio", "suplemento", "dieta_especial"],
};
const speciesTargetLabels = { perro: "Perro", gato: "Gato", ave: "Ave", universal: "Todas las especies" };
const lifeStageLabels = { cachorro: "Cachorro", adulto: "Adulto", senior: "Senior", todas: "Todas las etapas" };
const treatmentStatusLabels = {
  recetado: "Recetado", en_curso: "En curso", completado: "Completado", suspendido: "Suspendido",
};
const catalogPhotos = {
  dogFood: {
    path: "/static/images/catalog/dog-food.jpg",
    alt: "Fotografía de alimento para perros",
    credit: "chrismetcalfTV",
    source: "https://commons.wikimedia.org/wiki/File:Dog_Food_(208810939).jpg",
    license: "CC BY 2.0",
    licenseUrl: "https://creativecommons.org/licenses/by/2.0/",
  },
  dogTreats: {
    path: "/static/images/catalog/dog-treats.jpg",
    alt: "Fotografía de premios para perros",
    credit: "Megan Marrs",
    source: "https://commons.wikimedia.org/wiki/File:Dog_Treats_(51049057473).jpg",
    license: "CC BY 2.0",
    licenseUrl: "https://creativecommons.org/licenses/by/2.0/",
  },
  catFood: {
    path: "/static/images/catalog/cat-food.jpg",
    alt: "Fotografía de alimento seco para gatos",
    credit: "Anne Jea.",
    source: "https://commons.wikimedia.org/wiki/File:Dry_cat_food_mix_08.jpg",
    license: "CC BY-SA 4.0",
    licenseUrl: "https://creativecommons.org/licenses/by-sa/4.0/",
  },
  catWetFood: {
    path: "/static/images/catalog/cat-wet-food.jpg",
    alt: "Fotografía de latas de alimento húmedo para gatos",
    credit: "Jonn Leffmann",
    source: "https://commons.wikimedia.org/wiki/File:Kattmat-Cat_food-Katzenfutter-Nourriture_pour_chats_-_2022.jpg",
    license: "CC BY 3.0",
    licenseUrl: "https://creativecommons.org/licenses/by/3.0/",
  },
  collar: {
    path: "/static/images/catalog/dog-collar.jpg",
    alt: "Fotografía de un collar de cuero para perro",
    credit: "Trougnouf (Benoit Brummer), Les cuirs d'Agathe",
    source: "https://commons.wikimedia.org/wiki/File:Leather_dog_collar_made_by_Les_cuirs_d%27Agathe_(DSC07529).jpg",
    license: "CC BY 4.0",
    licenseUrl: "https://creativecommons.org/licenses/by/4.0/",
  },
  leash: {
    path: "/static/images/catalog/dog-leash.jpg",
    alt: "Fotografía de una correa para perro",
    credit: "Schizek",
    source: "https://commons.wikimedia.org/wiki/File:PPD-Leash-PinkGreenStripes.jpg",
    license: "Dominio público",
    licenseUrl: "https://commons.wikimedia.org/wiki/Commons:Licensing",
  },
  toy: {
    path: "/static/images/catalog/cat-toy.jpg",
    alt: "Fotografía de un gato jugando con un ratón de juguete",
    credit: "Nancy Wong",
    source: "https://commons.wikimedia.org/wiki/File:Cat_playing_with_toy_mouse.jpg",
    license: "CC BY-SA 4.0",
    licenseUrl: "https://creativecommons.org/licenses/by-sa/4.0/",
  },
  bed: {
    path: "/static/images/catalog/dog-bed.jpg",
    alt: "Fotografía de un perro durmiendo en su cama",
    credit: "Tomwsulcer",
    source: "https://commons.wikimedia.org/wiki/File:Dog_sleeping_in_a_dog_bed.JPG",
    license: "CC0",
    licenseUrl: "https://creativecommons.org/publicdomain/zero/1.0/",
  },
  shampoo: {
    path: "/static/images/catalog/pet-shampoo.jpg",
    alt: "Fotografía de un frasco de shampoo antipulgas para perro",
    credit: "Shingoli",
    source: "https://commons.wikimedia.org/wiki/File:Shingoli_shampoo_Tick_n_flea_front.jpg",
    license: "CC BY-SA 4.0",
    licenseUrl: "https://creativecommons.org/licenses/by-sa/4.0/",
  },
  earDrops: {
    path: "/static/images/catalog/ear-drops.jpg",
    alt: "Fotografía de un frasco de gotas para los oídos",
    credit: "3df",
    source: "https://commons.wikimedia.org/wiki/File:Ear_drops_bottle.jpg",
    license: "CC BY-SA 4.0",
    licenseUrl: "https://creativecommons.org/licenses/by-sa/4.0/",
  },
  pills: {
    path: "/static/images/catalog/medicine-pills.jpg",
    alt: "Fotografía de cápsulas y tabletas en blíster",
    credit: "BuhaM",
    source: "https://commons.wikimedia.org/wiki/File:Pills_and_medicines_01.jpg",
    license: "CC BY-SA 4.0",
    licenseUrl: "https://creativecommons.org/licenses/by-sa/4.0/",
  },
};

function escapeHtml(value) {
  return String(value ?? "").replace(/[&<>"']/g, (character) => ({
    "&": "&amp;",
    "<": "&lt;",
    ">": "&gt;",
    '"': "&quot;",
    "'": "&#39;",
  })[character]);
}

function normalize(value) {
  return String(value ?? "").normalize("NFD").replace(/[\u0300-\u036f]/g, "").toLowerCase();
}

function initials(name) {
  return String(name ?? "")
    .trim()
    .split(/\s+/)
    .slice(0, 2)
    .map((part) => part[0]?.toUpperCase() ?? "")
    .join("") || "—";
}

function ownerName(ownerId) {
  return state.owners.find((owner) => owner.id === ownerId)?.nombre ?? "Dueño no encontrado";
}

function formatDate(value) {
  if (!value) return "—";
  const date = new Date(`${value}T00:00:00`);
  return Number.isNaN(date.valueOf())
    ? escapeHtml(value)
    : new Intl.DateTimeFormat("es-HN", { day: "2-digit", month: "short", year: "numeric" }).format(date);
}

function formatDateTime(value) {
  if (!value) return "—";
  const date = new Date(value.includes("T") ? value : value.replace(" ", "T"));
  return Number.isNaN(date.valueOf())
    ? escapeHtml(value)
    : new Intl.DateTimeFormat("es-HN", {
      day: "2-digit", month: "short", year: "numeric", hour: "2-digit", minute: "2-digit",
    }).format(date);
}

function localDateValue() {
  const now = new Date();
  return `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, "0")}-${String(now.getDate()).padStart(2, "0")}`;
}

function localDateTimeValue() {
  const date = new Date(Date.now() + 60 * 60 * 1000);
  return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, "0")}-${String(date.getDate()).padStart(2, "0")}T${String(date.getHours()).padStart(2, "0")}:${String(date.getMinutes()).padStart(2, "0")}`;
}

function toast(message, type = "success") {
  const item = document.createElement("div");
  item.className = `toast ${type}`;
  item.textContent = message;
  $("#toast-region").append(item);
  window.setTimeout(() => item.remove(), 4000);
}

async function api(path, options = {}) {
  const response = await fetch(path, {
    ...options,
    headers: {
      ...(options.body ? { "Content-Type": "application/json" } : {}),
      ...options.headers,
    },
  });
  if (!response.ok) {
    let detail = `Error del servidor (${response.status}).`;
    try {
      const body = await response.json();
      if (typeof body.detail === "string") detail = body.detail;
      else if (Array.isArray(body.detail)) detail = body.detail.map((item) => item.msg).join(" ");
    } catch {
      detail = `No se pudo completar la solicitud (${response.status}).`;
    }
    throw new Error(detail);
  }
  if (response.status === 204) return null;
  return response.json();
}

function showView(view) {
  state.view = view;
  document.querySelectorAll(".view-section").forEach((section) => section.classList.add("hidden"));
  $(`#${view}-view`).classList.remove("hidden");
  document.querySelectorAll(".nav-item").forEach((item) => {
    const active = item.dataset.view === view;
    item.classList.toggle("active", active);
    if (active) item.setAttribute("aria-current", "page");
    else item.removeAttribute("aria-current");
  });
  const labels = {
    dashboard: "Resumen", pets: "Mascotas", owners: "Dueños",
    accessories: "Tienda", products: "Farmacia", treatments: "Tratamientos",
    foods: "Nutrición", agenda: "Agenda y vacunas", reports: "Informes y seguridad",
  };
  $("#breadcrumb-current").textContent = labels[view];
  render();
}

function renderStats() {
  $("#owner-stat").textContent = state.owners.length;
  $("#pet-stat").textContent = state.pets.length;
  $("#species-stat").textContent = new Set(state.pets.map((pet) => pet.especie)).size;
  $("#pet-nav-count").textContent = state.pets.length;
  $("#owner-nav-count").textContent = state.owners.length;
  $("#pets-heading-count").textContent = state.pets.length;
  $("#owners-heading-count").textContent = state.owners.length;
  for (const [key, resource] of Object.entries(inventoryResources)) {
    const count = state[resource.key].length;
    $(`#${key}-nav-count`).textContent = count;
    $(`#${resource.key}-heading-count`).textContent = count;
  }
}

function petAvatarFor(pet) {
  const speciesClass = speciesStyleClasses[pet.especie] ?? "other";
  if (!pet.imagen_url) {
    const illustrations = petIllustrations[pet.especie] ?? petIllustrations.otro;
    const illustration = illustrations[pet.id % illustrations.length];
    return `<span class="pet-avatar ${speciesClass} pet-avatar-illustration" role="img" aria-label="Ilustración de ${speciesLabels[pet.especie] ?? "mascota"}" title="Ilustración de ${speciesLabels[pet.especie] ?? "mascota"}">${illustration}</span>`;
  }
  const image = `<img src="${escapeHtml(pet.imagen_url)}" alt="" loading="lazy" decoding="async">`;
  return `<span class="pet-avatar pet-avatar-photo ${speciesClass}" title="Foto de ${escapeHtml(pet.nombre)}">${image}</span>`;
}

function petRow(pet, withActions = false) {
  const species = speciesLabels[pet.especie] ?? "Otro";
  const className = pet.especie === "perro" ? "" : ` ${speciesStyleClasses[pet.especie] ?? "other"}`;
  const canEdit = Boolean(state.user);
  const canDelete = state.user?.rol !== "recepcion";
  const actions = withActions
    ? `<td><div class="row-actions">${canEdit ? `<button class="action-button" type="button" data-action="edit-pet" data-id="${pet.id}" aria-label="Editar ${escapeHtml(pet.nombre)}" title="Editar">✎</button>` : ""}${canDelete ? `<button class="action-button delete" type="button" data-action="delete-pet" data-id="${pet.id}" aria-label="Eliminar ${escapeHtml(pet.nombre)}" title="Eliminar">⌫</button>` : ""}</div></td>`
    : "";
  return `<tr>
    <td><div class="pet-cell">${petAvatarFor(pet)}<div><div class="pet-name">${escapeHtml(pet.nombre)}</div><div class="pet-id">Paciente #${pet.id}</div></div></div></td>
    <td><span class="species-badge${className}">${escapeHtml(species)}</span></td>
    <td>${escapeHtml(pet.raza || "Sin especificar")}</td>
    <td>${escapeHtml(ownerName(pet.dueno_id))}</td>
    <td>${formatDate(pet.fecha_nacimiento)}</td>
    ${actions}
  </tr>`;
}

function wirePetAvatarImages(container) {
  container.querySelectorAll(".pet-avatar-photo img").forEach((image) => {
    image.addEventListener("error", () => {
      const avatar = image.closest(".pet-avatar-photo");
      avatar?.classList.remove("pet-avatar-photo");
      image.remove();
      if (avatar) avatar.textContent = "🐾";
    });
  });
}

function ownerRow(owner) {
  const pets = state.pets.filter((pet) => pet.dueno_id === owner.id);
  const deleteAction = state.user?.rol !== "recepcion"
    ? `<button class="action-button delete" type="button" data-action="delete-owner" data-id="${owner.id}" aria-label="Eliminar ${escapeHtml(owner.nombre)}" title="Eliminar">⌫</button>`
    : "";
  return `<tr>
    <td><div class="owner-cell"><span class="avatar">${escapeHtml(initials(owner.nombre))}</span><div><div class="owner-name">${escapeHtml(owner.nombre)}</div><div class="owner-subtitle">Cliente #${owner.id}</div></div></div></td>
    <td>${escapeHtml(owner.telefono)}</td>
    <td>${escapeHtml(owner.direccion || "Sin dirección")}</td>
    <td><span class="result-count">${pets.length} ${pets.length === 1 ? "mascota" : "mascotas"}</span></td>
    <td><div class="row-actions"><button class="action-button" type="button" data-action="edit-owner" data-id="${owner.id}" aria-label="Editar ${escapeHtml(owner.nombre)}" title="Editar">✎</button>${deleteAction}</div></td>
  </tr>`;
}

function setEmptyState(element, show, title, message) {
  element.classList.toggle("hidden", !show);
  const titleNode = element.querySelector("strong");
  const messageNode = element.querySelector("p");
  if (titleNode && title) titleNode.textContent = title;
  if (messageNode && message) messageNode.textContent = message;
}

function renderDashboard() {
  const recent = [...state.pets].sort((first, second) => second.id - first.id).slice(0, 5);
  $("#recent-pets-body").innerHTML = recent.map((pet) => petRow(pet)).join("");
  wirePetAvatarImages($("#recent-pets-body"));
  $("#recent-pets-body").closest(".table-wrap").classList.toggle("hidden", recent.length === 0);
  $("#recent-empty").classList.toggle("hidden", recent.length !== 0);
}

function renderPets() {
  const query = normalize($("#pets-search").value);
  const filtered = state.pets.filter((pet) => normalize([
    pet.nombre, pet.especie, pet.raza, ownerName(pet.dueno_id),
  ].join(" ")).includes(query));
  $("#pets-result-count").textContent = `${filtered.length} ${filtered.length === 1 ? "registro" : "registros"}`;
  $("#pets-body").innerHTML = filtered.map((pet) => petRow(pet, true)).join("");
  wirePetAvatarImages($("#pets-body"));
  $("#pets-body").closest(".table-wrap").classList.toggle("hidden", filtered.length === 0);
  const noData = state.pets.length === 0;
  setEmptyState(
    $("#pets-empty"),
    filtered.length === 0,
    noData ? "No hay mascotas registradas" : "No encontramos resultados",
    noData ? "Añade la primera mascota a la clínica." : "Prueba con otro nombre, especie, raza o dueño.",
  );
}

function renderOwners() {
  const query = normalize($("#owners-search").value);
  const filtered = state.owners.filter((owner) => normalize([
    owner.nombre, owner.telefono, owner.direccion,
  ].join(" ")).includes(query));
  $("#owners-result-count").textContent = `${filtered.length} ${filtered.length === 1 ? "registro" : "registros"}`;
  $("#owners-body").innerHTML = filtered.map(ownerRow).join("");
  $("#owners-body").closest(".table-wrap").classList.toggle("hidden", filtered.length === 0);
  const noData = state.owners.length === 0;
  setEmptyState(
    $("#owners-empty"),
    filtered.length === 0,
    noData ? "No hay dueños registrados" : "No encontramos resultados",
    noData ? "Añade el primer dueño a la clínica." : "Prueba con otro nombre o teléfono.",
  );
}

function catalogPhotoFor(type, record) {
  if (type === "food") {
    if (record.especie === "gato") {
      return record.categoria === "humedo" ? catalogPhotos.catWetFood : catalogPhotos.catFood;
    }
    if (record.categoria === "premio") return catalogPhotos.dogTreats;
    return catalogPhotos.dogFood;
  }
  if (type === "product") {
    const productName = normalize(record.nombre);
    if (productName.includes("oido") || productName.includes("otica") || productName.includes("otico")) {
      return catalogPhotos.earDrops;
    }
    if (record.categoria === "pastilla") return catalogPhotos.pills;
    return record.categoria === "shampoo" || record.categoria === "higiene"
      ? catalogPhotos.shampoo
      : catalogPhotos.pills;
  }
  if (record.categoria === "juguete") return catalogPhotos.toy;
  if (record.categoria === "cama") return catalogPhotos.bed;
  if (record.categoria === "correa") return catalogPhotos.leash;
  return catalogPhotos.collar;
}

function catalogPhoto(type, record) {
  if (record.imagen_url) {
    return `<figure class="catalog-card-photo catalog-card-photo-uploaded">
      <img src="${escapeHtml(record.imagen_url)}" alt="Fotografía de ${escapeHtml(record.nombre)}" loading="lazy" decoding="async">
      <figcaption><span>Foto del artículo</span></figcaption>
    </figure>`;
  }
  const photo = catalogPhotoFor(type, record);
  return `<figure class="catalog-card-photo">
    <img src="${photo.path}" alt="${photo.alt}" loading="lazy" decoding="async">
    <figcaption>
      <a href="${photo.source}" target="_blank" rel="noopener noreferrer">Foto: ${photo.credit}</a>
      <a href="${photo.licenseUrl}" target="_blank" rel="noopener noreferrer">${photo.license}</a>
    </figcaption>
  </figure>`;
}

function inventoryCard(type, record) {
  const category = categoryLabels[record.categoria] ?? record.categoria;
  const active = record.activo;
  const isDraft = !active && Number(record.precio) === 0 && record.stock === 0;
  const stockClass = record.stock <= 3 ? " low" : "";
  const stockLabel = isDraft
    ? "Existencias por configurar"
    : `${record.stock} ${record.stock === 1 ? "unidad" : "unidades"}`;
  const statusLabel = isDraft ? "Borrador" : active ? "Activo" : "Inactivo";
  const priceLabel = isDraft ? "Precio por configurar" : `L ${Number(record.precio).toFixed(2)}`;
  const canManage = state.user?.rol === "administrador"
    || (type === "treatment" && state.user?.rol === "veterinario");
  const actions = canManage
    ? `<div class="catalog-card-actions"><button class="action-button" type="button" data-action="edit-${type}" data-id="${record.id}" aria-label="Editar ${escapeHtml(record.nombre)}" title="Editar">✎</button><button class="action-button delete" type="button" data-action="delete-${type}" data-id="${record.id}" aria-label="Eliminar ${escapeHtml(record.nombre)}" title="Eliminar">⌫</button></div>`
    : "";
  const foodMeta = type === "food"
    ? `<div class="catalog-card-meta"><span>${escapeHtml(speciesTargetLabels[record.especie] ?? record.especie)}</span><span>${escapeHtml(lifeStageLabels[record.etapa] ?? record.etapa)}</span></div>`
    : "";
  return `<article class="catalog-card">
    ${catalogPhoto(type, record)}
    <div class="catalog-card-content">
      <div class="catalog-card-tags"><span class="species-badge">${escapeHtml(category)}</span><span class="species-badge${active ? "" : " other"}">${statusLabel}</span></div>
      <h4>${escapeHtml(record.nombre)}</h4>
      <p class="catalog-card-description">${escapeHtml(record.descripcion)}</p>
      <div class="catalog-card-purpose"><span>¿Para qué sirve?</span><p>${escapeHtml(record.uso)}</p></div>
      ${foodMeta}
      <div class="catalog-card-footer"><div class="catalog-card-price"><strong>${priceLabel}</strong><span class="stock-badge${stockClass}">${record.stock <= 3 ? "⚑ " : ""}${escapeHtml(stockLabel)}</span></div>${actions}</div>
    </div>
  </article>`;
}

function inventoryCategorySections(type, records) {
  const grouped = new Map();
  records.forEach((record) => {
    const category = record.categoria;
    if (!grouped.has(category)) grouped.set(category, []);
    grouped.get(category).push(record);
  });

  const categoryOrder = inventoryCategoryOrder[type] ?? [];
  const categories = [...grouped.keys()].sort((left, right) => {
    const leftIndex = categoryOrder.indexOf(left);
    const rightIndex = categoryOrder.indexOf(right);
    if (leftIndex !== -1 || rightIndex !== -1) {
      return (leftIndex === -1 ? Number.MAX_SAFE_INTEGER : leftIndex)
        - (rightIndex === -1 ? Number.MAX_SAFE_INTEGER : rightIndex);
    }
    return (categoryLabels[left] ?? left).localeCompare(categoryLabels[right] ?? right, "es", { sensitivity: "base" });
  });
  const itemLabel = type === "accessory" ? "artículo" : inventoryResources[type].label;

  return categories.map((category) => {
    const categoryLabel = categoryLabels[category] ?? category;
    const categoryRecords = grouped.get(category)
      .slice()
      .sort((left, right) => left.nombre.localeCompare(right.nombre, "es", { sensitivity: "base" }));
    return `<section class="catalog-category" aria-label="Categoría ${escapeHtml(categoryLabel)}">
      <div class="catalog-category-heading">
        <h3>${escapeHtml(categoryLabel)}</h3>
        <span>${categoryRecords.length} ${categoryRecords.length === 1 ? itemLabel : `${itemLabel}s`}</span>
      </div>
      <div class="catalog-category-grid">${categoryRecords.map((record) => inventoryCard(type, record)).join("")}</div>
    </section>`;
  }).join("");
}

function renderInventory(type) {
  const resource = inventoryResources[type];
  const records = state[resource.key];
  const query = normalize($(`#${resource.key}-search`).value);
  const filtered = records.filter((record) => {
    const pet = state.pets.find((item) => item.id === record.mascota_id);
    const product = state.products.find((item) => item.id === record.producto_id);
    if (type === "treatment" && state.treatmentSpeciesFilter
      && pet?.especie !== state.treatmentSpeciesFilter) return false;
    if (type !== "treatment") {
      const category = state.inventoryCategoryFilters[type];
      if (category && record.categoria !== category) return false;
    }
    if (type === "product") {
      if (state.pharmacyLowStockOnly && (!record.activo || record.stock > 3)) return false;
    }
    return normalize([
      record.nombre, record.categoria, record.descripcion, record.uso, record.estado,
      record.especie, record.etapa, pet?.nombre, speciesLabels[pet?.especie], product?.nombre,
    ].join(" ")).includes(query);
  });
  $(`#${resource.key}-result-count`).textContent =
    `${filtered.length} ${filtered.length === 1 ? "registro" : "registros"}`;
  if (type !== "treatment") {
    const body = $(`#${resource.key}-body`);
    body.innerHTML = inventoryCategorySections(type, filtered);
    body.closest(".table-wrap").classList.toggle("hidden", filtered.length === 0);
    setEmptyState(
      $(`#${resource.key}-empty`),
      filtered.length === 0,
      records.length === 0
        ? `No hay ${resource.label}${resource.label.endsWith("s") ? "" : "s"} registrados`
        : "No encontramos resultados",
      records.length === 0
        ? `Añade el primer ${resource.label} al inventario.`
        : "Prueba con otra búsqueda o ajusta los filtros.",
    );
    return;
  }
  const rows = filtered.map((record) => {
    const canManage = state.user?.rol === "administrador"
      || (type === "treatment" && state.user?.rol === "veterinario");
    const actions = canManage
      ? `<td><div class="row-actions"><button class="action-button" type="button" data-action="edit-${type}" data-id="${record.id}" aria-label="Editar ${escapeHtml(record.nombre)}" title="Editar">✎</button><button class="action-button delete" type="button" data-action="delete-${type}" data-id="${record.id}" aria-label="Eliminar ${escapeHtml(record.nombre)}" title="Eliminar">⌫</button></div></td>`
      : "<td>—</td>";
    if (type === "treatment") {
      const pet = state.pets.find((item) => item.id === record.mascota_id);
      const product = state.products.find((item) => item.id === record.producto_id);
      const species = pet?.especie;
      const speciesClass = species === "perro" ? "" : speciesStyleClasses[species] ?? "other";
      return `<tr><td><div class="pet-name">${escapeHtml(record.nombre)}</div><div class="pet-id">${escapeHtml(record.indicaciones)}</div></td><td>${escapeHtml(pet?.nombre ?? "Mascota no encontrada")}</td><td><span class="species-badge ${speciesClass}">${escapeHtml(speciesLabels[species] ?? "No disponible")}</span></td><td>${escapeHtml(product?.nombre ?? "Sin producto")}</td><td>${formatDate(record.fecha_inicio)}</td><td><span class="species-badge">${escapeHtml(treatmentStatusLabels[record.estado] ?? record.estado)}</span></td>${actions}</tr>`;
    }
    const stock = `<span class="stock-badge${record.stock <= 3 ? " low" : ""}">${record.stock <= 3 ? "⚑ " : ""}${record.stock} ${record.stock === 1 ? "unidad" : "unidades"}</span>`;
    if (type === "food") {
      return `<tr><td><div class="pet-name">${escapeHtml(record.nombre)}</div><div class="pet-id">${escapeHtml(record.descripcion || "Alimentación para mascotas")}</div></td><td><span class="species-badge">${escapeHtml(categoryLabels[record.categoria] ?? record.categoria)}</span></td><td>${escapeHtml(speciesTargetLabels[record.especie] ?? record.especie)}</td><td>${escapeHtml(lifeStageLabels[record.etapa] ?? record.etapa)}</td><td>L ${Number(record.precio).toFixed(2)}</td><td>${stock}</td><td><span class="species-badge${record.activo ? "" : " other"}">${record.activo ? "Activo" : "Inactivo"}</span></td>${actions}</tr>`;
    }
    return `<tr><td><div class="pet-name">${escapeHtml(record.nombre)}</div><div class="pet-id">${escapeHtml(record.descripcion || "Sin descripción")}</div></td><td>${escapeHtml(categoryLabels[record.categoria] ?? record.categoria)}</td><td>L ${Number(record.precio).toFixed(2)}</td><td>${stock}</td><td><span class="species-badge${record.activo ? "" : " other"}">${record.activo ? "Activo" : "Inactivo"}</span></td>${actions}</tr>`;
  }).join("");
  $(`#${resource.key}-body`).innerHTML = rows;
  $(`#${resource.key}-body`).closest(".table-wrap").classList.toggle("hidden", filtered.length === 0);
  setEmptyState(
    $(`#${resource.key}-empty`),
    filtered.length === 0,
    records.length === 0
      ? type === "treatment"
        ? "No hay tratamientos registrados"
        : `No hay ${resource.label}${resource.label.endsWith("s") ? "" : "s"} registrados`
      : "No encontramos resultados",
    records.length === 0
      ? type === "treatment"
        ? "Registra el primer tratamiento indicado para una mascota."
        : `Añade el primer ${resource.label} al inventario.`
      : "Prueba con otra búsqueda o ajusta los filtros.",
  );
}

function render() {
  renderStats();
  renderPharmacyStats();
  renderDashboard();
  renderPets();
  renderOwners();
  Object.keys(inventoryResources).forEach(renderInventory);
  renderAppointments();
  renderVaccines();
  renderLots();
  renderReports();
}

function renderAppointments() {
  if (!$("#appointment-form").elements.fecha_hora.value) {
    $("#appointment-form").elements.fecha_hora.value = localDateTimeValue();
  }
  if (!$("#vaccine-form").elements.fecha.value) {
    $("#vaccine-form").elements.fecha.value = localDateValue();
  }
  const pets = state.pets.map((pet) =>
    `<option value="${pet.id}">${escapeHtml(pet.nombre)} · ${escapeHtml(speciesLabels[pet.especie] ?? "Otro")}</option>`,
  ).join("");
  $("#appointment-pet").innerHTML = `<option value="">Selecciona una mascota</option>${pets}`;
  $("#vaccine-pet").innerHTML = `<option value="">Selecciona una mascota</option>${pets}`;
  $("#appointment-vet").innerHTML = `<option value="">Selecciona un veterinario</option>${
    state.veterinarians.map((vet) =>
      `<option value="${vet.id}">${escapeHtml(vet.nombre)}</option>`,
    ).join("")
  }`;
  const canDelete = state.user?.rol === "administrador";
  $("#appointments-body").innerHTML = state.appointments.map((appointment) => {
    const actions = appointment.estado === "programada"
      ? `<button class="action-button" type="button" data-action="complete-appointment" data-id="${appointment.id}" title="Marcar como atendida" aria-label="Marcar cita como atendida">✓</button><button class="action-button" type="button" data-action="cancel-appointment" data-id="${appointment.id}" title="Cancelar cita" aria-label="Cancelar cita">×</button>`
      : "";
    const remove = canDelete
      ? `<button class="action-button delete" type="button" data-action="delete-appointment" data-id="${appointment.id}" title="Eliminar cita" aria-label="Eliminar cita">⌫</button>`
      : "";
    return `<tr><td>${formatDateTime(appointment.fecha_hora)}</td><td>${escapeHtml(appointment.mascota)}</td><td>${escapeHtml(appointment.veterinario)}</td><td>${escapeHtml(appointment.motivo)}</td><td><span class="species-badge">${escapeHtml(appointment.estado)}</span></td><td><div class="row-actions">${actions}${remove}</div></td></tr>`;
  }).join("");
  setEmptyState($("#appointments-empty"), state.appointments.length === 0);
}

function renderVaccines() {
  const today = localDateValue();
  $("#vaccines-body").innerHTML = state.vaccines.map((vaccine) => {
    const upcoming = vaccine.proxima_dosis && vaccine.proxima_dosis >= today;
    const actions = state.user?.rol === "administrador" || state.user?.rol === "veterinario"
      ? `<button class="action-button delete" type="button" data-action="delete-vaccine" data-id="${vaccine.id}" title="Eliminar vacuna" aria-label="Eliminar vacuna de ${escapeHtml(vaccine.mascota)}">⌫</button>`
      : "—";
    return `<tr><td>${escapeHtml(vaccine.mascota)}</td><td>${escapeHtml(vaccine.vacuna)}</td><td>${formatDate(vaccine.fecha)}</td><td><span class="species-badge${upcoming ? " low" : ""}">${formatDate(vaccine.proxima_dosis)}</span></td><td><div class="row-actions">${actions}</div></td></tr>`;
  }).join("");
  setEmptyState($("#vaccines-empty"), state.vaccines.length === 0);
}

function renderLots() {
  const today = localDateValue();
  const limit = new Date();
  limit.setDate(limit.getDate() + 90);
  const limitValue = `${limit.getFullYear()}-${String(limit.getMonth() + 1).padStart(2, "0")}-${String(limit.getDate()).padStart(2, "0")}`;
  $("#lot-product").innerHTML = `<option value="">Selecciona un producto</option>${
    state.products.map((product) =>
      `<option value="${product.id}">${escapeHtml(product.nombre)}</option>`,
    ).join("")
  }`;
  $("#lots-body").innerHTML = state.lots.map((lot) => {
    const warning = lot.vencimiento <= limitValue;
    const status = lot.vencimiento < today ? "Vencido" : warning ? "Por vencer" : "Vigente";
    const actions = state.user?.rol === "administrador"
      ? `<button class="action-button delete" type="button" data-action="delete-lot" data-id="${lot.id}" title="Eliminar lote" aria-label="Eliminar lote ${escapeHtml(lot.numero_lote)}">⌫</button>`
      : "—";
    return `<tr><td>${escapeHtml(lot.producto)}</td><td>${escapeHtml(lot.numero_lote)}</td><td>${escapeHtml(lot.proveedor || "Sin proveedor")}</td><td><span class="species-badge${warning ? " low" : ""}">${formatDate(lot.vencimiento)} · ${status}</span></td><td>${lot.stock}</td><td><div class="row-actions">${actions}</div></td></tr>`;
  }).join("");
  setEmptyState($("#lots-empty"), state.lots.length === 0);
}

function renderReports() {
  const report = state.report;
  $("#report-appointments").textContent = report.citas_programadas ?? "—";
  $("#report-vaccines").textContent = report.vacunas_proximas ?? "—";
  $("#report-expiring").textContent = report.lotes_por_vencer ?? "—";
  $("#report-low-stock").textContent = report.productos_stock_bajo ?? "—";
  $("#report-inventory-value").textContent = report.valor_inventario === undefined
    ? "—"
    : `L ${Number(report.valor_inventario).toFixed(2)}`;
  const roleOptions = [["administrador", "Administración"], ["veterinario", "Veterinario"], ["recepcion", "Recepción"]];
  $("#users-body").innerHTML = state.users.map((user) => {
    const isCurrentUser = user.id === state.user?.id;
    const options = roleOptions.map(([value, label]) =>
      `<option value="${value}" ${user.rol === value ? "selected" : ""}>${label}</option>`,
    ).join("");
    return `<tr><td>${escapeHtml(user.nombre_usuario)}</td><td>${escapeHtml(user.nombre_completo)}</td><td>${escapeHtml(user.correo)}</td><td><select data-action="change-user-role" data-id="${user.id}" aria-label="Perfil de ${escapeHtml(user.nombre_usuario)}" ${isCurrentUser ? "disabled" : ""}>${options}</select></td><td>${user.activo ? "Activo" : "Inactivo"}</td><td><button class="action-button${user.activo ? " delete" : ""}" type="button" data-action="toggle-user" data-id="${user.id}" data-active="${user.activo}" ${isCurrentUser ? "disabled" : ""} aria-label="${user.activo ? "Desactivar" : "Activar"} a ${escapeHtml(user.nombre_usuario)}">${user.activo ? "Desactivar" : "Activar"}</button></td></tr>`;
  }).join("");
}

function renderPharmacyStats() {
  const active = state.products.filter((product) => product.activo);
  $("#pharmacy-total-stat").textContent = state.products.length;
  $("#pharmacy-low-stat").textContent = active.filter((product) => product.stock <= 3).length;
  $("#pharmacy-active-stat").textContent = active.length;
  $("#products-low-filter").setAttribute("aria-pressed", String(state.pharmacyLowStockOnly));
}

async function loadData(showMessage = false) {
  try {
    const [owners, pets, accessories, products, foods, treatments, appointments,
      vaccines, veterinarians, lots, report, users] = await Promise.all([
      api("/duenos/"),
      api("/mascotas/"),
      api("/accesorios/"),
      api("/productos-veterinarios/"),
      api("/alimentos/"),
      api("/tratamientos/"),
      api("/citas/"),
      api("/vacunas/"),
      api("/veterinarios/"),
      api("/lotes-farmacia/"),
      api("/reportes/resumen"),
      state.user?.rol === "administrador" ? api("/auth/usuarios") : Promise.resolve([]),
    ]);
    state.owners = owners;
    state.pets = pets;
    state.accessories = accessories;
    state.products = products;
    state.foods = foods;
    state.treatments = treatments;
    state.appointments = appointments;
    state.vaccines = vaccines;
    state.veterinarians = veterinarians;
    state.lots = lots;
    state.report = report;
    state.users = users;
    render();
    if (showMessage) toast("Datos actualizados correctamente.");
  } catch (error) {
    toast(`No se pudieron cargar los datos: ${error.message}`, "error");
    $("#owner-stat").textContent = "!";
    $("#pet-stat").textContent = "!";
  }
}

function actualizarPerfil(user) {
  state.user = user;
  const roles = {
    administrador: "Administración",
    veterinario: "Veterinario",
    recepcion: "Recepción",
  };
  $("#profile-name").textContent = user.nombre_completo;
  $("#profile-role").textContent = roles[user.rol] ?? user.rol;
  $(".profile .avatar").textContent = initials(user.nombre_completo);
  $("#assistant-launcher").classList.remove("hidden");
  const isAdmin = user.rol === "administrador";
  const isVeterinarian = user.rol === "veterinario" || isAdmin;
  document.querySelectorAll(".admin-only").forEach((element) => {
    element.classList.toggle("hidden", !isAdmin);
  });
  document.querySelectorAll(".veterinarian-only").forEach((element) => {
    element.classList.toggle("hidden", !isVeterinarian);
  });
  $("#add-treatment-button").classList.toggle("hidden", !isVeterinarian);
}

async function mostrarSistema(user) {
  actualizarPerfil(user);
  $("#login-error").classList.add("hidden");
  $("#login-gate").classList.add("hidden");
  $("#app-shell").classList.remove("hidden");
  await loadData();
}

$("#login-form").addEventListener("submit", async (event) => {
  event.preventDefault();
  const form = event.currentTarget;
  const submit = $("#login-submit");
  const error = $("#login-error");
  submit.disabled = true;
  submit.textContent = "Verificando…";
  error.classList.add("hidden");
  try {
    const user = await api("/auth/login", {
      method: "POST",
      body: JSON.stringify(Object.fromEntries(new FormData(form).entries())),
    });
    form.reset();
    await mostrarSistema(user);
  } catch (loginError) {
    error.textContent = loginError.message;
    error.classList.remove("hidden");
  } finally {
    submit.disabled = false;
    submit.textContent = "Iniciar sesión";
  }
});

$("#logout-button").addEventListener("click", async () => {
  try {
    await api("/auth/logout", { method: "POST" });
    state.user = null;
    $("#app-shell").classList.add("hidden");
    $("#login-gate").classList.remove("hidden");
    $("#assistant-launcher").classList.add("hidden");
    $("#assistant-panel").classList.add("hidden");
    $("#login-username").focus();
  } catch (error) {
    toast(`No se pudo cerrar la sesión: ${error.message}`, "error");
  }
});

function enviarFormulario(form, endpoint, transform = (data) => data) {
  return async (event) => {
    event.preventDefault();
    if (!form.reportValidity()) return;
    const button = form.querySelector('button[type="submit"]');
    const originalText = button.textContent;
    button.disabled = true;
    button.textContent = "Guardando…";
    try {
      const data = transform(Object.fromEntries(new FormData(form).entries()));
      await api(endpoint, { method: "POST", body: JSON.stringify(data) });
      form.reset();
      await loadData();
      toast("Registro guardado correctamente.");
    } catch (error) {
      toast(`No se pudo guardar: ${error.message}`, "error");
    } finally {
      button.disabled = false;
      button.textContent = originalText;
    }
  };
}

$("#appointment-form").addEventListener("submit", enviarFormulario(
  $("#appointment-form"),
  "/citas/",
  (data) => ({
    ...data,
    mascota_id: Number(data.mascota_id),
    veterinario_id: Number(data.veterinario_id),
  }),
));

$("#vaccine-form").addEventListener("submit", enviarFormulario(
  $("#vaccine-form"),
  "/vacunas/",
  (data) => ({
    ...data,
    mascota_id: Number(data.mascota_id),
    proxima_dosis: data.proxima_dosis || null,
  }),
));

$("#lot-form").addEventListener("submit", enviarFormulario(
  $("#lot-form"),
  "/lotes-farmacia/",
  (data) => ({
    ...data,
    producto_id: Number(data.producto_id),
    proveedor: data.proveedor || null,
    stock: Number(data.stock),
  }),
));

$("#user-form").addEventListener("submit", enviarFormulario(
  $("#user-form"),
  "/auth/usuarios",
));

$("#users-body").addEventListener("change", async (event) => {
  const select = event.target.closest('[data-action="change-user-role"]');
  if (!select) return;
  const account = state.users.find((item) => item.id === Number(select.dataset.id));
  if (!account) return;
  try {
    await api(`/auth/usuarios/${account.id}`, {
      method: "PUT",
      body: JSON.stringify({ rol: select.value, activo: Boolean(account.activo) }),
    });
    await loadData();
    toast("Perfil actualizado correctamente.");
  } catch (error) {
    toast(`No se pudo actualizar el perfil: ${error.message}`, "error");
    renderReports();
  }
});

$("#password-form").addEventListener("submit", async (event) => {
  event.preventDefault();
  const form = event.currentTarget;
  if (!form.reportValidity()) return;
  const data = Object.fromEntries(new FormData(form).entries());
  try {
    await api("/auth/password", { method: "POST", body: JSON.stringify(data) });
    form.reset();
    state.user = null;
    $("#app-shell").classList.add("hidden");
    $("#login-gate").classList.remove("hidden");
    $("#assistant-launcher").classList.add("hidden");
    $("#assistant-panel").classList.add("hidden");
    toast("Contraseña actualizada. Inicia sesión con tu nueva contraseña.");
  } catch (error) {
    toast(`No se pudo cambiar la contraseña: ${error.message}`, "error");
  }
});

$("#backup-button").addEventListener("click", async (event) => {
  const button = event.currentTarget;
  button.disabled = true;
  try {
    const response = await fetch("/respaldos/", { method: "POST" });
    if (!response.ok) {
      const result = await response.json();
      throw new Error(result.detail || `Error del servidor (${response.status}).`);
    }
    const blob = await response.blob();
    const url = URL.createObjectURL(blob);
    const download = document.createElement("a");
    download.href = url;
    download.download = response.headers.get("content-disposition")
      ?.match(/filename="([^"]+)"/)?.[1] ?? "zeus-vet-respaldo.db";
    download.click();
    URL.revokeObjectURL(url);
    toast("Copia de seguridad descargada.");
  } catch (error) {
    toast(`No se pudo crear la copia: ${error.message}`, "error");
  } finally {
    button.disabled = false;
  }
});

$("#appointments-body").addEventListener("click", async (event) => {
  const button = event.target.closest("[data-action]");
  if (!button) return;
  const appointment = state.appointments.find((item) => item.id === Number(button.dataset.id));
  if (!appointment) return;
  if (button.dataset.action === "delete-appointment") {
    if (!window.confirm("¿Seguro que deseas eliminar esta cita?")) return;
    try {
      await api(`/citas/${appointment.id}`, { method: "DELETE" });
      await loadData();
    } catch (error) {
      toast(`No se pudo eliminar la cita: ${error.message}`, "error");
    }
    return;
  }
  const estado = button.dataset.action === "complete-appointment" ? "atendida" : "cancelada";
  try {
    await api(`/citas/${appointment.id}`, {
      method: "PUT",
      body: JSON.stringify({
        mascota_id: appointment.mascota_id,
        veterinario_id: appointment.veterinario_id,
        fecha_hora: appointment.fecha_hora,
        motivo: appointment.motivo,
        estado,
      }),
    });
    await loadData();
  } catch (error) {
    toast(`No se pudo actualizar la cita: ${error.message}`, "error");
  }
});

document.addEventListener("click", async (event) => {
  const button = event.target.closest(
    '[data-action="delete-vaccine"], [data-action="delete-lot"], [data-action="toggle-user"]',
  );
  if (!button) return;
  if (button.dataset.action === "toggle-user") {
    const account = state.users.find((item) => item.id === Number(button.dataset.id));
    if (!account) return;
    const active = !account.activo;
    if (!active && !window.confirm(`¿Desactivar la cuenta ${account.nombre_usuario}?`)) return;
    try {
      await api(`/auth/usuarios/${account.id}`, {
        method: "PUT",
        body: JSON.stringify({ rol: account.rol, activo: active }),
      });
      await loadData();
      toast(`Cuenta ${active ? "activada" : "desactivada"} correctamente.`);
    } catch (error) {
      toast(`No se pudo actualizar la cuenta: ${error.message}`, "error");
    }
    return;
  }
  const isVaccine = button.dataset.action === "delete-vaccine";
  if (!window.confirm(`¿Seguro que deseas eliminar este ${isVaccine ? "registro de vacuna" : "lote"}?`)) return;
  try {
    await api(`${isVaccine ? "/vacunas/" : "/lotes-farmacia/"}${button.dataset.id}`, {
      method: "DELETE",
    });
    await loadData();
  } catch (error) {
    toast(`No se pudo eliminar: ${error.message}`, "error");
  }
});

function field(label, name, type, value = "", options = {}) {
  const id = `field-${name}`;
  const required = options.required ? "required" : "";
  const hint = options.hint ? `<span class="field-hint">${escapeHtml(options.hint)}</span>` : "";
  let control;
  if (type === "select") {
    const choices = options.choices.map(([choice, title]) =>
      `<option value="${escapeHtml(choice)}" ${String(value) === String(choice) ? "selected" : ""}>${escapeHtml(title)}</option>`,
    ).join("");
    control = `<select id="${id}" name="${name}" ${required}>${choices}</select>`;
  } else if (type === "textarea") {
    control = `<textarea id="${id}" name="${name}" ${required} ${options.maxLength ? `maxlength="${options.maxLength}"` : ""} ${options.minLength ? `minlength="${options.minLength}"` : ""} ${options.placeholder ? `placeholder="${escapeHtml(options.placeholder)}"` : ""}>${escapeHtml(value)}</textarea>`;
  } else {
    control = `<input id="${id}" name="${name}" type="${type}" value="${escapeHtml(value)}" ${required} ${options.maxLength ? `maxlength="${options.maxLength}"` : ""} ${options.minLength ? `minlength="${options.minLength}"` : ""} ${options.min !== undefined ? `min="${options.min}"` : ""} ${options.step ? `step="${options.step}"` : ""} ${options.placeholder ? `placeholder="${escapeHtml(options.placeholder)}"` : ""}>`;
  }
  return `<div class="form-field"><label for="${id}">${escapeHtml(label)}${options.required ? " *" : ""}</label>${control}${hint}</div>`;
}

function imageField(record, label) {
  const preview = record?.imagen_url
    ? `<img src="${escapeHtml(record.imagen_url)}" alt="Foto actual ${escapeHtml(label)}">`
    : "<span>La foto aparecerá aquí</span>";
  return `<div class="form-field form-field-wide image-upload-field">
    <label for="field-imagen">Foto ${escapeHtml(label)} (opcional)</label>
    <input id="field-imagen" name="imagen" type="file" accept="image/jpeg,image/png,image/webp">
    <input type="hidden" name="imagen_url" value="${escapeHtml(record?.imagen_url ?? "")}">
    <span class="field-hint">JPG, PNG o WebP · Máximo 5 MB</span>
    <div class="image-upload-preview" id="image-upload-preview">${preview}</div>
  </div>`;
}

const dialogContext = { entity: "pet", id: null };

function openDialog(entity, record = null) {
  dialogContext.entity = entity;
  dialogContext.id = record?.id ?? null;
  const editing = Boolean(record);
  const ownerEntity = entity === "owner";
  const petEntity = entity === "pet";
  const resource = inventoryResources[entity];
  const entityTitle = ownerEntity ? "dueño" : petEntity ? "mascota" : resource.label;
  const title = `${editing ? "Editar" : entity === "owner" || entity === "pet" ? "Registrar" : "Añadir"} ${entityTitle}`;
  $("#dialog-eyebrow").textContent = editing ? "ACTUALIZAR REGISTRO" : "NUEVO REGISTRO";
  $("#dialog-title").textContent = title;
  $("#dialog-description").textContent = ownerEntity
    ? "Información de contacto de la persona responsable."
    : petEntity
      ? "Completa los datos del paciente y selecciona a su dueño."
      : entity === "treatment"
        ? "Asocia el tratamiento con una mascota y, si corresponde, un producto veterinario."
        : "Completa la información del artículo, incluido para qué sirve y cómo se describe.";
  $("#dialog-submit").textContent = editing ? "Guardar cambios" : "Guardar registro";
  const categoryChoices = entity === "accessory"
    ? [["collar", "Collar"], ["correa", "Correa"], ["juguete", "Juguete"], ["ropa", "Ropa"], ["cama", "Cama"], ["transporte", "Transporte"], ["otro", "Otro"]]
    : entity === "food"
      ? [["concentrado", "Concentrado"], ["humedo", "Alimento húmedo"], ["premio", "Premio"], ["suplemento", "Suplemento"], ["dieta_especial", "Dieta especial"]]
      : [["medicamento", "Medicamento"], ["pastilla", "Pastilla"], ["shampoo", "Shampoo"], ["higiene", "Higiene"], ["otro", "Otro"]];
  const fields = ownerEntity
    ? [
        field("Nombre completo", "nombre", "text", record?.nombre ?? "", { required: true, minLength: 1, maxLength: 120, placeholder: "Ej. Ana Rivera" }),
        field("Teléfono", "telefono", "tel", record?.telefono ?? "", { required: true, minLength: 8, maxLength: 30, placeholder: "Ej. +504 9876-1234" }),
        field("Dirección", "direccion", "text", record?.direccion ?? "", { maxLength: 200, placeholder: "Barrio o colonia" }),
      ].join("")
    : petEntity
      ? [
        field("Nombre de la mascota", "nombre", "text", record?.nombre ?? "", { required: true, minLength: 1, maxLength: 100, placeholder: "Ej. Luna" }),
        field("Especie", "especie", "select", record?.especie ?? "perro", { required: true, choices: [["perro", "Perro"], ["gato", "Gato"], ["ave", "Ave"], ["gallina", "Gallina"], ["caballo", "Caballo"], ["vaca", "Vaca"], ["otro", "Otro"]] }),
        field("Raza", "raza", "text", record?.raza ?? "", { maxLength: 100, placeholder: "Ej. Labrador" }),
        field("Fecha de nacimiento", "fecha_nacimiento", "date", record?.fecha_nacimiento ?? ""),
        imageField(record, `de la mascota ${record?.nombre ?? ""}`.trim()),
        field("Dueño", "dueno_id", "select", record?.dueno_id ?? "", {
          required: true,
          choices: [["", "Selecciona un dueño"], ...state.owners.map((owner) => [owner.id, owner.nombre])],
          hint: state.owners.length ? "" : "Primero registra un dueño para asociar la mascota.",
        }),
      ].join("")
      : entity === "treatment"
        ? [
            field("Nombre del tratamiento", "nombre", "text", record?.nombre ?? "", { required: true, maxLength: 120 }),
            field("Mascota", "mascota_id", "select", record?.mascota_id ?? "", {
              required: true,
              choices: [["", "Selecciona una mascota"], ...state.pets.map((pet) => [pet.id, `${pet.nombre} (${speciesLabels[pet.especie] ?? "Otro"})`])],
              hint: state.pets.length ? "" : "Registra una mascota antes de añadir tratamientos.",
            }),
            field("Producto veterinario", "producto_id", "select", record?.producto_id ?? "", {
              choices: [["", "Sin producto asociado"], ...state.products.map((product) => [product.id, `${product.nombre} (${categoryLabels[product.categoria] ?? product.categoria})`])],
              hint: "Opcional. Registrar el tratamiento no modifica las existencias.",
            }),
            field("Indicaciones", "indicaciones", "text", record?.indicaciones ?? "", { required: true, maxLength: 1000 }),
            field("Dosis", "dosis", "text", record?.dosis ?? "", { maxLength: 200 }),
            field("Fecha de inicio", "fecha_inicio", "date", record?.fecha_inicio ?? new Date().toISOString().slice(0, 10), { required: true }),
            field("Fecha de finalización", "fecha_fin", "date", record?.fecha_fin ?? ""),
            field("Estado", "estado", "select", record?.estado ?? "recetado", { required: true, choices: [["recetado", "Recetado"], ["en_curso", "En curso"], ["completado", "Completado"], ["suspendido", "Suspendido"]] }),
          ].join("")
        : [
            field("Nombre", "nombre", "text", record?.nombre ?? "", { required: true, maxLength: 120, placeholder: entity === "accessory" ? "Ej. Collar ajustable" : entity === "food" ? "Ej. Concentrado para cachorro" : "Ej. Shampoo hipoalergénico" }),
            field("Categoría", "categoria", "select", record?.categoria ?? categoryChoices[0][0], { required: true, choices: categoryChoices }),
            ...(entity === "food" ? [
              field("Especie recomendada", "especie", "select", record?.especie ?? "universal", { required: true, choices: [["universal", "Todas las especies"], ["perro", "Perro"], ["gato", "Gato"], ["ave", "Ave"]] }),
              field("Etapa de vida", "etapa", "select", record?.etapa ?? "todas", { required: true, choices: [["todas", "Todas las etapas"], ["cachorro", "Cachorro"], ["adulto", "Adulto"], ["senior", "Senior"]] }),
            ] : []),
            field("Descripción", "descripcion", "textarea", record?.descripcion ?? "", { required: true, minLength: 1, maxLength: 500, placeholder: "Describe el artículo, sus materiales o características." }),
            field("¿Para qué sirve?", "uso", "textarea", record?.uso ?? "", {
              required: true,
              minLength: 1,
              maxLength: 500,
              placeholder: entity === "product"
                ? "Describe el uso indicado en la etiqueta del producto."
                : entity === "food"
                  ? "Indica para qué tipo de alimentación está pensado."
                  : "Explica para qué se utiliza el artículo.",
              hint: entity === "product" ? "Los medicamentos deben usarse únicamente según la etiqueta y la indicación veterinaria." : "",
            }),
            field("Precio (L)", "precio", "number", record?.precio ?? "", { required: true, min: 0, step: "0.01" }),
            field("Existencias", "stock", "number", record?.stock ?? 0, { required: true, min: 0, step: "1" }),
            field("Estado", "activo", "select", record?.activo ?? true, { required: true, choices: [["true", "Activo"], ["false", "Inactivo"]] }),
            imageField(record, `del artículo ${record?.nombre ?? ""}`.trim()),
          ].join("");
  $("#dialog-fields").innerHTML = fields;
  $("#record-form").dataset.entity = entity;
  const imageInput = $("#field-imagen");
  if (imageInput) {
    imageInput.addEventListener("change", () => {
      const file = imageInput.files[0];
      if (!file) return;
      if (file.size > 5 * 1024 * 1024) {
        imageInput.value = "";
        toast("La imagen no puede superar los 5 MB.", "error");
        return;
      }
      if (!["image/jpeg", "image/png", "image/webp"].includes(file.type)) {
        imageInput.value = "";
        toast("Selecciona una imagen JPG, PNG o WebP.", "error");
        return;
      }
      const previewUrl = URL.createObjectURL(file);
      const preview = $("#image-upload-preview");
      preview.innerHTML = `<img src="${previewUrl}" alt="Vista previa de la imagen seleccionada">`;
      preview.querySelector("img").addEventListener("load", () => URL.revokeObjectURL(previewUrl), { once: true });
    });
  }
  $("#form-dialog").showModal();
  $("#dialog-fields input, #dialog-fields select")?.focus();
}

async function submitForm(event) {
  event.preventDefault();
  const form = event.currentTarget;
  if (!form.reportValidity()) return;
  const data = Object.fromEntries(new FormData(form).entries());
  const imageFile = form.elements.namedItem("imagen")?.files[0];
  delete data.imagen;
  if ("imagen_url" in data && !data.imagen_url) data.imagen_url = null;
  if (dialogContext.entity === "owner" && !data.direccion) data.direccion = null;
  if (dialogContext.entity === "pet") {
    data.dueno_id = Number(data.dueno_id);
    if (!data.raza) data.raza = null;
    if (!data.fecha_nacimiento) data.fecha_nacimiento = null;
  }
  if (dialogContext.entity === "accessory" || dialogContext.entity === "product" || dialogContext.entity === "food") {
    data.precio = Number(data.precio);
    data.stock = Number(data.stock);
    data.activo = data.activo === "true";
  }
  if (dialogContext.entity === "treatment") {
    data.mascota_id = Number(data.mascota_id);
    data.producto_id = data.producto_id ? Number(data.producto_id) : null;
    if (!data.dosis) data.dosis = null;
    if (!data.fecha_fin) data.fecha_fin = null;
  }
  const resource = inventoryResources[dialogContext.entity];
  const entityName = dialogContext.entity === "owner"
    ? "dueño"
    : dialogContext.entity === "pet"
      ? "mascota"
      : resource.label;
  const collection = dialogContext.entity === "owner"
    ? "/duenos/"
    : dialogContext.entity === "pet"
      ? "/mascotas/"
      : resource.collection;
  const path = dialogContext.id ? `${collection}${dialogContext.id}` : collection;
  const method = dialogContext.id ? "PUT" : "POST";
  const button = $("#dialog-submit");
  button.disabled = true;
  button.textContent = "Guardando…";
  try {
    if (imageFile) {
      const uploadedImage = await api("/imagenes/", {
        method: "POST",
        body: imageFile,
        headers: { "Content-Type": imageFile.type },
      });
      data.imagen_url = uploadedImage.imagen_url;
    }
    await api(path, { method, body: JSON.stringify(data) });
    $("#form-dialog").close();
    await loadData();
    toast(`${entityName[0].toUpperCase()}${entityName.slice(1)} ${dialogContext.id ? "actualizado" : "registrado"} correctamente.`);
  } catch (error) {
    toast(error.message, "error");
  } finally {
    button.disabled = false;
    button.textContent = dialogContext.id ? "Guardar cambios" : "Guardar registro";
  }
}

async function deleteRecord(entity, id) {
  const isOwner = entity === "owner";
  const isPet = entity === "pet";
  const resource = inventoryResources[entity];
  const records = isOwner ? state.owners : isPet ? state.pets : state[resource.key];
  const record = records.find((item) => item.id === id);
  if (!record) return;
  const type = isOwner ? "dueño" : isPet ? "mascota" : resource.label;
  if (!window.confirm(`¿Seguro que deseas eliminar a ${record.nombre}?`)) return;
  try {
    const collection = isOwner ? "/duenos/" : isPet ? "/mascotas/" : resource.collection;
    await api(`${collection}${id}`, { method: "DELETE" });
    await loadData();
    toast(`${type[0].toUpperCase()}${type.slice(1)} eliminado correctamente.`);
  } catch (error) {
    toast(`No se pudo eliminar: ${error.message}`, "error");
  }
}

document.querySelectorAll(".nav-item").forEach((button) => {
  button.addEventListener("click", () => showView(button.dataset.view));
});
document.querySelectorAll("[data-go]").forEach((button) => {
  button.addEventListener("click", () => showView(button.dataset.go));
});
$("#dashboard-add-pet").addEventListener("click", () => {
  if (!state.owners.length) {
    toast("Primero registra un dueño para asociar la mascota.", "error");
    showView("owners");
    openDialog("owner");
    return;
  }
  openDialog("pet");
});
$("#add-pet-button").addEventListener("click", () => {
  if (!state.owners.length) {
    toast("Primero registra un dueño para asociar la mascota.", "error");
    showView("owners");
    openDialog("owner");
    return;
  }
  openDialog("pet");
});
$("#add-owner-button").addEventListener("click", () => openDialog("owner"));
$("#add-accessory-button").addEventListener("click", () => openDialog("accessory"));
$("#add-product-button").addEventListener("click", () => openDialog("product"));
$("#add-food-button").addEventListener("click", () => openDialog("food"));
$("#add-treatment-button").addEventListener("click", () => {
  if (!state.pets.length) {
    toast("Primero registra una mascota para asociar el tratamiento.", "error");
    showView("pets");
    return;
  }
  openDialog("treatment");
});
$("#empty-add-pet").addEventListener("click", () => $("#add-pet-button").click());
$("#refresh-button").addEventListener("click", () => loadData(true));
$("#pets-search").addEventListener("input", renderPets);
$("#owners-search").addEventListener("input", renderOwners);
$("#treatment-species-filter").addEventListener("change", () => renderInventory("treatment"));
for (const type of ["accessory", "product", "food"]) {
  const resource = inventoryResources[type];
  $(`#${resource.key}-category-filter`).addEventListener("change", (event) => {
    state.inventoryCategoryFilters[type] = event.target.value;
    renderInventory(type);
  });
}
$("#products-low-filter").addEventListener("click", () => {
  state.pharmacyLowStockOnly = !state.pharmacyLowStockOnly;
  renderInventory("product");
  renderPharmacyStats();
});
for (const resource of Object.values(inventoryResources)) {
  $(`#${resource.key}-search`).addEventListener("input", () => renderInventory(
    Object.keys(inventoryResources).find((key) => inventoryResources[key] === resource),
  ));
}
$("#record-form").addEventListener("submit", submitForm);
$("#dialog-close").addEventListener("click", () => $("#form-dialog").close());
$("#dialog-cancel").addEventListener("click", () => $("#form-dialog").close());
$("#form-dialog").addEventListener("click", (event) => {
  if (event.target === $("#form-dialog")) $("#form-dialog").close();
});
document.addEventListener("click", (event) => {
  const button = event.target.closest("[data-action]");
  if (!button) return;
  const id = Number(button.dataset.id);
  switch (button.dataset.action) {
    case "edit-owner":
      openDialog("owner", state.owners.find((owner) => owner.id === id));
      break;
    case "delete-owner":
      deleteRecord("owner", id);
      break;
    case "edit-pet":
      openDialog("pet", state.pets.find((pet) => pet.id === id));
      break;
    case "delete-pet":
      deleteRecord("pet", id);
      break;
    case "edit-accessory":
      openDialog("accessory", state.accessories.find((item) => item.id === id));
      break;
    case "delete-accessory":
      deleteRecord("accessory", id);
      break;
    case "edit-product":
      openDialog("product", state.products.find((item) => item.id === id));
      break;
    case "delete-product":
      deleteRecord("product", id);
      break;
    case "edit-food":
      openDialog("food", state.foods.find((item) => item.id === id));
      break;
    case "delete-food":
      deleteRecord("food", id);
      break;
    case "edit-treatment":
      openDialog("treatment", state.treatments.find((item) => item.id === id));
      break;
    case "delete-treatment":
      deleteRecord("treatment", id);
      break;
  }
});

function addAssistantMessage(text, sender) {
  const message = document.createElement("div");
  message.className = `assistant-message assistant-message-${sender}`;
  message.textContent = text;
  $("#assistant-messages").append(message);
  message.scrollIntoView({ block: "end", behavior: "smooth" });
}

async function askAssistant(question) {
  $(".assistant-suggestions")?.remove();
  $(".assistant-prompt-label")?.remove();
  addAssistantMessage(question, "user");
  $("#assistant-input").value = "";
  const sendButton = $("#assistant-send");
  const input = $("#assistant-input");
  sendButton.disabled = true;
  input.disabled = true;
  const loading = document.createElement("div");
  loading.className = "assistant-message assistant-message-bot assistant-typing";
  loading.textContent = "Estoy consultando los datos…";
  $("#assistant-messages").append(loading);
  try {
    const result = await api("/asistente/preguntar", {
      method: "POST",
      body: JSON.stringify({ pregunta: question }),
    });
    loading.remove();
    addAssistantMessage(result.respuesta, "bot");
  } catch (error) {
    loading.remove();
    addAssistantMessage(`No pude consultar el sistema: ${error.message}`, "bot");
  } finally {
    sendButton.disabled = false;
    input.disabled = false;
    input.focus();
  }
}

$("#assistant-launcher").addEventListener("click", () => {
  const panel = $("#assistant-panel");
  const isOpening = panel.classList.contains("hidden");
  panel.classList.toggle("hidden", !isOpening);
  $("#assistant-launcher").setAttribute("aria-expanded", String(isOpening));
  if (isOpening) {
    $("#assistant-input").focus();
    $("#assistant-messages").scrollTop = $("#assistant-messages").scrollHeight;
  }
});
$("#assistant-close").addEventListener("click", () => {
  $("#assistant-panel").classList.add("hidden");
  $("#assistant-launcher").setAttribute("aria-expanded", "false");
});
$("#assistant-form").addEventListener("submit", (event) => {
  event.preventDefault();
  const question = $("#assistant-input").value.trim();
  if (question) askAssistant(question);
});
document.querySelectorAll("[data-assistant-question]").forEach((button) => {
  button.addEventListener("click", () => askAssistant(button.dataset.assistantQuestion));
});
$("#theme-dark-button").addEventListener("click", () => setTheme("dark"));
$("#theme-light-button").addEventListener("click", () => setTheme("light"));
setTheme(savedTheme);

const now = new Date();
$("#today-label").textContent = new Intl.DateTimeFormat("es-HN", {
  weekday: "long",
  day: "numeric",
  month: "long",
}).format(now).toLocaleUpperCase("es-HN");

async function inicializarSesion() {
  try {
    const user = await api("/auth/me");
    await mostrarSistema(user);
  } catch (error) {
    $("#app-shell").classList.add("hidden");
    $("#login-gate").classList.remove("hidden");
    if (error.message !== "Inicia sesión para continuar.") {
      $("#login-error").textContent = error.message;
      $("#login-error").classList.remove("hidden");
    }
    $("#login-username").focus();
  }
}

inicializarSesion();
