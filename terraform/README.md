# Terraform: AWS VPC + EKS for ClinicFlow

| File | Contents |
|---|---|
| `versions.tf` | Terraform/AWS provider versions, provider with default tags |
| `variables.tf` | region, names, CIDR, Kubernetes version, node sizes |
| `main.tf` | VPC module, EKS module (managed node group + add-ons), EBS CSI IRSA role |
| `outputs.tf` | VPC/subnet IDs, cluster name/endpoint, the `aws eks update-kubeconfig` command |
| `terraform.tfvars.example` | copy to `terraform.tfvars` (git-ignored) |

```bash
cp terraform.tfvars.example terraform.tfvars
terraform init
terraform fmt -check && terraform validate
terraform plan -out tfplan
terraform apply tfplan                 # ~15-20 minutes
$(terraform output -raw configure_kubectl)
kubectl get nodes
terraform destroy                      # ~10-15 minutes. Do not forget it.
```

> **Cost:** EKS control plane + 2× t3.medium + NAT gateway + load balancer is roughly US$0.30/hour (about US$7/day). Always run `terraform destroy` after grading.
>
> **Before destroy:** run `helm uninstall` for ingress-nginx and clinicflow first, so the AWS load balancer and EBS volume Kubernetes created are removed. Otherwise the VPC can't be deleted.

Credentials come from `aws configure` or environment variables, never from files in this repo. State is local (`terraform.tfstate`, git-ignored); keep this folder until you have destroyed everything.
