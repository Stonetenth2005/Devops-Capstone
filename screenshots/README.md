# Submission screenshots

Evidence for each rubric module in [GRADING.md](../GRADING.md). File names start with the module number. How to produce each one is in [YOUR-STEPS.md](../YOUR-STEPS.md).

## Captured

| Module | File | Shows |
|---|---|---|
| M1 / M4 | `m1-m4-app-localhost-3000.png` | ClinicFlow UI at `localhost:3000` with booked, checked-in, completed and cancelled visits |
| M1 | `m1-double-booking-rejected.png` | Booking form rejecting a clash: *Doctor already has an appointment* (HTTP 409) |
| M1 | `m1-swagger-api-docs.png` | Swagger UI at `localhost:8000/docs` listing the GET/POST/PUT/DELETE endpoints |
| M2 | `m2-pytest-19-passed.png` | `pytest -v`: 19 passed |
| M2 | `m2-ruff-code-quality.png` | `ruff check` and `ruff format --check` clean |
| M3 | `m3-git-commit-history.png` | `git log --oneline`: 18 meaningful commits |
| M4 | `m4-docker-compose-up-build.png` | `docker compose up --build`: images built, all 3 containers healthy |
| M7 | `m7-terraform-validate.png` | `terraform fmt -check` and `terraform validate` succeed |
| M9 | `m9-metrics-endpoint-local.png` | `curl /metrics`: business and HTTP metrics (local Compose backend) |
| M9 | `m9-metrics-endpoint-browser.png` | `localhost:8000/metrics` in the browser |

## Still to capture (need GitHub / AWS sign-in)

| Module | File name to use | YOUR-STEPS section |
|---|---|---|
| M3 | `m3-github-commits-page.png` (repo → Commits) | 4 |
| M5 | `m5-actions-green-run.png` + the run URL | 4, 7 |
| M5 | `m5-ghcr-packages-sha-tags.png` | 4 |
| M6 | `m6-trivy-scan-output.png` | 4 |
| M7 | `m7-terraform-plan.png` | 5 |
| M7 | `m7-aws-console-vpc.png`, `m7-aws-console-eks.png` | 5 |
| M7 | `m7-terraform-destroy.png` | 10 |
| M8 | `m8-kubectl-get-pods.png`, `m8-kubectl-get-svc.png`, `m8-helm-list.png` | 7 |
| M8 | `m8-app-via-ingress.png` | 7 |
| M9 | `m9-metrics-endpoint-cluster.png` (via port-forward) | 8 |
| M9 | `m9-prometheus-targets-up.png`, `m9-grafana-dashboard.png` | 8 |
