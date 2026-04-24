#!/usr/bin/env python3
"""
Integrazione Amazon Product Advertising API v5.
Supporta:
  A) API ufficiale Amazon PA-API v5
  B) Inserimento manuale ASIN
  C) Importazione semi-automatica da lista ASIN
  D) Fallback con placeholder se API non disponibile
"""
import hashlib
import hmac
import json
import os
import re
import sys
from datetime import datetime, timezone
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError

# Carica .env se presente
def load_env():
    env_path = os.path.join(os.path.dirname(__file__), "..", ".env")
    if os.path.exists(env_path):
        with open(env_path, "r") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, _, val = line.partition("=")
                    os.environ.setdefault(key.strip(), val.strip())

load_env()

# Configurazione
ACCESS_KEY = os.environ.get("AMAZON_ACCESS_KEY", "")
SECRET_KEY = os.environ.get("AMAZON_SECRET_KEY", "")
PARTNER_TAG = os.environ.get("AMAZON_PARTNER_TAG", "prezzotop08-21")
MARKETPLACE = os.environ.get("AMAZON_MARKETPLACE", "IT")
HOST = os.environ.get("AMAZON_HOST", "webservices.amazon.it")
REGION = os.environ.get("AMAZON_REGION", "eu-west-1")

SERVICE = "ProductAdvertisingAPI"
API_PATH = "/paapi5/searchitems"
API_PATH_GET = "/paapi5/getitems"

def has_api_credentials():
    return bool(ACCESS_KEY and SECRET_KEY and PARTNER_TAG)

def sign(key, msg):
    return hmac.new(key, msg.encode("utf-8"), hashlib.sha256).digest()

def get_signature_key(key, date_stamp, region, service):
    k_date = sign(("AWS4" + key).encode("utf-8"), date_stamp)
    k_region = sign(k_date, region)
    k_service = sign(k_region, service)
    k_signing = sign(k_service, "aws4_request")
    return k_signing

def make_signed_request(path, payload_dict):
    """Crea una richiesta firmata AWS Signature v4 per PA-API v5."""
    if not has_api_credentials():
        return None

    t = datetime.now(timezone.utc)
    amz_date = t.strftime("%Y%m%dT%H%M%SZ")
    date_stamp = t.strftime("%Y%m%d")

    payload = json.dumps(payload_dict)
    content_type = "application/json; charset=UTF-8"

    # Determina target dall'operazione
    if "SearchItems" in path or path == API_PATH:
        target = "com.amazon.paapi5.v1.ProductAdvertisingAPIv1.SearchItems"
    else:
        target = "com.amazon.paapi5.v1.ProductAdvertisingAPIv1.GetItems"

    headers_to_sign = {
        "content-encoding": "amz-1.0",
        "content-type": content_type,
        "host": HOST,
        "x-amz-date": amz_date,
        "x-amz-target": target,
    }

    signed_headers = ";".join(sorted(headers_to_sign.keys()))
    canonical_headers = "".join(
        f"{k}:{v}\n" for k, v in sorted(headers_to_sign.items())
    )

    payload_hash = hashlib.sha256(payload.encode("utf-8")).hexdigest()

    canonical_request = "\n".join([
        "POST",
        path,
        "",
        canonical_headers,
        signed_headers,
        payload_hash,
    ])

    credential_scope = f"{date_stamp}/{REGION}/{SERVICE}/aws4_request"
    string_to_sign = "\n".join([
        "AWS4-HMAC-SHA256",
        amz_date,
        credential_scope,
        hashlib.sha256(canonical_request.encode("utf-8")).hexdigest(),
    ])

    signing_key = get_signature_key(SECRET_KEY, date_stamp, REGION, SERVICE)
    signature = hmac.new(
        signing_key, string_to_sign.encode("utf-8"), hashlib.sha256
    ).hexdigest()

    authorization = (
        f"AWS4-HMAC-SHA256 Credential={ACCESS_KEY}/{credential_scope}, "
        f"SignedHeaders={signed_headers}, Signature={signature}"
    )

    request_headers = {
        "Content-Encoding": "amz-1.0",
        "Content-Type": content_type,
        "Host": HOST,
        "X-Amz-Date": amz_date,
        "X-Amz-Target": target,
        "Authorization": authorization,
    }

    url = f"https://{HOST}{path}"
    req = Request(url, data=payload.encode("utf-8"), headers=request_headers, method="POST")

    try:
        with urlopen(req, timeout=15) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")
        print(f"  API Error {e.code}: {body[:300]}")
        return None
    except URLError as e:
        print(f"  Network Error: {e}")
        return None


def search_items(keywords, category=None, max_results=5):
    """Cerca prodotti tramite PA-API v5 SearchItems."""
    payload = {
        "Keywords": keywords,
        "Resources": [
            "Images.Primary.Large",
            "Images.Variants.Large",
            "ItemInfo.Title",
            "ItemInfo.Features",
            "ItemInfo.ByLineInfo",
            "Offers.Listings.Price",
            "Offers.Listings.SavingBasis",
            "Offers.Listings.Condition",
        ],
        "PartnerTag": PARTNER_TAG,
        "PartnerType": "Associates",
        "Marketplace": f"www.amazon.{MARKETPLACE.lower()}",
        "ItemCount": min(max_results, 10),
    }

    if category:
        search_index_map = {
            "scarpe": "Shoes",
            "abbigliamento": "Apparel",
            "accessori": "Apparel",
            "borse": "Shoes",
            "casa": "HomeAndKitchen",
            "gadget": "Electronics",
            "idee-regalo": "All",
            "beauty": "Beauty",
            "tech": "Electronics",
        }
        idx = search_index_map.get(category, "All")
        payload["SearchIndex"] = idx

    return make_signed_request(API_PATH, payload)


def get_items_by_asin(asin_list):
    """Recupera dettagli prodotto tramite lista ASIN."""
    if not asin_list:
        return None
    payload = {
        "ItemIds": asin_list[:10],
        "Resources": [
            "Images.Primary.Large",
            "Images.Variants.Large",
            "ItemInfo.Title",
            "ItemInfo.Features",
            "ItemInfo.ByLineInfo",
            "Offers.Listings.Price",
            "Offers.Listings.SavingBasis",
        ],
        "PartnerTag": PARTNER_TAG,
        "PartnerType": "Associates",
        "Marketplace": f"www.amazon.{MARKETPLACE.lower()}",
    }
    return make_signed_request(API_PATH_GET, payload)


def parse_api_item(item):
    """Converte un item della PA-API in formato prodotto sito."""
    asin = item.get("ASIN", "")
    title = ""
    image_url = ""
    images_secondary = []
    price = None
    old_price = None
    currency = "EUR"

    # Titolo
    item_info = item.get("ItemInfo", {})
    title_info = item_info.get("Title", {})
    title = title_info.get("DisplayValue", "Prodotto Amazon")

    # Immagine principale
    images = item.get("Images", {})
    primary = images.get("Primary", {})
    large = primary.get("Large", {})
    image_url = large.get("URL", "")

    # Immagini secondarie
    variants = images.get("Variants", [])
    for v in variants[:4]:
        lg = v.get("Large", {})
        url = lg.get("URL", "")
        if url:
            images_secondary.append(url)

    # Prezzo
    offers = item.get("Offers", {})
    listings = offers.get("Listings", [])
    if listings:
        listing = listings[0]
        price_info = listing.get("Price", {})
        price = price_info.get("Amount")
        currency = price_info.get("Currency", "EUR")

        saving = listing.get("SavingBasis", {})
        old_price = saving.get("Amount")

    # Link affiliato
    detail_url = item.get("DetailPageURL", f"https://www.amazon.it/dp/{asin}?tag={PARTNER_TAG}")

    return {
        "asin": asin,
        "title": title[:80],
        "image_url": image_url,
        "images_secondary": images_secondary,
        "price": price,
        "old_price": old_price,
        "currency": currency,
        "amazon_url": detail_url,
        "source": "api",
    }


def create_manual_product(asin, title, category, image_url="", price=None):
    """Crea un prodotto da inserimento manuale."""
    return {
        "asin": asin,
        "title": title[:80],
        "image_url": image_url,
        "images_secondary": [],
        "price": price,
        "old_price": None,
        "currency": "EUR",
        "amazon_url": f"https://www.amazon.it/dp/{asin}?tag={PARTNER_TAG}",
        "source": "manual",
    }


def test_api_connection():
    """Testa la connessione API. Ritorna (success, message)."""
    if not has_api_credentials():
        return False, "Credenziali API mancanti. Configura AMAZON_ACCESS_KEY e AMAZON_SECRET_KEY nel file .env"

    result = search_items("smartphone", max_results=1)
    if result and "SearchResult" in result:
        count = result["SearchResult"].get("TotalResultCount", 0)
        return True, f"API connessa. {count} risultati trovati per test."
    elif result and "Errors" in result:
        errors = result["Errors"]
        msg = errors[0].get("Message", "Errore sconosciuto") if errors else "Errore sconosciuto"
        return False, f"Errore API: {msg}"
    else:
        return False, "Nessuna risposta dall'API Amazon."


if __name__ == "__main__":
    print("=== Test Amazon PA-API v5 ===")
    ok, msg = test_api_connection()
    print(f"{'OK' if ok else 'ERRORE'}: {msg}")
