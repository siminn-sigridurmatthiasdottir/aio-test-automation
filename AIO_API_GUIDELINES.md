# AIO API Usage Rules and Guidelines

## Purpose

This document defines rules and best practices for interacting with the AIO Tests API in this project.

It is intended for:

* Developers
* QA engineers
* Automation scripts and agents

---

## Security Rules

1. Never commit secrets

   * Do not commit `.env`
   * Do not commit API tokens
   * Do not hardcode tokens in code

2. Use environment variables only

   ```python
   token = os.getenv("AIO_TOKEN")
   ```

3. Each user must use their own API token

---

## API Basics

### Base URL

```
https://tcms.aiojiraapps.com/aio-tcms/api/v1
```

### Authentication

Header must be:

```
Authorization: AioAuth <TOKEN>
```

---

## Test Case Creation Rules

### Required fields (minimum working payload)

```json
{
  "title": "Test title",
  "scriptType": { "ID": 7 },
  "steps": [
    {
      "stepType": "TEXT",
      "step": "Step description",
      "data": "",
      "expectedResult": "Expected result"
    }
  ]
}
```

---

## Field Rules

### Title

* Must use `title` (not `name`)
* Mandatory

### Script Type

* Use:

  ```json
  { "ID": 7 }
  ```
* 7 represents Classic (step-by-step tests)

### Steps

Each step must include:

```json
{
  "stepType": "TEXT",
  "step": "...",
  "data": "",
  "expectedResult": "..."
}
```

Allowed `stepType` values:

* TEXT (default for manual tests)
* BDD_* (for Gherkin tests)

### Preconditions

Optional but recommended:

```json
"precondition": "..."
```

### Tags

* Use `tags`, not `labels`
* Example:

  ```json
  "tags": ["e2e", "stb"]
  ```

---

## Common Mistakes

* Using `name` instead of `title`
* Using `"priority": "High"` (must be an object)
* Using `"STEP"` as stepType (invalid)
* Using `testScriptType` (incorrect field name)
* Omitting `data` field in steps
* Sending invalid enum values

---

## Testing Strategy

1. Start with a single test case
2. Validate it in AIO UI
3. Scale only after confirmation

---

## Project Structure

```
aio-test-project/
├── create_test.py
├── README.md
├── AIO_API_GUIDELINES.md
├── .env           (not committed)
├── .gitignore
└── venv/
```

---

## Future Improvements

* Move test definitions to JSON files
* Support bulk test creation
* Add folder assignment
* Add priority, type, and status support
* Improve error handling and retries

---

## Agent Behavior Rules

Agents working on this project must:

1. Follow API schema strictly
2. Prefer minimal working payloads first
3. Validate responses before proceeding
4. Never expose tokens
5. Log API responses clearly

---

## Definition of Done

A script is considered working when:

* API returns status 200
* Test case appears in AIO
* Steps are correctly formatted
* No manual fixes are required in the UI
