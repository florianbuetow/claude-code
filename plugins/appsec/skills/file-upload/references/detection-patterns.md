# File Upload Detection Patterns

Patterns for detecting file upload vulnerabilities including unrestricted
upload, path traversal, and zip slip.

---

## 1. Client-Only File Type Validation

**Description**: The application validates file types only on the client side
(HTML `accept` attribute, JavaScript checks) without server-side enforcement.
An attacker can bypass client-side validation by sending requests directly.

**Search Heuristics**:
- Grep: `accept=["'](\.\w+|image/|video/|audio/)` in HTML without matching server check
- Grep: `file\.type\s*===|file\.name\.endsWith|\.test\(file\.name\)` (JS-only validation)
- Grep: `allowedTypes|acceptedFiles|fileFilter` in frontend code without backend match
- Glob: `**/components/**`, `**/views/**`, `**/templates/**`

**Language Examples**:

JavaScript (Frontend) -- VULNERABLE:
```javascript
const handleUpload = (file) => {
  if (!['image/png', 'image/jpeg'].includes(file.type)) {
    alert('Only images allowed');
    return;  // Client-side only -- trivially bypassed
  }
  fetch('/api/upload', { method: 'POST', body: formData });
};
```

JavaScript (Backend - Express) -- STILL VULNERABLE (no server check):
```javascript
router.post('/api/upload', upload.single('file'), async (req, res) => {
  await fs.promises.writeFile(`uploads/${req.file.originalname}`, req.file.buffer);
  res.json({ status: 'uploaded' });
});
```

JavaScript (Backend - Express) -- FIXED:
```javascript
const ALLOWED_TYPES = ['image/png', 'image/jpeg', 'image/gif'];

router.post('/api/upload', upload.single('file'), async (req, res) => {
  if (!ALLOWED_TYPES.includes(req.file.mimetype)) {
    return res.status(400).json({ error: 'Invalid file type' });
  }
  const ext = path.extname(req.file.originalname).toLowerCase();
  if (!['.png', '.jpg', '.jpeg', '.gif'].includes(ext)) {
    return res.status(400).json({ error: 'Invalid extension' });
  }
  // Also validate magic bytes -- see pattern #3
  await fs.promises.writeFile(`uploads/${uuid()}${ext}`, req.file.buffer);
  res.json({ status: 'uploaded' });
});
```

Python (Flask) -- VULNERABLE:
```python
@app.route('/upload', methods=['POST'])
def upload_file():
    f = request.files['file']
    f.save(os.path.join('uploads', f.filename))  # No validation at all
    return jsonify({"status": "uploaded"})
```

Python (Flask) -- FIXED:
```python
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

@app.route('/upload', methods=['POST'])
def upload_file():
    f = request.files['file']
    ext = f.filename.rsplit('.', 1)[-1].lower() if '.' in f.filename else ''
    if ext not in ALLOWED_EXTENSIONS:
        return jsonify({"error": "Invalid file type"}), 400
    safe_name = f"{uuid.uuid4()}.{ext}"
    f.save(os.path.join('uploads', safe_name))
    return jsonify({"status": "uploaded"})
```

**Scanner Coverage**: semgrep `javascript.express.security.unrestricted-upload`

**False Positive Guidance**: Applications that intentionally accept all file
types (file managers, cloud storage) may not need type restriction, but should
still validate size and sanitize filenames. Check the application context.

**Severity Assessment**:
- **high**: No server-side validation on upload endpoints serving user content
- **medium**: Client-only validation with some server-side extension checking
- **low**: Missing validation on internal-only upload endpoints

---

## 2. Path Traversal in Filename

**Description**: The application uses the user-supplied original filename to
construct a file path without sanitization. An attacker can include `../`
sequences in the filename to write files outside the intended directory.

**Search Heuristics**:
- Grep: `originalname|original_filename|filename` used in `path\.join|os\.path\.join`
- Grep: `req\.file\.originalname|request\.files.*\.filename`
- Grep: `\.filename` without `secure_filename|sanitize|basename|path\.basename`
- Glob: `**/upload/**`, `**/handlers/**`, `**/controllers/**`

**Language Examples**:

Python (Flask) -- VULNERABLE:
```python
@app.route('/upload', methods=['POST'])
def upload():
    f = request.files['file']
    f.save(os.path.join('/var/uploads', f.filename))  # f.filename = "../../etc/cron.d/evil"
```

Python (Flask) -- FIXED:
```python
from werkzeug.utils import secure_filename

@app.route('/upload', methods=['POST'])
def upload():
    f = request.files['file']
    safe_name = secure_filename(f.filename)
    if not safe_name:
        return jsonify({"error": "Invalid filename"}), 400
    f.save(os.path.join('/var/uploads', safe_name))
```

JavaScript (Express) -- VULNERABLE:
```javascript
router.post('/upload', upload.single('file'), (req, res) => {
  const dest = path.join('/var/uploads', req.file.originalname);
  fs.renameSync(req.file.path, dest);  // originalname = "../../app/shell.js"
});
```

JavaScript (Express) -- FIXED:
```javascript
router.post('/upload', upload.single('file'), (req, res) => {
  const safeName = path.basename(req.file.originalname);
  const dest = path.join('/var/uploads', safeName);
  if (!dest.startsWith('/var/uploads/')) {
    return res.status(400).json({ error: 'Invalid filename' });
  }
  fs.renameSync(req.file.path, dest);
});
```

Java (Spring) -- VULNERABLE:
```java
@PostMapping("/upload")
public String upload(@RequestParam("file") MultipartFile file) {
    Path dest = Paths.get("/var/uploads/" + file.getOriginalFilename());
    Files.copy(file.getInputStream(), dest);
    return "uploaded";
}
```

Java (Spring) -- FIXED:
```java
@PostMapping("/upload")
public String upload(@RequestParam("file") MultipartFile file) {
    String safeName = Paths.get(file.getOriginalFilename()).getFileName().toString();
    Path dest = Paths.get("/var/uploads").resolve(safeName).normalize();
    if (!dest.startsWith("/var/uploads")) {
        throw new SecurityException("Invalid filename");
    }
    Files.copy(file.getInputStream(), dest);
    return "uploaded";
}
```

Go -- VULNERABLE:
```go
func uploadHandler(w http.ResponseWriter, r *http.Request) {
    file, header, _ := r.FormFile("file")
    dest := filepath.Join("/var/uploads", header.Filename)
    out, _ := os.Create(dest)  // header.Filename = "../../etc/cron.d/evil"
    io.Copy(out, file)
}
```

Go -- FIXED:
```go
func uploadHandler(w http.ResponseWriter, r *http.Request) {
    file, header, _ := r.FormFile("file")
    safeName := filepath.Base(header.Filename)
    dest := filepath.Join("/var/uploads", safeName)
    if !strings.HasPrefix(filepath.Clean(dest), "/var/uploads/") {
        http.Error(w, "invalid filename", http.StatusBadRequest)
        return
    }
    out, _ := os.Create(dest)
    io.Copy(out, file)
}
```

**Scanner Coverage**: semgrep `generic.path-traversal.upload-filename`,
bandit `B108`

**False Positive Guidance**: If filenames are replaced entirely with generated
names (UUID, hash), there is no path traversal risk even without sanitization
of the original name. Check whether the original filename is actually used in
path construction.

**Severity Assessment**:
- **critical**: Path traversal allowing overwrite of system/application files
- **high**: Path traversal in upload handler with user-supplied filename
- **medium**: Filename used in path without full sanitization but with some checks

---

## 3. Missing Magic Byte Validation

**Description**: The application determines file type solely by file extension
or the client-provided Content-Type header, without verifying the actual file
content via magic bytes (file signatures). Attackers can upload executable
files disguised with safe extensions.

**Search Heuristics**:
- Grep: `mimetype|content.type|file\.type` without `magic|file-type|fileTypeFromBuffer`
- Grep: `endsWith\(['"]\.jpg|\.split\(['"]\.['"]|rsplit.*\.\s*1` (extension-only check)
- Grep: `file-type|python-magic|libmagic|FileTypeDetector` (safe patterns to verify presence)
- Glob: `**/upload/**`, `**/middleware/**`, `**/validators/**`

**Language Examples**:

Python -- VULNERABLE:
```python
def validate_image(uploaded_file):
    if not uploaded_file.filename.endswith(('.jpg', '.png', '.gif')):
        raise ValueError("Invalid image type")
    # Trusts extension only -- a PHP file renamed to .jpg passes
```

Python -- FIXED:
```python
import magic

def validate_image(uploaded_file):
    mime = magic.from_buffer(uploaded_file.read(2048), mime=True)
    uploaded_file.seek(0)
    if mime not in ('image/jpeg', 'image/png', 'image/gif'):
        raise ValueError(f"Invalid file content: {mime}")
```

JavaScript -- VULNERABLE:
```javascript
const ext = path.extname(file.originalname).toLowerCase();
if (['.jpg', '.png'].includes(ext)) {
  // Trusts extension only
  saveFile(file);
}
```

JavaScript -- FIXED:
```javascript
const { fileTypeFromBuffer } = require('file-type');

const type = await fileTypeFromBuffer(file.buffer);
if (!type || !['image/jpeg', 'image/png'].includes(type.mime)) {
  throw new Error('Invalid file content');
}
saveFile(file);
```

Java -- VULNERABLE:
```java
String filename = file.getOriginalFilename();
if (filename.endsWith(".jpg") || filename.endsWith(".png")) {
    // Extension check only -- no content validation
    Files.copy(file.getInputStream(), dest);
}
```

Java -- FIXED:
```java
String detectedType = Files.probeContentType(tempFile);
// Or use Apache Tika: new Tika().detect(file.getInputStream())
if (!List.of("image/jpeg", "image/png").contains(detectedType)) {
    throw new SecurityException("Invalid file content type");
}
```

Go -- VULNERABLE:
```go
ext := filepath.Ext(filename)
if ext == ".jpg" || ext == ".png" {
    // Extension only
}
```

Go -- FIXED:
```go
buf := make([]byte, 512)
file.Read(buf)
file.Seek(0, 0)
contentType := http.DetectContentType(buf)
if contentType != "image/jpeg" && contentType != "image/png" {
    return errors.New("invalid file type")
}
```

**Scanner Coverage**: No direct scanner rule. Detected by checking for absence
of content-based type detection libraries.

**False Positive Guidance**: Applications handling plain text or known-safe
binary formats (CSV, JSON) may not need magic byte checking. The risk is
primarily for applications serving uploaded content to other users.

**Severity Assessment**:
- **high**: Image upload without magic bytes on user-facing content
- **medium**: Missing magic bytes on uploads that are processed server-side only
- **low**: Missing magic bytes on internal-only upload functionality

---

## 4. Upload to Webroot / Executable Directory

**Description**: Uploaded files are stored in a directory served by the web
server where they can be accessed (and potentially executed) directly via URL.
A PHP, JSP, or ASPX file uploaded to the webroot achieves remote code execution.

**Search Heuristics**:
- Grep: `public/|static/|www/|htdocs/|webroot/|wwwroot/` in upload destination
- Grep: `express\.static.*uploads|STATIC_URL.*uploads`
- Grep: `MEDIA_ROOT|upload_to=|UPLOAD_DIR.*public`
- Glob: `**/config/**`, `**/settings/**`, `**/app.*`

**Language Examples**:

Python (Django) -- VULNERABLE:
```python
MEDIA_ROOT = os.path.join(BASE_DIR, 'static', 'uploads')  # Inside static directory
MEDIA_URL = '/static/uploads/'  # Directly web-accessible
```

Python (Django) -- FIXED:
```python
MEDIA_ROOT = '/var/app/uploads/'  # Outside webroot
# Serve via authenticated view, not static files
```

JavaScript (Express) -- VULNERABLE:
```javascript
app.use(express.static('public'));
// Uploads saved to public/uploads/ -- directly accessible and executable
const storage = multer.diskStorage({
  destination: 'public/uploads/',
});
```

JavaScript (Express) -- FIXED:
```javascript
// Store outside webroot
const storage = multer.diskStorage({
  destination: '/var/app/uploads/',
});
// Serve via authenticated route with Content-Disposition: attachment
```

Java (Spring) -- VULNERABLE:
```java
@Value("${upload.path:src/main/resources/static/uploads}")
private String uploadPath;  // Inside static resources -- served directly
```

Java (Spring) -- FIXED:
```java
@Value("${upload.path:/var/app/uploads}")
private String uploadPath;  // Outside webroot, served via controller
```

Go -- VULNERABLE:
```go
http.Handle("/static/", http.StripPrefix("/static/", http.FileServer(http.Dir("./static"))))
// Uploads saved to ./static/uploads/ -- directly served
```

Go -- FIXED:
```go
// Store uploads in /var/app/uploads/ (not static-served)
// Serve via handler that sets Content-Type and Content-Disposition
```

**Scanner Coverage**: semgrep `generic.security.upload-to-webroot`

**False Positive Guidance**: Static asset uploads (images for a CMS) that are
validated and stripped of metadata may be intentionally web-accessible. The
concern is when executable file types can be uploaded to served directories.

**Severity Assessment**:
- **critical**: Upload to webroot on servers that execute uploaded scripts (PHP, JSP)
- **high**: Upload to web-served directory without execution but with XSS risk (HTML, SVG)
- **medium**: Upload to served directory with type validation but no magic bytes

---

## 5. Zip Slip (Archive Extraction Path Traversal)

**Description**: When extracting files from ZIP, TAR, or other archive formats,
entry names containing `../` can write files outside the intended extraction
directory. This can overwrite application files, configuration, or executables.

**Search Heuristics**:
- Grep: `zipfile\.extract|ZipFile|ZipInputStream|tar\.Extract|unzip`
- Grep: `entry\.getName|entry\.name|member\.name` without path validation
- Grep: `extractall|extractAll|extract_all` without path prefix check
- Glob: `**/extract/**`, `**/import/**`, `**/unzip/**`, `**/archive/**`

**Language Examples**:

Python -- VULNERABLE:
```python
import zipfile

def extract_upload(zip_path, dest):
    with zipfile.ZipFile(zip_path, 'r') as z:
        z.extractall(dest)  # No path validation -- zip slip
```

Python -- FIXED:
```python
import zipfile, os

def extract_upload(zip_path, dest):
    dest = os.path.realpath(dest)
    with zipfile.ZipFile(zip_path, 'r') as z:
        for member in z.namelist():
            member_path = os.path.realpath(os.path.join(dest, member))
            if not member_path.startswith(dest + os.sep):
                raise SecurityError(f"Zip slip detected: {member}")
        z.extractall(dest)
```

JavaScript (Node.js) -- VULNERABLE:
```javascript
const AdmZip = require('adm-zip');
const zip = new AdmZip(uploadedFile);
zip.extractAllTo('./extracted/', true);  // No path validation
```

JavaScript (Node.js) -- FIXED:
```javascript
const AdmZip = require('adm-zip');
const zip = new AdmZip(uploadedFile);
const destDir = path.resolve('./extracted/');
for (const entry of zip.getEntries()) {
  const entryPath = path.resolve(destDir, entry.entryName);
  if (!entryPath.startsWith(destDir + path.sep)) {
    throw new Error(`Zip slip: ${entry.entryName}`);
  }
}
zip.extractAllTo(destDir, true);
```

Java -- VULNERABLE:
```java
ZipInputStream zis = new ZipInputStream(new FileInputStream(zipFile));
ZipEntry entry;
while ((entry = zis.getNextEntry()) != null) {
    File dest = new File(outputDir, entry.getName());  // No path check
    Files.copy(zis, dest.toPath());
}
```

Java -- FIXED:
```java
ZipInputStream zis = new ZipInputStream(new FileInputStream(zipFile));
ZipEntry entry;
Path outputPath = outputDir.toPath().toRealPath();
while ((entry = zis.getNextEntry()) != null) {
    Path dest = outputPath.resolve(entry.getName()).normalize();
    if (!dest.startsWith(outputPath)) {
        throw new SecurityException("Zip slip: " + entry.getName());
    }
    Files.copy(zis, dest);
}
```

Go -- VULNERABLE:
```go
r, _ := zip.OpenReader(zipPath)
for _, f := range r.File {
    dest := filepath.Join(outputDir, f.Name)
    os.MkdirAll(filepath.Dir(dest), 0755)
    out, _ := os.Create(dest)  // No path validation
    rc, _ := f.Open()
    io.Copy(out, rc)
}
```

Go -- FIXED:
```go
r, _ := zip.OpenReader(zipPath)
absOutput, _ := filepath.Abs(outputDir)
for _, f := range r.File {
    dest := filepath.Join(absOutput, f.Name)
    if !strings.HasPrefix(filepath.Clean(dest), absOutput+string(os.PathSeparator)) {
        return fmt.Errorf("zip slip: %s", f.Name)
    }
    os.MkdirAll(filepath.Dir(dest), 0755)
    out, _ := os.Create(dest)
    rc, _ := f.Open()
    io.Copy(out, rc)
}
```

**Scanner Coverage**: semgrep `generic.zipslip.security.zip-path-traversal`

**False Positive Guidance**: Libraries that have built-in zip slip protection
(e.g., Python 3.12+ `zipfile` with `extractall` validates paths by default)
may not be vulnerable. Check library version and documentation.

**Severity Assessment**:
- **critical**: Zip slip allowing overwrite of application code or config
- **high**: Zip slip in import/upload functionality with user-supplied archives
- **medium**: Zip slip with limited write scope (sandboxed extraction directory)
