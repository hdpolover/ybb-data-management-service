# 📊 Excel Export API Documentation

## Overview

The YBB Data Management Service provides comprehensive Excel export functionality through multiple endpoints designed to handle various data types and export scenarios. This API is deployed on Railway platform and designed for integration with CodeIgniter 4 frontend applications.

**Base URL:** `https://ybb-data-management-service-production.up.railway.app` (Production - Railway Hosted) | `http://localhost:5000` (Development)

**Frontend Integration:** Optimized for CodeIgniter 4 with comprehensive PHP integration examples included.

**Last Updated:** August 25, 2025

---

## 🌐 Global Headers & Authentication

### Required Headers
```http
Content-Type: application/json
Accept: application/json
```

### Response Headers (File Downloads)
```http
Content-Type: application/vnd.openxmlformats-officedocument.spreadsheetml.sheet
Content-Disposition: attachment; filename="{filename}.xlsx"
Content-Length: {file_size_bytes}
```

### Authentication

**Production Environment:** API Key authentication required

**Development Environment:** No authentication required

For production environments, API Key authentication is implemented:

**Header:** `X-API-Key: your_api_key_here`

**Example:**
```bash
curl -X POST "https://ybb-data-management-service-production.up.railway.app/api/ybb/export/participants" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: ybb_api_key_abc123456789" \
  -d '{"data": [...], "template": "standard"}'
```

**Rate Limiting by API Key:**

| Tier | Rate Limit | Max File Size | Concurrent Exports |
|------|------------|---------------|-------------------|
| Development | 50 req/hour | 10 MB | 2 |
| Production | 500 req/hour | 100 MB | 10 |
| Enterprise | 2000 req/hour | 500 MB | 25 |

---

## 📋 Core Excel Export Endpoints

### 1. Basic Excel Export

**Endpoint:** `POST /api/export/excel`

**Purpose:** Convert JSON data to Excel format for datasets under 5,000 records

**Request Body:**
```json
{
    "data": [
        {
            "name": "John Doe",
            "email": "john@example.com", 
            "department": "Engineering",
            "salary": 75000,
            "hire_date": "2024-01-15",
            "status": "active"
        },
        {
            "name": "Jane Smith",
            "email": "jane@example.com",
            "department": "Marketing", 
            "salary": 68000,
            "hire_date": "2024-02-20",
            "status": "active"
        }
    ],
    "filename": "employee_report.xlsx",
    "sheet_name": "Employees",
    "columns": ["name", "email", "department", "salary", "status"],
    "format_options": {
        "auto_width": true,
        "header_style": true,
        "freeze_header": true,
        "date_format": "MM/DD/YYYY"
    }
}
```

**Request Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `data` | Array | ✅ | Array of objects containing the data to export |
| `filename` | String | ❌ | Custom filename (default: "export_{timestamp}.xlsx") |
| `sheet_name` | String | ❌ | Excel sheet name (default: "Data") |
| `columns` | Array | ❌ | Specific columns to include (default: all columns) |
| `format_options` | Object | ❌ | Excel formatting options |

**Format Options:**
| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `auto_width` | Boolean | `true` | Automatically adjust column widths |
| `header_style` | Boolean | `true` | Apply bold styling to headers |
| `freeze_header` | Boolean | `false` | Freeze the header row |
| `date_format` | String | `"YYYY-MM-DD"` | Date column formatting |
| `number_format` | String | `"#,##0.00"` | Number column formatting |

**Success Response:**
- **Status Code:** `200 OK`
- **Content-Type:** `application/vnd.openxmlformats-officedocument.spreadsheetml.sheet`
- **Body:** Binary Excel file content

**Error Response:**
```json
{
    "status": "error",
    "message": "Invalid data format: expected array of objects",
    "error_code": "VALIDATION_ERROR",
    "request_id": "req_abc123456"
}
```

**Example cURL:**
```bash
curl -X POST "https://ybb-data-management-service-production.up.railway.app/api/export/excel" \
  -H "Content-Type: application/json" \
  -d '{
    "data": [{"name": "John", "email": "john@test.com"}],
    "filename": "test_export.xlsx"
  }' \
  --output "test_export.xlsx"
```

---

### 2. Chunked Excel Export

**Endpoint:** `POST /api/export/excel/chunked`

**Purpose:** Handle large datasets using chunked processing for better performance

**Request Body:**
```json
{
    "session_id": "session_abc123456789",
    "chunk_data": [
        {
            "id": 1001,
            "name": "Alice Johnson",
            "email": "alice@company.com",
            "department": "Sales"
        },
        {
            "id": 1002, 
            "name": "Bob Wilson",
            "email": "bob@company.com",
            "department": "Support"
        }
    ],
    "chunk_index": 0,
    "total_chunks": 5,
    "filename": "large_employee_export.xlsx",
    "sheet_name": "All_Employees",
    "format_options": {
        "auto_width": true,
        "header_style": true
    }
}
```

**Request Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `session_id` | String | ✅ | Unique identifier for the chunked export session |
| `chunk_data` | Array | ✅ | Current chunk of data to process |
| `chunk_index` | Integer | ✅ | Index of current chunk (0-based) |
| `total_chunks` | Integer | ✅ | Total number of chunks in the session |
| `filename` | String | ❌ | Output filename |
| `sheet_name` | String | ❌ | Excel sheet name |
| `format_options` | Object | ❌ | Excel formatting options |

**Response (Non-final chunk):**

```json
{
    "status": "chunk_received",
    "message": "Chunk 1 of 5 processed successfully",
    "session_id": "session_abc123456789",
    "chunk_index": 0,
    "total_chunks": 5,
    "chunks_remaining": 4,
    "estimated_completion_time": "2025-08-25T15:45:30Z",
    "processing_stats": {
        "records_processed": 1000,
        "total_records_expected": 5000,
        "progress_percentage": 20.0,
        "current_chunk_processing_time_ms": 234.5,
        "average_chunk_processing_time_ms": 234.5,
        "estimated_remaining_time_ms": 938.0,
        "memory_usage_mb": 25.5,
        "peak_memory_this_chunk_mb": 28.2,
        "records_per_second_this_chunk": 4264.9
    },
    "performance_metrics": {
        "chunks_completed": 1,
        "total_processing_time_so_far_ms": 234.5,
        "average_records_per_second": 4264.9,
        "memory_efficiency_mb_per_1k_records": 25.5
    },
    "request_id": "req_def789012"
}
```

**Response (Final chunk):**
- **Status Code:** `200 OK`
- **Content-Type:** `application/vnd.openxmlformats-officedocument.spreadsheetml.sheet`
- **Body:** Complete Excel file with all chunks combined
- **Headers:**
  ```http
  Content-Disposition: attachment; filename="large_employee_export.xlsx"
  X-Total-Chunks: 5
  X-Total-Records: 5000
  X-Processing-Time-Ms: 1173.2
  X-Memory-Peak-Mb: 45.7
  ```

**Example JavaScript Implementation:**
```javascript
async function exportLargeDataset(data, chunkSize = 1000) {
    const sessionId = `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    const chunks = [];
    
    // Split data into chunks
    for (let i = 0; i < data.length; i += chunkSize) {
        chunks.push(data.slice(i, i + chunkSize));
    }
    
    // Process each chunk
    for (let i = 0; i < chunks.length; i++) {
        const response = await fetch('/api/export/excel/chunked', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                session_id: sessionId,
                chunk_data: chunks[i],
                chunk_index: i,
                total_chunks: chunks.length,
                filename: 'large_export.xlsx'
            })
        });
        
        if (i === chunks.length - 1) {
            // Final chunk - download file
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = 'large_export.xlsx';
            a.click();
            window.URL.revokeObjectURL(url);
        } else {
            // Intermediate chunk - check status
            const result = await response.json();
            console.log(`Chunk ${i + 1}/${chunks.length} processed`);
        }
    }
}
```

---

## 🎯 YBB-Specific Excel Export Endpoints

### 1. Export Participants to Excel

**Endpoint:** `POST /api/ybb/export/participants`

**Purpose:** Export participant data with YBB-specific templates and formatting

**Request Body:**
```json
{
    "data": [
        {
            "id": "P2024001",
            "first_name": "John",
            "last_name": "Doe",
            "email": "john.doe@university.edu",
            "country": "United States",
            "institution": "Harvard University",
            "phone": "+1-555-0123",
            "category": "student",
            "form_status": "approved",
            "payment_status": "completed",
            "registration_date": "2024-08-15T10:30:00Z",
            "gender": "male",
            "birth_date": "1998-03-15",
            "education_level": "undergraduate",
            "emergency_contact": "Jane Doe (+1-555-0124)",
            "ambassador_reference": "AMB2024-001"
        }
    ],
    "template": "detailed",
    "format": "excel",
    "filters": {
        "country": ["United States", "Canada"],
        "status": "approved",
        "registration_date_range": {
            "start": "2024-01-01",
            "end": "2024-12-31"
        }
    },
    "filename": "ybb_participants_2024",
    "sheet_name": "YBB_Participants_2024"
}
```

**Request Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `data` | Array | ✅ | Array of participant objects |
| `template` | String | ❌ | Export template: `standard`, `detailed`, `summary`, `complete` |
| `format` | String | ❌ | Output format: `excel` (default), `csv` |
| `filters` | Object | ❌ | Data filtering options |
| `filename` | String | ❌ | Custom filename |
| `sheet_name` | String | ❌ | Excel sheet name |

**Template Specifications:**

#### Standard Template (Default)
- **Fields:** 10 core fields
- **Columns:** ID, Full Name, Email, Country, Institution, Phone, Category, Form Status, Payment Status, Registration Date
- **Max Records:** 15,000 (single file)
- **Chunk Size:** 5,000 records
- **Use Case:** Basic participant listings

#### Detailed Template
- **Fields:** 18 comprehensive fields
- **Additional Columns:** Gender, Birth Date, Education Level, Emergency Contact, Ambassador Reference, Address, Program Track
- **Max Records:** 10,000 (single file)
- **Chunk Size:** 3,000 records
- **Use Case:** Complete participant profiles

#### Summary Template
- **Fields:** 5 essential fields
- **Columns:** Full Name, Email, Country, Category, Status
- **Max Records:** 50,000 (single file)
- **Chunk Size:** 10,000 records
- **Use Case:** Quick overviews, large datasets

#### Complete Template
- **Fields:** 36+ fields
- **Includes:** All available data including social media, medical history, preferences
- **Max Records:** 5,000 (single file)
- **Chunk Size:** 1,000 records
- **Use Case:** Comprehensive data analysis

**Success Response:**
```json
{
    "status": "success",
    "message": "Participants export completed successfully",
    "export_strategy": "single_file",
    "data": {
        "export_id": "exp_participants_ba91221e_6c85_43da",
        "download_url": "/api/ybb/export/exp_participants_ba91221e_6c85_43da/download",
        "file_name": "ybb_participants_detailed_ba91221e_25-08-2025_143022.xlsx",
        "file_size": 87632,
        "file_size_mb": 0.085,
        "record_count": 425,
        "created_at": "2025-08-25T14:30:22Z",
        "expires_at": "2025-09-01T14:30:22Z"
    },
    "metadata": {
        "export_type": "participants",
        "template": "detailed",
        "format": "excel",
        "generated_at": "2025-08-25T14:30:22Z",
        "compression_used": "none",
        "filters_applied": {
            "country": ["United States", "Canada"],
            "form_status": "approved",
            "date_range": {
                "start": "2024-01-01",
                "end": "2024-12-31"
            },
            "payment_status": null,
            "limit": null,
            "program_payment_id": null
        },
        "temp_files_cleanup_scheduled": false
    },
    "performance_metrics": {
        "processing_time_ms": 639.21,
        "total_processing_time_seconds": 0.64,
        "records_per_second": 1564.4,
        "memory_used_mb": 12.25,
        "peak_memory_mb": 94.2,
        "efficiency_metrics": {
            "kb_per_record": 0.08,
            "processing_ms_per_record": 0.64,
            "memory_efficiency_kb_per_record": 12.54
        }
    },
    "is_chunked_export": true,
    "total_chunks": 45,
    "chunk_size": 1000,
    "total_records": 44728,
    "request_id": "req_ybb_participants_abc123"
}
```

**Multi-file Response (Large datasets):**
```json
{
    "status": "success",
    "message": "Large participants export completed - multiple files generated",
    "export_strategy": "multi_file", 
    "data": {
        "export_id": "exp_participants_large_def456789",
        "total_records": 20000,
        "total_files": 4,
        "individual_files": [
            {
                "batch_number": 1,
                "file_name": "ybb_participants_standard_batch_1_of_4.xlsx",
                "file_size": 245760,
                "record_count": 5000,
                "record_range": "1-5000",
                "processing_time_seconds": 4.82,
                "records_per_second": 1037.3
            },
            {
                "batch_number": 2,
                "file_name": "ybb_participants_standard_batch_2_of_4.xlsx",
                "file_size": 248320,
                "record_count": 5000,
                "record_range": "5001-10000",
                "processing_time_seconds": 4.95,
                "records_per_second": 1010.1
            }
        ],
        "archive_info": {
            "filename": "ybb_participants_standard_archive_25-08-2025.zip",
            "compressed_size": 687104,
            "uncompressed_size": 983040,
            "compression_ratio": "30.1%",
            "compression_time_seconds": 1.23
        },
        "performance_metrics": {
            "total_processing_time_seconds": 20.39,
            "data_preparation_time_seconds": 0.85,
            "average_chunk_processing_time_seconds": 4.89,
            "total_records_per_second": 981.0,
            "chunk_processing_times": [4.82, 4.95, 4.88, 4.91],
            "average_memory_peak_mb": 18.3,
            "efficiency_metrics": {
                "kb_per_record_uncompressed": 0.049,
                "kb_per_record_compressed": 0.034,
                "processing_ms_per_record": 1.02,
                "compression_efficiency": "73.0%"
            }
        },
        "system_info": {
            "chunk_size": 5000,
            "compression_level": 6,
            "temp_files_cleanup_scheduled": true,
            "export_expires_at": "2025-09-01T14:30:22Z"
        }
    },
    "download_url": "/api/ybb/export/exp_participants_large_def456789/download"
}
```

---

### 2. Export Payments to Excel

**Endpoint:** `POST /api/ybb/export/payments`

**Purpose:** Export payment transaction data with financial formatting

**Request Body:**
```json
{
    "data": [
        {
            "payment_id": "PAY2024001", 
            "participant_id": "P2024001",
            "participant_name": "John Doe",
            "amount": 150.00,
            "currency": "USD",
            "payment_method": "credit_card",
            "transaction_id": "txn_abc123456",
            "status": "completed",
            "payment_date": "2024-08-15T14:30:00Z",
            "description": "YBB Summit 2024 Registration Fee",
            "processor": "stripe",
            "fee_amount": 4.65,
            "net_amount": 145.35
        }
    ],
    "template": "detailed",
    "format": "excel",
    "filters": {
        "status": ["completed", "pending"],
        "date_range": {
            "start": "2024-01-01",
            "end": "2024-12-31"
        },
        "amount_range": {
            "min": 50.00,
            "max": 500.00
        }
    },
    "filename": "ybb_payments_2024",
    "sheet_name": "Payment_Records"
}
```

**Template Options:**
- **`standard`**: Basic payment info (ID, Participant, Amount, Status, Date)
- **`detailed`**: Full transaction details including fees, processor info, descriptions

**Success Response:**
```json
{
    "status": "success", 
    "message": "Payments export completed successfully",
    "data": {
        "export_id": "exp_payments_xyz789012",
        "download_url": "/api/ybb/export/exp_payments_xyz789012/download",
        "file_name": "ybb_payments_detailed_xyz789012_25-08-2025_143530.xlsx",
        "record_count": 1247,
        "total_amount": 186750.00,
        "currency_breakdown": {
            "USD": 156230.00,
            "EUR": 20850.00,
            "GBP": 9670.00
        }
    },
    "system_info": {
        "export_type": "payments",
        "template": "detailed",
        "financial_formatting_applied": true,
        "currency_columns_formatted": true
    }
}
```

---

### 3. Export Ambassadors to Excel

**Endpoint:** `POST /api/ybb/export/ambassadors`

**Purpose:** Export ambassador data with role-specific information

**Request Body:**
```json
{
    "data": [
        {
            "ambassador_id": "AMB2024001",
            "first_name": "Sarah", 
            "last_name": "Johnson",
            "email": "sarah.johnson@ybb.org",
            "country": "United Kingdom",
            "region": "Europe",
            "university": "Oxford University",
            "field_of_study": "International Business",
            "role": "senior_ambassador",
            "status": "active",
            "join_date": "2023-01-15",
            "mentees_count": 15,
            "events_organized": 8,
            "social_media": {
                "linkedin": "https://linkedin.com/in/sarahjohnson",
                "instagram": "@sarah_ybb"
            }
        }
    ],
    "template": "detailed",
    "format": "excel", 
    "filters": {
        "region": ["Europe", "Asia"],
        "status": "active",
        "role": ["senior_ambassador", "regional_coordinator"]
    },
    "filename": "ybb_ambassadors_2024",
    "sheet_name": "Active_Ambassadors"
}
```

**Template Options:**
- **`standard`**: Basic ambassador info (ID, Name, Country, Role, Status)
- **`detailed`**: Complete profile including activities, social media, performance metrics

---

## 📊 Export Management & Download Endpoints

### 1. Check Export Status

**Endpoint:** `GET /api/ybb/export/{export_id}/status`

**Purpose:** Monitor export progress and get file information

**URL Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| `export_id` | String | Unique export identifier |

**Response:**
```json
{
    "status": "completed",
    "export_id": "exp_participants_ba91221e_6c85_43da",
    "export_type": "participants",
    "template": "detailed",
    "format": "excel",
    "record_count": 425,
    "created_at": "2025-08-25T14:30:22Z",
    "completed_at": "2025-08-25T14:31:09Z",
    "expires_at": "2025-09-01T14:30:22Z",
    "file_size_bytes": 87632,
    "file_size_mb": 0.085,
    "processing_time_ms": 1247.3,
    "processing_time_seconds": 1.247,
    "records_per_second": 340.8,
    "export_strategy": "single_file",
    "download_ready": true,
    "download_info": {
        "single_file_url": "/api/ybb/export/exp_participants_ba91221e_6c85_43da/download",
        "file_name": "ybb_participants_detailed_ba91221e_25-08-2025_143022.xlsx"
    }
}
```

**Status Values:**
- `processing`: Export is being generated
- `completed`: Export ready for download
- `failed`: Export failed (check error message)
- `expired`: Export has expired and is no longer available

---

### 2. Download Single Export File

**Endpoint:** `GET /api/ybb/export/{export_id}/download`

**Purpose:** Download the generated Excel file

**Query Parameters:**
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `type` | String | `single` | Download type: `single`, `zip` |

**Response:**
- **Status Code:** `200 OK`
- **Content-Type:** `application/vnd.openxmlformats-officedocument.spreadsheetml.sheet`
- **Headers:**
  ```http
  Content-Disposition: attachment; filename="ybb_participants_detailed_ba91221e_25-08-2025_143022.xlsx"
  Content-Length: 87632
  Cache-Control: no-cache, no-store, must-revalidate
  ```

**Example JavaScript:**
```javascript
async function downloadExport(exportId) {
    try {
        const response = await fetch(`/api/ybb/export/${exportId}/download`);
        
        if (response.ok) {
            const blob = await response.blob();
            const filename = response.headers.get('Content-Disposition')
                .split('filename=')[1].replace(/"/g, '');
            
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = filename;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            window.URL.revokeObjectURL(url);
        } else {
            console.error('Download failed:', response.statusText);
        }
    } catch (error) {
        console.error('Download error:', error);
    }
}
```

---

### 3. Download ZIP Archive (Large Exports)

**Endpoint:** `GET /api/ybb/export/{export_id}/download/zip`

**Purpose:** Download ZIP archive containing multiple Excel files for large exports

**Response:**
- **Status Code:** `200 OK`
- **Content-Type:** `application/zip`
- **Headers:**
  ```http
  Content-Disposition: attachment; filename="ybb_participants_detailed_archive_25-08-2025.zip"
  ```

---

### 4. Download Individual Batch File

**Endpoint:** `GET /api/ybb/export/{export_id}/download/batch/{batch_number}`

**Purpose:** Download specific batch file from multi-file export

**URL Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| `export_id` | String | Export identifier |
| `batch_number` | Integer | Batch number (1-based) |

**Response:**
- **Status Code:** `200 OK`
- **Content-Type:** `application/vnd.openxmlformats-officedocument.spreadsheetml.sheet`
- **Headers:**
  ```http
  Content-Disposition: attachment; filename="ybb_participants_detailed_batch_1_of_4.xlsx"
  ```

---

### 5. Delete Export

**Endpoint:** `DELETE /api/ybb/export/{export_id}`

**Purpose:** Manually delete an export and free up storage space

**URL Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| `export_id` | String | Export identifier to delete |

**Response:**
```json
{
    "status": "success",
    "message": "Export deleted successfully",
    "export_id": "exp_participants_ba91221e_6c85_43da",
    "files_deleted": 1,
    "space_freed_mb": 0.085,
    "deletion_timestamp": "2025-08-25T14:35:00Z"
}
```

**Error Response:**
```json
{
    "status": "error",
    "message": "Export not found or already deleted",
    "error_code": "EXPORT_NOT_FOUND",
    "export_id": "exp_invalid_123"
}
```

### 6. List User Exports

**Endpoint:** `GET /api/ybb/exports`

**Purpose:** List all exports for monitoring and management

**Query Parameters:**
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `status` | String | `all` | Filter by status: `processing`, `completed`, `failed`, `expired` |
| `export_type` | String | `all` | Filter by type: `participants`, `payments`, `ambassadors` |
| `limit` | Integer | `50` | Maximum number of results |
| `offset` | Integer | `0` | Pagination offset |

**Response:**
```json
{
    "status": "success",
    "data": {
        "exports": [
            {
                "export_id": "exp_participants_ba91221e_6c85_43da",
                "export_type": "participants",
                "template": "detailed",
                "status": "completed",
                "record_count": 425,
                "file_size_mb": 0.085,
                "created_at": "2025-08-25T14:30:22Z",
                "expires_at": "2025-09-01T14:30:22Z",
                "processing_time_ms": 1247.3,
                "export_strategy": "single_file"
            },
            {
                "export_id": "exp_payments_xyz789012",
                "export_type": "payments",
                "template": "standard",
                "status": "completed",
                "record_count": 1247,
                "file_size_mb": 1.024,
                "created_at": "2025-08-25T13:15:10Z",
                "expires_at": "2025-09-01T13:15:10Z",
                "processing_time_ms": 2890.7,
                "export_strategy": "multi_file"
            }
        ],
        "pagination": {
            "total_exports": 127,
            "current_page": 1,
            "total_pages": 3,
            "limit": 50,
            "offset": 0
        },
        "summary": {
            "completed": 124,
            "processing": 2,
            "failed": 1,
            "total_size_mb": 234.7
        }
    }
}
```

### 4. Batch Export Operations

**Endpoint:** `POST /api/ybb/batch/export`

**Purpose:** Process multiple export requests in a single batch operation

**Request Body:**
```json
{
    "batch_id": "batch_exports_20250825",
    "exports": [
        {
            "export_type": "participants",
            "template": "standard",
            "filename": "participants_2024_q3",
            "filters": {
                "registration_date_range": {
                    "start": "2024-07-01",
                    "end": "2024-09-30"
                }
            }
        },
        {
            "export_type": "payments",
            "template": "detailed",
            "filename": "payments_2024_q3",
            "filters": {
                "payment_date_range": {
                    "start": "2024-07-01",
                    "end": "2024-09-30"
                }
            }
        }
    ],
    "batch_options": {
        "create_combined_archive": true,
        "archive_name": "ybb_q3_2024_reports",
        "parallel_processing": true,
        "max_concurrent": 3
    }
}
```

**Response:**
```json
{
    "status": "batch_started",
    "message": "Batch export operation initiated",
    "data": {
        "batch_id": "batch_exports_20250825",
        "total_exports": 2,
        "batch_status_url": "/api/ybb/batch/batch_exports_20250825/status",
        "estimated_completion_time": "2025-08-25T14:35:00Z",
        "individual_exports": [
            {
                "export_index": 0,
                "export_type": "participants",
                "status": "queued",
                "export_id": null
            },
            {
                "export_index": 1,
                "export_type": "payments",
                "status": "queued",
                "export_id": null
            }
        ]
    }
}
```

### 5. Batch Status Monitoring

**Endpoint:** `GET /api/ybb/batch/{batch_id}/status`

**Purpose:** Monitor progress of batch export operations

**Response:**
```json
{
    "status": "processing",
    "data": {
        "batch_id": "batch_exports_20250825",
        "overall_status": "processing",
        "progress_percentage": 65.0,
        "started_at": "2025-08-25T14:30:00Z",
        "estimated_completion": "2025-08-25T14:35:00Z",
        "exports": [
            {
                "export_index": 0,
                "export_id": "exp_participants_xyz123",
                "export_type": "participants",
                "status": "completed",
                "record_count": 1247,
                "processing_time_ms": 2340.5,
                "file_size_mb": 1.2
            },
            {
                "export_index": 1,
                "export_id": "exp_payments_abc456",
                "export_type": "payments",
                "status": "processing",
                "progress_percentage": 30.0,
                "estimated_remaining_time_ms": 8000
            }
        ],
        "combined_archive": {
            "status": "pending",
            "will_be_created": true,
            "estimated_size_mb": 2.4
        },
        "performance_metrics": {
            "total_records_processed": 1247,
            "average_processing_speed_records_per_second": 1456.2,
            "parallel_efficiency": 87.3
        }
    }
}
```

---

## 🔄 Data Processing & Transformation Endpoints

### 1. Process and Transform Data

**Endpoint:** `POST /api/data/process`

**Purpose:** Transform and process data before export with filtering, sorting, and aggregation

**Request Body:**
```json
{
    "data": [
        {
            "id": "P2024001",
            "first_name": "John",
            "last_name": "Doe",
            "email": "john.doe@university.edu",
            "country": "United States",
            "registration_date": "2024-08-15T10:30:00Z",
            "payment_amount": 150.00,
            "status": "approved"
        }
    ],
    "transformations": {
        "filters": [
            {
                "field": "status",
                "operator": "equals",
                "value": "approved"
            },
            {
                "field": "payment_amount",
                "operator": "greater_than",
                "value": 100
            }
        ],
        "sorting": {
            "field": "registration_date",
            "order": "desc"
        },
        "grouping": {
            "field": "country",
            "aggregations": ["count", "sum_payment_amount"]
        },
        "columns": ["id", "first_name", "last_name", "country", "payment_amount"],
        "calculated_fields": [
            {
                "name": "full_name",
                "formula": "CONCAT({first_name}, ' ', {last_name})"
            },
            {
                "name": "payment_category",
                "formula": "IF({payment_amount} > 200, 'Premium', 'Standard')"
            }
        ]
    },
    "export_options": {
        "format": "json",
        "include_metadata": true
    }
}
```

**Response:**
```json
{
    "status": "success",
    "message": "Data processed successfully",
    "data": {
        "processed_records": [
            {
                "id": "P2024001",
                "first_name": "John",
                "last_name": "Doe",
                "country": "United States",
                "payment_amount": 150.00,
                "full_name": "John Doe",
                "payment_category": "Standard"
            }
        ],
        "aggregations": {
            "by_country": {
                "United States": {
                    "count": 1247,
                    "sum_payment_amount": 187050.00
                },
                "Canada": {
                    "count": 892,
                    "sum_payment_amount": 133800.00
                }
            }
        },
        "metadata": {
            "original_record_count": 2500,
            "filtered_record_count": 2139,
            "records_removed_by_filters": 361,
            "filter_efficiency": 14.4,
            "processing_time_ms": 234.7,
            "memory_used_mb": 8.3
        }
    }
}
```

### 2. Data Quality Validation

**Endpoint:** `POST /api/data/validate`

**Purpose:** Validate data quality and identify potential issues before export

**Request Body:**
```json
{
    "data": [
        {
            "email": "invalid-email",
            "phone": "123",
            "birth_date": "2025-01-01",
            "payment_amount": -50
        }
    ],
    "validation_rules": {
        "email": {
            "type": "email",
            "required": true
        },
        "phone": {
            "type": "phone",
            "min_length": 10
        },
        "birth_date": {
            "type": "date",
            "max_date": "2010-01-01"
        },
        "payment_amount": {
            "type": "number",
            "min_value": 0
        }
    }
}
```

**Response:**
```json
{
    "status": "validation_completed",
    "data": {
        "total_records": 1,
        "valid_records": 0,
        "invalid_records": 1,
        "validation_issues": [
            {
                "record_index": 0,
                "field": "email",
                "issue": "Invalid email format",
                "severity": "error",
                "current_value": "invalid-email"
            },
            {
                "record_index": 0,
                "field": "phone",
                "issue": "Phone number too short",
                "severity": "warning",
                "current_value": "123"
            },
            {
                "record_index": 0,
                "field": "birth_date",
                "issue": "Date is in the future",
                "severity": "error",
                "current_value": "2025-01-01"
            }
        ],
        "summary": {
            "errors": 2,
            "warnings": 1,
            "data_quality_score": 0.0,
            "recommended_action": "Fix errors before export"
        }
    }
}
```

### 3. Database Query Export

**Endpoint:** `POST /api/query/export`

**Purpose:** Execute database queries and export results directly to Excel

**Request Body:**
```json
{
    "query": "SELECT p.id, p.first_name, p.last_name, p.email, py.amount FROM participants p LEFT JOIN payments py ON p.id = py.participant_id WHERE p.status = 'approved' ORDER BY p.registration_date DESC",
    "export_options": {
        "format": "excel",
        "filename": "custom_participant_report",
        "sheet_name": "Query_Results",
        "include_query_info": true
    },
    "format_options": {
        "auto_width": true,
        "header_style": true,
        "freeze_header": true
    }
}
```

**Response:**
```json
{
    "status": "success",
    "message": "Query executed and exported successfully",
    "data": {
        "export_id": "exp_query_abc123456",
        "download_url": "/api/ybb/export/exp_query_abc123456/download",
        "file_name": "custom_participant_report_25-08-2025_143022.xlsx",
        "record_count": 1247,
        "query_execution_time_ms": 450.2,
        "export_processing_time_ms": 892.7,
        "total_time_ms": 1342.9
    },
    "query_info": {
        "query": "SELECT p.id, p.first_name...",
        "executed_at": "2025-08-25T14:30:22Z",
        "tables_accessed": ["participants", "payments"],
        "result_columns": ["id", "first_name", "last_name", "email", "amount"]
    }
}
```

### 1. Health Check

**Endpoint:** `GET /health`

**Purpose:** Check API service status and dependencies

**Response:**
```json
{
    "status": "healthy",
    "timestamp": "2025-08-25T14:30:22Z",
    "version": "1.0.0",
    "environment": "production",
    "services": {
        "pandas": "available",
        "excel": "available",
        "storage": "available",
        "memory_tracking": "available"
    },
    "system_info": {
        "python_version": "3.11.4",
        "pandas_version": "2.2.2",
        "numpy_version": "2.2.6",
        "openpyxl_version": "3.1.2"
    },
    "performance": {
        "uptime_seconds": 86400,
        "total_exports_processed": 1547,
        "average_processing_time_ms": 892.5,
        "current_memory_usage_mb": 45.2
    }
}
```

### 2. Storage Information

**Endpoint:** `GET /api/ybb/storage/info`

**Purpose:** Get storage statistics and cleanup information

**Response:**
```json
{
    "status": "success",
    "data": {
        "total_exports": 1547,
        "active_exports": 23,
        "total_size_bytes": 157286400,
        "total_size_mb": 150.0,
        "oldest_export": "2025-08-18T10:15:30Z",
        "newest_export": "2025-08-25T14:30:22Z",
        "exports_by_type": {
            "participants": 1205,
            "payments": 287,
            "ambassadors": 55
        },
        "storage_limits": {
            "max_file_retention_days": 7,
            "max_file_size_mb": 100,
            "max_concurrent_exports": 10
        },
        "cleanup_info": {
            "next_cleanup": "2025-08-26T02:00:00Z",
            "files_scheduled_for_cleanup": 12,
            "estimated_space_to_free_mb": 85.3
        }
    }
}
```

### 3. Export Statistics

**Endpoint:** `GET /api/ybb/stats`

**Purpose:** Get comprehensive export performance statistics

**Query Parameters:**
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `period` | String | `24h` | Time period: `1h`, `24h`, `7d`, `30d` |
| `export_type` | String | `all` | Filter by type: `participants`, `payments`, `ambassadors` |

**Response:**
```json
{
    "status": "success",
    "period": "24h",
    "data": {
        "total_exports": 89,
        "successful_exports": 87,
        "failed_exports": 2,
        "success_rate": 97.8,
        "total_records_exported": 1547892,
        "total_files_generated": 127,
        "performance_metrics": {
            "average_processing_time_ms": 1247.5,
            "median_processing_time_ms": 892.0,
            "fastest_export_ms": 156.2,
            "slowest_export_ms": 28450.7,
            "average_records_per_second": 1456.3,
            "average_memory_usage_mb": 23.7,
            "peak_memory_usage_mb": 127.4
        },
        "export_strategies": {
            "single_file": 76,
            "multi_file": 11,
            "chunked_percentage": 12.4
        },
        "file_size_distribution": {
            "small_files_under_1mb": 68,
            "medium_files_1_10mb": 18,
            "large_files_over_10mb": 3,
            "average_file_size_mb": 2.4,
            "total_storage_used_mb": 267.8
        },
        "templates_usage": {
            "standard": 52,
            "detailed": 28,
            "summary": 7,
            "complete": 2
        }
    }
}
```

---

## 🔧 Configuration & Template Information

### 1. Get Available Templates

**Endpoint:** `GET /api/ybb/templates`

**Purpose:** Retrieve all available export templates and their configurations

**Response:**
```json
{
    "status": "success",
    "data": {
        "participants": {
            "standard": {
                "name": "standard",
                "display_name": "Standard Participants Export",
                "description": "Basic participant information for general use",
                "fields": [
                    "id", "first_name", "last_name", "email", "country", 
                    "institution", "phone", "category", "form_status", 
                    "payment_status", "registration_date"
                ],
                "headers": [
                    "Participant ID", "First Name", "Last Name", "Email", 
                    "Country", "Institution", "Phone", "Category", 
                    "Form Status", "Payment Status", "Registration Date"
                ],
                "max_records_single_file": 15000,
                "recommended_chunk_size": 5000,
                "includes_sensitive_data": false,
                "estimated_file_size_per_1k_records": "35 KB"
            },
            "detailed": {
                "name": "detailed", 
                "display_name": "Detailed Participants Export",
                "description": "Comprehensive participant data including personal details",
                "fields": [
                    "id", "first_name", "last_name", "email", "country",
                    "institution", "phone", "category", "form_status",
                    "payment_status", "registration_date", "gender",
                    "birth_date", "education_level", "emergency_contact",
                    "ambassador_reference", "address", "program_track", "dietary_preferences"
                ],
                "max_records_single_file": 10000,
                "recommended_chunk_size": 3000,
                "includes_sensitive_data": true,
                "estimated_file_size_per_1k_records": "58 KB"
            }
        },
        "payments": {
            "standard": {
                "name": "standard",
                "display_name": "Standard Payments Export", 
                "description": "Basic payment transaction information",
                "fields": [
                    "payment_id", "participant_id", "participant_name", 
                    "amount", "currency", "status", "payment_date"
                ],
                "financial_formatting": true,
                "currency_support": ["USD", "EUR", "GBP", "CAD"]
            }
        }
    }
}
```

---

### 2. Get Template by Type

**Endpoint:** `GET /api/ybb/templates/{export_type}`

**URL Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| `export_type` | String | Type: `participants`, `payments`, `ambassadors` |

**Response:**
```json
{
    "status": "success",
    "export_type": "participants",
    "data": {
        "standard": { /* template details */ },
        "detailed": { /* template details */ },
        "summary": { /* template details */ },
        "complete": { /* template details */ }
    },
    "default_template": "standard",
    "recommended_template_by_size": {
        "small_dataset": "detailed",
        "medium_dataset": "standard", 
        "large_dataset": "summary"
    }
}
```

---

## ⚠️ Error Handling & Status Codes

### HTTP Status Codes

| Code | Status | Description |
|------|--------|-------------|
| 200 | OK | Request successful, file ready for download |
| 201 | Created | Export created successfully |
| 400 | Bad Request | Invalid request data or parameters |
| 404 | Not Found | Export not found or expired |
| 413 | Payload Too Large | Dataset exceeds maximum size limits |
| 422 | Unprocessable Entity | Valid format but processing failed |
| 429 | Too Many Requests | Rate limit exceeded |
| 500 | Internal Server Error | Server processing error |
| 503 | Service Unavailable | Service temporarily unavailable |

### Error Response Format

```json
{
    "status": "error",
    "message": "Detailed error description",
    "error_code": "ERROR_TYPE",
    "details": {
        "field": "specific_field_with_error",
        "expected": "expected_value_format",
        "received": "actual_received_value"
    },
    "request_id": "req_abc123456",
    "timestamp": "2025-08-25T14:30:22Z",
    "documentation_url": "https://docs.ybbfoundation.com/api/errors#ERROR_TYPE"
}
```

### Common Error Codes

| Error Code | Description | Resolution |
|------------|-------------|------------|
| `VALIDATION_ERROR` | Invalid request data format | Check request body structure |
| `TEMPLATE_NOT_FOUND` | Invalid template specified | Use valid template from `/templates` endpoint |
| `EXPORT_NOT_FOUND` | Export ID not found | Verify export ID or check if expired |
| `EXPORT_EXPIRED` | Export has expired | Create new export request |
| `DATASET_TOO_LARGE` | Dataset exceeds limits | Use chunked processing or reduce dataset |
| `MEMORY_LIMIT_EXCEEDED` | Processing requires too much memory | Split data into smaller chunks |
| `PROCESSING_TIMEOUT` | Export processing timed out | Retry with smaller dataset or contact support |
| `INVALID_TEMPLATE_CONFIG` | Template configuration error | Contact support for template issues |
| `FILE_GENERATION_FAILED` | Excel file creation failed | Check data format and retry |
| `COMPRESSION_FAILED` | ZIP archive creation failed | Retry or use individual file downloads |

### Error Examples

**Validation Error:**
```json
{
    "status": "error",
    "message": "Invalid request: 'data' field is required and must be a non-empty array",
    "error_code": "VALIDATION_ERROR",
    "details": {
        "field": "data",
        "expected": "array of objects",
        "received": "null"
    },
    "request_id": "req_val_error_123"
}
```

**Export Not Found:**
```json
{
    "status": "error",
    "message": "Export with ID 'exp_invalid_123' not found or has expired",
    "error_code": "EXPORT_NOT_FOUND", 
    "details": {
        "export_id": "exp_invalid_123",
        "possible_reasons": [
            "Export has expired (files are retained for 7 days)",
            "Invalid export ID format",
            "Export was cleaned up due to storage limits"
        ]
    },
    "request_id": "req_not_found_456"
}
```

---

## 🚀 Usage Examples & Best Practices

### JavaScript/AJAX Complete Example

```javascript
class YBBExcelExporter {
    constructor(baseUrl = 'https://ybb-data-management-service-production.up.railway.app') {
        this.baseUrl = baseUrl;
    }

    async exportParticipants(data, options = {}) {
        const defaultOptions = {
            template: 'standard',
            format: 'excel',
            filename: 'participants_export'
        };

        const exportOptions = { ...defaultOptions, ...options };

        try {
            // Step 1: Create export
            const createResponse = await fetch(`${this.baseUrl}/api/ybb/export/participants`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    data: data,
                    ...exportOptions
                })
            });

            if (!createResponse.ok) {
                throw new Error(`Export creation failed: ${createResponse.statusText}`);
            }

            const createResult = await createResponse.json();

            if (createResult.status === 'error') {
                throw new Error(createResult.message);
            }

            // Step 2: Download file directly if small dataset
            if (createResult.export_strategy === 'single_file') {
                this.downloadFile(createResult.data.download_url, createResult.data.file_name);
                return createResult;
            }

            // Step 3: Handle large dataset with polling
            return await this.handleLargeExport(createResult.data.export_id);

        } catch (error) {
            console.error('Export failed:', error);
            throw error;
        }
    }

    async handleLargeExport(exportId) {
        // Poll for completion
        const maxAttempts = 30;
        let attempts = 0;

        while (attempts < maxAttempts) {
            const statusResponse = await fetch(`${this.baseUrl}/api/ybb/export/${exportId}/status`);
            const status = await statusResponse.json();

            if (status.status === 'completed') {
                // Download based on strategy
                if (status.export_strategy === 'single_file') {
                    this.downloadFile(status.download_info.single_file_url, status.download_info.file_name);
                } else {
                    // Multiple files - offer ZIP download
                    this.downloadFile(`${this.baseUrl}/api/ybb/export/${exportId}/download/zip`, 
                                    `export_${exportId}.zip`);
                }
                return status;
            } else if (status.status === 'failed') {
                throw new Error(`Export failed: ${status.message}`);
            }

            // Wait before next poll
            await new Promise(resolve => setTimeout(resolve, 2000));
            attempts++;
        }

        throw new Error('Export timeout - please try again');
    }

    downloadFile(url, filename) {
        const link = document.createElement('a');
        link.href = url;
        link.download = filename;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
    }

    async getTemplates(exportType = null) {
        const url = exportType 
            ? `${this.baseUrl}/api/ybb/templates/${exportType}`
            : `${this.baseUrl}/api/ybb/templates`;

        const response = await fetch(url);
        return await response.json();
    }
}

// Usage
const exporter = new YBBExcelExporter();

// Export participants with detailed template
exporter.exportParticipants(participantData, {
    template: 'detailed',
    filename: 'ybb_participants_detailed_2024'
}).then(result => {
    console.log('Export completed:', result);
}).catch(error => {
    console.error('Export failed:', error);
});
```

### PHP Integration Example

```php
<?php
class YBBExcelExporter {
    private $baseUrl;
    private $timeout;

    public function __construct($baseUrl = 'https://ybb-data-management-service-production.up.railway.app', $timeout = 300) {
        $this->baseUrl = rtrim($baseUrl, '/');
        $this->timeout = $timeout;
    }

    public function exportParticipants($data, $options = []) {
        $defaultOptions = [
            'template' => 'standard',
            'format' => 'excel',
            'filename' => 'participants_export'
        ];

        $exportOptions = array_merge($defaultOptions, $options);
        $payload = array_merge(['data' => $data], $exportOptions);

        // Create export
        $ch = curl_init();
        curl_setopt_array($ch, [
            CURLOPT_URL => $this->baseUrl . '/api/ybb/export/participants',
            CURLOPT_POST => true,
            CURLOPT_POSTFIELDS => json_encode($payload),
            CURLOPT_HTTPHEADER => [
                'Content-Type: application/json',
                'Accept: application/json'
            ],
            CURLOPT_RETURNTRANSFER => true,
            CURLOPT_TIMEOUT => $this->timeout,
            CURLOPT_FOLLOWLOCATION => true
        ]);

        $response = curl_exec($ch);
        $httpCode = curl_getinfo($ch, CURLINFO_HTTP_CODE);
        curl_close($ch);

        if ($httpCode !== 200) {
            throw new Exception("Export creation failed with HTTP code: $httpCode");
        }

        $result = json_decode($response, true);

        if ($result['status'] === 'error') {
            throw new Exception("Export failed: " . $result['message']);
        }

        // Handle single file download
        if ($result['export_strategy'] === 'single_file') {
            return $this->downloadFile($result['data']['download_url'], $result['data']['file_name']);
        }

        // Handle large export with polling
        return $this->handleLargeExport($result['data']['export_id']);
    }

    private function downloadFile($url, $filename) {
        $ch = curl_init();
        curl_setopt_array($ch, [
            CURLOPT_URL => $this->baseUrl . $url,
            CURLOPT_RETURNTRANSFER => true,
            CURLOPT_FOLLOWLOCATION => true,
            CURLOPT_TIMEOUT => $this->timeout
        ]);

        $fileContent = curl_exec($ch);
        $httpCode = curl_getinfo($ch, CURLINFO_HTTP_CODE);
        curl_close($ch);

        if ($httpCode !== 200) {
            throw new Exception("File download failed with HTTP code: $httpCode");
        }

        // Trigger download in browser
        header('Content-Type: application/vnd.openxmlformats-officedocument.spreadsheetml.sheet');
        header('Content-Disposition: attachment; filename="' . $filename . '"');
        header('Content-Length: ' . strlen($fileContent));
        
        echo $fileContent;
        exit;
    }

    private function handleLargeExport($exportId) {
        $maxAttempts = 30;
        $attempts = 0;

        while ($attempts < $maxAttempts) {
            $ch = curl_init();
            curl_setopt_array($ch, [
                CURLOPT_URL => $this->baseUrl . "/api/ybb/export/$exportId/status",
                CURLOPT_RETURNTRANSFER => true,
                CURLOPT_TIMEOUT => 30
            ]);

            $response = curl_exec($ch);
            $status = json_decode($response, true);
            curl_close($ch);

            if ($status['status'] === 'completed') {
                if ($status['export_strategy'] === 'single_file') {
                    return $this->downloadFile($status['download_info']['single_file_url'], 
                                             $status['download_info']['file_name']);
                } else {
                    return $this->downloadFile("/api/ybb/export/$exportId/download/zip", 
                                             "export_$exportId.zip");
                }
            } else if ($status['status'] === 'failed') {
                throw new Exception("Export failed: " . $status['message']);
            }

            sleep(2);
            $attempts++;
        }

        throw new Exception('Export timeout - please try again');
    }
}

// Usage
try {
    $exporter = new YBBExcelExporter();
    
    $participants = [
        ['first_name' => 'John', 'last_name' => 'Doe', 'email' => 'john@test.com'],
        ['first_name' => 'Jane', 'last_name' => 'Smith', 'email' => 'jane@test.com']
    ];
    
    $exporter->exportParticipants($participants, [
        'template' => 'detailed',
        'filename' => 'ybb_participants_2024'
    ]);
    
} catch (Exception $e) {
    echo "Export failed: " . $e->getMessage();
}
?>
```

### Performance Best Practices

1. **Choose Appropriate Templates:**
   - Use `summary` template for large datasets (>10k records)
   - Use `detailed` template for comprehensive analysis (<5k records)
   - Use `standard` template for general purposes

2. **Handle Large Datasets:**
   - Implement chunked processing for datasets >5k records
   - Use status polling for exports that might take time
   - Consider filtering data before export to reduce size

3. **Optimize Client-Side:**
   - Show progress indicators for large exports
   - Implement retry logic for network failures
   - Cache template configurations to reduce API calls

4. **Error Handling:**
   - Always check export status before attempting download
   - Implement exponential backoff for polling
   - Provide meaningful error messages to users

---

## � Performance Metrics & Monitoring

### Understanding Export Metrics

All export responses include comprehensive performance metrics to help optimize exports and monitor system performance.

#### 🔍 **Memory Metrics**
- **`memory_used_mb`**: Actual memory consumed during export processing
- **`peak_memory_mb`**: Maximum memory usage reached during processing
- **`memory_efficiency_kb_per_record`**: Memory usage per processed record
- **`average_memory_peak_mb`**: Average memory usage per chunk (multi-file exports)

#### ⏱️ **Timing Metrics**
- **`processing_time_ms`**: Total processing time in milliseconds
- **`total_processing_time_seconds`**: Same as above in seconds format
- **`records_per_second`**: Processing throughput rate
- **`processing_ms_per_record`**: Time efficiency per individual record

#### 📁 **File & Compression Metrics**
- **`kb_per_record`**: File size efficiency (smaller is better)
- **`compression_ratio`**: Space saved by ZIP compression (multi-file exports)
- **`compression_efficiency`**: Percentage of space saved
- **`kb_per_record_compressed`**: File size after compression

#### 🎯 **Quality Indicators**

**Excellent Performance:**
- `records_per_second > 1500`
- `processing_ms_per_record < 0.5`
- `memory_efficiency_kb_per_record < 10`
- `compression_efficiency > 70%` (chunked exports)

**Good Performance:**
- `records_per_second > 1000`
- `processing_ms_per_record < 1.0`
- `memory_efficiency_kb_per_record < 20`
- `compression_efficiency > 50%`

**Needs Optimization:**
- `records_per_second < 500`
- `processing_ms_per_record > 2.0`
- `memory_efficiency_kb_per_record > 50`
- `compression_efficiency < 30%`

### Performance Optimization Tips

#### For Speed:
- Use `summary` template for large datasets
- Set smaller `chunk_size` (2000-3000)
- Process during off-peak hours
- Filter data before export

#### For Memory Efficiency:
- Use `standard` template instead of `complete`
- Enable chunking for datasets > 5000 records
- Monitor `peak_memory_mb` in responses

#### For Storage Efficiency:
- Use `detailed` or `complete` templates (compress better)
- Larger chunk sizes (5000-8000) for better compression
- Enable ZIP compression for multi-file exports

---

## �📋 Rate Limits & Performance

### System Limits

| Limit Type | Value | Description |
|------------|-------|-------------|
| Max Request Size | 100 MB | Maximum payload size per request |
| Max Records (Single File) | 25,000 | Global maximum for single file exports |
| Max Processing Time | 30 minutes | Maximum time allowed for export processing |
| Max Concurrent Exports | 10 per IP | Simultaneous export limit |
| File Retention | 7 days | How long export files are kept |
| Rate Limit | 100 requests/hour | API request limit per IP |

### Performance Guidelines

| Dataset Size | Recommended Template | Expected Processing Time | Memory Usage |
|--------------|---------------------|-------------------------|--------------|
| 1-1,000 records | Any template | < 1 second | 10-20 MB |
| 1,001-5,000 records | Standard/Detailed | 1-5 seconds | 20-50 MB |
| 5,001-15,000 records | Standard | 5-15 seconds | 50-100 MB |
| 15,001-50,000 records | Summary (chunked) | 15-60 seconds | 100-200 MB |

---

## � CodeIgniter 4 Frontend Integration

### Configuration Setup

Add the API configuration to your CodeIgniter 4 configuration:

```php
// app/Config/YbbExport.php
<?php

namespace Config;

use CodeIgniter\Config\BaseConfig;

class YbbExport extends BaseConfig
{
    public $baseUrl = 'https://ybb-data-management-service-production.up.railway.app';
    public $timeout = 120; // 2 minutes timeout
    public $maxRetries = 3;
    public $defaultBatchSize = 5000;
    
    // Template mapping
    public $templates = [
        'participants' => 'standard',
        'payments' => 'detailed', 
        'ambassadors' => 'summary'
    ];
}
```

### Service Integration Class

Create a service class to handle API interactions:

```php
// app/Services/YbbExportService.php
<?php

namespace App\Services;

use Config\YbbExport;
use CodeIgniter\HTTP\CURLRequest;

class YbbExportService
{
    protected $config;
    protected $client;
    
    public function __construct()
    {
        $this->config = config('YbbExport');
        $this->client = \Config\Services::curlrequest();
    }
    
    /**
     * Export participants with custom filename and options
     */
    public function exportParticipants($data, $options = [])
    {
        $payload = [
            'data' => $data,
            'template' => $options['template'] ?? 'standard',
            'format' => 'excel',
            'filename' => $this->generateFilename('participants', $options),
            'sheet_name' => $this->generateSheetName('participants'),
            'options' => [
                'batch_size' => $options['batch_size'] ?? $this->config->defaultBatchSize,
                'sort_by' => $options['sort_by'] ?? 'created_at',
                'sort_order' => $options['sort_order'] ?? 'desc'
            ]
        ];
        
        return $this->makeRequest('/api/ybb/export/participants', $payload);
    }
    
    /**
     * Check export status and handle polling
     */
    public function checkExportStatus($exportId)
    {
        $response = $this->client->get($this->config->baseUrl . "/api/ybb/export/{$exportId}/status", [
            'timeout' => 30,
            'headers' => [
                'Accept' => 'application/json'
            ]
        ]);
        
        return json_decode($response->getBody(), true);
    }
    
    /**
     * Download completed export file
     */
    public function downloadExport($exportId, $saveAs = null)
    {
        $response = $this->client->get($this->config->baseUrl . "/api/ybb/export/{$exportId}/download", [
            'timeout' => 300, // 5 minutes for large files
        ]);
        
        if ($response->getStatusCode() === 200) {
            $filename = $saveAs ?? $this->extractFilenameFromHeaders($response);
            
            // Save to writable directory
            $filepath = WRITEPATH . 'uploads/exports/' . $filename;
            
            // Ensure directory exists
            if (!is_dir(dirname($filepath))) {
                mkdir(dirname($filepath), 0755, true);
            }
            
            file_put_contents($filepath, $response->getBody());
            
            return [
                'success' => true,
                'filepath' => $filepath,
                'filename' => $filename,
                'size' => filesize($filepath)
            ];
        }
        
        return ['success' => false, 'error' => 'Download failed'];
    }
    
    /**
     * Handle export with polling for completion
     */
    public function exportWithPolling($type, $data, $options = [])
    {
        // Start export
        $exportResponse = $this->startExport($type, $data, $options);
        
        if (!$exportResponse['success']) {
            return $exportResponse;
        }
        
        $exportId = $exportResponse['export_id'];
        $maxAttempts = 60; // 5 minutes with 5-second intervals
        $attempt = 0;
        
        while ($attempt < $maxAttempts) {
            sleep(5); // Wait 5 seconds between checks
            
            $status = $this->checkExportStatus($exportId);
            
            if ($status['status'] === 'completed') {
                return [
                    'success' => true,
                    'export_id' => $exportId,
                    'file_name' => $status['data']['file_name'],
                    'download_url' => "/api/ybb/export/{$exportId}/download",
                    'processing_time' => $status['metadata']['processing_time'] ?? null
                ];
            }
            
            if ($status['status'] === 'failed') {
                return [
                    'success' => false,
                    'error' => $status['message'] ?? 'Export failed'
                ];
            }
            
            $attempt++;
        }
        
        return ['success' => false, 'error' => 'Export timeout'];
    }
    
    /**
     * Generate descriptive filename
     */
    private function generateFilename($type, $options = [])
    {
        $program = $options['program_name'] ?? 'YBB_Program';
        $filters = $options['filters'] ?? [];
        $date = date('d-m-Y');
        
        $program = preg_replace('/[^a-zA-Z0-9_-]/', '_', $program);
        $type = ucfirst($type);
        
        $filterDesc = '';
        if (!empty($filters)) {
            $filterDesc = '_' . implode('_', array_keys($filters));
        }
        
        return "{$program}_{$type}{$filterDesc}_{$date}.xlsx";
    }
    
    /**
     * Generate sheet name
     */
    private function generateSheetName($type)
    {
        $typeName = ucfirst($type);
        $monthYear = date('M Y');
        return substr("{$typeName} Data {$monthYear}", 0, 31);
    }
    
    /**
     * Make API request with error handling
     */
    private function makeRequest($endpoint, $payload)
    {
        try {
            $response = $this->client->post($this->config->baseUrl . $endpoint, [
                'json' => $payload,
                'timeout' => $this->config->timeout,
                'headers' => [
                    'Content-Type' => 'application/json',
                    'Accept' => 'application/json'
                ]
            ]);
            
            $statusCode = $response->getStatusCode();
            $body = json_decode($response->getBody(), true);
            
            if ($statusCode >= 200 && $statusCode < 300) {
                return array_merge(['success' => true], $body);
            } else {
                return [
                    'success' => false,
                    'error' => $body['message'] ?? 'API request failed',
                    'status_code' => $statusCode
                ];
            }
            
        } catch (\Exception $e) {
            log_message('error', 'YBB Export API Error: ' . $e->getMessage());
            return [
                'success' => false,
                'error' => 'Network error: ' . $e->getMessage()
            ];
        }
    }
}
```

### Controller Implementation Example

```php
// app/Controllers/ExportController.php
<?php

namespace App\Controllers;

use App\Services\YbbExportService;
use CodeIgniter\HTTP\ResponseInterface;

class ExportController extends BaseController
{
    protected $exportService;
    
    public function __construct()
    {
        $this->exportService = new YbbExportService();
    }
    
    /**
     * Export participants with AJAX handling
     */
    public function exportParticipants()
    {
        if (!$this->request->isAJAX()) {
            return $this->response->setStatusCode(400)->setJSON(['error' => 'AJAX only']);
        }
        
        $data = $this->request->getJSON(true);
        
        // Validate required data
        if (empty($data['participants'])) {
            return $this->response->setStatusCode(400)->setJSON([
                'error' => 'Participants data is required'
            ]);
        }
        
        $options = [
            'template' => $data['template'] ?? 'standard',
            'program_name' => $data['program_name'] ?? 'YBB_Program',
            'filters' => $data['filters'] ?? [],
            'batch_size' => $data['batch_size'] ?? 5000
        ];
        
        $result = $this->exportService->exportWithPolling(
            'participants', 
            $data['participants'], 
            $options
        );
        
        if ($result['success']) {
            return $this->response->setJSON([
                'success' => true,
                'export_id' => $result['export_id'],
                'download_url' => base_url('export/download/' . $result['export_id']),
                'file_name' => $result['file_name'],
                'processing_time' => $result['processing_time']
            ]);
        } else {
            return $this->response->setStatusCode(500)->setJSON([
                'error' => $result['error']
            ]);
        }
    }
    
    /**
     * Handle file download
     */
    public function downloadFile($exportId)
    {
        $result = $this->exportService->downloadExport($exportId);
        
        if ($result['success']) {
            return $this->response->download($result['filepath'], null)
                                 ->setFileName($result['filename']);
        } else {
            throw new \CodeIgniter\Exceptions\PageNotFoundException('Export file not found');
        }
    }
}
```

### Frontend JavaScript Integration

```javascript
// assets/js/ybb-export.js
class YbbExportManager {
    constructor(baseUrl) {
        this.baseUrl = baseUrl;
        this.activeExports = new Map();
    }
    
    /**
     * Start export with progress tracking
     */
    async startExport(type, data, options = {}) {
        const exportButton = document.getElementById('export-btn');
        const progressContainer = document.getElementById('export-progress');
        
        // Disable export button
        exportButton.disabled = true;
        exportButton.textContent = 'Exporting...';
        
        // Show progress container
        progressContainer.style.display = 'block';
        this.updateProgress(0, 'Starting export...');
        
        try {
            const response = await fetch(`${this.baseUrl}/export/exportParticipants`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-Requested-With': 'XMLHttpRequest'
                },
                body: JSON.stringify({
                    participants: data,
                    template: options.template || 'standard',
                    program_name: options.programName || 'YBB_Program',
                    filters: options.filters || {},
                    batch_size: options.batchSize || 5000
                })
            });
            
            const result = await response.json();
            
            if (result.success) {
                this.updateProgress(100, 'Export completed!');
                this.showDownloadLink(result.download_url, result.file_name);
                
                // Show processing time if available
                if (result.processing_time) {
                    this.showProcessingInfo(result.processing_time);
                }
            } else {
                this.showError(result.error);
            }
            
        } catch (error) {
            this.showError('Network error: ' + error.message);
        } finally {
            // Re-enable export button
            exportButton.disabled = false;
            exportButton.textContent = 'Export Data';
        }
    }
    
    updateProgress(percent, message) {
        const progressBar = document.getElementById('progress-bar');
        const progressText = document.getElementById('progress-text');
        
        progressBar.style.width = percent + '%';
        progressText.textContent = message;
    }
    
    showDownloadLink(url, filename) {
        const container = document.getElementById('download-container');
        container.innerHTML = `
            <div class="alert alert-success">
                <h5>Export Complete!</h5>
                <p>Your export file is ready for download.</p>
                <a href="${url}" class="btn btn-primary" download="${filename}">
                    <i class="fas fa-download"></i> Download ${filename}
                </a>
            </div>
        `;
        container.style.display = 'block';
    }
    
    showError(message) {
        const container = document.getElementById('error-container');
        container.innerHTML = `
            <div class="alert alert-danger">
                <h5>Export Failed</h5>
                <p>${message}</p>
            </div>
        `;
        container.style.display = 'block';
    }
    
    showProcessingInfo(processingTime) {
        const container = document.getElementById('processing-info');
        container.innerHTML = `
            <div class="alert alert-info">
                <small>Processing completed in ${processingTime}</small>
            </div>
        `;
    }
}

// Initialize export manager
const exportManager = new YbbExportManager('/your-codeigniter-base-url');

// Example usage
document.getElementById('export-btn').addEventListener('click', function() {
    const participantData = getParticipantData(); // Your data collection function
    const options = {
        template: document.getElementById('template-select').value,
        programName: document.getElementById('program-name').value,
        filters: getActiveFilters(), // Your filter collection function
        batchSize: parseInt(document.getElementById('batch-size').value) || 5000
    };
    
    exportManager.startExport('participants', participantData, options);
});
```

### Routes Configuration

```php
// app/Config/Routes.php
$routes->group('export', function($routes) {
    $routes->post('exportParticipants', 'ExportController::exportParticipants');
    $routes->post('exportPayments', 'ExportController::exportPayments');
    $routes->post('exportAmbassadors', 'ExportController::exportAmbassadors');
    $routes->get('download/(:segment)', 'ExportController::downloadFile/$1');
    $routes->get('status/(:segment)', 'ExportController::checkStatus/$1');
});
```

---

## �🔒 Security Considerations

### Data Protection
- All exports contain potentially sensitive data
- Implement proper access controls in your application
- Consider data encryption for highly sensitive exports
- Audit export activities for compliance

### Best Practices
- Validate all input data before sending to API
- Implement proper error handling to avoid data leaks
- Use HTTPS for all API communications
- Consider implementing API key authentication for production

### Compliance
- Ensure exported data complies with GDPR, CCPA, and other regulations
- Implement data retention policies aligned with legal requirements
- Provide data export/deletion capabilities for user requests

---

This comprehensive documentation covers all Excel export functionality available in the YBB Data Management Service API. For additional support or feature requests, please contact the development team.

**Last Updated:** August 25, 2025
**API Version:** 1.0.0
**Documentation Version:** 2.0.0