# Secure Coding Patterns — Per-Language Reference

This file maps concrete libraries, config locations, and code patterns to
ISO 27001:2022 A.8.28 secure coding evidence. Used by the scan script for
dependency-based detection and by Claude for scoring and fix suggestions.

## Table of Contents

1. [Dependency Evidence Maps](#dependency-evidence-maps)
2. [Unsafe Code Patterns](#unsafe-code-patterns)
3. [Insecure Config Patterns](#insecure-config-patterns)
4. [SBOM Tooling](#sbom-tooling)

---

## Dependency Evidence Maps

Each category lists package names to search for in dependency manifests.
The scan script checks these against detected languages.

### Input Validation Frameworks

| Ecosystem | Packages (presence = positive evidence) | Manifest file |
|---|---|---|
| Python (Django) | `django` (built-in forms/serializers), `djangorestframework` | requirements*.txt, pyproject.toml, Pipfile |
| Python (Flask) | `marshmallow`, `webargs`, `pydantic`, `flask-wtf`, `wtforms` | requirements*.txt, pyproject.toml |
| Python (FastAPI) | `pydantic` (core to FastAPI), `fastapi` | requirements*.txt, pyproject.toml |
| JavaScript/TS | `express-validator`, `joi`, `@hapi/joi`, `zod`, `yup`, `class-validator`, `ajv`, `superstruct`, `io-ts`, `valibot` | package.json |
| Java/Kotlin | `spring-boot-starter-validation`, `hibernate-validator`, `jakarta.validation` | pom.xml, build.gradle, build.gradle.kts |
| Go | `github.com/go-playground/validator` | go.mod |
| Ruby | (ActiveModel built-in with Rails) | Gemfile |
| PHP (Laravel) | (built-in `$request->validate`), `respect/validation` | composer.json |
| PHP (Symfony) | `symfony/validator` | composer.json |
| Elixir | (Ecto changesets built-in with Phoenix) | mix.exs |
| C#/.NET | `FluentValidation`, `System.ComponentModel.DataAnnotations` (built-in) | *.csproj, packages.config |
| Rust | `validator` | Cargo.toml |
| Dart | `form_field_validator` | pubspec.yaml |
| Scala | (Play forms built-in) | build.sbt |
| Swift (Vapor) | `vapor` (built-in Validations API) | Package.swift |

### Authentication Frameworks

| Ecosystem | Packages | Manifest |
|---|---|---|
| Python (Django) | `django-allauth`, `djangorestframework-simplejwt`, `django-oauth-toolkit`, `social-auth-app-django` | requirements*.txt, pyproject.toml |
| Python (Flask) | `flask-login`, `flask-security-too`, `flask-jwt-extended`, `authlib` | requirements*.txt, pyproject.toml |
| JavaScript/TS | `passport`, `next-auth`, `@auth/core`, `express-session`, `jsonwebtoken`, `jose` | package.json |
| Java/Kotlin | `spring-boot-starter-security`, `spring-boot-starter-oauth2-client` | pom.xml, build.gradle |
| Go | `github.com/golang-jwt/jwt`, `github.com/coreos/go-oidc`, `github.com/markbates/goth` | go.mod |
| Ruby | `devise`, `omniauth`, `sorcery`, `rodauth` | Gemfile |
| PHP (Laravel) | `laravel/passport`, `laravel/sanctum`, `laravel/fortify`, `laravel/breeze` | composer.json |
| PHP (Symfony) | `lexik/jwt-authentication-bundle`, `symfony/security-bundle` | composer.json |
| Elixir | `guardian`, `pow`, `ueberauth`, `phx_gen_auth` | mix.exs |
| C#/.NET | `Microsoft.AspNetCore.Identity`, `Microsoft.AspNetCore.Authentication.JwtBearer` | *.csproj |
| Rust | `actix-web-httpauth`, `jsonwebtoken` | Cargo.toml |
| Scala | `play-silhouette`, `pac4j` | build.sbt |

### Cryptography — Compliant Password Hashing

| Ecosystem | Packages (positive evidence) |
|---|---|
| Python | `bcrypt`, `argon2-cffi`, `passlib`, `django.contrib.auth.hashers` (built-in PBKDF2) |
| JavaScript/TS | `bcrypt`, `bcryptjs`, `argon2`, `scrypt` |
| Java/Kotlin | Spring Security `BCryptPasswordEncoder`, `Argon2PasswordEncoder`, `Pbkdf2PasswordEncoder` (built-in) |
| Go | `golang.org/x/crypto/bcrypt`, `golang.org/x/crypto/argon2` |
| Ruby | `bcrypt`, `argon2`, `scrypt` |
| PHP | `password_hash()` (built-in BCRYPT/ARGON2) |
| Elixir | `bcrypt_elixir`, `argon2_elixir`, `pbkdf2_elixir`, `comeonin` |
| C#/.NET | `Microsoft.AspNetCore.Identity` (built-in PBKDF2), `BCrypt.Net-Next`, `Isopoh.Cryptography.Argon2` |
| Rust | `bcrypt`, `argon2`, `rust-argon2` |

### Security HTTP Headers Middleware

| Ecosystem | Packages / Config (positive evidence) |
|---|---|
| Python (Django) | `django.middleware.security.SecurityMiddleware` in MIDDLEWARE + `SECURE_HSTS_SECONDS`, `django-csp` |
| Python (Flask) | `flask-talisman`, `secure` |
| JavaScript/TS (Express) | `helmet` |
| JavaScript/TS (Next.js) | `headers()` in `next.config.js` with CSP/HSTS |
| Java/Kotlin (Spring) | Spring Security auto-sets headers; `http.headers()` config blocks |
| Go | Manual middleware or framework-specific; check for `Content-Security-Policy` header sets |
| Ruby (Rails) | `secure_headers` gem, built-in `config.action_dispatch.default_headers` |
| PHP (Laravel) | Custom middleware in `app/Http/Middleware`, security header packages |
| Elixir (Phoenix) | `put_secure_browser_headers` plug in router pipelines |
| C#/.NET | `app.UseHsts()`, `NetEscapades.AspNetCore.SecurityHeaders` |

### Rate Limiting

| Ecosystem | Packages |
|---|---|
| Python (Django) | `django-ratelimit` |
| Python (Flask/FastAPI) | `flask-limiter`, `slowapi` |
| JavaScript/TS | `express-rate-limit`, `rate-limiter-flexible`, `@upstash/ratelimit` |
| Java/Kotlin | `bucket4j`, `resilience4j-ratelimiter` |
| Go | `golang.org/x/time/rate`, `github.com/ulule/limiter`, `github.com/didip/tollbooth` |
| Ruby | `rack-attack`, `rack-throttle` |
| PHP (Laravel) | Built-in `ThrottleRequests` middleware |
| Elixir | `hammer`, `ex_rated` |
| C#/.NET | Built-in `app.UseRateLimiter()` (.NET 7+), `AspNetCoreRateLimit` |
| Rust | `tower-governor` |

### CORS Libraries

| Ecosystem | Packages |
|---|---|
| Python (Django) | `django-cors-headers` |
| Python (Flask) | `flask-cors` |
| Python (FastAPI) | `fastapi.middleware.cors.CORSMiddleware` (built-in) |
| JavaScript/TS | `cors` |
| Java/Kotlin (Spring) | Built-in `@CrossOrigin`, `WebMvcConfigurer.addCorsMappings` |
| Go | `github.com/rs/cors` |
| Ruby | `rack-cors` |
| PHP (Laravel) | Built-in or `fruitcake/laravel-cors` |
| Elixir | `cors_plug` |
| C#/.NET | Built-in `builder.Services.AddCors` |
| Rust | Framework-specific CORS middleware |

### Structured Logging

| Ecosystem | Packages (positive evidence) |
|---|---|
| Python | `structlog`, `python-json-logger` |
| JavaScript/TS | `winston`, `pino`, `bunyan` |
| Java/Kotlin | `logstash-logback-encoder`, `log4j2` JSON layout |
| Go | `go.uber.org/zap`, `github.com/rs/zerolog`, `github.com/sirupsen/logrus` |
| Ruby | `lograge`, `semantic_logger` |
| PHP | (Laravel logging built-in), `monolog` JSON formatter |
| Elixir | `logger_json` |
| C#/.NET | `Serilog`, `Serilog.Sinks.Console` |
| Rust | `tracing`, `tracing-subscriber` |

### Output Encoding / Sanitization Libraries

| Ecosystem | Packages (positive evidence) |
|---|---|
| JavaScript/TS | `dompurify`, `sanitize-html`, `xss`, `isomorphic-dompurify`, `he` |
| Python | `bleach`, `nh3` |
| Java | `owasp-java-html-sanitizer`, `owasp-java-encoder` |
| Ruby | `sanitize`, `loofah` |
| PHP | `htmlpurifier` |

### ORM / Query Builder Libraries

| Ecosystem | Packages (positive evidence for parameterized queries) |
|---|---|
| Python | `sqlalchemy`, `django` (built-in ORM), `peewee`, `tortoise-orm` |
| JavaScript/TS | `sequelize`, `typeorm`, `prisma`, `@prisma/client`, `knex`, `mongoose`, `drizzle-orm` |
| Java/Kotlin | `spring-boot-starter-data-jpa`, `hibernate`, `mybatis` |
| Go | `gorm.io/gorm`, `github.com/jmoiron/sqlx`, `entgo.io/ent` |
| Ruby | `activerecord` (built-in with Rails), `sequel` |
| PHP | `doctrine/orm` (Symfony), `illuminate/database` (Laravel Eloquent built-in) |
| Elixir | `ecto` (built-in with Phoenix) |
| C#/.NET | `Microsoft.EntityFrameworkCore` |
| Rust | `diesel`, `sqlx`, `sea-orm` |
| Scala | `slick`, `anorm` (Play built-in) |

---

## Unsafe Code Patterns

These patterns should be flagged when found in source files.
Organized by category, then by language-specific variants.

### Unsafe Functions / Code Execution

| Language | Patterns to flag |
|---|---|
| Python | `eval(`, `exec(`, `compile(`, `pickle.load(`, `pickle.loads(`, `yaml.load(` without `Loader=SafeLoader`, `subprocess.Popen(` with `shell=True` + user input, `os.system(` |
| JavaScript/TS | `eval(`, `new Function(`, `setTimeout(userStr`, `setInterval(userStr`, `child_process.exec(` with unsanitized args |
| Java/Kotlin | `Runtime.getRuntime().exec(`, `ProcessBuilder` with request params, `ObjectInputStream.readObject(` on untrusted streams |
| Go | `exec.Command(` / `exec.CommandContext(` with user-controlled args |
| Ruby | `eval`, `class_eval`, `instance_eval`, `send(` on user input, `.constantize` on user strings |
| PHP | `eval(`, `preg_replace` with `/e` modifier, `unserialize(` on untrusted data, dynamic `include`/`require` paths |
| Elixir | `Code.eval_string(`, `:erlang.binary_to_term(` with untrusted data |
| C#/.NET | `Process.Start(` with user input, dynamic compilation, `DataTable.Select("... " + userInput)` |
| Rust | `Command::new(` with user input, unguarded `unsafe` blocks with raw pointers |
| Swift | `NSExpression`/`NSPredicate` with untrusted strings, `Process()`/`system()` from user input |

### Unsafe Template / Output Patterns (XSS vectors)

| Language/Framework | Patterns to flag |
|---|---|
| Python (Django) | `{% autoescape off %}`, `\|safe` filter, `mark_safe(` with user input |
| Python (Jinja2) | `\|safe` filter, `Markup(` with user input |
| JavaScript (React) | `dangerouslySetInnerHTML` |
| JavaScript (DOM) | `innerHTML`, `outerHTML`, `document.write(` with user data |
| JavaScript (templates) | `{{{` in Handlebars (triple-stache = raw), `<%- %>` in EJS (unescaped) |
| Java (Thymeleaf) | `th:utext` (unescaped text) |
| Ruby (Rails) | `.html_safe`, `raw(`, `<%== %>` |
| PHP (Blade) | `{!! ... !!}` |
| PHP (Twig) | `\|raw` filter |
| Elixir (Phoenix) | `raw(` in templates |
| C# (Razor) | `@Html.Raw(` |
| Rust (Tera/Askama) | `\|safe` filter |

### Raw SQL Concatenation Patterns

| Language | Patterns to flag |
|---|---|
| Python | `.raw("SELECT ... " + `, `cursor.execute("SELECT ... " + `, `f"SELECT ... {` |
| JavaScript/TS | `` `SELECT ... ${userInput}` ``, `.query("SELECT ... " + ` |
| Java/Kotlin | `Statement.execute("... " + `, `@Query("... " + `, JPQL/HQL string concat |
| Go | `db.Query(fmt.Sprintf("SELECT ... %s"`, `"SELECT ... " + id` |
| Ruby | `where("name = '#{params[`, `find_by_sql("... " + ` |
| PHP | `DB::select("... $`, `$conn->query("... " . $_GET[` |
| Elixir | `Ecto.Adapters.SQL.query!(..., "SELECT ... " <>` |
| C#/.NET | `FromSqlRaw("... " + `, `ExecuteSqlRaw("... " + ` |

### Deprecated Crypto Patterns

| Language | Patterns to flag |
|---|---|
| Python | `hashlib.md5(` / `hashlib.sha1(` for passwords, manual `AES` with ECB |
| JavaScript/TS | `crypto.createHash('md5')` / `crypto.createHash('sha1')` for passwords, `Math.random()` for tokens |
| Java/Kotlin | `MessageDigest.getInstance("MD5")` / `"SHA1"` for passwords, `Cipher.getInstance("AES/ECB/` |
| Go | `md5.New()` / `sha1.New()` for passwords, `math/rand` for tokens instead of `crypto/rand` |
| Ruby | `Digest::MD5.hexdigest(password)`, `OpenSSL::Cipher.new('AES-128-ECB')` |
| PHP | `md5($password)`, `sha1($password)` |
| Elixir | `:crypto.hash(:md5, ` for passwords |
| C#/.NET | `MD5CryptoServiceProvider`, `SHA1Managed`, `new AesManaged { Mode = CipherMode.ECB }` |

---

## Insecure Config Patterns

Check framework config files for these insecure settings.

### Django (settings.py)

| Setting | Insecure value | Expected secure value |
|---|---|---|
| `DEBUG` | `True` in production | `False` |
| `SESSION_COOKIE_SECURE` | `False` | `True` |
| `SESSION_COOKIE_HTTPONLY` | `False` | `True` |
| `CSRF_COOKIE_SECURE` | `False` | `True` |
| `SECURE_HSTS_SECONDS` | `0` or absent | `> 0` (typically 31536000) |
| `CORS_ALLOW_ALL_ORIGINS` | `True` | `False` with explicit allowlist |
| `ALLOWED_HOSTS` | `['*']` | Explicit hostnames |

### Express / Node.js

| Pattern | Insecure | Secure |
|---|---|---|
| CORS | `origin: '*'` with `credentials: true` | Explicit origin allowlist |
| Session cookie | `secure: false` in production | `secure: true, httpOnly: true, sameSite: 'lax'` |
| Helmet | Absent | `app.use(helmet())` |

### Spring Boot (application.yml / application.properties)

| Setting | Insecure | Secure |
|---|---|---|
| `server.servlet.session.cookie.secure` | `false` | `true` |
| `server.servlet.session.cookie.http-only` | `false` | `true` |
| `server.servlet.session.cookie.same-site` | absent or `none` | `lax` or `strict` |
| CORS | `allowedOrigins("*")` with `allowCredentials(true)` | Explicit origins |

### Laravel (config/session.php)

| Setting | Insecure | Secure |
|---|---|---|
| `secure` | `false` in production | `true` |
| `http_only` | `false` | `true` |
| `same_site` | `null` | `lax` or `strict` |

### Phoenix / Elixir

| Pattern | Insecure | Secure |
|---|---|---|
| Missing `put_secure_browser_headers` in router pipeline | Absent | Present |
| Missing `Plug.CSRFProtection` in browser pipeline | Absent | Present |
| Session config without `secure: true` | Missing flag | `secure: true, http_only: true` |

### ASP.NET / C#

| Pattern | Insecure | Secure |
|---|---|---|
| Cookie options | `Secure = false`, `SameSite = None` without `Secure = true` | `Secure = true, HttpOnly = true, SameSite = Lax` |
| CORS | `AllowAnyOrigin().AllowCredentials()` | Explicit origins |

---

## SBOM Tooling

Evidence that SBOM generation is part of the build/release process.

### Cross-ecosystem tools

| Tool | CI pattern to detect |
|---|---|
| Syft (Anchore) | `syft` command in CI YAML |
| Trivy (SBOM mode) | `trivy sbom` or `trivy fs --format cyclonedx` in CI |
| Microsoft SBOM | `GenerateSBOM` in `.csproj`, `sbom-tool` in CI |

### Per-ecosystem CycloneDX plugins

| Ecosystem | Tool / CI command |
|---|---|
| Python | `cyclonedx-py`, `cyclonedx-bom` in CI |
| JavaScript/TS | `cyclonedx-npm`, `@cyclonedx/bom` in CI or package.json scripts |
| Java/Kotlin (Maven) | `org.cyclonedx:cyclonedx-maven-plugin` in pom.xml |
| Java/Kotlin (Gradle) | `org.cyclonedx.bom` plugin in build.gradle |
| Go | `cyclonedx-gomod` in CI |
| Ruby | CycloneDX Bundler plugin in CI |
| PHP | CycloneDX Composer plugin in CI |
| Elixir | CycloneDX Mix task in CI |
| C#/.NET | `CycloneDX` dotnet tool or `Microsoft.Sbom.Targets` NuGet |
| Rust | Syft or `cargo-cyclonedx` |
