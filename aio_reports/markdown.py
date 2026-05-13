from typing import Any, Dict


def escape_markdown_cell(value: str) -> str:
    return value.replace("|", "\\|")


def to_markdown(report: Dict[str, Any]) -> str:
    lines = []
    lines.append(f"# AIO Test Report: {report['testName']}")
    lines.append("")
    lines.append(f"- Project: {report['projectKey']}")
    lines.append(f"- Test/report name: {report['testName']}")
    lines.append(f"- Cycle key: {report['cycleKey']}")
    lines.append(f"- Cycle title: {report['cycleTitle']}")
    lines.append(f"- Generated at: {report['generatedAt']}")
    lines.append("")

    summary = report["summary"]
    lines.append("## Summary")
    lines.append("")
    lines.append(f"- Total cases: {summary['totalCases']}")
    lines.append(f"- Executed cases: {summary['executedCases']}")
    lines.append(f"- Passed: {summary['passed']}")
    lines.append(f"- Failed: {summary['failed']}")
    lines.append(f"- Blocked: {summary['blocked']}")
    lines.append(f"- In Progress: {summary['inProgress']}")
    lines.append(f"- Not Run: {summary['notRun']}")
    lines.append(f"- Pass rate (executed): {summary['passRateExecuted']}%")
    lines.append("")

    lines.append("## Cases")
    lines.append("")
    lines.append("| Case Key | Title | Latest Status |")
    lines.append("|---|---|---|")
    for row in report["cases"]:
        key = row.get("caseKey") or "-"
        title = escape_markdown_cell(row.get("caseTitle") or "-")
        status = row.get("status") or "-"
        lines.append(f"| {key} | {title} | {status} |")

    return "\n".join(lines) + "\n"
