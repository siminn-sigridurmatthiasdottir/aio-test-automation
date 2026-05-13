import unittest

from aio_reports.report_builder import calculate_summary


class TestReportBuilder(unittest.TestCase):
    def test_status_counting(self):
        rows = [
            {"status": "Passed"},
            {"status": "Passed"},
            {"status": "Failed"},
            {"status": "Blocked"},
            {"status": "In Progress"},
            {"status": "Not Run"},
        ]

        summary = calculate_summary(rows)

        self.assertEqual(summary["totalCases"], 6)
        self.assertEqual(summary["executedCases"], 5)
        self.assertEqual(summary["passed"], 2)
        self.assertEqual(summary["failed"], 1)
        self.assertEqual(summary["blocked"], 1)
        self.assertEqual(summary["inProgress"], 1)
        self.assertEqual(summary["notRun"], 1)

    def test_pass_rate_uses_executed(self):
        rows = [
            {"status": "Passed"},
            {"status": "Passed"},
            {"status": "Failed"},
            {"status": "Not Run"},
        ]

        summary = calculate_summary(rows)

        self.assertEqual(summary["executedCases"], 3)
        self.assertEqual(summary["passRateExecuted"], 66.67)


if __name__ == "__main__":
    unittest.main()
