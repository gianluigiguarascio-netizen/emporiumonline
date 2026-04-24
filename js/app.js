/* ===================================================
   EmporiumOnline — App principale
   Gestisce: rendering prodotti, fallback immagini,
   filtri categorie, lazy loading, SEO dinamico
   =================================================== */

(function () {
  "use strict";

  // ---- CONFIGURAZIONE ----
  var TAG = window.AMAZON_TAG || "prezzotop08-21";

  // Categorie con label e icona
  var CATEGORIES = {
    scarpe:        { label: "Scarpe",        icon: "👟" },
    abbigliamento: { label: "Abbigliamento", icon: "👗" },
    accessori:     { label: "Accessori",     icon: "👜" },
    borse:         { label: "Borse & Zaini", icon: "🎒" },
    casa:          { label: "Casa",          icon: "🏠" },
    gadget:        { label: "Gadget",        icon: "🎮" },
    "idee-regalo": { label: "Idee Regalo",   icon: "🎁" },
    beauty:        { label: "Beauty",        icon: "💄" },
    tech:          { label: "Tech",          icon: "📱" },
  };

  // ---- HELPERS ----

  function escapeHtml(str) {
    var div = document.createElement("div");
    div.appendChild(document.createTextNode(str || ""));
    return div.innerHTML;
  }

  function getAffiliateLink(product) {
    if (product.amazonLink) return product.amazonLink;
    if (product.asin) return "https://www.amazon.it/dp/" + product.asin + "?tag=" + TAG;
    return "#";
  }

  function getCategoryInfo(cat) {
    return CATEGORIES[cat] || { label: cat, icon: "🛍️" };
  }

  function formatPrice(price) {
    if (!price && price !== 0) return null;
    var num = parseFloat(price);
    if (isNaN(num)) return null;
    return num.toFixed(2).replace(".", ",");
  }

  function getRelativeDate(dateStr) {
    if (!dateStr) return "";
    var date = new Date(dateStr);
    var now = new Date();
    var diff = Math.floor((now - date) / 86400000);
    if (diff === 0) return "Oggi";
    if (diff === 1) return "Ieri";
    if (diff < 7) return diff + " giorni fa";
    return "";
  }

  // ---- SVG PLACEHOLDER ----

  function createPlaceholderSvg(emoji, clr1, clr2, text) {
    var c1 = clr1 || "#ff6b9d";
    var c2 = clr2 || "#a78bfa";
    var label = text || "Immagine non disponibile";
    return (
      "data:image/svg+xml," +
      encodeURIComponent(
        '<svg xmlns="http://www.w3.org/2000/svg" width="400" height="400">' +
        '<defs><linearGradient id="g" x1="0" y1="0" x2="1" y2="1">' +
        '<stop offset="0%" stop-color="' + c1 + '"/>' +
        '<stop offset="100%" stop-color="' + c2 + '"/>' +
        '</linearGradient></defs>' +
        '<rect width="400" height="400" fill="url(#g)"/>' +
        '<text x="200" y="170" text-anchor="middle" font-size="80">' + (emoji || "🛍️") + '</text>' +
        '<text x="200" y="260" text-anchor="middle" font-family="sans-serif" font-size="16" fill="white" opacity="0.9">' +
        label + '</text>' +
        '</svg>'
      )
    );
  }

  // ---- IMMAGINE CON FALLBACK ----

  function handleImageError(img) {
    if (img.dataset.fallbackApplied) return;
    img.dataset.fallbackApplied = "true";
    var emoji = img.dataset.emoji || "🛍️";
    var clr1 = img.dataset.clr1 || "#ff6b9d";
    var clr2 = img.dataset.clr2 || "#a78bfa";
    img.src = createPlaceholderSvg(emoji, clr1, clr2, "Vedi su Amazon");
  }

  // ---- RENDER CARD PRODOTTO ----

  function renderProductCard(product) {
    var info = getCategoryInfo(product.category);
    var link = getAffiliateLink(product);
    var hasImage = product.image && product.image.length > 5;
    var imageSrc = hasImage
      ? product.image
      : createPlaceholderSvg(product.emoji || info.icon, product.clr1, product.clr2, "Vedi su Amazon");

    var priceHtml = "";
    var formattedPrice = formatPrice(product.price);
    var formattedOldPrice = formatPrice(product.oldPrice);

    if (formattedPrice) {
      priceHtml += '<span class="price-current">&euro;' + formattedPrice + '</span>';
      if (formattedOldPrice && product.oldPrice > product.price) {
        priceHtml += ' <span class="price-old">&euro;' + formattedOldPrice + '</span>';
      }
      if (product.discount) {
        priceHtml += ' <span class="discount-badge">' + escapeHtml(product.discount) + '</span>';
      }
    } else {
      priceHtml = '<span class="price-check">Verifica prezzo su Amazon</span>';
    }

    var badgeHtml = "";
    if (product.offerBadge) {
      badgeHtml = '<div class="offer-badge">Offerta</div>';
    }

    var dateLabel = getRelativeDate(product.importedAt);
    var dateHtml = dateLabel ? '<span class="date-label">' + dateLabel + '</span>' : '';

    var card = document.createElement("div");
    card.className = "product-card";
    card.innerHTML =
      '<a href="' + escapeHtml(link) + '" target="_blank" rel="nofollow noopener sponsored" class="card-link">' +
        '<div class="card-image" style="--clr1:' + (product.clr1 || "#ff6b9d") + ';--clr2:' + (product.clr2 || "#a78bfa") + '">' +
          badgeHtml +
          dateHtml +
          '<img src="' + escapeHtml(imageSrc) + '" alt="' + escapeHtml(product.name) + '" loading="lazy" ' +
            'data-emoji="' + escapeHtml(product.emoji || info.icon) + '" ' +
            'data-clr1="' + (product.clr1 || "#ff6b9d") + '" ' +
            'data-clr2="' + (product.clr2 || "#a78bfa") + '" ' +
            'onerror="handleImageError(this)">' +
        '</div>' +
        '<div class="card-body">' +
          '<div class="card-category">' + escapeHtml(info.icon + " " + info.label) + '</div>' +
          '<h3 class="card-title">' + escapeHtml(product.name) + '</h3>' +
          '<div class="card-price">' + priceHtml + '</div>' +
          '<div class="card-cta">' +
            '<span class="cta-btn">Vedi offerta su Amazon</span>' +
          '</div>' +
          '<p class="card-disclaimer">Prezzo e disponibilit&agrave; possono variare su Amazon</p>' +
        '</div>' +
      '</a>';

    return card;
  }

  // Esponi globalmente per onerror inline
  window.handleImageError = handleImageError;

  // ---- RENDER GRIGLIA ----

  function renderGrid(containerId, products) {
    var container = document.getElementById(containerId);
    if (!container) return;
    container.innerHTML = "";

    if (!products.length) {
      container.innerHTML =
        '<div class="empty-state">' +
          '<p>Nuove offerte in arrivo! Torna a trovarci.</p>' +
        '</div>';
      return;
    }

    var fragment = document.createDocumentFragment();
    products.forEach(function (p) {
      fragment.appendChild(renderProductCard(p));
    });
    container.appendChild(fragment);
  }

  // ---- FILTRO CATEGORIE ----

  function renderCategoryFilters() {
    var container = document.getElementById("category-filters");
    if (!container) return;

    var products = window.products || [];
    var activeCats = {};
    products.forEach(function (p) {
      activeCats[p.category] = (activeCats[p.category] || 0) + 1;
    });

    container.innerHTML = "";
    var allBtn = document.createElement("button");
    allBtn.className = "filter-btn active";
    allBtn.dataset.cat = "all";
    allBtn.textContent = "Tutte (" + products.length + ")";
    allBtn.addEventListener("click", function () { filterProducts("all"); });
    container.appendChild(allBtn);

    Object.keys(activeCats).forEach(function (cat) {
      var info = getCategoryInfo(cat);
      var btn = document.createElement("button");
      btn.className = "filter-btn";
      btn.dataset.cat = cat;
      btn.textContent = info.icon + " " + info.label + " (" + activeCats[cat] + ")";
      btn.addEventListener("click", function () { filterProducts(cat); });
      container.appendChild(btn);
    });
  }

  function filterProducts(category) {
    var products = window.products || [];
    var filtered = category === "all" ? products : products.filter(function (p) { return p.category === category; });
    renderGrid("offers-grid", filtered);

    // Update active button
    var btns = document.querySelectorAll(".filter-btn");
    btns.forEach(function (btn) {
      btn.classList.toggle("active", btn.dataset.cat === category);
    });
  }

  // ---- OFFERTE DEL GIORNO ----

  function renderTodayOffers() {
    var products = window.products || [];
    // Le prime 5 sono le offerte del giorno (le piu recenti)
    var today = products.slice(0, 5);
    renderGrid("today-grid", today);
  }

  // ---- ULTIME OFFERTE ----

  function renderLatestOffers() {
    var products = window.products || [];
    renderGrid("offers-grid", products);
  }

  // ---- CATEGORIE COLORATE ----

  function renderColorCategories() {
    var container = document.getElementById("color-categories");
    if (!container) return;

    var products = window.products || [];
    var activeCats = {};
    products.forEach(function (p) {
      if (!activeCats[p.category]) activeCats[p.category] = 0;
      activeCats[p.category]++;
    });

    var colors = ["#ff6b9d", "#a78bfa", "#34d399", "#fbbf24", "#fb923c", "#38bdf8", "#f472b6", "#818cf8", "#2dd4bf"];
    var i = 0;

    container.innerHTML = "";
    Object.keys(CATEGORIES).forEach(function (cat) {
      var info = CATEGORIES[cat];
      var count = activeCats[cat] || 0;
      var color = colors[i % colors.length];
      i++;

      var card = document.createElement("a");
      card.href = "#offerte";
      card.className = "color-cat-card";
      card.style.setProperty("--cat-color", color);
      card.innerHTML =
        '<span class="cat-icon">' + info.icon + '</span>' +
        '<span class="cat-name">' + info.label + '</span>' +
        (count > 0 ? '<span class="cat-count">' + count + '</span>' : '');
      card.addEventListener("click", function (e) {
        e.preventDefault();
        filterProducts(cat);
        document.getElementById("offerte").scrollIntoView({ behavior: "smooth" });
      });
      container.appendChild(card);
    });
  }

  // ---- NEWSLETTER ----

  function subscribeNewsletter(e) {
    e.preventDefault();
    showToast("Iscrizione ricevuta! Controlla la tua email.");
    e.target.reset();
  }

  // ---- TOAST ----

  function showToast(msg) {
    var existing = document.querySelector(".toast");
    if (existing) existing.remove();

    var t = document.createElement("div");
    t.className = "toast show";
    t.textContent = msg;
    document.body.appendChild(t);
    setTimeout(function () {
      t.classList.remove("show");
      setTimeout(function () { t.remove(); }, 400);
    }, 3500);
  }

  // ---- MOBILE MENU ----

  function toggleMenu() {
    document.querySelector(".nav-links").classList.toggle("open");
  }

  // ---- CONTATORE ANIMATO ----

  function animateCounters() {
    var counters = document.querySelectorAll("[data-count]");
    counters.forEach(function (el) {
      var target = parseInt(el.dataset.count, 10);
      var current = 0;
      var step = Math.ceil(target / 40);
      var timer = setInterval(function () {
        current += step;
        if (current >= target) {
          current = target;
          clearInterval(timer);
        }
        el.textContent = current;
      }, 30);
    });
  }

  // ---- SEO DINAMICO ----

  function updateSEO() {
    var products = window.products || [];
    var count = products.length;

    // Aggiorna contatori
    var countEl = document.getElementById("product-count");
    if (countEl) countEl.textContent = count;

    // Meta description dinamica
    var metaDesc = document.querySelector('meta[name="description"]');
    if (metaDesc && count > 0) {
      metaDesc.content = "Scopri " + count + " offerte colorate da Amazon: moda, scarpe, casa, gadget e accessori. Ogni giorno 5 nuove idee selezionate per te.";
    }
  }

  // ---- MERGE ADMIN PRODUCTS ----

  function mergeAdminProducts() {
    // Legge prodotti salvati dall'admin in localStorage e li aggiunge a window.products
    try {
      var raw = localStorage.getItem("eo_published");
      if (!raw) return;
      var data = JSON.parse(raw);
      if (!data || !Array.isArray(data.products) || !data.products.length) return;

      // Evita duplicati per ASIN
      var existingAsins = {};
      (window.products || []).forEach(function (p) { existingAsins[p.asin] = true; });

      data.products.forEach(function (p) {
        if (!existingAsins[p.asin]) {
          window.products.push(p);
          existingAsins[p.asin] = true;
        }
      });
    } catch (e) {
      // silently ignore
    }
  }

  // ---- INIT ----

  function init() {
    mergeAdminProducts();
    renderTodayOffers();
    renderColorCategories();
    renderCategoryFilters();
    renderLatestOffers();
    updateSEO();
    animateCounters();
  }

  // Esponi globali
  window.subscribeNewsletter = subscribeNewsletter;
  window.toggleMenu = toggleMenu;
  window.showToast = showToast;
  window.filterProducts = filterProducts;

  document.addEventListener("DOMContentLoaded", init);
})();
