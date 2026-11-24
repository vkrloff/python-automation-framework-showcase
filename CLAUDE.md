# CLAUDE.md

## Project

Portfolio test automation framework for **OWASP Juice Shop**, meant to show Middle/Senior QA
Automation skills in Python. Quality of the framework (design, typing, reliability) matters more
than test count.

- **SUT:** `bkimminich/juice-shop` (pinned tag in `docker-compose.yml`), `http://localhost:3000`.
  It is a deliberately vulnerable app: some "bugs" are intended challenges. Do not report them as defects.
- **Stack:** Python 3.13 + uv, pytest, Playwright (Python), requests, Pydantic v2,
  pydantic-settings, Locust, Allure, Docker Compose, GitHub Actions.

## Structure

```
src/framework/          installable package `framework` (src layout)
  api/                  API clients wrapping requests.Session; return Pydantic models
  models/               Pydantic v2 models for every request/response payload
  data/                 test data factories (unique, randomized, typed)
  ui/                   Playwright page objects / components
tests/
  conftest.py           shared fixtures (config, API clients, auth)
  api/                  API tests (marker: api)
  ui/                   UI tests (marker: ui)
load/                   Locust scenarios (dependency group `load`)
docs/                   test strategy, design notes
```

Layering: `tests -> framework.ui / framework.api -> framework.models`. Tests never use raw
`requests` calls or raw locators; they go through clients and page objects.

## Commands

```bash
docker compose up -d --wait            # start SUT, block until healthcheck passes
docker compose down                    # stop SUT
uv sync --all-groups                   # install everything (dev + load groups)
uv run pytest                          # all tests
uv run pytest -m api                   # API tests only
uv run pytest -m ui                    # UI tests only
uv run ruff check . && uv run ruff format --check .
uv run mypy                            # strict type check (src, tests, load)
uv run pre-commit run --all-files      # every quality gate
```

Do not run `playwright install` unless asked.

## Coding rules

1. **Strict typing.** `mypy --strict` must pass. Annotate everything; no bare `Any` or
   `# type: ignore` without a code and a reason comment. Every API payload and response is a
   Pydantic v2 model. Never pass raw dicts around.
2. **No sleeps.** `time.sleep`, `page.wait_for_timeout` and fixed delays are forbidden. Use
   Playwright auto-waiting and web-first assertions (`expect(...)`). For async backend state, use
   a polling helper with an explicit timeout and condition.
3. **Independent tests.** Each test sets up its own state, can run alone, in any order and in
   parallel (pytest-xdist). No shared mutable state between tests and no test ordering.
4. **Test data only via factories / API.** Build data with factories in `framework/data` and set
   up state through the API (e.g. register a fresh user per test), never through the UI or
   hardcoded shared accounts. Seeded Juice Shop accounts are used only where a test is about them,
   and are named in one constants module.
5. **Config from the environment.** Base URL and credentials come from settings
   (`pydantic-settings`, `.env`). No hardcoded hosts in code.
6. **Assertions** live in tests (or dedicated assertion helpers), not in page objects or clients.
   Clients return data; tests decide what is correct.
7. **Style.** ruff (lint + format, line length 100) decides formatting. Keep functions small and
   names descriptive; use markers `api` / `ui` / `smoke` (strict markers are enabled).
8. **Before you finish** a change, run ruff, mypy and pytest and make sure they pass.
