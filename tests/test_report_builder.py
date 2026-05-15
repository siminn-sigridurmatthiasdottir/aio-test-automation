import unittest

from aio_reports.report_builder import (
    build_report_payload,
    calculate_summary,
    detect_inconsistencies,
    select_relevant_run,
)


class TestReportBuilder(unittest.TestCase):
    def test_status_counting(self):
        executions = [
            {"run": {"status": "Passed"}},
            {"run": {"status": "Passed"}},
            {"run": {"status": "Failed"}},
            {"run": {"status": "Blocked"}},
            {"run": {"status": "In Progress"}},
            {"run": {"status": "Not Run"}},
        ]

        summary = calculate_summary(executions)

        self.assertEqual(summary["totalCases"], 6)
        self.assertEqual(summary["executedCases"], 5)
        self.assertEqual(summary["passed"], 2)
        self.assertEqual(summary["failed"], 1)
        self.assertEqual(summary["blocked"], 1)
        self.assertEqual(summary["inProgress"], 1)
        self.assertEqual(summary["notRun"], 1)

    def test_pass_rate_uses_executed(self):
        executions = [
            {"run": {"status": "Passed"}},
            {"run": {"status": "Passed"}},
            {"run": {"status": "Failed"}},
            {"run": {"status": "Not Run"}},
        ]

        summary = calculate_summary(executions)

        self.assertEqual(summary["executedCases"], 3)
        self.assertEqual(summary["passRateExecuted"], 66.67)

    def test_select_relevant_run_prefers_latest_executed_run(self):
        runs = [
            {"ID": 1853, "createdDate": 20, "updatedDate": None, "executedByID": None, "effort": None, "testRunStatus": {"name": "Not Run"}},
            {"ID": 1852, "createdDate": 10, "updatedDate": 30, "executedByID": "user-1", "effort": 194, "testRunStatus": {"name": "Passed"}},
        ]

        selection = select_relevant_run(runs)

        self.assertEqual(selection["selectedRun"]["ID"], 1852)
        self.assertEqual(selection["selectionReason"], "latest_executed_run")

    def test_detect_inconsistencies_flags_passed_run_with_failed_step(self):
        inconsistencies = detect_inconsistencies(
            "Passed",
            [
                {"status": "Passed"},
                {"status": "Failed"},
            ],
        )

        self.assertEqual(
            inconsistencies,
            ["Run status is Passed but at least one step is Failed."],
        )

    def test_build_report_payload_aggregates_execution_notes(self):
        cycle_run_items = [
            {
                "ID": 1538,
                "testCase": {"key": "TVSYSTEMS-TC-88", "title": "Web E2E Flow"},
                "runs": [
                    {
                        "ID": 1852,
                        "createdDate": 10,
                        "updatedDate": 20,
                        "executedByID": "user-1",
                        "effort": 194,
                        "testRunStatus": {"name": "Passed"},
                    },
                    {
                        "ID": 1853,
                        "createdDate": 30,
                        "updatedDate": None,
                        "executedByID": None,
                        "effort": None,
                        "testRunStatus": {"name": "Not Run"},
                    },
                ],
            }
        ]
        run_details = {
            1852: {
                "ID": 1852,
                "executedByID": "user-1",
                "createdDate": 10,
                "updatedDate": 20,
                "effort": 194,
                "jiraDefectIDs": ["BUG-1"],
                "testRunStatus": {"name": "Passed"},
                "testRunSteps": [
                    {
                        "stepOrder": 0,
                        "step": "Open app",
                        "expectedResult": "App loads",
                        "testRunStepStatus": {"name": "Passed"},
                    },
                    {
                        "stepOrder": 1,
                        "step": "Play content",
                        "expectedResult": "Playback starts",
                        "testRunStepStatus": {"name": "Failed"},
                        "actualResult": "Playback delayed",
                    },
                ],
            }
        }

        report = build_report_payload(
            project_key="TVSYSTEMS",
            test_name="web-e2e",
            cycle_key="TVSYSTEMS-CY-21",
            cycle_title="web - E2E",
            cycle_run_items=cycle_run_items,
            run_details=run_details,
        )

        self.assertEqual(report["summary"]["executedCases"], 1)
        self.assertEqual(report["summary"]["runStatusPassed"], 1)
        self.assertEqual(report["summary"]["testCasesWithStepFailures"], 1)
        self.assertEqual(report["summary"]["failedSteps"], 1)
        self.assertEqual(report["summary"]["passedSteps"], 1)
        self.assertEqual(report["summary"]["totalExecutedSteps"], 2)
        self.assertEqual(report["summary"]["warnings"], 1)
        self.assertEqual(report["executions"][0]["run"]["status"], "Passed")
        self.assertEqual(report["executions"][0]["steps"][1]["status"], "Failed")
        self.assertIn(
            "Run status is Passed but at least one step is Failed.",
            report["executions"][0]["inconsistencies"],
        )
        self.assertIn("TVSYSTEMS-TC-88: Playback delayed", report["executionNotes"])
        self.assertIn("TVSYSTEMS-TC-88: Linked defect: BUG-1", report["executionNotes"])


if __name__ == "__main__":
    unittest.main()
