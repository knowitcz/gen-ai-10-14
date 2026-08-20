# HB-5: Deployment Readiness Report — Happy Bank

**Example solution** for the tasks in [deployability.md](deployability.md) and [report.md](report.md).

| | |
|---|---|
| **Assessed revision** | commit **Add task HB-5: Report** |
| **Assessed by** | Operations / SRE review, with AI assistance |
| **Verdict** | **Not ready to deploy.** 7 blocking issues, 6 accepted as documented debt. |

## 1. Scope, target environment and method

Verdicts depend entirely on *where* we intend to deploy. This report assumes the
first realistic target:

* one containerized instance behind a reverse proxy, in an internal environment,
* restarted and rescheduled by an orchestrator (Docker Compose / Kubernetes),
* handling real — if small — customer money, therefore subject to audit expectations,
* operated by a team that is *not* the development team.

If the target were only a laptop demo, most items below drop to "acceptable".
The assumption is the load-bearing part of the assessment, so it is stated first.

Method — three passes, no guessing:

1. **Static:** read `app/`, `pyproject.toml`, `.gitignore`, `.github/instructions/`.
2. **Dynamic:** ran the server and exercised the API, then compared what appeared on
   stdout against what appeared in `logs/app.log` (commands in [Appendix A](#appendix-a--how-to-reproduce)).
3. **Artifact:** built the distribution (`uv build --wheel`) and inspected what a
   deployed artifact would actually contain.

## 2. Findings

### 2.1 How does the project log?

Logging was introduced in HB-4 and is centralized in `app/logging_config.py`:

* Standard library `logging`, configured once by `setup_logging()`, called at import
  time in `app/main.py:12`. Module loggers are obtained as `logging.getLogger(__name__)`,
  so the logger hierarchy mirrors the package structure — good.
* **Single sink: a file.** `log_to_file=True`, `log_to_console=False` by default
  (`app/logging_config.py:22`). Nothing the application logs reaches stdout.
* `RotatingFileHandler` on `logs/app.log`, 10 MB × 5 backups (≈60 MB ceiling, oldest
  data silently discarded). `logs/` is git-ignored, i.e. it is a local, unshipped file.
* Format: `%(asctime)s - %(name)s - %(levelname)s - %(message)s`, `datefmt='%Y-%m-%d %H:%M:%S'`
  — local time, no timezone, no milliseconds, no process/thread, no request identifier.
* Root level `INFO`, so the `DEBUG` statements that exist (e.g. `app/services/account_service.py:16`)
  never appear in a deployed run.
* Third-party noise is suppressed: `uvicorn.access` → `WARNING`, `sqlalchemy.engine` → `WARNING`
  (`app/logging_config.py:43-44`).
* Nothing is configurable at deploy time — no environment variables for level,
  destination or format. Changing the log level means editing code and rebuilding.
* `.github/instructions/python-log.instructions.md` makes Copilot-generated code carry
  logging by default. That is a genuine strength: the convention is enforced at
  authoring time, not by review alone.

**Two consequences worth calling out explicitly.**

*Access logs do not exist anywhere.* uvicorn's `uvicorn.access` logger has its own
handler and `propagate=False`, so raising its level to `WARNING` does not redirect
HTTP access lines into the app log — it deletes them. Confirmed: five requests were
issued during the dynamic pass and produced zero access lines on stdout and zero in
the file.

*Application logs and framework logs go to different places.* `uvicorn.error`
resolves to uvicorn's own handler (stderr) and never propagates to the root logger,
so unhandled exceptions — the 500s that matter most — exist **only** on stdout and
are absent from `logs/app.log`. The dynamic pass reproduced exactly that: a full ASGI
traceback on stdout, no corresponding entry in the log file. An operator reading the
log file would conclude the request simply never happened.

### 2.2 What exactly is recorded?

Actual output from the dynamic pass (`logs/app.log`, verbatim):

```
2026-08-20 12:37:44 - app.main - INFO - Application starting up
2026-08-20 12:37:44 - app.startup - INFO - Default accounts created successfully.
2026-08-20 12:37:49 - app.services.account_service - INFO - Account 1 retrieved successfully
2026-08-20 12:37:49 - app.services.account_service - WARNING - Account 999 not found
2026-08-20 12:37:49 - app.services.account_service - INFO - Transfer initiated: 999999 from account 1 to 2
2026-08-20 12:37:49 - app.services.account_service - ERROR - Transfer failed: Insufficient balance
Traceback (most recent call last):
  ...
ValueError: Insufficient balance
```

| Layer | Coverage | Assessment |
|---|---|---|
| Service (`account_service`) | Intent + outcome for every money operation, `exc_info=True` on failure | **Good.** This is the layer that matters and it is done well |
| Startup (`main`, `startup`) | "Application starting up", seed data created | Minimal but sufficient |
| API routes | **Nothing** — no route logs an entry, no HTTP status, no caller | Gap; contradicts the project's own instruction file ("API Routes — INFO level for endpoint access") |
| Repository | Nothing | Acceptable; the service layer covers the same events |
| HTTP access | **Nothing** (suppressed, see 2.1) | Gap — no method, path, status, latency, client |
| Unhandled 500s | On stdout only, not in the log file | Gap |
| Shutdown | Nothing | Minor gap — cannot distinguish a clean stop from a crash or an OOM kill |

What a log line **cannot** answer today: which request did this belong to, who called
it, what HTTP status the caller received, how long it took, which instance and which
process produced it. Two concurrent transfers interleave in the file with no way to
separate them.

On sensitive data: no names, no credentials, no PII in the messages — the HB-4
instruction file is being respected. Account IDs and amounts *are* logged, which is
correct and necessary for an audit trail, but it makes the log file itself a
confidential artifact. Today it is an unencrypted file on a container filesystem with
no retention policy and no access control. The content is right; its handling is not.

### 2.3 Does the project allow runtime monitoring?

No. This is the weakest area.

* **No health endpoint.** `GET /health` returns 404 (verified). The only routes are
  `/`, `/api/v1/account/{id}`, `/api/v1/account/withdraw`, `/api/v1/bank/transfer`.
  An orchestrator has nothing to probe, so it cannot restart a wedged instance and a
  load balancer cannot take a broken one out of rotation.
* **No readiness signal.** Liveness ≠ readiness. The process accepts connections
  before anyone has established that the database is reachable. A `200` from the REST
  API would not prove the app can serve traffic — the DB check is the interesting part.
* **No metrics.** No request counters, latency histograms, error rates, no `/metrics`
  endpoint, no OpenTelemetry. Alerting can only be built by scraping text logs.
* **No version/build info** exposed anywhere, so "which revision is running in prod?"
  is unanswerable from the running system.
* **Error rate is actively misleading.** `app/api/bank_routes.py:1` imports
  `HTTPException` from `http.client` instead of `fastapi`. A transfer with insufficient
  funds therefore raises `TypeError: HTTPException() takes no keyword arguments` and
  the caller gets **HTTP 500** where 400 was intended (verified: the same overdraw
  returns 400 on `/account/withdraw` but 500 on `/bank/transfer`). Any alert on the 500
  rate would fire on ordinary customer behaviour, and the real defects would drown in it.

### 2.4 Deployment artifact and runtime configuration

Building the wheel exposes problems no amount of code reading would surface:

* `pyproject.toml` sets `package-dir = {"" = "app"}`, so the wheel ships `main.py`,
  `db.py`, `api/`, `services/`, … as **top-level** modules. There is no `app` package
  in the artifact, so `uvicorn app.main:app` cannot work from an installed
  distribution — it only works with the repo root as the working directory.
* `resources/` is **not** in the wheel. `FileResponse("resources/static/index.html")`
  (`app/main.py:24`) is resolved against the working directory, and
  `create_default_accounts()` reads `../resources/data/default_accounts.sql` relative
  to `__file__` (`app/startup.py:16`) — both break outside the repo checkout, the
  latter by crashing startup on a fresh database.
* Tests (`test_bank_service.py`, `test_amount_validator.py`) are shipped **inside** the
  wheel.
* Dependencies in `pyproject.toml` carry no version constraints. `uv.lock` pins them
  for the `uv` path, but the documented `pip install -e .` path resolves whatever is
  newest — builds are not reproducible across environments.
* `DATABASE_URL = "sqlite:///./app.db"` is hardcoded (`app/db.py:3`) — a file relative
  to the working directory, with `check_same_thread=False` while FastAPI runs sync
  endpoints in a threadpool. One file, one node: no horizontal scaling, no backups, and
  `database is locked` under concurrent writes.
* Schema is created with `SQLModel.metadata.create_all()` at import (`app/main.py:15`)
  and **demo accounts are seeded whenever the table is empty** (`app/main.py:29`).
  Deploying this to production creates "Alice" and "Bob" with 1000 each. There is no
  migration mechanism, so no controlled path for any future schema change.
* All of the above runs at **module import time**, i.e. once per worker process, before
  the ASGI lifespan starts — concurrent `create_all` and concurrent seeding across
  workers, and no clean shutdown hook.
* The money-moving endpoints have **no authentication, authorization or rate limiting**.
  Anyone who can reach the port can transfer anyone's money.
* No CI: nothing runs the 21 existing tests or a linter on merge, so nothing prevents
  the next regression from reaching the deployable branch.

## 3. Status table

Verdicts: **OK** = fine as is · **Acceptable** = ship with documented debt ·
**Critical** = blocks the deploy.

| # | Area | Current state | Verdict |
|---|---|---|---|
| 1 | Logging framework & structure | Centralized `setup_logging()`, per-module loggers, lazy `%s` formatting, rotation configured | **OK** |
| 2 | Business-event coverage | Every money operation logs intent, outcome and exception with `exc_info=True` | **OK** |
| 3 | Sensitive data in messages | No PII, names or credentials; IDs and amounts only | **OK** |
| 4 | Convention enforcement for new code | `.github/instructions/python-log.instructions.md` applies to all `**/*.py` | **OK** |
| 5 | Unit tests exist | 21 tests, all passing locally | **OK** |
| 6 | DEBUG statements invisible in prod | Root level `INFO` | **Acceptable** — intended; revisit when level becomes configurable (#12) |
| 7 | Repository layer not logged | Service layer covers the same events | **Acceptable** |
| 8 | Plain-text log format | Not machine-parsable; no structured fields | **Acceptable** — grep works for a single instance; JSON is the HB-7 task |
| 9 | No metrics / tracing | No `/metrics`, no OTel | **Acceptable** — logs + health cover an MVP; not acceptable once traffic is real |
| 10 | Timestamps: local time, second precision | `2026-08-20 12:37:49`, no zone, no ms | **Acceptable** — but the fix is one line, so do it now |
| 11 | Shutdown not logged | Clean stop indistinguishable from a crash | **Acceptable** |
| 12 | Logging not configurable at deploy time | Level, destination, format hardcoded | **Critical** — cannot raise the level during an incident without a rebuild |
| 13 | Logs go to a file, not stdout | `log_to_console=False`; file is git-ignored, container-local | **Critical** — logs die with the container; no aggregation, no retention, no access control |
| 14 | Framework/error logs bypass the app log | `uvicorn.error` never propagates; 500 tracebacks only on stdout | **Critical** — the log file omits the most important events |
| 15 | No HTTP access log | `uvicorn.access` raised to `WARNING`, deleting it | **Critical** — no method/path/status/latency/caller, no request correlation, no audit trail |
| 16 | No health / readiness endpoint | `/health` → 404 | **Critical** — orchestrator cannot detect or recover a broken instance |
| 17 | Business error returned as HTTP 500 | `http.client.HTTPException` in `bank_routes.py:1` | **Critical** — corrupts the error-rate signal *and* is a customer-visible defect |
| 18 | Schema + demo data created at startup; no migrations | `create_all()` + `create_default_accounts()` at import | **Critical** — production would be seeded with Alice and Bob; no path for schema change |
| 19 | Artifact is not runnable; config hardcoded | Wheel has no `app` package, no `resources/`; `DATABASE_URL` fixed in code | **Critical** — one artifact cannot be promoted across environments |
| 20 | No authn/authz or rate limiting on transfers | Endpoints fully open | **Critical** — out of the logging brief, but an unconditional deploy blocker |
| 21 | SQLite single file, no backups | `sqlite:///./app.db`, `check_same_thread=False` | **Critical for production**; acceptable for a single-node internal pilot with a documented backup and a scaling limit |
| 22 | No CI on merge | Tests and lint run only locally | **Critical** — no gate protecting the deployable branch (this is the HB-6 task) |

Summary: 5 OK · 6 acceptable · 11 critical.

## 4. Actions

Ordered by what unblocks a deploy soonest. Effort is a rough dev-day estimate.

### P0 — must be done before the first deploy

| # | Action | Addresses | Effort |
|---|---|---|---|
| A1 | Fix the import in `app/api/bank_routes.py` — use `fastapi.HTTPException`, return 400 with a `detail`, and add a regression test | 17 | 0.5 |
| A2 | Log to **stdout** by default (`log_to_console=True`), keep the file handler opt-in for local development; let the platform collect and retain the stream | 13, 14 | 0.5 |
| A3 | Configure logging from the environment: `LOG_LEVEL`, `LOG_FORMAT`, `LOG_TO_FILE`, and move `setup_logging()` out of import scope into the FastAPI lifespan | 12, 6 | 1 |
| A4 | Route framework logs through the app configuration: drop the `uvicorn.access` suppression, attach uvicorn's loggers to the root handlers (`propagate=True`), and log shutdown in the lifespan | 14, 15, 11 | 1 |
| A5 | Add request-scoped context: middleware assigning a request ID (honouring an inbound `X-Request-ID`), logged with method, path, status, duration and client, injected via a `logging` filter so every line carries it | 15 | 1.5 |
| A6 | Add `GET /health` (liveness) and `GET /ready` (readiness, including a real `SELECT 1`), and expose build/revision info | 16 | 1 |
| A7 | Externalize configuration — `DATABASE_URL` and everything else from the environment via Pydantic settings; no defaults that silently point at a local file | 19 | 1 |
| A8 | Remove startup side effects: no `create_all()`, no demo seeding in the deployed path; make seeding an explicit opt-in flag used only by dev and test | 18 | 0.5 |
| A9 | Introduce schema migrations (Alembic) and run them as a deploy step, not from application code | 18 | 2 |
| A10 | Fix packaging: `packages = ["app"]`, exclude `test_*` from the wheel, ship or externalize `resources/`, resolve resource paths from `__file__` or config, and pin dependency ranges | 19 | 1 |
| A11 | Add authentication and authorization to the money-moving endpoints, plus rate limiting | 20 | 3+ |
| A12 | Add CI on merge requests: tests on Python 3.10+, PEP8/ruff, failures reported (the HB-6 task) | 22 | 1 |
| A13 | Decide and document the log retention and access policy: how long, who can read, where PII/financial data is allowed | 3, 13 | 0.5 |

### P1 — first iteration after the deploy

| # | Action | Addresses |
|---|---|---|
| B1 | UTC timestamps with milliseconds (`datefmt` + `%(msecs)03d` or `logging.Formatter(..., defaults=...)`) | 10 |
| B2 | Emit JSON-formatted logs so the aggregator can index fields instead of regex-matching text (the HB-7 task covers the transformation of existing logs) | 8 |
| B3 | Add INFO-level entry logging to the API routes, as the project's own instruction file already requires | 2.2 gap |
| B4 | Decide the database target: either accept SQLite with a documented single-instance constraint and an automated backup, or migrate to PostgreSQL before scaling out | 21 |
| B5 | Alerting on the now-trustworthy signals: 5xx rate, health-probe failures, `ERROR`-level volume | 9 |

### P2 — when traffic justifies it

| # | Action | Addresses |
|---|---|---|
| C1 | Prometheus metrics (`/metrics`): request rate, latency histogram, error rate, DB pool | 9 |
| C2 | Distributed tracing via OpenTelemetry, reusing the request ID from A5 as the trace correlation key | 9 |
| C3 | Separate the audit trail from the operational log — money movements belong in an append-only store with its own retention, not in a file that rotates away after 60 MB | 3, 13 |

### Release gate

Deploy is approved once **A1–A10, A12 and A13 are done** and the following hold:

1. A failed transfer returns 400, and the 5xx rate is zero under normal customer behaviour.
2. Every log line carries a request ID; a single request can be reconstructed end to end from the aggregator.
3. Unhandled exceptions appear in the same stream as application logs.
4. `/health` and `/ready` respond correctly, and `/ready` fails when the database is unreachable.
5. The same artifact runs in two environments with different configuration and no code change.
6. A fresh deploy creates no demo accounts.
7. CI passes on the merge request that contains these changes.

A11 (authentication) can be waived **only** if the deployment is network-isolated and
that isolation is documented and verified; otherwise it is part of the gate.

## Appendix A — how to reproduce

```bash
# static + tests
uv run pytest -q                       # 21 passed

# dynamic: run the server and exercise the API
uv run uvicorn app.main:app --port 8123 > stdout.txt 2>&1 &
curl -s -o /dev/null -w '%{http_code}\n' localhost:8123/health                 # 404 — no health endpoint
curl -s localhost:8123/api/v1/account/1
curl -s -o /dev/null -w '%{http_code}\n' \
  -X POST 'localhost:8123/api/v1/bank/transfer?from_account_id=1&to_account_id=2&amount=999999'   # 500, should be 400
curl -s -o /dev/null -w '%{http_code}\n' \
  -X POST 'localhost:8123/api/v1/account/withdraw?account_id=1&amount=999999'                     # 400, correct

# compare the two sinks
grep -c 'GET /api' stdout.txt logs/app.log      # 0 and 0 — no access logs anywhere
grep -c 'Traceback' stdout.txt logs/app.log     # traceback on stdout only

# artifact
uv build --wheel -o dist
unzip -l dist/*.whl        # top-level main.py/api/... — no `app` package, no resources/
```

## Appendix B — note for the workshop

The interesting move in this task is the **dynamic** pass. Reading
`app/logging_config.py` suggests logging is in decent shape; running the app and
diffing stdout against the log file is what reveals that access logs were deleted
rather than redirected, and that 500 tracebacks never reach the log file at all.
Building the wheel plays the same role for the deployment artifact. Ask the AI what
it *verified* versus what it *inferred* — and note that items 8, 16, 18 and 22 are
precisely the later tasks HB-7, HB-10, HB-9 and HB-6, so the action list doubles as
the workshop backlog.
