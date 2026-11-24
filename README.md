# juice-shop-qa

Test automation framework for [OWASP Juice Shop](https://owasp-juice.shop), built to show
production-grade QA automation practice in Python: layered framework, strictly typed code,
isolated tests, and CI-ready infrastructure.

> **Status:** work in progress. The repository skeleton is in place; tests come next.

## Stack

| Area | Tools |
|---|---|
| Language / packaging | Python 3.13, [uv](https://docs.astral.sh/uv/) |
| Test runner | pytest |
| UI | Playwright (Python) |
| API | requests + Pydantic v2 models |
| Load | Locust |
| Reporting | Allure |
| Infra / CI | Docker Compose, GitHub Actions |
| Quality gates | ruff, mypy (strict), pre-commit |

## Quick start

```bash
docker compose up -d --wait        # start Juice Shop on http://localhost:3000, wait until healthy
uv sync --all-groups               # create .venv with all dependencies
uv run pre-commit install          # enable git hooks
uv run pytest                      # run tests
docker compose down                # stop Juice Shop
```

## Layout

```
src/framework/
  api/      typed API clients
  models/   Pydantic request/response models
  data/     test data factories
  ui/       Playwright page objects
tests/
  api/      API tests
  ui/       UI tests
load/       Locust scenarios
docs/       test strategy and design notes
```
