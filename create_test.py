import os
import json
import requests
from dotenv import load_dotenv

load_dotenv()

PROJECT_KEY = "TVSYSTEMS"
AIO_BASE_URL = "https://tcms.aiojiraapps.com/aio-tcms/api/v1"
TEST_DATA_DIR = "test_data"

token = os.getenv("AIO_TOKEN")

if not token:
    raise ValueError("AIO_TOKEN is missing. Check your .env file.")

headers = {
    "Authorization": f"AioAuth {token}",
    "Content-Type": "application/json",
}


def validate(data, filename):
    errors = []

    # Reject wrong field names at the root level
    if "name" in data and "title" not in data:
        errors.append("Use 'title' not 'name'")
    if "testScriptType" in data:
        errors.append("Use 'scriptType' not 'testScriptType'")
    if "folder" in data and "folderHierarchy" not in data:
        errors.append("Use 'folderHierarchy' not 'folder' at root level")

    # title
    if "title" not in data:
        errors.append("Missing required field: title")
    elif not isinstance(data["title"], str) or not data["title"].strip():
        errors.append("'title' must be a non-empty string")

    # folderHierarchy in JSON is optional now; folder placement is derived from file path
    if "folderHierarchy" in data:
        fh = data["folderHierarchy"]
        if not isinstance(fh, list):
            errors.append("'folderHierarchy' must be a list when provided")
        elif not all(isinstance(item, str) and item.strip() for item in fh):
            errors.append("'folderHierarchy' must be a list of non-empty strings")

    # scriptType
    if "scriptType" not in data:
        errors.append("Missing required field: scriptType")
    else:
        st = data["scriptType"]
        if not isinstance(st, dict):
            errors.append("'scriptType' must be an object")
        else:
            if st.get("ID") != 7:
                errors.append(f"'scriptType.ID' must be 7, got: {st.get('ID')!r}")
            if st.get("name") != "Classic":
                errors.append(f"'scriptType.name' must be 'Classic', got: {st.get('name')!r}")

    # precondition
    if "precondition" not in data:
        errors.append("Missing required field: precondition")
    elif not isinstance(data["precondition"], str):
        errors.append("'precondition' must be a string")

    # priority — reject if string
    if "priority" in data and isinstance(data["priority"], str):
        errors.append(f"'priority' must not be a plain string, got: {data['priority']!r}")

    # tags — reject if list of strings
    if "tags" in data:
        tags = data["tags"]
        if isinstance(tags, list) and any(isinstance(t, str) for t in tags):
            errors.append("'tags' must not be a list of plain strings")

    # steps
    if "steps" not in data:
        errors.append("Missing required field: steps")
    else:
        steps = data["steps"]
        if not isinstance(steps, list) or len(steps) == 0:
            errors.append("'steps' must be a non-empty list")
        else:
            for i, step in enumerate(steps):
                n = i + 1
                if not isinstance(step, dict):
                    errors.append(f"Step {n} is not an object")
                    continue
                if "stepType" not in step:
                    errors.append(f"Step {n} missing 'stepType'")
                elif step["stepType"] != "TEXT":
                    errors.append(f"Step {n} 'stepType' must be 'TEXT', got: {step['stepType']!r}")
                if "step" not in step:
                    errors.append(f"Step {n} missing 'step'")
                elif not isinstance(step["step"], str) or not step["step"].strip():
                    errors.append(f"Step {n} 'step' must be a non-empty string")
                if "data" not in step:
                    errors.append(f"Step {n} missing 'data'")
                if "expectedResult" not in step:
                    errors.append(f"Step {n} missing 'expectedResult'")
                elif not isinstance(step["expectedResult"], str) or not step["expectedResult"].strip():
                    errors.append(f"Step {n} 'expectedResult' must be a non-empty string")

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
    except Exception as e:
        print(f"  ERROR: Could not parse folder response: {e}")
        return None


def create_test_case(test_data, folder_id):
    url = f"{AIO_BASE_URL}/project/{PROJECT_KEY}/testcase"
    payload = {
        "title": test_data["title"],
        "scriptType": test_data["scriptType"],
        "folder": {"ID": folder_id},
        "precondition": test_data.get("precondition", ""),
        "steps": test_data["steps"],
    }
    response = requests.post(url, headers=headers, json=payload)
    if response.status_code not in (200, 201):
        print(f"  ERROR: Test case API returned {response.status_code}: {response.text}")
        return None
    try:
        return response.json()
    except Exception as e:
        print(f"  ERROR: Could not parse test case response: {e}")
        return None


def fetch_existing_titles():
    titles = set()
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
            return titles

        try:
            data = response.json()
        except Exception as e:
            print(f"  WARNING: Could not parse test case list response: {e}")
            return titles

        items = data.get("items", [])
        for item in items:
            title = item.get("title")
            if isinstance(title, str) and title.strip():
                titles.add(title.strip())

        if data.get("isLast", True) or not items:
            break

        start_at += len(items)

    return titles


def folder_hierarchy_from_path(path):
    rel_dir = os.path.dirname(os.path.relpath(path, TEST_DATA_DIR))
    if rel_dir in ("", "."):
        return []
    return [part for part in rel_dir.split(os.sep) if part and part != "."]


# --- MAIN FLOW ---

if not os.path.isdir(TEST_DATA_DIR):
    raise FileNotFoundError(f"Test data directory not found: {TEST_DATA_DIR}")

json_files = []
for root, _, files in os.walk(TEST_DATA_DIR):
    for filename in files:
        if filename.endswith(".json"):
            json_files.append(os.path.join(root, filename))

json_files.sort()

if not json_files:
    print(f"No JSON files found in {TEST_DATA_DIR}")
    exit()

print("Loading existing test case titles from AIO...")
existing_titles = fetch_existing_titles()
print(f"Loaded {len(existing_titles)} existing titles")

seen_titles = set()

for path in json_files:
    filename = os.path.relpath(path, TEST_DATA_DIR)
    print(f"\nProcessing: {filename}")

    try:
        with open(path, encoding="utf-8") as f:
            test_data = json.load(f)
    except json.JSONDecodeError as e:
        print(f"  ERROR: JSON parse error: {e}")
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
    if title in existing_titles:
        print(f"  SKIP: Title already exists in AIO: {title}")
        continue
    seen_titles.add(title)

    folder_hierarchy = folder_hierarchy_from_path(path)
    if not folder_hierarchy:
        print("  SKIP: File is directly under test_data; put it inside a subfolder to derive folder hierarchy")
        continue

    folder_id = get_folder_id(folder_hierarchy)
    if not folder_id:
        print(f"  SKIP: Could not resolve folder for {filename}")
        continue

    result = create_test_case(test_data, folder_id)
    if result:
        key = result.get("key") or result.get("id") or "(unknown)"
        existing_titles.add(title)
        print(f"  CREATED: {key} — {test_data['title']}")
    else:
        print(f"  FAILED: {test_data['title']}")