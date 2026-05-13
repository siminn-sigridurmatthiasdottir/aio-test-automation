# AIO Reports CLI

Small Python CLI tool for generating AIO test cycle reports.

## Features

- Pulls executed cycle data from AIO API
- Generates JSON and Markdown reports
- Stores reports in `reports/<report-name>/`
- Supports pagination for cycle test cases
- Calculates summary metrics:
  - total
  - executed
  - passed
  - failed
  - blocked
  - in progress
  - not run
  - pass rate based on executed cases

## Setup

1. Create and activate your virtual environment.
2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Copy `.env.example` to `.env` and set your token:

```env
AIO_TOKEN=your_aio_token_here
AIO_PROJECT_KEY=TVSYSTEMS
```

Notes:
- `AIO_TOKEN` is required.
- API keys are read from environment variables only.

## Run

Main command:

```bash
python -m aio_reports.cli --cycle TVSYSTEMS-CY-21
```

Compatibility command:

```bash
python generate_cycle_report.py --cycle TVSYSTEMS-CY-21
```

Optional flags:

- `--test-name` (overrides the derived report name)
- `--project` (default: `TVSYSTEMS`)
- `--output-dir` (default: `reports`)

Required flags:

- `--cycle`

Report name source:

- `--test-name` if provided
- otherwise the AIO cycle title
- otherwise the cycle key

Report name sanitization:

- converted to lowercase
- spaces become `-`
- unsafe characters are removed

## Expected Output

If the cycle title is `Web E2E`, the derived report name becomes `web-e2e` and the output paths are:

- `reports/web-e2e/web-e2e_report.json`
- `reports/web-e2e/web-e2e_report.md`

Custom root output directory:

```bash
python -m aio_reports.cli --cycle TVSYSTEMS-CY-21 --output-dir output
```

If the derived report name is `web-e2e`, this writes:

- `output/web-e2e/web-e2e_report.json`
- `output/web-e2e/web-e2e_report.md`