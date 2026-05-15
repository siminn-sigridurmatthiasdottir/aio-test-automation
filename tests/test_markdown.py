import unittest

from aio_reports.markdown import escape_markdown_cell, to_markdown


class TestMarkdown(unittest.TestCase):
    def test_escape_pipe(self):
        self.assertEqual(escape_markdown_cell("A|B"), "A\\|B")

    def test_render_execution_sections(self):
        report = {
            "projectKey": "TVSYSTEMS",
            "testName": "web-e2e",
            "cycleKey": "TVSYSTEMS-CY-21",
            "cycleTitle": "web - E2E",
            "generatedAt": "2026-05-13T00:00:00+00:00",
            "summary": {
                "totalCases": 1,
                "runStatusPassed": 1,
                "testCasesWithStepFailures": 1,
                "failedSteps": 1,
                "passedSteps": 1,
                "totalExecutedSteps": 2,
                "warnings": 1,
                "executedCases": 1,
                "passed": 1,
                "failed": 0,
                "blocked": 0,
                "inProgress": 0,
                "notRun": 0,
                "passRateExecuted": 100.0,
            },
            "whatWasTested": ["Web E2E Flow: Passed with 2/2 executed steps."],
            "executionNotes": ["TVSYSTEMS-TC-88: Run status is Passed but at least one step is Failed."],
            "executions": [
                {
                    "caseKey": "TVSYSTEMS-TC-88",
                    "caseTitle": "Web E2E Flow",
                    "selectionReason": "latest_executed_run",
                    "run": {
                        "runId": 1852,
                        "status": "Passed",
                        "executedByID": "user-1",
                        "createdDate": 1,
                        "updatedDate": 2,
                        "effort": 194,
                        "jiraDefectIDs": ["BUG-1"],
                    },
                    "inconsistencies": [
                        "Run status is Passed but at least one step is Failed.",
                    ],
                    "steps": [
                        {
                            "stepOrder": 0,
                            "step": "Open app",
                            "expectedResult": "App loads",
                            "status": "Passed",
                            "actualResult": None,
                        },
                        {
                            "stepOrder": 1,
                            "step": "Play content",
                            "expectedResult": "Playback starts",
                            "status": "Failed",
                            "actualResult": "Playback delayed",
                        },
                    ],
                }
            ],
        }

        markdown = to_markdown(report)

        self.assertIn("# AIO Test Execution Report", markdown)
        self.assertIn("## Execution Summary", markdown)
        self.assertIn("## What Was Tested", markdown)
        self.assertIn("## Execution Notes", markdown)
        self.assertIn("## Test Case Results", markdown)
        self.assertIn("Run status Passed: 1", markdown)
        self.assertIn("Test cases with step failures: 1", markdown)
        self.assertIn("Warnings: 1", markdown)
        self.assertIn("Selected run: 1852", markdown)
        self.assertIn("Run status: Passed", markdown)
        self.assertIn("Actual: Playback delayed", markdown)


if __name__ == "__main__":
    unittest.main()
