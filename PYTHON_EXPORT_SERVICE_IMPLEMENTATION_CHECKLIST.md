# Python Export Service - Filename Enhancement Quick Implementation Checklist

## Priority Implementation Steps

### 🚀 Phase 1: Basic Filename Support (Essential)

#### ✅ 1. Update Request Handler
- [ ] Modify export endpoints to accept `filename` parameter
- [ ] Modify export endpoints to accept `sheet_name` parameter
- [ ] Add parameter validation and sanitization

#### ✅ 2. Update Response Structure
- [ ] Include `file_name` in single file responses
- [ ] Include `file_name` in batch file responses
- [ ] Include `zip_file_name` in ZIP archive responses

#### ✅ 3. Core File Management
```python
# Essential functions to implement:
def generate_filename(request_data, export_id, batch_info=None)
def get_sheet_name(request_data, batch_info=None)
def sanitize_filename(filename)
```

### 🔧 Phase 2: Enhanced Features (Important)

#### ✅ 4. Multi-File Support
- [ ] Handle batch file naming with descriptive names
- [ ] Generate ZIP archive names based on original filename
- [ ] Update batch response structure

#### ✅ 5. Download Endpoints
- [ ] Return correct filename in Content-Disposition header
- [ ] Handle both custom and fallback filenames
- [ ] Support batch and ZIP downloads

### 🛡️ Phase 3: Error Handling & Testing (Critical)

#### ✅ 6. Error Handling
- [ ] Sanitize dangerous filename characters
- [ ] Handle filename length limits
- [ ] Implement fallback naming when custom name fails

#### ✅ 7. Testing
- [ ] Test custom filename scenarios
- [ ] Test fallback scenarios
- [ ] Test batch file naming
- [ ] Test ZIP archive naming

## Code Integration Points

### Required Changes in Existing Endpoints

#### `/api/ybb/export/participants` (POST)
```python
# Before
request_data = request.get_json()
export_id = generate_unique_id()

# After
request_data = request.get_json()
export_id = generate_unique_id()
filename = request_data.get('filename')
sheet_name = request_data.get('sheet_name')
```

#### Response Updates
```python
# Before
return jsonify({
    "data": {
        "export_id": export_id,
        "file_url": f"/download/{export_id}"
    }
})

# After
return jsonify({
    "data": {
        "export_id": export_id,
        "file_name": actual_filename,  # NEW
        "file_url": f"/download/{export_id}"
    }
})
```

## Expected CodeIgniter Payloads

### Participants Export
```json
{
  "data": [...],
  "template": "standard",
  "format": "excel",
  "filename": "Japan_Youth_Summit_Participants_Complete_Registration_Data_26-07-2025.xlsx",
  "sheet_name": "Participants Data Jul 2025",
  "include_images": false,
  "compress": true,
  "batch_size": 5000
}
```

### Payments Export
```json
{
  "data": [...],
  "template": "standard", 
  "format": "excel",
  "filename": "Japan_Youth_Summit_Payments_Complete_Transaction_Report_26-07-2025.xlsx",
  "sheet_name": "Payment Records Jul 2025",
  "include_images": false,
  "compress": true,
  "batch_size": 5000
}
```

### Ambassadors Export
```json
{
  "data": [...],
  "template": "standard",
  "format": "excel", 
  "filename": "Japan_Youth_Summit_Ambassadors_List_26-07-2025.xlsx",
  "sheet_name": "Ambassadors Jul 2025",
  "include_images": false,
  "compress": true,
  "batch_size": 5000
}
```

## Expected Response Examples

### Single File Response
```json
{
  "status": "success",
  "data": {
    "export_id": "exp_123456789",
    "file_name": "Japan_Youth_Summit_Participants_Complete_Registration_Data_26-07-2025.xlsx",
    "file_url": "/api/ybb/export/exp_123456789/download",
    "file_size": 2048576,
    "record_count": 1250
  }
}
```

### Multi-File Response
```json
{
  "status": "success",
  "export_strategy": "multi_file",
  "data": {
    "individual_files": [
      {
        "batch_number": 1,
        "file_name": "Japan_Youth_Summit_Participants_Complete_Registration_Data_26-07-2025_batch_1_of_3.xlsx",
        "file_url": "/api/ybb/export/exp_123456789/download/batch/1"
      }
    ],
    "archive": {
      "zip_file_name": "Japan_Youth_Summit_Participants_Complete_Registration_Data_26-07-2025_complete_export.zip",
      "zip_file_url": "/api/ybb/export/exp_123456789/download/zip"
    }
  }
}
```

## Minimal Implementation (MVP)

If time is limited, implement these essential features first:

### 1. Basic Filename Support
```python
def create_export_file(data, request_data, export_id):
    # Get custom filename or use fallback
    filename = request_data.get('filename', f'export_{export_id}.xlsx')
    
    # Sanitize filename
    safe_filename = sanitize_filename(filename)
    
    # Create file with custom name
    file_path = os.path.join(EXPORT_DIR, safe_filename)
    
    return {
        'file_path': file_path,
        'file_name': safe_filename
    }
```

### 2. Response Update
```python
@app.route('/api/ybb/export/participants', methods=['POST'])
def export_participants():
    request_data = request.get_json()
    export_id = generate_unique_id()
    
    # Create export
    result = create_export_file(request_data['data'], request_data, export_id)
    
    return jsonify({
        "status": "success",
        "data": {
            "export_id": export_id,
            "file_name": result['file_name'],  # Include original filename
            "file_url": f"/api/ybb/export/{export_id}/download"
        }
    })
```

### 3. Download Endpoint Update
```python
@app.route('/api/ybb/export/<export_id>/download')
def download_export(export_id):
    export_info = get_export_info(export_id)
    
    return send_file(
        export_info['file_path'],
        as_attachment=True,
        download_name=export_info['file_name']  # Use original filename
    )
```

## Testing Commands

### Quick Test
```bash
# Test with custom filename
curl -X POST http://localhost:5000/api/ybb/export/participants \
  -H "Content-Type: application/json" \
  -d '{
    "data": [{"name": "Test", "email": "test@example.com"}],
    "filename": "Test_Program_Participants_26-07-2025.xlsx",
    "sheet_name": "Test Data Jul 2025"
  }'

# Test download
curl -O http://localhost:5000/api/ybb/export/{export_id}/download
```

---

## 📋 Implementation Status Tracking

- [ ] Phase 1: Basic filename support implemented
- [ ] Phase 2: Multi-file and batch support implemented  
- [ ] Phase 3: Error handling and testing completed
- [ ] Integration testing with CodeIgniter completed
- [ ] Production deployment completed

## 🚨 Critical Notes

1. **Backward Compatibility**: Ensure existing exports without custom filenames still work
2. **Security**: Always sanitize filenames to prevent directory traversal attacks
3. **Performance**: Consider caching sanitized filenames for repeated exports
4. **Storage**: Monitor disk usage as descriptive filenames may be longer

## 📞 Support & Questions

When implementing, focus on:
1. **Filename handling** - The core feature
2. **Response structure** - Ensure CodeIgniter gets the right data
3. **Download behavior** - Users see the descriptive filenames
4. **Error handling** - Graceful fallbacks when things go wrong
