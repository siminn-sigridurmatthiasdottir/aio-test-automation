import datetime as dt
from collections import Counter
from typing import Any, Dict, List, Optional


NOT_RUN_STATUS = "Not Run"


def get_run_status_name(run_info: Dict[str, Any]) -> str:
    return ((run_info or {}).get("testRunStatus") or {}).get("name", NOT_RUN_STATUS)


def normalize_run_marker(run_info: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "runId": run_info.get("ID"),
        "status": get_run_status_name(run_info),
        "executedByID": run_info.get("executedByID"),
        "createdDate": run_info.get("createdDate"),
        "updatedDate": run_info.get("updatedDate"),
        "effort": run_info.get("effort"),
    }


def sort_runs_by_recency(run_items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    return sorted(
        run_items,
        key=lambda run: (
            run.get("updatedDate") or 0,
            run.get("createdDate") or 0,
            run.get("ID") or 0,
        ),
        reverse=True,
    )


def is_executed_run(run_info: Dict[str, Any]) -> bool:
    status_name = get_run_status_name(run_info)
    if status_name != NOT_RUN_STATUS:
        return True
    return any(
        run_info.get(field) is not None
        for field in ("executedByID", "updatedDate", "effort")
    )


def select_relevant_run(run_items: List[Dict[str, Any]]) -> Dict[str, Any]:
    ordered_runs = sort_runs_by_recency(run_items)

    for run_info in ordered_runs:
        if is_executed_run(run_info):
            return {
                "selectedRun": run_info,
                "selectionReason": "latest_executed_run",
                "availableRuns": [normalize_run_marker(run) for run in ordered_runs],
            }

    for run_info in ordered_runs:
        if get_run_status_name(run_info) != NOT_RUN_STATUS:
            return {
                "selectedRun": run_info,
                "selectionReason": "latest_non_not_run",
                "availableRuns": [normalize_run_marker(run) for run in ordered_runs],
            }

    selected_run = ordered_runs[0] if ordered_runs else None
    return {
        "selectedRun": selected_run,
        "selectionReason": "fallback_latest_available" if selected_run else "no_runs",
        "availableRuns": [normalize_run_marker(run) for run in ordered_runs],
    }


def normalize_step(step_info: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "stepOrder": step_info.get("stepOrder"),
        "step": step_info.get("step", ""),
        "expectedResult": step_info.get("expectedResult", ""),
        "status": ((step_info.get("testRunStepStatus") or {}).get("name") or NOT_RUN_STATUS),
        "actualResult": step_info.get("actualResult"),
    }


def calculate_step_summary(steps: List[Dict[str, Any]]) -> Dict[str, Any]:
    status_counts = Counter(step.get("status") or NOT_RUN_STATUS for step in steps)
    total = len(steps)
    not_run = status_counts.get(NOT_RUN_STATUS, 0)
    executed = max(total - not_run, 0)
    return {
        "totalSteps": total,
        "executedSteps": executed,
        "passed": status_counts.get("Passed", 0),
        "failed": status_counts.get("Failed", 0),
        "blocked": status_counts.get("Blocked", 0),
        "inProgress": status_counts.get("In Progress", 0),
        "notRun": not_run,
    }


def detect_inconsistencies(run_status: str, steps: List[Dict[str, Any]]) -> List[str]:
    inconsistencies: List[str] = []
    step_statuses = {step.get("status") or NOT_RUN_STATUS for step in steps}

    if run_status == "Passed" and "Failed" in step_statuses:
        inconsistencies.append("Run status is Passed but at least one step is Failed.")
    if run_status == NOT_RUN_STATUS and any(status != NOT_RUN_STATUS for status in step_statuses):
        inconsistencies.append("Run status is Not Run but step results show executed steps.")
    if run_status != NOT_RUN_STATUS and steps and all(status == NOT_RUN_STATUS for status in step_statuses):
        inconsistencies.append("Run status shows execution but all steps are Not Run.")

    return inconsistencies


def normalize_execution(
    run_item: Dict[str, Any],
    selected_run: Optional[Dict[str, Any]],
    run_detail: Optional[Dict[str, Any]],
    selection_reason: str,
    available_runs: List[Dict[str, Any]],
) -> Dict[str, Any]:
    case_info = run_item.get("testCase", {})
    detail = run_detail or selected_run or {}
    run_status = get_run_status_name(detail)
    steps = [normalize_step(step_info) for step_info in (detail.get("testRunSteps") or [])]
    step_summary = calculate_step_summary(steps)
    inconsistencies = detect_inconsistencies(run_status, steps)
    actual_results = [step["actualResult"] for step in steps if step.get("actualResult")]
    defect_ids = detail.get("jiraDefectIDs") or []

    execution_notes = list(actual_results)
    execution_notes.extend(inconsistencies)
    execution_notes.extend(f"Linked defect: {defect_id}" for defect_id in defect_ids)

    return {
        "caseKey": case_info.get("key", ""),
        "caseTitle": case_info.get("title", ""),
        "assignmentId": run_item.get("ID"),
        "selectionReason": selection_reason,
        "availableRuns": available_runs,
        "run": {
            "runId": detail.get("ID") if detail else None,
            "status": run_status,
            "executedByID": detail.get("executedByID"),
            "createdDate": detail.get("createdDate"),
            "updatedDate": detail.get("updatedDate"),
            "effort": detail.get("effort"),
            "jiraDefectIDs": defect_ids,
        },
        "stepSummary": step_summary,
        "steps": steps,
        "executionNotes": execution_notes,
        "inconsistencies": inconsistencies,
    }


def build_what_was_tested(executions: List[Dict[str, Any]]) -> List[str]:
    summaries: List[str] = []
    for execution in executions:
        executed_steps = execution.get("stepSummary", {}).get("executedSteps", 0)
        total_steps = execution.get("stepSummary", {}).get("totalSteps", 0)
        status = ((execution.get("run") or {}).get("status") or NOT_RUN_STATUS)
        summaries.append(
            f"{execution.get('caseTitle') or execution.get('caseKey')}: {status} with {executed_steps}/{total_steps} executed steps."
        )
    return summaries


def build_execution_notes(executions: List[Dict[str, Any]]) -> List[str]:
    notes: List[str] = []
    for execution in executions:
        case_key = execution.get("caseKey") or "Unknown case"
        for note in execution.get("executionNotes", []):
            notes.append(f"{case_key}: {note}")
    return notes


def get_execution_status(execution: Dict[str, Any]) -> str:
    if "run" in execution:
        return ((execution.get("run") or {}).get("status") or NOT_RUN_STATUS)
    return execution.get("status") or NOT_RUN_STATUS


def calculate_summary(executions: List[Dict[str, Any]]) -> Dict[str, Any]:
    total = len(executions)
    run_status_counts = Counter(get_execution_status(execution) for execution in executions)
    step_summary_totals = Counter()
    test_cases_with_step_failures = 0
    warnings = 0

    for execution in executions:
        step_summary = execution.get("stepSummary") or {}
        step_summary_totals.update(step_summary)
        if step_summary.get("failed", 0) > 0:
            test_cases_with_step_failures += 1
        warnings += len(execution.get("inconsistencies") or [])

    total_executed_steps = step_summary_totals.get("executedSteps", 0)
    failed_steps = step_summary_totals.get("failed", 0)
    passed_steps = step_summary_totals.get("passed", 0)
    executed_cases = sum(1 for execution in executions if get_execution_status(execution) != NOT_RUN_STATUS)
    pass_rate_executed = round((run_status_counts.get("Passed", 0) / executed_cases) * 100, 2) if executed_cases else 0.0

    return {
        "totalCases": total,
        "runStatusPassed": run_status_counts.get("Passed", 0),
        "testCasesWithStepFailures": test_cases_with_step_failures,
        "failedSteps": failed_steps,
        "passedSteps": passed_steps,
        "totalExecutedSteps": total_executed_steps,
        "warnings": warnings,
        "executedCases": executed_cases,
        "passed": run_status_counts.get("Passed", 0),
        "failed": run_status_counts.get("Failed", 0),
        "blocked": run_status_counts.get("Blocked", 0),
        "inProgress": run_status_counts.get("In Progress", 0),
        "notRun": run_status_counts.get(NOT_RUN_STATUS, 0),
        "passRateExecuted": pass_rate_executed,
    }


def build_report_payload(
    project_key: str,
    test_name: str,
    cycle_key: str,
    cycle_title: str,
    cycle_run_items: List[Dict[str, Any]],
    run_details: Dict[int, Dict[str, Any]],
) -> Dict[str, Any]:
    executions: List[Dict[str, Any]] = []
    for run_item in cycle_run_items:
        selection = select_relevant_run(run_item.get("runs") or [])
        selected_run = selection.get("selectedRun")
        run_detail = None
        if selected_run and selected_run.get("ID") is not None:
            run_detail = run_details.get(selected_run["ID"])

        executions.append(
            normalize_execution(
                run_item=run_item,
                selected_run=selected_run,
                run_detail=run_detail,
                selection_reason=selection["selectionReason"],
                available_runs=selection["availableRuns"],
            )
        )

    summary = calculate_summary(executions)

    return {
        "generatedAt": dt.datetime.now(dt.UTC).isoformat(),
        "projectKey": project_key,
        "testName": test_name,
        "cycleKey": cycle_key,
        "cycleTitle": cycle_title,
        "whatWasTested": build_what_was_tested(executions),
        "executionNotes": build_execution_notes(executions),
        "summary": summary,
        "executions": executions,
    }
