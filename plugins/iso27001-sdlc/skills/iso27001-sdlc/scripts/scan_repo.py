#!/usr/bin/env python3
"""
ISO 27001:2022 Repository Evidence Scanner

Scans a repository and produces a structured JSON evidence file.
This separates deterministic file-finding from judgment-based scoring,
ensuring consistent, reproducible results across runs.

Usage:
    python scan_repo.py /path/to/repo [--output evidence.json]
"""

import argparse
import json
import os
import re
import sys
from pathlib import Path
from datetime import datetime, timezone


# ---------------------------------------------------------------------------
# File pattern definitions
# ---------------------------------------------------------------------------

# Maps a logical evidence category to glob patterns (case-insensitive matching
# is done in code, not via glob, because not all filesystems support it).

FILE_PATTERNS = {
    # 8.4 — Access to Source Code
    "codeowners": [
        "CODEOWNERS", ".github/CODEOWNERS", ".gitlab/CODEOWNERS", "docs/CODEOWNERS"
    ],
    "branch_protection_config": [
        ".github/settings.yml", ".github/branch-protection.yml"
    ],
    "signed_commits_config": [
        ".gitsign.yml"
    ],
    "contributing": [
        "CONTRIBUTING.md", "CONTRIBUTING.rst", "CONTRIBUTING.txt",
        "docs/CONTRIBUTING.md", "docs/contributing.md"
    ],

    # 8.25 — Secure Development Life Cycle
    "pr_template": [
        ".github/PULL_REQUEST_TEMPLATE.md",
        ".github/PULL_REQUEST_TEMPLATE",       # directory
        ".github/pull_request_template.md",
        "docs/pull_request_template.md",
    ],
    "mr_template_dir": [
        ".gitlab/merge_request_templates",      # directory
    ],
    "issue_template": [
        ".github/ISSUE_TEMPLATE",               # directory
        ".gitlab/issue_templates",              # directory
    ],
    "security_policy": [
        "SECURITY.md", "security.md",
        "docs/security-policy.md", "docs/secure-development.md",
        "docs/sdlc.md", "docs/secure-sdlc.md",
        ".github/SECURITY.md",
    ],

    # 8.27 — Secure Architecture and Engineering
    "architecture_docs_dirs": [
        "docs/architecture", "docs/adr", "architecture", "doc/architecture",
    ],
    "architecture_docs_files": [
        "ARCHITECTURE.md", "docs/ARCHITECTURE.md",
    ],
    "threat_model": [
        "docs/security/threat-model.md", "docs/threat-model.md",
        "security/threat-model.md", "threat-model.md", "threat_model.md",
        "docs/security/threat_model.md",
    ],

    # 8.28 — Secure Coding
    "pre_commit": [".pre-commit-config.yaml"],
    "editorconfig": [".editorconfig"],
    "env_gitignore_check": [".gitignore"],
    "env_example": [".env.example", ".env.template", ".env.sample"],
    "secure_coding_docs": [
        "docs/coding-standards.md", "docs/secure-coding.md",
        "docs/code-guidelines.md", "docs/coding-guide.md",
        "CODING_STANDARDS.md", "SECURE_CODING.md",
    ],

    # Secrets scanning config
    "secrets_scanning_config": [
        ".gitleaks.toml", ".gitguardian.yml", ".trufflehog.yml",
        ".secrets.baseline",
    ],

    # Dependency management
    "lockfiles": [
        "package-lock.json", "yarn.lock", "pnpm-lock.yaml",
        "Pipfile.lock", "poetry.lock", "Gemfile.lock",
        "go.sum", "Cargo.lock", "composer.lock", "pubspec.lock",
        "mix.lock", "Package.resolved",
    ],
    "dependency_scanning_config": [
        ".snyk", "renovate.json", "renovate.json5", ".renovaterc",
        ".renovaterc.json",
        ".github/dependabot.yml", ".gitlab/dependabot.yml",
    ],

    # 8.29 — Security Testing
    "codeql_config": [
        ".github/codeql", ".github/workflows/codeql-analysis.yml",
        ".github/workflows/codeql.yml",
    ],
    "semgrep_config": [
        ".semgrep.yml", ".semgrep.yaml", ".semgrep",
    ],
    "sonar_config": [
        "sonar-project.properties",
    ],

    # 8.31 — Separation of Environments
    "env_specific_configs": [
        "config/development.yml", "config/development.json",
        "config/test.yml", "config/test.json",
        "config/staging.yml", "config/staging.json",
        "config/production.yml", "config/production.json",
        ".env.development", ".env.staging", ".env.production", ".env.test",
    ],
    "env_dirs": [
        "environments", "deploy", "infra/environments",
    ],
    "k8s_envs": [
        "k8s/overlays", "kustomize/overlays",
    ],
    "terraform_envs": [
        "terraform/environments", "infra/terraform/environments",
    ],
    "docker_compose_envs": [
        "docker-compose.dev.yml", "docker-compose.prod.yml",
        "docker-compose.staging.yml", "docker-compose.test.yml",
        "docker-compose.override.yml",
    ],

    # 8.32 — Change Management
    "changelog": [
        "CHANGELOG.md", "CHANGES.md", "HISTORY.md",
        "docs/changelog.md", "CHANGELOG.rst",
    ],
    "commitlint_config": [
        ".commitlintrc", ".commitlintrc.yml", ".commitlintrc.json",
        ".commitlintrc.js", "commitlint.config.js", "commitlint.config.ts",
        ".czrc", ".cz.toml",
    ],
    "runbooks": [
        "runbooks", "docs/runbooks", "docs/runbook.md", "docs/rollback.md",
        "scripts/rollback.sh", "scripts/rollback.py",
    ],

    # 8.33 — Test Information and Data
    "test_fixtures_dirs": [
        "fixtures", "factories", "seeds", "test/data",
        "test/fixtures", "tests/fixtures", "spec/fixtures",
        "__fixtures__", "test/factories", "tests/factories",
    ],

    # Supporting controls
    "security_txt": [
        "security.txt", ".well-known/security.txt",
    ],
    "iac_configs": [
        "terraform", "pulumi", "cloudformation",
        "ansible", "ansible.cfg",
    ],
    "gitops_configs": [
        "argocd", "flux-system", ".flux.yaml",
    ],
    "monitoring_configs": [
        "prometheus.yml", "prometheus.yaml",
        "alertmanager.yml", "datadog.yaml",
        ".pagerduty.yml",
    ],

    # CI/CD configs
    "ci_github_actions": [".github/workflows"],
    "ci_gitlab": [".gitlab-ci.yml"],
    "ci_jenkins": ["Jenkinsfile", "jenkins"],
    "ci_azure": ["azure-pipelines.yml", ".azure-pipelines"],
    "ci_circleci": [".circleci/config.yml", ".circleci"],
    "ci_bitbucket": ["bitbucket-pipelines.yml"],
}

# Linter configs by language
LINTER_PATTERNS = {
    "javascript_typescript": [
        ".eslintrc", ".eslintrc.js", ".eslintrc.json", ".eslintrc.yml",
        ".eslintrc.yaml", "eslint.config.js", "eslint.config.mjs",
        "eslint.config.ts", "biome.json", "biome.jsonc",
    ],
    "python": [
        ".flake8", ".bandit", ".pylintrc", ".ruff.toml", "ruff.toml",
    ],
    "java_kotlin": [
        "checkstyle.xml", "pmd.xml", "pmd-ruleset.xml",
        "spotbugs-exclude.xml", "spotbugs-include.xml",
    ],
    "go": [".golangci.yml", ".golangci.yaml"],
    "ruby": [".rubocop.yml", "brakeman.yml"],
    "rust": ["clippy.toml", "rustfmt.toml"],
    "c_cpp": [".clang-tidy", ".clang-format"],
    "php": ["phpstan.neon", "phpstan.neon.dist", "phpcs.xml", "phpcs.xml.dist", "psalm.xml"],
    "scala": ["scalastyle-config.xml", ".scalafix.conf", ".scalafmt.conf"],
    "swift": [".swiftlint.yml"],
    "elixir": [".credo.exs"],
    "csharp": [".editorconfig"],  # often used with Roslyn analyzers
    "dart": ["analysis_options.yaml"],
    "formatting_only": [
        ".prettierrc", ".prettierrc.js", ".prettierrc.json",
        ".prettierrc.yml", ".prettierrc.yaml",
    ],
}

# Security-specific static analysis tools
SECURITY_ANALYSIS_PATTERNS = {
    "bandit": [".bandit"],
    "brakeman": ["brakeman.yml"],
    "semgrep": [".semgrep.yml", ".semgrep.yaml", ".semgrep"],
    "sonarqube": ["sonar-project.properties"],
    "snyk": [".snyk"],
    "spotbugs_security": [],  # detected via content scanning
    "eslint_security": [],    # detected via content scanning
    "phpstan": ["phpstan.neon", "phpstan.neon.dist"],
    "credo": [".credo.exs"],
}

# Synthetic data / faker libraries by ecosystem
FAKER_LIBRARIES = {
    "python": ["faker", "factory_boy", "factory-boy", "mimesis", "polyfactory"],
    "javascript": ["@faker-js/faker", "faker", "casual", "chance", "fishery"],
    "java": ["java-faker", "datafaker", "instancio"],
    "ruby": ["faker", "factory_bot", "fabrication"],
    "go": ["gofakeit"],
    "php": ["fakerphp/faker"],
    "elixir": ["ex_machina", "faker"],
    "rust": ["fake"],
    "csharp": ["Bogus", "AutoFixture"],
    "dart": ["faker_dart"],
    "scala": ["scalacheck"],
    "swift": ["Fakery"],
}

# Secrets patterns (compiled regexes)
SECRET_PATTERNS = [
    ("AWS Access Key", re.compile(r'AKIA[0-9A-Z]{16}')),
    ("AWS Secret Key", re.compile(r'(?i)(aws_secret_access_key|aws_secret_key)\s*[=:]\s*[A-Za-z0-9/+=]{40}')),
    ("Private Key", re.compile(r'-----BEGIN\s+(RSA\s+|EC\s+|DSA\s+|OPENSSH\s+)?PRIVATE\s+KEY-----')),
    ("Generic API Key assignment", re.compile(
        r'''(?i)(api[_-]?key|api[_-]?secret|secret[_-]?key|access[_-]?token|auth[_-]?token|private[_-]?key)\s*[=:]\s*['"][A-Za-z0-9_\-/.+=]{20,}['"]'''
    )),
    ("Generic Password assignment", re.compile(
        r'''(?i)(password|passwd|pwd)\s*[=:]\s*['"][^'"]{8,}['"]'''
    )),
    ("Connection string with credentials", re.compile(
        r'(?i)(mongodb|postgres|mysql|redis|amqp)://[^:]+:[^@]+@'
    )),
    ("GitHub Token", re.compile(r'gh[ps]_[A-Za-z0-9_]{36,}')),
    ("Slack Token", re.compile(r'xox[baprs]-[0-9]+-[A-Za-z0-9]+')),
    ("Stripe Key", re.compile(r'[sr]k_(live|test)_[A-Za-z0-9]{20,}')),
]

# Files to skip during secrets scanning
SECRETS_SCAN_SKIP_PATTERNS = [
    r'\.lock$', r'lock\.json$', r'lock\.yaml$',
    r'\.min\.js$', r'\.min\.css$', r'\.map$',
    r'\.png$', r'\.jpg$', r'\.gif$', r'\.ico$', r'\.svg$', r'\.woff',
    r'\.pdf$', r'\.zip$', r'\.tar', r'\.gz$',
    r'node_modules/', r'vendor/', r'\.git/',
    r'__pycache__/', r'\.pyc$',
    r'\.sum$',  # go.sum contains hashes, not secrets
]

# CI security-related keywords (for scanning CI config content)
CI_SECURITY_KEYWORDS = [
    "codeql", "semgrep", "snyk", "trivy", "grype", "sast", "dast",
    "security-scan", "security_scan", "dependency-review", "dependency_scanning",
    "container_scanning", "license_scanning", "npm audit", "pip-audit",
    "safety check", "cargo audit", "bundler-audit", "gitleaks",
    "sonar-scanner", "sonarqube", "sonar", "checkmarx", "fortify",
    "veracode", "bandit", "brakeman", "gosec", "spotbugs",
    "zap", "owasp-zap", "dastardly", "nuclei", "anchore",
    "docker scan", "docker-scan",
]

CI_GATE_KEYWORDS_GITHUB = ["if: failure()", "required: true", "environment:"]
CI_GATE_KEYWORDS_GITLAB = ["allow_failure: false", "when: manual", "rules:"]


# ---------------------------------------------------------------------------
# Scanning functions
# ---------------------------------------------------------------------------

def find_files(repo_root: Path) -> dict:
    """Walk the repo and index all file paths (relative to root) for fast lookup."""
    index = {"files": [], "dirs": []}
    skip_dirs = {".git", "node_modules", "vendor", "__pycache__", ".tox",
                 ".venv", "venv", ".mypy_cache", ".pytest_cache", "dist",
                 "build", ".next", ".nuxt", "target", "bin", "obj"}
    for dirpath, dirnames, filenames in os.walk(repo_root):
        # Prune skipped directories
        dirnames[:] = [d for d in dirnames if d not in skip_dirs]
        rel_dir = os.path.relpath(dirpath, repo_root)
        if rel_dir != ".":
            index["dirs"].append(rel_dir)
        for f in filenames:
            rel_path = os.path.join(rel_dir, f) if rel_dir != "." else f
            index["files"].append(rel_path)
    return index


def match_patterns(file_index: dict, patterns: list[str]) -> dict:
    """Match file patterns against the index. Returns {pattern: [matched_paths]}."""
    results = {}
    all_files = file_index["files"]
    all_dirs = file_index["dirs"]
    all_entries = all_files + all_dirs

    for pattern in patterns:
        matched = []
        pattern_lower = pattern.lower()
        for entry in all_entries:
            if entry.lower() == pattern_lower or entry.lower().endswith("/" + pattern_lower):
                matched.append(entry)
        results[pattern] = matched
    return results


def check_file_patterns(repo_root: Path, file_index: dict) -> dict:
    """Check all FILE_PATTERNS categories and return evidence."""
    evidence = {}
    for category, patterns in FILE_PATTERNS.items():
        matches = match_patterns(file_index, patterns)
        found = []
        for pattern, paths in matches.items():
            found.extend(paths)
        evidence[category] = sorted(set(found))
    return evidence


def check_linter_patterns(repo_root: Path, file_index: dict) -> dict:
    """Check linter configs by language."""
    evidence = {}
    for language, patterns in LINTER_PATTERNS.items():
        matches = match_patterns(file_index, patterns)
        found = []
        for pattern, paths in matches.items():
            found.extend(paths)
        evidence[language] = sorted(set(found))
    return evidence


def check_security_analysis(repo_root: Path, file_index: dict) -> dict:
    """Check for security-specific analysis tool configs."""
    evidence = {}
    for tool, patterns in SECURITY_ANALYSIS_PATTERNS.items():
        if not patterns:
            evidence[tool] = []  # needs content scanning
            continue
        matches = match_patterns(file_index, patterns)
        found = []
        for pattern, paths in matches.items():
            found.extend(paths)
        evidence[tool] = sorted(set(found))
    return evidence


def check_faker_libraries(repo_root: Path, file_index: dict) -> dict:
    """Check package manifests for synthetic data libraries."""
    evidence = {}
    manifest_files = {
        "python": ["requirements.txt", "requirements-dev.txt", "requirements-test.txt",
                    "pyproject.toml", "setup.py", "setup.cfg", "Pipfile"],
        "javascript": ["package.json"],
        "java": ["pom.xml", "build.gradle", "build.gradle.kts"],
        "ruby": ["Gemfile"],
        "go": ["go.mod"],
        "php": ["composer.json"],
        "elixir": ["mix.exs"],
        "rust": ["Cargo.toml"],
        "csharp": ["*.csproj"],  # special handling
        "dart": ["pubspec.yaml"],
        "scala": ["build.sbt"],
        "swift": ["Package.swift"],
    }

    for ecosystem, libs in FAKER_LIBRARIES.items():
        manifests = manifest_files.get(ecosystem, [])
        found_libs = []
        for manifest_pattern in manifests:
            # Find matching manifest files
            for fpath in file_index["files"]:
                fname = os.path.basename(fpath).lower()
                if manifest_pattern.startswith("*"):
                    if fname.endswith(manifest_pattern[1:].lower()):
                        found_libs.extend(_scan_file_for_strings(
                            repo_root / fpath, libs))
                elif fname == manifest_pattern.lower():
                    found_libs.extend(_scan_file_for_strings(
                        repo_root / fpath, libs))
        evidence[ecosystem] = sorted(set(found_libs))

    # Also check pyproject.toml for Python tool configs (ruff, bandit, etc.)
    for fpath in file_index["files"]:
        if os.path.basename(fpath).lower() == "pyproject.toml":
            content = _read_file_safe(repo_root / fpath)
            if content:
                if "bandit" in content.lower():
                    evidence.setdefault("_security_tools_in_pyproject", []).append(
                        f"{fpath}: bandit config found")
                if "ruff" in content.lower():
                    evidence.setdefault("_security_tools_in_pyproject", []).append(
                        f"{fpath}: ruff config found")

    return evidence


def scan_for_secrets(repo_root: Path, file_index: dict, max_files: int = 500) -> list[dict]:
    """Scan source files for potential hardcoded secrets."""
    findings = []
    skip_compiled = [re.compile(p) for p in SECRETS_SCAN_SKIP_PATTERNS]
    scanned = 0

    for fpath in file_index["files"]:
        if scanned >= max_files:
            break

        # Skip binary/irrelevant files
        if any(p.search(fpath) for p in skip_compiled):
            continue

        full_path = repo_root / fpath
        if not full_path.is_file():
            continue

        # Only scan text-like files under 500KB
        try:
            size = full_path.stat().st_size
            if size > 500_000:
                continue
        except OSError:
            continue

        content = _read_file_safe(full_path)
        if content is None:
            continue

        scanned += 1
        for line_no, line in enumerate(content.splitlines(), 1):
            # Skip comments and obvious test/example lines
            stripped = line.strip()
            if stripped.startswith("#") or stripped.startswith("//"):
                if "example" in stripped.lower() or "placeholder" in stripped.lower():
                    continue

            for pattern_name, pattern in SECRET_PATTERNS:
                if pattern.search(line):
                    findings.append({
                        "file": fpath,
                        "line": line_no,
                        "pattern": pattern_name,
                        "snippet": line.strip()[:120],
                    })

    return findings


def check_env_in_gitignore(repo_root: Path) -> dict:
    """Check whether .env is in .gitignore."""
    gitignore_path = repo_root / ".gitignore"
    result = {"gitignore_exists": False, "env_ignored": False, "env_files_committed": []}

    if gitignore_path.is_file():
        result["gitignore_exists"] = True
        content = _read_file_safe(gitignore_path) or ""
        for line in content.splitlines():
            line = line.strip()
            if line in (".env", ".env*", ".env.*", "*.env"):
                result["env_ignored"] = True
                break

    # Check if any .env files exist (not .env.example etc.)
    for fpath in os.listdir(repo_root):
        if fpath == ".env":
            result["env_files_committed"].append(fpath)

    return result


def scan_ci_configs(repo_root: Path, file_index: dict) -> dict:
    """Scan CI config files for security-related content."""
    ci_evidence = {
        "system_detected": None,
        "config_files": [],
        "security_jobs": [],
        "gate_indicators": [],
        "deployment_stages": [],
        "all_ci_content": "",
    }

    # Detect CI system
    ci_systems = [
        ("github_actions", [".github/workflows"]),
        ("gitlab_ci", [".gitlab-ci.yml"]),
        ("jenkins", ["Jenkinsfile"]),
        ("azure_pipelines", ["azure-pipelines.yml"]),
        ("circleci", [".circleci"]),
        ("bitbucket_pipelines", ["bitbucket-pipelines.yml"]),
    ]

    detected_systems = []
    for system_name, indicators in ci_systems:
        for indicator in indicators:
            indicator_lower = indicator.lower()
            for entry in file_index["files"] + file_index["dirs"]:
                if entry.lower() == indicator_lower or entry.lower().startswith(indicator_lower + "/"):
                    detected_systems.append(system_name)
                    break

    ci_evidence["system_detected"] = list(set(detected_systems)) or None

    # Collect all CI config file contents
    ci_file_patterns = [
        ".github/workflows/", ".gitlab-ci.yml", "Jenkinsfile",
        "azure-pipelines.yml", ".circleci/config.yml",
        "bitbucket-pipelines.yml",
    ]

    all_content = []
    for fpath in file_index["files"]:
        for pattern in ci_file_patterns:
            if fpath.lower().startswith(pattern.lower()) or fpath.lower() == pattern.lower():
                ci_evidence["config_files"].append(fpath)
                content = _read_file_safe(repo_root / fpath)
                if content:
                    all_content.append(f"--- {fpath} ---\n{content}")
                break

    combined = "\n".join(all_content)
    ci_evidence["all_ci_content"] = combined[:50000]  # cap at 50KB

    # Search for security keywords
    combined_lower = combined.lower()
    for keyword in CI_SECURITY_KEYWORDS:
        if keyword.lower() in combined_lower:
            ci_evidence["security_jobs"].append(keyword)

    # Search for gate indicators
    for keyword in CI_GATE_KEYWORDS_GITHUB + CI_GATE_KEYWORDS_GITLAB:
        if keyword.lower() in combined_lower:
            ci_evidence["gate_indicators"].append(keyword)

    # Search for deployment indicators
    deploy_keywords = ["deploy", "release", "publish", "rollout"]
    for keyword in deploy_keywords:
        if keyword in combined_lower:
            ci_evidence["deployment_stages"].append(keyword)

    ci_evidence["security_jobs"] = sorted(set(ci_evidence["security_jobs"]))
    ci_evidence["gate_indicators"] = sorted(set(ci_evidence["gate_indicators"]))
    ci_evidence["deployment_stages"] = sorted(set(ci_evidence["deployment_stages"]))

    return ci_evidence


def scan_content_for_keywords(repo_root: Path, file_index: dict,
                               target_files: list[str],
                               keywords: list[str]) -> list[dict]:
    """Scan specific files for keyword presence. Used for checking
    security content in PR templates, architecture docs, etc."""
    findings = []
    for fpath in file_index["files"]:
        fpath_lower = fpath.lower()
        if not any(fpath_lower == t.lower() or fpath_lower.endswith("/" + t.lower())
                   for t in target_files):
            # Also match by directory prefix
            if not any(fpath_lower.startswith(t.lower()) for t in target_files
                       if t.endswith("/")):
                continue

        content = _read_file_safe(repo_root / fpath)
        if not content:
            continue

        content_lower = content.lower()
        matched_keywords = [k for k in keywords if k.lower() in content_lower]
        if matched_keywords:
            findings.append({
                "file": fpath,
                "keywords_found": matched_keywords,
            })
    return findings


def detect_languages(file_index: dict) -> list[str]:
    """Detect programming languages from file extensions and manifests."""
    ext_map = {
        ".py": "Python", ".js": "JavaScript", ".ts": "TypeScript",
        ".jsx": "JavaScript (React)", ".tsx": "TypeScript (React)",
        ".java": "Java", ".kt": "Kotlin", ".scala": "Scala",
        ".go": "Go", ".rs": "Rust", ".rb": "Ruby",
        ".php": "PHP", ".cs": "C#", ".swift": "Swift",
        ".ex": "Elixir", ".exs": "Elixir",
        ".c": "C", ".cpp": "C++", ".h": "C/C++",
        ".dart": "Dart", ".lua": "Lua",
    }
    manifest_map = {
        "package.json": "JavaScript/TypeScript",
        "pyproject.toml": "Python", "setup.py": "Python",
        "Cargo.toml": "Rust", "go.mod": "Go",
        "Gemfile": "Ruby", "pom.xml": "Java",
        "build.gradle": "Java/Kotlin", "build.gradle.kts": "Kotlin",
        "mix.exs": "Elixir", "composer.json": "PHP",
        "pubspec.yaml": "Dart", "build.sbt": "Scala",
        "Package.swift": "Swift",
    }

    detected = set()
    for fpath in file_index["files"]:
        ext = os.path.splitext(fpath)[1].lower()
        if ext in ext_map:
            detected.add(ext_map[ext])
        fname = os.path.basename(fpath).lower()
        for manifest, lang in manifest_map.items():
            if fname == manifest.lower():
                detected.add(lang)
    return sorted(detected)


def detect_containers(file_index: dict) -> dict:
    """Detect container usage."""
    evidence = {"dockerfile": False, "docker_compose": False, "k8s_manifests": False}
    for fpath in file_index["files"]:
        fname = os.path.basename(fpath).lower()
        if fname == "dockerfile" or fname.startswith("dockerfile."):
            evidence["dockerfile"] = True
        if fname.startswith("docker-compose"):
            evidence["docker_compose"] = True
        if fpath.lower().endswith((".yaml", ".yml")):
            content = _read_file_safe(Path(fpath))
            # Don't read; just check by path patterns
            if any(d in fpath.lower() for d in ["k8s/", "kubernetes/", "kustomize/", "helm/"]):
                evidence["k8s_manifests"] = True
    return evidence


def detect_iac(file_index: dict) -> dict:
    """Detect infrastructure-as-code presence."""
    evidence = {
        "terraform": False, "pulumi": False, "cloudformation": False,
        "ansible": False, "helm": False,
    }
    for entry in file_index["files"] + file_index["dirs"]:
        entry_lower = entry.lower()
        if ".tf" in entry_lower or "terraform" in entry_lower:
            evidence["terraform"] = True
        if "pulumi" in entry_lower:
            evidence["pulumi"] = True
        if "cloudformation" in entry_lower or entry_lower.endswith(".template"):
            evidence["cloudformation"] = True
        if "ansible" in entry_lower or "playbook" in entry_lower:
            evidence["ansible"] = True
        if "helm" in entry_lower or "chart.yaml" in os.path.basename(entry).lower():
            evidence["helm"] = True
    return evidence


def detect_monorepo(repo_root: Path, file_index: dict) -> dict:
    """Detect monorepo patterns."""
    indicators = {
        "is_monorepo": False,
        "workspace_config": False,
        "sub_projects": [],
    }

    # Check for workspace configs
    for fpath in file_index["files"]:
        fname = os.path.basename(fpath).lower()
        if fname == "package.json" and os.path.dirname(fpath) == "":
            content = _read_file_safe(repo_root / fpath)
            if content and "workspaces" in content:
                indicators["workspace_config"] = True
                indicators["is_monorepo"] = True
        if fname in ("pnpm-workspace.yaml", "lerna.json", "nx.json", "turbo.json",
                      "rush.json"):
            indicators["workspace_config"] = True
            indicators["is_monorepo"] = True

    # Check for packages/ or apps/ directories with their own manifests
    for fpath in file_index["files"]:
        parts = fpath.split(os.sep)
        if len(parts) == 3 and parts[0] in ("packages", "apps", "services", "libs", "modules"):
            fname = parts[2].lower()
            if fname in ("package.json", "pyproject.toml", "cargo.toml", "go.mod",
                         "pom.xml", "build.gradle"):
                indicators["sub_projects"].append(parts[1])
                indicators["is_monorepo"] = True

    indicators["sub_projects"] = sorted(set(indicators["sub_projects"]))
    return indicators


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _read_file_safe(path: Path, max_size: int = 500_000) -> str | None:
    """Read a file, returning None if it can't be read or is too large."""
    try:
        if not path.is_file():
            return None
        if path.stat().st_size > max_size:
            return None
        return path.read_text(encoding="utf-8", errors="replace")
    except (OSError, PermissionError):
        return None


def _scan_file_for_strings(path: Path, strings: list[str]) -> list[str]:
    """Check if a file contains any of the given strings (case-insensitive)."""
    content = _read_file_safe(path)
    if not content:
        return []
    content_lower = content.lower()
    return [s for s in strings if s.lower() in content_lower]


# ---------------------------------------------------------------------------
# ADR scanning (for 8.27)
# ---------------------------------------------------------------------------

def scan_adrs_for_security(repo_root: Path, file_index: dict) -> list[dict]:
    """Find ADRs and check if any address security topics."""
    adr_dirs = ["docs/adr", "docs/architecture", "architecture", "adr"]
    security_keywords = [
        "security", "authentication", "authorization", "encryption",
        "threat", "trust boundary", "least privilege", "zero trust",
        "defence in depth", "defense in depth", "fail-secure",
    ]
    findings = []
    for fpath in file_index["files"]:
        fpath_lower = fpath.lower()
        is_adr = any(fpath_lower.startswith(d.lower() + "/") for d in adr_dirs)
        is_adr = is_adr or "adr-" in fpath_lower or "adr_" in fpath_lower
        if not is_adr:
            continue
        if not fpath_lower.endswith((".md", ".rst", ".txt")):
            continue

        content = _read_file_safe(repo_root / fpath)
        if not content:
            continue
        content_lower = content.lower()
        matched = [k for k in security_keywords if k in content_lower]
        findings.append({
            "file": fpath,
            "has_security_content": len(matched) > 0,
            "security_keywords": matched,
        })
    return findings


# ---------------------------------------------------------------------------
# Test file scanning (for 8.29, 8.33)
# ---------------------------------------------------------------------------

def find_security_test_files(file_index: dict) -> list[str]:
    """Find test files with security-related names."""
    security_test_patterns = [
        "security", "auth", "permission", "access_control",
        "access-control", "authz", "authn", "csrf", "xss",
        "injection", "sanitiz",
    ]
    results = []
    test_dirs = ["test", "tests", "spec", "__tests__", "test_", "tests_"]
    for fpath in file_index["files"]:
        fpath_lower = fpath.lower()
        # Must be in a test directory or have test in the name
        is_test = any(f"/{d}/" in f"/{fpath_lower}" for d in test_dirs)
        is_test = is_test or "test_" in fpath_lower or "_test." in fpath_lower or ".test." in fpath_lower or ".spec." in fpath_lower
        if not is_test:
            continue
        if any(p in fpath_lower for p in security_test_patterns):
            results.append(fpath)
    return results


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def run_scan(repo_path: str, output_path: str | None = None) -> dict:
    repo_root = Path(repo_path).resolve()
    if not repo_root.is_dir():
        print(f"Error: {repo_root} is not a directory", file=sys.stderr)
        sys.exit(1)

    print(f"Scanning repository: {repo_root}", file=sys.stderr)

    # Phase 1: Index all files
    print("  Indexing files...", file=sys.stderr)
    file_index = find_files(repo_root)
    print(f"  Found {len(file_index['files'])} files, {len(file_index['dirs'])} directories",
          file=sys.stderr)

    # Phase 2: Run all checks
    print("  Checking file patterns...", file=sys.stderr)
    file_evidence = check_file_patterns(repo_root, file_index)

    print("  Checking linter configs...", file=sys.stderr)
    linter_evidence = check_linter_patterns(repo_root, file_index)

    print("  Checking security analysis tools...", file=sys.stderr)
    security_analysis = check_security_analysis(repo_root, file_index)

    print("  Checking faker/synthetic data libraries...", file=sys.stderr)
    faker_evidence = check_faker_libraries(repo_root, file_index)

    print("  Scanning for hardcoded secrets...", file=sys.stderr)
    secret_findings = scan_for_secrets(repo_root, file_index)

    print("  Checking .env/.gitignore...", file=sys.stderr)
    env_check = check_env_in_gitignore(repo_root)

    print("  Scanning CI/CD configs...", file=sys.stderr)
    ci_evidence = scan_ci_configs(repo_root, file_index)

    print("  Scanning ADRs for security content...", file=sys.stderr)
    adr_findings = scan_adrs_for_security(repo_root, file_index)

    print("  Finding security test files...", file=sys.stderr)
    security_tests = find_security_test_files(file_index)

    print("  Detecting languages...", file=sys.stderr)
    languages = detect_languages(file_index)

    print("  Detecting containers...", file=sys.stderr)
    containers = detect_containers(file_index)

    print("  Detecting IaC...", file=sys.stderr)
    iac = detect_iac(file_index)

    print("  Detecting monorepo...", file=sys.stderr)
    monorepo = detect_monorepo(repo_root, file_index)

    # PR template security content check
    print("  Scanning PR templates for security content...", file=sys.stderr)
    pr_security = scan_content_for_keywords(
        repo_root, file_index,
        [".github/PULL_REQUEST_TEMPLATE.md", ".github/PULL_REQUEST_TEMPLATE/",
         ".gitlab/merge_request_templates/", "docs/pull_request_template.md"],
        ["security", "vulnerability", "threat", "risk", "data protection",
         "authentication", "authorization", "privacy"]
    )

    # Architecture docs security content check
    print("  Scanning architecture docs for security content...", file=sys.stderr)
    arch_security = scan_content_for_keywords(
        repo_root, file_index,
        ["docs/architecture/", "architecture/", "ARCHITECTURE.md",
         "docs/ARCHITECTURE.md"],
        ["trust boundary", "threat model", "least privilege",
         "defence in depth", "defense in depth", "zero trust",
         "network segmentation", "encryption at rest", "encryption in transit",
         "security", "authentication", "authorization"]
    )

    # Assemble evidence
    evidence = {
        "scan_metadata": {
            "repository": str(repo_root),
            "scan_date": datetime.now(timezone.utc).isoformat(),
            "total_files": len(file_index["files"]),
            "total_dirs": len(file_index["dirs"]),
        },
        "repo_context": {
            "languages": languages,
            "containers": containers,
            "iac": iac,
            "monorepo": monorepo,
            "ci_cd": {
                "systems_detected": ci_evidence["system_detected"],
                "config_files": ci_evidence["config_files"],
            },
        },
        "file_evidence": file_evidence,
        "linter_evidence": linter_evidence,
        "security_analysis": security_analysis,
        "faker_evidence": faker_evidence,
        "secrets_findings": secret_findings,
        "env_gitignore": env_check,
        "ci_evidence": {
            "systems": ci_evidence["system_detected"],
            "config_files": ci_evidence["config_files"],
            "security_jobs": ci_evidence["security_jobs"],
            "gate_indicators": ci_evidence["gate_indicators"],
            "deployment_stages": ci_evidence["deployment_stages"],
        },
        "adr_findings": adr_findings,
        "security_test_files": security_tests,
        "pr_template_security": pr_security,
        "architecture_security": arch_security,
    }

    # Strip the all_ci_content from the output (too large for JSON report)
    # but note: Claude can read CI files directly if needed for deeper analysis

    # Output
    output = json.dumps(evidence, indent=2, default=str)
    if output_path:
        Path(output_path).write_text(output)
        print(f"Evidence written to: {output_path}", file=sys.stderr)
    else:
        print(output)

    # Print summary
    print("\n--- Scan Summary ---", file=sys.stderr)
    print(f"Languages: {', '.join(languages) or 'None detected'}", file=sys.stderr)
    print(f"CI/CD: {', '.join(ci_evidence['system_detected'] or ['None detected'])}", file=sys.stderr)
    print(f"Containers: {'Yes' if any(containers.values()) else 'No'}", file=sys.stderr)
    print(f"IaC: {', '.join(k for k, v in iac.items() if v) or 'None'}", file=sys.stderr)
    print(f"Monorepo: {'Yes' if monorepo['is_monorepo'] else 'No'}", file=sys.stderr)
    print(f"Potential secrets found: {len(secret_findings)}", file=sys.stderr)
    print(f"Security test files: {len(security_tests)}", file=sys.stderr)
    print(f"CI security jobs: {len(ci_evidence['security_jobs'])}", file=sys.stderr)

    return evidence


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="ISO 27001 Repository Evidence Scanner")
    parser.add_argument("repo_path", help="Path to the repository root")
    parser.add_argument("--output", "-o", help="Output JSON file path (default: stdout)")
    args = parser.parse_args()

    run_scan(args.repo_path, args.output)
