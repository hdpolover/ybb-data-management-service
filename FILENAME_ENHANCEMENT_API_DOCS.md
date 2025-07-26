# YBB Export Service - Filename Enhancement API Documentation

## Overview
The YBB Export Service now supports enhanced filename and sheet name functionality, allowing for descriptive, program-specific file naming that makes exported files easier to manage and identify.

## Enhanced Request Payload

All export endpoints now accept additional optional parameters for customizing file names:

```json
{
  "export_type": "participants|payments|ambassadors",
  "data": [...],
  "template": "standard|detailed|custom",
  "format": "excel|csv|pdf",
  "filename": "Japan_Youth_Summit_Participants_Complete_Registration_Data_26-07-2025.xlsx",
  "sheet_name": "Participants Data Jul 2025",
  "filters": {},
  "options": {
    "include_related": true,
    "batch_size": 5000,
    "sort_by": "created_at",
    "sort_order": "desc"
  }
}
```

### New Parameters

#### `filename` (string, optional)
- **Purpose**: Custom filename for the exported file
- **Format**: Should include file extension (.xlsx, .csv)
- **Example**: `"Japan_Youth_Summit_Participants_Complete_Registration_Data_26-07-2025.xlsx"`
- **Behavior**: 
  - If provided, this exact filename will be used
  - For multi-file exports, batch suffixes will be added automatically
  - Filename will be sanitized to remove dangerous characters
  - If not provided, falls back to auto-generated naming

#### `sheet_name` (string, optional)
- **Purpose**: Custom Excel worksheet name
- **Format**: Plain text (no special characters like \, /, ?, *, [, ], :)
- **Example**: `"Participants Data Jul 2025"`
- **Behavior**:
  - If provided, this will be used as the Excel sheet name
  - Limited to 31 characters (Excel limitation)
  - For multi-file exports, batch numbers will be appended
  - If not provided, falls back to generic sheet names

## API Endpoints

### Single File Export Response

```json
{
  "status": "success",
  "message": "Export completed successfully",
  "data": {
    "export_id": "unique_export_id",
    "file_name": "Japan_Youth_Summit_Participants_Complete_Registration_Data_26-07-2025.xlsx",
    "file_url": "/api/ybb/export/unique_export_id/download",
    "file_size": 1048576,
    "record_count": 1250,
    "expires_at": "2025-07-27T10:30:00Z"
  },
  "metadata": {
    "export_type": "participants",
    "template": "standard",
    "processing_time": 2.5,
    "generated_at": "2025-07-26T10:30:00Z",
    "filters_applied": {}
  }
}
```

### Multi-File Export Response

For exports exceeding the batch size limit:

```json
{
  "status": "success",
  "message": "Large export completed successfully",
  "export_strategy": "multi_file",
  "data": {
    "export_id": "unique_export_id",
    "total_records": 15000,
    "total_files": 3,
    "individual_files": [
      {
        "batch_number": 1,
        "file_name": "Japan_Youth_Summit_Participants_Complete_Registration_Data_26-07-2025_batch_1_of_3.xlsx",
        "file_url": "/api/ybb/export/unique_export_id/download/batch/1",
        "file_size": 5242880,
        "record_count": 5000,
        "record_range": "1-5000"
      },
      {
        "batch_number": 2,
        "file_name": "Japan_Youth_Summit_Participants_Complete_Registration_Data_26-07-2025_batch_2_of_3.xlsx",
        "file_url": "/api/ybb/export/unique_export_id/download/batch/2",
        "file_size": 5242880,
        "record_count": 5000,
        "record_range": "5001-10000"
      },
      {
        "batch_number": 3,
        "file_name": "Japan_Youth_Summit_Participants_Complete_Registration_Data_26-07-2025_batch_3_of_3.xlsx",
        "file_url": "/api/ybb/export/unique_export_id/download/batch/3",
        "file_size": 2621440,
        "record_count": 5000,
        "record_range": "10001-15000"
      }
    ],
    "archive": {
      "zip_file_name": "Japan_Youth_Summit_Participants_Complete_Registration_Data_26-07-2025_complete_export.zip",
      "zip_file_url": "/api/ybb/export/unique_export_id/download/zip",
      "zip_file_size": 12582912,
      "compression_ratio": "75.0"
    }
  }
}
```

## File Naming Logic

### Single File Exports
- **With custom filename**: Uses the exact filename provided
- **Without custom filename**: `{export_type}_{template}_{export_id}_{date}_{time}.xlsx`

### Multi-File Exports
- **With custom filename**: `{custom_name}_batch_{number}_of_{total}.xlsx`
- **Without custom filename**: `{export_type}_{template}_{export_id}_batch_{number}_{date}_{time}.xlsx`

### ZIP Archives
- **With custom filename**: `{custom_name}_complete_export.zip`
- **Without custom filename**: `{export_type}_{template}_{export_id}_complete_{date}.zip`

### Sheet Names
- **With custom sheet name**: Uses provided name (truncated to 31 chars if needed)
- **Without custom sheet name**: `{Export_Type} {Month Year}`
- **Multi-file sheets**: Appends `(Batch {number})` to the sheet name

## Security Features

### Filename Sanitization
- Removes dangerous characters: `< > : " / \ | ? *`
- Removes control characters
- Prevents directory traversal attacks
- Limits filename length to 200 characters
- Ensures valid file extensions

### Validation
- Validates filename format and safety
- Checks sheet name for Excel compatibility
- Prevents injection attacks through filename parameters

## Usage Examples

### Basic Export with Custom Filename
```bash
curl -X POST https://api.example.com/api/ybb/export/participants \
  -H "Content-Type: application/json" \
  -d '{
    "data": [...],
    "filename": "My_Program_Participants_26-07-2025.xlsx",
    "sheet_name": "Participants Jul 2025"
  }'
```

### Large Dataset Export
```bash
curl -X POST https://api.example.com/api/ybb/export/participants \
  -H "Content-Type: application/json" \
  -d '{
    "data": [...], // 15000+ records
    "filename": "Large_Program_Export_26-07-2025.xlsx",
    "sheet_name": "All Participants",
    "options": {
      "batch_size": 5000
    }
  }'
```

### Payment Export
```bash
curl -X POST https://api.example.com/api/ybb/export/payments \
  -H "Content-Type: application/json" \
  -d '{
    "data": [...],
    "filename": "Program_Payments_Report_26-07-2025.xlsx",
    "sheet_name": "Payment Records Jul 2025"
  }'
```

## Download Endpoints

### Single File Download
```
GET /api/ybb/export/{export_id}/download
```
Downloads the main export file with the original custom filename.

### Batch File Download
```
GET /api/ybb/export/{export_id}/download/batch/{batch_number}
```
Downloads a specific batch file from a multi-file export.

### ZIP Archive Download
```
GET /api/ybb/export/{export_id}/download/zip
```
Downloads the complete ZIP archive containing all batch files.

## Error Handling

### Invalid Filename
```json
{
  "status": "error",
  "message": "Filename contains potentially dangerous pattern: ../"
}
```

### Invalid Sheet Name
```json
{
  "status": "error",
  "message": "Sheet name cannot contain character: /"
}
```

## Backward Compatibility

The enhancement is fully backward compatible:
- Existing API calls without `filename` or `sheet_name` work unchanged
- Default naming convention is preserved for legacy requests
- All existing download links remain functional

## Best Practices

1. **Descriptive Filenames**: Use program names, dates, and content type
   - Good: `"Japan_Youth_Summit_Participants_Complete_Data_26-07-2025.xlsx"`
   - Avoid: `"export.xlsx"`

2. **Sheet Names**: Keep them descriptive but concise (31 char limit)
   - Good: `"Participants Data Jul 2025"`
   - Avoid: `"Very_Long_Sheet_Name_That_Exceeds_Excel_Limits"`

3. **Date Format**: Use consistent date format in filenames
   - Recommended: `DD-MM-YYYY` format

4. **Special Characters**: Avoid special characters in filenames
   - Safe: Letters, numbers, underscores, hyphens
   - Avoid: `< > : " / \ | ? *`

## Migration Guide

To migrate existing integrations:

1. **Update Request Payloads**: Add `filename` and `sheet_name` parameters
2. **Update Response Handling**: Use `file_name` from response for display
3. **Test Download Links**: Ensure download endpoints work with new filenames
4. **Validate Filenames**: Implement client-side validation for filename safety

## Support

For questions or issues with the filename enhancement:
1. Check the validation messages for specific error details
2. Ensure filenames follow the security guidelines
3. Test with fallback scenarios for robust integration
