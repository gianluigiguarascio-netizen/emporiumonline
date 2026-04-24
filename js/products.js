// EmporiumOnline - Prodotti reali con immagini e link Amazon verificati
// Tag affiliato: prezzotop08-21

window.AMAZON_TAG = "prezzotop08-21";

window.products = [

  // ── ABBIGLIAMENTO ──────────────────────────────────────────
  {
    "id": 116,
    "asin": "B0FLCS5FB2",
    "name": "Giacca Donna Stampata Volant Maniche 3/4",
    "category": "abbigliamento",
    "emoji": "\ud83d\udc57",
    "clr1": "#ff6b9d",
    "clr2": "#38bdf8",
    "image": "https://m.media-amazon.com/images/I/71piWfHl4dL._AC_SL300_.jpg",
    "price": 6.78,
    "oldPrice": 12.99,
    "discount": "-48%",
    "currency": "EUR",
    "amazonLink": "https://www.amazon.it/dp/B0FLCS5FB2?tag=prezzotop08-21",
    "offerBadge": true,
    "importedAt": "2026-04-25"
  },

  // ── SCARPE ────────────────────────────────────────────────
  {
    "id": 111,
    "asin": "B0D48KJW57",
    "name": "NobleOnly Mary Jane Scarpe Donna Tacco Colorato",
    "category": "scarpe",
    "emoji": "\ud83d\udc60",
    "clr1": "#ff6b9d",
    "clr2": "#fbbf24",
    "image": "https://m.media-amazon.com/images/I/71iV+i3aceL._AC_SL300_.jpg",
    "price": 63.99,
    "oldPrice": null,
    "discount": null,
    "currency": "EUR",
    "amazonLink": "https://www.amazon.it/dp/B0D48KJW57?tag=prezzotop08-21",
    "offerBadge": true,
    "importedAt": "2026-04-24"
  },
  {
    "id": 112,
    "asin": "B0B3WRBQB7",
    "name": "Castamere Sandali Tacco Donna Colorati",
    "category": "scarpe",
    "emoji": "\ud83d\udc60",
    "clr1": "#34d399",
    "clr2": "#38bdf8",
    "image": "https://m.media-amazon.com/images/I/615-RVRzTHL._AC_SL300_.jpg",
    "price": 69.90,
    "oldPrice": null,
    "discount": null,
    "currency": "EUR",
    "amazonLink": "https://www.amazon.it/dp/B0B3WRBQB7?tag=prezzotop08-21",
    "offerBadge": true,
    "importedAt": "2026-04-25"
  },
  {
    "id": 113,
    "asin": "B0D411DMR1",
    "name": "NobleOnly Stivaletti Tacco Colorati Donna",
    "category": "scarpe",
    "emoji": "\ud83d\udc60",
    "clr1": "#a78bfa",
    "clr2": "#fb923c",
    "image": "https://m.media-amazon.com/images/I/71orUdROr4L._AC_SL300_.jpg",
    "price": 69.99,
    "oldPrice": null,
    "discount": null,
    "currency": "EUR",
    "amazonLink": "https://www.amazon.it/dp/B0D411DMR1?tag=prezzotop08-21",
    "offerBadge": true,
    "importedAt": "2026-04-25"
  },

  // ── CASA ──────────────────────────────────────────────────
  {
    "id": 114,
    "asin": "B0DBQMZZRH",
    "name": "Fioriere Colorate Astratte - Vaso Viso in Resina",
    "category": "casa",
    "emoji": "\ud83c\udf3f",
    "clr1": "#34d399",
    "clr2": "#fbbf24",
    "image": "https://m.media-amazon.com/images/I/718f4rqY5eL._AC_SL300_.jpg",
    "price": 42.99,
    "oldPrice": null,
    "discount": null,
    "currency": "EUR",
    "amazonLink": "https://www.amazon.it/dp/B0DBQMZZRH?tag=prezzotop08-21",
    "offerBadge": true,
    "importedAt": "2026-04-25"
  },
  {
    "id": 115,
    "asin": "B09X6RKRPW",
    "name": "Scultura Elefante Graffiti in Resina - Decorazione",
    "category": "casa",
    "emoji": "\ud83d\udc18",
    "clr1": "#fb923c",
    "clr2": "#a78bfa",
    "image": "https://m.media-amazon.com/images/I/61yrcNkV-KL._AC_SL300_.jpg",
    "price": 36.88,
    "oldPrice": null,
    "discount": null,
    "currency": "EUR",
    "amazonLink": "https://www.amazon.it/dp/B09X6RKRPW?tag=prezzotop08-21",
    "offerBadge": true,
    "importedAt": "2026-04-25"
  }

];

function buildAmazonLink(asin) {
  return "https://www.amazon.it/dp/" + asin + "?tag=" + window.AMAZON_TAG;
}
