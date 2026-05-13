import unittest

from aio_reports.storage import build_report_paths, sanitize_test_name


class TestStorage(unittest.TestCase):
    def test_sanitize_test_name(self):
        self.assertEqual(sanitize_test_name("Web E2E"), "web-e2e")
        self.assertEqual(sanitize_test_name("Payment_Flow#1"), "payment-flow1")

    def test_paths_use_sanitized_test_name(self):
        safe_name, json_path, md_path = build_report_paths("reports", "Web E2E")

        self.assertEqual(safe_name, "web-e2e")
        self.assertEqual(
            json_path,
            "reports/web-e2e/web-e2e_report.json",
        )
        self.assertEqual(
            md_path,
            "reports/web-e2e/web-e2e_report.md",
        )

    def test_invalid_test_name_raises(self):
        with self.assertRaises(ValueError):
            sanitize_test_name("!!!")


if __name__ == "__main__":
    unittest.main()
