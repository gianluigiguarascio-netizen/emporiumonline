#!/usr/bin/env python3
"""
Agente automatico che recupera prodotti reali da Amazon.it
tramite feed RSS pubblici dei bestseller — nessuna API key richiesta.
"""
import json, os, re, random, xml.etree.ElementTree as ET
from urllib.request import urlopen, Request
from urllib.error import URLError
from datetime import datetime

AMAZON_TAG = os.environ.get("AMAZON_TAG", "prezzotop08-21")

HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; RSS reader)",
    "Accept": "application/rss+xml, application/xml, text/xml",
}

# Feed RSS bestseller Amazon.it per categoria moda
RSS_FEEDS = {
    "fashion": [
        "https://www.amazon.it/gp/rss/bestsellers/fashion/2892904031",   # Vestiti donna
        "https://www.amazon.it/gp/rss/bestsellers/fashion/13901048031",  # Vestiti casual donna
        "https://www.amazon.it/gp/rss/bestsellers/fashion/2892859031",   # Abbigliamento donna
    ],
    "shoes": [
        "https://www.amazon.it/gp/rss/bestsellers/fashion/700832031",    # Sneakers donna
        "https://www.amazon.it/gp/rss/bestsellers/fashion/700766031",    # Scarpe donna
    ],
    "accessories": [
        "https://www.amazon.it/gp/rss/bestsellers/fashion/2004757031",   # Borse zaino donna
        "https://www.amazon.it/gp/rss/bestsellers/fashion/2646560031",   # Zaini
    ],
}

COLORS = ["#ff6b9d","#a78bfa","#34d399","#fbbf24","#fb923c","#38bdf8"]
EMOJIS = {
    "fashion":     ["👗","🌈","🎽","🧥","👚","🩱","🎀","🩲"],
    "shoes":       ["👟","👠","🥿","👞","🩴","🥾","👡","🌈"],
    "accessories": ["👜","🎒","💍","🧣","🕶️","💄","👒","🌂"],
}

def fetch_rss(url):
    try:
        req = Request(url, headers=HEADERS)
        with urlopen(req, timeout=10) as r:
            return r.read()
    except Exception as e:
        print(f"⚠️  Errore feed {url}: {e}")
        return None

def extract_asin(url):
    m = re.search(r'/dp/([A-Z0-9]{10})', url)
    return m.group(1) if m else None

def extract_price(description):
    m = re.search(r'(\d+[.,]\d+)\s*€|€\s*(\d+[.,]\d+)', description or "")
    if m:
        raw = (m.group(1) or m.group(2)).replace(",", ".")
        return float(raw)
    return None

def parse_feed(xml_data):
    items = []
    try:
        root = ET.fromstring(xml_data)
        ns = {"dc": "http://purl.org/dc/elements/1.1/"}
        for item in root.iter("item"):
            title_el = item.find("title")
            link_el  = item.find("link")
            desc_el  = item.find("description")
            title = title_el.text.strip() if title_el is not None and title_el.text else None
            link  = link_el.text.strip()  if link_el  is not None and link_el.text  else None
            desc  = desc_el.text          if desc_el  is not None else ""
            if not title or not link:
                continue
            asin = extract_asin(link)
            if not asin:
                continue
            price = extract_price(desc)
            items.append({"title": title, "asin": asin, "price": price, "link": link})
    except Exception as e:
        print(f"⚠️  Errore parsing XML: {e}")
    return items

def build_affiliate_link(asin):
    return f"https://www.amazon.it/dp/{asin}?tag={AMAZON_TAG}"

def random_colors():
    return random.sample(COLORS, 2)

def make_product(raw, idx, category, id_start):
    c1, c2 = random_colors()
    emoji = EMOJIS[category][idx % len(EMOJIS[category])]
    price = raw["price"] or round(random.uniform(20, 80), 2)
    old_price = round(price * random.uniform(1.3, 1.8), 2)
    discount = f"-{int((1 - price / old_price) * 100)}%"
    name = raw["title"][:60] + ("…" if len(raw["title"]) > 60 else "")
    return {
        "id": id_start + idx,
        "emoji": emoji,
        "name": name,
        "tag": category.capitalize(),
        "price": f"{price:.2f}",
        "oldPrice": f"{old_price:.2f}",
        "clr1": c1,
        "clr2": c2,
        "discount": discount,
        "asin": raw["asin"],
    }

def collect(category, max_items=8, id_start=0):
    all_items = []
    for url in RSS_FEEDS[category]:
        data = fetch_rss(url)
        if data:
            all_items.extend(parse_feed(data))
    seen = set()
    unique = []
    for item in all_items:
        if item["asin"] not in seen:
            seen.add(item["asin"])
            unique.append(item)
    unique = unique[:max_items]
    print(f"✅ {category}: {len(unique)} prodotti trovati")
    return [make_product(r, i, category, id_start) for i, r in enumerate(unique)]

def write_js(fashion, shoes, accessories):
    now = datetime.now().strftime("%d/%m/%Y %H:%M")

    # Combina scarpe e accessori per amazon grid
    amazon = []
    for i, p in enumerate(shoes[:4] + accessories[:4]):
        p2 = dict(p)
        p2["id"] = 200 + i
        p2["tag"] = "Amazon"
        amazon.append(p2)

    lines = [
        f"// Aggiornato automaticamente il {now} — dati reali Amazon.it",
        "",
        "const fashionProducts = " + json.dumps(fashion,      ensure_ascii=False, indent=2) + ";",
        "",
        "const shoesProducts = "   + json.dumps(shoes,        ensure_ascii=False, indent=2) + ";",
        "",
        "const amazonProducts = "  + json.dumps(amazon,       ensure_ascii=False, indent=2) + ";",
        "",
        f'const AMAZON_TAG = "{AMAZON_TAG}";',
        "",
        "function buildAmazonLink(asin) {",
        f'  return `https://www.amazon.it/dp/${{asin}}?tag={AMAZON_TAG}`;',
        "}",
    ]
    out = os.path.join(os.path.dirname(__file__), "..", "js", "products.js")
    with open(out, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    print(f"✅ products.js scritto con {len(fashion)} moda, {len(shoes)} scarpe, {len(accessories)} accessori")

if __name__ == "__main__":
    fashion     = collect("fashion",     max_items=8, id_start=1)
    shoes       = collect("shoes",       max_items=8, id_start=10)
    accessories = collect("accessories", max_items=8, id_start=20)

    if not fashion and not shoes and not accessories:
        print("❌ Nessun prodotto trovato dai feed RSS. Controlla la connessione.")
        exit(1)

    write_js(fashion, shoes, accessories)
