# Checks by stack

Use the rows that match the project. If a stack isn't listed, find its equivalent of these: a static check, a deploy step, an interface test and a teardown.

| Stack | Static check | Deploy / run | Test the interfaces | Teardown + verify |
|---|---|---|---|---|
| Python app/API | `ruff check .`, `mypy .` | `uv run …` / `docker compose up -d` | `pytest`, `curl` each route | stop process / `docker compose down` |
| Docker Compose | `docker compose config -q`, `hadolint Dockerfile` | `docker compose up -d --wait` | `curl`, `docker compose exec`, health status | `docker compose down` (add `-v` only if data is disposable) |
| Terraform / OpenTofu | `terraform fmt -check`, `terraform validate`, `tflint` | `terraform plan -out tfplan` → `terraform apply tfplan` | cloud CLI (`aws …`), `curl` | `terraform destroy`, then `terraform state list` is empty |
| Kubernetes | `kubectl apply --dry-run=server -f …`, `kubeconform` | `kubectl apply -f …` | `kubectl rollout status`, `kubectl port-forward` + `curl` | `kubectl delete -f …`, confirm nothing left in namespace |
| Ansible | `ansible-lint`, `--syntax-check` | `ansible-playbook … --check --diff`, then for real | run twice: second run must report `changed=0` (idempotency) | playbook's `state: absent` path |
| Shell scripts | `shellcheck`, `bash -n` | run against a test target | run twice (idempotency) | — |
| ML pipeline | `ruff`, `mypy`, data schema validation | run on a small sample | metrics vs. baseline, output shape/dtype checks | remove temp artifacts, stop GPU instances |
| Proxmox / homelab | config diff / `qm config` | snapshot first, then change | `ssh` + `systemctl status`, `curl` | restore or delete snapshot when confirmed |
