# Serverless Detection Patterns

Patterns for detecting serverless-specific security vulnerabilities including
IAM, event injection, secrets management, and resource configuration.

---

## 1. Overprivileged IAM Policies

**Description**: Serverless functions are granted IAM policies with `Action: *`
or `Resource: *` instead of following the principle of least privilege. A
compromise of any single function grants broad access to cloud resources.

**Search Heuristics**:
- Grep: `Action:\s*['"]?\*['"]?|Effect:\s*Allow.*Action.*\*`
- Grep: `Resource:\s*['"]?\*['"]?` in IAM policy definitions
- Grep: `arn:aws:.*:\*` (wildcard ARN)
- Grep: `AdministratorAccess|PowerUserAccess|FullAccess` (managed policy names)
- Glob: `**/serverless.yml`, `**/template.yaml`, `**/*.tf`, `**/iam/**`

**Language Examples**:

Serverless Framework -- VULNERABLE:
```yaml
provider:
  name: aws
  iam:
    role:
      statements:
        - Effect: Allow
          Action: '*'
          Resource: '*'
```

Serverless Framework -- FIXED:
```yaml
provider:
  name: aws
  iam:
    role:
      statements:
        - Effect: Allow
          Action:
            - dynamodb:GetItem
            - dynamodb:PutItem
          Resource:
            - arn:aws:dynamodb:us-east-1:123456789:table/users
```

AWS SAM (template.yaml) -- VULNERABLE:
```yaml
Resources:
  MyFunction:
    Type: AWS::Serverless::Function
    Properties:
      Policies:
        - Statement:
            - Effect: Allow
              Action: 's3:*'
              Resource: '*'
```

AWS SAM (template.yaml) -- FIXED:
```yaml
Resources:
  MyFunction:
    Type: AWS::Serverless::Function
    Properties:
      Policies:
        - S3ReadPolicy:
            BucketName: !Ref MyBucket
```

Terraform -- VULNERABLE:
```hcl
resource "aws_iam_role_policy" "lambda_policy" {
  policy = jsonencode({
    Statement = [{
      Effect   = "Allow"
      Action   = "*"
      Resource = "*"
    }]
  })
}
```

Terraform -- FIXED:
```hcl
resource "aws_iam_role_policy" "lambda_policy" {
  policy = jsonencode({
    Statement = [{
      Effect   = "Allow"
      Action   = ["dynamodb:GetItem", "dynamodb:PutItem"]
      Resource = [aws_dynamodb_table.users.arn]
    }]
  })
}
```

**Scanner Coverage**: checkov `CKV_AWS_1`, `CKV_AWS_49`; tfsec
`aws-iam-no-policy-wildcards`

**False Positive Guidance**: Development/sandbox environments may intentionally
use broad permissions. Deployment/CI roles may need broader access. Check the
stage/environment context. SAM policy templates (e.g., `DynamoDBCrudPolicy`)
are pre-scoped and not overprivileged.

**Severity Assessment**:
- **critical**: `Action: *` on `Resource: *` in production functions
- **high**: Wildcard actions on specific services (`s3:*`, `dynamodb:*`)
- **medium**: Overly broad but service-scoped permissions
- **low**: Slightly more permissions than strictly needed

---

## 2. Event Data Injection

**Description**: Serverless functions receive event data from many sources
(API Gateway, S3, SQS, SNS, DynamoDB Streams). This data is untrusted and
using it directly in SQL queries, shell commands, or file paths enables
injection attacks identical to web application injection.

**Search Heuristics**:
- Grep: `event\['body|event\['queryString|event\['pathParameters`
- Grep: `event\.Records\[0\]\.s3\.object\.key` (S3 event key)
- Grep: `subprocess|os\.system|exec\(|child_process` near event data
- Grep: `f"SELECT.*{event|f"INSERT.*{event` (SQL with event interpolation)
- Glob: `**/handlers/**`, `**/functions/**`, `**/lambdas/**`

**Language Examples**:

Python (Lambda + API Gateway) -- VULNERABLE:
```python
def handler(event, context):
    body = json.loads(event['body'])
    name = body['name']
    cursor.execute(f"SELECT * FROM users WHERE name = '{name}'")  # SQL injection
```

Python (Lambda + API Gateway) -- FIXED:
```python
def handler(event, context):
    body = json.loads(event['body'])
    name = body['name']
    cursor.execute("SELECT * FROM users WHERE name = %s", (name,))
```

Python (Lambda + S3 event) -- VULNERABLE:
```python
def handler(event, context):
    key = event['Records'][0]['s3']['object']['key']
    os.system(f"convert /tmp/{key} /tmp/output.jpg")  # Command injection via S3 key
```

Python (Lambda + S3 event) -- FIXED:
```python
import shlex, subprocess

def handler(event, context):
    key = event['Records'][0]['s3']['object']['key']
    safe_key = os.path.basename(key)  # Remove path components
    subprocess.run(["convert", f"/tmp/{safe_key}", "/tmp/output.jpg"], check=True)
```

JavaScript (Lambda) -- VULNERABLE:
```javascript
exports.handler = async (event) => {
  const { name } = JSON.parse(event.body);
  const result = await db.query(`SELECT * FROM users WHERE name = '${name}'`);
  return { statusCode: 200, body: JSON.stringify(result) };
};
```

JavaScript (Lambda) -- FIXED:
```javascript
exports.handler = async (event) => {
  const { name } = JSON.parse(event.body);
  const result = await db.query('SELECT * FROM users WHERE name = $1', [name]);
  return { statusCode: 200, body: JSON.stringify(result) };
};
```

Go (Lambda) -- VULNERABLE:
```go
func handler(ctx context.Context, event events.APIGatewayProxyRequest) (events.APIGatewayProxyResponse, error) {
    name := event.QueryStringParameters["name"]
    query := fmt.Sprintf("SELECT * FROM users WHERE name = '%s'", name)
    db.Query(query)  // SQL injection
}
```

Go (Lambda) -- FIXED:
```go
func handler(ctx context.Context, event events.APIGatewayProxyRequest) (events.APIGatewayProxyResponse, error) {
    name := event.QueryStringParameters["name"]
    db.Query("SELECT * FROM users WHERE name = $1", name)
}
```

**Scanner Coverage**: semgrep `python.aws-lambda.security.event-injection`,
semgrep `javascript.aws-lambda.security.sqli-event-body`

**False Positive Guidance**: Event data used for logging or metrics (not in
queries/commands) is not injection. Event data passed to well-typed ORM
methods that use parameterization is safe. Check the sink function.

**Severity Assessment**:
- **critical**: Event data in shell commands or raw SQL (RCE or SQLi)
- **high**: Event data in file paths or dynamic code evaluation
- **medium**: Event data in NoSQL queries without sanitization
- **low**: Event data in log messages (log injection, lower impact)

---

## 3. Secrets in Plain-Text Environment Variables

**Description**: Secrets (API keys, database passwords, encryption keys) are
defined as plain-text values in Infrastructure-as-Code templates. These values
are visible in the IaC files, version control, and the cloud console.

**Search Heuristics**:
- Grep: `(PASSWORD|SECRET|API_KEY|TOKEN|CREDENTIAL).*:.*['"][^'"]{8,}['"]` in YAML/JSON
- Grep: `environment:` section containing secret-like values in serverless configs
- Grep: `Variables:.*PASSWORD|Variables:.*SECRET` in SAM templates
- Grep: `value\s*=\s*"[^"]+"\s*#.*(secret|key|password)` in Terraform
- Glob: `**/serverless.yml`, `**/template.yaml`, `**/*.tf`, `**/function.json`

**Language Examples**:

Serverless Framework -- VULNERABLE:
```yaml
functions:
  api:
    handler: handler.main
    environment:
      DB_PASSWORD: "SuperSecret123"
      API_KEY: "sk_live_EXAMPLE_DO_NOT_USE_1234567890abcdef"
```

Serverless Framework -- FIXED:
```yaml
functions:
  api:
    handler: handler.main
    environment:
      DB_PASSWORD: ${ssm:/prod/db-password}
      API_KEY: ${ssm:/prod/api-key}
```

AWS SAM -- VULNERABLE:
```yaml
Resources:
  MyFunction:
    Type: AWS::Serverless::Function
    Properties:
      Environment:
        Variables:
          JWT_SECRET: "my-hardcoded-jwt-secret-key"
```

AWS SAM -- FIXED:
```yaml
Resources:
  MyFunction:
    Type: AWS::Serverless::Function
    Properties:
      Environment:
        Variables:
          JWT_SECRET: !Sub '{{resolve:secretsmanager:prod/jwt-secret}}'
```

Terraform -- VULNERABLE:
```hcl
resource "aws_lambda_function" "api" {
  environment {
    variables = {
      DB_PASSWORD = "SuperSecret123"
    }
  }
}
```

Terraform -- FIXED:
```hcl
data "aws_secretsmanager_secret_version" "db_password" {
  secret_id = "prod/db-password"
}

resource "aws_lambda_function" "api" {
  environment {
    variables = {
      DB_PASSWORD = data.aws_secretsmanager_secret_version.db_password.secret_string
    }
  }
}
```

**Scanner Coverage**: checkov `CKV_AWS_45`; tfsec `aws-lambda-environment-no-secrets`;
gitleaks/trufflehog scan IaC files

**False Positive Guidance**: Environment variables referencing SSM parameters,
Secrets Manager ARNs, or `!Ref` to other resources are not plain-text secrets.
Non-secret configuration (region, stage, table names) in environment is fine.

**Severity Assessment**:
- **critical**: Production database passwords or API keys in plain-text IaC
- **high**: Any secret-looking value in environment variable definitions
- **medium**: Non-production secrets in IaC files (test/staging)
- **low**: Missing secret management pattern but values are references/ARNs

---

## 4. /tmp Directory Reuse Between Invocations

**Description**: In serverless, the `/tmp` directory persists between warm
invocations of the same function instance. Sensitive data written to `/tmp`
(temporary credentials, user data, decrypted secrets) may be accessible to
subsequent invocations handling different users' requests.

**Search Heuristics**:
- Grep: `/tmp/|tempfile|mktemp|os\.tmpdir|ioutil\.TempFile`
- Grep: `open\(['"]/tmp|fs\.write.*['"]/tmp|os\.Create\(['"]/tmp`
- Grep: `shutil\.rmtree\(['"]/tmp|fs\.unlinkSync|os\.Remove\(['"]/tmp` (cleanup patterns)
- Glob: `**/handlers/**`, `**/functions/**`, `**/lambdas/**`

**Language Examples**:

Python -- VULNERABLE:
```python
def handler(event, context):
    user_data = decrypt(event['body'])
    with open(f"/tmp/user_{event['user_id']}.json", 'w') as f:
        json.dump(user_data, f)  # Persists for next invocation
    process_file(f"/tmp/user_{event['user_id']}.json")
    # No cleanup -- next invocation may read stale data
```

Python -- FIXED:
```python
import tempfile, os

def handler(event, context):
    user_data = decrypt(event['body'])
    fd, path = tempfile.mkstemp(dir='/tmp', suffix='.json')
    try:
        with os.fdopen(fd, 'w') as f:
            json.dump(user_data, f)
        process_file(path)
    finally:
        os.unlink(path)  # Always clean up
```

JavaScript -- VULNERABLE:
```javascript
exports.handler = async (event) => {
  const data = decrypt(event.body);
  fs.writeFileSync(`/tmp/${event.userId}.json`, JSON.stringify(data));
  await processFile(`/tmp/${event.userId}.json`);
  // File remains for next invocation
};
```

JavaScript -- FIXED:
```javascript
const { mkdtemp, rm } = require('fs/promises');
const os = require('os');

exports.handler = async (event) => {
  const tmpDir = await mkdtemp(path.join(os.tmpdir(), 'work-'));
  try {
    const filePath = path.join(tmpDir, 'data.json');
    await fs.promises.writeFile(filePath, JSON.stringify(decrypt(event.body)));
    await processFile(filePath);
  } finally {
    await rm(tmpDir, { recursive: true });
  }
};
```

Go -- VULNERABLE:
```go
func handler(ctx context.Context, event Event) error {
    path := fmt.Sprintf("/tmp/user_%s.json", event.UserID)
    os.WriteFile(path, decryptedData, 0644)
    processFile(path)
    // No cleanup
    return nil
}
```

Go -- FIXED:
```go
func handler(ctx context.Context, event Event) error {
    f, err := os.CreateTemp("/tmp", "work-*.json")
    if err != nil { return err }
    defer os.Remove(f.Name())
    defer f.Close()
    f.Write(decryptedData)
    processFile(f.Name())
    return nil
}
```

**Scanner Coverage**: semgrep `python.aws-lambda.security.tmp-data-persistence`

**False Positive Guidance**: Caching non-sensitive data in `/tmp` (downloaded
libraries, compiled templates) is a legitimate optimization pattern. Only flag
when sensitive data (user PII, credentials, decrypted secrets) is written to
`/tmp` without cleanup.

**Severity Assessment**:
- **high**: Sensitive user data or credentials written to /tmp without cleanup
- **medium**: Temporary processing data in /tmp without cleanup
- **low**: Non-sensitive cache files in /tmp (expected pattern)

---

## 5. Excessive Function Timeout

**Description**: Functions configured with the maximum timeout (e.g., 900
seconds for AWS Lambda) when their actual task takes seconds. In a DoS
scenario, each malicious invocation holds resources for the maximum duration,
amplifying the attack's cost and resource exhaustion.

**Search Heuristics**:
- Grep: `timeout:\s*(900|600|300)|Timeout:\s*(900|600|300)` in IaC
- Grep: `memorySize:\s*(3008|10240)` (maximum memory -- related overprovisioning)
- Grep: `reservedConcurrency|ReservedConcurrentExecutions` (check presence)
- Glob: `**/serverless.yml`, `**/template.yaml`, `**/*.tf`, `**/function.json`

**Language Examples**:

Serverless Framework -- VULNERABLE:
```yaml
functions:
  api:
    handler: handler.main
    timeout: 900  # Maximum timeout -- unnecessary for API handler
```

Serverless Framework -- FIXED:
```yaml
functions:
  api:
    handler: handler.main
    timeout: 30  # Appropriate for API response time
```

AWS SAM -- VULNERABLE:
```yaml
Resources:
  ApiFunction:
    Type: AWS::Serverless::Function
    Properties:
      Timeout: 900
      # No reserved concurrency
```

AWS SAM -- FIXED:
```yaml
Resources:
  ApiFunction:
    Type: AWS::Serverless::Function
    Properties:
      Timeout: 30
      ReservedConcurrentExecutions: 100
```

Terraform -- VULNERABLE:
```hcl
resource "aws_lambda_function" "api" {
  timeout     = 900
  memory_size = 10240
  # No reserved concurrency
}
```

Terraform -- FIXED:
```hcl
resource "aws_lambda_function" "api" {
  timeout     = 30
  memory_size = 256
  reserved_concurrent_executions = 100
}
```

**Scanner Coverage**: checkov `CKV_AWS_115` (reserved concurrency); no direct
timeout scanner rule

**False Positive Guidance**: Long-running functions (batch processing, video
transcoding, data pipeline steps) may legitimately need high timeouts. Check
the function's purpose before flagging. The concern is API-facing functions
with excessive timeouts.

**Severity Assessment**:
- **high**: API-facing functions with maximum timeout and no concurrency limit
- **medium**: Excessive timeout on event-driven functions without concurrency limit
- **low**: Slightly high timeout but with reserved concurrency configured

---

## 6. Missing Concurrency Limit

**Description**: Without reserved concurrency limits, a single function can
consume the entire account's concurrent execution quota (default 1000 for AWS).
An attacker triggering rapid invocations can cause all other functions in the
account to throttle, creating a cross-function denial of service.

**Search Heuristics**:
- Grep: `reservedConcurrency|ReservedConcurrentExecutions|reserved_concurrent_executions`
- Grep: `provisionedConcurrency|ProvisionedConcurrencyConfig`
- Grep: `concurrency|maxConcurrency` in function configuration
- Glob: `**/serverless.yml`, `**/template.yaml`, `**/*.tf`

**Language Examples**:

Serverless Framework -- VULNERABLE:
```yaml
functions:
  processUpload:
    handler: handler.processUpload
    events:
      - s3:
          bucket: uploads
    # No concurrency limit -- unbounded S3 events can exhaust account
```

Serverless Framework -- FIXED:
```yaml
functions:
  processUpload:
    handler: handler.processUpload
    reservedConcurrency: 50
    events:
      - s3:
          bucket: uploads
```

AWS SAM -- VULNERABLE:
```yaml
Resources:
  ProcessFunction:
    Type: AWS::Serverless::Function
    Properties:
      Handler: handler.process
      # No ReservedConcurrentExecutions
```

AWS SAM -- FIXED:
```yaml
Resources:
  ProcessFunction:
    Type: AWS::Serverless::Function
    Properties:
      Handler: handler.process
      ReservedConcurrentExecutions: 50
```

Terraform -- VULNERABLE:
```hcl
resource "aws_lambda_function" "processor" {
  function_name = "processor"
  handler       = "handler.process"
  # No reserved_concurrent_executions
}
```

Terraform -- FIXED:
```hcl
resource "aws_lambda_function" "processor" {
  function_name                  = "processor"
  handler                        = "handler.process"
  reserved_concurrent_executions = 50
}
```

**Scanner Coverage**: checkov `CKV_AWS_115`

**False Positive Guidance**: Functions behind API Gateway inherit API Gateway's
throttling, providing some protection. Functions that are rarely invoked
(scheduled tasks running once daily) may not need concurrency limits. Focus
on event-driven functions with unbounded triggers (S3, SQS, SNS).

**Severity Assessment**:
- **high**: No concurrency limit on functions with unbounded event triggers
- **medium**: No concurrency limit on API-facing functions (API Gateway provides some protection)
- **low**: No concurrency limit on scheduled/low-frequency functions
