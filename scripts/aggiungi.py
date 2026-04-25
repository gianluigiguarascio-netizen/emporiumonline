#!/usr/bin/env python3
"""
EmporiumOnline — Aggiungi Prodotto
Uso: python3 scripts/aggiungi.py <url_o_asin> [categoria]

Esempi:
  python3 scripts/aggiungi.py https://www.amazon.it/dp/B0DBHRD535
  python3 scripts/aggiungi.py B0DBHRD535 tech
  python3 scripts/aggiungi.py B0DBHRD535 B0FLCS5FB2 B0D48KJW57
"""
import json
import os
import re
import sys

BASE_DIR = os.path.join(os.path.dirname(__file__), "..")
sys.path.insert(0, os.path.dirname(__file__))

from agent_products import (
    scrape_amazon_product, get_affiliate_image, build_product,
    load_products, save_products, generate_products_js,
    AMAZON_TAG, COLORS_BY_CATEGORY, KEYWORDS_EXCLUDED,
)
from datetime import datetime

# ── Categorie disponibili ──────────────────────────────────────
CATEGORIES = [
    "scarpe", "abbigliamento", "accessori", "borse",
    "casa", "gadget", "beauty", "idee-regalo", "tech",
]

CATEGORY_COLORS = {
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

CATEGORY_EMOJI = {
    "scarpe": "👟", "abbigliamento": "👗", "accessori": "👜",
    "borse": "🎒", "casa": "🏠", "gadget": "🎮",
    "beauty": "💄", "idee-regalo": "🎁", "tech": "📱",
}


def estrai_asin(testo):
    """Estrae ASIN da URL Amazon o stringa diretta."""
    for pat in [r'/dp/([A-Z0-9]{10})', r'/gp/product/([A-Z0-9]{10})', r'^([A-Z0-9]{10})$']:
        m = re.search(pat, testo.strip())
        if m:
            return m.group(1)
    return None


def chiedi_categoria(nome_prodotto):
    """Suggerisce una categoria e chiede conferma."""
    nome = nome_prodotto.lower()
    suggerimenti = {
        "scarpe": ["scarpa", "stival", "sandal", "sneaker", "mocassin", "décolleté", "ballerina"],
        "abbigliamento": ["vestit", "abito", "magliett", "camicia", "gonna", "giacca", "maglion", "felpa", "pantalone", "tuta", "kimono"],
        "accessori": ["collana", "orecchi", "braccial", "anello", "cintura", "occhial", "orologio", "sciarpa", "cappell"],
        "borse": ["borsa", "zaino", "borsett", "pochette", "tracolla", "wallet", "portafoglio"],
        "casa": ["cuscino", "vaso", "tappeto", "lampada", "candela", "decorazion", "piatto", "bicchier", "fiore", "fioriera"],
        "gadget": ["cover", "cuffie", "speaker", "caricator", "mouse", "tastier", "fidget", "gadget"],
        "beauty": ["rossetto", "ombretto", "palette", "smalto", "profum", "crema", "siero", "makeup", "matita"],
        "idee-regalo": ["regalo", "sorpresa", "set", "kit"],
        "tech": ["cavo", "usb", "telefon", "iphone", "samsung", "tablet", "laptop", "hdmi", "adattator"],
    }
    for cat, parole in suggerimenti.items():
        if any(p in nome for p in parole):
            return cat
    return "accessori"


def aggiungi_prodotto(asin, categoria=None):
    print(f"\n🔍 Scarico dati per ASIN: {asin}")
    dati = scrape_amazon_product(asin)

    if not dati or not dati.get("title"):
        print(f"  ❌ Impossibile recuperare dati per {asin}")
        print(f"     Link affiliato: https://www.amazon.it/dp/{asin}?tag={AMAZON_TAG}")
        return None

    titolo = dati["title"]
    prezzo = dati.get("price")
    immagine = dati.get("image") or get_affiliate_image(asin)

    print(f"  ✅ {titolo[:80]}")
    if prezzo:
        print(f"  💶 Prezzo: €{prezzo:.2f}")
    print(f"  🖼️  Immagine: {'trovata' if dati.get('image') else 'widget affiliato'}")

    # Determina categoria
    if not categoria:
        categoria = chiedi_categoria(titolo)
        print(f"  📂 Categoria: {categoria}")

    clr1, clr2 = CATEGORY_COLORS.get(categoria, ("#a78bfa", "#818cf8"))
    emoji = CATEGORY_EMOJI.get(categoria, "🛍️")

    prodotto = {
        "id": f"{categoria}-{asin}",
        "asin": asin,
        "name": titolo[:120],
        "category": categoria,
        "emoji": emoji,
        "price": prezzo,
        "oldPrice": None,
        "discount": None,
        "image": immagine,
        "amazonLink": f"https://www.amazon.it/dp/{asin}?tag={AMAZON_TAG}",
        "clr1": clr1,
        "clr2": clr2,
        "offerBadge": True,
        "importedAt": datetime.now().isoformat(),
        "status": "published",
    }

    print(f"  📂 Categoria: {categoria}")
    return prodotto


def main():
    args = sys.argv[1:]

    if not args or args[0] in ("-h", "--help"):
        print(__doc__)
        sys.exit(0)

    # Estrai ASIN e eventuale categoria dagli argomenti
    asins = []
    categoria_forzata = None
    for a in args:
        asin = estrai_asin(a)
        if asin:
            asins.append(asin)
        elif a.lower() in CATEGORIES:
            categoria_forzata = a.lower()
        else:
            print(f"⚠️  Non riconosco '{a}' come ASIN o categoria valida, lo salto.")

    if not asins:
        print("❌ Nessun ASIN valido trovato negli argomenti.")
        print("   Usa: python3 scripts/aggiungi.py <url_amazon_o_asin>")
        sys.exit(1)

    # Carica prodotti esistenti
    esistenti = load_products()
    asin_esistenti = {p["asin"] for p in esistenti}

    nuovi = []
    for asin in asins:
        if asin in asin_esistenti:
            print(f"\n⚠️  {asin} già presente nel catalogo, salto.")
            continue
        prodotto = aggiungi_prodotto(asin, categoria_forzata)
        if prodotto:
            nuovi.append(prodotto)
            asin_esistenti.add(asin)

    if not nuovi:
        print("\nNessun nuovo prodotto da aggiungere.")
        sys.exit(0)

    # Salva
    tutti = nuovi + esistenti
    save_products(tutti)
    generate_products_js(tutti)

    print(f"\n{'='*50}")
    print(f"✅ Aggiunti {len(nuovi)} prodotti. Totale: {len(tutti)}")
    for p in nuovi:
        print(f"   • [{p['category']}] {p['name'][:60]}")
    print(f"\n📦 Prossimo passo:")
    print(f"   cd /Users/admin/emporiumonline")
    print(f"   git add -A && git commit -m 'feat: aggiungi prodotti' && git push")
    print(f"{'='*50}\n")


if __name__ == "__main__":
    main()
