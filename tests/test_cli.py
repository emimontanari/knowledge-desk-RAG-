import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class PublicCliTests(unittest.TestCase):
    def run_cli(self, *args):
        return subprocess.run(
            [sys.executable, "-m", "knowledge_desk", *args],
            cwd=ROOT,
            capture_output=True,
            text=True,
            timeout=10,
        )

    def test_exact_error_code_returns_attributed_account_section(self):
        result = self.run_cli("AUTH_042")
        self.assertEqual(result.returncode, 0, result.stderr)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["query"], "AUTH_042")
        self.assertEqual(payload["results"][0]["source"], "corpus/account-access.md")
        self.assertEqual(payload["results"][0]["heading"], "Account recovery")
        self.assertIn("AUTH_042", payload["results"][0]["text"])

    def test_ordinary_spanish_query_matches_manual(self):
        result = self.run_cli("recuperar acceso cuenta")
        self.assertEqual((result.returncode, result.stderr), (0, ""))
        payload = json.loads(result.stdout)
        self.assertEqual(payload["results"][0]["heading"], "Account recovery")

    def test_unknown_query_returns_no_evidence(self):
        result = self.run_cli("xyzzy quux")
        self.assertEqual((result.returncode, result.stderr), (0, ""))
        self.assertEqual(result.stdout, '{\n  "query": "xyzzy quux",\n  "results": []\n}\n')

    def test_ranking_and_ties_are_deterministic(self):
        first = self.run_cli("plan factura", "--top-k", "3")
        second = self.run_cli("plan factura", "--top-k", "3")
        self.assertEqual(first.stdout, second.stdout)
        self.assertEqual((first.returncode, first.stderr), (0, ""))
        results = json.loads(first.stdout)["results"]
        self.assertGreaterEqual(len(results), 2)
        self.assertEqual([item["score"] for item in results], sorted(
            (item["score"] for item in results), reverse=True
        ))
        tied = [item for item in results if item["score"] == results[-1]["score"]]
        self.assertEqual(tied, sorted(tied, key=lambda item: (item["source"], item["heading"])))

    def test_top_k_limits_results_and_invalid_value_is_rejected(self):
        limited = self.run_cli("access", "--top-k", "1")
        self.assertEqual(len(json.loads(limited.stdout)["results"]), 1)
        invalid = self.run_cli("access", "--top-k", "0")
        self.assertEqual(invalid.returncode, 2)
        self.assertEqual(invalid.stdout, "")
        self.assertIn("must be a positive integer", invalid.stderr)


if __name__ == "__main__":
    unittest.main()
