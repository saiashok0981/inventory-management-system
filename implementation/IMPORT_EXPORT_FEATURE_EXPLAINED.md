# 📄 PDF Import/Export Feature Explained

## 🎯 Overview

Your system has two main features for bulk asset management:

1. **📥 IMPORT** - Upload CSV/PDF files to bulk-create or update assets
2. **📤 EXPORT** - Download all asset logs as a PDF file

---

## 📥 IMPORT FEATURE

### How It Works

**Step 1: User Uploads File**
- User clicks "📥 Import" button on dashboard
- Selects a `.csv` or `.pdf` file
- System reads the file

**Step 2: Parse File Content**

#### For CSV Files:
```
Example CSV:
asset,serial_no,location,assigned_to,division,asset_owner,model,network_on,status
laptop,LAP001,Building A,John Doe,IT,IT Manager,Dell XPS,DRONA,Inuse
cpu,CPU001,Building B,Jane Smith,HR,HR Manager,Intel i7,internet,Inuse
```

The system:
1. Reads each row as data
2. Matches column headers to field names
3. Extracts asset information

#### For PDF Files:
```
The PDF contains text like:
asset  serial_no  location  assigned_to  division  asset_owner  model  network_on  status
laptop  LAP001    Building A  John Doe   IT        IT Manager   Dell   DRONA       Inuse
```

The system:
1. Extracts text from PDF stream
2. Finds header row (auto-detected)
3. Parses data rows below it
4. Converts to asset records

**Step 3: Smart Header Matching**

The system is **flexible with column names**. These all map to `serial_no`:
- `serial_no` ✓
- `serialno` ✓
- `serialnumber` ✓
- `serial` ✓

**Mapping Table:**
```python
HEADER_FIELD_MAP = {
    "asset": "asset",
    "serialno": "serial_no",
    "assignedto": "assigned_to",
    "roomno": "room_no",
    "assetowner": "asset_owner",
    "networkon": "network_on",
    # ... and more variations
}
```

**Step 4: Validate Data**

Required fields that must exist:
- ✅ `asset` (laptop, cpu, router, etc.)
- ✅ `serial_no` (unique identifier)
- ✅ `division` (which department)
- ✅ `asset_owner` (who owns it)
- ✅ `model` (device model)
- ✅ `network_on` (which network)

Optional fields (can be empty):
- `location`
- `assigned_to`
- `room_no`

Default values:
- If `status` is missing → Set to "Inuse"

**Step 5: Create or Update Assets**

For each row in the file:

**Case 1: New Asset (serial_no doesn't exist)**
```
If serial_no = "LAP001" is NEW:
1. Create new ProjectData record
2. Set all fields from file
3. Set created_by = current user
4. Log creation in audit trail
✅ "created" count ++
```

**Case 2: Existing Asset (serial_no already exists)**
```
If serial_no = "LAP001" already exists:
1. Find existing record
2. Update ONLY fields that changed
3. Log each change:
   - Old value: "Building A"
   - New value: "Building B"
   - Changed by: Current user
   - Timestamp: Auto-recorded
✅ "updated" count ++
```

**Case 3: Invalid/Incomplete Row**
```
If required fields missing:
✅ "skipped" count ++
📝 Error logged: "Row 3: missing required fields: asset_owner"
```

**Step 6: Return Results**

Response shows:
```json
{
  "message": "Import completed",
  "created": 5,      // New assets created
  "updated": 3,      // Existing assets updated
  "skipped": 2,      // Rows with errors
  "errors": [
    "Row 8: missing required fields: division",
    "Row 9: database constraint error"
  ]
}
```

### Example: Import Flow

**Input CSV:**
```
asset,serial_no,location,division,asset_owner,model,network_on
laptop,LAP001,Room 101,IT,IT Manager,Dell XPS,DRONA
cpu,LAP001,Room 102,IT,System Admin,Intel i7,DRONA
router,ROU001,Server Room,Network,Network Lead,Cisco,internet
```

**What Happens:**
1. Row 1 (LAP001): NEW → Create ✅
2. Row 2 (LAP001): EXISTS → Update location + assigned_to ✅
3. Row 3 (ROU001): NEW → Create ✅

**Result:**
```
Created: 2
Updated: 1
Skipped: 0
```

---

## 📤 EXPORT FEATURE

### How It Works

**Step 1: User Clicks Export Button**
- System queries ALL non-deleted assets from database
- Retrieves all fields: asset, serial_no, location, assigned_to, room_no, division, asset_owner, model, network_on, status

**Step 2: Format Data as Text**

Creates text lines like:
```
Asset Logs
ID  Asset  Serial No  Location  User  Room No  Division  Asset Owner  Model  Network On  Status
1   laptop LAP001     Building A John  101     IT        IT Manager   Dell   DRONA      Inuse
2   cpu    CPU001     Building B Jane  102     IT        IT Manager   Intel  DRONA      Inuse
3   router ROU001     Basement   -     -       Network   Network Lead Cisco  internet   Inuse
```

**Step 3: Generate PDF**

Converts text to PDF using custom PDF builder:
1. Creates PDF structure (objects, pages, fonts)
2. Splits content into pages (36 lines per page)
3. Builds xref table (index of all objects)
4. Returns as downloadable PDF

**Step 4: Download**

Browser downloads file as `asset_logs.pdf`

---

## 🔧 Technical Implementation

### PDF Generation (From Scratch - No External Libraries!)

The system builds a valid PDF 1.4 file without using `reportlab` or `pdfplumber`:

**PDF Structure:**
```
%PDF-1.4
1 0 obj
  << /Type /Catalog /Pages 2 0 R >>
endobj

2 0 obj
  << /Type /Pages /Kids [4 0 R 5 0 R] /Count 2 >>
endobj

3 0 obj
  << /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>
endobj

4 0 obj
  << /Type /Page /Parent 2 0 R /MediaBox [0 0 792 612] /Contents 6 0 R /Resources << /Font << /F1 3 0 R >> >> >>
endobj

6 0 obj
  << /Length XXX >>
stream
BT
/F1 12 Tf
72 540 Td
(Asset Logs) Tj
ET
endstream
endobj

xref
0 7
0000000000 65535 f
0000000009 00000 n
...
trailer
<< /Size 7 /Root 1 0 R >>
startxref
12345
%%EOF
```

**Key Points:**
- Each `obj` gets a unique number
- `xref` table tracks byte offset of each object
- PDF must have correct structure or readers fail
- Text strings need escaping: `\` → `\\`, `(` → `\(`, `)` → `\)`

### PDF Text Extraction (Import)

When parsing imported PDFs:

1. **Find stream blocks** using regex: `stream...endstream`
2. **Extract text literals** inside parentheses: `(text here)`
3. **Unescape special characters**: `\\` → `\`, `\(` → `(`, `\)` → `)`
4. **Decode to UTF-8** and extract lines

---

## 📊 Database Changes (Audit Trail)

When importing:
- Every change to an existing asset is logged in `AuditLog` table
- Shows who changed what, when, and the old/new values

Example audit log entry:
```
table_name: "project_data"
record_id: 5
field_name: "location"
old_value: "Building A"
new_value: "Building B"
changed_by: 1  (user ID)
timestamp: 2024-05-22 10:30:45
```

---

## 🚨 Error Handling

### What Happens if Something Goes Wrong?

1. **Empty file** → Error: "Uploaded file is empty"
2. **Wrong file type** → Error: "Only CSV and PDF files are supported"
3. **Missing headers** → Error: "No asset rows were found"
4. **Bad CSV encoding** → Error: "CSV file must be encoded as UTF-8"
5. **Missing required fields** → Row is skipped with error message
6. **Database constraint violation** → Row is skipped, transaction rolled back
7. **Malformed PDF** → Extraction fails gracefully, returns empty rows

---

## 💡 Usage Examples

### Import Example 1: CSV File
```
File: assets.csv
┌─────────────────────────────────────────────────────┐
│ asset | serial_no | location | division | model   │
│ laptop| LAP100    | Room 101 | IT       | Dell XPS│
│ cpu   | CPU200    | Room 102 | IT       | Intel i7│
└─────────────────────────────────────────────────────┘

Result: 2 assets created, all fields imported ✅
```

### Import Example 2: PDF File with Update
```
Current DB:
- LAP001 in Building A

Import PDF contains:
- LAP001 in Building B

Result: 
- Asset LAP001 updated
- Audit log shows: Building A → Building B
- changed_by: current_user.id ✅
```

### Export Example
```
Click "Export PDF" button
        ↓
System queries all 50 assets
        ↓
Formats as readable text
        ↓
Generates PDF (2 pages)
        ↓
Browser downloads: asset_logs.pdf ✅
```

---

## 🎯 Key Features

| Feature | Details |
|---------|---------|
| **Smart Headers** | Flexible column name matching (serialno, serialnumber, serial all work) |
| **Auto-Detection** | Automatically finds headers in PDF files |
| **Duplicate Handling** | Updates existing assets by serial_no instead of creating duplicates |
| **Audit Trail** | Every import creates audit logs for compliance |
| **Default Values** | Missing status defaults to "Inuse" |
| **Error Recovery** | Skips bad rows but continues processing |
| **PDF from Scratch** | No external libraries needed - built-in PDF generation |
| **Large Files** | Can handle hundreds of assets in one import |

---

## 🔐 Permissions

Both import and export require authentication:
- User must be logged in (JWT token)
- Any authenticated user can import/export
- All changes tracked back to user ID

---

## Summary

**IMPORT:** Upload CSV/PDF → Parse → Smart header matching → Create/Update assets → Log changes ✅

**EXPORT:** Query all assets → Format → Generate PDF → Download ✅

Both work without external PDF libraries through custom parsing and PDF generation!
