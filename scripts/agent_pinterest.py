#!/usr/bin/env python3
"""
EmporiumOnline — Agente Pinterest
Genera Pin per ogni prodotto e li pubblica via Pinterest API v5.
Senza credenziali: salva i pin in data/pinterest_queue.json pronti da copiare.
"""
import json, os, re, time, random
from datetime import datetime
from urllib.request import Request, urlopen
from urllib.parse import urlencode
from urllib.error import HTTPError

BASE_DIR = os.path.join(os.path.dirname(__file__), "..")
PRODUCTS_FILE = os.path.join(BASE_DIR, "data", "products.json")
QUEUE_FILE    = os.path.join(BASE_DIR, "data", "pinterest_queue.json")
LOG_FILE      = os.path.join(BASE_DIR, "data", "pinterest_log.json")

def _load_env():
    env_path = os.path.join(BASE_DIR, ".env")
    if os.path.exists(env_path):
        with open(env_path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, _, v = line.partition("=")
                    os.environ.setdefault(k.strip(), v.strip())
_load_env()

PINTEREST_TOKEN  = os.environ.get("PINTEREST_ACCESS_TOKEN", "")
PINTEREST_BOARD  = os.environ.get("PINTEREST_BOARD_ID", "")
SITE_URL         = "https://emporiumonline.it"
AMAZON_TAG       = "prezzotop08-21"

# Emoji e hashtag per categoria
CATEGORY_META = {
    "scarpe":        {"emoji": "👟👠", "hashtags": "#scarpe #scarpedonna #fashion #style #colorate #moda"},
    "abbigliamento": {"emoji": "👗🌈", "hashtags": "#moda #vestiti #outfit #fashion #donna #colori"},
    "accessori":     {"emoji": "💍✨", "hashtags": "#accessori #gioielli #moda #donna #stile #colorati"},
    "borse":         {"emoji": "👜🌸", "hashtags": "#borse #bag #fashion #donna #moda #colorata"},
    "casa":          {"emoji": "🏠🌈", "hashtags": "#casacolorata #homedecor #arredamento #decorazione #design"},
    "gadget":        {"emoji": "🎧✨", "hashtags": "#gadget #tech #colorato #regalo #hightech #accessories"},
    "beauty":        {"emoji": "💄🌈", "hashtags": "#beauty #makeupitalia #trucco #colorato #nail #glitter"},
    "idee-regalo":   {"emoji": "🎁🌟", "hashtags": "#regalo #ideeregalo #compleanno #donna #originale"},
}

TITOLI_TEMPLATE = [
    "{name} — scopri questa offerta su Amazon!",
    "✨ {name} — prezzo imperdibile!",
    "{emoji} {name}",
    "🛍️ Offerta del giorno: {name}",
    "{name} — qualità e colore per te!",
]

DESCRIZIONI_TEMPLATE = [
    "{emoji} {name}\n\n💰 Solo €{price} su Amazon!\n\n{hashtags}\n\n🔗 Vedi l'offerta → {link}",
    "Hai visto? {name} a soli €{price}!\n{emoji}\n\n{hashtags}\n\n👉 Clicca per l'offerta → {link}",
    "✨ {name}\n\nUn must-have colorato e di qualità!\n💸 Prezzo: €{price}\n\n{hashtags}\n\n🔗 {link}",
    "{emoji} La nostra scelta di oggi:\n{name}\n\n💰 €{price} con spedizione Amazon\n\n{hashtags}\n\n👉 {link}",
]


def load_products():
    with open(PRODUCTS_FILE) as f:
        data = json.load(f)
    return data.get("products", [])


def load_log():
    if not os.path.exists(LOG_FILE):
        return {"posted_asins": []}
    with open(LOG_FILE) as f:
        return json.load(f)


def save_log(log):
    with open(LOG_FILE, "w") as f:
        json.dump(log, f, ensure_ascii=False, indent=2)


def format_price(p):
    if p is None:
        return "N/D"
    return f"{p:.2f}".replace(".", ",")


def build_pin_content(product):
    cat   = product.get("category", "accessori")
    meta  = CATEGORY_META.get(cat, {"emoji": "✨", "hashtags": "#moda #colorato"})
    name  = product["name"]
    price = format_price(product.get("price"))
    asin  = product["asin"]
    link  = f"{SITE_URL}/#offerte"
    amz   = product.get("amazonLink", f"https://www.amazon.it/dp/{asin}?tag={AMAZON_TAG}")

    titolo = random.choice(TITOLI_TEMPLATE).format(
        name=name[:80], emoji=meta["emoji"], price=price
    )
    descrizione = random.choice(DESCRIZIONI_TEMPLATE).format(
        name=name[:100], emoji=meta["emoji"],
        price=price, hashtags=meta["hashtags"], link=amz
    )
    return {
        "asin": asin,
        "title": titolo[:100],
        "description": descrizione[:500],
        "image_url": product.get("image", ""),
        "link": amz,
        "board_id": PINTEREST_BOARD,
        "generated_at": datetime.now().isoformat(),
    }


def post_pin_api(pin):
    """Posta un pin via Pinterest API v5."""
    if not PINTEREST_TOKEN or not PINTEREST_BOARD:
        return None

    payload = json.dumps({
        "title": pin["title"],
        "description": pin["description"],
        "link": pin["link"],
        "board_id": pin["board_id"],
        "media_source": {
            "source_type": "image_url",
            "url": pin["image_url"],
        },
    }).encode()

    req = Request(
        "https://api.pinterest.com/v5/pins",
        data=payload,
        headers={
            "Authorization": f"Bearer {PINTEREST_TOKEN}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    try:
        resp = urlopen(req, timeout=15)
        result = json.loads(resp.read())
        return result.get("id")
    except HTTPError as e:
        print(f"    [API ERR] {e.code}: {e.read().decode()[:200]}")
        return None
    except Exception as e:
        print(f"    [ERR] {e}")
        return None


def main(count=5):
    print("=" * 60)
    print("  EMPORIUM — Agente Pinterest")
    print(f"  {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    has_api = bool(PINTEREST_TOKEN and PINTEREST_BOARD)
    print(f"  Modalità: {'📌 API Pinterest' if has_api else '📋 Coda locale'}")
    print("=" * 60)

    products = load_products()
    log      = load_log()
    posted   = set(log.get("posted_asins", []))

    # Prodotti non ancora postati su Pinterest
    todo = [p for p in products if p["asin"] not in posted and p.get("image","")]
    random.shuffle(todo)
    todo = todo[:count]

    if not todo:
        print("  Tutti i prodotti sono già stati postati su Pinterest.")
        return

    pins_generati = []
    for product in todo:
        pin = build_pin_content(product)
        print(f"\n  Prodotto: {product['name'][:60]}")
        print(f"  Titolo Pin: {pin['title'][:70]}")

        if has_api:
            pin_id = post_pin_api(pin)
            if pin_id:
                print(f"  [✅ POSTATO] Pin ID: {pin_id}")
                posted.add(product["asin"])
                pin["pin_id"] = pin_id
                pin["status"] = "posted"
            else:
                print(f"  [❌ ERRORE] Salvato in coda")
                pin["status"] = "queued"
        else:
            print(f"  [📋 CODA] Salvato (configura PINTEREST_ACCESS_TOKEN per postare)")
            pin["status"] = "queued"

        pins_generati.append(pin)
        time.sleep(random.uniform(1.5, 3.0))

    # Salva coda
    queue = []
    if os.path.exists(QUEUE_FILE):
        with open(QUEUE_FILE) as f:
            queue = json.load(f)
    queue = pins_generati + queue
    with open(QUEUE_FILE, "w", encoding="utf-8") as f:
        json.dump(queue, f, ensure_ascii=False, indent=2)

    # Aggiorna log
    log["posted_asins"] = list(posted)
    log["last_run"] = datetime.now().isoformat()
    save_log(log)

    postati  = sum(1 for p in pins_generati if p["status"] == "posted")
    in_coda  = sum(1 for p in pins_generati if p["status"] == "queued")
    print(f"\n{'='*60}")
    print(f"  Postati su Pinterest: {postati}")
    print(f"  In coda locale:       {in_coda}")
    print(f"  Coda salvata in:      data/pinterest_queue.json")
    print("=" * 60)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--count", type=int, default=5, help="Pin da generare")
    args = parser.parse_args()
    main(args.count)
