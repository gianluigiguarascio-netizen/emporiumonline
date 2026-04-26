#!/usr/bin/env python3
"""
EmporiumOnline — Agente SEO
Genera sitemap.xml aggiornata e inietta JSON-LD strutturati per ogni prodotto.
Da eseguire dopo ogni aggiornamento del catalogo.
"""
import json, os
from datetime import datetime

BASE_DIR = os.path.join(os.path.dirname(__file__), "..")
PRODUCTS_FILE = os.path.join(BASE_DIR, "data", "products.json")
SITEMAP_FILE  = os.path.join(BASE_DIR, "sitemap.xml")
JSONLD_FILE   = os.path.join(BASE_DIR, "js", "seo_jsonld.js")
SITE_URL      = "https://emporiumonline.it"

CATEGORIES = ["scarpe","abbigliamento","accessori","borse","casa","gadget","beauty","idee-regalo"]


def load_products():
    with open(PRODUCTS_FILE) as f:
        return json.load(f).get("products", [])


def generate_sitemap(products):
    today = datetime.now().strftime("%Y-%m-%d")
    urls = []

    # Homepage
    urls.append(f"""  <url>
    <loc>{SITE_URL}/</loc>
    <lastmod>{today}</lastmod>
    <changefreq>daily</changefreq>
    <priority>1.0</priority>
  </url>""")

    # Pagine statiche
    for page, freq, prio in [
        ("affiliate.html", "monthly", "0.4"),
        ("privacy.html",   "monthly", "0.3"),
    ]:
        urls.append(f"""  <url>
    <loc>{SITE_URL}/{page}</loc>
    <lastmod>{today}</lastmod>
    <changefreq>{freq}</changefreq>
    <priority>{prio}</priority>
  </url>""")

    # Pagine categoria (anchor su homepage)
    for cat in CATEGORIES:
        urls.append(f"""  <url>
    <loc>{SITE_URL}/#cat-{cat}</loc>
    <lastmod>{today}</lastmod>
    <changefreq>daily</changefreq>
    <priority>0.8</priority>
  </url>""")

    # Prodotti (link Amazon con tag)
    for p in products:
        asin = p.get("asin","")
        if not asin: continue
        amz  = p.get("amazonLink", f"https://www.amazon.it/dp/{asin}?tag=prezzotop08-21")
        # Non indicizziamo link Amazon esterni — solo i tag prodotto interni
        urls.append(f"""  <url>
    <loc>{SITE_URL}/#prodotto-{asin}</loc>
    <lastmod>{today}</lastmod>
    <changefreq>weekly</changefreq>
    <priority>0.6</priority>
  </url>""")

    sitemap = f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
{chr(10).join(urls)}
</urlset>"""

    with open(SITEMAP_FILE, "w", encoding="utf-8") as f:
        f.write(sitemap)
    print(f"  ✅ sitemap.xml → {len(urls)} URL")


def generate_jsonld(products):
    """Genera un JS che inietta JSON-LD structured data per ogni prodotto."""

    # JSON-LD ItemList per la homepage
    item_list_elements = []
    for i, p in enumerate(products[:20], 1):  # Prime 20 per non appesantire
        asin  = p.get("asin","")
        name  = p.get("name","").replace('"', '\\"')
        price = p.get("price")
        image = p.get("image","")
        url   = p.get("amazonLink", f"https://www.amazon.it/dp/{asin}?tag=prezzotop08-21")
        if not asin: continue
        item_list_elements.append({
            "@type": "ListItem",
            "position": i,
            "item": {
                "@type": "Product",
                "name": p.get("name","")[:120],
                "image": image,
                "url": url,
                **({"offers": {
                    "@type": "Offer",
                    "price": str(price),
                    "priceCurrency": "EUR",
                    "availability": "https://schema.org/InStock",
                    "url": url,
                }} if price else {}),
            }
        })

    jsonld_itemlist = {
        "@context": "https://schema.org",
        "@type": "ItemList",
        "name": "Offerte Colorate EmporiumOnline",
        "description": "Selezione giornaliera di prodotti colorati da Amazon",
        "url": SITE_URL,
        "numberOfItems": len(products),
        "itemListElement": item_list_elements,
    }

    # BreadcrumbList
    breadcrumb = {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "EmporiumOnline", "item": SITE_URL},
            {"@type": "ListItem", "position": 2, "name": "Offerte Amazon", "item": f"{SITE_URL}/#offerte"},
        ]
    }

    js_content = f"""// SEO JSON-LD — generato da agent_seo.py il {datetime.now().strftime('%d/%m/%Y %H:%M')}
// NON modificare manualmente
(function() {{
  function injectJsonLd(data) {{
    var s = document.createElement('script');
    s.type = 'application/ld+json';
    s.text = JSON.stringify(data);
    document.head.appendChild(s);
  }}
  injectJsonLd({json.dumps(jsonld_itemlist, ensure_ascii=False)});
  injectJsonLd({json.dumps(breadcrumb, ensure_ascii=False)});
}})();
"""
    with open(JSONLD_FILE, "w", encoding="utf-8") as f:
        f.write(js_content)
    print(f"  ✅ seo_jsonld.js → {len(item_list_elements)} prodotti strutturati")


def main():
    print("=" * 60)
    print("  EMPORIUM — Agente SEO")
    print(f"  {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    print("=" * 60)
    products = load_products()
    print(f"  Prodotti nel catalogo: {len(products)}")
    generate_sitemap(products)
    generate_jsonld(products)
    print("=" * 60)


if __name__ == "__main__":
    main()
