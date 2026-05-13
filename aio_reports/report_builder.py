import datetime as dt
from collections import Counter
from typing import Any, Dict, List


def normalize_case_row(item: Dict[str, Any]) -> Dict[str, Any]:
    case_info = item.get("testCase", {})
    run_info = item.get("latestRun") or {}
    run_status = (run_info.get("testRunStatus") or {}).get("name", "Not Run")

    return {
        "caseKey": case_info.get("key", ""),
        "caseTitle": case_info.get("title", ""),
        "status": run_status,
        "runId": run_info.get("ID"),
        "runUpdatedDate": run_info.get("updatedDate"),
    }


def calculate_summary(rows: List[Dict[str, Any]]) -> Dict[str, Any]:
    status_counts = Counter(row.get("status") or "Not Run" for row in rows)

    total = len(rows)
    passed = status_counts.get("Passed", 0)
    failed = status_counts.get("Failed", 0)
    blocked = status_counts.get("Blocked", 0)
    in_progress = status_counts.get("In Progress", 0)
    not_run = status_counts.get("Not Run", 0)
    executed = max(total - not_run, 0)
    pass_rate = round((passed / executed) * 100, 2) if executed else 0.0

    return {
        "totalCases": total,
        "executedCases": executed,
        "passed": passed,
        "failed": failed,
        "blocked": blocked,
        "inProgress": in_progress,
        "notRun": not_run,
        "passRateExecuted": pass_rate,
    }


def build_report_payload(
    project_key: str,
    test_name: str,
    cycle_key: str,
    cycle_title: str,
    case_items: List[Dict[str, Any]],
) -> Dict[str, Any]:
    rows = [normalize_case_row(item) for item in case_items]
    summary = calculate_summary(rows)

    return {
        "generatedAt": dt.datetime.now(dt.UTC).isoformat(),
        "projectKey": project_key,
        "testName": test_name,
        "cycleKey": cycle_key,
        "cycleTitle": cycle_title,
        "summary": summary,
        "cases": rows,
    }
