# YBB Export API - CodeIgniter Integration Documentation

## API Overview

The YBB Export API is a Python Flask service that handles data export operations for participants, payments, and ambassadors data. It provides efficient processing of large datasets with automatic chunking and professional Excel formatting.

**Base URL**: `http://localhost:5000` (development) / `https://api.ybb-exports.your-domain.com` (production)

---

## 🔗 API Endpoints Reference

### 1. Health Check

**Endpoint**: `GET /health`

**Purpose**: Verify API service is running

**Request**: No body required

**Response**:
```json
{
  "status": "healthy",
  "timestamp": "2025-07-23T16:27:55.123456",
  "service": "YBB Data Processing Service",
  "version": "1.0.0"
}
```

**CodeIgniter Example**:
```php
$response = file_get_contents('http://localhost:5000/health');
$health = json_decode($response, true);
if ($health['status'] === 'healthy') {
    echo "API is running";
}
```

---

### 2. Export Participants

**Endpoint**: `POST /api/ybb/export/participants`

**Purpose**: Export participant data to Excel/CSV

**Request Headers**:
```
Content-Type: application/json
```

**Request Body**:
```json
{
  "data": [
    {
      "id": 1,
      "form_id": "YBB2024_001",
      "first_name": "John",
      "last_name": "Doe",
      "email": "john.doe@example.com",
      "phone": "+1234567890",
      "birthdate": "1995-05-15",
      "nationality": "American",
      "state": "California",
      "form_status": 1,
      "is_active": 1,
      "created_at": "2024-01-15 10:30:00",
      "updated_at": "2024-01-15 10:30:00"
    }
  ],
  "template": "standard",
  "format": "excel",
  "filename": "participants_export.xlsx",
  "sheet_name": "Participants"
}
```

**Request Parameters**:
- `data` (required): Array of participant objects
- `template` (optional): "standard", "detailed", "summary", "complete" (default: "standard")
- `format` (optional): "excel", "csv" (default: "excel")
- `filename` (optional): Custom filename
- `sheet_name` (optional): Excel sheet name

**Success Response (< 5,000 records)**:
```json
{
  "status": "success",
  "message": "Export completed successfully",
  "data": {
    "export_id": "ac9433a4-a37a-499d-a92f-e4e6163c5ef7",
    "file_name": "participants_export.xlsx",
    "file_size": 5386,
    "record_count": 3,
    "download_url": "/api/export/ac9433a4-a37a-499d-a92f-e4e6163c5ef7/download",
    "expires_at": "2025-07-24T16:27:57.800548"
  },
  "metadata": {
    "export_type": "participants",
    "template": "standard",
    "filters_applied": {},
    "generated_at": "2025-07-23T16:27:57.800548",
    "processing_time": 0.5
  }
}
```

**Success Response (> 5,000 records - Multi-file)**:
```json
{
  "status": "success",
  "message": "Large export completed successfully",
  "export_strategy": "multi_file",
  "data": {
    "export_id": "116bf7a1-1137-4a7b-a6d0-d475dcc84f47",
    "total_records": 6000,
    "total_files": 3,
    "individual_files": [
      {
        "batch_number": 1,
        "file_name": "participants_complete_batch_1_of_3_20250723_162810.xlsx",
        "file_size": 89456,
        "record_count": 2000,
        "record_range": "1-2000",
        "download_url": "/api/export/116bf7a1-1137-4a7b-a6d0-d475dcc84f47/download/batch/1"
      },
      {
        "batch_number": 2,
        "file_name": "participants_complete_batch_2_of_3_20250723_162810.xlsx",
        "file_size": 89456,
        "record_count": 2000,
        "record_range": "2001-4000",
        "download_url": "/api/export/116bf7a1-1137-4a7b-a6d0-d475dcc84f47/download/batch/2"
      },
      {
        "batch_number": 3,
        "file_name": "participants_complete_batch_3_of_3_20250723_162810.xlsx",
        "file_size": 89456,
        "record_count": 2000,
        "record_range": "4001-6000",
        "download_url": "/api/export/116bf7a1-1137-4a7b-a6d0-d475dcc84f47/download/batch/3"
      }
    ],
    "archive": {
      "zip_file_name": "participants_complete_export_20250723_162810.zip",
      "zip_file_size": 88655,
      "download_url": "/api/export/116bf7a1-1137-4a7b-a6d0-d475dcc84f47/download/zip",
      "compression_ratio": "86.5%"
    },
    "expires_at": "2025-07-24T16:28:10.553628"
  },
  "metadata": {
    "export_type": "participants",
    "template": "complete",
    "chunk_size": 2000,
    "compression_used": "zip",
    "processing_time": 8.6,
    "memory_peak": "200MB"
  }
}
```

**CodeIgniter Example**:
```php
// Get participants data from your model
$participants = $this->Participant_model->get_all_participants();

// Prepare API request
$data = array(
    'data' => $participants,
    'template' => 'standard',
    'format' => 'excel',
    'filename' => 'participants_' . date('Y-m-d') . '.xlsx'
);

// Make API call
$curl = curl_init();
curl_setopt_array($curl, array(
    CURLOPT_URL => 'http://localhost:5000/api/ybb/export/participants',
    CURLOPT_RETURNTRANSFER => true,
    CURLOPT_POST => true,
    CURLOPT_POSTFIELDS => json_encode($data),
    CURLOPT_HTTPHEADER => array('Content-Type: application/json')
));

$response = curl_exec($curl);
$result = json_decode($response, true);
curl_close($curl);

if ($result['status'] === 'success') {
    $export_id = $result['data']['export_id'];
    // Store export_id for download
    redirect('exports/download/' . $export_id);
}
```

---

### 3. Export Payments

**Endpoint**: `POST /api/ybb/export/payments`

**Purpose**: Export payment data to Excel/CSV

**Request Body**:
```json
{
  "data": [
    {
      "id": 1,
      "participant_id": 1,
      "payment_method_id": 1,
      "amount": 1500.00,
      "usd_amount": 1500.00,
      "payment_date": "2024-01-20",
      "payment_status": 1,
      "reference_number": "PAY_001_2024",
      "notes": "Registration fee payment",
      "created_at": "2024-01-20 16:45:00",
      "updated_at": "2024-01-20 16:45:00"
    }
  ],
  "template": "standard",
  "format": "excel"
}
```

**Templates Available**: "standard", "detailed"

**Success Response**: Same structure as participants export

**CodeIgniter Example**:
```php
$payments = $this->Payment_model->get_payments_for_export();

$curl = curl_init();
curl_setopt_array($curl, array(
    CURLOPT_URL => 'http://localhost:5000/api/ybb/export/payments',
    CURLOPT_RETURNTRANSFER => true,
    CURLOPT_POST => true,
    CURLOPT_POSTFIELDS => json_encode(array(
        'data' => $payments,
        'template' => 'detailed',
        'format' => 'excel'
    )),
    CURLOPT_HTTPHEADER => array('Content-Type: application/json')
));

$response = curl_exec($curl);
$result = json_decode($response, true);
```

---

### 4. Export Ambassadors

**Endpoint**: `POST /api/ybb/export/ambassadors`

**Purpose**: Export ambassador data to Excel/CSV

**Request Body**:
```json
{
  "data": [
    {
      "id": 1,
      "participant_id": 1,
      "ambassador_code": "AMB_001",
      "category": "university",
      "status": "active",
      "referral_count": 15,
      "commission_earned": 750.00,
      "is_active": 1,
      "created_at": "2024-01-25 12:00:00",
      "updated_at": "2024-01-25 12:00:00"
    }
  ],
  "template": "standard",
  "format": "excel"
}
```

**Templates Available**: "standard", "detailed"

**Success Response**: Same structure as participants export

---

### 5. Check Export Status

**Endpoint**: `GET /api/ybb/export/{export_id}/status`

**Purpose**: Check the status of an export operation

**Request**: No body required

**Success Response**:
```json
{
  "status": "success",
  "export_id": "ac9433a4-a37a-499d-a92f-e4e6163c5ef7",
  "export_type": "participants",
  "template": "standard",
  "record_count": 3,
  "created_at": "2025-07-23T16:27:57.800548",
  "expires_at": "2025-07-24T16:27:57.800548"
}
```

**CodeIgniter Example**:
```php
$export_id = $this->input->get('export_id');
$response = file_get_contents("http://localhost:5000/api/ybb/export/{$export_id}/status");
$status = json_decode($response, true);

echo json_encode($status); // For AJAX responses
```

---

### 6. Download Export File

**Endpoint**: `GET /api/ybb/export/{export_id}/download`

**Purpose**: Download the generated export file

**Request**: No body required

**Response**: Binary file data (Excel/CSV)

**Response Headers**:
```
Content-Type: application/vnd.openxmlformats-officedocument.spreadsheetml.sheet
Content-Disposition: attachment; filename="participants_export.xlsx"
Content-Length: 5386
```

**CodeIgniter Example**:
```php
public function download_export($export_id)
{
    $url = "http://localhost:5000/api/ybb/export/{$export_id}/download";
    
    $curl = curl_init();
    curl_setopt_array($curl, array(
        CURLOPT_URL => $url,
        CURLOPT_RETURNTRANSFER => true,
        CURLOPT_FOLLOWLOCATION => true
    ));
    
    $file_content = curl_exec($curl);
    $http_code = curl_getinfo($curl, CURLINFO_HTTP_CODE);
    curl_close($curl);
    
    if ($http_code === 200) {
        header('Content-Type: application/vnd.openxmlformats-officedocument.spreadsheetml.sheet');
        header('Content-Disposition: attachment; filename="export.xlsx"');
        header('Content-Length: ' . strlen($file_content));
        echo $file_content;
    } else {
        show_404();
    }
}
```

---

### 7. Download ZIP Archive (Large Exports)

**Endpoint**: `GET /api/ybb/export/{export_id}/download/zip`

**Purpose**: Download ZIP archive containing multiple export files

**Response**: ZIP file binary data

**Response Headers**:
```
Content-Type: application/zip
Content-Disposition: attachment; filename="participants_complete_export_20250723_162810.zip"
```

---

### 8. Download Individual Batch File

**Endpoint**: `GET /api/ybb/export/{export_id}/download/batch/{batch_number}`

**Purpose**: Download specific batch file from multi-file export

**Response**: Excel file binary data

---

### 9. Get Available Templates

**Endpoint**: `GET /api/ybb/templates`

**Purpose**: Get all available export templates

**Success Response**:
```json
{
  "status": "success",
  "data": {
    "participants": {
      "standard": {
        "name": "standard",
        "description": "Basic participant information",
        "fields": ["id", "form_id", "first_name", "last_name", "email", "phone", "nationality", "state", "form_status"],
        "headers": ["ID", "Form ID", "First Name", "Last Name", "Email", "Phone", "Nationality", "State", "Status"],
        "includes_sensitive_data": false
      },
      "detailed": {
        "name": "detailed",
        "description": "Extended participant information",
        "fields": ["id", "form_id", "first_name", "last_name", "email", "phone", "birthdate", "nationality", "state", "form_status", "is_active", "created_at"],
        "headers": ["ID", "Form ID", "First Name", "Last Name", "Email", "Phone", "Birth Date", "Nationality", "State", "Status", "Active", "Created At"],
        "includes_sensitive_data": true
      }
    },
    "payments": {
      "standard": {
        "name": "standard",
        "description": "Basic payment information",
        "fields": ["id", "participant_id", "amount", "payment_date", "payment_status", "reference_number", "created_at", "updated_at"],
        "headers": ["ID", "Participant ID", "Amount", "Payment Date", "Status", "Reference", "Created", "Updated"],
        "includes_sensitive_data": false
      }
    },
    "ambassadors": {
      "standard": {
        "name": "standard",
        "description": "Basic ambassador information",
        "fields": ["id", "participant_id", "ambassador_code", "category", "status", "referral_count", "commission_earned"],
        "headers": ["ID", "Participant ID", "Code", "Category", "Status", "Referrals", "Commission"],
        "includes_sensitive_data": false
      }
    }
  }
}
```

---

### 10. Get Status Mappings

**Endpoint**: `GET /api/ybb/status-mappings`

**Purpose**: Get status code to label mappings used in data transformation

**Success Response**:
```json
{
  "status": "success",
  "data": {
    "form_status": {
      "1": "Draft",
      "2": "Submitted", 
      "3": "Approved",
      "4": "Rejected"
    },
    "payment_status": {
      "1": "Pending",
      "2": "Completed",
      "3": "Failed", 
      "4": "Refunded"
    },
    "payment_method": {
      "1": "Credit Card",
      "2": "Bank Transfer",
      "3": "PayPal",
      "4": "Cash"
    },
    "boolean_status": {
      "0": "No",
      "1": "Yes"
    }
  }
}
```

---

## 🚨 Error Responses

### Common Error Format
```json
{
  "status": "error",
  "message": "Error description"
}
```

### Error Codes
- **400 Bad Request**: Invalid request data
- **404 Not Found**: Export not found or expired
- **500 Internal Server Error**: Service error

### Error Examples

**Invalid Data**:
```json
{
  "status": "error",
  "message": "No data provided for export"
}
```

**Export Not Found**:
```json
{
  "status": "error", 
  "message": "Export not found"
}
```

**Invalid Template**:
```json
{
  "status": "error",
  "message": "Template 'invalid_template' not found for participants"
}
```

---

## 📋 CodeIgniter Integration Checklist

### 1. Prerequisites
- [ ] YBB Export API service running on accessible URL
- [ ] CodeIgniter application with cURL support
- [ ] Network connectivity between CodeIgniter and API service

### 2. Basic Integration Steps

```php
// 1. Create config file: application/config/ybb_export.php
$config['ybb_export_api_url'] = 'http://localhost:5000';
$config['ybb_export_timeout'] = 300;

// 2. Create helper function
function call_ybb_api($endpoint, $data = null, $method = 'GET') {
    $ci = &get_instance();
    $ci->load->config('ybb_export');
    
    $url = $ci->config->item('ybb_export_api_url') . $endpoint;
    
    $curl = curl_init();
    curl_setopt_array($curl, array(
        CURLOPT_URL => $url,
        CURLOPT_RETURNTRANSFER => true,
        CURLOPT_TIMEOUT => $ci->config->item('ybb_export_timeout'),
        CURLOPT_CUSTOMREQUEST => $method,
        CURLOPT_HTTPHEADER => array('Content-Type: application/json')
    ));
    
    if ($data && in_array($method, ['POST', 'PUT'])) {
        curl_setopt($curl, CURLOPT_POSTFIELDS, json_encode($data));
    }
    
    $response = curl_exec($curl);
    $http_code = curl_getinfo($curl, CURLINFO_HTTP_CODE);
    curl_close($curl);
    
    return array(
        'success' => $http_code >= 200 && $http_code < 300,
        'data' => json_decode($response, true),
        'http_code' => $http_code
    );
}

// 3. Usage in controller
public function export_participants() {
    $participants = $this->Participant_model->get_all();
    
    $result = call_ybb_api('/api/ybb/export/participants', array(
        'data' => $participants,
        'template' => 'standard',
        'format' => 'excel'
    ), 'POST');
    
    if ($result['success']) {
        $export_id = $result['data']['data']['export_id'];
        redirect('exports/download/' . $export_id);
    } else {
        $this->session->set_flashdata('error', 'Export failed');
        redirect('exports');
    }
}

public function download($export_id) {
    $download_url = "/api/ybb/export/{$export_id}/download";
    
    // Proxy download through CodeIgniter
    $file_content = file_get_contents($this->config->item('ybb_export_api_url') . $download_url);
    
    header('Content-Type: application/vnd.openxmlformats-officedocument.spreadsheetml.sheet');
    header('Content-Disposition: attachment; filename="export.xlsx"');
    echo $file_content;
}
```

### 3. Testing Integration

```php
// Test API connectivity
public function test_api() {
    $result = call_ybb_api('/health');
    
    if ($result['success']) {
        echo "API is healthy: " . $result['data']['status'];
    } else {
        echo "API connection failed";
    }
}

// Test small export
public function test_export() {
    $sample_data = array(
        array(
            'id' => 1,
            'first_name' => 'Test',
            'last_name' => 'User',
            'email' => 'test@example.com'
        )
    );
    
    $result = call_ybb_api('/api/ybb/export/participants', array(
        'data' => $sample_data,
        'template' => 'standard'
    ), 'POST');
    
    var_dump($result);
}
```

---

## 🎯 Best Practices for CodeIgniter Integration

### 1. Error Handling
```php
try {
    $result = call_ybb_api('/api/ybb/export/participants', $data, 'POST');
    
    if (!$result['success']) {
        throw new Exception($result['data']['message'] ?? 'Export failed');
    }
    
    // Handle success
    
} catch (Exception $e) {
    log_message('error', 'Export failed: ' . $e->getMessage());
    $this->session->set_flashdata('error', $e->getMessage());
}
```

### 2. Asynchronous Processing for Large Datasets
```php
// For datasets > 1000 records, inform user about processing time
if (count($data) > 1000) {
    $this->session->set_flashdata('info', 'Large export in progress. This may take a few minutes.');
}
```

### 3. Progress Tracking
```php
// Store export ID and check status via AJAX
$this->session->set_userdata('current_export_id', $export_id);

// JavaScript to check status
setInterval(function() {
    $.get('/exports/check_status/' + export_id, function(data) {
        if (data.status === 'success') {
            window.location = '/exports/download/' + export_id;
        }
    });
}, 2000);
```

---

This documentation provides everything your CodeIgniter team needs to integrate with the YBB Export API. The service is ready for production use and handles all the complex data processing, chunking, and Excel generation automatically.
