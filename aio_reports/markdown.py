from typing import Any, Dict


def escape_markdown_cell(value: str) -> str:
    return value.replace("|", "\\|")


def to_markdown(report: Dict[str, Any]) -> str:
    lines = []
    lines.append("# AIO Test Execution Report")
    lines.append("")
    lines.append("## Execution Summary")
    lines.append("")
    lines.append(f"- Project: {report['projectKey']}")
    lines.append(f"- Test/report name: {report['testName']}")
    lines.append(f"- Cycle key: {report['cycleKey']}")
    lines.append(f"- Cycle title: {report['cycleTitle']}")
    lines.append(f"- Generated at: {report['generatedAt']}")

    summary = report["summary"]
    lines.append(f"- Total cases: {summary['totalCases']}")
    lines.append(f"- Run status Passed: {summary['runStatusPassed']}")
    lines.append(f"- Test cases with step failures: {summary['testCasesWithStepFailures']}")
    lines.append(f"- Failed steps: {summary['failedSteps']}")
    lines.append(f"- Passed steps: {summary['passedSteps']}")
    lines.append(f"- Total executed steps: {summary['totalExecutedSteps']}")
    lines.append(f"- Warnings: {summary['warnings']}")
    lines.append("")

    lines.append("## What Was Tested")
    lines.append("")
    for summary_line in report.get("whatWasTested", []):
        lines.append(f"- {summary_line}")
    if not report.get("whatWasTested"):
        lines.append("- No executed test scope available.")
    lines.append("")

    lines.append("## Execution Notes")
    lines.append("")
    for note in report.get("executionNotes", []):
        lines.append(f"- {escape_markdown_cell(note)}")
    if not report.get("executionNotes"):
        lines.append("- No execution notes recorded.")
    lines.append("")

    lines.append("## Test Case Results")
    lines.append("")
    for execution in report.get("executions", []):
        run = execution.get("run") or {}
        lines.append(f"### {execution.get('caseKey') or '-'}")
        lines.append("")
        lines.append(f"- Title: {escape_markdown_cell(execution.get('caseTitle') or '-')}")
        lines.append(f"- Selected run: {run.get('runId') or '-'}")
        lines.append(f"- Run status: {run.get('status') or '-'}")
        lines.append(f"- Selection reason: {execution.get('selectionReason') or '-'}")
        lines.append(f"- Executed by: {run.get('executedByID') or '-'}")
        lines.append(f"- Created date: {run.get('createdDate') or '-'}")
        lines.append(f"- Updated date: {run.get('updatedDate') or '-'}")
        lines.append(f"- Effort: {run.get('effort') or '-'}")
        lines.append(f"- Defects: {', '.join(run.get('jiraDefectIDs') or []) or '-'}")

        if execution.get("inconsistencies"):
            lines.append("- Inconsistencies:")
            for inconsistency in execution["inconsistencies"]:
                lines.append(f"  - {escape_markdown_cell(inconsistency)}")

        lines.append("")
        lines.append("Steps:")
        for step in execution.get("steps", []):
            lines.append(
                f"- {step.get('stepOrder', '-')} | {escape_markdown_cell(step.get('step') or '-')} | {step.get('status') or '-'}"
            )
            lines.append(
                f"  Expected: {escape_markdown_cell(step.get('expectedResult') or '-')}"
            )
            if step.get("actualResult"):
                lines.append(
                    f"  Actual: {escape_markdown_cell(step.get('actualResult') or '-') }"
                )
        if not execution.get("steps"):
            lines.append("- No step execution details available.")
        lines.append("")

    return "\n".join(lines) + "\n"
