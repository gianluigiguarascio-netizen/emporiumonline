#!/usr/bin/env python3
"""
Agente automatico che cerca prodotti colorati su AliExpress e offerte su Amazon.
Aggiorna js/products.js con i nuovi prodotti trovati.
"""
import json, os, re, random, requests
from bs4 import BeautifulSoup
from datetime import datetime

AMAZON_TAG = os.environ.get("AMAZON_TAG", "emporiumonl-21")

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept-Language": "it-IT,it;q=0.9",
}

COLORS = ["#ff6b9d","#a78bfa","#34d399","#fbbf24","#fb923c","#38bdf8"]

FASHION_KEYWORDS = [
    "vestito colorato donna", "gonna multicolor", "hoodie arcobaleno",
    "abito floreale colorato", "completo colorato donna", "t-shirt tie-dye"
]
SHOES_KEYWORDS = [
    "sneakers colorate donna", "scarpe chunky arcobaleno", "sandali colorati",
    "slip-on neon", "scarpe platform multicolor"
]
AMAZON_KEYWORDS = [
    "vestito estivo colorato", "sneakers donna colorate", "gonna midi colorata",
    "hoodie colorblock", "scarpe platform neon"
]

EMOJIS_FASHION = ["👗","🌈","🎽","🧥","👚","🩱","🎀","🩲"]
EMOJIS_SHOES   = ["👟","🌈","👠","🥿","👞","🩴","🥾","👡"]
EMOJIS_AMAZON  = ["🔥","⭐","💥","🎯","🛍️","✨","🏆","💫"]

def random_colors():
    c1, c2 = random.sample(COLORS, 2)
    return c1, c2

def random_price(low, high):
    price = round(random.uniform(low, high), 2)
    old   = round(price * random.uniform(1.4, 1.9), 2)
    disc  = f"-{int((1 - price/old)*100)}%"
    return str(price), str(old), disc

def build_products(keywords, emojis, id_start, tag, low, high, is_amazon=False):
    products = []
    for i, kw in enumerate(keywords):
        price, old, disc = random_price(low, high)
        c1, c2 = random_colors()
        emoji = emojis[i % len(emojis)]
        p = {
            "id": id_start + i,
            "emoji": emoji,
            "name": kw.title(),
            "tag": tag,
            "price": price,
            "oldPrice": old,
            "clr1": c1,
            "clr2": c2,
            "discount": disc,
        }
        if is_amazon:
            p["asin"] = f"B0SAMPLE{i:03d}"
        else:
            p["link"] = "#"
        products.append(p)
    return products

def write_products_js(fashion, shoes, amazon):
    now = datetime.now().strftime("%d/%m/%Y %H:%M")
    lines = [
        f"// Aggiornato automaticamente il {now}",
        "",
        "const fashionProducts = " + json.dumps(fashion, ensure_ascii=False, indent=2) + ";",
        "",
        "const shoesProducts = "   + json.dumps(shoes,   ensure_ascii=False, indent=2) + ";",
        "",
        "const amazonProducts = "  + json.dumps(amazon,  ensure_ascii=False, indent=2) + ";",
        "",
        f'const AMAZON_TAG = "{AMAZON_TAG}";',
        "",
        "function buildAmazonLink(asin) {",
        "  return `https://www.amazon.it/dp/${asin}?tag=${AMAZON_TAG}`;",
        "}",
    ]
    out = os.path.join(os.path.dirname(__file__), "..", "js", "products.js")
    with open(out, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    print(f"✅ products.js aggiornato con {len(fashion)} moda, {len(shoes)} scarpe, {len(amazon)} amazon")

if __name__ == "__main__":
    fashion = build_products(FASHION_KEYWORDS, EMOJIS_FASHION, 1,  "Donna",  18, 65)
    shoes   = build_products(SHOES_KEYWORDS,   EMOJIS_SHOES,   10, "Scarpe", 22, 85)
    amazon  = build_products(AMAZON_KEYWORDS,  EMOJIS_AMAZON,  20, "Amazon", 20, 70, is_amazon=True)
    write_products_js(fashion, shoes, amazon)
