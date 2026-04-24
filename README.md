# AIO Test Automation Pilot

This project creates AIO Tests test cases using the AIO REST API, specifically for STB (Set-Top Box) end-to-end testing scenarios.

## Current Status

Working proof of concept for automated test case creation:

- **Project**: TVSYSTEMS
- **Script type**: Classic (ID: 7)
- **Tool**: Python with requests library
- **Environment**: Cross-platform Python script

## Project Structure

- `create_test.py` - Main Python script that creates test cases in AIO
- `requirements.txt` - Python dependencies (requests, python-dotenv, etc.)
- `.env` - Environment file for AIO API token (not committed)
- `venv/` - Python virtual environment
- `test_data/` - Directory for test data files (currently empty)
- `AIO_API_GUIDELINES.md` - Comprehensive API usage rules and best practices
- `.gitignore` - Git ignore rules (excludes .env, venv, __pycache__)

## Setup

1. **Clone and navigate to the project**:
   ```bash
   cd aio-test-project
   ```

2. **Activate the virtual environment**:
   ```bash
   source venv/bin/activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure your AIO token**:
   - Create a `.env` file in the project root
   - Add your AIO API token:
     ```
     AIO_TOKEN=your_aio_token_here
     ```

## Usage

Run the script to create a new test case:

```bash
python create_test.py
```

The script will:
1. Create/retrieve the folder structure: `STB E2E` → `Remote`  
2. Create a test case with preconditions and test steps
3. Output the created test case key and folder information

## What It Creates

**Test Case**: "STB E2E - Pair remote (API test)"
- **Precondition**: STB is factory reset. Remote has batteries.
- **Steps**:
  1. Power on the STB → Setup screen is shown
  2. Start pairing → Remote is detected  
  3. Confirm pairing → Remote works

## Security

- API tokens are stored in `.env` (git-ignored)
- Follow security guidelines in `AIO_API_GUIDELINES.md`
- Never commit secrets or tokens to version control

## Dependencies

- Python 3.14+
- requests 2.33.1
- python-dotenv 1.2.2
- Additional dependencies listed in `requirements.txt`