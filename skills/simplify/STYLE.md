# Style standards

These apply when the repo has no standard of its own. If it does (in `pyproject.toml`, `.tflint.hcl`, `CODING_STANDARDS.md` and so on), follow the repo.

## Python (PEP 8, ruff-era)

- **Formatting:** let `ruff format` own it. That means 4-space indents and an **88**-character line, the ruff/black default. PEP 8's 79 only applies if the repo pins it.
- **Imports:** at the top, grouped stdlib, then third-party, then local, sorted (`ruff` rule `I`). Prefer absolute imports.
- **Naming:**
  - `snake_case` for functions, variables and modules
  - `PascalCase` for classes
  - `UPPER_SNAKE_CASE` for constants
  - a single leading `_` for private names
  - names that reveal intent; single letters only for short loop counters
- **Type hints** on every public function signature. Use `X | None` (3.10+), not `Optional[X]`.
- **Docstrings** on public modules, classes and functions, Google style. They say what and why, not how.
- **Idioms:**
  - f-strings
  - `with` for any resource
  - `pathlib` over `os.path`
  - comprehensions only while they stay readable
  - `dataclasses` or `pydantic` models over loose dicts at boundaries
  - `enumerate`/`zip` over index juggling
- **Errors:** catch specific exceptions, never a bare `except:`. Don't swallow errors silently. Raise with a message that says what to do about it.

## Terraform (HashiCorp style guide)

- **Files:** `versions.tf` (`required_version`, `required_providers`), `providers.tf`, `variables.tf`, `locals.tf`, `data.tf`, `main.tf` (split by domain when large, e.g. `network.tf`), `outputs.tf`.
- **Formatting:** `terraform fmt` owns it: 2 spaces, aligned `=`.
- **Argument order:** meta-arguments first (`count`/`for_each`, `provider`), then required arguments, then optional ones, then nested blocks, then `lifecycle`/`depends_on` last.
- **Naming:** `snake_case` everywhere. Don't repeat the resource type in the name (`aws_s3_bucket.logs`, not `aws_s3_bucket.logs_bucket`).
- **Variables:** every variable has a `type` and a `description`. Use `validation` blocks for edge checks. Mark secrets `sensitive = true`.
- **Values:** no hardcoded values. Use variables for inputs and locals for derived values. Apply tags through provider `default_tags` where possible.
- **Repetition:** use `for_each` (stable keys) over `count` for collections. Use `moved` blocks for renames, never destroy and recreate.
- **Versions:** pin provider versions with `~>`, and commit `.terraform.lock.hcl`.

## Bash (ysap.sh style)

- **Header:** start with `#!/usr/bin/env bash`, followed by a comment block with the purpose and usage.
- **Error handling:** avoid relying on `set -e`, which has many surprising edge cases (ysap's advice). Check errors explicitly: `cmd || die "msg"`. `set -u` and `set -o pipefail` are fine if the repo uses them.
- **Formatting:** 2-space indents (`shfmt -i 2`). `then`/`do` go on the same line as `if`/`for`/`while`.
- **Naming:** `UPPER_SNAKE_CASE` for constants and exported variables (mark constants `readonly`). `lower_snake_case` for locals and functions, with `local` inside functions.
- **Quoting and tests:** always quote expansions (`"$var"`, `"${arr[@]}"`). Use `[[ … ]]` for tests and `$(…)`, never backticks.
- **Structure:** define functions before use. Use a `main "$@"` entry point. Use meaningful exit codes, and send errors to stderr.
- **Linting:** clean under `shellcheck`.

## Docker Compose (Compose Specification)

- **No top-level `version:` key.** It's obsolete; Compose ignores it and warns.
- **Images:** pin image tags, and digests for production. Never `latest`.
- **Key order per service:** `image`/`build`, `container_name`, `restart`, `environment`/`env_file`, `volumes`, `ports`, `networks`, `depends_on`, `healthcheck`, `deploy`.
- **Dependencies:** `depends_on` with `condition: service_healthy`, paired with a real `healthcheck`.
- **Volumes and networks:** named volumes for persistent data, and explicit networks. Only publish the ports something outside actually needs.
- **Secrets:** go in `env_file`s that are gitignored, with a committed `.env.example`. Use Compose `secrets:` where supported.
- **Repetition:** use YAML anchors (`x-common: &common`) for repeated config, and comments for anything non-obvious.

## Dockerfile

- **Base images:** pinned to a specific tag, small (`-slim`, distroless).
- **Builds:** multi-stage, with the build tools kept out of the final image.
- **User:** run as a non-root `USER`.
- **Layer order:** put the layers that change least first, so the cache works (dependencies before source).
- **Hygiene:** a `.dockerignore`, no secrets in layers, and a `HEALTHCHECK` where the platform uses it.
- **Linting:** clean under `hadolint`.
