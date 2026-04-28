import os
import json
import requests
from dotenv import load_dotenv

load_dotenv()

PROJECT_KEY = "TVSYSTEMS"
AIO_BASE_URL = "https://tcms.aiojiraapps.com/aio-tcms/api/v1"

token = os.getenv("AIO_TOKEN")

if not token:
    raise ValueError("AIO_TOKEN is missing. Check your .env file.")

headers = {
    "Authorization": f"AioAuth {token}",
    "Content-Type": "application/json",
}


def create_or_get_folder():
    url = f"{AIO_BASE_URL}/project/{PROJECT_KEY}/testcase/folder/hierarchy"

    data = {
        "baseFolderId": None,
        "folderHierarchy": ["VSB E2E", "Remote"]
    }

    response = requests.put(url, headers=headers, json=data)

    print("Folder Status:", response.status_code)
    print("Folder Response:")

    try:
        folder_data = response.json()
        print(json.dumps(folder_data, indent=2))
    except Exception:
        print(response.text)
        return None

    if response.status_code != 200:
        print("ERROR creating folder")
        return None

    return folder_data


def create_test_case(folder_id):
    url = f"{AIO_BASE_URL}/project/{PROJECT_KEY}/testcase"

    data = {
        "title": "STB E2E - Pair remote (API test)",
        "scriptType": {
            "ID": 7,
            "name": "Classic"
        },
        "folder": {
            "ID": folder_id
        },
        "precondition": "STB is factory reset. Remote has batteries.",
        "steps": [
            {
                "stepType": "TEXT",
                "step": "Power on the STB",
                "data": "",
                "expectedResult": "Setup screen is shown"
            },
            {
                "stepType": "TEXT",
                "step": "Start pairing",
                "data": "",
                "expectedResult": "Remote is detected"
            },
            {
                "stepType": "TEXT",
                "step": "Confirm pairing",
                "data": "",
                "expectedResult": "Remote works"
            }
        ]
    }

    response = requests.post(url, headers=headers, json=data)

    print("Test Case Status:", response.status_code)
    print("Test Case Response:")

    try:
        test_data = response.json()
        print(json.dumps(test_data, indent=2))
    except Exception:
        print(response.text)
        return None

    if response.status_code != 200:
        print("ERROR creating test case")
        return None

    return test_data


# --- MAIN FLOW ---

folder_response = create_or_get_folder()

if not folder_response:
    print("Stopping: folder creation failed")
    exit()

target_folder = folder_response  # AIO returns single object

test_case = create_test_case(target_folder["ID"])

if test_case:
    print("Created test case:", test_case["key"])
    print("Folder used:", target_folder["name"], "ID:", target_folder["ID"])
else:
    print("Test case creation failed")