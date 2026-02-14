---
name: config
description: >
  This skill should be used when the user asks to "configure security",
  "appsec settings", "security preferences", or invokes /appsec:config.
  Manages security tool preferences and thresholds.
---

# AppSec Config -- Preferences Management

Manage persistent security preferences stored in `.appsec/config.yaml`.
Settings control default behavior for all `/appsec:*` tools -- scope, depth,
severity filters, scanner paths, enabled hooks, accepted risks, and
excluded paths.

This skill runs entirely in the main agent context. It does NOT dispatch
subagents.

## Supported Operations

Detect the user's intent from their message:

| Intent | Action |
|--------|--------|
| "show config", "current settings" | Display current config |
| "set default scope to full" | Update a setting |
| "exclude vendor/ from scans" | Add to excluded paths |
| "accept risk INJ-003" | Add to accepted risks |
| "reset config" | Delete config file |
| "enable hooks" | Enable/disable hook settings |
| No specific intent | Show current config with explanations |

## Config Schema

The config file is `.appsec/config.yaml`. All fields are optional. When a
field is absent, the tool default applies.

```yaml
# .appsec/config.yaml
# AppSec plugin preferences

# Default scope when no --scope flag is provided
# Values: changed, staged, branch, full
# Default: changed
default_scope: changed

# Default depth when no --depth flag is provided
# Values: quick, standard, deep, expert
# Default: standard
default_depth: standard

# Minimum severity to report
# Values: critical, high, medium, low
# Default: low (report everything)
minimum_severity: low

# Scanner binary paths (override auto-detection)
# Use when scanners are not on PATH
scanner_paths:
  # semgrep: /usr/local/bin/semgrep
  # gitleaks: /opt/tools/gitleaks
  # trivy: /usr/local/bin/trivy

# Paths to exclude from all scans
# Glob patterns relative to repository root
excluded_paths:
  - "vendor/**"
  - "node_modules/**"
  - "dist/**"
  - "build/**"
  - "*.min.js"
  - "*.bundle.js"
  - "**/*.test.*"
  - "**/*.spec.*"

# Accepted risks (findings to suppress in future scans)
# Each entry: finding ID, reason, who accepted, when
accepted_risks: []
  # - id: INJ-003
  #   reason: "Input is validated upstream by API gateway"
  #   accepted_by: "developer"
  #   accepted_on: "2026-02-14"

# Hook configuration
hooks:
  # Review implementation plans for security on ExitPlanMode
  plan_review: true
  # Scan written/edited files for hardcoded secrets
  secret_detection: true

# Frameworks to include in full-audit
# Default: all
enabled_frameworks:
  - owasp
  - stride
  - pasta
  - linddun
  - sans25

# Red team personas to include in expert mode
# Default: all
enabled_personas:
  - script-kiddie
  - insider
  - organized-crime
  - hacktivist
  - nation-state
  - supply-chain
```

## Workflow

### Step 1: Load Current Config

Check if `.appsec/config.yaml` exists using Glob. If it exists, read it.
If not, use all defaults.

### Step 2: Parse User Intent

Determine what the user wants:

**Show config:**
Display the current config (or defaults if no file exists) with
explanations for each setting.

**Update a setting:**
1. Validate the new value against the allowed values for that field.
2. If the config file exists, read it and update the field.
3. If no config file exists, create one with the single changed field.
4. Write the file.
5. Confirm the change.

**Exclude a path:**
Add the path pattern to `excluded_paths`. Validate it is a valid glob
pattern. Warn if the pattern seems too broad (e.g., `**/*` would exclude
everything).

**Accept a risk:**
1. Verify the finding ID exists in `.appsec/findings.json`.
2. Ask the user for a reason if not provided.
3. Add to `accepted_risks` with timestamp.
4. Confirm the acceptance.

**Reset config:**
Delete `.appsec/config.yaml`. Confirm that all settings return to defaults.

**Enable/disable hooks:**
Toggle `hooks.plan_review` or `hooks.secret_detection`.

### Step 3: Output

#### Show Config (Text Format)

```
=====================================================
          APPSEC CONFIG -- Current Settings
=====================================================

DEFAULTS:
  Scope:    <value> (default: changed)
  Depth:    <value> (default: standard)
  Severity: <value> (default: low)

SCANNERS:
  semgrep:    <auto-detected / custom path>
  gitleaks:   <auto-detected / custom path>
  ...

EXCLUDED PATHS:
  - vendor/**
  - node_modules/**
  - ...

ACCEPTED RISKS: <N>
  - <ID>: <reason> (accepted <date>)
  - ...

HOOKS:
  Plan review:      <enabled/disabled>
  Secret detection: <enabled/disabled>

FRAMEWORKS: <list>
RED TEAM:   <list>

CONFIG FILE: .appsec/config.yaml <exists / not created>

=====================================================
  /appsec:config set <key> <value>    Change a setting
  /appsec:config exclude <path>       Add exclusion
  /appsec:config accept <ID>          Accept a risk
  /appsec:config reset                Reset to defaults
=====================================================
```

#### Update Confirmation

```
Updated .appsec/config.yaml:
  <key>: <old value> -> <new value>
```

## Validation Rules

| Field | Allowed Values | Error on Invalid |
|-------|---------------|------------------|
| `default_scope` | `changed`, `staged`, `branch`, `full` | Yes, show allowed values |
| `default_depth` | `quick`, `standard`, `deep`, `expert` | Yes, show allowed values |
| `minimum_severity` | `critical`, `high`, `medium`, `low` | Yes, show allowed values |
| `scanner_paths.*` | Absolute file path that exists | Warn if path does not exist |
| `excluded_paths` | Valid glob pattern | Warn if pattern is too broad |
| `accepted_risks.*.id` | Finding ID present in findings.json | Warn if ID not found |
| `hooks.*` | `true` or `false` | Yes |
| `enabled_frameworks` | `owasp`, `stride`, `pasta`, `linddun`, `sans25` | Yes |
| `enabled_personas` | `script-kiddie`, `insider`, `organized-crime`, `hacktivist`, `nation-state`, `supply-chain` | Yes |

## How Config Is Consumed

Other skills read `.appsec/config.yaml` at startup to apply defaults:

1. If the user provides a flag (e.g., `--scope full`), the flag wins.
2. If no flag is provided, the config value is used.
3. If no config value exists, the tool default applies.

Accepted risks are filtered out during consolidation in `/appsec:run` and
`/appsec:full-audit`. The finding is still detected but marked as
`"accepted": true` and excluded from severity counts unless `--severity low`
is explicitly set.
