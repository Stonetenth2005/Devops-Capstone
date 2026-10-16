# ClinicFlow: Clinic Appointment Booking (DevOps Capstone)

ClinicFlow is a front-desk console for a small clinic. Receptionists use it to **book patient appointments with doctors**, **check patients in** when they arrive, **mark visits complete**, and **manage the doctor roster**. The backend refuses to double-book a doctor and enforces a simple visit workflow.

The application is the vehicle for the real goal: a complete delivery path from laptop to a monitored Kubernetes cluster on AWS.

> **Doing the setup yourself?** Every manual step (installs, sign-ins, AWS, GitHub, screenshots, teardown) is in **[YOUR-STEPS.md](YOUR-STEPS.md)**.

---

## Architecture

```text
 Developer ── git push ──► GitHub ──► GitHub Actions
                                       ├─ ruff + pytest (19 tests)
                                       ├─ frontend build
                                       ├─ helm lint + terraform validate
                                       ├─ docker build (backend, frontend)  tag = commit SHA
                                       ├─ Trivy scan  (fail on HIGH/CRITICAL)
                                       ├─ push ──► GHCR
                                       └─ helm upgrade --install ──┐
                                                                   ▼
 Terraform ──► AWS: VPC (2 public + 2 private subnets, NAT) ──► EKS (managed node group)
                                                                   │
                         ┌────────── ingress-nginx (AWS load balancer) ──────────┐
                         │  /      ──► frontend Service ──► React + Nginx (x2)    │
                         │  /api   ──► backend  Service ──► FastAPI       (x2-6, HPA)
                         └───────────────────────────────────────────┬──────────┘
                                                                     ▼
                                                     PostgreSQL StatefulSet + EBS gp3 volume
 Prometheus ◄── ServiceMonitor scrapes backend /metrics ──► Grafana "ClinicFlow API" dashboard
```

| Layer | Technology |
|---|---|
| Frontend | React 19 + Vite, served by unprivileged Nginx |
| Backend | FastAPI, SQLAlchemy 2, Pydantic |
| Database | PostgreSQL 16, schema managed by Alembic migrations |
| Tests / quality | pytest (in-memory SQLite), ruff |
| Containers | Multi-stage Dockerfiles, non-root users, Docker Compose |
| CI/CD | GitHub Actions → GHCR, images tagged with the Git SHA |
| Security | Trivy image scan (HIGH/CRITICAL gate), no secrets in Git |
| Infrastructure | Terraform: AWS VPC + EKS + EBS CSI driver |
| Deployment | Helm chart: Deployments, Services, Ingress, HPA, StatefulSet |
| Observability | kube-prometheus-stack (Prometheus + Grafana), custom business metrics |

## Repository layout

```text
.
├── backend/                 FastAPI service
│   ├── app/                 main.py, models, schemas, routers/, metrics.py, db/config
│   ├── alembic/versions/    0001 tables, 0002 seed doctors
│   ├── tests/               conftest.py (isolated SQLite) + test_api.py
│   ├── Dockerfile           multi-stage, runs as uid 10001
│   └── pytest.ini, ruff.toml, requirements*.txt
├── frontend/                React app (src/App.jsx, components/, api.js, styles.css)
│   ├── Dockerfile           Node build stage → nginx-unprivileged runtime (uid 101)
│   └── nginx.conf.template  SPA routing + /api proxy (target set by BACKEND_URL)
├── docker-compose.yml       postgres + backend + frontend, one command
├── .github/workflows/       ci-cd.yml
├── terraform/               VPC + EKS (+ terraform.tfvars.example)
├── k8s/                     namespaces, gp3 StorageClass
├── helm/clinicflow/         the Helm chart (+ dashboards/clinicflow.json)
├── monitoring/              kube-prometheus-stack values
├── troubleshooting/         deliberately broken manifests for the debugging lab
└── scripts/load-test.sh     traffic generator for Grafana / HPA demos
```

---

## The application

### Domain model

```text
doctors (id, name, specialty, room, created_at)
   1 ──── * appointments (id, patient_name, patient_phone, doctor_id → doctors.id,
                          scheduled_at, duration_minutes, reason, status, created_at)
```

Appointment status workflow (other transitions return **409 Conflict**):

```text
SCHEDULED ──► CHECKED_IN ──► COMPLETED
    │              │
    └──────────────┴──► CANCELLED
```

Booking rules:
- a doctor cannot have two overlapping, non-cancelled appointments (**409**)
- back-to-back slots are fine; a cancelled slot can be re-booked
- all times are stored in UTC; the UI shows local time

### REST API

Interactive docs: `http://localhost:8000/docs` (Swagger UI).

| Method | Path | Purpose |
|---|---|---|
| GET | `/health` | Liveness: process is up |
| GET | `/ready` | Readiness: database reachable |
| GET | `/metrics` | Prometheus metrics |
| GET | `/api/doctors` | List doctors |
| POST | `/api/doctors` | Add a doctor |
| DELETE | `/api/doctors/{id}` | Remove a doctor (and their appointments) |
| GET | `/api/appointments?status=&doctor_id=&on=YYYY-MM-DD` | List / filter appointments |
| GET | `/api/appointments/stats` | Dashboard counters |
| GET | `/api/appointments/{id}` | One appointment |
| POST | `/api/appointments` | Book an appointment |
| PUT | `/api/appointments/{id}` | Reschedule, edit or change status |
| DELETE | `/api/appointments/{id}` | Delete an appointment |

Example:

```bash
curl -X POST http://localhost:8000/api/appointments \
  -H 'Content-Type: application/json' \
  -d '{"patient_name":"Asha Verma","doctor_id":2,"scheduled_at":"2030-01-15T10:00:00Z","reason":"ECG follow-up"}'
```

### Metrics

Besides the standard `http_requests_total` and `http_request_duration_seconds` from `prometheus-fastapi-instrumentator`, the API exports business metrics:

- `clinicflow_appointments_booked_total{specialty}`
- `clinicflow_appointment_status_changes_total{status}`

---

## Run it locally

### Option A: Docker Compose (whole stack, one command)

```bash
docker compose up --build
```

| URL | What |
|---|---|
| http://localhost:3000 | ClinicFlow UI |
| http://localhost:8000/docs | API docs |
| http://localhost:8000/metrics | Prometheus metrics |

Stop with `docker compose down` (add `-v` to wipe the database).

### Option B: Run the services directly

```bash
# backend (Python 3.12)
cd backend
python -m venv .venv
source .venv/bin/activate            # Windows: .venv\Scripts\activate
pip install -r requirements-dev.txt
cp .env.example .env                 # points at a local PostgreSQL
alembic upgrade head
uvicorn app.main:app --reload --port 8000

# frontend (Node 22), in a second terminal; proxies /api to :8000
cd frontend
npm ci
npm run dev                          # http://localhost:5173
```

## Tests and code quality

```bash
cd backend
ruff check . && ruff format --check .
pytest -v
```

`tests/conftest.py` gives every test a **fresh in-memory SQLite database** through FastAPI dependency overrides, so tests never touch PostgreSQL. The 19 tests cover the health, readiness and metrics endpoints, doctor CRUD and validation, appointment CRUD and filters, double-booking, the status workflow and the stats endpoint.

## Docker

| Image | Build | Runtime user |
|---|---|---|
| backend | `python:3.12-slim` build stage creates a venv → slim runtime copies only the venv and the code; runs `alembic upgrade head` then Uvicorn | `appuser` (uid 10001) |
| frontend | `node:22-alpine` runs `npm ci && npm run build` → `nginxinc/nginx-unprivileged` serves `dist/` on port 8080 | `nginx` (uid 101) |

Alembic takes a PostgreSQL advisory lock, so several backend replicas can start at once without racing on migrations.

## CI/CD pipeline (`.github/workflows/ci-cd.yml`)

Runs on every push and pull request to `main`:

1. **backend-test**: ruff lint and format check, then `pytest` with coverage. Any failure stops the pipeline.
2. **frontend-build**: `npm ci && npm run build`.
3. **iac-validate**: `helm lint` and `helm template`, plus `terraform fmt -check` and `terraform validate`.
4. **build-scan-push** (matrix: backend, frontend): build the image tagged `ghcr.io/<owner>/clinicflow-<component>:<git-sha>`, **scan it with Trivy** (fails on fixable HIGH/CRITICAL CVEs), then push to GHCR. PRs build and scan but never push.
5. **deploy** (push to `main`, when the repo variable `DEPLOY_ENABLED=true`): `aws eks update-kubeconfig`, then `helm upgrade --install` with the new SHA tags and `--wait`.

Images are never tagged `latest`, so every running pod can be traced back to the exact commit.

## Security (DevSecOps)

- **Trivy** scans both images for OS and library CVEs; HIGH or CRITICAL findings that have a fix fail the build.
- The Trivy action is **pinned to a commit SHA** (v0.35.0). In March 2026 most `aquasecurity/trivy-action` tags were hijacked (CVE-2026-33634), which is why third-party actions should be pinned by SHA rather than tag.
- Containers run as non-root, with `allowPrivilegeEscalation: false` and all Linux capabilities dropped in Kubernetes.
- No credentials in Git: `.env`, `*.tfvars`, state and kubeconfigs are git-ignored. AWS keys and the database password live in GitHub Secrets, and DB credentials are a Kubernetes Secret.

## Infrastructure as Code (`terraform/`)

Creates in `ap-south-1` (configurable):

- VPC `10.30.0.0/16` with **2 public subnets** (tagged for load balancers) and **2 private subnets** across 2 AZs, plus one NAT gateway
- **EKS** cluster `clinicflow-dev-eks` with an AL2023 **managed node group** (2× t3.medium)
- EKS add-ons: CoreDNS, kube-proxy, VPC CNI, and the **EBS CSI driver** (with an IRSA role) so PostgreSQL gets a real disk

```bash
cd terraform
cp terraform.tfvars.example terraform.tfvars
terraform init && terraform plan && terraform apply
aws eks update-kubeconfig --region ap-south-1 --name clinicflow-dev-eks
terraform destroy      # when finished. EKS + NAT cost money every hour
```

## Kubernetes and Helm (`helm/clinicflow/`)

| Resource | Details |
|---|---|
| `clinicflow-backend` Deployment | 2+ replicas (HPA 2-6 on 60% CPU), startup, readiness and liveness probes |
| `clinicflow-frontend` Deployment | 2 replicas |
| `clinicflow-postgres` StatefulSet | 5 Gi PVC (gp3 on EKS), credentials from a Secret |
| ClusterIP Services | backend :8000, frontend :80, postgres :5432 |
| Ingress (`nginx`) | `/api` → backend, `/` → frontend |
| HPA | backend CPU autoscaling (needs metrics-server) |
| ServiceMonitor | created automatically when the Prometheus Operator CRDs exist |
| ConfigMap | Grafana dashboard JSON (label `grafana_dashboard: "1"`) |

```bash
kubectl apply -f k8s/namespace.yaml
helm upgrade --install clinicflow ./helm/clinicflow -n clinicflow \
  -f helm/clinicflow/values-prod.yaml \
  --set backend.image.repository=ghcr.io/<owner>/clinicflow-backend \
  --set frontend.image.repository=ghcr.io/<owner>/clinicflow-frontend \
  --set backend.image.tag=<git-sha> --set frontend.image.tag=<git-sha> \
  --set postgres.password=<db-password>
kubectl get pods,svc,ingress,hpa -n clinicflow
```

`values-dev.yaml` targets a local cluster (1 replica, host `clinicflow.local`, no HPA). `values-prod.yaml` targets EKS.

## Observability

```bash
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm upgrade --install kube-prometheus-stack prometheus-community/kube-prometheus-stack \
  -n monitoring --create-namespace -f monitoring/prometheus-values.yaml \
  --set grafana.adminPassword=<password>
kubectl port-forward -n monitoring svc/kube-prometheus-stack-prometheus 9090   # Targets page
kubectl port-forward -n monitoring svc/kube-prometheus-stack-grafana 3001:80   # Grafana
```

The **ClinicFlow API** dashboard has 8 panels: pods up, request count, bookings in the last 24h, 5xx error ratio, request rate per endpoint, p50/p95 latency, responses by status class, and bookings and status changes. Use `scripts/load-test.sh` to put traffic on them.

## Troubleshooting lab

| Manifest | Symptom | How to diagnose |
|---|---|---|
| `troubleshooting/broken-image.yaml` | `ImagePullBackOff` | `kubectl describe pod`; events show the missing tag |
| `troubleshooting/broken-service.yaml` | Service has no endpoints | `kubectl get endpoints` vs `kubectl get pods --show-labels`; the selector has a typo |

## Grading rubric map

| Module | Where |
|---|---|
| M1 App | `backend/app`, `backend/alembic/versions`, `frontend/`, `docker-compose.yml` |
| M2 Tests | `backend/tests`, `backend/pytest.ini`, 19 tests on isolated SQLite |
| M3 Git | commit history, `.gitignore` |
| M4 Docker | `backend/Dockerfile`, `frontend/Dockerfile` (multi-stage, non-root), compose |
| M5 CI/CD | `.github/workflows/ci-cd.yml` (SHA tags, GHCR) |
| M6 Trivy | `build-scan-push` job; see YOUR-STEPS.md for the written explanation |
| M7 Terraform | `terraform/` (+ `terraform.tfvars.example`) |
| M8 K8s/Helm | `k8s/`, `helm/clinicflow/` |
| M9 Observability | `/metrics`, ServiceMonitor, `monitoring/`, Grafana dashboard |
| M10 Docs/Demo | this README, demo script in YOUR-STEPS.md |
