# YOUR STEPS: everything you need to do yourself

The code is finished and committed. Most of what's left needs **your** accounts (GitHub, AWS) or tools that aren't installed on this PC yet (Docker, Terraform, kubectl, Helm, AWS CLI). Work through the sections in order. 📸 marks each screenshot the rubric asks for; save them all in one folder.

**Shell:** use **Git Bash** for every command below (it comes with Git for Windows). Run them from the project folder:

```bash
cd "/c/Users/Tushar Srivastava/Desktop/Devops/Project/clinicflow-capstone"
```

## Screenshot guide (status on 17 Oct 2026)

All screenshots live in [`screenshots/`](screenshots/). File names start with the rubric module.

**Repo:** <https://github.com/Stonetenth2005/Devops-Capstone> · **Green pipeline run:** <https://github.com/Stonetenth2005/Devops-Capstone/actions/runs/38943202171>

### ✅ Already taken (25)

| Module | File | Shows |
|---|---|---|
| M1/M4 | `m1-m4-app-localhost-3000.png` | App at `localhost:3000` with booked / checked-in / completed / cancelled visits |
| M1 | `m1-double-booking-rejected.png` | "Doctor already has an appointment" (409) in the booking form |
| M1 | `m1-swagger-api-docs.png` | Swagger UI with GET/POST/PUT/DELETE endpoints |
| M2 | `m2-pytest-19-passed.png` | `pytest -v`: 19 passed |
| M2 | `m2-ruff-code-quality.png` | `ruff check` + `ruff format --check` clean |
| M3 | `m3-git-commit-history.png` | `git log --oneline` |
| M3 | `m3-github-commits-page.png` | GitHub *Commits* page |
| M3 | `m3-github-repo-public.png` | Public repo, 1 contributor |
| M4 | `m4-docker-compose-up-build.png` | `docker compose up --build`, 3 containers healthy |
| M5 | `m5-actions-green-run.png` | Run #3: every job green, deploy skipped (EKS not up yet) |
| M5 | `m5-actions-runs-list.png` | Runs list: #1/#2 failed on Trivy, #3 green after the fix |
| M5 | `m5-ghcr-backend-sha-tag.png`, `m5-ghcr-frontend-sha-tag.png` | GHCR packages, **Public**, tag = commit SHA |
| M6 | `m6-trivy-backend-findings-before-fix.png` | Trivy finding 4 HIGH CVEs (the gate failing) |
| M6 | `m6-trivy-backend-clean-after-fix.png`, `m6-trivy-frontend-clean.png` | Both images clean after the fix |
| M7 | `m7-terraform-plan.png`, `m7-terraform-plan-resources.png` | `terraform plan`: 61 to add (VPC + EKS) |
| M7 | `m7-terraform-validate.png` | `fmt` + `validate` |
| M8 | `m8-kubectl-get-pods.png`, `m8-kubectl-get-svc.png`, `m8-helm-list.png`, `m8-deployments-and-image-sha.png`, `m8-app-via-ingress.png` | Helm deploy on a **local kind cluster**: 2+2 replicas Running, ClusterIP services, Ingress, HPA, SHA image tag |
| M9 | `m9-metrics-endpoint-local.png`, `m9-metrics-endpoint-browser.png`, `m9-metrics-endpoint-cluster.png` | `/metrics` output |
| M9 | `m9-prometheus-targets-up.png` | ServiceMonitor target **2/2 UP** |
| M9 | `m9-grafana-dashboard.png` | "ClinicFlow API" dashboard, all panels populated |
| M9 | `m9-monitoring-pods.png` | Prometheus/Grafana pods Running |

The M8/M9 shots come from a local **kind** cluster (Kubernetes in Docker) running the same Helm chart and kube-prometheus-stack. They are valid evidence, but the rubric's M7 asks for EKS, so retake the M8/M9 ones on EKS if you have time (same commands, steps 7-8).

### ❌ Still to take (need EKS: `terraform apply` costs money, so it was not run for you)

| # | File name to save as | How |
|---|---|---|
| 1 | `m7-terraform-apply.png` | `cd terraform && terraform apply tfplan` (~15-20 min). Screenshot the end: *Apply complete! Resources: 61 added*. If `tfplan` is stale, run `terraform plan -out tfplan` first. |
| 2 | `m7-aws-console-vpc.png` | AWS Console → region **Asia Pacific (Mumbai) ap-south-1** → **VPC → Your VPCs**: `clinicflow-dev-vpc`. Then **Subnets** (filter by that VPC): 2 public + 2 private. |
| 3 | `m7-aws-console-eks.png` | AWS Console → **EKS → Clusters → clinicflow-dev-eks**: status *Active*; open the **Compute** tab to show the node group with 2 nodes. |
| 4 | `m8-eks-get-pods.png`, `m8-eks-get-svc.png`, `m8-eks-helm-list.png` | After steps 6-7: `kubectl get pods -n clinicflow`, `kubectl get svc -n clinicflow`, `helm list -n clinicflow` |
| 5 | `m8-eks-app-via-loadbalancer.png` | Open `http://<load-balancer-hostname>` (step 7 prints it); screenshot with the address bar visible |
| 6 | `m5-actions-deploy-green.png` | After `gh variable set DEPLOY_ENABLED --body true` + secrets (step 7), re-run the pipeline; screenshot the run with *Deploy to EKS with Helm* green |
| 7 | `m6-trivy-step-in-pipeline.png` | Signed in to GitHub: Actions → run #3 → *Build, scan & push (backend)* → expand **Trivy scan**. (Logs are hidden when signed out, so this could not be captured.) |
| 8 | `m9-eks-prometheus-targets.png`, `m9-eks-grafana.png` | Step 8 port-forwards on EKS |
| 9 | `m7-terraform-destroy.png` | Step 10: `terraform destroy` → *Destroy complete!* **Do this the same day.** |

**How to take a screenshot on Windows:** `Win + Shift + S` → drag a box → it is copied; paste into Paint and save as PNG in `screenshots/`. For a terminal, make the window big enough to show the command and the final lines of output.

Also needed before EKS deploy: `gh auth login` in your own terminal (it is not signed in yet), then the `gh secret set` / `gh variable set` commands in step 7.

### Time plan (about 3 hours)

| Step | What | Time |
|---|---|---|
| 1 | Install tools | 20 min |
| 2 | Sign in / create AWS credentials | 15 min |
| 3 | Run locally + screenshots | 15 min |
| 4 | Push to GitHub, first pipeline | 15 min |
| 5 | `terraform apply` (start it early: it runs ~20 min while you do other things) | 25 min |
| 6 | Cluster add-ons (ingress, metrics, monitoring) | 15 min |
| 7 | Deploy through the pipeline + screenshots | 20 min |
| 8 | Grafana / Prometheus screenshots | 15 min |
| 9 | Rehearse live demo | 15 min |
| 10 | `terraform destroy` (after grading!) | 15 min |

> **Tip:** start step 5 (`terraform apply`) as soon as AWS credentials work, and do steps 3-4 while EKS is being created.

---

## 1. Install the tools (Windows)

Open **PowerShell as Administrator** and run:

```powershell
winget install -e --id Docker.DockerDesktop
winget install -e --id GitHub.cli
winget install -e --id Amazon.AWSCLI
winget install -e --id Hashicorp.Terraform
winget install -e --id Kubernetes.kubectl
winget install -e --id Helm.Helm
```

Already installed on this PC: Git 2.47, Python 3.12, Node 22.

Then:
1. **Restart Windows** (Docker Desktop needs it for WSL 2).
2. Start **Docker Desktop** and wait until it says *Engine running*. Accept its terms yourself if prompted.
3. Open a **new** Git Bash and check everything is on the PATH:

```bash
docker --version && docker compose version
gh --version && aws --version && terraform version
kubectl version --client && helm version
```

If one says "command not found", close and reopen Git Bash (the PATH refreshes only in new windows).

---

## 2. Accounts and sign-in

### 2a. GitHub

```bash
gh auth login
#  → GitHub.com → HTTPS → "Login with a web browser" → paste the one-time code
gh auth status
```

**Commit author:** this PC's git is configured as `Stonetenth2005 <srivastavatushar2005@gmail.com>`, and all commits so far use that identity. If the submission must be under a different GitHub account, set it **before pushing**:

```bash
git config user.name  "Your Name"
git config user.email "your-github-email@example.com"
```

(Earlier commits keep the old author. That's fine as long as the email belongs to your GitHub account.)

### 2b. AWS

1. Sign in to <https://console.aws.amazon.com> with your **root** account (or the account your course gave you).
2. **Billing alarm (recommended):** Billing → Budgets → Create budget → "Zero spend" or a monthly budget of $10 → your email.
3. Create a user for the CLI: **IAM → Users → Create user**
   - name: `clinicflow-admin`
   - Permissions: *Attach policies directly* → `AdministratorAccess` (simplest for a capstone; delete the user afterwards)
   - Open the user → **Security credentials → Create access key → Command Line Interface** → copy the **Access key ID** and **Secret access key**. They are shown only once. Never commit or paste them into any file in this repo.
4. Configure the CLI:

```bash
aws configure
#  AWS Access Key ID:     <paste>
#  AWS Secret Access Key: <paste>
#  Default region name:   ap-south-1
#  Default output format: json
aws sts get-caller-identity          # should print your account id and user/clinicflow-admin
```

5. Check that Kubernetes 1.34 is offered in standard support:

```bash
aws eks describe-cluster-versions --region ap-south-1 \
  --query "clusterVersions[?versionStatus=='STANDARD_SUPPORT'].clusterVersion" --output text
```

   If `1.34` is not in the list, put a listed version in `terraform/terraform.tfvars` (`kubernetes_version = "1.35"`).

---

## 3. Run it locally (M1, M2, M4 screenshots)

```bash
docker compose up --build
```

Wait for `clinicflow-frontend` and `clinicflow-backend` to be *healthy* (about 1-2 minutes the first time).

- 📸 **Terminal** showing `docker compose up --build` with all three services running
- Open <http://localhost:3000>, click **Book appointment**, book 2-3 visits, check one in, complete it
- 📸 **Browser** at `localhost:3000` with data (this covers both M1 and M4)
- Try booking the same doctor at the same time again to show the red *"Doctor already has an appointment"* message (nice in the demo)
- Open <http://localhost:8000/docs> (Swagger) for the API demo

Stop it with `Ctrl+C`, then `docker compose down`.

Tests:

```bash
cd backend
python -m venv .venv && source .venv/Scripts/activate
pip install -r requirements-dev.txt
pytest -v
cd ..
```

- 📸 **pytest -v** output showing **19 passed**

---

## 4. Push to GitHub (M3, M5, M6)

```bash
gh repo create clinicflow-capstone --public --source . --remote origin --push
```

This creates a **public** repo and pushes `main`. The pipeline starts immediately:

```bash
gh run watch            # or open the repo → Actions tab
```

On the first run, **backend-test, frontend-build, iac-validate and build-scan-push should pass**. **deploy is skipped** until step 7, which is expected.

After the first green run:
1. Make sure the images are public so the cluster can pull them without a password: GitHub → your profile → **Packages** → `clinicflow-backend` → **Package settings** → *Change visibility* → **Public**. Repeat for `clinicflow-frontend`. (On this repo they were already public, inherited from the public repository.)
2. 📸 **GHCR package page** showing the tag that equals the commit SHA
3. 📸 **Commit history** (repo → *Commits*; there are 15+ meaningful commits)
4. 📸 **Trivy step output**: Actions → the run → *Build, scan & push (backend)* → expand *Trivy scan*

**If Trivy fails the build:** the log names the package and CVE. For OS packages, rebuilding usually picks up the fix (the Dockerfiles run `apt-get upgrade` / `apk upgrade`). For Python or npm packages, bump the version in `requirements.txt` / `package.json`, run `npm install` to refresh the lock file, then commit and push.

### Written explanation for M6 (our actual result)

> Trivy scanned both images built in the pipeline: the Debian OS packages of `python:3.12-slim`, the Alpine packages of `nginx-unprivileged`, and every Python package in the backend image. The first two pipeline runs **failed the gate**: Trivy found 4 fixable HIGH CVEs in the backend, e.g. **CVE-2026-97687 in urllib3 2.7.0** (an HTTPS-proxy TLS setting can be overridden, allowing traffic interception; fixed in 2.8.0), plus another urllib3 DoS, a msgpack out-of-bounds read and a setuptools path traversal. All four were not in our app's dependencies but in the copies **bundled inside pip** itself, so the fix was to uninstall pip from the runtime image (it is never needed at runtime). After that, both images scan clean (0 fixable HIGH/CRITICAL) and run #3 went green — the scan stopped a vulnerable image from reaching GHCR, which is exactly its job.

Generic version, if you ever need it:

> Trivy scanned both container images built in the pipeline: the OS packages of the Debian `python:3.12-slim` and Alpine `nginx-unprivileged` base images, plus the Python packages installed in the backend virtualenv and the npm packages bundled in the frontend. The pipeline fails if any HIGH or CRITICAL vulnerability with an available fix is found; unfixed CVEs are reported but don't block, because there is nothing to upgrade to yet. Our scan was clean (0 fixable HIGH/CRITICAL), which means no known serious vulnerability with a patch exists in the shipped images at build time. It doesn't mean the app is "secure" forever, since new CVEs are published daily, which is why the scan runs on every build.

If your scan *did* find something, explain that one CVE instead: the package, the severity, what it affects, and how you fixed it (version bump).

---

## 5. Create AWS infrastructure with Terraform (M7)

```bash
cd terraform
cp terraform.tfvars.example terraform.tfvars
terraform init
terraform plan -out tfplan
```

- 📸 **terraform plan** output (scroll to the end: *Plan: N to add, 0 to change, 0 to destroy*)

```bash
terraform apply tfplan            # ~15-20 minutes. Keep this window open
$(terraform output -raw configure_kubectl)
kubectl get nodes                 # 2 nodes, STATUS Ready
cd ..
```

- 📸 **AWS Console → VPC** (region *Mumbai ap-south-1*) showing `clinicflow-dev-vpc` and its subnets
- 📸 **AWS Console → EKS → Clusters** showing `clinicflow-dev-eks` *Active*, plus the *Compute* tab with the node group

---

## 6. Prepare the cluster (once)

```bash
# namespaces + gp3 disk class for PostgreSQL
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/storageclass-gp3.yaml

# metrics-server (needed by the HPA)
helm repo add metrics-server https://kubernetes-sigs.github.io/metrics-server/
helm upgrade --install metrics-server metrics-server/metrics-server -n kube-system

# ingress-nginx: creates an AWS load balancer for the Ingress
helm upgrade --install ingress-nginx ingress-nginx \
  --repo https://kubernetes.github.io/ingress-nginx \
  -n ingress-nginx --create-namespace \
  --set controller.service.type=LoadBalancer

# Prometheus + Grafana (install BEFORE the app so the ServiceMonitor gets created)
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update
helm upgrade --install kube-prometheus-stack prometheus-community/kube-prometheus-stack \
  -n monitoring --create-namespace -f monitoring/prometheus-values.yaml \
  --set grafana.adminPassword='Pick-A-Grafana-Password'

kubectl get pods -n monitoring        # wait until everything is Running
```

---

## 7. Deploy the app through the pipeline (M5 deploy, M8)

Pick a database password (letters and digits only is easiest) and **keep using the same one**: PostgreSQL only reads it the first time the disk is created.

```bash
gh secret set AWS_ACCESS_KEY_ID          # paste the same key as in `aws configure`
gh secret set AWS_SECRET_ACCESS_KEY      # paste the secret
gh secret set POSTGRES_PASSWORD          # paste your chosen DB password
gh variable set AWS_REGION --body ap-south-1
gh variable set EKS_CLUSTER_NAME --body clinicflow-dev-eks
gh variable set DEPLOY_ENABLED --body true

gh workflow run ci-cd.yml --ref main     # re-run the whole pipeline, now including deploy
gh run watch
```

The pipeline uses the same IAM user that created the cluster, so it already has admin access to EKS.

Check:

```bash
kubectl get pods -n clinicflow           # 📸 all Running (2 backend, 2 frontend, 1 postgres)
kubectl get svc -n clinicflow            # 📸 ClusterIP services
helm list -n clinicflow                  # 📸 release "clinicflow", STATUS deployed
kubectl get ingress,hpa -n clinicflow
kubectl get svc -n ingress-nginx ingress-nginx-controller \
  -o jsonpath='{.status.loadBalancer.ingress[0].hostname}'; echo
```

Open `http://<that-hostname>` in the browser. A new AWS load balancer can take 2-3 minutes to answer.
- 📸 **Browser** showing ClinicFlow through the load balancer / Ingress
- 📸 **GitHub Actions run URL** with every job green, including *Deploy to EKS with Helm*

---

## 8. Monitoring screenshots (M9)

```bash
# /metrics
kubectl port-forward -n clinicflow svc/clinicflow-backend 8000:8000 &
curl -s localhost:8000/metrics | grep -E "clinicflow_|http_requests_total" | head -20     # 📸
kill %1

# generate traffic so graphs have data
BASE_URL=http://<load-balancer-hostname> ./scripts/load-test.sh

# Prometheus targets
kubectl port-forward -n monitoring svc/kube-prometheus-stack-prometheus 9090 &
#  open http://localhost:9090/targets → find "serviceMonitor/clinicflow/clinicflow-backend" → State UP   📸

# Grafana
kubectl port-forward -n monitoring svc/kube-prometheus-stack-grafana 3001:80 &
#  open http://localhost:3001 → user "admin", password = the one you set in step 6
#  Dashboards → "ClinicFlow API" → panels populated                                                    📸
```

Stop the port-forwards with `kill %1 %2 %3` (or close the terminal).

---

## 9. Live demo script (M10, about 5 minutes)

1. **App**: open the load-balancer URL, book an appointment, check it in, show the double-booking error.
2. **Code change**: edit `frontend/src/App.jsx`, e.g. change `Clinic overview` to `Clinic overview, live demo`.
   ```bash
   git commit -am "feat(frontend): update dashboard heading for live demo"
   git push
   ```
3. **Pipeline**: show the Actions tab: tests → build → Trivy scan → push to GHCR → deploy.
4. **Rollout**: `kubectl get pods -n clinicflow -w` shows new pods replacing old ones; `kubectl describe deploy clinicflow-frontend -n clinicflow | grep Image` shows the new SHA tag.
5. **Result**: refresh the browser; the new heading is live.
6. **Observability**: Grafana dashboard request-rate panel moving; Prometheus target UP.
7. **Optional, troubleshooting**: `kubectl apply -f troubleshooting/broken-service.yaml`, then `kubectl get endpoints broken-service -n clinicflow` (empty), and explain the label typo.
8. **Optional, autoscaling**: `kubectl get hpa -n clinicflow -w` while `REQUESTS=3000 ./scripts/load-test.sh` runs.

Talking points: why tests come before the image build, why SHA tags instead of `latest`, why images run as non-root, what the Ingress controller does vs the Ingress resource, readiness vs liveness, and why Terraform instead of console clicks.

---

## 10. Tear down (do this right after grading)

Order matters: delete what Kubernetes created in AWS **before** Terraform deletes the VPC.

```bash
helm uninstall clinicflow -n clinicflow
kubectl delete pvc --all -n clinicflow           # removes the EBS disk
helm uninstall ingress-nginx -n ingress-nginx    # removes the AWS load balancer
helm uninstall kube-prometheus-stack -n monitoring
# wait ~2 minutes for the load balancer to disappear (EC2 → Load Balancers)

gh variable set DEPLOY_ENABLED --body false      # stop the pipeline from deploying to a dead cluster

cd terraform
terraform destroy                                # type "yes"; ~10-15 min
```

- 📸 **terraform destroy** output ending in *Destroy complete!*

Afterwards: in IAM, **delete the `clinicflow-admin` access key/user**, and delete the `AWS_*` GitHub secrets (`gh secret delete AWS_ACCESS_KEY_ID`, and the same for `AWS_SECRET_ACCESS_KEY`).

If `destroy` hangs on the VPC or subnets: a load balancer or network interface is still there. Delete it in the EC2 console (Load Balancers, then Network Interfaces), then run `terraform destroy` again.

---

## Submission checklist

| Rubric | Evidence | Done |
|---|---|---|
| M1 | Browser screenshot of the app; repo files | ☑ |
| M2 | `pytest -v` screenshot (19 passed) | ☑ |
| M3 | Public repo URL; commit-history screenshot (≥10 commits) | ☑ |
| M4 | `docker compose up --build` terminal + `localhost:3000` browser screenshots | ☑ |
| M5 | Green Actions run URL; GHCR page with SHA tags | ☑ (deploy-green run still needs EKS) |
| M6 | Trivy step screenshot + the 2-3 sentence explanation above | ☑ local scans + explanation; ☐ pipeline-log shot (sign in) |
| M7 | `terraform plan`, AWS console VPC + EKS, `terraform destroy` screenshots | plan ☑; apply / console / destroy ☐ |
| M8 | `kubectl get pods`, `kubectl get svc`, `helm list` screenshots; app via Ingress | ☑ on kind; ☐ on EKS |
| M9 | `/metrics` curl, Prometheus Targets UP, Grafana dashboard screenshots | ☑ on kind; ☐ on EKS |
| M10 | README.md; live demo (section 9) | ☐ |

---

## Common problems

| Symptom | Fix |
|---|---|
| `docker: command not found` | Docker Desktop not running, or reopen Git Bash after install |
| `terraform init`: *Filename too long* | Windows path limit: run `git config --global core.longpaths true`, then `terraform init` again |
| Port 5432/8000/3000 already in use | Stop the other program, or change the left-hand port in `docker-compose.yml` |
| Pods `ImagePullBackOff` | GHCR packages still private: make them public (step 4) |
| Postgres pod `Pending` | `kubectl apply -f k8s/storageclass-gp3.yaml`; check `kubectl get pvc -n clinicflow` |
| Backend `CrashLoopBackOff`, logs say *password authentication failed* | `POSTGRES_PASSWORD` changed after the first deploy. Use the original one, or `helm uninstall clinicflow -n clinicflow && kubectl delete pvc --all -n clinicflow` and deploy again |
| Deploy job: *You must be logged in to the server (Unauthorized)* | GitHub secrets must belong to the same IAM user that ran `terraform apply` |
| Load-balancer URL doesn't load | Wait 2-3 min; `kubectl get svc -n ingress-nginx` must show an EXTERNAL-IP/hostname |
| Prometheus target missing | Monitoring was installed after the app: re-run the pipeline (or `helm upgrade` the app) so the ServiceMonitor is created |
| `kubectl get hpa` shows `<unknown>` CPU | metrics-server not installed or still starting (step 6) |
| ingress-nginx | The upstream project stopped active maintenance in 2026, but the chart still installs and works for this capstone; mention Gateway API / AWS Load Balancer Controller as the long-term replacement if asked |
