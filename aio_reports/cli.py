import argparse
import os

from dotenv import load_dotenv

from aio_reports.aio_client import AioClient
from aio_reports.markdown import to_markdown
from aio_reports.report_builder import build_report_payload
from aio_reports.storage import build_report_paths, write_json, write_text


DEFAULT_BASE_URL = "https://tcms.aiojiraapps.com/aio-tcms/api/v1"
DEFAULT_PROJECT_KEY = "TVSYSTEMS"
DEFAULT_OUTPUT_DIR = "reports"
DEFAULT_TIMEOUT_SECONDS = 30


def read_token_from_env() -> str:
    token = os.getenv("AIO_TOKEN", "").strip()
    if not token:
        raise ValueError("AIO_TOKEN is missing. Set it in environment or .env.")
    return token


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate JSON and Markdown report for an AIO executed cycle"
    )
    parser.add_argument("--cycle", required=True, help="Cycle key or ID (example: TVSYSTEMS-CY-21)")
    parser.add_argument(
        "--test-name",
        default=None,
        help="Optional report name override used for folder and file naming",
    )
    parser.add_argument(
        "--project",
        default=os.getenv("AIO_PROJECT_KEY", DEFAULT_PROJECT_KEY),
        help="AIO project key",
    )
    parser.add_argument(
        "--output-dir",
        default=DEFAULT_OUTPUT_DIR,
        help="Base output directory for report files",
    )
    return parser.parse_args()


def derive_report_name(explicit_name: str | None, cycle_title: str, cycle_key: str) -> str:
    if explicit_name and explicit_name.strip():
        return explicit_name
    if cycle_title and cycle_title.strip():
        return cycle_title
    return cycle_key


def main() -> None:
    load_dotenv()
    args = parse_args()

    token = read_token_from_env()
    client = AioClient(
        base_url=DEFAULT_BASE_URL,
        project_key=args.project,
        token=token,
        timeout_seconds=DEFAULT_TIMEOUT_SECONDS,
    )

    cycle_detail = client.fetch_cycle_detail(args.cycle)
    case_items = client.fetch_cycle_cases(args.cycle)
    cycle_title = cycle_detail.get("title", args.cycle)
    report_name_source = derive_report_name(args.test_name, cycle_title, args.cycle)

    safe_test_name, json_path, md_path = build_report_paths(
        output_dir=args.output_dir,
        test_name=report_name_source,
    )

    report = build_report_payload(
        project_key=args.project,
        test_name=safe_test_name,
        cycle_key=args.cycle,
        cycle_title=cycle_title,
        case_items=case_items,
    )

    write_json(json_path, report)
    write_text(md_path, to_markdown(report))

    print(f"Report JSON: {json_path}")
    print(f"Report Markdown: {md_path}")


if __name__ == "__main__":
    main()
