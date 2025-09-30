# YBB Export Service - Complete Integration Guide

## Overview
This comprehensive guide explains the complete flow for integrating with the YBB Data Management Service, from initiating an export to downloading the generated files. The service can be accessed at your deployment URL.

## Complete Export Flow (Start to Finish)

### Production API Base URL
```
https://your-api-service.com
```

## Step 1: Initiate Export Request

First, send your data to be processed and exported.
### Available Export Endpoints

#### A. Participants Export
**Endpoint:** `POST /api/ybb/export/participants`
**URL:** `https://your-api-service.com/api/ybb/export/participants`

**Request Body:**
```json
{
  "data": [
    {
      "id": 1,
      "name": "John Doe",
      "email": "john@example.com",
      "country": "Indonesia",
      "registration_date": "2025-01-15"
    }
  ],
  "filename": "YBB_Participants_Export_2025",
  "sheet_name": "Participants Data",
  "format": "xlsx",
  "limit": 1000
}
```

#### B. Payments Export
**Endpoint:** `POST /api/ybb/export/payments`
**URL:** `https://your-api-service.com/api/ybb/export/payments`

**Request Body:**
```json
{
  "data": [
    {
      "id": 1,
      "participant_name": "John Doe",
      "amount": 50000,
      "currency": "IDR",
      "payment_date": "2025-01-20",
      "status": "completed"
    }
  ],
  "filename": "YBB_Payments_Export_2025",
  "sheet_name": "Payment Records",
  "format": "xlsx"
}
```

#### C. Ambassadors Export
**Endpoint:** `POST /api/ybb/export/ambassadors`
**URL:** `https://your-api-service.com/api/ybb/export/ambassadors`

**Request Body:**
```json
{
  "data": [
    {
      "id": 1,
      "name": "Jane Smith",
      "email": "jane@example.com",
      "country": "Indonesia",
      "referral_count": 25,
      "commission_earned": 125000
    }
  ],
  "filename": "YBB_Ambassadors_Export_2025",
  "sheet_name": "Ambassador Data",
  "format": "xlsx"
}
```

### Request Parameters Explanation

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `data` | Array | ✅ Yes | Array of objects containing the data to export |
| `filename` | String | ❌ No | Custom filename (will be sanitized and have timestamp added) |
| `sheet_name` | String | ❌ No | Excel sheet name (default: based on export type) |
| `format` | String | ❌ No | Export format: "xlsx" (default) or "csv" |
| `limit` | Integer | ❌ No | Maximum number of records to process |

### Response from Export Request

**Success Response:**
```json
{
  "success": true,
  "data": {
    "export_id": "f72f0c14-28be-4f5e-b5b8-efbca02056de",
    "message": "Export request received and is being processed",
    "estimated_completion": "2025-07-26T13:35:00Z"
  },
  "request_id": "abc123",
  "http_code": 202
}
```

**Error Response:**
```json
{
  "success": false,
  "message": "Invalid request data",
  "errors": ["Data array is required", "Invalid email format in record 3"],
  "request_id": "def456",
  "http_code": 400
}
```

## Step 2: Poll Export Status

After initiating the export, continuously check the status until completion.

### Status Check Endpoint
**Endpoint:** `GET /api/ybb/export/{export_id}/status`
**URL:** `https://your-api-service.com/api/ybb/export/{export_id}/status`

### Status Responses

#### Processing Status
```json
{
  "success": true,
  "data": {
    "export_id": "f72f0c14-28be-4f5e-b5b8-efbca02056de",
    "status": "processing",
    "progress": 45,
    "message": "Processing 430 of 860 records",
    "created_at": "2025-07-26T13:32:46.377978",
    "estimated_completion": "2025-07-26T13:35:00Z"
  },
  "request_id": "xyz789"
}
```

#### Completed Status (Ready for Download)
```json
{
  "success": true,
  "data": {
    "export_id": "f72f0c14-28be-4f5e-b5b8-efbca02056de",
    "status": "success",
    "export_type": "participants",
    "file_size": 1442532,
    "record_count": 860,
    "created_at": "2025-07-26T13:32:46.377978",
    "expires_at": "2025-07-27T13:32:46.377988",
    "filename": "YBB_Participants_Export_860_records_2025-07-26_13-32-46.xlsx"
  },
  "request_id": "status123"
}
```

#### Error Status
```json
{
  "success": true,
  "data": {
    "export_id": "f72f0c14-28be-4f5e-b5b8-efbca02056de",
    "status": "error",
    "message": "Failed to process record at index 234: Invalid data format",
    "created_at": "2025-07-26T13:32:46.377978"
  },
  "request_id": "error456"
}
```

## Step 3: Download Completed Export

When status returns `"status": "success"`, the file is ready for download.

### Download Endpoint
**Endpoint:** `GET /api/ybb/export/{export_id}/download`
**URL:** `https://your-api-service.com/api/ybb/export/{export_id}/download`

**Response:** Binary file content with appropriate headers
- `Content-Type`: `application/vnd.openxmlformats-officedocument.spreadsheetml.sheet` (for Excel)
- `Content-Disposition`: `attachment; filename="actual_filename.xlsx"`
- `Content-Length`: File size in bytes

## Step 4: Additional Utility Endpoints

### A. Storage Information
**Endpoint:** `GET /api/ybb/storage/info`
**URL:** `https://your-api-service.com/api/ybb/storage/info`

**Response:**
```json
{
  "success": true,
  "data": {
    "total_exports": 15,
    "total_size": 25680435,
    "oldest_export": "2025-07-25T10:15:30Z",
    "newest_export": "2025-07-26T13:32:46Z",
    "available_space": "Unlimited"
  }
}
```

### B. Health Check
**Endpoint:** `GET /health`
**URL:** `https://your-api-service.com/health`

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-07-26T13:45:00Z",
  "services": {
    "pandas": "available",
    "excel": "available", 
    "storage": "available"
  }
}
```

## Complete Implementation Example

### CodeIgniter Integration (Frontend)

#### Complete Export Flow Implementation

```php
<?php
class YbbExportController extends CI_Controller 
{
    private $api_base_url = 'https://your-api-service.com';
    
    public function __construct() {
        parent::__construct();
        $this->load->library('curl');
        $this->load->helper('download');
    }
    
    /**
     * Step 1: Initiate Export Request
     */
    public function initiate_export() 
    {
        // Get data from your database or form
        $export_data = $this->get_export_data();
        
        $request_payload = [
            'data' => $export_data,
            'filename' => 'YBB_Participants_Export_' . date('Y_m_d'),
            'sheet_name' => 'Participants Data',
            'format' => 'xlsx'
        ];
        
        // Send export request
        $response = $this->send_export_request('participants', $request_payload);
        
        if ($response['success']) {
            $export_id = $response['data']['export_id'];
            
            // Store export ID in session or database
            $this->session->set_userdata('current_export_id', $export_id);
            
            // Start polling for status
            $this->poll_export_status($export_id);
        } else {
            $this->handle_export_error($response);
        }
    }
    
    /**
     * Step 2: Poll Export Status
     */
    public function poll_export_status($export_id = null) 
    {
        if (!$export_id) {
            $export_id = $this->session->userdata('current_export_id');
        }
        
        if (!$export_id) {
            show_error('No export ID found', 400);
            return;
        }
        
        $status_url = $this->api_base_url . "/api/ybb/export/{$export_id}/status";
        
        $this->curl->create($status_url);
        $this->curl->option(CURLOPT_RETURNTRANSFER, true);
        $this->curl->option(CURLOPT_TIMEOUT, 30);
        $response = $this->curl->execute();
        
        if ($this->curl->error_code === 0) {
            $status_data = json_decode($response, true);
            
            if ($status_data['success']) {
                $status = $status_data['data']['status'];
                
                switch ($status) {
                    case 'processing':
                        $this->handle_processing_status($status_data);
                        break;
                    case 'success':
                        $this->handle_export_ready($export_id, $status_data);
                        break;
                    case 'error':
                        $this->handle_export_error($status_data);
                        break;
                }
            } else {
                $this->handle_status_error($status_data);
            }
        } else {
            log_message('error', 'Status check failed: ' . $this->curl->error_string);
        }
    }
    
    /**
     * Step 3: Download Export File
     */
    public function download_export($export_id) 
    {
        try {
            // Final status check
            $status_check = $this->check_export_status($export_id);
            
            if (!$status_check['success'] || $status_check['data']['status'] !== 'success') {
                show_404('Export not found or not ready');
                return;
            }
            
            // Download the file
            $download_url = $this->api_base_url . "/api/ybb/export/{$export_id}/download";
            
            $this->curl->create($download_url);
            $this->curl->option(CURLOPT_RETURNTRANSFER, true);
            $this->curl->option(CURLOPT_FOLLOWLOCATION, true);
            $this->curl->option(CURLOPT_TIMEOUT, 300); // 5 minutes for large files
            
            $file_content = $this->curl->execute();
            $http_code = $this->curl->info['http_code'];
            
            if ($http_code === 200 && $file_content) {
                // Get filename from status
                $filename = $status_check['data']['filename'] ?? 
                           "YBB_Export_{$export_id}_" . date('Y-m-d_H-i-s') . '.xlsx';
                
                // Set download headers and output file
                $this->output
                    ->set_content_type('application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
                    ->set_header('Content-Disposition: attachment; filename="' . $filename . '"')
                    ->set_header('Content-Length: ' . strlen($file_content))
                    ->set_header('Cache-Control: no-cache, must-revalidate')
                    ->set_output($file_content);
                
                // Log successful download
                log_message('info', "Export downloaded: ID={$export_id}, size=" . strlen($file_content));
                
            } else {
                show_error('Failed to download export file', 500);
            }
            
        } catch (Exception $e) {
            log_message('error', 'Download exception: ' . $e->getMessage());
            show_error('Download failed: ' . $e->getMessage(), 500);
        }
    }
    
    /**
     * AJAX endpoint for real-time status updates
     */
    public function ajax_status($export_id) 
    {
        $this->output->set_content_type('application/json');
        
        $status_data = $this->check_export_status($export_id);
        
        if ($status_data['success']) {
            $data = $status_data['data'];
            
            $response = [
                'success' => true,
                'status' => $data['status'],
                'progress' => $data['progress'] ?? null,
                'message' => $data['message'] ?? '',
                'record_count' => $data['record_count'] ?? null,
                'file_size' => $data['file_size'] ?? null,
                'file_size_formatted' => isset($data['file_size']) ? $this->format_file_size($data['file_size']) : null,
                'download_url' => $data['status'] === 'success' ? base_url("exports/download/{$export_id}") : null
            ];
        } else {
            $response = [
                'success' => false,
                'message' => $status_data['message'] ?? 'Status check failed'
            ];
        }
        
        $this->output->set_output(json_encode($response));
    }
    
    // Helper Methods
    
    private function send_export_request($export_type, $payload) 
    {
        $url = $this->api_base_url . "/api/ybb/export/{$export_type}";
        
        $this->curl->create($url);
        $this->curl->option(CURLOPT_RETURNTRANSFER, true);
        $this->curl->option(CURLOPT_POST, true);
        $this->curl->option(CURLOPT_POSTFIELDS, json_encode($payload));
        $this->curl->option(CURLOPT_HTTPHEADER, [
            'Content-Type: application/json',
            'Accept: application/json'
        ]);
        
        $response = $this->curl->execute();
        
        if ($this->curl->error_code === 0) {
            return json_decode($response, true);
        } else {
            return [
                'success' => false,
                'message' => $this->curl->error_string
            ];
        }
    }
    
    private function check_export_status($export_id) 
    {
        $url = $this->api_base_url . "/api/ybb/export/{$export_id}/status";
        
        $this->curl->create($url);
        $this->curl->option(CURLOPT_RETURNTRANSFER, true);
        $response = $this->curl->execute();
        
        if ($this->curl->error_code === 0) {
            return json_decode($response, true);
        } else {
            return [
                'success' => false,
                'message' => $this->curl->error_string
            ];
        }
    }
    
    private function get_export_data() 
    {
        // Replace with your actual data retrieval logic
        $this->load->model('participants_model');
        return $this->participants_model->get_export_data();
    }
    
    private function handle_processing_status($status_data) 
    {
        $data = $status_data['data'];
        $progress = $data['progress'] ?? 0;
        $message = $data['message'] ?? 'Processing...';
        
        // Load view with processing status
        $view_data = [
            'export_id' => $data['export_id'],
            'status' => 'processing',
            'progress' => $progress,
            'message' => $message
        ];
        
        $this->load->view('export_status', $view_data);
    }
    
    private function handle_export_ready($export_id, $status_data) 
    {
        $data = $status_data['data'];
        
        // Load view with download option
        $view_data = [
            'export_id' => $export_id,
            'status' => 'ready',
            'record_count' => $data['record_count'],
            'file_size' => $this->format_file_size($data['file_size']),
            'download_url' => base_url("exports/download/{$export_id}"),
            'filename' => $data['filename'] ?? "export_{$export_id}.xlsx"
        ];
        
        $this->load->view('export_ready', $view_data);
    }
    
    private function handle_export_error($error_data) 
    {
        $message = $error_data['message'] ?? 'Export failed';
        log_message('error', 'Export error: ' . $message);
        show_error($message, 500);
    }
    
    private function format_file_size($bytes) 
    {
        $units = ['B', 'KB', 'MB', 'GB'];
        $i = 0;
        while ($bytes >= 1024 && $i < count($units) - 1) {
            $bytes /= 1024;
            $i++;
        }
        return round($bytes, 2) . ' ' . $units[$i];
    }
}
?>
```

### JavaScript Frontend Implementation for Real-Time Updates

```javascript
class YbbExportManager {
    constructor(baseUrl) {
        this.baseUrl = baseUrl;
        this.exportId = null;
        this.pollInterval = null;
        this.pollDelay = 2000; // 2 seconds
    }
    
    /**
     * Step 1: Initiate Export
     */
    async initiateExport(exportType, data, options = {}) {
        try {
            const payload = {
                data: data,
                filename: options.filename || `YBB_${exportType}_Export_${new Date().toISOString().split('T')[0]}`,
                sheet_name: options.sheetName || `${exportType} Data`,
                format: options.format || 'xlsx',
                limit: options.limit
            };
            
            const response = await fetch(`${this.baseUrl}/api/ybb/export/${exportType}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(payload)
            });
            
            const result = await response.json();
            
            if (result.success) {
                this.exportId = result.data.export_id;
                this.showMessage('success', 'Export initiated successfully!');
                this.startStatusPolling();
                return result;
            } else {
                this.showMessage('error', 'Export failed: ' + result.message);
                return result;
            }
            
        } catch (error) {
            this.showMessage('error', 'Network error: ' + error.message);
            return { success: false, message: error.message };
        }
    }
    
    /**
     * Step 2: Poll Status
     */
    startStatusPolling() {
        if (!this.exportId) return;
        
        this.updateUI('processing', { message: 'Starting export...' });
        
        this.pollInterval = setInterval(async () => {
            try {
                const status = await this.checkStatus(this.exportId);
                
                if (status.success) {
                    const statusData = status.data;
                    
                    switch (statusData.status) {
                        case 'processing':
                            this.updateUI('processing', statusData);
                            break;
                        case 'success':
                            this.stopPolling();
                            this.updateUI('ready', statusData);
                            break;
                        case 'error':
                            this.stopPolling();
                            this.updateUI('error', statusData);
                            break;
                    }
                } else {
                    this.stopPolling();
                    this.showMessage('error', 'Status check failed: ' + status.message);
                }
                
            } catch (error) {
                this.stopPolling();
                this.showMessage('error', 'Status check error: ' + error.message);
            }
        }, this.pollDelay);
    }
    
    async checkStatus(exportId) {
        const response = await fetch(`${this.baseUrl}/api/ybb/export/${exportId}/status`);
        return await response.json();
    }
    
    stopPolling() {
        if (this.pollInterval) {
            clearInterval(this.pollInterval);
            this.pollInterval = null;
        }
    }
    
    /**
     * Step 3: Download File
     */
    downloadExport(exportId = null) {
        const id = exportId || this.exportId;
        if (!id) {
            this.showMessage('error', 'No export ID available');
            return;
        }
        
        const downloadUrl = `${this.baseUrl}/api/ybb/export/${id}/download`;
        
        // Create invisible download link
        const link = document.createElement('a');
        link.href = downloadUrl;
        link.style.display = 'none';
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        
        this.showMessage('success', 'Download started!');
    }
    
    /**
     * UI Update Methods
     */
    updateUI(status, data) {
        const statusContainer = document.getElementById('export-status');
        const downloadBtn = document.getElementById('download-btn');
        
        switch (status) {
            case 'processing':
                const progress = data.progress || 0;
                const message = data.message || 'Processing...';
                
                statusContainer.innerHTML = `
                    <div class="alert alert-info">
                        <h5><i class="fas fa-spinner fa-spin"></i> Processing Export</h5>
                        <div class="progress mb-2">
                            <div class="progress-bar" role="progressbar" style="width: ${progress}%">
                                ${progress}%
                            </div>
                        </div>
                        <p class="mb-0">${message}</p>
                    </div>
                `;
                
                downloadBtn.disabled = true;
                downloadBtn.innerHTML = '<i class="fas fa-clock"></i> Processing...';
                break;
                
            case 'ready':
                statusContainer.innerHTML = `
                    <div class="alert alert-success">
                        <h5><i class="fas fa-check-circle"></i> Export Ready!</h5>
                        <div class="row">
                            <div class="col-md-6">
                                <p><strong>Records:</strong> ${data.record_count?.toLocaleString()}</p>
                                <p><strong>File Size:</strong> ${this.formatFileSize(data.file_size)}</p>
                            </div>
                            <div class="col-md-6">
                                <p><strong>Type:</strong> ${data.export_type}</p>
                                <p><strong>Created:</strong> ${new Date(data.created_at).toLocaleString()}</p>
                            </div>
                        </div>
                    </div>
                `;
                
                downloadBtn.disabled = false;
                downloadBtn.innerHTML = '<i class="fas fa-download"></i> Download Export';
                downloadBtn.onclick = () => this.downloadExport();
                break;
                
            case 'error':
                statusContainer.innerHTML = `
                    <div class="alert alert-danger">
                        <h5><i class="fas fa-exclamation-circle"></i> Export Failed</h5>
                        <p>${data.message || 'An error occurred during export'}</p>
                    </div>
                `;
                
                downloadBtn.disabled = true;
                downloadBtn.innerHTML = '<i class="fas fa-times"></i> Export Failed';
                break;
        }
    }
    
    showMessage(type, message) {
        const messageContainer = document.getElementById('message-container');
        const alertClass = type === 'success' ? 'alert-success' : 
                          type === 'error' ? 'alert-danger' : 'alert-info';
        
        const messageDiv = document.createElement('div');
        messageDiv.className = `alert ${alertClass} alert-dismissible fade show`;
        messageDiv.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        messageContainer.appendChild(messageDiv);
        
        setTimeout(() => {
            if (messageDiv.parentNode) {
                messageDiv.remove();
            }
        }, 5000);
    }
    
    formatFileSize(bytes) {
        if (!bytes) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }
}

// Usage Example
const exportManager = new YbbExportManager('https://your-api-service.com');

// Start export
document.getElementById('start-export-btn').onclick = async () => {
    const participantData = await getParticipantData(); // Your data source
    
    await exportManager.initiateExport('participants', participantData, {
        filename: 'YBB_Participants_Export_Custom',
        sheetName: 'Participants Data',
        format: 'xlsx'
    });
};
```

### HTML Template for Complete Flow

```html
<!DOCTYPE html>
<html>
<head>
    <title>YBB Export System</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
</head>
<body>
    <div class="container mt-4">
        <div class="row">
            <div class="col-md-10 mx-auto">
                <div class="card">
                    <div class="card-header">
                        <h4><i class="fas fa-file-export"></i> YBB Export System</h4>
                        <small class="text-muted">Complete export workflow from data to download</small>
                    </div>
                    <div class="card-body">
                        <!-- Step 1: Export Configuration -->
                        <div class="mb-4">
                            <h5>Step 1: Configure Export</h5>
                            <div class="row">
                                <div class="col-md-6">
                                    <label>Export Type:</label>
                                    <select id="export-type" class="form-select">
                                        <option value="participants">Participants</option>
                                        <option value="payments">Payments</option>
                                        <option value="ambassadors">Ambassadors</option>
                                    </select>
                                </div>
                                <div class="col-md-6">
                                    <label>Filename:</label>
                                    <input type="text" id="export-filename" class="form-control" 
                                           placeholder="YBB_Export_Custom_Name">
                                </div>
                            </div>
                            <div class="mt-2">
                                <button id="start-export-btn" class="btn btn-primary">
                                    <i class="fas fa-play"></i> Start Export
                                </button>
                            </div>
                        </div>
                        
                        <!-- Step 2: Status Display -->
                        <div class="mb-4">
                            <h5>Step 2: Export Status</h5>
                            <div id="message-container"></div>
                            <div id="export-status">
                                <div class="alert alert-secondary">
                                    <i class="fas fa-info-circle"></i> Ready to start export...
                                </div>
                            </div>
                        </div>
                        
                        <!-- Step 3: Download -->
                        <div class="mb-4">
                            <h5>Step 3: Download</h5>
                            <div class="text-center">
                                <button id="download-btn" class="btn btn-secondary btn-lg" disabled>
                                    <i class="fas fa-clock"></i> Waiting for Export...
                                </button>
                                <div id="download-info" class="text-muted mt-2"></div>
                            </div>
                        </div>
                        
                        <!-- Export Details -->
                        <div class="mt-4">
                            <h6>API Endpoints Used:</h6>
                            <div class="small text-muted">
                                <div><strong>Base URL:</strong> https://your-api-service.com</div>
                                <div><strong>Export:</strong> POST /api/ybb/export/{type}</div>
                                <div><strong>Status:</strong> GET /api/ybb/export/{id}/status</div>
                                <div><strong>Download:</strong> GET /api/ybb/export/{id}/download</div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
    
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
    <script>
        // Initialize export manager
        const exportManager = new YbbExportManager('https://your-api-service.com');
        
        // Sample data generator (replace with your actual data source)
        async function getSampleData(type) {
            // Replace with your actual data retrieval
            const sampleData = {
                participants: [
                    { id: 1, name: 'John Doe', email: 'john@example.com', country: 'Indonesia' },
                    { id: 2, name: 'Jane Smith', email: 'jane@example.com', country: 'Malaysia' }
                ],
                payments: [
                    { id: 1, participant_name: 'John Doe', amount: 50000, currency: 'IDR', status: 'completed' },
                    { id: 2, participant_name: 'Jane Smith', amount: 75000, currency: 'IDR', status: 'pending' }
                ],
                ambassadors: [
                    { id: 1, name: 'Alice Johnson', referral_count: 25, commission_earned: 125000 },
                    { id: 2, name: 'Bob Wilson', referral_count: 18, commission_earned: 90000 }
                ]
            };
            
            return sampleData[type] || [];
        }
        
        // Start export button handler
        document.getElementById('start-export-btn').onclick = async () => {
            const exportType = document.getElementById('export-type').value;
            const customFilename = document.getElementById('export-filename').value;
            
            const data = await getSampleData(exportType);
            
            if (data.length === 0) {
                exportManager.showMessage('warning', 'No data available for export');
                return;
            }
            
            const options = {};
            if (customFilename) {
                options.filename = customFilename;
            }
            
            await exportManager.initiateExport(exportType, data, options);
        };
    </script>
</body>
</html>
```

## Summary: Complete Export Flow

### 🔄 **The Complete Process:**

1. **📤 Initiate Export** → `POST /api/ybb/export/{type}` with your data
2. **⏳ Poll Status** → `GET /api/ybb/export/{id}/status` until status = "success"  
3. **⬇️ Download File** → `GET /api/ybb/export/{id}/download` to get the Excel file

### 🌐 **Production URLs:**
- **Base URL:** `https://your-api-service.com`
- **Health Check:** `https://your-api-service.com/health`
- **Storage Info:** `https://your-api-service.com/api/ybb/storage/info`

### ⏱️ **Timing:**
- **Small exports** (< 1000 records): ~5-15 seconds
- **Large exports** (> 10000 records): ~30-120 seconds  
- **Files expire** in 24 hours
- **Poll every** 2-3 seconds for status updates

Your production service is ready to handle the complete export workflow from data submission to file download!

## Error Handling and Edge Cases

### Common Scenarios

#### 1. Export Request Failures
```json
{
  "success": false,
  "message": "Validation failed",
  "errors": [
    "Data array is required",
    "Invalid email format in record 3",
    "Filename contains invalid characters"
  ],
  "http_code": 400
}
```

#### 2. Status Check Failures
```json
{
  "success": false,
  "message": "Export not found",
  "http_code": 404
}
```

#### 3. Download Failures
- **File Expired**: Export was automatically cleaned up
- **File Not Found**: Invalid export ID or cleanup occurred
- **Server Error**: Temporary service issues

### Error Handling Implementation

```php
class YbbExportErrorHandler 
{
    public static function handleExportError($response) 
    {
        if (!$response['success']) {
            $message = $response['message'] ?? 'Unknown error';
            $errors = $response['errors'] ?? [];
            
            log_message('error', 'Export failed: ' . $message);
            
            if (!empty($errors)) {
                foreach ($errors as $error) {
                    log_message('error', 'Export validation error: ' . $error);
                }
                $message .= ' Details: ' . implode(', ', $errors);
            }
            
            return [
                'success' => false,
                'user_message' => self::getUserFriendlyMessage($response),
                'technical_message' => $message
            ];
        }
        
        return ['success' => true];
    }
    
    private static function getUserFriendlyMessage($response) 
    {
        $code = $response['http_code'] ?? 500;
        
        switch ($code) {
            case 400:
                return 'Please check your export data and try again.';
            case 404:
                return 'Export not found. It may have expired or been cleaned up.';
            case 500:
                return 'Server error. Please try again later.';
            default:
                return 'An unexpected error occurred. Please contact support.';
        }
    }
}
```

## Performance Considerations

### File Size Limits
- **Small Files** (< 1MB): Near-instant processing
- **Medium Files** (1-10MB): 10-30 seconds processing
- **Large Files** (10-50MB): 30-120 seconds processing
- **Maximum Size**: 100MB per export

### Optimization Tips

1. **Batch Processing**: For very large datasets, consider splitting into multiple exports
2. **Polling Frequency**: Use 2-3 second intervals (don't overload the server)
3. **Timeout Handling**: Set appropriate timeouts for different operations
4. **Caching**: Cache export metadata to reduce API calls

```javascript
// Adaptive polling with backoff
class AdaptivePolling {
    constructor(exportManager) {
        this.exportManager = exportManager;
        this.pollCount = 0;
        this.baseDelay = 2000; // Start with 2 seconds
        this.maxDelay = 10000;  // Max 10 seconds
    }
    
    getNextDelay() {
        // Exponential backoff: 2s, 3s, 4s, 6s, 8s, 10s, 10s...
        const delay = Math.min(
            this.baseDelay + (this.pollCount * 1000),
            this.maxDelay
        );
        this.pollCount++;
        return delay;
    }
    
    resetDelay() {
        this.pollCount = 0;
    }
}
```

## Testing and Validation

### Test Data Samples

#### Participants Test Data
```json
{
  "data": [
    {
      "id": 1,
      "name": "Test User 1",
      "email": "test1@example.com",
      "country": "Indonesia",
      "registration_date": "2025-01-15T10:30:00Z",
      "status": "active"
    },
    {
      "id": 2,
      "name": "Test User 2", 
      "email": "test2@example.com",
      "country": "Malaysia",
      "registration_date": "2025-01-16T14:20:00Z",
      "status": "pending"
    }
  ],
  "filename": "Test_Participants_Export",
  "format": "xlsx"
}
```

### cURL Test Commands

```bash
# 1. Test Export Request
curl -X POST "https://your-api-service.com/api/ybb/export/participants" \
     -H "Content-Type: application/json" \
     -d '{
       "data": [{"id": 1, "name": "Test User", "email": "test@example.com"}],
       "filename": "Test_Export"
     }'

# 2. Test Status Check (replace {export_id})
curl "https://your-api-service.com/api/ybb/export/{export_id}/status"

# 3. Test Download (replace {export_id})
curl -o "test_download.xlsx" \
     "https://your-api-service.com/api/ybb/export/{export_id}/download"

# 4. Test Health Check
curl "https://your-api-service.com/health"

# 5. Test Storage Info
curl "https://your-api-service.com/api/ybb/storage/info"
```

## Security and Best Practices

### Data Security
- ✅ **Validate all input data** before sending to API
- ✅ **Sanitize filenames** to prevent path traversal
- ✅ **Limit export size** to prevent resource exhaustion
- ✅ **Log all export activities** for audit trails
- ✅ **Use HTTPS only** for all API communications

### Access Control
```php
// Example access control in CodeIgniter
public function before_export_request() 
{
    // Check user permissions
    if (!$this->user_model->can_export($this->session->userdata('user_id'))) {
        show_error('Insufficient permissions', 403);
        return false;
    }
    
    // Rate limiting
    if ($this->rate_limiter->is_exceeded($this->session->userdata('user_id'), 'export')) {
        show_error('Too many export requests. Please wait.', 429);
        return false;
    }
    
    return true;
}
```

### Monitoring and Logging
```php
// Comprehensive logging
private function log_export_activity($action, $export_id, $details = []) 
{
    $log_data = [
        'timestamp' => date('Y-m-d H:i:s'),
        'user_id' => $this->session->userdata('user_id'),
        'action' => $action, // 'initiated', 'downloaded', 'failed'
        'export_id' => $export_id,
        'ip_address' => $this->input->ip_address(),
        'user_agent' => $this->input->user_agent(),
        'details' => json_encode($details)
    ];
    
    $this->db->insert('export_activity_log', $log_data);
}
```

#### Common Scenarios to Handle:

1. **Export Expired**: File was deleted due to TTL
2. **Download Failed**: Network or server error
3. **File Not Found**: Export ID invalid or cleaned up
4. **Large File Timeout**: Download interrupted

#### Error Handling Code:

```php
// In your controller
public function download($export_id) {
    try {
        $status = $this->ybb_export->get_export_status($export_id);
        
        if (!$status['success']) {
            if (strpos($status['message'], 'not found') !== false) {
                show_404('Export not found or has expired');
            } else {
                show_error('Export status check failed: ' . $status['message'], 500);
            }
            return;
        }
        
        if ($status['data']['status'] !== 'success') {
            show_error('Export is not ready for download', 400);
            return;
        }
        
        // Continue with download...
        
    } catch (Exception $e) {
        log_message('error', 'Download error: ' . $e->getMessage());
        show_error('An unexpected error occurred during download', 500);
    }
}
```

### 6. Testing Your Implementation

#### Test Download Flow:

1. **Generate Test Export**:
   ```bash
   curl -X POST "https://your-api-service.com/api/ybb/export/participants" \
        -H "Content-Type: application/json" \
        -d '{"limit": 10}'
   ```

2. **Check Status Until Ready**:
   ```bash
   curl "https://your-api-service.com/api/ybb/export/{export_id}/status"
   ```

3. **Test Download**:
   ```bash
   curl -o "test_export.xlsx" \
        "https://your-api-service.com/api/ybb/export/{export_id}/download"
   ```

### 7. Performance Considerations

- **Large Files**: Consider using streaming for files > 10MB
- **Concurrent Downloads**: Implement rate limiting if needed
- **Caching**: Cache export metadata to reduce API calls
- **Progress Tracking**: Show download progress for large files

### 8. Security Notes

- Validate export IDs before processing
- Implement proper access controls
- Log all download attempts
- Consider implementing download tokens for additional security
- Set appropriate file download limits

## Summary

After receiving a successful export status:

1. ✅ **Parse the response** - Extract export metadata
2. ✅ **Update UI** - Show export is ready with details
3. ✅ **Enable download** - Activate download button/link
4. ✅ **Handle download** - Use direct URL or fetch approach
5. ✅ **Provide feedback** - Show success/error messages
6. ✅ **Handle errors** - Gracefully handle various failure scenarios

Your export with **860 participants** (1.4MB) is ready for download using the provided integration methods.
