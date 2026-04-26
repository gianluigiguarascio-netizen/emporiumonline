#!/usr/bin/env python3
"""
EmporiumOnline — Agente Instagram
Genera caption + hashtag per ogni prodotto e li pubblica via Instagram Graph API.
Senza credenziali: salva i post in data/instagram_queue.json pronti da copiare.
"""
import json, os, re, time, random
from datetime import datetime
from urllib.request import Request, urlopen
from urllib.error import HTTPError

BASE_DIR = os.path.join(os.path.dirname(__file__), "..")
PRODUCTS_FILE = os.path.join(BASE_DIR, "data", "products.json")
QUEUE_FILE    = os.path.join(BASE_DIR, "data", "instagram_queue.json")
LOG_FILE      = os.path.join(BASE_DIR, "data", "instagram_log.json")

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

IG_USER_ID   = os.environ.get("INSTAGRAM_USER_ID", "")
IG_TOKEN     = os.environ.get("INSTAGRAM_ACCESS_TOKEN", "")
SITE_URL     = "https://emporiumonline.it"
AMAZON_TAG   = "prezzotop08-21"

CATEGORY_META = {
    "scarpe": {
        "emoji": "👟👠✨",
        "hashtags": (
            "#scarpe #scarpedonna #scarpenuove #fashionitalia #outfitdonna "
            "#stiledonna #moda #modaitaliana #shoes #womensfashion "
            "#sneakers #lookdonna #fashionblogger #shopping #amazon"
        ),
        "hook": ["Hai già visto queste scarpe?? 😍", "Le scarpe perfette per l'estate 🌸", "QUESTE SCARPE THO 😭✨"],
    },
    "abbigliamento": {
        "emoji": "👗🌈💫",
        "hashtags": (
            "#moda #modadonna #outfit #outfitdonna #vestiti #lookdelpgiorno "
            "#fashionitalia #ootd #styleinspo #abbigliamento #estate "
            "#vestito #colori #womensfashion #amazon"
        ),
        "hook": ["Il vestito dei tuoi sogni 🌈", "Questo outfit è un ✨MUST✨", "Quanto è bello questo look? 😍"],
    },
    "accessori": {
        "emoji": "💍✨🌸",
        "hashtags": (
            "#accessori #gioielli #bijoux #collana #orecchini #bracciale "
            "#fashionitalia #moda #jewelry #accessories #stile "
            "#modadonna #lookdonna #shopping #amazon"
        ),
        "hook": ["Gli accessori che completano tutto 💍", "Piccoli dettagli, grande stile ✨", "Non puoi non averli 😍"],
    },
    "borse": {
        "emoji": "👜💛🌼",
        "hashtags": (
            "#borse #bag #borsa #borsadonna #fashionbag #handbag "
            "#modadonna #fashionitalia #accessories #ootd "
            "#borsenuove #shopping #stile #look #amazon"
        ),
        "hook": ["La borsa che cercavi è qui 👜", "Colori che fanno innamorare 🌈", "Questa borsa è un SOGNO 😭"],
    },
    "casa": {
        "emoji": "🏠✨🌈",
        "hashtags": (
            "#casacolorata #homedecor #arredamento #decorazionecasa #interior "
            "#homedesign #casabella #livingroom #deco #interiordesign "
            "#idecor #homeinspiration #abitare #design #amazon"
        ),
        "hook": ["La tua casa merita colore 🎨", "Trasforma casa con questi dettagli ✨", "Decora con stile e colore 🌈"],
    },
    "gadget": {
        "emoji": "🎧⚡✨",
        "hashtags": (
            "#gadget #tech #tecnologia #cuffie #bluetooth #wireless "
            "#techitalia #amazon #shopping #hightech #electronica "
            "#gadgettech #musica #accessories #regalo"
        ),
        "hook": ["Il gadget del momento ⚡", "Tech + colore = perfezione 🎧", "Non puoi vivere senza questo 😍"],
    },
    "beauty": {
        "emoji": "💄🌟💅",
        "hashtags": (
            "#beauty #makeupitalia #trucco #makeup #makeuplook #beautylover "
            "#nailart #smalto #palette #glitter #makeuptutorial "
            "#beautyinfluencer #cosmetici #shopping #amazon"
        ),
        "hook": ["Il trucco perfetto inizia da qui 💄", "Colori che fanno impazzire 🌈", "Beauty vibes solo ✨"],
    },
    "idee-regalo": {
        "emoji": "🎁🌟💝",
        "hashtags": (
            "#regalo #ideeregalo #compleanno #regalooriginale #giftideas "
            "#regalodonna #amazon #shopping #feastadellamamma "
            "#regaloperfetto #surprise #dono #gift #surprise #originale"
        ),
        "hook": ["Non sai cosa regalare? 🎁", "Il regalo perfetto esiste ✨", "Idea regalo che fa colpo 😍"],
    },
}

CAPTION_TEMPLATE = [
    """{hook}

{emoji} {name}

💰 Solo €{price} su Amazon!

Per trovare l'offerta cerca "{name_short}" su Amazon oppure visita il link in bio 👆

{hashtags}""",

    """{hook}

✨ {name}

🛍️ Prezzo: €{price}
📦 Spedizione Amazon veloce

👉 Link diretto in bio!

{hashtags}""",

    """{emoji} {name}

{hook}

💸 €{price} — offerta a tempo!
🔗 Trovalo su Amazon (link in bio)

{hashtags}""",

    """🌈 Prodotto del giorno:

{name}

{emoji} {hook}
💰 Prezzo: €{price}

🛒 Link in bio per l'offerta completa!

{hashtags}""",
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
    if p is None: return "N/D"
    return f"{p:.2f}".replace(".", ",")


def build_post_content(product):
    cat   = product.get("category", "accessori")
    meta  = CATEGORY_META.get(cat, CATEGORY_META["accessori"])
    name  = product["name"]
    price = format_price(product.get("price"))
    asin  = product["asin"]

    hook       = random.choice(meta["hook"])
    name_short = name[:40]
    caption    = random.choice(CAPTION_TEMPLATE).format(
        hook=hook, emoji=meta["emoji"],
        name=name[:100], name_short=name_short,
        price=price, hashtags=meta["hashtags"],
    )
    return {
        "asin": asin,
        "caption": caption[:2200],
        "image_url": product.get("image", ""),
        "amazon_link": product.get("amazonLink", f"https://www.amazon.it/dp/{asin}?tag={AMAZON_TAG}"),
        "category": cat,
        "generated_at": datetime.now().isoformat(),
    }


def post_instagram_api(post):
    """Pubblica su Instagram via Graph API (richiede account Business/Creator)."""
    if not IG_USER_ID or not IG_TOKEN:
        return None

    # Step 1: crea container media
    container_url = f"https://graph.facebook.com/v19.0/{IG_USER_ID}/media"
    data = {
        "image_url": post["image_url"],
        "caption": post["caption"],
        "access_token": IG_TOKEN,
    }
    req = Request(
        container_url,
        data=json.dumps(data).encode(),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        resp   = urlopen(req, timeout=20)
        result = json.loads(resp.read())
        container_id = result.get("id")
        if not container_id:
            print(f"    [ERR container] {result}")
            return None
    except HTTPError as e:
        print(f"    [API ERR] {e.code}: {e.read().decode()[:200]}")
        return None

    time.sleep(3)

    # Step 2: pubblica il container
    publish_url = f"https://graph.facebook.com/v19.0/{IG_USER_ID}/media_publish"
    pub_data = {"creation_id": container_id, "access_token": IG_TOKEN}
    req2 = Request(
        publish_url,
        data=json.dumps(pub_data).encode(),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        resp2  = urlopen(req2, timeout=20)
        result2 = json.loads(resp2.read())
        return result2.get("id")
    except HTTPError as e:
        print(f"    [PUBLISH ERR] {e.code}: {e.read().decode()[:200]}")
        return None


def main(count=3):
    print("=" * 60)
    print("  EMPORIUM — Agente Instagram")
    print(f"  {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    has_api = bool(IG_USER_ID and IG_TOKEN)
    print(f"  Modalità: {'📸 API Instagram' if has_api else '📋 Coda locale'}")
    print("=" * 60)

    products = load_products()
    log      = load_log()
    posted   = set(log.get("posted_asins", []))

    todo = [p for p in products if p["asin"] not in posted and p.get("image","")]
    random.shuffle(todo)
    todo = todo[:count]

    if not todo:
        print("  Tutti i prodotti sono già stati postati su Instagram.")
        return

    posts_generati = []
    for product in todo:
        post = build_post_content(product)
        print(f"\n  Prodotto: {product['name'][:60]}")
        print(f"  Caption preview: {post['caption'][:80]}...")

        if has_api:
            post_id = post_instagram_api(post)
            if post_id:
                print(f"  [✅ POSTATO] Post ID: {post_id}")
                posted.add(product["asin"])
                post["post_id"] = post_id
                post["status"] = "posted"
            else:
                print(f"  [❌ ERRORE] Salvato in coda")
                post["status"] = "queued"
        else:
            print(f"  [📋 CODA] Salvato (configura INSTAGRAM_USER_ID + INSTAGRAM_ACCESS_TOKEN)")
            post["status"] = "queued"

        posts_generati.append(post)
        time.sleep(random.uniform(2.0, 4.0))

    # Salva coda
    queue = []
    if os.path.exists(QUEUE_FILE):
        with open(QUEUE_FILE) as f:
            queue = json.load(f)
    queue = posts_generati + queue
    with open(QUEUE_FILE, "w", encoding="utf-8") as f:
        json.dump(queue, f, ensure_ascii=False, indent=2)

    log["posted_asins"] = list(posted)
    log["last_run"] = datetime.now().isoformat()
    save_log(log)

    postati = sum(1 for p in posts_generati if p["status"] == "posted")
    in_coda = sum(1 for p in posts_generati if p["status"] == "queued")
    print(f"\n{'='*60}")
    print(f"  Postati su Instagram: {postati}")
    print(f"  In coda locale:       {in_coda}")
    print(f"  Coda salvata in:      data/instagram_queue.json")
    print("=" * 60)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--count", type=int, default=3, help="Post da generare")
    args = parser.parse_args()
    main(args.count)
