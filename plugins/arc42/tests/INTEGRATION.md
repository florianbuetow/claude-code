# Integration Smoke Run (manual acceptance test)

Status: **PENDING — requires a live Claude Code session**

This document describes the manual steps to run the full `/arc42:generate` flow
against the test fixtures and then validate the output with `validate_output.py`.

## Prerequisites

- Claude Code CLI installed and authenticated
- Plugin loaded from this repository (`--plugin-dir ./plugins/arc42`)
- A temporary git repository (required so `source_commit` resolves)

## Steps

### 1. Set up a temporary git repo from `sample-repo`

```bash
TMPDIR=$(mktemp -d)
cp -r plugins/arc42/tests/fixtures/sample-repo/. "$TMPDIR/"
git -C "$TMPDIR" init
git -C "$TMPDIR" add .
git -C "$TMPDIR" commit -m "initial"
echo "Temp repo: $TMPDIR"
```

### 2. Run arc42 generation

```bash
cd "$TMPDIR"
claude --plugin-dir /path/to/plugins/arc42
```

Then inside the Claude Code session:

```
/arc42:generate
```

Wait for the command to complete. It should produce a `docs/arc42/` tree.

### 3. Validate the output

```bash
/usr/bin/python3 /path/to/plugins/arc42/tests/validate_output.py "$TMPDIR/docs/arc42"
```

Expected: `Output OK` (exit 0)

### 4. Repeat against `infra-only-repo`

```bash
TMPDIR2=$(mktemp -d)
cp -r plugins/arc42/tests/fixtures/infra-only-repo/. "$TMPDIR2/"
git -C "$TMPDIR2" init
git -C "$TMPDIR2" add .
git -C "$TMPDIR2" commit -m "initial"

cd "$TMPDIR2"
claude --plugin-dir /path/to/plugins/arc42
# Inside session: /arc42:generate
```

Then validate:

```bash
/usr/bin/python3 /path/to/plugins/arc42/tests/validate_output.py "$TMPDIR2/docs/arc42"
```

Expected: `Output OK` (exit 0). The IaC-only repo has no build manifest, so
code-only sections (e.g. §5 Building Block View) should emit `gap-no-evidence`
provenance rather than aborting, while §7 Deployment View should populate from
`main.tf` and `k8s/deployment.yaml`.

## Acceptance criteria

- [ ] `sample-repo` → `Output OK`, all 12 sections present, stakeholders section
      has `<!-- GAP:human-input … -->` and no invented rows.
- [ ] `infra-only-repo` → `Output OK`, §7 populated from IaC files,
      code-only sections have `provenance:gap-no-evidence`, no fabrication flags.
