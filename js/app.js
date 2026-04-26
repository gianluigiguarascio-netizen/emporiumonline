/* ===================================================
   EmporiumOnline — App principale v3
   Fix immagini, lazy loading, design migliorato
   =================================================== */

(function () {
  "use strict";

  var TAG = window.AMAZON_TAG || "prezzotop08-21";

  var CATEGORIES = {
    scarpe:        { label: "Scarpe",        icon: "👟", color: "#ff6b9d" },
    abbigliamento: { label: "Abbigliamento", icon: "👗", color: "#a78bfa" },
    accessori:     { label: "Accessori",     icon: "👜", color: "#34d399" },
    borse:         { label: "Borse & Zaini", icon: "🎒", color: "#fbbf24" },
    casa:          { label: "Casa",          icon: "🏠", color: "#38bdf8" },
    gadget:        { label: "Gadget",        icon: "🎮", color: "#fb923c" },
    "idee-regalo": { label: "Idee Regalo",   icon: "🎁", color: "#34d399" },
    beauty:        { label: "Beauty",        icon: "💄", color: "#f472b6" },
    tech:          { label: "Tech",          icon: "📱", color: "#818cf8" },
    bambini:       { label: "Bambini",       icon: "🧸", color: "#f59e0b" },
  };

  // ---- HELPERS ----

  function escapeHtml(str) {
    var d = document.createElement("div");
    d.appendChild(document.createTextNode(str || ""));
    return d.innerHTML;
  }

  function getAffiliateLink(p) {
    if (p.amazonLink) return p.amazonLink;
    if (p.asin) return "https://www.amazon.it/dp/" + p.asin + "?tag=" + TAG;
    return "#";
  }

  function getCategoryInfo(cat) {
    return CATEGORIES[cat] || { label: cat, icon: "🛍️", color: "#a78bfa" };
  }

  function formatPrice(price) {
    if (!price && price !== 0) return null;
    var n = parseFloat(price);
    if (isNaN(n)) return null;
    return n.toFixed(2).replace(".", ",");
  }

  function getRelativeDate(dateStr) {
    if (!dateStr) return "";
    var d = new Date(dateStr), now = new Date();
    var diff = Math.floor((now - d) / 86400000);
    if (diff === 0) return "Nuovo";
    if (diff === 1) return "Ieri";
    if (diff < 7) return diff + " giorni fa";
    return "";
  }

  function isToday(dateStr) {
    if (!dateStr) return false;
    var d = new Date(dateStr), now = new Date();
    return d.toDateString() === now.toDateString();
  }

  // ---- SVG PLACEHOLDER COLORATO ----

  function createPlaceholderSvg(emoji, clr1, clr2, text) {
    var c1 = clr1 || "#ff6b9d", c2 = clr2 || "#a78bfa";
    var label = escapeHtml(text || "Vedi su Amazon");
    return "data:image/svg+xml," + encodeURIComponent(
      '<svg xmlns="http://www.w3.org/2000/svg" width="500" height="500">' +
      '<defs><linearGradient id="g" x1="0" y1="0" x2="1" y2="1">' +
      '<stop offset="0%" stop-color="' + c1 + '"/>' +
      '<stop offset="100%" stop-color="' + c2 + '"/>' +
      '</linearGradient></defs>' +
      '<rect width="500" height="500" fill="url(#g)"/>' +
      '<text x="250" y="210" text-anchor="middle" font-size="100">' + (emoji || "🛍️") + '</text>' +
      '<text x="250" y="310" text-anchor="middle" font-family="sans-serif" ' +
      'font-size="22" fill="white" opacity="0.9">' + label + '</text>' +
      '</svg>'
    );
  }

  // ---- GESTIONE IMMAGINI AMAZON ----
  // Strategia multi-fallback per massimizzare il caricamento immagini

  function upgradeImageUrl(url) {
    if (!url) return url;
    // Normalizza a SX500 per qualità migliore
    return url
      .replace(/\._[A-Z]{2}\d+_\./g, "._AC_SX500_.")
      .replace(/\._SL\d+_\./g, "._AC_SX500_.")
      .replace(/\._AC_SL\d+_\./g, "._AC_SX500_.");
  }

  function getFallbackImageUrl(url) {
    if (!url) return null;
    // Prova formati alternativi
    if (url.includes("_AC_SX500_")) return url.replace("_AC_SX500_", "_AC_SL500_");
    if (url.includes("_AC_SL500_")) return url.replace("_AC_SL500_", "_AC_UY500_");
    return null;
  }

  window.handleImageError = function (img) {
    if (img.dataset.retry) {
      // Già provato fallback: mostra placeholder
      if (!img.dataset.placeholder) {
        img.dataset.placeholder = "1";
        img.removeAttribute("referrerpolicy");
        img.src = createPlaceholderSvg(
          img.dataset.emoji, img.dataset.clr1, img.dataset.clr2, "Vedi su Amazon"
        );
      }
      return;
    }
    // Primo errore: prova URL alternativo
    img.dataset.retry = "1";
    var fallback = getFallbackImageUrl(img.src);
    if (fallback && fallback !== img.src) {
      img.src = fallback;
    } else {
      img.dataset.placeholder = "1";
      img.src = createPlaceholderSvg(
        img.dataset.emoji, img.dataset.clr1, img.dataset.clr2, "Vedi su Amazon"
      );
    }
  };

  // ---- LAZY LOADING con IntersectionObserver ----

  var observer = null;
  if ("IntersectionObserver" in window) {
    observer = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          var img = entry.target;
          var src = img.dataset.src;
          if (src) {
            img.src = src;
            img.removeAttribute("data-src");
            observer.unobserve(img);
          }
        }
      });
    }, { rootMargin: "200px 0px", threshold: 0.01 });
  }

  function observeImage(img) {
    if (observer && img.dataset.src) {
      observer.observe(img);
    } else if (img.dataset.src) {
      img.src = img.dataset.src;
    }
  }

  // ---- RENDER CARD PRODOTTO ----

  function renderProductCard(product) {
    var info = getCategoryInfo(product.category);
    var link = getAffiliateLink(product);
    var rawImage = product.image || product.image_url || "";
    var imageSrc = upgradeImageUrl(rawImage) || createPlaceholderSvg(
      product.emoji || info.icon, product.clr1, product.clr2
    );

    var priceHtml = "";
    var fp = formatPrice(product.price);
    var fop = formatPrice(product.oldPrice || product.old_price);
    if (fp) {
      priceHtml += '<span class="price-current">&euro;' + fp + '</span>';
      if (fop && parseFloat(product.oldPrice || product.old_price) > parseFloat(product.price)) {
        priceHtml += ' <span class="price-old">&euro;' + fop + '</span>';
      }
      if (product.discount) {
        priceHtml += ' <span class="discount-badge">' + escapeHtml(product.discount) + '</span>';
      }
    } else {
      priceHtml = '<span class="price-check">Verifica prezzo su Amazon &#8599;</span>';
    }

    var todayBadge = isToday(product.importedAt)
      ? '<div class="new-badge">&#x2728; Nuovo</div>' : "";
    var offerBadge = product.offerBadge
      ? '<div class="offer-badge">OFFERTA</div>' : "";
    var dateLabel = getRelativeDate(product.importedAt);
    var dateHtml = (dateLabel && !isToday(product.importedAt))
      ? '<span class="date-label">' + dateLabel + '</span>' : "";

    var catColor = info.color || product.clr1 || "#a78bfa";

    var card = document.createElement("div");
    card.className = "product-card";
    card.style.setProperty("--cat-accent", catColor);

    // Usa lazy loading: src vuoto, data-src con l'immagine reale
    var imgTag = '<img ' +
      'data-src="' + escapeHtml(imageSrc) + '" ' +
      'src="data:image/svg+xml,%3Csvg xmlns=\'http://www.w3.org/2000/svg\'/%3E" ' +
      'alt="' + escapeHtml(product.name) + '" ' +
      'loading="lazy" ' +
      'referrerpolicy="no-referrer" ' +
      'crossorigin="anonymous" ' +
      'data-emoji="' + escapeHtml(product.emoji || info.icon) + '" ' +
      'data-clr1="' + escapeHtml(product.clr1 || "#ff6b9d") + '" ' +
      'data-clr2="' + escapeHtml(product.clr2 || "#a78bfa") + '" ' +
      'onerror="handleImageError(this)">';

    var priceBadge = product.price
      ? '<div class="img-price-badge">€' + formatPrice(product.price) + '</div>'
      : '';

    card.innerHTML =
      '<a href="' + escapeHtml(link) + '" target="_blank" ' +
         'rel="nofollow noopener sponsored" class="card-link">' +
        '<div class="card-image">' +
          offerBadge +
          imgTag +
          priceBadge +
          '<div class="card-hover-overlay"><span>&#x1F6CD;&#xFE0F; Vedi su Amazon</span></div>' +
        '</div>' +
        '<div class="card-top-bar" style="background:' + catColor + '"></div>' +
        '<div class="card-body">' +
          '<div class="card-category" style="color:' + catColor + '">' +
            escapeHtml(info.icon + " " + info.label) +
          '</div>' +
          '<h3 class="card-title">' + escapeHtml(product.name) + '</h3>' +
          '<div class="card-price">' + priceHtml + '</div>' +
          '<div class="card-cta">' +
            '<span class="cta-btn">&#x1F6D2; Confronta prezzo su Amazon</span>' +
          '</div>' +
          '<p class="card-disclaimer">Prezzo e disponibilit&agrave; aggiornati su Amazon al momento del click</p>' +
        '</div>' +
      '</a>';

    // Attiva lazy loading sull'immagine
    var img = card.querySelector("img");
    if (img) observeImage(img);

    return card;
  }

  // ---- RENDER GRIGLIA ----

  function renderGrid(containerId, products) {
    var container = document.getElementById(containerId);
    if (!container) return;
    container.innerHTML = "";
    if (!products || !products.length) {
      container.innerHTML =
        '<div class="empty-state">' +
          '<p>&#x1F308; Nuove offerte in arrivo! Torna presto.</p>' +
        '</div>';
      return;
    }
    var frag = document.createDocumentFragment();
    products.forEach(function (p) { frag.appendChild(renderProductCard(p)); });
    container.appendChild(frag);
  }

  // ---- FILTRO CATEGORIE ----

  function renderCategoryFilters() {
    var container = document.getElementById("category-filters");
    if (!container) return;
    var products = window.products || [];
    var activeCats = {};
    products.forEach(function (p) { activeCats[p.category] = (activeCats[p.category] || 0) + 1; });

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
      btn.style.setProperty("--cat-filter-color", info.color || "#a78bfa");
      btn.textContent = info.icon + " " + info.label + " (" + activeCats[cat] + ")";
      btn.addEventListener("click", function () { filterProducts(cat); });
      container.appendChild(btn);
    });
  }

  function filterProducts(category) {
    var products = window.products || [];
    var filtered = category === "all" ? products
      : products.filter(function (p) { return p.category === category; });
    renderGrid("offers-grid", filtered);
    document.querySelectorAll(".filter-btn").forEach(function (btn) {
      var isActive = btn.dataset.cat === category;
      btn.classList.toggle("active", isActive);
      if (isActive && btn.dataset.cat !== "all") {
        var info = getCategoryInfo(btn.dataset.cat);
        btn.style.background = info.color || "";
        btn.style.color = "#fff";
      } else if (!isActive) {
        btn.style.background = "";
        btn.style.color = "";
      }
    });
  }

  // ---- IDEE REGALO PER FASCIA PREZZO ----

  function renderGiftsByPrice(maxPrice, containerId, limit) {
    var products = window.products || [];
    var gifts = products.filter(function (p) {
      var n = parseFloat(p.price);
      return !isNaN(n) && n > 0 && n <= maxPrice;
    }).sort(function (a, b) {
      return parseFloat(a.price) - parseFloat(b.price);
    }).slice(0, limit || 8);
    renderGrid(containerId, gifts);
  }

  function setActiveGiftBand(band) {
    document.querySelectorAll(".gift-tab-btn").forEach(function (btn) {
      btn.classList.toggle("active", btn.dataset.band === String(band));
    });
    document.querySelectorAll(".gift-band-panel").forEach(function (panel) {
      panel.classList.toggle("active", panel.id === ("gift-band-" + band));
    });
  }

  function setupGiftTabs() {
    var tabs = document.querySelectorAll(".gift-tab-btn");
    if (!tabs.length) return;
    tabs.forEach(function (btn) {
      btn.addEventListener("click", function () {
        setActiveGiftBand(btn.dataset.band);
      });
    });
    setActiveGiftBand(5);
  }

  function updateGiftTabCounts() {
    var products = window.products || [];
    var counts = { 5: 0, 10: 0, 15: 0 };

    products.forEach(function (p) {
      var n = parseFloat(p.price);
      if (isNaN(n) || n <= 0) return;
      if (n <= 5) counts[5] += 1;
      if (n <= 10) counts[10] += 1;
      if (n <= 15) counts[15] += 1;
    });

    document.querySelectorAll(".gift-tab-btn").forEach(function (btn) {
      var band = parseInt(btn.dataset.band, 10);
      if (!counts[band] && counts[band] !== 0) return;
      btn.textContent = "Sotto " + band + "€ (" + counts[band] + ")";
    });
  }

  function renderGiftPriceBands() {
    renderGiftsByPrice(5, "gift-under-5-grid", 8);
    renderGiftsByPrice(10, "gift-under-10-grid", 8);
    renderGiftsByPrice(15, "gift-under-15-grid", 8);
    updateGiftTabCounts();
    setupGiftTabs();
  }

  // ---- MIGLIORI AFFARI (sconto reale) ----

  function renderBestDeals() {
    var products = window.products || [];
    var deals = products.filter(function (p) {
      var price = parseFloat(p.price);
      var oldPrice = parseFloat(p.oldPrice || p.old_price);
      return !isNaN(price) && !isNaN(oldPrice) && oldPrice > price;
    }).map(function (p) {
      var price = parseFloat(p.price);
      var oldPrice = parseFloat(p.oldPrice || p.old_price);
      var pct = ((oldPrice - price) / oldPrice) * 100;
      var clone = Object.assign({}, p);
      clone._dealPct = pct;
      clone.discount = "Risparmi " + Math.round(pct) + "%";
      clone.offerBadge = true;
      return clone;
    }).sort(function (a, b) {
      return b._dealPct - a._dealPct;
    }).slice(0, 8);

    renderGrid("best-deals-grid", deals);
  }

  // ---- OFFERTE DEL GIORNO ----

  function renderTodayOffers() {
    var products = window.products || [];
    var today = products.slice(0, 5);
    renderGrid("today-grid", today);
  }

  // ---- CATEGORIE COLORATE ----

  function renderColorCategories() {
    var container = document.getElementById("color-categories");
    if (!container) return;
    var products = window.products || [];
    var activeCats = {};
    products.forEach(function (p) { activeCats[p.category] = (activeCats[p.category] || 0) + 1; });

    container.innerHTML = "";
    Object.keys(CATEGORIES).forEach(function (cat) {
      var info = CATEGORIES[cat];
      var count = activeCats[cat] || 0;
      var card = document.createElement("a");
      card.href = "#offerte";
      card.className = "color-cat-card";
      card.style.setProperty("--cat-color", info.color);
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

  // ---- TICKER BAR (offerte del giorno scorrevoli) ----

  function renderTickerBar() {
    var ticker = document.getElementById("ticker-content");
    if (!ticker) return;
    var products = window.products || [];
    if (!products.length) return;
    var items = products.slice(0, 10).map(function (p) {
      var fp = formatPrice(p.price);
      var priceStr = fp ? " — &euro;" + fp : "";
      return '<span class="ticker-item">&#x1F525; ' + escapeHtml(p.name.substring(0, 50)) + priceStr + '</span>';
    });
    // Duplica per loop continuo
    ticker.innerHTML = items.join("") + items.join("");
  }

  // ---- NEWSLETTER ----

  function subscribeNewsletter(e) {
    e.preventDefault();
    showToast("&#x1F4EC; Iscrizione ricevuta! Grazie.");
    e.target.reset();
  }

  // ---- TOAST ----

  function showToast(msg) {
    var ex = document.querySelector(".toast");
    if (ex) ex.remove();
    var t = document.createElement("div");
    t.className = "toast show";
    t.innerHTML = msg;
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

  // ---- CONTATORI ANIMATI ----

  function animateCounters() {
    document.querySelectorAll("[data-count]").forEach(function (el) {
      var target = parseInt(el.dataset.count, 10);
      if (!target) return;
      var current = 0, step = Math.max(1, Math.ceil(target / 50));
      var timer = setInterval(function () {
        current = Math.min(current + step, target);
        el.textContent = current;
        if (current >= target) clearInterval(timer);
      }, 25);
    });
  }

  // ---- SEO DINAMICO ----

  function updateSEO() {
    var products = window.products || [];
    var count = products.length;
    var countEl = document.getElementById("product-count");
    if (countEl) { countEl.textContent = count; countEl.dataset.count = count; }
    var metaDesc = document.querySelector('meta[name="description"]');
    if (metaDesc && count > 0) {
      metaDesc.content = "Scopri " + count + " offerte colorate da Amazon: moda, scarpe, casa, gadget e accessori. Aggiornate ogni giorno con i migliori prodotti colorati.";
    }
  }

  // ---- MERGE PRODOTTI ADMIN (localStorage) ----

  function mergeAdminProducts() {
    try {
      var raw = localStorage.getItem("eo_published");
      if (!raw) return;
      var data = JSON.parse(raw);
      if (!data || !Array.isArray(data.products) || !data.products.length) return;
      var existingAsins = {};
      (window.products || []).forEach(function (p) { existingAsins[p.asin] = true; });
      data.products.forEach(function (p) {
        if (!existingAsins[p.asin]) {
          window.products.push(p);
          existingAsins[p.asin] = true;
        }
      });
    } catch (e) { /* silent */ }
  }

  // ---- INIT ----

  function init() {
    mergeAdminProducts();
    renderTickerBar();
    renderCategoryFilters();
    renderGiftPriceBands();
    renderBestDeals();
    renderGrid("offers-grid", window.products || []);
    renderColorCategories();
    renderTodayOffers();
    renderGrid("bambini-grid", (window.products || []).filter(function(p){ return p.category === "bambini"; }));
    updateSEO();
    animateCounters();
  }

  // Esposizioni globali
  window.subscribeNewsletter = subscribeNewsletter;
  window.toggleMenu = toggleMenu;
  window.showToast = showToast;
  window.filterProducts = filterProducts;

  document.addEventListener("DOMContentLoaded", init);
})();
