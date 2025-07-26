# YBB Data Management Service - PHP Integration Guide

## Overview

This guide provides comprehensive examples and best practices for integrating the YBB Data Management Service with PHP applications, particularly CodeIgniter-based systems.

## Quick Start

### 1. Basic PHP Integration Class

Create a reusable PHP class for API communication:

```php
<?php

class YBBDataProcessor {
    private $api_base_url;
    private $timeout;
    
    public function __construct($api_url = 'http://localhost:5000', $timeout = 300) {
        $this->api_base_url = rtrim($api_url, '/');
        $this->timeout = $timeout;
    }
    
    /**
     * Convert array data to Excel file
     */
    public function arrayToExcel($data, $filename = null, $options = []) {
        $payload = [
            'data' => $data,
            'filename' => $filename ?: 'export_' . date('Y-m-d_H-i-s') . '.xlsx',
            'format_options' => array_merge([
                'auto_width' => true,
                'header_style' => true
            ], $options)
        ];
        
        return $this->makeRequest('POST', '/api/export/excel', $payload, true);
    }
    
    /**
     * Process data with filters and transformations
     */
    public function processData($data, $operations = []) {
        $payload = [
            'data' => $data,
            'operations' => $operations
        ];
        
        $response = $this->makeRequest('POST', '/api/data/process', $payload);
        return json_decode($response, true);
    }
    
    /**
     * Export YBB-specific data with templates
     */
    public function exportYBBData($type, $data, $options = []) {
        $payload = array_merge([
            'data' => $data,
            'template' => 'standard',
            'format' => 'excel'
        ], $options);
        
        return $this->makeRequest('POST', "/api/ybb/export/{$type}", $payload, true);
    }
    
    /**
     * Upload and convert CSV to Excel
     */
    public function csvToExcel($csv_file_path, $output_filename = null) {
        $post_data = [
            'file' => new CURLFile($csv_file_path),
            'format' => 'excel',
            'filename' => $output_filename ?: 'converted_' . date('Y-m-d_H-i-s') . '.xlsx'
        ];
        
        return $this->makeRequest('POST', '/api/upload/csv', $post_data, true, false);
    }
    
    /**
     * Validate data structure
     */
    public function validateData($data) {
        $payload = ['data' => $data];
        $response = $this->makeRequest('POST', '/api/data/validate', $payload);
        return json_decode($response, true);
    }
    
    /**
     * Check API health
     */
    public function healthCheck() {
        $response = $this->makeRequest('GET', '/health');
        return json_decode($response, true);
    }
    
    /**
     * Make HTTP request to API
     */
    private function makeRequest($method, $endpoint, $data = null, $return_binary = false, $json_encode = true) {
        $url = $this->api_base_url . $endpoint;
        
        $ch = curl_init();
        curl_setopt($ch, CURLOPT_URL, $url);
        curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
        curl_setopt($ch, CURLOPT_TIMEOUT, $this->timeout);
        curl_setopt($ch, CURLOPT_FOLLOWLOCATION, true);
        
        if ($method === 'POST') {
            curl_setopt($ch, CURLOPT_POST, true);
            
            if ($data) {
                if ($json_encode && !isset($data['file'])) {
                    curl_setopt($ch, CURLOPT_POSTFIELDS, json_encode($data));
                    curl_setopt($ch, CURLOPT_HTTPHEADER, [
                        'Content-Type: application/json',
                        'Accept: application/json'
                    ]);
                } else {
                    curl_setopt($ch, CURLOPT_POSTFIELDS, $data);
                }
            }
        }
        
        $response = curl_exec($ch);
        $http_code = curl_getinfo($ch, CURLINFO_HTTP_CODE);
        $error = curl_error($ch);
        curl_close($ch);
        
        if ($error) {
            throw new Exception("cURL Error: " . $error);
        }
        
        if ($http_code >= 400) {
            $error_data = json_decode($response, true);
            throw new Exception("API Error ({$http_code}): " . ($error_data['message'] ?? 'Unknown error'));
        }
        
        return $response;
    }
    
    /**
     * Helper method to download Excel file directly to browser
     */
    public function downloadExcel($excel_data, $filename) {
        header('Content-Type: application/vnd.openxmlformats-officedocument.spreadsheetml.sheet');
        header('Content-Disposition: attachment; filename="' . $filename . '"');
        header('Content-Length: ' . strlen($excel_data));
        echo $excel_data;
        exit;
    }
}
?>
```

### 2. CodeIgniter 4 Integration

Create a CodeIgniter service for the YBB API:

```php
<?php

namespace App\Libraries;

use CodeIgniter\Config\BaseService;

class YBBExportService extends BaseService
{
    private $processor;
    
    public function __construct()
    {
        $this->processor = new \YBBDataProcessor(
            getenv('YBB_API_URL') ?: 'http://localhost:5000'
        );
    }
    
    /**
     * Export participants data
     */
    public function exportParticipants($participants, $template = 'standard')
    {
        try {
            // Transform data if needed
            $export_data = array_map(function($participant) {
                return [
                    'name' => $participant['full_name'],
                    'email' => $participant['email'],
                    'program' => $participant['program_name'],
                    'status' => $participant['status'],
                    'registration_date' => $participant['created_at'],
                    'country' => $participant['country'],
                    'university' => $participant['university']
                ];
            }, $participants);
            
            return $this->processor->exportYBBData('participants', $export_data, [
                'template' => $template,
                'filename' => 'participants_' . date('Y-m-d') . '.xlsx'
            ]);
            
        } catch (Exception $e) {
            log_message('error', 'Participant export failed: ' . $e->getMessage());
            throw $e;
        }
    }
    
    /**
     * Export payments data
     */
    public function exportPayments($payments, $template = 'standard')
    {
        try {
            $export_data = array_map(function($payment) {
                return [
                    'participant_name' => $payment['participant_name'],
                    'email' => $payment['email'],
                    'program' => $payment['program'],
                    'amount' => $payment['amount'],
                    'currency' => $payment['currency'],
                    'payment_date' => $payment['payment_date'],
                    'payment_method' => $payment['payment_method'],
                    'status' => $payment['status'],
                    'transaction_id' => $payment['transaction_id']
                ];
            }, $payments);
            
            return $this->processor->exportYBBData('payments', $export_data, [
                'template' => $template,
                'filename' => 'payments_' . date('Y-m-d') . '.xlsx'
            ]);
            
        } catch (Exception $e) {
            log_message('error', 'Payment export failed: ' . $e->getMessage());
            throw $e;
        }
    }
    
    /**
     * Export ambassadors data
     */
    public function exportAmbassadors($ambassadors, $template = 'standard')
    {
        try {
            $export_data = array_map(function($ambassador) {
                return [
                    'name' => $ambassador['name'],
                    'email' => $ambassador['email'],
                    'region' => $ambassador['region'],
                    'country' => $ambassador['country'],
                    'status' => $ambassador['status'],
                    'appointment_date' => $ambassador['appointment_date'],
                    'university' => $ambassador['university'],
                    'programs_managed' => $ambassador['programs_count']
                ];
            }, $ambassadors);
            
            return $this->processor->exportYBBData('ambassadors', $export_data, [
                'template' => $template,
                'filename' => 'ambassadors_' . date('Y-m-d') . '.xlsx'
            ]);
            
        } catch (Exception $e) {
            log_message('error', 'Ambassador export failed: ' . $e->getMessage());
            throw $e;
        }
    }
    
    /**
     * Process and filter data before export
     */
    public function processAndExport($data, $filters, $export_type, $template = 'standard')
    {
        try {
            // First process the data
            $operations = [];
            
            // Add filter operations
            foreach ($filters as $field => $value) {
                if (!empty($value)) {
                    $operations[] = [
                        'type' => 'filter',
                        'column' => $field,
                        'value' => $value
                    ];
                }
            }
            
            // Add sorting if specified
            if (isset($filters['sort_by']) && !empty($filters['sort_by'])) {
                $operations[] = [
                    'type' => 'sort',
                    'column' => $filters['sort_by'],
                    'order' => $filters['sort_order'] ?? 'asc'
                ];
            }
            
            // Process data if we have operations
            if (!empty($operations)) {
                $processed = $this->processor->processData($data, $operations);
                $data = $processed['data'];
            }
            
            // Export processed data
            return $this->processor->exportYBBData($export_type, $data, [
                'template' => $template,
                'filename' => $export_type . '_filtered_' . date('Y-m-d') . '.xlsx'
            ]);
            
        } catch (Exception $e) {
            log_message('error', 'Process and export failed: ' . $e->getMessage());
            throw $e;
        }
    }
}
```

### 3. Controller Examples

#### Basic Export Controller

```php
<?php

namespace App\Controllers;

use CodeIgniter\Controller;
use App\Libraries\YBBExportService;

class ExportController extends Controller
{
    private $exportService;
    
    public function __construct()
    {
        $this->exportService = new YBBExportService();
    }
    
    /**
     * Export participants
     */
    public function participants()
    {
        try {
            // Get filters from request
            $filters = [
                'program' => $this->request->getGet('program'),
                'status' => $this->request->getGet('status'),
                'country' => $this->request->getGet('country'),
                'date_from' => $this->request->getGet('date_from'),
                'date_to' => $this->request->getGet('date_to')
            ];
            
            $template = $this->request->getGet('template') ?: 'standard';
            
            // Get data from database
            $participantModel = new \App\Models\ParticipantModel();
            $participants = $participantModel->getFilteredParticipants($filters);
            
            if (empty($participants)) {
                return $this->response->setJSON([
                    'status' => 'error',
                    'message' => 'No participants found with the specified filters'
                ]);
            }
            
            // Export data
            $excel_data = $this->exportService->exportParticipants($participants, $template);
            
            // Send file to browser
            return $this->response
                ->setContentType('application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
                ->setHeader('Content-Disposition', 'attachment; filename="participants_export.xlsx"')
                ->setBody($excel_data);
                
        } catch (Exception $e) {
            log_message('error', 'Participant export error: ' . $e->getMessage());
            return $this->response->setJSON([
                'status' => 'error',
                'message' => 'Export failed: ' . $e->getMessage()
            ])->setStatusCode(500);
        }
    }
    
    /**
     * Export payments
     */
    public function payments()
    {
        try {
            $filters = [
                'status' => $this->request->getGet('status'),
                'date_from' => $this->request->getGet('date_from'),
                'date_to' => $this->request->getGet('date_to'),
                'program' => $this->request->getGet('program')
            ];
            
            $template = $this->request->getGet('template') ?: 'standard';
            
            $paymentModel = new \App\Models\PaymentModel();
            $payments = $paymentModel->getFilteredPayments($filters);
            
            if (empty($payments)) {
                return $this->response->setJSON([
                    'status' => 'error',
                    'message' => 'No payments found with the specified filters'
                ]);
            }
            
            $excel_data = $this->exportService->exportPayments($payments, $template);
            
            return $this->response
                ->setContentType('application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
                ->setHeader('Content-Disposition', 'attachment; filename="payments_export.xlsx"')
                ->setBody($excel_data);
                
        } catch (Exception $e) {
            log_message('error', 'Payment export error: ' . $e->getMessage());
            return $this->response->setJSON([
                'status' => 'error',
                'message' => 'Export failed: ' . $e->getMessage()
            ])->setStatusCode(500);
        }
    }
    
    /**
     * Bulk export with multiple sheets
     */
    public function bulkExport()
    {
        try {
            $export_types = $this->request->getPost('types') ?: ['participants', 'payments'];
            $template = $this->request->getPost('template') ?: 'standard';
            
            $results = [];
            
            foreach ($export_types as $type) {
                switch ($type) {
                    case 'participants':
                        $model = new \App\Models\ParticipantModel();
                        $data = $model->findAll();
                        $excel_data = $this->exportService->exportParticipants($data, $template);
                        break;
                        
                    case 'payments':
                        $model = new \App\Models\PaymentModel();
                        $data = $model->findAll();
                        $excel_data = $this->exportService->exportPayments($data, $template);
                        break;
                        
                    case 'ambassadors':
                        $model = new \App\Models\AmbassadorModel();
                        $data = $model->findAll();
                        $excel_data = $this->exportService->exportAmbassadors($data, $template);
                        break;
                        
                    default:
                        continue 2;
                }
                
                $results[$type] = $excel_data;
            }
            
            // For multiple exports, create a ZIP file
            if (count($results) > 1) {
                $zip = new \ZipArchive();
                $zip_filename = tempnam(sys_get_temp_dir(), 'ybb_export_') . '.zip';
                
                if ($zip->open($zip_filename, \ZipArchive::CREATE) === TRUE) {
                    foreach ($results as $type => $data) {
                        $zip->addFromString($type . '_export.xlsx', $data);
                    }
                    $zip->close();
                    
                    $zip_data = file_get_contents($zip_filename);
                    unlink($zip_filename);
                    
                    return $this->response
                        ->setContentType('application/zip')
                        ->setHeader('Content-Disposition', 'attachment; filename="ybb_bulk_export.zip"')
                        ->setBody($zip_data);
                } else {
                    throw new Exception('Failed to create ZIP archive');
                }
            } else {
                // Single export
                $type = array_keys($results)[0];
                return $this->response
                    ->setContentType('application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
                    ->setHeader('Content-Disposition', 'attachment; filename="' . $type . '_export.xlsx"')
                    ->setBody($results[$type]);
            }
            
        } catch (Exception $e) {
            log_message('error', 'Bulk export error: ' . $e->getMessage());
            return $this->response->setJSON([
                'status' => 'error',
                'message' => 'Bulk export failed: ' . $e->getMessage()
            ])->setStatusCode(500);
        }
    }
    
    /**
     * CSV upload and conversion
     */
    public function uploadCsv()
    {
        try {
            $file = $this->request->getFile('csv_file');
            
            if (!$file->isValid()) {
                return $this->response->setJSON([
                    'status' => 'error',
                    'message' => 'Invalid file upload'
                ]);
            }
            
            if ($file->getClientExtension() !== 'csv') {
                return $this->response->setJSON([
                    'status' => 'error',
                    'message' => 'Only CSV files are allowed'
                ]);
            }
            
            // Move file to temporary location
            $temp_path = WRITEPATH . 'uploads/' . $file->getRandomName();
            $file->move(WRITEPATH . 'uploads/', $file->getRandomName());
            
            // Convert to Excel using API
            $processor = new \YBBDataProcessor(getenv('YBB_API_URL'));
            $excel_data = $processor->csvToExcel($temp_path, 'converted_file.xlsx');
            
            // Clean up temporary file
            unlink($temp_path);
            
            return $this->response
                ->setContentType('application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
                ->setHeader('Content-Disposition', 'attachment; filename="converted_file.xlsx"')
                ->setBody($excel_data);
                
        } catch (Exception $e) {
            log_message('error', 'CSV conversion error: ' . $e->getMessage());
            return $this->response->setJSON([
                'status' => 'error',
                'message' => 'CSV conversion failed: ' . $e->getMessage()
            ])->setStatusCode(500);
        }
    }
}
```

### 4. Frontend Integration Examples

#### HTML Form for Export Options

```html
<!DOCTYPE html>
<html>
<head>
    <title>YBB Data Export</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body>
    <div class="container mt-5">
        <h2>YBB Data Export</h2>
        
        <!-- Export Form -->
        <form id="exportForm">
            <div class="row">
                <div class="col-md-6">
                    <div class="mb-3">
                        <label for="export_type" class="form-label">Export Type</label>
                        <select class="form-select" id="export_type" name="export_type" required>
                            <option value="">Select Export Type</option>
                            <option value="participants">Participants</option>
                            <option value="payments">Payments</option>
                            <option value="ambassadors">Ambassadors</option>
                        </select>
                    </div>
                </div>
                
                <div class="col-md-6">
                    <div class="mb-3">
                        <label for="template" class="form-label">Template</label>
                        <select class="form-select" id="template" name="template">
                            <option value="standard">Standard</option>
                            <option value="detailed">Detailed</option>
                            <option value="summary">Summary</option>
                        </select>
                    </div>
                </div>
            </div>
            
            <div class="row">
                <div class="col-md-4">
                    <div class="mb-3">
                        <label for="status" class="form-label">Status Filter</label>
                        <select class="form-select" id="status" name="status">
                            <option value="">All Statuses</option>
                            <option value="active">Active</option>
                            <option value="pending">Pending</option>
                            <option value="completed">Completed</option>
                            <option value="cancelled">Cancelled</option>
                        </select>
                    </div>
                </div>
                
                <div class="col-md-4">
                    <div class="mb-3">
                        <label for="date_from" class="form-label">Date From</label>
                        <input type="date" class="form-control" id="date_from" name="date_from">
                    </div>
                </div>
                
                <div class="col-md-4">
                    <div class="mb-3">
                        <label for="date_to" class="form-label">Date To</label>
                        <input type="date" class="form-control" id="date_to" name="date_to">
                    </div>
                </div>
            </div>
            
            <div class="mb-3">
                <button type="submit" class="btn btn-primary">
                    <i class="fas fa-download"></i> Export Data
                </button>
                <button type="button" class="btn btn-secondary" onclick="resetForm()">
                    <i class="fas fa-reset"></i> Reset
                </button>
            </div>
        </form>
        
        <!-- Progress Bar -->
        <div id="progressContainer" class="mb-3" style="display: none;">
            <div class="progress">
                <div id="progressBar" class="progress-bar" role="progressbar" style="width: 0%">0%</div>
            </div>
        </div>
        
        <!-- CSV Upload Form -->
        <hr>
        <h4>CSV Upload & Conversion</h4>
        <form id="csvUploadForm" enctype="multipart/form-data">
            <div class="mb-3">
                <label for="csv_file" class="form-label">CSV File</label>
                <input type="file" class="form-control" id="csv_file" name="csv_file" accept=".csv" required>
            </div>
            <button type="submit" class="btn btn-success">
                <i class="fas fa-upload"></i> Upload & Convert
            </button>
        </form>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
    <script>
        // Export form handler
        document.getElementById('exportForm').addEventListener('submit', function(e) {
            e.preventDefault();
            
            const formData = new FormData(this);
            const exportType = formData.get('export_type');
            
            // Show progress
            document.getElementById('progressContainer').style.display = 'block';
            updateProgress(0);
            
            // Build query string
            const params = new URLSearchParams();
            for (let [key, value] of formData.entries()) {
                if (value && key !== 'export_type') {
                    params.append(key, value);
                }
            }
            
            // Make request
            const url = `/export/${exportType}?${params.toString()}`;
            
            fetch(url, {
                method: 'GET'
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error('Export failed');
                }
                
                updateProgress(100);
                
                // Create download link
                return response.blob();
            })
            .then(blob => {
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = `${exportType}_export_${new Date().toISOString().slice(0,10)}.xlsx`;
                document.body.appendChild(a);
                a.click();
                window.URL.revokeObjectURL(url);
                document.body.removeChild(a);
                
                // Hide progress
                setTimeout(() => {
                    document.getElementById('progressContainer').style.display = 'none';
                }, 2000);
            })
            .catch(error => {
                console.error('Export error:', error);
                alert('Export failed: ' + error.message);
                document.getElementById('progressContainer').style.display = 'none';
            });
        });
        
        // CSV upload form handler
        document.getElementById('csvUploadForm').addEventListener('submit', function(e) {
            e.preventDefault();
            
            const formData = new FormData(this);
            
            fetch('/export/uploadCsv', {
                method: 'POST',
                body: formData
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error('Upload failed');
                }
                return response.blob();
            })
            .then(blob => {
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = 'converted_file.xlsx';
                document.body.appendChild(a);
                a.click();
                window.URL.revokeObjectURL(url);
                document.body.removeChild(a);
            })
            .catch(error => {
                console.error('Upload error:', error);
                alert('Upload failed: ' + error.message);
            });
        });
        
        function updateProgress(percent) {
            const progressBar = document.getElementById('progressBar');
            progressBar.style.width = percent + '%';
            progressBar.textContent = percent + '%';
        }
        
        function resetForm() {
            document.getElementById('exportForm').reset();
            document.getElementById('progressContainer').style.display = 'none';
        }
    </script>
</body>
</html>
```

### 5. Ajax Integration Example

```javascript
// YBB Export JavaScript Library
class YBBExporter {
    constructor(baseUrl) {
        this.baseUrl = baseUrl || '/export';
    }
    
    /**
     * Export data with progress tracking
     */
    async exportData(type, filters = {}, template = 'standard', onProgress = null) {
        try {
            if (onProgress) onProgress(0, 'Starting export...');
            
            const params = new URLSearchParams({
                template: template,
                ...filters
            });
            
            const response = await fetch(`${this.baseUrl}/${type}?${params}`, {
                method: 'GET'
            });
            
            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.message || 'Export failed');
            }
            
            if (onProgress) onProgress(50, 'Processing data...');
            
            const blob = await response.blob();
            
            if (onProgress) onProgress(100, 'Download ready');
            
            return blob;
            
        } catch (error) {
            console.error('Export error:', error);
            throw error;
        }
    }
    
    /**
     * Download blob as file
     */
    downloadBlob(blob, filename) {
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
    }
    
    /**
     * Upload and convert CSV
     */
    async uploadCsv(file, onProgress = null) {
        try {
            const formData = new FormData();
            formData.append('csv_file', file);
            
            if (onProgress) onProgress(0, 'Uploading file...');
            
            const response = await fetch(`${this.baseUrl}/uploadCsv`, {
                method: 'POST',
                body: formData
            });
            
            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.message || 'Upload failed');
            }
            
            if (onProgress) onProgress(100, 'Conversion complete');
            
            return await response.blob();
            
        } catch (error) {
            console.error('Upload error:', error);
            throw error;
        }
    }
    
    /**
     * Validate data before export
     */
    async validateExportData(type, filters = {}) {
        try {
            const params = new URLSearchParams(filters);
            
            const response = await fetch(`${this.baseUrl}/validate/${type}?${params}`, {
                method: 'GET'
            });
            
            if (!response.ok) {
                throw new Error('Validation failed');
            }
            
            return await response.json();
            
        } catch (error) {
            console.error('Validation error:', error);
            throw error;
        }
    }
}

// Usage example
const exporter = new YBBExporter();

// Export participants with progress
exporter.exportData('participants', {
    status: 'active',
    program: 'YBB2024'
}, 'detailed', (progress, message) => {
    console.log(`${progress}%: ${message}`);
}).then(blob => {
    exporter.downloadBlob(blob, 'participants_export.xlsx');
}).catch(error => {
    alert('Export failed: ' + error.message);
});
```

### 6. Error Handling Best Practices

```php
<?php

class YBBExportErrorHandler
{
    public static function handleApiError($exception, $context = [])
    {
        $error_data = [
            'timestamp' => date('Y-m-d H:i:s'),
            'message' => $exception->getMessage(),
            'context' => $context,
            'trace' => $exception->getTraceAsString()
        ];
        
        // Log error
        log_message('error', 'YBB Export Error: ' . json_encode($error_data));
        
        // Send notification for critical errors
        if (self::isCriticalError($exception)) {
            self::sendErrorNotification($error_data);
        }
        
        // Return user-friendly error response
        return [
            'status' => 'error',
            'message' => self::getUserFriendlyMessage($exception),
            'error_code' => self::getErrorCode($exception),
            'timestamp' => $error_data['timestamp']
        ];
    }
    
    private static function isCriticalError($exception)
    {
        $critical_errors = [
            'API connection failed',
            'Service unavailable',
            'Memory limit exceeded'
        ];
        
        $message = $exception->getMessage();
        
        foreach ($critical_errors as $critical) {
            if (stripos($message, $critical) !== false) {
                return true;
            }
        }
        
        return false;
    }
    
    private static function getUserFriendlyMessage($exception)
    {
        $message = $exception->getMessage();
        
        $friendly_messages = [
            'cURL Error' => 'Unable to connect to export service. Please try again later.',
            'API Error (400)' => 'Invalid export parameters. Please check your filters and try again.',
            'API Error (404)' => 'Export service not found. Please contact support.',
            'API Error (500)' => 'Export service is temporarily unavailable. Please try again later.',
            'Memory limit' => 'Dataset too large for export. Please apply filters to reduce the data size.',
            'Timeout' => 'Export is taking longer than expected. Please try with smaller dataset.'
        ];
        
        foreach ($friendly_messages as $pattern => $friendly) {
            if (stripos($message, $pattern) !== false) {
                return $friendly;
            }
        }
        
        return 'An unexpected error occurred. Please try again or contact support.';
    }
    
    private static function getErrorCode($exception)
    {
        $message = $exception->getMessage();
        
        if (stripos($message, 'cURL Error') !== false) return 'CONNECTION_ERROR';
        if (stripos($message, 'API Error (400)') !== false) return 'VALIDATION_ERROR';
        if (stripos($message, 'API Error (404)') !== false) return 'SERVICE_NOT_FOUND';
        if (stripos($message, 'API Error (500)') !== false) return 'SERVICE_ERROR';
        if (stripos($message, 'Memory limit') !== false) return 'MEMORY_LIMIT';
        if (stripos($message, 'Timeout') !== false) return 'TIMEOUT_ERROR';
        
        return 'UNKNOWN_ERROR';
    }
    
    private static function sendErrorNotification($error_data)
    {
        // Implementation depends on your notification system
        // Could be email, Slack, Discord, etc.
        
        $subject = 'YBB Export Service Critical Error';
        $message = "A critical error occurred in the YBB Export Service:\n\n";
        $message .= "Time: " . $error_data['timestamp'] . "\n";
        $message .= "Error: " . $error_data['message'] . "\n";
        $message .= "Context: " . json_encode($error_data['context'], JSON_PRETTY_PRINT) . "\n";
        
        // Send email notification
        mail('admin@ybbfoundation.com', $subject, $message);
    }
}
```

This comprehensive PHP integration guide provides everything needed to integrate the YBB Data Management Service with PHP applications, including error handling, progress tracking, and user-friendly interfaces.
