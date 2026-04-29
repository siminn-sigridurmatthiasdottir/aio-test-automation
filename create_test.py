import os
import json
import requests
from dotenv import load_dotenv

load_dotenv()

PROJECT_KEY = "TVSYSTEMS"
AIO_BASE_URL = "https://tcms.aiojiraapps.com/aio-tcms/api/v1"
TEST_DATA_DIR = "test_data/vsb_stb"

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

    # folderHierarchy
    if "folderHierarchy" not in data:
        errors.append("Missing required field: folderHierarchy")
    else:
        fh = data["folderHierarchy"]
        if not isinstance(fh, list) or len(fh) == 0:
            errors.append("'folderHierarchy' must be a non-empty list")
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


# --- MAIN FLOW ---

if not os.path.isdir(TEST_DATA_DIR):
    raise FileNotFoundError(f"Test data directory not found: {TEST_DATA_DIR}")

json_files = sorted(f for f in os.listdir(TEST_DATA_DIR) if f.endswith(".json"))

if not json_files:
    print(f"No JSON files found in {TEST_DATA_DIR}")
    exit()

for filename in json_files:
    path = os.path.join(TEST_DATA_DIR, filename)
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

    folder_id = get_folder_id(test_data["folderHierarchy"])
    if not folder_id:
        print(f"  SKIP: Could not resolve folder for {filename}")
        continue

    result = create_test_case(test_data, folder_id)
    if result:
        key = result.get("key") or result.get("id") or "(unknown)"
        print(f"  CREATED: {key} — {test_data['title']}")
    else:
        print(f"  FAILED: {test_data['title']}")