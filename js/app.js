const FALLBACK_FASHION = [
  { id: 1001, emoji: "👗", name: "Vestito Floreale Arcobaleno", tag: "Donna", price: "29.99", oldPrice: "59.99", clr1: "#ff6b9d", clr2: "#fbbf24", asin: "B07ZPKBL9V", discount: "-50%" },
  { id: 1002, emoji: "🌈", name: "Gonna a Ruota Multicolor", tag: "Donna", price: "24.90", oldPrice: "44.90", clr1: "#a78bfa", clr2: "#38bdf8", asin: "B0B2P4BLGW", discount: "-44%" },
  { id: 1003, emoji: "🎽", name: "T-Shirt Tie-Dye Neon", tag: "Unisex", price: "18.50", oldPrice: "35.00", clr1: "#34d399", clr2: "#fbbf24", asin: "B09V3HN1KC", discount: "-47%" },
];

const FALLBACK_SHOES = [
  { id: 1010, emoji: "👟", name: "Sneakers Chunky Arcobaleno", tag: "Sneakers", price: "64.90", oldPrice: "119.90", clr1: "#ff6b9d", clr2: "#a78bfa", asin: "B07FM2GLNQ", discount: "-46%" },
  { id: 1011, emoji: "🌈", name: "Slip-On Neon Multicolor", tag: "Casual", price: "42.00", oldPrice: "78.00", clr1: "#fbbf24", clr2: "#34d399", asin: "B09G3HRMVB", discount: "-46%" },
  { id: 1012, emoji: "👠", name: "Sandali Platform Colorati", tag: "Donna", price: "38.90", oldPrice: "72.90", clr1: "#38bdf8", clr2: "#ff6b9d", asin: "B0B1T1FLK9", discount: "-47%" },
];

const FALLBACK_AMAZON = [
  { id: 1020, emoji: "🔥", name: "Amazon: Vestito Estivo Floreale", tag: "Amazon", price: "27.99", oldPrice: "49.99", clr1: "#fbbf24", clr2: "#fb923c", asin: "B07ZPKBL9V", discount: "-44%" },
  { id: 1021, emoji: "⭐", name: "Amazon: Sneakers Donna Colorate", tag: "Amazon", price: "34.90", oldPrice: "64.90", clr1: "#ff6b9d", clr2: "#a78bfa", asin: "B07FM2GLNQ", discount: "-46%" },
  { id: 1022, emoji: "✨", name: "Amazon: T-Shirt Tie-Dye Pack 3pz", tag: "Amazon", price: "32.00", oldPrice: "58.00", clr1: "#38bdf8", clr2: "#34d399", asin: "B09V3HN1KC", discount: "-45%" },
];

function getCatalogOrFallback(globalName, fallback) {
  const value = globalThis[globalName];
  return Array.isArray(value) && value.length ? value : fallback;
}

function getCatalogFromAdminStorage() {
  try {
    const raw = localStorage.getItem("eo_products");
    if (!raw) return null;
    const products = JSON.parse(raw);
    if (!Array.isArray(products) || !products.length) return null;

    const mapProduct = (p, id, tag) => ({
      id,
      emoji: p.emoji || "🛍️",
      name: p.name || "Prodotto",
      tag: tag || p.tag || "Shop",
      price: p.price || "0.00",
      oldPrice: p.oldPrice || p.price || "0.00",
      clr1: p.clr1 || "#ff6b9d",
      clr2: p.clr2 || "#a78bfa",
      discount: p.discount || "-0%",
      asin: p.asin || "",
    });

    const fashion = products
      .filter((p) => p.cat === "fashion")
      .map((p, i) => mapProduct(p, i + 1, "Fashion"));
    const shoes = products
      .filter((p) => p.cat === "shoes")
      .map((p, i) => mapProduct(p, i + 10, "Shoes"));
    const accessories = products
      .filter((p) => p.cat === "accessories")
      .map((p, i) => mapProduct(p, i + 20, "Accessories"));

    const amazon = [...shoes, ...accessories]
      .slice(0, 8)
      .map((p, i) => ({ ...p, id: 200 + i, tag: "Amazon" }));

    if (!fashion.length && !shoes.length && !amazon.length) return null;
    return { fashion, shoes, amazon };
  } catch {
    return null;
  }
}

function getAffiliateLink(asin) {
  if (typeof buildAmazonLink === "function") return buildAmazonLink(asin);
  return `https://www.amazon.it/dp/${asin}?tag=prezzotop08-21`;
}

// Render product card
function renderCard(p, isAmazon = false) {
  const hasAsin = Boolean(p.asin);
  const link = (isAmazon || hasAsin) ? getAffiliateLink(p.asin) : p.link;
  const btnLabel = isAmazon ? "🛒 Vedi su Amazon" : "🛍️ Acquista Ora";
  const btnClass = isAmazon ? "product-btn amazon-btn" : "product-btn";
  const target = (isAmazon || hasAsin) ? 'target="_blank" rel="nofollow noopener"' : "";

  return `
    <div class="product-card">
      <div class="product-img" style="--clr1:${p.clr1};--clr2:${p.clr2}">
        <span>${p.emoji}</span>
      </div>
      <div class="product-info">
        <div class="product-tag">${p.tag}</div>
        <div class="product-name">${p.name}</div>
        <div class="product-price">
          €${p.price}
          <span class="old-price">€${p.oldPrice}</span>
          <span class="discount-badge">${p.discount}</span>
        </div>
        <a href="${link}" class="${btnClass}" ${target}>${btnLabel}</a>
      </div>
    </div>`;
}

// Populate grids
function initProducts() {
  const adminCatalog = getCatalogFromAdminStorage();
  const fashion = adminCatalog?.fashion?.length
    ? adminCatalog.fashion
    : getCatalogOrFallback("fashionProducts", FALLBACK_FASHION);
  const shoes = adminCatalog?.shoes?.length
    ? adminCatalog.shoes
    : getCatalogOrFallback("shoesProducts", FALLBACK_SHOES);
  const amazon = adminCatalog?.amazon?.length
    ? adminCatalog.amazon
    : getCatalogOrFallback("amazonProducts", FALLBACK_AMAZON);

  const fashionGrid = document.getElementById("fashion-grid");
  const shoesGrid = document.getElementById("shoes-grid");
  const amazonGrid = document.getElementById("amazon-grid");

  if (fashionGrid) fashionGrid.innerHTML = fashion.map((p) => renderCard(p)).join("");
  if (shoesGrid) shoesGrid.innerHTML = shoes.map((p) => renderCard(p)).join("");
  if (amazonGrid) amazonGrid.innerHTML = amazon.map((p) => renderCard(p, true)).join("");
}

// Newsletter
function subscribeNewsletter(e) {
  e.preventDefault();
  showToast("✅ Iscritto! Controlla la tua email.");
  e.target.reset();
}

// Toast notification
function showToast(msg) {
  let t = document.querySelector(".toast");
  if (!t) {
    t = document.createElement("div");
    t.className = "toast";
    document.body.appendChild(t);
  }
  t.textContent = msg;
  t.classList.add("show");
  setTimeout(() => t.classList.remove("show"), 3500);
}

// Mobile menu toggle
function toggleMenu() {
  document.querySelector(".nav-links").classList.toggle("open");
}

document.addEventListener("DOMContentLoaded", initProducts);
