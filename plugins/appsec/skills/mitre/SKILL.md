---
name: mitre
description: >
  This skill should be used when the user asks to "map to ATT&CK",
  "show attack techniques", "MITRE mapping", or wants to understand
  how findings relate to real-world attacker behavior. Maps security
  findings to MITRE ATT&CK tactics, techniques, and procedures.
---

# MITRE ATT&CK Mapping Skill

Post-analysis enrichment tool that maps existing security findings to the
MITRE ATT&CK framework. This skill does NOT discover new vulnerabilities.
It takes findings produced by other skills (OWASP, STRIDE, SANS/CWE Top 25)
and enriches them with ATT&CK tactics, techniques, attack chain analysis,
and threat actor TTP cross-references.

This skill operates on findings, not on source code directly.

## Supported Flags

Read [`../../shared/schemas/flags.md`](../../shared/schemas/flags.md) for the
full flag specification. This skill supports the following flags.

| Flag | Skill-Specific Behavior |
|------|------------------------|
| `--scope` | Not used directly. Findings are sourced from prior analysis or `.appsec/findings/`. |
| `--depth` | Controls enrichment depth. `standard` maps techniques. `deep` builds kill chains. `expert` adds threat actor TTPs and DREAD scoring. |
| `--severity` | Filter input findings before mapping. Only findings at or above this severity are processed. |
| `--format` | Applied to final output. |
| `--quiet` | Mappings only, suppress narrative descriptions. |
| `--explain` | Add detailed ATT&CK context and learning material per mapping. |

## Framework Reference

Read [`../../shared/frameworks/mitre-attck.md`](../../shared/frameworks/mitre-attck.md)
for the full MITRE ATT&CK specification including tactic definitions,
technique descriptions, code-level patterns, cross-framework mapping tables,
and kill chain construction guidance.

## Workflow

### Step 1: Acquire Findings

Collect existing findings from one or more sources, checked in priority order:

1. **Current conversation context**: If findings are present from a prior
   analysis step (e.g., `/appsec:owasp` or `/appsec:stride`), use those.
2. **Findings directory**: Check `.appsec/findings/` for persisted `*.json` files.
3. **User-specified file**: If the user provides a path, read and parse it.

If no findings are available, inform the user and suggest running
`/appsec:owasp`, `/appsec:stride`, or `/appsec:sans25` first.

### Step 2: Validate and Normalize Findings

Verify each finding conforms to `shared/schemas/findings.md`. Ensure
required fields are present (`id`, `title`, `severity`, `location.file`,
`description`). Discard malformed entries with a warning.

Normalize existing cross-references for mapping priority:
- `references.cwe` — primary key for ATT&CK mapping.
- `references.owasp` — secondary, via OWASP-to-ATT&CK table.
- `references.stride` — tertiary, via STRIDE-to-ATT&CK table.

### Step 3: Map Findings to ATT&CK Techniques

For each finding, determine applicable ATT&CK techniques using the
cross-framework mapping tables in `mitre-attck.md`:

1. **CWE-based**: "ATT&CK Techniques to CWE" table (e.g., CWE-89 maps to T1190, T1059).
2. **OWASP-based**: "ATT&CK Techniques to OWASP Top 10" table (when CWE unavailable).
3. **STRIDE-based**: "ATT&CK Techniques to STRIDE" table (tertiary source).
4. **Pattern-based**: Analyze `description` and `title` keywords against technique descriptions.

For each mapped technique, record `technique_id`, `technique_name`,
`tactic_id`, and `tactic_name`. Update `references.mitre_attck` with the
primary technique ID.

### Step 4: Build Tactic Coverage Matrix

Each technique belongs to one or more tactics. Produce a matrix showing
which tactics each finding touches:

| Finding ID | Recon | Initial Access | Execution | Priv Esc | Cred Access | Collection | Exfiltration | Impact |
|------------|-------|---------------|-----------|----------|-------------|------------|--------------|--------|
| INJ-001 | | T1190 | T1059 | | T1552 | T1005 | T1041 | T1485 |
| AUTH-003 | T1589 | T1078 | | T1548 | T1110 | | | |

### Step 5: Build Attack Chains

Group findings that chain into multi-step attack scenarios from
reconnaissance through impact. For each chain:

1. **Entry point**: A finding enabling Initial Access (TA0001) or Reconnaissance (TA0043).
2. **Lateral steps**: Trace technique-to-technique transitions through the kill chain.
3. **Terminal impact**: Map to Impact tactics (TA0040): data destruction (T1485), manipulation (T1565), ransomware (T1486), or DoS (T1498).
4. **Chain severity**: Maximum terminal impact severity, elevated one level if 3+ findings compound.

```
CHAIN-001: SQL Injection to Data Exfiltration
  Severity: critical
  Steps:
    1. [INJ-001] SQL injection in /api/users (T1190 -> Initial Access)
    2. [INJ-001] Database dump via UNION SELECT (T1005 -> Collection)
    3. [CRYPT-002] Credentials stored in plaintext (T1552 -> Credential Access)
    4. [AUTH-003] No MFA on admin portal (T1078 -> Privilege Escalation)
  Impact: Full database compromise, credential theft, admin takeover
```

### Step 6: Kill Chain Visualization

Produce a text-based kill chain diagram mapping findings onto Lockheed Martin
Cyber Kill Chain stages aligned with ATT&CK tactics:

```
Reconnaissance   Initial Access    Execution        Collection       Exfiltration
     |                |                |                |                |
     v                v                v                v                v
[T1595 Scan] -> [T1190 SQLi] --> [T1059 Cmd] -> [T1005 Dump] -> [T1041 Exfil]
                 INJ-001           INJ-001        INJ-001
                                                     |
                                                     v
                                   [T1552 Creds] -> [T1078 Acct] -> [T1548 Priv]
                                    CRYPT-002        AUTH-003        AUTH-003
```

For `--format json`, produce a structured chain object with nodes and edges.

### Step 7: Cross-Reference Threat Actor TTPs

Available at `--depth deep` and `--depth expert`. For each technique, note
which threat actor groups commonly use it:

| Technique | Known Usage |
|-----------|-------------|
| T1190 Exploit Public-Facing App | APT28, APT41, Lazarus Group, FIN7, most initial access brokers |
| T1078 Valid Accounts | APT29, APT41, FIN6 -- commonly after credential theft |
| T1552 Unsecured Credentials | APT33, FIN7 -- harvesting from config files |
| T1505.003 Web Shell | APT41, Hafnium -- persistent access via uploaded shells |

This is NOT a threat intelligence assessment. It shows that identified
techniques are actively used in real-world attacks.

### Step 8: Produce Output

```json
{
  "tool": "mitre",
  "input_findings": 12,
  "mapped_findings": 10,
  "unmapped_findings": 2,
  "techniques_identified": 8,
  "tactics_covered": 6,
  "attack_chains": 2,
  "tactic_coverage": {
    "reconnaissance": ["T1595"],
    "initial_access": ["T1190", "T1078"],
    "execution": ["T1059"],
    "credential_access": ["T1552", "T1110"],
    "collection": ["T1005"],
    "exfiltration": ["T1041"],
    "impact": ["T1485"]
  },
  "chains": [ ... ],
  "enriched_findings": [ ... ]
}
```

### Step 9: Present Results

Output the report in the requested `--format`. Include:
- **Mapping summary**: findings mapped, techniques identified, tactics covered.
- **Tactic coverage matrix**: ATT&CK tactics represented and gaps.
- **Technique breakdown**: findings per technique with parent tactic.
- **Attack chains**: step-by-step narrative with kill chain visualization.
- **Coverage gaps**: tactics with no mapped findings flagged as areas needing further analysis.

## Expert Mode

If `--depth expert` is set, additionally:

1. Read [`../../shared/frameworks/dread.md`](../../shared/frameworks/dread.md)
   for DREAD scoring criteria. Assign a DREAD score to each attack chain.

2. **Threat actor profiling**: For each chain, identify the most likely
   threat actor class (opportunistic, insider, APT, nation-state) based
   on complexity and resources required.

3. **Detection gap analysis**: For each technique in a chain, assess
   whether the codebase has logging or alerting to detect the attack at
   that stage. Cross-reference with OWASP A09 findings if available.
   Flag chains where multiple stages lack detection as highest priority.

4. **Mitigation roadmap**: For each chain, produce a prioritized list
   of mitigations that break the chain at the earliest stage. Prefer
   mitigations that break multiple chains simultaneously.

5. Append expert findings with prefix `ATK` and `metadata.tool` set to
   `"mitre-attck"`.
