import unittest

from aio_reports.cli import derive_report_name


class TestCli(unittest.TestCase):
    def test_explicit_name_wins(self):
        self.assertEqual(
            derive_report_name("custom-name", "Web E2E", "TVSYSTEMS-CY-21"),
            "custom-name",
        )

    def test_cycle_title_used_when_no_explicit_name(self):
        self.assertEqual(
            derive_report_name(None, "Web E2E", "TVSYSTEMS-CY-21"),
            "Web E2E",
        )

    def test_cycle_key_used_when_title_missing(self):
        self.assertEqual(
            derive_report_name(None, "", "TVSYSTEMS-CY-21"),
            "TVSYSTEMS-CY-21",
        )


if __name__ == "__main__":
    unittest.main()
