# Findings Schema

All appsec skills output findings in this standardized format. This ensures consistent reporting, deduplication, and cross-framework mapping regardless of which tool produced the finding.

## Finding Object

```json
{
  "id": "INJ-001",
  "title": "SQL injection in user lookup",
  "severity": "critical",
  "confidence": "high",
  "location": {
    "file": "src/db/queries.ts",
    "line": 45,
    "end_line": 47,
    "function": "findUserById",
    "snippet": "cursor.execute(f\"SELECT * FROM users WHERE id = {user_id}\")"
  },
  "description": "User-controlled input is interpolated directly into a SQL query string without parameterization, allowing arbitrary SQL execution.",
  "impact": "An attacker can read, modify, or delete any data in the database, and potentially execute operating system commands.",
  "fix": {
    "summary": "Use parameterized query with placeholder",
    "diff": "- cursor.execute(f\"SELECT * FROM users WHERE id = {user_id}\")\n+ cursor.execute(\"SELECT * FROM users WHERE id = %s\", (user_id,))"
  },
  "references": {
    "cwe": "CWE-89",
    "owasp": "A03:2021",
    "stride": "T",
    "api_top10": null,
    "mitre_attck": "T1190",
    "sans_cwe25": 3
  },
  "scanner": {
    "name": "semgrep",
    "rule": "python.lang.security.audit.raw-query",
    "confirmed": true
  },
  "dread": {
    "damage": 9,
    "reproducibility": 8,
    "exploitability": 7,
    "affected_users": 8,
    "discoverability": 6,
    "score": 7.6
  },
  "metadata": {
    "tool": "injection",
    "framework": "owasp",
    "category": "A03",
    "scope": "changed",
    "depth": "standard",
    "timestamp": "2026-02-14T10:30:00Z"
  }
}
```

## Field Definitions

### Required Fields

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Unique identifier: `<PREFIX>-<NNN>`. Prefix is the tool's short code (e.g., `INJ`, `AC`, `CRYPT`, `SEC`). |
| `title` | string | One-line summary of the finding. |
| `severity` | enum | `critical`, `high`, `medium`, `low` |
| `location.file` | string | Relative file path from repository root. |
| `description` | string | What is wrong and why it matters. 2-3 sentences max. |

### Optional Fields

| Field | Type | Description |
|-------|------|-------------|
| `confidence` | enum | `high`, `medium`, `low` — how certain the finding is real (not a false positive). |
| `location.line` | number | Start line number. |
| `location.end_line` | number | End line number (for multi-line findings). |
| `location.function` | string | Function or method name containing the finding. |
| `location.snippet` | string | The vulnerable code snippet. |
| `impact` | string | What an attacker can achieve by exploiting this. |
| `fix.summary` | string | One-line fix description. |
| `fix.diff` | string | Unified diff showing the fix. |
| `references.cwe` | string | CWE identifier (e.g., `CWE-89`). |
| `references.owasp` | string | OWASP Top 10 category (e.g., `A03:2021`). |
| `references.stride` | string | Primary STRIDE category letter: `S`, `T`, `R`, `I`, `D`, or `E`. Use the single most relevant letter. |
| `references.api_top10` | string | OWASP API Top 10 category (e.g., `API1:2023`). |
| `references.mitre_attck` | string | MITRE ATT&CK technique ID (e.g., `T1190`). |
| `references.sans_cwe25` | number | Position in SANS/CWE Top 25 list (1-25). |
| `scanner.name` | string | Scanner that detected this (e.g., `semgrep`, `gitleaks`). |
| `scanner.rule` | string | Specific scanner rule ID. |
| `scanner.confirmed` | boolean | Whether scanner confirmed the finding. |
| `dread` | object | DREAD scoring (0-10 per factor). Present only in expert mode. |
| `metadata.tool` | string | The appsec skill that produced this finding. |
| `metadata.framework` | string | Parent framework (`owasp`, `stride`, `pasta`, `linddun`, `sans25`, `api`). |
| `metadata.category` | string | Category within framework (e.g., `A03`, `T`, `Stage-5`). |
| `metadata.scope` | string | Scope used for analysis. |
| `metadata.depth` | string | Depth mode used. |
| `metadata.timestamp` | string | ISO 8601 timestamp. |

## Severity Criteria

| Severity | Criteria |
|----------|----------|
| `critical` | Remotely exploitable, no authentication required, leads to full system compromise, data breach, or RCE. Fix immediately. |
| `high` | Exploitable with low effort, leads to significant data exposure, privilege escalation, or service disruption. Fix before release. |
| `medium` | Requires specific conditions or authenticated access to exploit. Limited impact. Fix in normal development cycle. |
| `low` | Theoretical risk, defense-in-depth issue, or minor information disclosure. Fix when convenient. |

## ID Prefix Registry

| Prefix | Tool | Framework |
|--------|------|-----------|
| `AC` | access-control | OWASP A01 |
| `CRYPT` | crypto | OWASP A02 |
| `INJ` | injection | OWASP A03 |
| `DESGN` | insecure-design | OWASP A04 |
| `MSCFG` | misconfig | OWASP A05 |
| `DEP` | outdated-deps | OWASP A06 |
| `AUTH` | auth | OWASP A07 |
| `INTEG` | integrity | OWASP A08 |
| `LOG` | logging | OWASP A09 |
| `SSRF` | ssrf | OWASP A10 |
| `SPOOF` | spoofing | STRIDE S |
| `TAMP` | tampering | STRIDE T |
| `REPUD` | repudiation | STRIDE R |
| `DISC` | info-disclosure | STRIDE I |
| `DOS` | dos | STRIDE D |
| `PRIV` | privilege-escalation | STRIDE E |
| `SEC` | secrets | Specialized |
| `RACE` | race-conditions | Specialized |
| `UPLD` | file-upload | Specialized |
| `GQL` | graphql | Specialized |
| `WS` | websocket | Specialized |
| `SRVLS` | serverless | Specialized |
| `API` | api | API Top 10 |
| `BIZ` | business-logic | Specialized |
| `FUZZ` | fuzz | Specialized |
| `LINK` | linking | LINDDUN L |
| `IDENT` | identifying | LINDDUN I |
| `NREP` | non-repudiation-privacy | LINDDUN N |
| `DTCT` | detecting | LINDDUN D1 |
| `DDSCL` | data-disclosure | LINDDUN D2 |
| `UNAWR` | unawareness | LINDDUN U |
| `NCMPL` | non-compliance | LINDDUN N2 |
| `PASTA` | pasta-* | PASTA |
| `RT` | red-team | Red Team |

## Aggregate Output

When a dispatcher or orchestrator collects findings from multiple subagents, wrap them in:

```json
{
  "tool": "owasp",
  "scope": "changed",
  "depth": "standard",
  "scanners_used": ["semgrep", "npm-audit"],
  "scanners_missing": ["gitleaks", "trivy"],
  "categories_checked": ["A01", "A03", "A07", "A10"],
  "categories_skipped": ["A02", "A04", "A05", "A06", "A08", "A09"],
  "skip_reason": "Not relevant based on pre-flight heuristics",
  "total_findings": 5,
  "by_severity": { "critical": 1, "high": 2, "medium": 1, "low": 1 },
  "findings": [ ... ]
}
```
