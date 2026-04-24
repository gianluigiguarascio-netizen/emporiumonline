#!/usr/bin/env python3
"""
Suite di agenti e-commerce per EmporiumOnline.

Agenti inclusi:
1) CatalogAgent: controlla qualità dati catalogo (ASIN, prezzi, sconti)
2) PricingAgent: individua sconti anomali e priorità di intervento
3) MerchandisingAgent: analizza bilanciamento categorie e naming prodotti

Uso:
  python scripts/ecommerce_agents.py --report
  python scripts/ecommerce_agents.py --json
  python scripts/ecommerce_agents.py --file js/products.js
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

ARRAY_NAMES = ("fashionProducts", "shoesProducts", "amazonProducts")


@dataclass
class Finding:
    agent: str
    severity: str
    message: str
    product: str | None = None

    def to_dict(self) -> dict[str, str]:
        out = {
            "agent": self.agent,
            "severity": self.severity,
            "message": self.message,
        }
        if self.product:
            out["product"] = self.product
        return out


def extract_js_array(content: str, array_name: str) -> list[dict[str, Any]]:
    pattern = rf"(?:const|let|var)\s+{re.escape(array_name)}\s*=\s*(\[.*?\])\s*;"
    match = re.search(pattern, content, flags=re.S)
    if not match:
        return []
    raw = match.group(1)

    # Normalizza object literal JS -> JSON:
    # - rimuove commenti // ...
    # - aggiunge virgolette alle chiavi
    # - converte stringhe con apici singoli in doppi apici
    # - rimuove trailing commas
    normalized = re.sub(r"//.*?$", "", raw, flags=re.M)
    normalized = re.sub(r"([{,]\s*)([A-Za-z_][A-Za-z0-9_]*)\s*:", r'\1"\2":', normalized)
    normalized = re.sub(r"'([^'\\]*(?:\\.[^'\\]*)*)'", r'"\1"', normalized)
    normalized = re.sub(r",\s*([}\]])", r"\1", normalized)

    try:
        return json.loads(normalized)
    except json.JSONDecodeError:
        return []


def load_catalog(path: Path) -> dict[str, list[dict[str, Any]]]:
    content = path.read_text(encoding="utf-8")
    return {name: extract_js_array(content, name) for name in ARRAY_NAMES}


def compute_discount(price: float, old_price: float) -> int:
    if old_price <= 0:
        return 0
    return round((1 - (price / old_price)) * 100)


def run_catalog_agent(catalog: dict[str, list[dict[str, Any]]]) -> list[Finding]:
    findings: list[Finding] = []
    asin_pattern = re.compile(r"^[A-Z0-9]{10}$")

    for section, products in catalog.items():
        for p in products:
            name = str(p.get("name", "(senza nome)"))
            price = p.get("price")
            old_price = p.get("oldPrice")

            try:
                p_val = float(price)
                o_val = float(old_price)
                if p_val <= 0 or o_val <= 0:
                    findings.append(Finding("CatalogAgent", "high", "Prezzi non positivi", name))
                if p_val > o_val:
                    findings.append(Finding("CatalogAgent", "high", "Prezzo attuale maggiore del prezzo barrato", name))
            except (TypeError, ValueError):
                findings.append(Finding("CatalogAgent", "high", "Prezzi non validi", name))
                continue

            if section == "amazonProducts":
                asin = str(p.get("asin", ""))
                if not asin_pattern.match(asin):
                    findings.append(Finding("CatalogAgent", "medium", "ASIN non valido o placeholder", name))

            if len(name) < 12:
                findings.append(Finding("CatalogAgent", "low", "Nome prodotto troppo corto", name))

    return findings


def run_pricing_agent(catalog: dict[str, list[dict[str, Any]]]) -> list[Finding]:
    findings: list[Finding] = []

    for products in catalog.values():
        for p in products:
            name = str(p.get("name", "(senza nome)"))
            try:
                p_val = float(p.get("price"))
                o_val = float(p.get("oldPrice"))
            except (TypeError, ValueError):
                continue

            discount_real = compute_discount(p_val, o_val)
            discount_text = str(p.get("discount", "")).strip().replace("%", "").replace("-", "")
            discount_declared = int(discount_text) if discount_text.isdigit() else None

            if discount_real < 15:
                findings.append(Finding("PricingAgent", "medium", f"Sconto basso ({discount_real}%)", name))
            if discount_real > 80:
                findings.append(Finding("PricingAgent", "high", f"Sconto non realistico ({discount_real}%)", name))
            if discount_declared is not None and abs(discount_declared - discount_real) >= 3:
                findings.append(
                    Finding(
                        "PricingAgent",
                        "low",
                        f"Sconto dichiarato (-{discount_declared}%) diverso da quello calcolato (-{discount_real}%)",
                        name,
                    )
                )

    return findings


def run_merchandising_agent(catalog: dict[str, list[dict[str, Any]]]) -> list[Finding]:
    findings: list[Finding] = []

    fashion = len(catalog.get("fashionProducts", []))
    shoes = len(catalog.get("shoesProducts", []))
    amazon = len(catalog.get("amazonProducts", []))

    if fashion == 0 or shoes == 0:
        findings.append(Finding("MerchandisingAgent", "high", "Catalogo incompleto: manca almeno una categoria principale"))

    if fashion and shoes:
        ratio = max(fashion, shoes) / min(fashion, shoes)
        if ratio > 2:
            findings.append(Finding("MerchandisingAgent", "medium", "Squilibrio tra moda e scarpe (>2x)"))

    if amazon < 4:
        findings.append(Finding("MerchandisingAgent", "medium", "Poche offerte Amazon in home (<4)"))

    for section, products in catalog.items():
        for p in products:
            name = str(p.get("name", ""))
            if "amazon:" in name.lower() and section != "amazonProducts":
                findings.append(Finding("MerchandisingAgent", "low", "Naming con prefisso Amazon in sezione non-Amazon", name))

    return findings


def build_summary(catalog: dict[str, list[dict[str, Any]]], findings: list[Finding]) -> dict[str, Any]:
    sev_count = {"high": 0, "medium": 0, "low": 0}
    for f in findings:
        sev_count[f.severity] = sev_count.get(f.severity, 0) + 1

    return {
        "catalog_size": {k: len(v) for k, v in catalog.items()},
        "findings_by_severity": sev_count,
        "total_findings": len(findings),
        "health_score": max(0, 100 - sev_count["high"] * 15 - sev_count["medium"] * 7 - sev_count["low"] * 2),
    }


def render_report(summary: dict[str, Any], findings: list[Finding]) -> str:
    severity_order = {"high": 0, "medium": 1, "low": 2}
    findings = sorted(findings, key=lambda f: (severity_order.get(f.severity, 9), f.agent, f.message))
    lines = [
        "🧠 Report Agenti E-commerce — EmporiumOnline",
        "=" * 52,
        f"Prodotti: moda={summary['catalog_size']['fashionProducts']}, scarpe={summary['catalog_size']['shoesProducts']}, amazon={summary['catalog_size']['amazonProducts']}",
        (
            "Issue: "
            f"high={summary['findings_by_severity']['high']}, "
            f"medium={summary['findings_by_severity']['medium']}, "
            f"low={summary['findings_by_severity']['low']}"
        ),
        f"Health score: {summary['health_score']}/100",
        "",
    ]

    if not findings:
        lines.append("✅ Nessun problema rilevato.")
        return "\n".join(lines)

    lines.append("Dettagli:")
    for f in findings:
        product = f" — {f.product}" if f.product else ""
        lines.append(f"- [{f.severity.upper()}] {f.agent}: {f.message}{product}")

    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Esegue agenti e-commerce sul catalogo prodotti")
    parser.add_argument("--file", default="js/products.js", help="Percorso del catalogo JS")
    parser.add_argument("--json", action="store_true", help="Output in JSON")
    parser.add_argument("--report", action="store_true", help="Output report testuale (default)")
    parser.add_argument(
        "--fail-on",
        choices=("none", "low", "medium", "high"),
        default="none",
        help="Esce con codice 1 se trova issue con severità uguale o superiore (utile in CI).",
    )
    parser.add_argument(
        "--min-health",
        type=int,
        default=0,
        help="Esce con codice 1 se health score è inferiore alla soglia indicata (0-100).",
    )
    args = parser.parse_args()

    path = Path(args.file)
    if not path.exists():
        raise SystemExit(f"File non trovato: {path}")

    catalog = load_catalog(path)
    findings = []
    findings.extend(run_catalog_agent(catalog))
    findings.extend(run_pricing_agent(catalog))
    findings.extend(run_merchandising_agent(catalog))
    summary = build_summary(catalog, findings)
    exit_code = 0

    if not 0 <= args.min_health <= 100:
        print("--min-health deve essere tra 0 e 100", file=sys.stderr)
        return 2

    severity_rank = {"none": -1, "low": 0, "medium": 1, "high": 2}
    finding_rank = {"low": 0, "medium": 1, "high": 2}

    if args.min_health and summary["health_score"] < args.min_health:
        exit_code = 1

    threshold = severity_rank[args.fail_on]
    if threshold >= 0 and any(finding_rank.get(f.severity, -1) >= threshold for f in findings):
        exit_code = 1

    if args.json:
        payload = {
            "summary": summary,
            "findings": [f.to_dict() for f in findings],
            "exit_code": exit_code,
        }
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return exit_code

    print(render_report(summary, findings))
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
