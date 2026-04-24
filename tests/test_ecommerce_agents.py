import importlib.util
import json
import subprocess
import sys
import tempfile
import textwrap
from pathlib import Path
import unittest

REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = REPO_ROOT / "scripts" / "ecommerce_agents.py"


def load_module():
    spec = importlib.util.spec_from_file_location("ecommerce_agents", SCRIPT_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class EcommerceAgentsTests(unittest.TestCase):
    def setUp(self):
        self.mod = load_module()

    def test_extract_js_array_parses_object_literals_and_comments(self):
        js = textwrap.dedent(
            """
            const fashionProducts = [
              { id: 1, name: 'Prodotto Test', price: '10.00', oldPrice: '20.00', discount: '-50%' }, // comment
            ];
            """
        )
        arr = self.mod.extract_js_array(js, "fashionProducts")
        self.assertEqual(len(arr), 1)
        self.assertEqual(arr[0]["name"], "Prodotto Test")
        self.assertEqual(arr[0]["price"], "10.00")

    def test_agents_detect_high_issue_for_invalid_prices(self):
        catalog = {
            "fashionProducts": [{"name": "Prodotto Rotto", "price": "80", "oldPrice": "10", "discount": "-10%"}],
            "shoesProducts": [],
            "amazonProducts": [],
        }
        findings = self.mod.run_catalog_agent(catalog)
        self.assertTrue(any(f.severity == "high" for f in findings))

    def test_cli_json_includes_exit_code_when_threshold_matches(self):
        js = textwrap.dedent(
            """
            const fashionProducts = [];
            const shoesProducts = [];
            const amazonProducts = [];
            """
        )
        with tempfile.NamedTemporaryFile("w", suffix=".js", delete=False, encoding="utf-8") as tmp:
            tmp.write(js)
            tmp_path = tmp.name

        proc = subprocess.run(
            [sys.executable, str(SCRIPT_PATH), "--file", tmp_path, "--json", "--fail-on", "medium"],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(proc.returncode, 1)
        payload = json.loads(proc.stdout)
        self.assertEqual(payload["exit_code"], 1)
        self.assertGreater(payload["summary"]["total_findings"], 0)


if __name__ == "__main__":
    unittest.main()
