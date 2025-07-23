# Python Flask Service - Data Export Specification

## Overview
This document specifies the data structure, filtering options, and statuses for the Python Flask service that will handle data processing, transformation, and Excel export for the YBB Web Admin system.

## Data Entities

### 1. Participants

#### Core Data Structure
```json
{
  "id": "integer",
  "user_id": "integer",
  "account_id": "string",
  "full_name": "string",
  "email": "string (from users table)",
  "gender": "string",
  "birthdate": "date",
  "nationality": "string",
  "nationality_flag": "string",
  "nationality_code": "string",
  "occupation": "string",
  "education_level": "string",
  "major": "string",
  "institution": "string",
  "organizations": "string",
  "phone_number": "string",
  "country_code": "string",
  "current_address": "string",
  "origin_address": "string",
  "picture_url": "string",
  "instagram_account": "string",
  "emergency_contact": "string",
  "contact_relation": "string",
  "disease_history": "string",
  "tshirt_size": "string",
  "category": "string", // fully_funded, self_funded
  "experiences": "text",
  "achievements": "text",
  "resume_url": "string",
  "knowledge_source": "string",
  "source_account_name": "string",
  "twibbon_link": "string",
  "requirement_link": "string",
  "ref_code_ambassador": "string",
  "program_id": "integer",
  "is_active": "integer",
  "is_deleted": "integer",
  "created_at": "datetime",
  "updated_at": "datetime"
}
```

#### Related Data
- **User Data**: Email, login information
- **Essays**: Participant essays/submissions
- **Status**: Current participant status
- **Payments**: Payment history

#### Filtering Options
- **Category**: `fully_funded`, `self_funded`
- **Form Status**: `0` (Not Started), `1` (On Progress), `2` (Submitted)
- **Payment Status**: Based on successful payments
- **Program Payment Type**: Filter by specific payment categories
- **Date Range**: Registration date filtering
- **Limit**: Record count limitations
- **Ambassador**: Filter by referring ambassador

#### Status System
**Form Status**:
- `0` = Not Started
- `1` = On Progress  
- `2` = Submitted

**General Status**:
- `0` = Not Started
- `1` = In Progress
- `2` = Completed

**Document Status**:
- `0` = Not Started
- `1` = On Progress
- `2` = Submitted

### 2. Payments

#### Core Data Structure
```json
{
  "id": "integer",
  "participant_id": "integer",
  "program_payment_id": "integer",
  "payment_method_id": "integer",
  "transaction_code": "string",
  "order_id": "string",
  "payment_date": "datetime",
  "amount": "decimal",
  "usd_amount": "decimal",
  "currency": "string",
  "status": "integer",
  "proof_url": "string",
  "account_name": "string",
  "source_name": "string",
  "notes": "text",
  "rejection_reason": "string",
  "payment_url": "string",
  "is_active": "integer",
  "is_deleted": "integer",
  "created_at": "datetime",
  "updated_at": "datetime"
}
```

#### Related Data
- **Participant**: Full participant details
- **Program Payment**: Payment category information
- **Payment Method**: Payment method details

#### Payment Status Values
- `0` = Created
- `1` = Pending
- `2` = Success
- `3` = Cancelled
- `4` = Rejected

#### Payment Method Values
- `1` = Midtrans (Digital payment)
- `2` = Manual Transfer

#### Filtering Options
- **Status**: Filter by payment status
- **Payment Method**: Filter by payment method
- **Date Range**: Payment date filtering
- **Amount Range**: Filter by payment amount
- **Currency**: Filter by payment currency
- **Program Payment Category**: Filter by payment type

### 3. Ambassadors

#### Core Data Structure
```json
{
  "id": "integer",
  "name": "string",
  "email": "string",
  "ref_code": "string",
  "program_id": "integer",
  "institution": "string",
  "gender": "string",
  "phone_number": "string",
  "notes": "text",
  "is_active": "integer",
  "is_deleted": "integer",
  "created_at": "datetime",
  "updated_at": "datetime"
}
```

#### Related Data
- **Referrals**: List of referred participants
- **Referral Count**: Total number of referrals

#### Filtering Options
- **Status**: `is_active` (1 = Active, 0 = Inactive)
- **Program**: Filter by program
- **Referral Count**: Filter by number of referrals
- **Date Range**: Registration date filtering

## Export Types and Templates

### 1. Participants Export

#### Standard Export Fields
- Order Number
- Full Name
- Email
- Nationality/Country
- Institution
- Phone Number
- Category (Fully Funded/Self Funded)
- Form Status
- Payment Status
- Registration Date
- Ambassador Reference

#### Detailed Export Fields (Additional)
- Gender
- Birthdate
- Education Level
- Major
- Current Address
- Origin Address
- Emergency Contact
- T-shirt Size
- Instagram Account
- Essays/Submissions
- Payment History

### 2. Payments Export

#### Standard Export Fields
- Payment ID
- Participant Name
- Participant Email
- Payment Amount
- Currency
- USD Amount
- Payment Status
- Payment Method
- Payment Date
- Transaction Code
- Order ID

#### Detailed Export Fields (Additional)
- Payment Category
- Account Name
- Source Name
- Proof URL
- Notes
- Rejection Reason
- Program Information

### 3. Ambassadors Export

#### Standard Export Fields
- Ambassador Name
- Email
- Reference Code
- Institution
- Total Referrals
- Active Status
- Registration Date

#### Detailed Export Fields (Additional)
- Gender
- Phone Number
- Notes
- Referral List (Names and emails)
- Referral Success Rate

## API Request Structure

### Base Request Format
```json
{
  "export_type": "participants|payments|ambassadors",
  "program_id": "integer",
  "format": "excel|csv|pdf",
  "template": "standard|detailed|custom",
  "filters": {
    // Type-specific filters
  },
  "options": {
    "include_related": "boolean",
    "batch_size": "integer",
    "sort_by": "string",
    "sort_order": "asc|desc"
  }
}
```

### Participants Export Request
```json
{
  "export_type": "participants",
  "program_id": 1,
  "format": "excel",
  "template": "detailed",
  "filters": {
    "category": "fully_funded|self_funded|all",
    "form_status": "0|1|2|all",
    "payment_status": "success|pending|all",
    "program_payment_id": "integer|all",
    "date_range": {
      "start": "YYYY-MM-DD",
      "end": "YYYY-MM-DD"
    },
    "ambassador_ref": "string|all",
    "limit": "integer"
  },
  "options": {
    "include_essays": true,
    "include_payments": true,
    "include_status": true
  }
}
```

### Payments Export Request
```json
{
  "export_type": "payments",
  "program_id": 1,
  "format": "excel",
  "template": "standard",
  "filters": {
    "status": "0|1|2|3|4|all",
    "payment_method": "1|2|all",
    "payment_category": "registration|program_fee_1|etc|all",
    "date_range": {
      "start": "YYYY-MM-DD",
      "end": "YYYY-MM-DD"
    },
    "amount_range": {
      "min": "decimal",
      "max": "decimal"
    },
    "currency": "USD|IDR|etc|all"
  },
  "options": {
    "include_participant_details": true,
    "group_by_participant": false
  }
}
```

### Ambassadors Export Request
```json
{
  "export_type": "ambassadors",
  "program_id": 1,
  "format": "excel",
  "template": "detailed",
  "filters": {
    "status": "1|0|all",
    "min_referrals": "integer",
    "date_range": {
      "start": "YYYY-MM-DD", 
      "end": "YYYY-MM-DD"
    }
  },
  "options": {
    "include_referral_details": true,
    "include_referral_success_rate": true
  }
}
```

## Response Format

### Success Response (Small to Medium Datasets)
```json
{
  "status": "success",
  "message": "Export completed successfully",
  "data": {
    "file_url": "string",
    "file_name": "string",
    "file_size": "integer",
    "record_count": "integer",
    "export_id": "string",
    "expires_at": "datetime"
  },
  "metadata": {
    "export_type": "string",
    "template": "string",
    "filters_applied": "object",
    "generated_at": "datetime",
    "processing_time": "float"
  }
}
```

### Success Response (Large Datasets - Multi-file)
```json
{
  "status": "success", 
  "message": "Large export completed successfully",
  "export_strategy": "multi_file",
  "data": {
    "export_id": "string",
    "total_records": "integer",
    "total_files": "integer",
    "individual_files": [
      {
        "batch_number": 1,
        "file_name": "participants_batch_1_of_5.xlsx",
        "file_url": "string",
        "file_size": "integer",
        "record_count": "integer",
        "record_range": "1-10000"
      }
    ],
    "archive": {
      "zip_file_name": "participants_complete_export.zip",
      "zip_file_url": "string", 
      "zip_file_size": "integer",
      "compression_ratio": "string"
    },
    "expires_at": "datetime"
  },
  "metadata": {
    "export_type": "string",
    "template": "string",
    "chunk_size": "integer",
    "compression_used": "string",
    "processing_time": "float",
    "memory_peak": "string"
  }
}
```

### Processing Response (Large Datasets)
```json
{
  "status": "processing",
  "message": "Large export is being processed",
  "data": {
    "export_id": "string",
    "estimated_completion": "datetime",
    "estimated_size": "string",
    "queue_position": "integer"
  },
  "progress": {
    "stage": "data_retrieval|processing|file_generation|compression",
    "percentage": "float",
    "current_chunk": "integer",
    "total_chunks": "integer",
    "records_processed": "integer",
    "total_records": "integer",
    "current_operation": "string"
  }
}
```

### Error Response
```json
{
  "status": "error",
  "message": "Error description",
  "error_code": "string",
  "details": {
    "field": "error_details",
    "record_count": "integer",
    "memory_exceeded": "boolean",
    "suggested_chunk_size": "integer"
  },
  "recovery_options": {
    "retry_with_smaller_chunks": "boolean",
    "use_multi_file_strategy": "boolean",
    "filter_suggestions": "array"
  }
}
```

## System Configuration for Large Datasets

### Resource Limits and Thresholds
```json
{
  "system_limits": {
    "max_records_single_file": 25000,
    "max_records_immediate_processing": 1000,
    "max_file_size_mb": 50,
    "max_memory_usage_gb": 2,
    "max_processing_time_minutes": 30,
    "max_concurrent_large_exports": 3,
    "file_retention_days": 7
  },
  "chunk_configurations": {
    "default_chunk_size": 10000,
    "min_chunk_size": 1000,
    "max_chunk_size": 25000,
    "memory_based_chunking": true,
    "adaptive_chunk_sizing": true
  },
  "format_limits": {
    "excel": {
      "max_rows_per_sheet": 1048576,
      "max_sheets_per_file": 10,
      "recommended_rows_per_sheet": 100000
    },
    "csv": {
      "no_row_limit": true,
      "recommended_chunk_size": 50000
    },
    "pdf": {
      "max_rows_recommended": 5000,
      "max_pages": 1000
    }
  }
}
```

### Export Queue Management
```json
{
  "queue_config": {
    "max_queue_size": 50,
    "priority_levels": {
      "immediate": "< 1000 records",
      "high": "1000-10000 records", 
      "normal": "10000-50000 records",
      "low": "> 50000 records"
    },
    "concurrent_processing": {
      "immediate": 10,
      "high": 5,
      "normal": 3,
      "low": 1
    },
    "timeout_settings": {
      "immediate": "5 minutes",
      "high": "15 minutes", 
      "normal": "30 minutes",
      "low": "60 minutes"
    }
  }
}
```

### Monitoring and Alerts
```json
{
  "monitoring": {
    "performance_metrics": [
      "records_per_second",
      "memory_usage_peak",
      "processing_time",
      "file_generation_time",
      "compression_time"
    ],
    "alert_thresholds": {
      "memory_usage_warning": "80%",
      "memory_usage_critical": "95%",
      "processing_time_warning": "25 minutes",
      "queue_length_warning": 40,
      "failed_exports_threshold": 5
    },
    "logging_levels": {
      "chunk_processing": "info",
      "memory_usage": "debug",
      "performance_metrics": "info",
      "errors": "error"
    }
  }
}
```

## Dynamic Export Configuration

### Template System
```json
{
  "templates": {
    "participants_standard": {
      "fields": ["id", "full_name", "email", "nationality", "institution", "category", "form_status", "created_at"],
      "headers": ["ID", "Full Name", "Email", "Country", "Institution", "Category", "Form Status", "Registration Date"],
      "max_records_single_file": 15000
    },
    "participants_detailed": {
      "fields": ["id", "full_name", "email", "gender", "birthdate", "nationality", "institution", "phone_number", "category", "form_status", "payment_status", "created_at"],
      "headers": ["ID", "Full Name", "Email", "Gender", "Birth Date", "Country", "Institution", "Phone", "Category", "Form Status", "Payment Status", "Registration Date"],
      "include_related": ["essays", "payments", "status"],
      "max_records_single_file": 10000,
      "recommended_chunk_size": 5000
    },
    "participants_summary": {
      "fields": ["full_name", "email", "nationality", "category", "form_status"],
      "headers": ["Name", "Email", "Country", "Category", "Status"],
      "max_records_single_file": 50000,
      "optimized_for_large_datasets": true
    }
  }
}
```

### Custom Field Mapping
```json
{
  "field_mappings": {
    "participants": {
      "id": "participant_id",
      "full_name": "name",
      "nationality": "country",
      "created_at": "registration_date"
    },
    "payments": {
      "id": "payment_id", 
      "amount": "payment_amount",
      "created_at": "payment_date"
    }
  },
  "data_transformations": {
    "date_format": "YYYY-MM-DD",
    "currency_format": "#,##0.00",
    "boolean_format": "Yes/No",
    "null_values": "N/A"
  }
}
```

## Large Dataset Handling

### Dataset Size Categories
- **Small**: < 1,000 records - Single file, immediate processing
- **Medium**: 1,000 - 10,000 records - Single file, background processing
- **Large**: 10,000 - 50,000 records - Chunked processing, compression
- **Extra Large**: 50,000+ records - Multi-file export or streaming

### Large Dataset Processing Strategies

#### 1. Multi-File Export (Recommended for 50k+ records)
```json
{
  "export_strategy": "multi_file",
  "chunk_size": 10000,
  "response": {
    "status": "success",
    "export_type": "multi_file",
    "files": [
      {
        "file_name": "participants_batch_1_of_6.xlsx",
        "file_url": "https://api.example.com/exports/files/exp123_batch1.xlsx",
        "record_range": "1-10000",
        "file_size": "15MB"
      },
      {
        "file_name": "participants_batch_2_of_6.xlsx", 
        "file_url": "https://api.example.com/exports/files/exp123_batch2.xlsx",
        "record_range": "10001-20000",
        "file_size": "15MB"
      }
    ],
    "total_records": 52000,
    "total_batches": 6,
    "zip_archive": {
      "file_name": "participants_complete_export.zip",
      "file_url": "https://api.example.com/exports/files/exp123_complete.zip",
      "file_size": "85MB"
    }
  }
}
```

#### 2. Streaming Export (Alternative for very large datasets)
```json
{
  "export_strategy": "streaming",
  "response": {
    "status": "processing",
    "stream_url": "https://api.example.com/exports/stream/exp123",
    "content_type": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    "estimated_size": "120MB",
    "estimated_records": 52000
  }
}
```

#### 3. Compressed Single File (For datasets 10k-50k)
```json
{
  "export_strategy": "compressed_single",
  "compression": "gzip",
  "response": {
    "file_name": "participants_export_compressed.xlsx.gz",
    "file_url": "https://api.example.com/exports/files/exp123.xlsx.gz",
    "uncompressed_size": "45MB",
    "compressed_size": "12MB",
    "compression_ratio": "73%"
  }
}
```

### Export Strategy Selection Logic
```json
{
  "strategy_rules": {
    "record_count < 1000": "immediate_single_file",
    "1000 <= record_count < 10000": "background_single_file", 
    "10000 <= record_count < 25000": "compressed_single_file",
    "25000 <= record_count < 50000": "multi_file_small_chunks",
    "record_count >= 50000": "multi_file_large_chunks_or_streaming"
  },
  "chunk_sizes": {
    "small_chunks": 5000,
    "medium_chunks": 10000,
    "large_chunks": 15000
  }
}
```

### Memory Management for Large Datasets

#### 1. Chunked Data Processing
```python
# Example processing approach
def process_large_dataset(data_query, chunk_size=10000):
    total_records = get_total_count(data_query)
    chunks = ceil(total_records / chunk_size)
    
    for chunk_num in range(chunks):
        offset = chunk_num * chunk_size
        chunk_data = get_data_chunk(data_query, offset, chunk_size)
        yield process_chunk(chunk_data, chunk_num + 1, chunks)
```

#### 2. Memory Optimization Techniques
- **Generator-based processing**: Yield data chunks instead of loading all in memory
- **Database cursor streaming**: Use database cursors for large result sets
- **Garbage collection**: Explicit memory cleanup between chunks
- **Temporary file cleanup**: Remove intermediate files immediately after use

### Large Dataset Request Format
```json
{
  "export_type": "participants",
  "program_id": 1,
  "format": "excel",
  "template": "detailed",
  "large_dataset_options": {
    "strategy": "auto|multi_file|streaming|compressed",
    "chunk_size": 10000,
    "max_file_size": "50MB",
    "compression": "gzip|zip|none",
    "parallel_processing": true,
    "memory_limit": "1GB"
  },
  "delivery_options": {
    "create_zip_archive": true,
    "email_notification": true,
    "email_address": "admin@example.com",
    "retention_days": 7
  }
}
```

### Progress Tracking for Large Exports
```json
{
  "export_id": "exp_123456",
  "status": "processing",
  "progress": {
    "current_chunk": 3,
    "total_chunks": 6,
    "records_processed": 25000,
    "total_records": 52000,
    "percentage": 48.1,
    "estimated_completion": "2025-07-23T15:30:00Z",
    "current_operation": "Processing chunk 3: records 20001-30000"
  },
  "performance": {
    "processing_speed": "2500 records/minute",
    "elapsed_time": "10 minutes",
    "estimated_remaining": "11 minutes"
  }
}
```

## Implementation Guidelines

### 1. Data Processing
- **Chunked processing**: Process data in configurable chunks (5k-15k records)
- **Memory streaming**: Use generators and iterators to avoid loading full datasets
- **Database optimization**: Use indexed queries and efficient joins
- **Parallel processing**: Process multiple chunks simultaneously when possible
- **Caching strategy**: Cache frequently requested export configurations
- **Memory monitoring**: Track and limit memory usage during processing

### 2. File Generation
- **Format-specific optimization**: Excel has 1M row limit, CSV has no practical limit
- **Dynamic file splitting**: Split large Excel files into multiple sheets or files
- **Compression options**: Offer GZIP or ZIP compression for large files
- **Incremental writing**: Write data to files as it's processed, not all at once
- **File size monitoring**: Monitor file sizes and split when approaching limits
- **Metadata tracking**: Include record counts and ranges in file names

### 3. Performance Optimization
- **Asynchronous processing**: All large exports should be background jobs
- **Queue management**: Implement job queues with priority levels
- **Resource pooling**: Database connection pooling for concurrent processing
- **Cleanup automation**: Automatic cleanup of temporary files and expired exports
- **Progress tracking**: Real-time progress updates for long-running exports
- **Error recovery**: Resume capability for failed large exports

### 4. Security
- Validate all input parameters
- Sanitize data before export
- Secure file storage and access
- Authentication/authorization checks

### 5. Error Handling
- Graceful handling of data inconsistencies
- Detailed error reporting
- Retry mechanisms for failed exports
- Logging and monitoring

## Integration Points

### PHP to Python API Calls

#### Small Dataset Export (Immediate Processing)
```php
// Example PHP integration for small datasets
$exportData = [
    'export_type' => 'participants',
    'program_id' => $programId,
    'format' => 'excel',
    'template' => 'standard',
    'filters' => $filters
];

$response = $this->callPythonExportService($exportData);

if ($response['status'] === 'success') {
    // Direct download
    return redirect($response['data']['file_url']);
}
```

#### Large Dataset Export (Background Processing)
```php
// Example PHP integration for large datasets
$exportData = [
    'export_type' => 'participants',
    'program_id' => $programId,
    'format' => 'excel', 
    'template' => 'detailed',
    'filters' => $filters,
    'large_dataset_options' => [
        'strategy' => 'auto',
        'chunk_size' => 10000,
        'create_zip_archive' => true,
        'email_notification' => true,
        'email_address' => session('user_email')
    ]
];

$response = $this->callPythonExportService($exportData);

if ($response['status'] === 'processing') {
    // Store export ID for tracking
    session()->set('pending_export_id', $response['data']['export_id']);
    
    // Redirect to progress page
    return redirect()->to('export/progress/' . $response['data']['export_id'])
        ->with('message', 'Large export is being processed. You will be notified when complete.');
}
```

#### Export Progress Tracking
```php
// Check export progress
public function checkExportProgress($exportId)
{
    $response = $this->callPythonExportService(null, 'GET', "/api/export/{$exportId}/status");
    
    if ($response['status'] === 'processing') {
        return $this->response->setJSON([
            'status' => 'processing',
            'progress' => $response['progress'],
            'message' => $response['progress']['current_operation']
        ]);
    } elseif ($response['status'] === 'success') {
        return $this->response->setJSON([
            'status' => 'completed',
            'download_options' => $response['data'],
            'message' => 'Export completed successfully'
        ]);
    }
}
```

#### Multi-file Download Handling
```php
// Handle multi-file downloads
public function downloadExportFiles($exportId)
{
    $response = $this->callPythonExportService(null, 'GET', "/api/export/{$exportId}/status");
    
    if ($response['export_strategy'] === 'multi_file') {
        // Offer download options
        $data = [
            'export_id' => $exportId,
            'individual_files' => $response['data']['individual_files'],
            'zip_archive' => $response['data']['archive'],
            'total_records' => $response['data']['total_records']
        ];
        
        return view('export/download_options', $data);
    } else {
        // Single file download
        return redirect($response['data']['file_url']);
    }
}
```

#### Error Handling for Large Exports
```php
// Handle export errors with recovery options
public function handleExportError($exportId)
{
    $response = $this->callPythonExportService(null, 'GET', "/api/export/{$exportId}/status");
    
    if ($response['status'] === 'error') {
        $errorDetails = $response['details'];
        
        if ($errorDetails['memory_exceeded']) {
            // Suggest smaller chunk size
            $suggestedFilters = $this->getOriginalFilters($exportId);
            $suggestedFilters['limit'] = $errorDetails['suggested_chunk_size'];
            
            return view('export/retry_options', [
                'original_export_id' => $exportId,
                'suggested_filters' => $suggestedFilters,
                'error_message' => $response['message'],
                'recovery_options' => $response['recovery_options']
            ]);
        }
    }
}
```

#### Background Job Integration  
```php
// Queue large export as background job
public function queueLargeExport($exportData)
{
    // Estimate export size first
    $estimate = $this->callPythonExportService($exportData, 'POST', '/api/export/estimate');
    
    if ($estimate['estimated_records'] > 25000) {
        // Queue as background job
        $job = new ExportJob($exportData);
        $this->queue->push($job);
        
        return redirect()->to('export/queued')
            ->with('message', 'Large export has been queued for processing');
    } else {
        // Process immediately
        return $this->processExport($exportData);
    }
}
```

### Python Service Endpoints
- `POST /api/export` - Main export endpoint
- `GET /api/export/{export_id}/status` - Check export status and progress
- `GET /api/export/{export_id}/download` - Download single file
- `GET /api/export/{export_id}/download/batch/{batch_number}` - Download specific batch file
- `GET /api/export/{export_id}/download/zip` - Download complete ZIP archive
- `DELETE /api/export/{export_id}` - Clean up export files
- `GET /api/templates` - Get available templates
- `POST /api/templates` - Create custom template
- `GET /api/export/stats` - Get system export statistics and limits

### Large Dataset Specific Endpoints
- `POST /api/export/estimate` - Estimate export size and processing time
- `GET /api/export/{export_id}/chunks` - List all available chunks for download
- `POST /api/export/{export_id}/resume` - Resume failed large export
- `GET /api/export/queue/status` - Check export queue status and position

This specification provides a complete framework for implementing a dynamic, scalable export system that can easily accommodate new data types and export formats in the future.
