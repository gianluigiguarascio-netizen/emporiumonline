#!/usr/bin/env python3
"""
EmporiumOnline - Agente v2
Trova prodotti colorati su Amazon.it tramite DuckDuckGo.
Non richiede API keys. Funziona in GitHub Actions.
"""
import json
import os
import re
import sys
import time
import random
import gzip
from datetime import datetime
from urllib.request import Request, urlopen
from urllib.parse import quote_plus, urlencode, unquote
from urllib.error import URLError, HTTPError

BASE_DIR = os.path.join(os.path.dirname(__file__), "..")
DATA_DIR = os.path.join(BASE_DIR, "data")
PRODUCTS_FILE = os.path.join(DATA_DIR, "products.json")
JS_FILE = os.path.join(BASE_DIR, "js", "products.js")

AMAZON_TAG = os.environ.get("AMAZON_TAG", "prezzotop08-21")

# Keyword di ricerca per categoria — prodotti colorati e vivaci
CATEGORY_QUERIES = {
    "scarpe": [
        "scarpe donna colorate arcobaleno",
        "sneakers multicolor vivaci donna",
        "sandali colorati estate donna",
        "stivaletti colorati donna",
        "ballerine colorate donna",
    ],
    "abbigliamento": [
        "vestito colorato floreale donna",
        "abito multicolore donna estate",
        "maglietta tie dye colorata",
        "gonna colorata fantasia donna",
        "kimono colorato donna",
    ],
    "accessori": [
        "collana colorata donna moda",
        "orecchini colorati vivaci",
        "bracciale colorato resina",
        "fascia capelli colorata",
    ],
    "borse": [
        "borsa colorata donna estate",
        "zaino colorato scuola",
        "pochette colorata glitter",
        "borsa tessuto colorata",
    ],
    "casa": [
        "cuscino colorato divano decorativo",
        "vaso colorato ceramica design",
        "tappeto colorato camera",
        "lampada colorata led design",
        "statuetta colorata decorazione",
    ],
    "gadget": [
        "cover colorata telefono arcobaleno",
        "cuffie colorate wireless",
        "mouse colorato pc arcobaleno",
        "fidget toy colorato",
    ],
    "beauty": [
        "palette ombretti colorati glitter",
        "rossetto colorato brillante",
        "smalto colorato nail art",
        "matita occhi colorata",
    ],
    "idee-regalo": [
        "regalo colorato originale donna",
        "idea regalo arcobaleno divertente",
        "kit regalo colorato",
    ],
}

# Colori CSS per ogni categoria
COLORS_BY_CATEGORY = {
    "scarpe":        ("#ff6b9d", "#f472b6"),
    "abbigliamento": ("#a78bfa", "#818cf8"),
    "accessori":     ("#34d399", "#2dd4bf"),
    "borse":         ("#fbbf24", "#fb923c"),
    "casa":          ("#38bdf8", "#06b6d4"),
    "gadget":        ("#fb923c", "#f97316"),
    "beauty":        ("#f472b6", "#ec4899"),
    "idee-regalo":   ("#34d399", "#a78bfa"),
    "tech":          ("#818cf8", "#6366f1"),
}

KEYWORDS_EXCLUDED = [
    "adulti", "erotico", "arma", "coltello", "sigarett",
    "tabacco", "sexy", "porn", "escort", "pistola",
]

# Pool di seed — prodotti verificati, usati come fallback
SEED_POOL = [
    {"asin": "B0FLCS5FB2", "name": "Giacca Donna Stampata Colorata con Bottoni",     "category": "abbigliamento", "price": 6.78},
    {"asin": "B0D48KJW57", "name": "Scarpe Mary Jane Donna Colorata Tacco Basso",    "category": "scarpe",        "price": 22.99},
    {"asin": "B0B3WRBQB7", "name": "Sandali Tacco Donna Castamere Colorati",         "category": "scarpe",        "price": 35.99},
    {"asin": "B0D411DMR1", "name": "Stivaletti Donna Colorati Tacco Basso Comodi",   "category": "scarpe",        "price": 28.99},
    {"asin": "B0DBQMZZRH", "name": "Fioriera Viso Colorata Decorazione Giardino",    "category": "casa",          "price": 19.99},
    {"asin": "B09X6RKRPW", "name": "Elefante Graffiti Colorato Decorazione Casa",    "category": "casa",          "price": 24.99},
    {"asin": "B09NVD51JY", "name": "Orecchini Colorati Arcobaleno Donna Resina",     "category": "accessori",     "price": 9.99},
    {"asin": "B0C5K7X2BL", "name": "Borsa Donna Colorata Tessuto Estate",            "category": "borse",         "price": 18.99},
    {"asin": "B0B8VK3LHF", "name": "Cuscino Colorato Arcobaleno Divano Decorativo",  "category": "casa",          "price": 14.99},
    {"asin": "B0BHGXK1FZ", "name": "Cover Colorata iPhone Arcobaleno Antiurto",      "category": "gadget",        "price": 8.99},
    {"asin": "B0C7S2H8KN", "name": "Palette Ombretti Colorati 12 Colori Glitter",    "category": "beauty",        "price": 12.99},
    {"asin": "B0D3MKQX7P", "name": "Vestito Donna Floreale Colorato Maniche Lunghe", "category": "abbigliamento", "price": 25.99},
    {"asin": "B0BZQ7XMRK", "name": "Smalto Colorato Set 24 Pezzi Nail Art",          "category": "beauty",        "price": 11.99},
    {"asin": "B0C3HM5P7Y", "name": "Zaino Colorato Scuola Ragazze Arcobaleno",       "category": "borse",         "price": 22.99},
    {"asin": "B0BNYY6CZP", "name": "Lampada LED Colorata RGB Design Moderno",        "category": "casa",          "price": 29.99},
    {"asin": "B0CF9BSLWX", "name": "Collana Colorata Perline Donna Arcobaleno",      "category": "accessori",     "price": 8.99},
    {"asin": "B0B2WK8LNX", "name": "Gonna Colorata Midi Donna Fantasia Floreale",    "category": "abbigliamento", "price": 19.99},
    {"asin": "B0C1QKHMFG", "name": "Rossetto Colorato Set 12 Toni Brillanti",        "category": "beauty",        "price": 14.99},
    {"asin": "B0CN5RQF8P", "name": "Borsa Zaino Colorato Donna Glitter",             "category": "borse",         "price": 24.99},
    {"asin": "B0CL2DKYQM", "name": "Vaso Colorato Ceramica Fantasia Fiori",          "category": "casa",          "price": 17.99},
]

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:125.0) Gecko/20100101 Firefox/125.0",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
]


def get_ua():
    return random.choice(USER_AGENTS)


def fetch_url(url, timeout=20, extra_headers=None):
    headers = {
        "User-Agent": get_ua(),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "it-IT,it;q=0.9,en;q=0.8",
        "Accept-Encoding": "gzip, deflate",
        "Connection": "keep-alive",
        "Cache-Control": "no-cache",
    }
    if extra_headers:
        headers.update(extra_headers)
    req = Request(url, headers=headers)
    try:
        resp = urlopen(req, timeout=timeout)
        raw = resp.read()
        enc = resp.info().get("Content-Encoding", "")
        if "gzip" in enc:
            raw = gzip.decompress(raw)
        return raw.decode("utf-8", errors="replace")
    except Exception:
        return None


def search_duckduckgo(query, max_results=20):
    """Cerca su DuckDuckGo HTML e restituisce lista di (url, title)."""
    url = "https://html.duckduckgo.com/html/?" + urlencode({"q": "site:amazon.it " + query, "kl": "it-it"})
    html = fetch_url(url)
    if not html:
        return []

    results = []

    # Pattern principale: blocchi risultato
    blocks = re.findall(
        r'result__title[^>]*>.*?href="([^"]+)"[^>]*>(.*?)</a>',
        html, re.DOTALL
    )
    for href, title_raw in blocks:
        real_url = href
        uddg = re.search(r'uddg=([^&"]+)', href)
        if uddg:
            real_url = unquote(uddg.group(1))
        title = re.sub(r'<[^>]+>', '', title_raw).strip()
        if "amazon.it" in real_url:
            results.append((real_url, title))
        if len(results) >= max_results:
            break

    # Fallback: tutti gli href amazon.it
    if not results:
        all_links = re.findall(r'href="(https?://(?:www\.)?amazon\.it/[^"]+)"', html)
        for link in all_links:
            results.append((link, ""))
            if len(results) >= max_results:
                break

    return results


def extract_asin(url):
    for pat in [r'/dp/([A-Z0-9]{10})', r'/gp/product/([A-Z0-9]{10})', r'ASIN=([A-Z0-9]{10})']:
        m = re.search(pat, url)
        if m:
            return m.group(1)
    return None


def scrape_amazon_product(asin):
    """Scrape pagina Amazon.it per titolo, prezzo, immagine."""
    url = f"https://www.amazon.it/dp/{asin}?tag={AMAZON_TAG}&language=it_IT"
    html = fetch_url(url, timeout=25, extra_headers={"Referer": "https://www.google.it/"})
    if not html or len(html) < 1000:
        return None

    # Titolo
    title = None
    for pat in [
        r'id="productTitle"[^>]*>\s*([^<]{5,200}?)\s*<',
        r'"name"\s*:\s*"([^"]{5,200})"',
        r'<title>([^|<]{10,150}?)(?:\s*[|\-])',
    ]:
        m = re.search(pat, html, re.DOTALL)
        if m:
            title = m.group(1).strip()
            break

    if not title:
        return None

    # Filtra titoli invalidi / errori Amazon
    INVALID_TITLES = ["flyouterror", "robot check", "page not found", "404", "access denied", "sorry"]
    if any(kw in title.lower() for kw in INVALID_TITLES):
        return None

    if any(kw in title.lower() for kw in KEYWORDS_EXCLUDED):
        return None

    # Prezzo
    price = None
    for pat in [
        r'"priceAmount"\s*:\s*([0-9]+(?:\.[0-9]+)?)',
        r'<span[^>]*class="[^"]*a-offscreen[^"]*">\s*€?\s*([0-9]+[.,][0-9]+)',
        r'"price"\s*:\s*"([0-9]+[.,][0-9]+)"',
    ]:
        m = re.search(pat, html)
        if m:
            try:
                raw = m.group(1).strip()
                # Formato IT: 1.234,56 → rimuove sep-migliaia, converte virgola
                if re.match(r'^\d{1,3}(\.\d{3})*(,\d{1,2})?$', raw):
                    raw = raw.replace(".", "").replace(",", ".")
                else:
                    raw = raw.replace(",", ".")
                v = float(raw)
                if 0.50 < v < 500:   # sopra 500€ quasi certamente errore di parsing
                    price = v
                    break
            except Exception:
                pass

    # Immagine
    image = None
    m = re.search(r'"large"\s*:\s*"(https://m\.media-amazon\.com/images/I/[^"]+)"', html)
    if m:
        image = m.group(1)

    if not image:
        m = re.search(r'data-a-dynamic-image="([^"]+)"', html)
        if m:
            val = m.group(1).replace("&quot;", '"').replace("&#34;", '"')
            imgs = re.findall(r'"(https://m\.media-amazon\.com/images/I/[^"]+)"', val)
            if imgs:
                image = imgs[0]

    if not image:
        m = re.search(r'<img[^>]+id="landingImage"[^>]+src="(https://[^"]+)"', html)
        if m:
            image = m.group(1)

    # Normalizza dimensione immagine
    if image and "media-amazon.com" in image:
        image = re.sub(r'\._[A-Z]{2}[^\.]*\.jpg', '._AC_SX500_.jpg', image)
        if "._AC_" not in image:
            base = image.split("._")[0] if "._" in image else image.replace(".jpg", "")
            image = base + "._AC_SX500_.jpg"

    if not image:
        image = get_affiliate_image(asin)

    return {"title": title, "price": price, "image": image, "asin": asin}


def get_affiliate_image(asin):
    return (
        f"https://ws-eu.amazon-adsystem.com/widgets/q?_encoding=UTF8"
        f"&ASIN={asin}&Format=_SL300_&ID=AsinImage&MarketPlace=IT"
        f"&ServiceVersion=20070822&WS=1&tag={AMAZON_TAG}"
    )


def build_product(asin, name, category, price, image):
    clr1, clr2 = COLORS_BY_CATEGORY.get(category, ("#ff6b9d", "#a78bfa"))
    return {
        "id": f"{category}-{asin}",
        "asin": asin,
        "name": name[:120],
        "category": category,
        "price": price,
        "image": image or get_affiliate_image(asin),
        "amazonLink": f"https://www.amazon.it/dp/{asin}?tag={AMAZON_TAG}",
        "clr1": clr1,
        "clr2": clr2,
        "offerBadge": True,
        "importedAt": datetime.now().isoformat(),
        "status": "published",
    }


def load_products():
    if not os.path.exists(PRODUCTS_FILE):
        return []
    try:
        with open(PRODUCTS_FILE) as f:
            data = json.load(f)
        return data.get("products", [])
    except Exception:
        return []


def save_products(products):
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(PRODUCTS_FILE, "w", encoding="utf-8") as f:
        json.dump({"last_updated": datetime.now().isoformat(), "products": products}, f, ensure_ascii=False, indent=2)


def generate_products_js(products):
    ts = datetime.now().strftime("%d/%m/%Y %H:%M")
    content = (
        "// EmporiumOnline - Catalogo Prodotti\n"
        f"// Aggiornato automaticamente il {ts}\n"
        "// NON modificare manualmente - generato da agent_products.py\n\n"
        f'window.AMAZON_TAG = "{AMAZON_TAG}";\n\n'
        f"window.products = {json.dumps(products, ensure_ascii=False, indent=2)};\n"
    )
    with open(JS_FILE, "w", encoding="utf-8") as f:
        f.write(content)


def main(count=5):
    print("=" * 60)
    print("  EMPORIUM ONLINE — Importazione Prodotti v2")
    print(f"  {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    print(f"  Tag affiliato: {AMAZON_TAG}")
    existing = load_products()
    existing_asins = {p["asin"] for p in existing}
    print(f"  Prodotti esistenti: {len(existing)}")
    print(f"  Da trovare: {count}")
    print("=" * 60)

    new_products = []
    categories = list(CATEGORY_QUERIES.keys())
    random.shuffle(categories)

    # Fase 1: DuckDuckGo → scrape Amazon
    for cat in categories:
        if len(new_products) >= count:
            break
        queries = CATEGORY_QUERIES[cat]
        random.shuffle(queries)
        print(f"\n  [{cat.upper()}] Ricerca DuckDuckGo...")

        for query in queries[:2]:
            if len(new_products) >= count:
                break
            results = search_duckduckgo(query, max_results=15)
            time.sleep(random.uniform(1.5, 2.5))

            for url, ddg_title in results:
                if len(new_products) >= count:
                    break
                asin = extract_asin(url)
                if not asin or asin in existing_asins:
                    continue

                print(f"    ASIN {asin} — scraping...")
                time.sleep(random.uniform(2.0, 4.0))
                data = scrape_amazon_product(asin)

                if data and data.get("title"):
                    p = build_product(asin, data["title"], cat, data.get("price"), data.get("image"))
                    new_products.append(p)
                    existing_asins.add(asin)
                    print(f"    [OK] {p['name'][:65]}")
                else:
                    # Fallback: usa titolo DuckDuckGo
                    title = re.sub(r'\s*[-|:]\s*Amazon\.it.*$', '', ddg_title, flags=re.IGNORECASE).strip()
                    if len(title) > 10 and not any(kw in title.lower() for kw in KEYWORDS_EXCLUDED):
                        p = build_product(asin, title, cat, None, get_affiliate_image(asin))
                        new_products.append(p)
                        existing_asins.add(asin)
                        print(f"    [OK-DDG] {p['name'][:65]}")
                    else:
                        print(f"    [SKIP] Dati insufficienti")

    # Fase 2: seed pool come fallback
    if len(new_products) < count:
        needed = count - len(new_products)
        print(f"\n  [SEED] Integro con {needed} prodotti dal pool verificato...")
        seed_shuffled = SEED_POOL.copy()
        random.shuffle(seed_shuffled)
        for seed in seed_shuffled:
            if len(new_products) >= count:
                break
            asin = seed["asin"]
            if asin in existing_asins:
                continue
            print(f"    Seed {asin} — verifica immagine...")
            time.sleep(random.uniform(1.0, 2.0))
            data = scrape_amazon_product(asin)
            name  = data["title"] if data and data.get("title") else seed["name"]
            price = data["price"]  if data and data.get("price")  else seed.get("price")
            image = data["image"]  if data and data.get("image")  else get_affiliate_image(asin)
            p = build_product(asin, name, seed["category"], price, image)
            new_products.append(p)
            existing_asins.add(asin)
            print(f"    [SEED-OK] {p['name'][:65]}")

    if not new_products:
        print("\n  [WARN] Nessun prodotto trovato. JS rigenerato con dati esistenti.")
        generate_products_js(existing)
        return

    # Nuovi in cima, max 40 totali
    all_products = (new_products + existing)[:40]
    save_products(all_products)
    generate_products_js(all_products)

    print("\n" + "=" * 60)
    print(f"  Nuovi trovati:  {len(new_products)}")
    print(f"  Totale nel DB:  {len(all_products)}")
    print("=" * 60)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--count", type=int, default=5)
    parser.add_argument("--regenerate", action="store_true")
    args = parser.parse_args()

    if args.regenerate:
        prods = load_products()
        generate_products_js(prods)
        print(f"JS rigenerato con {len(prods)} prodotti.")
    else:
        main(args.count)
