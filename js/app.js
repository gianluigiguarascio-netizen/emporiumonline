// Render product card
function renderCard(p, isAmazon = false) {
  const link = isAmazon ? buildAmazonLink(p.asin) : p.link;
  const btnLabel = isAmazon ? "🛒 Vedi su Amazon" : "🛍️ Acquista Ora";
  const btnClass = isAmazon ? "product-btn amazon-btn" : "product-btn";
  const target = isAmazon ? 'target="_blank" rel="nofollow noopener"' : "";

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
  document.getElementById("fashion-grid").innerHTML = fashionProducts.map(p => renderCard(p)).join("");
  document.getElementById("shoes-grid").innerHTML   = shoesProducts.map(p => renderCard(p)).join("");
  document.getElementById("amazon-grid").innerHTML  = amazonProducts.map(p => renderCard(p, true)).join("");
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
