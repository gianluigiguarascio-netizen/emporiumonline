# EmporiumOnline — Guida per AI Assistenti

Questo file contiene tutto il necessario per continuare lo sviluppo del sito con qualsiasi AI.

---

## Cos'è il progetto

**EmporiumOnline** è un sito affiliato Amazon che vende prodotti colorati/fantasia.
- **Sito live:** https://emporiumonline.it
- **Repository GitHub:** https://github.com/gianluigiguarascio-netizen/emporiumonline
- **Tag affiliato Amazon:** `prezzotop08-21`
- **Account Amazon Associates:** registrato su programma-affiliazione.amazon.it

---

## Come funziona il sito

- Sito statico su **GitHub Pages** — ogni push su `main` fa deploy automatico (~1 min)
- I prodotti sono in `/js/products.js` (array `window.products`)
- Le immagini vengono da `m.media-amazon.com` (CDN Amazon che funziona senza blocchi)
- I link affiliati hanno sempre `?tag=prezzotop08-21` alla fine

---

## Come aggiungere un prodotto

### 1. Prendi l'ASIN dal link Amazon
Dal link `https://www.amazon.it/dp/B0XXXXXXXX/ref=...` → ASIN = `B0XXXXXXXX`

### 2. Apri la pagina Amazon e estrai i dati
```javascript
// Esegui questo JS nella console del browser sulla pagina Amazon
({
  name: document.getElementById('productTitle')?.textContent?.trim(),
  price: document.querySelector('.a-price-whole')?.textContent?.trim(),
  priceDecimal: document.querySelector('.a-price-fraction')?.textContent?.trim(),
  oldPrice: document.querySelector('.a-text-price .a-offscreen')?.textContent?.trim(),
  image: document.getElementById('landingImage')?.src
})
```

### 3. Aggiungi il prodotto in `/js/products.js`
```javascript
{
  "id": 200,                          // incrementa l'ultimo ID
  "asin": "B0XXXXXXXX",
  "name": "Nome Breve Prodotto",
  "category": "abbigliamento",        // vedi categorie sotto
  "emoji": "👗",
  "clr1": "#ff6b9d",                  // colore gradiente card (hex)
  "clr2": "#a78bfa",
  "image": "https://m.media-amazon.com/images/I/XXXXXXXXX._AC_SL300_.jpg",
  "price": 19.99,                     // null se non disponibile
  "oldPrice": 35.99,                  // null se nessuno sconto
  "discount": "-44%",                 // null se nessuno sconto
  "currency": "EUR",
  "amazonLink": "https://www.amazon.it/dp/B0XXXXXXXX?tag=prezzotop08-21",
  "offerBadge": true,
  "importedAt": "2026-04-25"
}
```

### 4. Fai push
```bash
cd /Users/admin/emporiumonline
git add js/products.js
git commit -m "Aggiungi [Nome Prodotto] (ASIN)"
git push
```

---

## Categorie disponibili

| category | label | emoji |
|----------|-------|-------|
| `abbigliamento` | Abbigliamento | 👗 |
| `scarpe` | Scarpe | 👟 |
| `accessori` | Accessori | 👜 |
| `borse` | Borse & Zaini | 🎒 |
| `casa` | Casa | 🏠 |
| `gadget` | Gadget | 🎮 |
| `idee-regalo` | Idee Regalo | 🎁 |
| `beauty` | Beauty | 💄 |
| `tech` | Tech | 📱 |

---

## Prodotti attuali (2026-04-25)

### Abbigliamento
- `B0FLCS5FB2` — Giacca Donna Stampata Volant €6,78 (-48%)
- `B0GQH3VZ8B` — T-Shirt Mosaico Colorato €23,99
- `B09TTDGBMK` — Xmiral Abito Lungo Floreale €26,99
- `B0GWVC5DFB` — LUNULE Vestito Giallo €13,99
- `B0GWVL4VV5` — LUNULE Vestito Blu €13,99
- `B0GWVGG8NB` — LUNULE Vestito Azzurro €13,99
- `B0GWVGR8MN` — LUNULE Vestito Zafferano €13,99
- `B0GWVDGMYP` — LUNULE Vestito Turchese €13,99
- `B0GWVJ5Z9N` — LUNULE Vestito Beige €13,99
- `B0GWVHC4PT` — LUNULE Vestito Viola €13,99
- `B0GWVJBJD3` — LUNULE Vestito Viola XL €13,99
- `B0GWVG3C2P` — LUNULE Vestito Rosa Acceso €13,99
- `B0GWVF8BTP` — LUNULE Vestito Zafferano S €13,99
- `B0GWVCG8C7` — LUNULE Vestito Azzurro L €13,99
- `B0GWVG91Y2` — LUNULE Vestito Beige L €13,99
- `B0GWVHYTKK` — LUNULE Vestito Verde €13,99
- `B0GWVGTLCR` — LUNULE Vestito Viola Scuro €13,99

### Scarpe
- `B0D48KJW57` — NobleOnly Mary Jane Tacco Colorato €63,99
- `B0B3WRBQB7` — Castamere Sandali Tacco Colorati €69,90
- `B0D411DMR1` — NobleOnly Stivaletti Tacco Colorati €69,99

### Casa
- `B0DBQMZZRH` — Fioriera Vaso Viso Colorato €42,99
- `B09X6RKRPW` — Scultura Elefante Graffiti €36,88

---

## Regole immagini

| CDN | Funziona? | Note |
|-----|-----------|------|
| `m.media-amazon.com/images/I/XXXXX._AC_SL300_.jpg` | ✅ SÌ | Usa questo |
| `images-eu.ssl-images-amazon.com/images/P/ASIN.01._AC_SL300_.jpg` | ❌ NO | Restituisce 1x1px |
| `ws-eu.amazon-adsystem.com/widgets/q?...` | ⚠️ Dipende | Solo su dominio registrato |
| `images.unsplash.com` | ✅ SÌ | Usare come fallback |

**Come ottenere l'URL immagine reale:** apri la pagina prodotto su Amazon, tasto destro sull'immagine principale → "Copia indirizzo immagine". Cambia la parte `_AC_SX679_` con `_AC_SL300_` per avere 300px.

---

## Struttura file principali

```
emporiumonline/
├── index.html          # Homepage
├── admin.html          # Pannello admin (gestione prodotti)
├── css/style.css       # Stili
├── js/
│   ├── app.js          # Logica rendering card, filtri, fallback immagini
│   └── products.js     # ← QUI si aggiungono i prodotti
├── data/
│   ├── products.json   # Aggiornato dall'agente Python (GitHub Actions)
│   └── config.json     # Configurazione sito
├── scripts/
│   └── agent_products.py  # Agente automatico prodotti
└── .github/workflows/
    └── deploy.yml      # Deploy automatico GitHub Pages
```

---

## Comandi utili

```bash
# Vedere stato deploy
gh run list --repo gianluigiguarascio-netizen/emporiumonline --limit 5

# Avviare server locale
cd /Users/admin/emporiumonline
python3 -m http.server 3456 --directory /Users/admin/emporiumonline
# Poi apri: http://localhost:3456

# Vedere tutti i prodotti attuali
grep '"name"' /Users/admin/emporiumonline/js/products.js
```

---

## Note importanti

1. **Il tag affiliato** `prezzotop08-21` deve essere sempre presente nei link
2. **I prezzi cambiano** su Amazon — aggiornare periodicamente
3. **Varianti stesso prodotto**: stessa famiglia → stesse ultime 2 cifre ID, diverso ASIN
4. **Sconto**: calcola `((oldPrice - price) / oldPrice * 100)` arrotondato
5. **Il sito è su GitHub Pages** — non c'è backend, tutto è statico
