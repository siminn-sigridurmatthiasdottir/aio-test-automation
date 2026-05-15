from typing import Any, Dict, List, Optional

import requests


class AioClient:
    def __init__(self, base_url: str, project_key: str, token: str, timeout_seconds: int = 30):
        self.base_url = base_url.rstrip("/")
        self.project_key = project_key
        self.timeout_seconds = timeout_seconds
        self.headers = {
            "Authorization": f"AioAuth {token}",
            "Content-Type": "application/json",
        }

    def _get(self, path: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        url = f"{self.base_url}/project/{self.project_key}{path}"
        response = requests.get(url, headers=self.headers, params=params, timeout=self.timeout_seconds)
        response.raise_for_status()
        return response.json()

    def fetch_cycle_detail(self, cycle_key: str) -> Dict[str, Any]:
        return self._get(f"/testcycle/{cycle_key}/detail")

    def fetch_cycle_test_runs(self, cycle_key: str) -> List[Dict[str, Any]]:
        items: List[Dict[str, Any]] = []
        start_at = 0
        page_size = 100

        while True:
            page = self._get(
                f"/testcycle/{cycle_key}/testrun",
                params={"startAt": start_at, "maxResults": page_size},
            )
            page_items = page.get("items", [])
            items.extend(page_items)

            if page.get("isLast", True) or not page_items:
                break

            start_at += len(page_items)

        return items

    def fetch_test_run_detail(self, cycle_key: str, run_id: int) -> Dict[str, Any]:
        return self._get(f"/testcycle/{cycle_key}/testrun/{run_id}")
