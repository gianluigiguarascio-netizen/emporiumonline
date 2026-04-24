#!/usr/bin/env python3
"""
Agente automatico giornaliero per EmporiumOnline.
Pubblica ogni giorno fino a 5 prodotti Amazon reali, colorati e attraenti.

FUNZIONA SENZA API AMAZON!
Usa i feed RSS pubblici dei bestseller Amazon.it per ottenere:
- Titolo prodotto reale
- ASIN reale
- Immagine reale dal feed
- Prezzo se disponibile

I link affiliati vengono costruiti con: amazon.it/dp/{ASIN}?tag={TAG}
Questo funziona subito, senza PA-API, senza vendite pregresse.

Modalita:
  1) RSS Feed Amazon.it (default, funziona SUBITO)
  2) PA-API v5 (opzionale, se hai le credenziali)
  3) Inserimento manuale ASIN

Uso:
  python agent_products.py                    # Importa 5 prodotti da RSS
  python agent_products.py --count 3          # Importa 3 prodotti
  python agent_products.py --manual ASIN1 ASIN2  # Importa ASIN specifici
  python agent_products.py --regenerate       # Rigenera products.js dal DB
  python agent_products.py --test             # Testa connessione API (opzionale)
"""
import json
import os
import random
import re
import sys
import xml.etree.ElementTree as ET
from datetime import datetime
from urllib.request import Request, urlopen
from urllib.error import URLError

BASE_DIR = os.path.join(os.path.dirname(__file__), "..")
DATA_DIR = os.path.join(BASE_DIR, "data")
PRODUCTS_FILE = os.path.join(DATA_DIR, "products.json")
CONFIG_FILE = os.path.join(DATA_DIR, "config.json")
LOG_FILE = os.path.join(DATA_DIR, "import_log.json")

# --- Configurazione ---
def load_env():
    env_path = os.path.join(BASE_DIR, ".env")
    if os.path.exists(env_path):
        with open(env_path, "r") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, _, val = line.partition("=")
                    os.environ.setdefault(key.strip(), val.strip())

load_env()

PARTNER_TAG = os.environ.get("AMAZON_PARTNER_TAG",
              os.environ.get("AMAZON_TAG", "prezzotop08-21"))

# --- Feed RSS Amazon.it Bestseller (PUBBLICI, nessuna API necessaria) ---
RSS_FEEDS = {
    "abbigliamento": [
        "https://www.amazon.it/gp/rss/bestsellers/fashion/2892904031",   # Vestiti donna
        "https://www.amazon.it/gp/rss/bestsellers/fashion/2892859031",   # Abbigliamento donna
    ],
    "scarpe": [
        "https://www.amazon.it/gp/rss/bestsellers/fashion/700832031",    # Sneakers donna
        "https://www.amazon.it/gp/rss/bestsellers/fashion/700766031",    # Scarpe donna
    ],
    "borse": [
        "https://www.amazon.it/gp/rss/bestsellers/fashion/2004757031",   # Borse donna
        "https://www.amazon.it/gp/rss/bestsellers/fashion/2646560031",   # Zaini casual
    ],
    "accessori": [
        "https://www.amazon.it/gp/rss/bestsellers/fashion/524012031",    # Orologi donna
        "https://www.amazon.it/gp/rss/bestsellers/fashion/524016031",    # Occhiali sole
    ],
    "casa": [
        "https://www.amazon.it/gp/rss/bestsellers/kitchen/3442161031",   # Decorazioni casa
        "https://www.amazon.it/gp/rss/bestsellers/kitchen/731861031",    # Illuminazione
    ],
    "tech": [
        "https://www.amazon.it/gp/rss/bestsellers/electronics/473535031", # Cuffie
        "https://www.amazon.it/gp/rss/bestsellers/electronics/460200031", # Accessori telefono
    ],
    "beauty": [
        "https://www.amazon.it/gp/rss/bestsellers/beauty/6198081031",    # Trucco viso
        "https://www.amazon.it/gp/rss/bestsellers/beauty/6198085031",    # Trucco occhi
    ],
    "gadget": [
        "https://www.amazon.it/gp/rss/bestsellers/toys/1398017031",     # Giochi creativi
    ],
    "idee-regalo": [
        "https://www.amazon.it/gp/rss/bestsellers/gift-cards",           # Buoni regalo
    ],
}

# Colori e emoji per categorie
CATEGORY_META = {
    "scarpe":        {"emoji": "\U0001f45f", "colors": [["#ff6b9d","#a78bfa"], ["#fb923c","#fbbf24"], ["#34d399","#38bdf8"]]},
    "abbigliamento": {"emoji": "\U0001f457", "colors": [["#a78bfa","#ff6b9d"], ["#fbbf24","#fb923c"], ["#38bdf8","#34d399"]]},
    "accessori":     {"emoji": "\U0001f45c", "colors": [["#34d399","#fbbf24"], ["#ff6b9d","#38bdf8"], ["#a78bfa","#fb923c"]]},
    "borse":         {"emoji": "\U0001f392", "colors": [["#fb923c","#ff6b9d"], ["#38bdf8","#a78bfa"], ["#fbbf24","#34d399"]]},
    "casa":          {"emoji": "\U0001f3e0", "colors": [["#fbbf24","#34d399"], ["#a78bfa","#38bdf8"], ["#ff6b9d","#fb923c"]]},
    "gadget":        {"emoji": "\U0001f3ae", "colors": [["#38bdf8","#a78bfa"], ["#34d399","#ff6b9d"], ["#fb923c","#fbbf24"]]},
    "idee-regalo":   {"emoji": "\U0001f381", "colors": [["#ff6b9d","#fbbf24"], ["#a78bfa","#34d399"], ["#38bdf8","#fb923c"]]},
    "beauty":        {"emoji": "\U0001f484", "colors": [["#ff6b9d","#a78bfa"], ["#fbbf24","#ff6b9d"], ["#fb923c","#a78bfa"]]},
    "tech":          {"emoji": "\U0001f4f1", "colors": [["#38bdf8","#34d399"], ["#a78bfa","#38bdf8"], ["#34d399","#fbbf24"]]},
}

BLOCKED_WORDS = [
    "adulti", "erotico", "sexy", "arma", "coltello", "pistola",
    "sigaretta", "alcol", "droga", "scommesse", "gambling",
]

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept": "application/rss+xml, application/xml, text/xml, */*",
}


# === FUNZIONI DATABASE ===

def load_products():
    if os.path.exists(PRODUCTS_FILE):
        with open(PRODUCTS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"last_updated": "", "products": []}


def save_products(data):
    data["last_updated"] = datetime.now().isoformat()
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(PRODUCTS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"daily_limit": 5, "categories_enabled": list(CATEGORY_META.keys()),
            "keywords_excluded": [], "auto_publish": True}


def add_log_entry(entry):
    logs = {"logs": []}
    if os.path.exists(LOG_FILE):
        try:
            with open(LOG_FILE, "r", encoding="utf-8") as f:
                logs = json.load(f)
        except Exception:
            pass
    logs["logs"].insert(0, entry)
    logs["logs"] = logs["logs"][:100]
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(LOG_FILE, "w", encoding="utf-8") as f:
        json.dump(logs, f, ensure_ascii=False, indent=2)


def is_blocked(title):
    t = title.lower()
    return any(w in t for w in BLOCKED_WORDS)


# === FUNZIONI RSS ===

def fetch_rss(url):
    """Scarica un feed RSS. Ritorna il contenuto XML o None."""
    try:
        req = Request(url, headers=HEADERS)
        with urlopen(req, timeout=15) as r:
            return r.read()
    except Exception as e:
        print(f"    [WARN] Feed non raggiungibile: {url}")
        print(f"           {e}")
        return None


def extract_asin(url):
    """Estrae l'ASIN da un URL Amazon."""
    m = re.search(r'/dp/([A-Z0-9]{10})', url)
    return m.group(1) if m else None


def extract_price(text):
    """Estrae il prezzo dal testo (description RSS)."""
    if not text:
        return None
    # Cerca pattern tipo "29,99 EUR" o "EUR 29,99" o "29.99"
    m = re.search(r'(\d+[.,]\d{2})\s*(?:EUR|€)', text)
    if not m:
        m = re.search(r'(?:EUR|€)\s*(\d+[.,]\d{2})', text)
    if m:
        raw = m.group(1).replace(",", ".")
        try:
            return float(raw)
        except ValueError:
            pass
    return None


def extract_image_from_description(desc):
    """Estrae l'URL dell'immagine dal campo description del RSS."""
    if not desc:
        return ""
    # L'RSS Amazon mette un <img src="..."> nella description
    m = re.search(r'<img\s+[^>]*src=["\']([^"\']+)["\']', desc, re.IGNORECASE)
    if m:
        img_url = m.group(1)
        # Migliora qualita: sostituisci _SL... o _SS... con _SL500_
        img_url = re.sub(r'\._[A-Z]{2}\d+_', '._SL500_', img_url)
        return img_url
    return ""


def parse_rss_feed(xml_data, category):
    """Parsa un feed RSS e ritorna lista di prodotti grezzi."""
    items = []
    try:
        root = ET.fromstring(xml_data)
        for item in root.iter("item"):
            title_el = item.find("title")
            link_el = item.find("link")
            desc_el = item.find("description")

            title = title_el.text.strip() if title_el is not None and title_el.text else None
            link = link_el.text.strip() if link_el is not None and link_el.text else None
            desc = desc_el.text if desc_el is not None else ""

            if not title or not link:
                continue

            # Pulisci titolo (rimuovi numeri di classifica tipo "#1: ")
            title = re.sub(r'^#?\d+[.:]\s*', '', title).strip()
            if len(title) < 8:
                continue

            asin = extract_asin(link)
            if not asin:
                continue

            price = extract_price(desc)
            image = extract_image_from_description(desc)

            items.append({
                "asin": asin,
                "title": title[:80],
                "price": price,
                "image_url": image,
                "category": category,
            })
    except ET.ParseError as e:
        print(f"    [WARN] Errore parsing XML: {e}")
    return items


# === IMPORTAZIONE DA RSS ===

def import_via_rss(config, existing_asins, max_count=5):
    """Importa prodotti REALI dai feed RSS pubblici di Amazon.it."""
    print("  Modalita: Feed RSS Amazon.it (nessuna API necessaria)")
    print(f"  Tag affiliato: {PARTNER_TAG}")

    products = []
    found = 0
    skipped_dup = 0
    skipped_blocked = 0
    errors = 0

    categories = config.get("categories_enabled", list(RSS_FEEDS.keys()))
    random.shuffle(categories)

    for cat in categories:
        if found >= max_count:
            break

        feeds = RSS_FEEDS.get(cat, [])
        if not feeds:
            continue

        # Prova un feed random per categoria
        feed_url = random.choice(feeds)
        print(f"\n    [{cat.upper()}] Scarico feed...")

        xml_data = fetch_rss(feed_url)
        if not xml_data:
            errors += 1
            continue

        items = parse_rss_feed(xml_data, cat)
        random.shuffle(items)  # Mescola per varieta

        for raw in items:
            if found >= max_count:
                break

            if raw["asin"] in existing_asins:
                skipped_dup += 1
                continue

            if is_blocked(raw["title"]):
                skipped_blocked += 1
                continue

            product = enrich_product(raw, cat)
            products.append(product)
            existing_asins.add(raw["asin"])
            found += 1
            price_str = f" - EUR {raw['price']:.2f}" if raw['price'] else ""
            img_str = " [con immagine]" if raw['image_url'] else " [placeholder]"
            print(f"    + {raw['title'][:55]}...{price_str}{img_str}")

    return products, {
        "found": len(products),
        "skipped_duplicate": skipped_dup,
        "skipped_blocked": skipped_blocked,
        "errors": errors,
    }


# === IMPORTAZIONE MANUALE ASIN ===

def import_manual_asins(asin_list, existing_asins):
    """Crea prodotti da ASIN inseriti manualmente (senza API)."""
    print(f"  Modalita: ASIN manuali ({len(asin_list)} ASIN)")
    products = []
    stats = {"found": 0, "skipped_duplicate": 0, "skipped_blocked": 0, "errors": 0}

    cats = list(CATEGORY_META.keys())

    for asin in asin_list:
        asin = asin.strip().upper()
        if not re.match(r'^[A-Z0-9]{10}$', asin):
            print(f"    [SKIP] ASIN non valido: {asin}")
            stats["errors"] += 1
            continue
        if asin in existing_asins:
            print(f"    [SKIP] Gia presente: {asin}")
            stats["skipped_duplicate"] += 1
            continue

        cat = random.choice(cats)
        raw = {
            "asin": asin,
            "title": f"Prodotto Amazon {asin}",
            "price": None,
            "image_url": "",
            "category": cat,
        }
        product = enrich_product(raw, cat)
        # I prodotti manuali senza dettagli vanno in bozza
        product["status"] = "draft"
        product["source"] = "manual_asin"
        products.append(product)
        existing_asins.add(asin)
        stats["found"] += 1
        print(f"    + [Bozza] {asin} — Modifica titolo e categoria dall'admin")

    return products, stats


# === ARRICCHIMENTO PRODOTTO ===

def enrich_product(raw, category):
    """Trasforma dati grezzi in prodotto completo per il sito."""
    meta = CATEGORY_META.get(category, CATEGORY_META.get("gadget"))
    colors = random.choice(meta["colors"])

    price = raw.get("price")
    old_price = None
    discount = None

    if price and price > 5:
        # Stima prezzo originale per mostrare sconto indicativo
        multiplier = random.uniform(1.25, 1.6)
        old_price = round(price * multiplier, 2)
        pct = int((1 - price / old_price) * 100)
        discount = f"-{pct}%"

    return {
        "id": int(datetime.now().timestamp() * 1000) + random.randint(0, 999),
        "asin": raw["asin"],
        "title": raw["title"],
        "category": category,
        "emoji": meta["emoji"],
        "clr1": colors[0],
        "clr2": colors[1],
        "image_url": raw.get("image_url", ""),
        "images_secondary": [],
        "price": price,
        "old_price": old_price,
        "currency": "EUR",
        "discount": discount,
        "amazon_url": f"https://www.amazon.it/dp/{raw['asin']}?tag={PARTNER_TAG}",
        "source": "rss",
        "imported_at": datetime.now().isoformat(),
        "published_at": datetime.now().isoformat(),
        "status": "published",
        "offer_badge": bool(discount),
        "color_tag": "",
    }


# === GENERAZIONE products.js ===

def generate_products_js(products_data):
    """Genera js/products.js dal database JSON."""
    published = [p for p in products_data["products"] if p.get("status") == "published"]
    published.sort(key=lambda p: p.get("published_at", ""), reverse=True)

    js_products = []
    for p in published:
        js_products.append({
            "id": p["id"],
            "asin": p["asin"],
            "name": p["title"],
            "category": p["category"],
            "emoji": p.get("emoji", "\U0001f6cd"),
            "clr1": p.get("clr1", "#ff6b9d"),
            "clr2": p.get("clr2", "#a78bfa"),
            "image": p.get("image_url", ""),
            "price": p.get("price"),
            "oldPrice": p.get("old_price"),
            "discount": p.get("discount"),
            "currency": p.get("currency", "EUR"),
            "amazonLink": p.get("amazon_url", ""),
            "offerBadge": p.get("offer_badge", False),
            "importedAt": p.get("imported_at", ""),
        })

    now = datetime.now().strftime("%d/%m/%Y %H:%M")

    js_content = f"""// EmporiumOnline - Catalogo Prodotti
// Aggiornato automaticamente il {now}
// NON modificare manualmente - generato da agent_products.py

window.AMAZON_TAG = "{PARTNER_TAG}";
window.products = {json.dumps(js_products, ensure_ascii=False, indent=2)};

function buildAmazonLink(asin) {{
  return "https://www.amazon.it/dp/" + asin + "?tag=" + window.AMAZON_TAG;
}}
"""

    js_path = os.path.join(BASE_DIR, "js", "products.js")
    with open(js_path, "w", encoding="utf-8") as f:
        f.write(js_content)
    print(f"\n  products.js generato con {len(js_products)} prodotti pubblicati")


# === ESECUZIONE PRINCIPALE ===

def run_import(max_count=None, asin_list=None):
    """Esegue l'importazione completa."""
    config = load_config()
    data = load_products()
    if max_count is None:
        max_count = config.get("daily_limit", 5)

    existing_asins = {p["asin"] for p in data["products"]}

    print(f"\n{'='*60}")
    print(f"  EMPORIUM ONLINE - Importazione Prodotti")
    print(f"  {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    print(f"  Tag affiliato: {PARTNER_TAG}")
    print(f"  Prodotti esistenti: {len(data['products'])}")
    print(f"  Da importare: {max_count}")
    print(f"{'='*60}")

    if asin_list:
        products, stats = import_manual_asins(asin_list, existing_asins)
    else:
        products, stats = import_via_rss(config, existing_asins, max_count)

    # Salva prodotti nel database
    if products:
        data["products"].extend(products)
        save_products(data)

    # Rigenera products.js
    generate_products_js(data)

    # Log
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "mode": "manual_asin" if asin_list else "rss",
        "products_found": stats["found"],
        "products_published": len([p for p in products if p["status"] == "published"]),
        "products_draft": len([p for p in products if p["status"] == "draft"]),
        "skipped_duplicate": stats["skipped_duplicate"],
        "skipped_blocked": stats["skipped_blocked"],
        "errors": stats["errors"],
        "total_in_db": len(data["products"]),
    }
    add_log_entry(log_entry)

    # Riepilogo
    pub = len([p for p in products if p["status"] == "published"])
    dra = len([p for p in products if p["status"] == "draft"])
    print(f"\n{'='*60}")
    print(f"  RIEPILOGO IMPORTAZIONE")
    print(f"  Trovati:    {stats['found']}")
    print(f"  Pubblicati: {pub}")
    print(f"  Bozze:      {dra}")
    print(f"  Duplicati:  {stats['skipped_duplicate']}")
    print(f"  Bloccati:   {stats['skipped_blocked']}")
    print(f"  Errori:     {stats['errors']}")
    print(f"  Totale DB:  {len(data['products'])}")
    print(f"{'='*60}\n")

    return products


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="EmporiumOnline - Agente Importazione Prodotti")
    parser.add_argument("--count", type=int, default=None, help="Numero prodotti da importare (default: 5)")
    parser.add_argument("--manual", nargs="+", metavar="ASIN", help="Importa ASIN specifici")
    parser.add_argument("--regenerate", action="store_true", help="Rigenera solo products.js dal database")

    args = parser.parse_args()

    if args.regenerate:
        data = load_products()
        generate_products_js(data)
        print("products.js rigenerato dal database esistente.")
    elif args.manual:
        run_import(asin_list=args.manual)
    else:
        run_import(max_count=args.count)
