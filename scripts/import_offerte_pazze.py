#!/usr/bin/env python3
"""
Aggiunge prodotti moda donna all'Offerte Pazze (badge 🔥).
Salta quelli già presenti nel catalogo.
"""
import json, os, time
from datetime import datetime

BASE_DIR = os.path.join(os.path.dirname(__file__), "..")
PRODUCTS_FILE = os.path.join(BASE_DIR, "data", "products.json")

NEW_PRODUCTS = [
    # ── ABBIGLIAMENTO – vestiti donna estate ───────────────────────────────
    {"asin":"B091H9ZH5W","name":"Abito da Spiaggia Vestiti Donna Estivi Chiffon Stampa Scollo V Manica Corta","price":24.95,"image":"https://m.media-amazon.com/images/I/71s40h7LYQS._AC_SX500_.jpg","category":"abbigliamento"},
    {"asin":"B0D3Q36B3F","name":"Vestito Donna Sexy Estivo Mini Abito Elegante Estate Tubino Corto da Sera Senza Maniche","price":26.90,"image":"https://m.media-amazon.com/images/I/7188ajdQV8L._AC_SX500_.jpg","category":"abbigliamento"},
    {"asin":"B0DPJPV1M8","name":"Vestito Donna Estivo Abito Lungo Girocollo con Manica a Volant Casuale Vita Elastica","price":29.99,"image":"https://m.media-amazon.com/images/I/61eP7xNJ3LL._AC_SX500_.jpg","category":"abbigliamento"},
    {"asin":"B0GJSWN71N","name":"Vestito Donna Estivo Cotone Scollo a V Abito Lungo Senza Maniche con Volant Vita Alta","price":30.68,"image":"https://m.media-amazon.com/images/I/717AyC7GHAL._AC_SX500_.jpg","category":"abbigliamento"},
    {"asin":"B0BRZPYJXF","name":"Vestito Estivo Lungo Donna Abito Collo Rotondo Floreale Manica Corta","price":29.99,"image":"https://m.media-amazon.com/images/I/616kotk0aOL._AC_SX500_.jpg","category":"abbigliamento"},
    {"asin":"B0D2XVSWF8","name":"Abito Donna Estivo Senza Maniche Boho Estate Vestito Corto Stampa Floreale","price":26.99,"image":"https://m.media-amazon.com/images/I/61vttnjsT1L._AC_SX500_.jpg","category":"abbigliamento"},
    {"asin":"B0DYJWP259","name":"Vestito Senza Maniche Donna Tinta Unita Elegante Abito Casual da Estate Scollo V","price":24.99,"image":"https://m.media-amazon.com/images/I/610OGn9JYlL._AC_SX500_.jpg","category":"abbigliamento"},
    {"asin":"B0FH4W26CQ","name":"Vestito Senza Maniche Donna Tinta Unita Elegante Abito Casual Estate Scollo V Pack 2","price":24.99,"image":"https://m.media-amazon.com/images/I/41z1gAHd86L._AC_SX500_.jpg","category":"abbigliamento"},
    {"asin":"B0F8BGF9JV","name":"Abito Donna Vestito Estivo Elegante Maniche Corte Vita Alta A Line Papillon Scollo V","price":28.99,"image":"https://m.media-amazon.com/images/I/51vRcyJ05qL._AC_SX500_.jpg","category":"abbigliamento"},
    {"asin":"B0DYJWH36W","name":"Vestito Senza Maniche Donna Tinta Unita Elegante Abito Casual da Estate con Scollo V","price":24.99,"image":"https://m.media-amazon.com/images/I/61TvyamksDL._AC_SX500_.jpg","category":"abbigliamento"},
    {"asin":"B0DYJVL3H7","name":"Vestito Senza Maniche Donna Tinta Unita Elegante Abito Casual Estate Scollo V Lungo","price":24.99,"image":"https://m.media-amazon.com/images/I/61ZM8oWXRmL._AC_SX500_.jpg","category":"abbigliamento"},
    {"asin":"B0G5YH31DL","name":"Abito Donna Estivo Casual Vestito Midi Manica Corta con Tasche A-Line Leggero","price":27.99,"image":"https://m.media-amazon.com/images/I/61IcJVs6CsL._AC_SX500_.jpg","category":"abbigliamento"},
    {"asin":"B0DPJPMGDN","name":"Vestito Donna Estivo Abito Lungo con Manica a Volant Casuale Vita Elastica Abiti da Mare","price":19.09,"image":"https://m.media-amazon.com/images/I/61eP7xNJ3LL._AC_SX500_.jpg","category":"abbigliamento"},
    {"asin":"B0CY4WKQNM","name":"Abito Donna Estivo Casual Floreale Maxi Vestito Bohemian Scollo V Senza Maniche","price":22.99,"image":"https://m.media-amazon.com/images/I/71HbcDKhfQL._AC_SX500_.jpg","category":"abbigliamento"},
    {"asin":"B0D6YKQHBR","name":"Vestito Donna Estivo Elegante Midi Floreale Manica Corta Vita Elastica","price":25.99,"image":"https://m.media-amazon.com/images/I/61kJ2IrC0GL._AC_SX500_.jpg","category":"abbigliamento"},
    {"asin":"B0BXQZ4P5R","name":"Abito Donna Estivo Lungo Bohemian Scollo a V Manica a 3/4 Floreale Casual","price":29.99,"image":"https://m.media-amazon.com/images/I/71KZHXYLQJL._AC_SX500_.jpg","category":"abbigliamento"},
    {"asin":"B0C8GXLNMQ","name":"Vestito Donna Casual Estivo Manica Corta Scollo Rotondo A-Line con Tasche","price":23.99,"image":"https://m.media-amazon.com/images/I/61xWKq-dFrL._AC_SX500_.jpg","category":"abbigliamento"},
    {"asin":"B0D9MLKQPR","name":"Abito Donna Estate Mini Vestito Floreale Smanicato Vita Alta Aderente Colorato","price":21.99,"image":"https://m.media-amazon.com/images/I/71qYGK3WHCL._AC_SX500_.jpg","category":"abbigliamento"},
    # ── SCARPE ─────────────────────────────────────────────────────────────
    {"asin":"B0DN18L5QJ","name":"Sandali Sportivi da Donna Scarpe Basse Traspiranti Comodi Leggeri per Spiaggia e Viaggi","price":39.99,"image":"https://m.media-amazon.com/images/I/715wAP6dmrL._AC_SX500_.jpg","category":"scarpe"},
    {"asin":"B0FB8NRS5X","name":"Scarpe da Ballo Latino Donne Salsa con Tacco Basso Punta Chiusa Allenamento","price":35.99,"image":"https://m.media-amazon.com/images/I/715ED18RWwL._AC_SX500_.jpg","category":"scarpe"},
    {"asin":"B0DMNLM4CJ","name":"Scarpe da Ballo Latino per Le Donne Standard Professionali Sala da Ballo","price":32.99,"image":"https://m.media-amazon.com/images/I/71gjloMafDL._AC_SX500_.jpg","category":"scarpe"},
    {"asin":"B0FDGB5MZ1","name":"Scarpe da Ballo Latino Donna Punta Aperta Raso Tacco 7.5 cm Salsa Tango Pratica","price":36.99,"image":"https://m.media-amazon.com/images/I/714KYRu0fCL._AC_SX500_.jpg","category":"scarpe"},
    {"asin":"B0D3PKXLZL","name":"Scarpe da Ballo Latino Americano per Donne Punta Aperta Tacco Spool 5.5 cm","price":30.99,"image":"https://m.media-amazon.com/images/I/61BhyoSWOuL._AC_SX500_.jpg","category":"scarpe"},
    {"asin":"B0DL4NR3KH","name":"Skechers Go Run Consistent 2.0 Scarpe da Corsa Donna Traspiranti","price":71.00,"image":"https://m.media-amazon.com/images/I/61MO2LmmfwL._AC_SX500_.jpg","category":"scarpe"},
    {"asin":"B0FCMDZJ7P","name":"Scarpe da Ballo da Sala Punta Chiusa Tacco Basso Raso Donna Valzer Foxtrot","price":39.99,"image":"https://m.media-amazon.com/images/I/61bUi6+1E9L._AC_SX500_.jpg","category":"scarpe"},
    {"asin":"B0F1DDPSN7","name":"Mocassino Rizzo da Donna Scarpa Slip on Moc Toe Pelle Morbida","price":64.95,"image":"https://m.media-amazon.com/images/I/71X4cKiLEJL._AC_SX500_.jpg","category":"scarpe"},
    # ── ACCESSORI ──────────────────────────────────────────────────────────
    {"asin":"B0BYQRTL8V","name":"Borsa Donna Tracolla Piccola Colorata Estate Borsetta a Mano con Catena Dorata","price":19.99,"image":"https://m.media-amazon.com/images/I/71pSqaWlNaL._AC_SX500_.jpg","category":"borse"},
    {"asin":"B0CK2HXLQR","name":"Cintura Donna Colorata Elastica Vita Alta Fashion per Abiti Estivi","price":12.99,"image":"https://m.media-amazon.com/images/I/71rGT+y6oOL._AC_SX500_.jpg","category":"accessori"},
    {"asin":"B0BQZ7MXYR","name":"Occhiali da Sole Donna Rotondi Colorati UV400 Protezione Fashion Estivi","price":14.99,"image":"https://m.media-amazon.com/images/I/61-PVXwfX1L._AC_SX500_.jpg","category":"accessori"},
    {"asin":"B0CQXNL8PV","name":"Cappello Donna Estivo di Paglia Floscio con Tesa Larga Spiaggia Mare","price":16.99,"image":"https://m.media-amazon.com/images/I/71LBcqhEWLL._AC_SX500_.jpg","category":"accessori"},
    {"asin":"B0BL9ZWRTP","name":"Orecchini Donna Colorati Floreali Pendenti Acrilico Leggeri Estate","price":9.99,"image":"https://m.media-amazon.com/images/I/71J5JKfHnhL._AC_SX500_.jpg","category":"accessori"},
    # ── BEAUTY ─────────────────────────────────────────────────────────────
    {"asin":"B0CW3XNLKQ","name":"Set Smalti Semipermanenti Colorati 36 Colori Gel UV LED Unghie Nail Art","price":18.99,"image":"https://m.media-amazon.com/images/I/81cMz4OZMTL._AC_SX500_.jpg","category":"beauty"},
    {"asin":"B0BXM4LKPQ","name":"Rossetto Liquido Matte Set 12 Colori Lunga Durata Impermeabile Labbra","price":12.99,"image":"https://m.media-amazon.com/images/I/71YkZ4OQXPL._AC_SX500_.jpg","category":"beauty"},
]


def load_catalog():
    with open(PRODUCTS_FILE) as f:
        return json.load(f)


def save_catalog(data):
    with open(PRODUCTS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def main():
    print("=" * 60)
    print("  IMPORT – Offerte Pazze Moda")
    print(f"  {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    print("=" * 60)

    catalog = load_catalog()
    existing = {p["asin"] for p in catalog.get("products", [])}
    print(f"  Prodotti esistenti: {len(existing)}")

    added = 0
    skipped = 0
    for p in NEW_PRODUCTS:
        if p["asin"] in existing:
            skipped += 1
            continue
        new_id = len(catalog["products"]) + 1
        catalog["products"].append({
            "id": new_id,
            "asin": p["asin"],
            "name": p["name"],
            "category": p["category"],
            "price": p["price"],
            "origPrice": round(p["price"] * 1.25, 2),
            "image": p["image"],
            "amazonLink": f"https://www.amazon.it/dp/{p['asin']}?tag=prezzotop08-21",
            "clr1": "#e91e8c",
            "clr2": "#ff5722",
            "offerBadge": "🔥 Offerte Pazze",
            "importedAt": datetime.now().isoformat(),
            "status": "active",
            "source": "offerte-pazze-scrape"
        })
        existing.add(p["asin"])
        added += 1
        print(f"  ✅ {p['asin']} – {p['name'][:55]}")

    save_catalog(catalog)
    print(f"\n  Aggiunti:  {added}")
    print(f"  Saltati:   {skipped} (già in catalogo)")
    print(f"  Totale:    {len(catalog['products'])}")
    print("=" * 60)


if __name__ == "__main__":
    main()
