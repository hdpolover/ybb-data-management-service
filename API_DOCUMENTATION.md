# YBB Data Management API Documentation

## Overview

The YBB Data Management Service is a Python Flask API designed for processing data exports, particularly for YBB Foundation applications. It provides robust Excel export functionality, data processing capabilities, and seamless integration with PHP applications.

## Base URL

```
Production: https://files.ybbfoundation.com
Development: http://localhost:5000
```

## Authentication

Currently, the API operates without authentication. For production deployment, consider implementing API key authentication or JWT tokens.

## Content Type

All POST requests should include:
```
Content-Type: application/json
```

## Response Format

All API responses follow this standard format:

```json
{
    "status": "success|error",
    "message": "Response message",
    "data": {...},
    "request_id": "unique_request_identifier"
}
```

## Core API Endpoints

### 1. Health Check

**GET** `/health`

Check service status and availability.

**Response:**
```json
{
    "status": "healthy",
    "timestamp": "2025-07-24T10:30:00Z",
    "service": "YBB Data Processing Service",
    "version": "1.0.0",
    "request_id": "abc123"
}
```

### 2. Excel Export (Standard)

**POST** `/api/export/excel`

Export data to Excel format for datasets under 5,000 records.

**Request Body:**
```json
{
    "data": [
        {"name": "John Doe", "email": "john@example.com", "status": "active"},
        {"name": "Jane Smith", "email": "jane@example.com", "status": "pending"}
    ],
    "filename": "users_export.xlsx",
    "sheet_name": "Users",
    "columns": ["name", "email", "status"],
    "format_options": {
        "auto_width": true,
        "header_style": true
    }
}
```

**Parameters:**
- `data` (required): Array of objects to export
- `filename` (optional): Custom filename for the Excel file
- `sheet_name` (optional): Name of the Excel sheet (default: "Data")
- `columns` (optional): Specific columns to include
- `format_options` (optional): Formatting options

**Response:**
Returns Excel file as binary attachment.

### 3. Excel Export (Chunked)

**POST** `/api/export/excel/chunked`

Export large datasets using chunked processing for better performance.

**Request Body:**
```json
{
    "session_id": "unique_session_123",
    "chunk_data": [...],
    "chunk_index": 0,
    "total_chunks": 5,
    "filename": "large_export.xlsx",
    "sheet_name": "Data"
}
```

**Parameters:**
- `session_id` (required): Unique identifier for the chunked export session
- `chunk_data` (required): Current chunk of data
- `chunk_index` (required): Index of current chunk (0-based)
- `total_chunks` (required): Total number of chunks
- `filename` (optional): Custom filename
- `sheet_name` (optional): Excel sheet name

**Response:**
For non-final chunks:
```json
{
    "status": "chunk_received",
    "session_id": "unique_session_123",
    "chunk_index": 0,
    "total_chunks": 5
}
```

For final chunk: Returns complete Excel file as binary attachment.

### 4. Data Processing

**POST** `/api/data/process`

Process and transform data with filtering, sorting, and grouping operations.

**Request Body:**
```json
{
    "data": [
        {"name": "John", "department": "IT", "salary": 50000, "status": "active"},
        {"name": "Jane", "department": "HR", "salary": 60000, "status": "active"}
    ],
    "operations": [
        {"type": "filter", "column": "status", "value": "active"},
        {"type": "sort", "column": "salary", "order": "desc"},
        {"type": "group", "column": "department", "aggregate": "count"}
    ]
}
```

**Operations:**
- **Filter**: `{"type": "filter", "column": "field_name", "value": "filter_value"}`
- **Sort**: `{"type": "sort", "column": "field_name", "order": "asc|desc"}`
- **Group**: `{"type": "group", "column": "field_name", "aggregate": "count|sum"}`

**Response:**
```json
{
    "status": "success",
    "data": [...],
    "columns": ["name", "department", "salary"],
    "row_count": 150
}
```

### 5. Data Validation

**POST** `/api/data/validate`

Validate data structure and get comprehensive statistics.

**Request Body:**
```json
{
    "data": [...]
}
```

**Response:**
```json
{
    "status": "success",
    "data": {
        "row_count": 1000,
        "column_count": 5,
        "columns": ["name", "email", "status", "created_at", "updated_at"],
        "data_types": {
            "name": "object",
            "email": "object",
            "status": "object",
            "created_at": "datetime64[ns]",
            "updated_at": "datetime64[ns]"
        },
        "null_counts": {
            "name": 0,
            "email": 5,
            "status": 2,
            "created_at": 0,
            "updated_at": 10
        },
        "memory_usage_mb": 2.5,
        "sample_data": [...],
        "recommendations": [
            "Dataset contains null values - consider data cleaning"
        ]
    }
}
```

### 6. CSV Upload and Conversion

**POST** `/api/upload/csv`

Upload CSV file and convert to Excel or process data.

**Request:**
- Content-Type: `multipart/form-data`
- Form fields:
  - `file`: CSV file
  - `format`: "excel" or "json" (optional, default: "excel")
  - `filename`: Custom output filename (optional)

**Response:**
For Excel format: Returns Excel file as binary attachment.
For JSON format:
```json
{
    "status": "success",
    "data": [...],
    "columns": [...],
    "row_count": 500,
    "message": "CSV data processed successfully"
}
```

## YBB-Specific API Endpoints

### 1. Export Participants

**POST** `/api/ybb/export/participants`

Export participants data with YBB-specific templates.

**Request Body:**
```json
{
    "data": [...],
    "template": "standard|detailed|summary|complete",
    "format": "excel|csv",
    "filters": {
        "status": "active",
        "program": "YBB2024"
    },
    "filename": "participants_export.xlsx",
    "sheet_name": "Participants"
}
```

**Templates:**
- `standard`: Basic participant information
- `detailed`: Comprehensive participant data
- `summary`: Summary statistics only
- `complete`: All available fields

### 2. Export Payments

**POST** `/api/ybb/export/payments`

Export payment data with financial templates.

**Request Body:**
```json
{
    "data": [...],
    "template": "standard|detailed",
    "format": "excel|csv",
    "filters": {
        "status": "completed",
        "date_range": {
            "start": "2024-01-01",
            "end": "2024-12-31"
        }
    }
}
```

### 3. Export Ambassadors

**POST** `/api/ybb/export/ambassadors`

Export ambassador data with role-specific formatting.

**Request Body:**
```json
{
    "data": [...],
    "template": "standard|detailed",
    "format": "excel|csv",
    "filters": {
        "region": "Asia",
        "status": "active"
    }
}
```

### 4. Get Export Templates

**GET** `/api/ybb/templates`

Retrieve available export templates for all data types.

**Response:**
```json
{
    "status": "success",
    "data": {
        "participants": {
            "standard": {
                "name": "standard",
                "description": "Basic participant information",
                "fields": ["name", "email", "program", "status"],
                "headers": ["Full Name", "Email Address", "Program", "Status"],
                "includes_sensitive_data": false
            }
        },
        "payments": {...},
        "ambassadors": {...}
    }
}
```

### 5. Get Export Type Templates

**GET** `/api/ybb/templates/{export_type}`

Get templates for a specific export type (participants, payments, ambassadors).

**Response:**
```json
{
    "status": "success",
    "export_type": "participants",
    "data": {
        "standard": {...},
        "detailed": {...}
    }
}
```

### 6. Export Status

**GET** `/api/ybb/export/{export_id}/status`

Check the status of a YBB export operation.

**Response:**
```json
{
    "status": "success",
    "data": {
        "export_id": "exp_123456",
        "status": "completed|processing|failed",
        "progress": 100,
        "created_at": "2024-07-24T10:00:00Z",
        "completed_at": "2024-07-24T10:05:00Z",
        "file_count": 1,
        "total_records": 1500,
        "export_type": "participants",
        "template": "detailed"
    }
}
```

### 7. Download Export

**GET** `/api/ybb/export/{export_id}/download`

Download completed export file.

**Query Parameters:**
- `type`: "single" or "zip" (optional, default: "single")

**Response:**
Returns the export file as binary attachment (Excel, CSV, or ZIP).

## Logging and Monitoring

### 1. Recent Logs

**GET** `/api/logs/recent`

Get recent log entries for monitoring.

**Query Parameters:**
- `type`: "all", "error", "access" (optional, default: "all")
- `lines`: Number of lines to return (optional, default: 50)
- `level`: Log level filter (optional)
- `hours`: Time range in hours (optional, default: 1)

**Response:**
```json
{
    "status": "success",
    "data": {
        "logs": [...],
        "total_found": 250,
        "filters_applied": {"level": "ERROR"},
        "request_id": "abc123"
    }
}
```

### 2. Log Statistics

**GET** `/api/logs/stats`

Get log statistics and performance metrics.

**Query Parameters:**
- `hours`: Time range in hours (optional, default: 24)

**Response:**
```json
{
    "status": "success",
    "data": {
        "time_period_hours": 24,
        "errors": {
            "total_errors": 5,
            "error_types": {"ValidationError": 3, "FileNotFound": 2}
        },
        "performance": {
            "avg_response_time": 250,
            "slow_requests": 2,
            "total_requests": 1500
        },
        "generated_at": "2024-07-24T15:30:00Z"
    }
}
```

### 3. Request Timeline

**GET** `/api/logs/request/{request_id}`

Get complete log timeline for a specific request.

**Response:**
```json
{
    "status": "success",
    "data": {
        "target_request_id": "abc123",
        "logs": [...],
        "total_entries": 8
    }
}
```

## Error Handling

### HTTP Status Codes

- `200 OK`: Successful request
- `400 Bad Request`: Invalid request data
- `404 Not Found`: Resource not found
- `500 Internal Server Error`: Server error

### Error Response Format

```json
{
    "status": "error",
    "message": "Detailed error description",
    "request_id": "abc123",
    "error_code": "VALIDATION_ERROR"
}
```

### Common Error Codes

- `VALIDATION_ERROR`: Invalid input data
- `FILE_NOT_FOUND`: Requested file not found
- `EXPORT_FAILED`: Export operation failed
- `MEMORY_LIMIT`: Dataset too large for processing
- `TEMPLATE_NOT_FOUND`: Invalid template specified

## Rate Limits and Performance

### Limits

- **Request Size**: Maximum 100MB per request
- **Processing Time**: 5 minutes maximum per request
- **Concurrent Requests**: 10 per IP address
- **File Retention**: Export files retained for 24 hours

### Performance Guidelines

- Use chunked processing for datasets > 5,000 records
- Implement client-side batching for large uploads
- Monitor memory usage with data validation endpoint
- Use appropriate templates to minimize data transfer

## SDK and Integration Examples

### PHP Integration

```php
<?php
require_once 'YBBDataProcessor.php';

$processor = new YBBDataProcessor('https://files.ybbfoundation.com');

// Export participants
$participants = getParticipantsData(); // Your data function
$export = $processor->exportYBBData('participants', $participants, [
    'template' => 'detailed',
    'filename' => 'participants_export.xlsx'
]);

// Download file
header('Content-Type: application/vnd.openxmlformats-officedocument.spreadsheetml.sheet');
header('Content-Disposition: attachment; filename="participants.xlsx"');
echo $export;
?>
```

### JavaScript/AJAX Integration

```javascript
// Export data to Excel
async function exportToExcel(data, filename) {
    try {
        const response = await fetch('/api/export/excel', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                data: data,
                filename: filename,
                format_options: {
                    auto_width: true,
                    header_style: true
                }
            })
        });

        if (response.ok) {
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = filename;
            a.click();
            window.URL.revokeObjectURL(url);
        } else {
            console.error('Export failed:', await response.json());
        }
    } catch (error) {
        console.error('Export error:', error);
    }
}

// Process data
async function processData(data, operations) {
    try {
        const response = await fetch('/api/data/process', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                data: data,
                operations: operations
            })
        });

        return await response.json();
    } catch (error) {
        console.error('Processing error:', error);
        return null;
    }
}
```

## Deployment Notes

### Production Configuration

1. **Environment Variables:**
   ```bash
   FLASK_ENV=production
   API_HOST=0.0.0.0
   API_PORT=5000
   MAX_CONTENT_LENGTH=104857600  # 100MB
   ```

2. **WSGI Server:**
   ```bash
   gunicorn -w 4 -b 0.0.0.0:5000 --timeout 300 app:app
   ```

3. **Reverse Proxy (Nginx):**
   ```nginx
   location /api/ {
       proxy_pass http://127.0.0.1:5000;
       proxy_set_header Host $host;
       proxy_set_header X-Real-IP $remote_addr;
       proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
       client_max_body_size 100M;
       proxy_read_timeout 300s;
   }
   ```

### Security Considerations

1. **API Authentication**: Implement API keys or JWT tokens
2. **Input Validation**: Validate all input data
3. **Rate Limiting**: Implement per-IP rate limiting
4. **File Cleanup**: Regular cleanup of temporary files
5. **Logging**: Monitor and log all API access

## Support and Troubleshooting

### Common Issues

1. **Memory Errors**: Use chunked processing for large datasets
2. **Timeout Errors**: Increase server timeout settings
3. **File Format Errors**: Validate data structure before export
4. **Excel Corruption**: Check data encoding and special characters

### Debug Mode

Enable debug logging by setting `FLASK_DEBUG=True` in development.

### Health Monitoring

Regular health checks should be performed using the `/health` endpoint.

---

For additional support or feature requests, please contact the development team or file an issue in the project repository.
