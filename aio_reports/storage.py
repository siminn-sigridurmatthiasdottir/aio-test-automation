import re
import json
import os
from typing import Any, Dict, Tuple


def sanitize_test_name(test_name: str) -> str:
    sanitized = test_name.strip().lower()
    sanitized = re.sub(r"[\s_]+", "-", sanitized)
    sanitized = re.sub(r"[^a-z0-9-]", "", sanitized)
    sanitized = re.sub(r"-+", "-", sanitized).strip("-")
    if not sanitized:
        raise ValueError("Report name must contain at least one valid character")
    return sanitized


def build_report_paths(output_dir: str, test_name: str) -> Tuple[str, str, str]:
    safe_test_name = sanitize_test_name(test_name)
    target_dir = os.path.join(output_dir, safe_test_name)
    os.makedirs(target_dir, exist_ok=True)

    json_path = os.path.join(target_dir, f"{safe_test_name}_report.json")
    md_path = os.path.join(target_dir, f"{safe_test_name}_report.md")
    return safe_test_name, json_path, md_path


def write_json(path: str, payload: Dict[str, Any]) -> None:
    with open(path, "w", encoding="utf-8") as file_handle:
        json.dump(payload, file_handle, indent=2, ensure_ascii=False)


def write_text(path: str, content: str) -> None:
    with open(path, "w", encoding="utf-8") as file_handle:
        file_handle.write(content)
