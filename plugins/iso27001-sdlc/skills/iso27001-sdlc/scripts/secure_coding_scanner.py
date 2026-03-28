#!/usr/bin/env python3
"""
Secure Coding Practice Evidence Scanner (supplement to scan_repo.py)

Detects evidence of secure coding practices by scanning dependency manifests
for known security libraries, source files for unsafe patterns, and config
files for insecure settings.

Covers: input validation, output encoding, authentication, cryptography,
security headers, session management, ORM usage, structured logging,
rate limiting, CORS, file upload security, unsafe functions, SBOM tooling.
"""

import os
import re
from pathlib import Path


# ---------------------------------------------------------------------------
# Per-ecosystem dependency maps
# ---------------------------------------------------------------------------

# Each category maps ecosystem names to lists of package/library names
# to search for in dependency manifests.

INPUT_VALIDATION_LIBS = {
    "python": ["marshmallow", "webargs", "pydantic", "flask-wtf", "wtforms",
               "cerberus", "voluptuous", "django-rest-framework", "djangorestframework"],
    "javascript": ["express-validator", "joi", "@hapi/joi", "zod", "yup",
                   "class-validator", "ajv", "superstruct", "io-ts", "valibot"],
    "java": ["spring-boot-starter-validation", "hibernate-validator",
             "jakarta.validation", "javax.validation"],
    "go": ["github.com/go-playground/validator"],
    "php": ["respect/validation", "symfony/validator"],
    "elixir": [],  # Ecto changesets built-in
    "csharp": ["FluentValidation"],
    "rust": ["validator"],
    "ruby": [],  # ActiveModel built-in
    "dart": ["form_field_validator"],
}

AUTH_LIBS = {
    "python": ["django-allauth", "djangorestframework-simplejwt",
               "django-oauth-toolkit", "social-auth-app-django",
               "flask-login", "flask-security-too", "flask-jwt-extended",
               "authlib", "python-jose", "pyjwt"],
    "javascript": ["passport", "next-auth", "@auth/core", "express-session",
                   "jsonwebtoken", "jose", "@auth0/nextjs-auth0",
                   "connect-mongo", "express-openid-connect"],
    "java": ["spring-boot-starter-security", "spring-boot-starter-oauth2-client",
             "spring-security-oauth2-jose"],
    "go": ["github.com/golang-jwt/jwt", "github.com/coreos/go-oidc",
           "github.com/markbates/goth"],
    "ruby": ["devise", "omniauth", "sorcery", "rodauth"],
    "php": ["laravel/passport", "laravel/sanctum", "laravel/fortify",
            "laravel/breeze", "lexik/jwt-authentication-bundle",
            "symfony/security-bundle"],
    "elixir": ["guardian", "pow", "ueberauth"],
    "csharp": ["Microsoft.AspNetCore.Authentication.JwtBearer"],
    "rust": ["actix-web-httpauth", "jsonwebtoken"],
}

PASSWORD_HASHING_LIBS = {
    "python": ["bcrypt", "argon2-cffi", "argon2", "passlib"],
    "javascript": ["bcrypt", "bcryptjs", "argon2", "scrypt"],
    "java": [],  # Spring Security built-in encoders
    "go": ["golang.org/x/crypto/bcrypt", "golang.org/x/crypto/argon2"],
    "ruby": ["bcrypt", "argon2", "scrypt"],
    "php": [],  # password_hash() built-in
    "elixir": ["bcrypt_elixir", "argon2_elixir", "pbkdf2_elixir", "comeonin"],
    "csharp": ["BCrypt.Net-Next", "Isopoh.Cryptography.Argon2"],
    "rust": ["bcrypt", "argon2", "rust-argon2"],
}

SECURITY_HEADER_LIBS = {
    "python": ["flask-talisman", "secure", "django-csp"],
    "javascript": ["helmet"],
    "ruby": ["secure_headers"],
    "csharp": ["NetEscapades.AspNetCore.SecurityHeaders"],
    "php": [],  # typically custom middleware
    "elixir": [],  # put_secure_browser_headers built-in
}

RATE_LIMIT_LIBS = {
    "python": ["django-ratelimit", "flask-limiter", "slowapi"],
    "javascript": ["express-rate-limit", "rate-limiter-flexible",
                   "@upstash/ratelimit", "express-slow-down"],
    "java": ["bucket4j", "resilience4j-ratelimiter"],
    "go": ["golang.org/x/time/rate", "github.com/ulule/limiter",
           "github.com/didip/tollbooth"],
    "ruby": ["rack-attack", "rack-throttle"],
    "csharp": ["AspNetCoreRateLimit"],
    "elixir": ["hammer", "ex_rated"],
    "rust": ["tower-governor"],
}

CORS_LIBS = {
    "python": ["django-cors-headers", "flask-cors"],
    "javascript": ["cors"],
    "ruby": ["rack-cors"],
    "php": ["fruitcake/laravel-cors"],
    "elixir": ["cors_plug"],
}

SANITIZATION_LIBS = {
    "javascript": ["dompurify", "sanitize-html", "xss",
                   "isomorphic-dompurify", "he"],
    "python": ["bleach", "nh3"],
    "java": ["owasp-java-html-sanitizer", "owasp-java-encoder"],
    "ruby": ["sanitize", "loofah"],
    "php": ["htmlpurifier"],
}

STRUCTURED_LOGGING_LIBS = {
    "python": ["structlog", "python-json-logger"],
    "javascript": ["winston", "pino", "bunyan"],
    "java": ["logstash-logback-encoder"],
    "go": ["go.uber.org/zap", "github.com/rs/zerolog",
           "github.com/sirupsen/logrus"],
    "ruby": ["lograge", "semantic_logger"],
    "csharp": ["Serilog"],
    "elixir": ["logger_json"],
    "rust": ["tracing", "tracing-subscriber"],
}

ORM_LIBS = {
    "python": ["sqlalchemy", "peewee", "tortoise-orm"],
    "javascript": ["sequelize", "typeorm", "prisma", "@prisma/client",
                   "knex", "mongoose", "drizzle-orm", "objection"],
    "java": ["spring-boot-starter-data-jpa", "hibernate-core", "mybatis"],
    "go": ["gorm.io/gorm", "github.com/jmoiron/sqlx", "entgo.io/ent"],
    "ruby": ["sequel"],  # ActiveRecord built-in
    "php": ["doctrine/orm"],  # Eloquent built-in with Laravel
    "csharp": ["Microsoft.EntityFrameworkCore"],
    "rust": ["diesel", "sqlx", "sea-orm"],
    "elixir": [],  # Ecto built-in
}

FILE_UPLOAD_LIBS = {
    "javascript": ["multer", "busboy", "formidable"],
    "ruby": ["carrierwave", "shrine"],
}

# Maps ecosystem to manifest file basenames
MANIFEST_FILES = {
    "python": ["requirements.txt", "requirements-dev.txt", "requirements-test.txt",
               "pyproject.toml", "setup.py", "setup.cfg", "Pipfile"],
    "javascript": ["package.json"],
    "java": ["pom.xml", "build.gradle", "build.gradle.kts"],
    "go": ["go.mod"],
    "ruby": ["Gemfile"],
    "php": ["composer.json"],
    "elixir": ["mix.exs"],
    "csharp": [],  # handled separately via *.csproj
    "rust": ["Cargo.toml"],
    "dart": ["pubspec.yaml"],
    "scala": ["build.sbt"],
    "swift": ["Package.swift"],
}

# Language detection name -> ecosystem key mapping
LANG_TO_ECOSYSTEM = {
    "Python": "python",
    "JavaScript": "javascript", "TypeScript": "javascript",
    "JavaScript (React)": "javascript", "TypeScript (React)": "javascript",
    "JavaScript/TypeScript": "javascript",
    "Java": "java", "Kotlin": "java", "Java/Kotlin": "java",
    "Go": "go",
    "Ruby": "ruby",
    "PHP": "php",
    "Elixir": "elixir",
    "C#": "csharp",
    "Rust": "rust",
    "Dart": "dart",
    "Scala": "scala",
    "Swift": "swift",
}


# ---------------------------------------------------------------------------
# Unsafe code patterns (compiled regexes)
# ---------------------------------------------------------------------------

UNSAFE_FUNCTION_PATTERNS = [
    # Python
    ("python_eval", re.compile(r'\beval\s*\('), [".py"]),
    ("python_exec", re.compile(r'\bexec\s*\('), [".py"]),
    ("python_pickle_load", re.compile(r'pickle\.loads?\s*\('), [".py"]),
    ("python_yaml_unsafe", re.compile(r'yaml\.load\s*\([^)]*(?!Loader\s*=\s*SafeLoader)'), [".py"]),
    ("python_os_system", re.compile(r'os\.system\s*\('), [".py"]),
    ("python_shell_true", re.compile(r'subprocess\.\w+\([^)]*shell\s*=\s*True'), [".py"]),
    # JavaScript / TypeScript
    ("js_eval", re.compile(r'\beval\s*\('), [".js", ".ts", ".jsx", ".tsx", ".mjs"]),
    ("js_new_function", re.compile(r'new\s+Function\s*\('), [".js", ".ts", ".jsx", ".tsx"]),
    ("js_dangerously_set", re.compile(r'dangerouslySetInnerHTML'), [".js", ".ts", ".jsx", ".tsx"]),
    ("js_innerhtml", re.compile(r'\.innerHTML\s*='), [".js", ".ts", ".jsx", ".tsx"]),
    ("js_document_write", re.compile(r'document\.write\s*\('), [".js", ".ts", ".jsx", ".tsx"]),
    ("js_child_process_exec", re.compile(r'child_process\.exec\s*\('), [".js", ".ts"]),
    # Java / Kotlin
    ("java_runtime_exec", re.compile(r'Runtime\.getRuntime\(\)\.exec\s*\('), [".java", ".kt"]),
    ("java_deserialize", re.compile(r'ObjectInputStream.*readObject\s*\('), [".java", ".kt"]),
    # Go
    ("go_exec_command", re.compile(r'exec\.Command\s*\('), [".go"]),
    # Ruby
    ("ruby_eval", re.compile(r'\beval\s*[\s(]'), [".rb"]),
    ("ruby_html_safe", re.compile(r'\.html_safe\b'), [".rb", ".erb"]),
    ("ruby_raw", re.compile(r'\braw\s*\('), [".rb", ".erb"]),
    ("ruby_constantize", re.compile(r'\.constantize\b'), [".rb"]),
    # PHP
    ("php_eval", re.compile(r'\beval\s*\('), [".php"]),
    ("php_unserialize", re.compile(r'\bunserialize\s*\('), [".php"]),
    # Elixir
    ("elixir_eval_string", re.compile(r'Code\.eval_string\s*\('), [".ex", ".exs"]),
    ("elixir_binary_to_term", re.compile(r':erlang\.binary_to_term\s*\('), [".ex", ".exs"]),
    ("elixir_raw", re.compile(r'\braw\s*\('), [".ex", ".heex", ".leex"]),
    # C#
    ("csharp_process_start", re.compile(r'Process\.Start\s*\('), [".cs"]),
    # Rust
    ("rust_command_new", re.compile(r'Command::new\s*\('), [".rs"]),
    # Template XSS patterns
    ("django_autoescape_off", re.compile(r'\{%\s*autoescape\s+off\s*%\}'), [".html", ".djhtml"]),
    ("django_safe_filter", re.compile(r'\|\s*safe\b'), [".html", ".djhtml"]),
    ("blade_raw", re.compile(r'\{!!\s*.*\s*!!\}'), [".blade.php"]),
    ("twig_raw", re.compile(r'\|\s*raw\b'), [".twig"]),
    ("razor_html_raw", re.compile(r'@Html\.Raw\s*\('), [".cshtml", ".razor"]),
    ("thymeleaf_utext", re.compile(r'th:utext'), [".html"]),
]

RAW_SQL_PATTERNS = [
    ("python_raw_sql", re.compile(
        r'''(?:\.raw|cursor\.execute|\.execute)\s*\(\s*(?:f['""]|['""].*\+|.*\.format\s*\().*(?:SELECT|INSERT|UPDATE|DELETE)''',
        re.IGNORECASE), [".py"]),
    ("js_raw_sql", re.compile(
        r'''(?:\.query|\.execute)\s*\(\s*(?:`.*\$\{|['""].*\+).*(?:SELECT|INSERT|UPDATE|DELETE)''',
        re.IGNORECASE), [".js", ".ts"]),
    ("java_raw_sql", re.compile(
        r'''(?:Statement\.execute|\.createQuery)\s*\(\s*['""].*\+.*(?:SELECT|INSERT|UPDATE|DELETE)''',
        re.IGNORECASE), [".java", ".kt"]),
    ("go_raw_sql", re.compile(
        r'''(?:db\.Query|db\.Exec)\s*\(\s*fmt\.Sprintf\s*\(''',
        re.IGNORECASE), [".go"]),
    ("ruby_raw_sql", re.compile(
        r'''(?:where|find_by_sql)\s*\(\s*['""].*#\{''',
        re.IGNORECASE), [".rb"]),
    ("php_raw_sql", re.compile(
        r'''(?:DB::select|->query)\s*\(\s*['""].*\$''',
        re.IGNORECASE), [".php"]),
    ("csharp_raw_sql", re.compile(
        r'''(?:FromSqlRaw|ExecuteSqlRaw)\s*\(\s*['""].*\+''',
        re.IGNORECASE), [".cs"]),
    ("elixir_raw_sql", re.compile(
        r'''SQL\.query!\s*\(.*<>''',
        re.IGNORECASE), [".ex", ".exs"]),
]

DEPRECATED_CRYPTO_PATTERNS = [
    ("python_md5_password", re.compile(r'hashlib\.md5\s*\('), [".py"]),
    ("python_sha1_password", re.compile(r'hashlib\.sha1\s*\('), [".py"]),
    ("js_md5_hash", re.compile(r'''createHash\s*\(\s*['"]md5['"]\s*\)'''), [".js", ".ts"]),
    ("js_sha1_hash", re.compile(r'''createHash\s*\(\s*['"]sha1['"]\s*\)'''), [".js", ".ts"]),
    ("js_math_random_token", re.compile(r'Math\.random\s*\(\s*\).*(?:token|key|secret|session|nonce)', re.IGNORECASE),
     [".js", ".ts"]),
    ("java_md5", re.compile(r'''MessageDigest\.getInstance\s*\(\s*['"]MD5['"]\s*\)'''), [".java", ".kt"]),
    ("java_sha1", re.compile(r'''MessageDigest\.getInstance\s*\(\s*['"]SHA-?1['"]\s*\)'''), [".java", ".kt"]),
    ("java_ecb", re.compile(r'''Cipher\.getInstance\s*\(\s*['"]AES/ECB/'''), [".java", ".kt"]),
    ("go_md5_password", re.compile(r'md5\.New\s*\(\s*\)'), [".go"]),
    ("go_math_rand_token", re.compile(r'math/rand.*(?:token|key|secret)', re.IGNORECASE), [".go"]),
    ("ruby_md5", re.compile(r'Digest::MD5'), [".rb"]),
    ("php_md5_password", re.compile(r'\bmd5\s*\(\s*\$.*(?:password|passwd|pwd)', re.IGNORECASE), [".php"]),
    ("php_sha1_password", re.compile(r'\bsha1\s*\(\s*\$.*(?:password|passwd|pwd)', re.IGNORECASE), [".php"]),
    ("csharp_md5", re.compile(r'MD5CryptoServiceProvider|MD5\.Create'), [".cs"]),
    ("csharp_sha1", re.compile(r'SHA1Managed|SHA1\.Create'), [".cs"]),
]

INSECURE_CORS_PATTERNS = [
    # Wildcard origin with credentials
    ("django_cors_all", re.compile(r'CORS_ALLOW_ALL_ORIGINS\s*=\s*True'), [".py"]),
    ("express_cors_star", re.compile(r'''origin\s*:\s*['"][*]['"]'''), [".js", ".ts"]),
    ("express_cors_star2", re.compile(r'''origin\s*:\s*true'''), [".js", ".ts"]),
    ("spring_cors_star", re.compile(r'''allowedOrigins\s*\(\s*['"][*]['"]\s*\)'''), [".java", ".kt"]),
    ("csharp_cors_any", re.compile(r'AllowAnyOrigin\s*\(\s*\).*AllowCredentials|AllowCredentials.*AllowAnyOrigin'), [".cs"]),
    ("go_cors_star", re.compile(r'''AllowedOrigins.*\*'''), [".go"]),
    ("ruby_cors_star", re.compile(r'''origins\s+['"][*]['"]'''), [".rb"]),
]

INSECURE_CONFIG_PATTERNS = [
    # Django
    ("django_debug_true", re.compile(r'^\s*DEBUG\s*=\s*True', re.MULTILINE), ["settings.py"]),
    ("django_allowed_hosts_star", re.compile(r'''ALLOWED_HOSTS\s*=\s*\[['"][*]['"]\]'''), ["settings.py"]),
    ("django_session_not_secure", re.compile(r'SESSION_COOKIE_SECURE\s*=\s*False'), ["settings.py"]),
    # Spring
    ("spring_debug", re.compile(r'debug\s*[:=]\s*true', re.IGNORECASE),
     ["application.yml", "application.yaml", "application.properties"]),
]

# SBOM tool names to search for in CI configs
SBOM_TOOL_PATTERNS = [
    "cyclonedx", "syft", "sbom-tool", "GenerateSBOM", "trivy sbom",
    "cyclonedx-py", "cyclonedx-npm", "cyclonedx-bom",
    "cyclonedx-maven-plugin", "org.cyclonedx.bom",
    "cyclonedx-gomod", "cargo-cyclonedx",
    "Microsoft.Sbom.Targets", "spdx",
]

SBOM_DEPENDENCY_PATTERNS = {
    "java_maven": ["org.cyclonedx:cyclonedx-maven-plugin"],
    "java_gradle": ["org.cyclonedx.bom"],
    "csharp": ["Microsoft.Sbom.Targets", "CycloneDX"],
}

# Manifest content for CSRF protection evidence
CSRF_PATTERNS = {
    "django": [
        (re.compile(r'django\.middleware\.csrf\.CsrfViewMiddleware'), ["settings.py"]),
    ],
    "rails": [
        (re.compile(r'protect_from_forgery'), [".rb"]),
    ],
    "laravel": [
        (re.compile(r'VerifyCsrfToken'), [".php"]),
    ],
    "phoenix": [
        (re.compile(r'Plug\.CSRFProtection|protect_from_forgery'), [".ex", ".exs"]),
    ],
    "spring": [
        # Spring Security enables CSRF by default; disabling it is a red flag
        (re.compile(r'csrf\(\)\.disable\(\)|csrf\s*\{\s*disable'), [".java", ".kt"]),
    ],
}


# ---------------------------------------------------------------------------
# Scanning functions
# ---------------------------------------------------------------------------

def _read_file_safe(path: Path, max_size: int = 500_000) -> str | None:
    """Read a file safely, returning None if unreadable or too large."""
    try:
        if not path.is_file():
            return None
        if path.stat().st_size > max_size:
            return None
        return path.read_text(encoding="utf-8", errors="replace")
    except (OSError, PermissionError):
        return None


def _find_manifest_files(repo_root: Path, file_index: dict,
                         ecosystem: str) -> list[Path]:
    """Find manifest files for an ecosystem."""
    patterns = MANIFEST_FILES.get(ecosystem, [])
    results = []
    for fpath in file_index["files"]:
        fname = os.path.basename(fpath).lower()
        for pattern in patterns:
            if fname == pattern.lower():
                results.append(repo_root / fpath)
                break
    # Handle csproj specially
    if ecosystem == "csharp":
        for fpath in file_index["files"]:
            if fpath.lower().endswith(".csproj"):
                results.append(repo_root / fpath)
    return results


def _scan_manifests_for_libs(repo_root: Path, file_index: dict,
                             ecosystem: str, libs: list[str]) -> list[str]:
    """Scan manifests of an ecosystem for specific library names."""
    if not libs:
        return []
    manifests = _find_manifest_files(repo_root, file_index, ecosystem)
    found = []
    for manifest_path in manifests:
        content = _read_file_safe(manifest_path)
        if not content:
            continue
        content_lower = content.lower()
        for lib in libs:
            if lib.lower() in content_lower:
                found.append(lib)
    return sorted(set(found))


def scan_secure_coding_deps(repo_root: Path, file_index: dict,
                            detected_languages: list[str]) -> dict:
    """Scan dependency manifests for secure coding practice evidence.
    
    Returns a dict with per-category findings.
    """
    # Map detected languages to ecosystem keys
    ecosystems = set()
    for lang in detected_languages:
        eco = LANG_TO_ECOSYSTEM.get(lang)
        if eco:
            ecosystems.add(eco)

    categories = {
        "input_validation": INPUT_VALIDATION_LIBS,
        "authentication": AUTH_LIBS,
        "password_hashing": PASSWORD_HASHING_LIBS,
        "security_headers": SECURITY_HEADER_LIBS,
        "rate_limiting": RATE_LIMIT_LIBS,
        "cors": CORS_LIBS,
        "sanitization": SANITIZATION_LIBS,
        "structured_logging": STRUCTURED_LOGGING_LIBS,
        "orm": ORM_LIBS,
        "file_upload": FILE_UPLOAD_LIBS,
    }

    results = {}
    for category_name, lib_map in categories.items():
        category_results = {}
        for eco in ecosystems:
            libs = lib_map.get(eco, [])
            if libs:
                found = _scan_manifests_for_libs(repo_root, file_index, eco, libs)
                if found:
                    category_results[eco] = found
        results[category_name] = category_results

    return results


def scan_source_patterns(repo_root: Path, file_index: dict,
                         max_files: int = 800) -> dict:
    """Scan source files for unsafe code patterns."""
    skip_dirs = {"node_modules", "vendor", ".git", "__pycache__", "dist",
                 "build", ".next", ".nuxt", "target", "venv", ".venv"}
    skip_exts = {".lock", ".min.js", ".min.css", ".map", ".sum",
                 ".png", ".jpg", ".gif", ".svg", ".ico", ".woff", ".woff2",
                 ".ttf", ".eot", ".pdf", ".zip", ".tar", ".gz"}

    findings = {
        "unsafe_functions": [],
        "raw_sql": [],
        "deprecated_crypto": [],
        "insecure_cors": [],
        "insecure_config": [],
        "xss_template_escapes": [],
    }

    scanned = 0
    for fpath in file_index["files"]:
        if scanned >= max_files:
            break

        # Skip irrelevant paths
        parts = fpath.split(os.sep)
        if any(p in skip_dirs for p in parts):
            continue

        ext = os.path.splitext(fpath)[1].lower()
        if ext in skip_exts:
            continue

        full_path = repo_root / fpath
        if not full_path.is_file():
            continue

        try:
            size = full_path.stat().st_size
            if size > 300_000:
                continue
        except OSError:
            continue

        content = _read_file_safe(full_path)
        if not content:
            continue

        scanned += 1
        fname = os.path.basename(fpath).lower()

        # Check each pattern category
        for pattern_name, pattern, file_exts in UNSAFE_FUNCTION_PATTERNS:
            if ext in file_exts or fname in [e.lstrip('.') for e in file_exts]:
                for line_no, line in enumerate(content.splitlines(), 1):
                    if pattern.search(line):
                        # Determine if it's a template XSS pattern
                        category = "xss_template_escapes" if pattern_name in (
                            "django_autoescape_off", "django_safe_filter",
                            "blade_raw", "twig_raw", "razor_html_raw",
                            "thymeleaf_utext", "js_dangerously_set",
                            "js_innerhtml", "js_document_write",
                            "ruby_html_safe", "ruby_raw", "elixir_raw"
                        ) else "unsafe_functions"
                        findings[category].append({
                            "file": fpath,
                            "line": line_no,
                            "pattern": pattern_name,
                            "snippet": line.strip()[:120],
                        })

        for pattern_name, pattern, file_exts in RAW_SQL_PATTERNS:
            if ext in file_exts:
                for line_no, line in enumerate(content.splitlines(), 1):
                    if pattern.search(line):
                        findings["raw_sql"].append({
                            "file": fpath,
                            "line": line_no,
                            "pattern": pattern_name,
                            "snippet": line.strip()[:120],
                        })

        for pattern_name, pattern, file_exts in DEPRECATED_CRYPTO_PATTERNS:
            if ext in file_exts:
                for line_no, line in enumerate(content.splitlines(), 1):
                    if pattern.search(line):
                        findings["deprecated_crypto"].append({
                            "file": fpath,
                            "line": line_no,
                            "pattern": pattern_name,
                            "snippet": line.strip()[:120],
                        })

        for pattern_name, pattern, file_exts in INSECURE_CORS_PATTERNS:
            if ext in file_exts:
                for line_no, line in enumerate(content.splitlines(), 1):
                    if pattern.search(line):
                        findings["insecure_cors"].append({
                            "file": fpath,
                            "line": line_no,
                            "pattern": pattern_name,
                            "snippet": line.strip()[:120],
                        })

        for pattern_name, pattern, file_matches in INSECURE_CONFIG_PATTERNS:
            if fname in [f.lower() for f in file_matches]:
                for match in pattern.finditer(content):
                    line_no = content[:match.start()].count('\n') + 1
                    findings["insecure_config"].append({
                        "file": fpath,
                        "line": line_no,
                        "pattern": pattern_name,
                        "snippet": match.group(0).strip()[:120],
                    })

    return findings


def check_sbom_tooling(repo_root: Path, file_index: dict,
                       ci_content: str = "") -> dict:
    """Check for SBOM generation tooling in CI configs and dependencies."""
    evidence = {
        "in_ci": [],
        "in_dependencies": [],
    }

    # Check CI content
    ci_lower = ci_content.lower()
    for tool in SBOM_TOOL_PATTERNS:
        if tool.lower() in ci_lower:
            evidence["in_ci"].append(tool)

    # Check dependency manifests for SBOM plugins
    for eco, dep_patterns in SBOM_DEPENDENCY_PATTERNS.items():
        for fpath in file_index["files"]:
            fname = os.path.basename(fpath).lower()
            if eco == "java_maven" and fname == "pom.xml":
                content = _read_file_safe(repo_root / fpath)
                if content:
                    for dep in dep_patterns:
                        if dep.lower() in content.lower():
                            evidence["in_dependencies"].append(
                                f"{fpath}: {dep}")
            elif eco == "java_gradle" and fname in ("build.gradle", "build.gradle.kts"):
                content = _read_file_safe(repo_root / fpath)
                if content:
                    for dep in dep_patterns:
                        if dep.lower() in content.lower():
                            evidence["in_dependencies"].append(
                                f"{fpath}: {dep}")
            elif eco == "csharp" and fname.endswith(".csproj"):
                content = _read_file_safe(repo_root / fpath)
                if content:
                    for dep in dep_patterns:
                        if dep.lower() in content.lower():
                            evidence["in_dependencies"].append(
                                f"{fpath}: {dep}")

    return evidence


def scan_csrf_evidence(repo_root: Path, file_index: dict) -> dict:
    """Check for CSRF protection configuration."""
    evidence = {"found": [], "disabled": []}

    for framework, patterns in CSRF_PATTERNS.items():
        for pattern, file_matches in patterns:
            for fpath in file_index["files"]:
                fname = os.path.basename(fpath).lower()
                ext = os.path.splitext(fpath)[1].lower()
                match = False
                for fm in file_matches:
                    if fm.startswith("."):
                        if ext == fm:
                            match = True
                    elif fname == fm.lower():
                        match = True
                if not match:
                    continue

                content = _read_file_safe(repo_root / fpath)
                if not content:
                    continue

                if pattern.search(content):
                    if framework == "spring" and "disable" in pattern.pattern:
                        evidence["disabled"].append({
                            "framework": framework,
                            "file": fpath,
                        })
                    else:
                        evidence["found"].append({
                            "framework": framework,
                            "file": fpath,
                        })
    return evidence


def run_secure_coding_scan(repo_root: Path, file_index: dict,
                           detected_languages: list[str],
                           ci_content: str = "") -> dict:
    """Run all secure coding practice scans and return combined evidence."""
    results = {}

    results["secure_coding_deps"] = scan_secure_coding_deps(
        repo_root, file_index, detected_languages)

    results["source_patterns"] = scan_source_patterns(repo_root, file_index)

    results["sbom_tooling"] = check_sbom_tooling(
        repo_root, file_index, ci_content)

    results["csrf_evidence"] = scan_csrf_evidence(repo_root, file_index)

    return results
