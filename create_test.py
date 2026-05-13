import json
import os

import requests
from dotenv import load_dotenv


load_dotenv()

PROJECT_KEY = "TVSYSTEMS"
AIO_BASE_URL = "https://tcms.aiojiraapps.com/aio-tcms/api/v1"
TEST_DATA_DIR = "test_data"
PUBLISHED_STATUS_NAME = "Published"
TARGET_SUBDIR = os.getenv("TEST_DATA_SUBDIR")

token = os.getenv("AIO_TOKEN")

if not token:
    raise ValueError("AIO_TOKEN is missing. Check your .env file.")

headers = {
    "Authorization": f"AioAuth {token}",
    "Content-Type": "application/json",
}


def validate(data, filename):
    errors = []

    if "name" in data and "title" not in data:
        errors.append("Use 'title' not 'name'")
    if "testScriptType" in data:
        errors.append("Use 'scriptType' not 'testScriptType'")
    if "folder" in data and "folderHierarchy" not in data:
        errors.append("Use 'folderHierarchy' not 'folder' at root level")

    if "title" not in data:
        errors.append("Missing required field: title")
    elif not isinstance(data["title"], str) or not data["title"].strip():
        errors.append("'title' must be a non-empty string")

    if "folderHierarchy" in data:
        folder_hierarchy = data["folderHierarchy"]
        if not isinstance(folder_hierarchy, list):
            errors.append("'folderHierarchy' must be a list when provided")
        elif not all(isinstance(item, str) and item.strip() for item in folder_hierarchy):
            errors.append("'folderHierarchy' must be a list of non-empty strings")

    if "scriptType" not in data:
        errors.append("Missing required field: scriptType")
    else:
        script_type = data["scriptType"]
        if not isinstance(script_type, dict):
            errors.append("'scriptType' must be an object")
        else:
            if script_type.get("ID") != 7:
                errors.append(f"'scriptType.ID' must be 7, got: {script_type.get('ID')!r}")
            if script_type.get("name") != "Classic":
                errors.append(f"'scriptType.name' must be 'Classic', got: {script_type.get('name')!r}")

    if "precondition" not in data:
        errors.append("Missing required field: precondition")
    elif not isinstance(data["precondition"], str):
        errors.append("'precondition' must be a string")

    if "priority" in data and isinstance(data["priority"], str):
        errors.append(f"'priority' must not be a plain string, got: {data['priority']!r}")

    if "tags" in data:
        tags = data["tags"]
        if isinstance(tags, list) and any(isinstance(tag, str) for tag in tags):
            errors.append("'tags' must not be a list of plain strings")

    if "steps" not in data:
        errors.append("Missing required field: steps")
    else:
        steps = data["steps"]
        if not isinstance(steps, list) or len(steps) == 0:
            errors.append("'steps' must be a non-empty list")
        else:
            for index, step in enumerate(steps):
                step_number = index + 1
                if not isinstance(step, dict):
                    errors.append(f"Step {step_number} is not an object")
                    continue
                if "stepType" not in step:
                    errors.append(f"Step {step_number} missing 'stepType'")
                elif step["stepType"] != "TEXT":
                    errors.append(f"Step {step_number} 'stepType' must be 'TEXT', got: {step['stepType']!r}")
                if "step" not in step:
                    errors.append(f"Step {step_number} missing 'step'")
                elif not isinstance(step["step"], str) or not step["step"].strip():
                    errors.append(f"Step {step_number} 'step' must be a non-empty string")
                if "data" not in step:
                    errors.append(f"Step {step_number} missing 'data'")
                if "expectedResult" not in step:
                    errors.append(f"Step {step_number} missing 'expectedResult'")
                elif not isinstance(step["expectedResult"], str) or not step["expectedResult"].strip():
                    errors.append(f"Step {step_number} 'expectedResult' must be a non-empty string")

    return errors


def get_folder_id(folder_hierarchy):
    url = f"{AIO_BASE_URL}/project/{PROJECT_KEY}/testcase/folder/hierarchy"
    payload = {"baseFolderId": None, "folderHierarchy": folder_hierarchy}
    response = requests.put(url, headers=headers, json=payload)
    if response.status_code != 200:
        print(f"  ERROR: Folder API returned {response.status_code}: {response.text}")
        return None

    try:
        data = response.json()
        return data["ID"]
    except Exception as exc:
        print(f"  ERROR: Could not parse folder response: {exc}")
        return None


def get_cycle_folder_id(folder_hierarchy):
    url = f"{AIO_BASE_URL}/project/{PROJECT_KEY}/testcycle/folder/hierarchy"
    payload = {"baseFolderId": None, "folderHierarchy": folder_hierarchy}
    response = requests.put(url, headers=headers, json=payload)
    if response.status_code != 200:
        print(f"  ERROR: Cycle folder API returned {response.status_code}: {response.text}")
        return None

    try:
        data = response.json()
        return data["ID"]
    except Exception as exc:
        print(f"  ERROR: Could not parse cycle folder response: {exc}")
        return None


def create_test_case(test_data, folder_id):
    url = f"{AIO_BASE_URL}/project/{PROJECT_KEY}/testcase"
    payload = {
        "title": test_data["title"],
        "scriptType": test_data["scriptType"],
        "folder": {"ID": folder_id},
        "precondition": test_data.get("precondition", ""),
        "steps": test_data["steps"],
        "status": test_data["status"],
    }
    response = requests.post(url, headers=headers, json=payload)
    if response.status_code not in (200, 201):
        print(f"  ERROR: Test case API returned {response.status_code}: {response.text}")
        return None

    try:
        return response.json()
    except Exception as exc:
        print(f"  ERROR: Could not parse test case response: {exc}")
        return None


def get_test_case_detail(case_key):
    url = f"{AIO_BASE_URL}/project/{PROJECT_KEY}/testcase/{case_key}/detail"
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print(f"  ERROR: Case detail API returned {response.status_code}: {response.text}")
        return None

    try:
        return response.json()
    except Exception as exc:
        print(f"  ERROR: Could not parse case detail response: {exc}")
        return None


def find_existing_case_by_title(title):
    url = f"{AIO_BASE_URL}/project/{PROJECT_KEY}/testcase/search"
    payload = {
        "title": {
            "comparisonType": "EXACT_MATCH",
            "value": title,
        }
    }
    response = requests.post(url, headers=headers, json=payload)
    if response.status_code != 200:
        print(f"  ERROR: Case search API returned {response.status_code}: {response.text}")
        return None

    try:
        data = response.json()
    except Exception as exc:
        print(f"  ERROR: Could not parse case search response: {exc}")
        return None

    items = data.get("items", [])
    if not items:
        return None

    return items[0]


def update_test_case(case_key, case_data):
    url = f"{AIO_BASE_URL}/project/{PROJECT_KEY}/testcase/{case_key}/detail"
    response = requests.put(url, headers=headers, json=case_data)
    if response.status_code not in (200, 201):
        print(f"  ERROR: Case update API returned {response.status_code}: {response.text}")
        return None

    try:
        return response.json()
    except Exception:
        return {}


def fetch_existing_cases():
    cases = {}
    start_at = 0
    page_size = 200

    while True:
        url = f"{AIO_BASE_URL}/project/{PROJECT_KEY}/testcase"
        response = requests.get(
            url,
            headers=headers,
            params={"startAt": start_at, "maxResults": page_size},
        )

        if response.status_code != 200:
            print(
                f"  WARNING: Could not preload existing test cases "
                f"({response.status_code}): {response.text}"
            )
            return cases

        try:
            data = response.json()
        except Exception as exc:
            print(f"  WARNING: Could not parse test case list response: {exc}")
            return cases

        items = data.get("items", [])
        for item in items:
            title = item.get("title")
            key = item.get("key")
            if isinstance(title, str) and title.strip() and isinstance(key, str) and key.strip():
                cases[title.strip()] = key.strip()

        if data.get("isLast", True) or not items:
            break

        start_at += len(items)

    return cases


def fetch_existing_cycles():
    cycles = {}
    start_at = 0
    page_size = 200

    while True:
        url = f"{AIO_BASE_URL}/project/{PROJECT_KEY}/testcycle"
        response = requests.get(
            url,
            headers=headers,
            params={"startAt": start_at, "maxResults": page_size},
        )

        if response.status_code != 200:
            print(
                f"  WARNING: Could not preload existing cycles "
                f"({response.status_code}): {response.text}"
            )
            return cycles

        try:
            data = response.json()
        except Exception as exc:
            print(f"  WARNING: Could not parse cycle list response: {exc}")
            return cycles

        items = data.get("items", [])
        for item in items:
            title = item.get("title")
            key = item.get("key")
            if isinstance(title, str) and title.strip() and isinstance(key, str) and key.strip():
                cycles[title.strip()] = key.strip()

        if data.get("isLast", True) or not items:
            break

        start_at += len(items)

    return cycles


def get_status_id(status_name):
    url = f"{AIO_BASE_URL}/project/{PROJECT_KEY}/config/testcase/status"
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print(f"  ERROR: Status API returned {response.status_code}: {response.text}")
        return None

    try:
        statuses = response.json()
    except Exception as exc:
        print(f"  ERROR: Could not parse status response: {exc}")
        return None

    for status in statuses:
        if isinstance(status, dict) and status.get("name") == status_name:
            return status.get("ID")

    print(f"  ERROR: Could not find case status named {status_name!r}")
    return None


def create_test_cycle(cycle_data, folder_id):
    url = f"{AIO_BASE_URL}/project/{PROJECT_KEY}/testcycle/detail"
    payload = {
        "title": cycle_data["title"],
        "objective": cycle_data.get("objective", ""),
        "folder": {"ID": folder_id},
    }
    response = requests.post(url, headers=headers, json=payload)
    if response.status_code not in (200, 201):
        print(f"  ERROR: Cycle API returned {response.status_code}: {response.text}")
        return None

    try:
        return response.json()
    except Exception as exc:
        print(f"  ERROR: Could not parse cycle response: {exc}")
        return None


def add_case_to_cycle(cycle_key, case_key):
    url = f"{AIO_BASE_URL}/project/{PROJECT_KEY}/testcycle/{cycle_key}/testcase/{case_key}"
    response = requests.post(url, headers=headers)
    if response.status_code not in (200, 201):
        print(f"  ERROR: Add case to cycle API returned {response.status_code}: {response.text}")
        return None

    try:
        return response.json()
    except Exception:
        return {}


def folder_hierarchy_from_path(path):
    rel_dir = os.path.dirname(os.path.relpath(path, TEST_DATA_DIR))
    if rel_dir in ("", "."):
        return []
    return [part for part in rel_dir.split(os.sep) if part and part != "."]


if not os.path.isdir(TEST_DATA_DIR):
    raise FileNotFoundError(f"Test data directory not found: {TEST_DATA_DIR}")

json_files = []
scan_root = os.path.join(TEST_DATA_DIR, TARGET_SUBDIR) if TARGET_SUBDIR else TEST_DATA_DIR

if TARGET_SUBDIR and not os.path.isdir(scan_root):
    raise FileNotFoundError(f"Target test data subdirectory not found: {scan_root}")

for root, _, files in os.walk(scan_root):
    for filename in files:
        if filename.endswith(".json"):
            json_files.append(os.path.join(root, filename))

json_files.sort()

if not json_files:
    print(f"No JSON files found in {TEST_DATA_DIR}")
    raise SystemExit(0)

print("Loading existing test case titles from AIO...")
existing_cases = fetch_existing_cases()
print(f"Loaded {len(existing_cases)} existing titles")

print("Loading existing cycle titles from AIO...")
existing_cycles = fetch_existing_cycles()
print(f"Loaded {len(existing_cycles)} existing cycle titles")

published_status_id = get_status_id(PUBLISHED_STATUS_NAME)
if not published_status_id:
    raise ValueError(f"Could not resolve case status ID for {PUBLISHED_STATUS_NAME!r}")

seen_titles = set()
cases_by_folder = {}

for path in json_files:
    filename = os.path.relpath(path, TEST_DATA_DIR)
    print(f"\nProcessing: {filename}")

    try:
        with open(path, encoding="utf-8") as file_handle:
            test_data = json.load(file_handle)
    except json.JSONDecodeError as exc:
        print(f"  ERROR: JSON parse error: {exc}")
        continue

    errors = validate(test_data, filename)
    if errors:
        print(f"  SKIP: Validation failed ({len(errors)} error(s)):")
        for err in errors:
            print(f"    - {err}")
        continue

    title = test_data["title"].strip()
    if title in seen_titles:
        print(f"  SKIP: Duplicate title in input set: {title}")
        continue
    seen_titles.add(title)

    test_data["status"] = {"ID": published_status_id, "name": PUBLISHED_STATUS_NAME}

    folder_hierarchy = folder_hierarchy_from_path(path)
    if not folder_hierarchy:
        print("  SKIP: File is directly under test_data; put it inside a subfolder to derive folder hierarchy")
        continue

    folder_id = get_folder_id(folder_hierarchy)
    if not folder_id:
        print(f"  SKIP: Could not resolve folder for {filename}")
        continue

    if title in existing_cases:
        case_detail = find_existing_case_by_title(title)
        if not case_detail:
            print(f"  FAILED: Could not resolve existing case for {test_data['title']}")
            continue

        case_identifier = case_detail.get("key") or case_detail.get("ID")
        if not case_identifier:
            print(f"  FAILED: Existing case is missing an ID/key for {test_data['title']}")
            continue

        case_detail["status"] = {"ID": published_status_id, "name": PUBLISHED_STATUS_NAME}
        result = update_test_case(case_identifier, case_detail)
        if result is None:
            print(f"  FAILED: Could not update existing case {case_identifier}")
            continue

        key = case_detail.get("key") or str(case_identifier)
        existing_cases[title] = key
        print(f"  UPDATED: {key} — set to Published")
    else:
        result = create_test_case(test_data, folder_id)
        if not result:
            print(f"  FAILED: {test_data['title']}")
            continue

        key = result.get("key") or result.get("id") or "(unknown)"
        existing_cases[title] = key
        print(f"  CREATED: {key} — {test_data['title']}")

    folder_key = tuple(folder_hierarchy)
    cases_by_folder.setdefault(folder_key, []).append({"key": key, "title": title})

for folder_key, cases in cases_by_folder.items():
    folder_name = " / ".join(folder_key)
    cycle_title = f"{folder_name} - E2E"

    if cycle_title in existing_cycles:
        cycle_key = existing_cycles[cycle_title]
        print(f"\nUSING EXISTING CYCLE: {cycle_key} — {cycle_title}")
    else:
        cycle_folder_id = get_cycle_folder_id(list(folder_key))
        if not cycle_folder_id:
            print(f"\nSKIP CYCLE: Could not resolve folder for {folder_name}")
            continue

        cycle_data = create_test_cycle(
            {"title": cycle_title, "objective": f"Folder-level E2E coverage for {folder_name}"},
            cycle_folder_id,
        )
        if not cycle_data:
            print(f"\nFAILED CYCLE: {cycle_title}")
            continue

        cycle_key = cycle_data.get("key") or cycle_data.get("ID") or cycle_data.get("id")
        if not cycle_key:
            print(f"\nFAILED CYCLE: Could not determine cycle key for {cycle_title}")
            continue

        existing_cycles[cycle_title] = cycle_key
        print(f"\nCREATED CYCLE: {cycle_key} — {cycle_title}")

    for case in cases:
        association = add_case_to_cycle(cycle_key, case["key"])
        if association is None:
            print(f"  FAILED TO ADD CASE: {case['key']} — {case['title']}")
            continue
        print(f"  ADDED TO CYCLE: {case['key']} — {case['title']}")
