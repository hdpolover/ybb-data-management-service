# CodeIgniter Integration Guide - YBB Export Service Enhancement

## Overview
This guide details the necessary changes required in the CodeIgniter web application to integrate with the enhanced Python Flask export service, including filename customization, processing time handling, and improved user experience.

## 🚀 Key Changes Required

### 1. Enhanced Export Request Payload

Update all export service calls to include the new filename and sheet name parameters:

#### Before (Old Implementation):
```php
// Old basic payload
$payload = [
    'data' => $participants,
    'template' => 'standard',
    'format' => 'excel'
];
```

#### After (Enhanced Implementation):
```php
// Enhanced payload with custom naming
$payload = [
    'data' => $participants,
    'template' => 'standard', 
    'format' => 'excel',
    'filename' => $this->generateDescriptiveFilename($program, 'participants'),
    'sheet_name' => $this->generateSheetName($program, 'participants'),
    'filters' => $this->getCurrentFilters(),
    'options' => [
        'include_related' => true,
        'batch_size' => 5000,
        'sort_by' => 'created_at',
        'sort_order' => 'desc'
    ]
];
```

### 2. Filename Generation Methods

Add these methods to your Export Controller or create a dedicated FilenameHelper:

```php
<?php

class ExportFilenameHelper {
    
    /**
     * Generate descriptive filename for exports
     * 
     * @param object $program Program data
     * @param string $type Export type (participants, payments, ambassadors)
     * @param array $filters Applied filters
     * @return string Generated filename
     */
    public function generateDescriptiveFilename($program, $type, $filters = []) {
        // Sanitize program name for filename
        $programName = $this->sanitizeForFilename($program->name);
        
        // Capitalize export type
        $exportType = ucfirst($type);
        
        // Add filter descriptions
        $filterDesc = $this->generateFilterDescription($filters, $type);
        
        // Current date
        $date = date('d-m-Y');
        
        // Construct filename
        $filename = "{$programName}_{$exportType}_{$filterDesc}_{$date}.xlsx";
        
        // Ensure filename doesn't exceed limits
        return $this->truncateFilename($filename, 200);
    }
    
    /**
     * Generate Excel sheet name
     * 
     * @param object $program Program data
     * @param string $type Export type
     * @return string Sheet name (max 31 characters)
     */
    public function generateSheetName($program, $type) {
        $typeName = ucfirst($type);
        $monthYear = date('M Y');
        
        $sheetName = "{$typeName} Data {$monthYear}";
        
        // Truncate to Excel limit (31 characters)
        return substr($sheetName, 0, 31);
    }
    
    /**
     * Generate filter description for filename
     * 
     * @param array $filters Applied filters
     * @param string $type Export type
     * @return string Filter description
     */
    private function generateFilterDescription($filters, $type) {
        $descriptions = [];
        
        switch($type) {
            case 'participants':
                if (isset($filters['status'])) {
                    $descriptions[] = ucfirst($filters['status']);
                }
                if (isset($filters['has_paid']) && $filters['has_paid']) {
                    $descriptions[] = 'Paid';
                }
                break;
                
            case 'payments':
                if (isset($filters['status'])) {
                    $descriptions[] = ucfirst($filters['status']);
                }
                if (isset($filters['currency'])) {
                    $descriptions[] = strtoupper($filters['currency']);
                }
                break;
                
            case 'ambassadors':
                if (isset($filters['active_only']) && $filters['active_only']) {
                    $descriptions[] = 'Active';
                }
                break;
        }
        
        if (empty($descriptions)) {
            return 'Complete_Data';
        }
        
        return implode('_', $descriptions) . '_Data';
    }
    
    /**
     * Sanitize string for use in filename
     * 
     * @param string $input Input string
     * @return string Sanitized string
     */
    private function sanitizeForFilename($input) {
        // Replace spaces with underscores
        $sanitized = str_replace(' ', '_', $input);
        
        // Remove or replace dangerous characters
        $sanitized = preg_replace('/[<>:"\/\\|?*]/', '_', $sanitized);
        
        // Remove multiple underscores
        $sanitized = preg_replace('/_+/', '_', $sanitized);
        
        // Remove leading/trailing underscores
        $sanitized = trim($sanitized, '_');
        
        return $sanitized;
    }
    
    /**
     * Truncate filename while preserving extension
     * 
     * @param string $filename Original filename
     * @param int $maxLength Maximum length
     * @return string Truncated filename
     */
    private function truncateFilename($filename, $maxLength = 200) {
        if (strlen($filename) <= $maxLength) {
            return $filename;
        }
        
        $extension = pathinfo($filename, PATHINFO_EXTENSION);
        $nameWithoutExt = pathinfo($filename, PATHINFO_FILENAME);
        
        $maxNameLength = $maxLength - strlen($extension) - 1; // -1 for the dot
        $truncatedName = substr($nameWithoutExt, 0, $maxNameLength);
        
        return $truncatedName . '.' . $extension;
    }
}
```

### 3. Enhanced Export Controller

Update your main Export Controller to handle the enhanced functionality:

```php
<?php

class ExportController extends CI_Controller {
    
    private $filenameHelper;
    private $pythonApiUrl;
    
    public function __construct() {
        parent::__construct();
        $this->filenameHelper = new ExportFilenameHelper();
        $this->pythonApiUrl = $this->config->item('python_api_url');
        $this->load->library('curl');
    }
    
    /**
     * Export participants with enhanced filename support
     */
    public function participants($program_id) {
        try {
            // Get program data
            $program = $this->Program_model->get($program_id);
            if (!$program) {
                show_404();
            }
            
            // Get current filters from request
            $filters = $this->getAppliedFilters();
            
            // Get participant data
            $participants = $this->Participant_model->get_for_export($program_id, $filters);
            
            // Prepare enhanced payload
            $payload = [
                'data' => $participants,
                'template' => $this->input->get('template') ?: 'standard',
                'format' => $this->input->get('format') ?: 'excel',
                'filename' => $this->filenameHelper->generateDescriptiveFilename(
                    $program, 
                    'participants', 
                    $filters
                ),
                'sheet_name' => $this->filenameHelper->generateSheetName($program, 'participants'),
                'filters' => $filters,
                'options' => [
                    'include_related' => true,
                    'batch_size' => 5000,
                    'sort_by' => $this->input->get('sort_by') ?: 'created_at',
                    'sort_order' => $this->input->get('sort_order') ?: 'desc'
                ]
            ];
            
            // Record export request for tracking
            $export_request_id = $this->logExportRequest($program_id, 'participants', $payload);
            
            // Send request to Python service
            $response = $this->sendExportRequest('/api/ybb/export/participants', $payload);
            
            if ($response['status'] === 'success') {
                // Handle successful export
                $this->handleSuccessfulExport($response, $export_request_id);
            } else {
                // Handle export error
                $this->handleExportError($response, $export_request_id);
            }
            
        } catch (Exception $e) {
            log_message('error', 'Participants export failed: ' . $e->getMessage());
            $this->handleExportException($e);
        }
    }
    
    /**
     * Export payments with enhanced filename support
     */
    public function payments($program_id) {
        try {
            $program = $this->Program_model->get($program_id);
            if (!$program) {
                show_404();
            }
            
            $filters = $this->getAppliedFilters();
            $payments = $this->Payment_model->get_for_export($program_id, $filters);
            
            $payload = [
                'data' => $payments,
                'template' => $this->input->get('template') ?: 'standard',
                'format' => $this->input->get('format') ?: 'excel',
                'filename' => $this->filenameHelper->generateDescriptiveFilename(
                    $program, 
                    'payments', 
                    $filters
                ),
                'sheet_name' => $this->filenameHelper->generateSheetName($program, 'payments'),
                'filters' => $filters,
                'options' => [
                    'batch_size' => 5000,
                    'sort_by' => $this->input->get('sort_by') ?: 'payment_date',
                    'sort_order' => $this->input->get('sort_order') ?: 'desc'
                ]
            ];
            
            $export_request_id = $this->logExportRequest($program_id, 'payments', $payload);
            $response = $this->sendExportRequest('/api/ybb/export/payments', $payload);
            
            if ($response['status'] === 'success') {
                $this->handleSuccessfulExport($response, $export_request_id);
            } else {
                $this->handleExportError($response, $export_request_id);
            }
            
        } catch (Exception $e) {
            log_message('error', 'Payments export failed: ' . $e->getMessage());
            $this->handleExportException($e);
        }
    }
    
    /**
     * Export ambassadors with enhanced filename support  
     */
    public function ambassadors($program_id) {
        try {
            $program = $this->Program_model->get($program_id);
            if (!$program) {
                show_404();
            }
            
            $filters = $this->getAppliedFilters();
            $ambassadors = $this->Ambassador_model->get_for_export($program_id, $filters);
            
            $payload = [
                'data' => $ambassadors,
                'template' => $this->input->get('template') ?: 'standard',
                'format' => $this->input->get('format') ?: 'excel',
                'filename' => $this->filenameHelper->generateDescriptiveFilename(
                    $program, 
                    'ambassadors', 
                    $filters
                ),
                'sheet_name' => $this->filenameHelper->generateSheetName($program, 'ambassadors'),
                'filters' => $filters
            ];
            
            $export_request_id = $this->logExportRequest($program_id, 'ambassadors', $payload);
            $response = $this->sendExportRequest('/api/ybb/export/ambassadors', $payload);
            
            if ($response['status'] === 'success') {
                $this->handleSuccessfulExport($response, $export_request_id);
            } else {
                $this->handleExportError($response, $export_request_id);
            }
            
        } catch (Exception $e) {
            log_message('error', 'Ambassadors export failed: ' . $e->getMessage());
            $this->handleExportException($e);
        }
    }
    
    /**
     * Handle successful export response
     */
    private function handleSuccessfulExport($response, $export_request_id) {
        $data = $response['data'];
        $metadata = $response['metadata'] ?? [];
        
        // Update export request log
        $this->updateExportRequestLog($export_request_id, [
            'status' => 'success',
            'export_id' => $data['export_id'],
            'file_name' => $data['file_name'],
            'file_size' => $data['file_size'],
            'record_count' => $data['record_count'],
            'processing_time' => $metadata['processing_time'] ?? null,
            'expires_at' => $data['expires_at'] ?? null
        ]);
        
        // Determine response based on export strategy
        if (isset($response['export_strategy']) && $response['export_strategy'] === 'multi_file') {
            $this->handleMultiFileExport($response);
        } else {
            $this->handleSingleFileExport($response);
        }
    }
    
    /**
     * Handle single file export response
     */
    private function handleSingleFileExport($response) {
        $data = $response['data'];
        
        // Prepare success response for frontend
        $frontendResponse = [
            'status' => 'success',
            'message' => 'Export completed successfully',
            'export_type' => 'single_file',
            'data' => [
                'export_id' => $data['export_id'],
                'file_name' => $data['file_name'],
                'download_url' => site_url("export/download/{$data['export_id']}"),
                'file_size' => $this->formatFileSize($data['file_size']),
                'record_count' => number_format($data['record_count']),
                'expires_at' => $this->formatExpiryTime($data['expires_at'] ?? null)
            ]
        ];
        
        // Return JSON response for AJAX or redirect for regular request
        if ($this->input->is_ajax_request()) {
            $this->output
                ->set_content_type('application/json')
                ->set_output(json_encode($frontendResponse));
        } else {
            // Store in session for display on redirect
            $this->session->set_flashdata('export_success', $frontendResponse);
            redirect($this->input->server('HTTP_REFERER') ?: 'admin/dashboard');
        }
    }
    
    /**
     * Handle multi-file export response
     */
    private function handleMultiFileExport($response) {
        $data = $response['data'];
        
        // Prepare multi-file response
        $frontendResponse = [
            'status' => 'success',
            'message' => 'Large export completed successfully',
            'export_type' => 'multi_file',
            'data' => [
                'export_id' => $data['export_id'],
                'total_records' => number_format($data['total_records']),
                'total_files' => $data['total_files'],
                'individual_files' => array_map(function($file) {
                    return [
                        'batch_number' => $file['batch_number'],
                        'file_name' => $file['file_name'],
                        'download_url' => site_url("export/download/{$file['export_id']}/batch/{$file['batch_number']}"),
                        'file_size' => $this->formatFileSize($file['file_size']),
                        'record_count' => number_format($file['record_count']),
                        'record_range' => $file['record_range']
                    ];
                }, $data['individual_files']),
                'archive' => [
                    'zip_file_name' => $data['archive']['zip_file_name'],
                    'download_url' => site_url("export/download/{$data['export_id']}/zip"),
                    'zip_file_size' => $this->formatFileSize($data['archive']['zip_file_size']),
                    'compression_ratio' => $data['archive']['compression_ratio'] . '%'
                ]
            ]
        ];
        
        if ($this->input->is_ajax_request()) {
            $this->output
                ->set_content_type('application/json')
                ->set_output(json_encode($frontendResponse));
        } else {
            $this->session->set_flashdata('export_success', $frontendResponse);
            redirect($this->input->server('HTTP_REFERER') ?: 'admin/dashboard');
        }
    }
    
    /**
     * Handle export errors
     */
    private function handleExportError($response, $export_request_id) {
        // Update export request log
        $this->updateExportRequestLog($export_request_id, [
            'status' => 'error',
            'error_message' => $response['message'] ?? 'Unknown error'
        ]);
        
        $errorResponse = [
            'status' => 'error',
            'message' => $response['message'] ?? 'Export failed',
            'request_id' => $response['request_id'] ?? null
        ];
        
        if ($this->input->is_ajax_request()) {
            $this->output
                ->set_status_header(400)
                ->set_content_type('application/json')
                ->set_output(json_encode($errorResponse));
        } else {
            $this->session->set_flashdata('export_error', $errorResponse);
            redirect($this->input->server('HTTP_REFERER') ?: 'admin/dashboard');
        }
    }
    
    /**
     * Send request to Python export service
     */
    private function sendExportRequest($endpoint, $payload) {
        $url = rtrim($this->pythonApiUrl, '/') . $endpoint;
        
        // Configure cURL options
        $options = [
            CURLOPT_URL => $url,
            CURLOPT_POST => true,
            CURLOPT_POSTFIELDS => json_encode($payload),
            CURLOPT_RETURNTRANSFER => true,
            CURLOPT_TIMEOUT => 300, // 5 minutes timeout for large exports
            CURLOPT_HTTPHEADER => [
                'Content-Type: application/json',
                'Accept: application/json'
            ]
        ];
        
        $ch = curl_init();
        curl_setopt_array($ch, $options);
        
        $response = curl_exec($ch);
        $httpCode = curl_getinfo($ch, CURLINFO_HTTP_CODE);
        $error = curl_error($ch);
        curl_close($ch);
        
        if ($error) {
            throw new Exception("cURL Error: " . $error);
        }
        
        $decodedResponse = json_decode($response, true);
        
        if (json_last_error() !== JSON_ERROR_NONE) {
            throw new Exception("Invalid JSON response from export service");
        }
        
        if ($httpCode >= 400) {
            log_message('error', "Export API error (HTTP $httpCode): " . $response);
        }
        
        return $decodedResponse;
    }
    
    /**
     * Get applied filters from request
     */
    private function getAppliedFilters() {
        $filters = [];
        
        // Common filters
        if ($this->input->get('status')) {
            $filters['status'] = $this->input->get('status');
        }
        
        if ($this->input->get('date_from')) {
            $filters['date_from'] = $this->input->get('date_from');
        }
        
        if ($this->input->get('date_to')) {
            $filters['date_to'] = $this->input->get('date_to');
        }
        
        // Type-specific filters
        $export_type = $this->router->method;
        
        switch($export_type) {
            case 'participants':
                if ($this->input->get('has_paid')) {
                    $filters['has_paid'] = (bool)$this->input->get('has_paid');
                }
                if ($this->input->get('form_status')) {
                    $filters['form_status'] = $this->input->get('form_status');
                }
                break;
                
            case 'payments':
                if ($this->input->get('payment_status')) {
                    $filters['payment_status'] = $this->input->get('payment_status');
                }
                if ($this->input->get('currency')) {
                    $filters['currency'] = $this->input->get('currency');
                }
                break;
                
            case 'ambassadors':
                if ($this->input->get('active_only')) {
                    $filters['active_only'] = (bool)$this->input->get('active_only');
                }
                break;
        }
        
        return $filters;
    }
    
    /**
     * Format file size for display
     */
    private function formatFileSize($bytes) {
        if ($bytes >= 1073741824) {
            return number_format($bytes / 1073741824, 2) . ' GB';
        } elseif ($bytes >= 1048576) {
            return number_format($bytes / 1048576, 2) . ' MB';
        } elseif ($bytes >= 1024) {
            return number_format($bytes / 1024, 2) . ' KB';
        } else {
            return $bytes . ' bytes';
        }
    }
    
    /**
     * Format expiry time for display
     */
    private function formatExpiryTime($expires_at) {
        if (!$expires_at) {
            return '24 hours from now';
        }
        
        $expiry = new DateTime($expires_at);
        $now = new DateTime();
        $interval = $now->diff($expiry);
        
        if ($interval->days > 0) {
            return $interval->days . ' day' . ($interval->days > 1 ? 's' : '');
        } elseif ($interval->h > 0) {
            return $interval->h . ' hour' . ($interval->h > 1 ? 's' : '');
        } else {
            return $interval->i . ' minute' . ($interval->i > 1 ? 's' : '');
        }
    }
    
    /**
     * Log export request for tracking
     */
    private function logExportRequest($program_id, $type, $payload) {
        $data = [
            'program_id' => $program_id,
            'export_type' => $type,
            'user_id' => $this->session->userdata('user_id'),
            'filters' => json_encode($payload['filters'] ?? []),
            'custom_filename' => $payload['filename'] ?? null,
            'record_count' => count($payload['data']),
            'status' => 'pending',
            'created_at' => date('Y-m-d H:i:s')
        ];
        
        return $this->db->insert('export_requests', $data) ? $this->db->insert_id() : null;
    }
    
    /**
     * Update export request log
     */
    private function updateExportRequestLog($export_request_id, $data) {
        if (!$export_request_id) return;
        
        $data['updated_at'] = date('Y-m-d H:i:s');
        $this->db->where('id', $export_request_id)->update('export_requests', $data);
    }
}
```

### 4. Database Schema Updates

Add a table to track export requests:

```sql
-- Create export_requests table for tracking
CREATE TABLE export_requests (
    id INT AUTO_INCREMENT PRIMARY KEY,
    program_id INT NOT NULL,
    export_type ENUM('participants', 'payments', 'ambassadors') NOT NULL,
    user_id INT NOT NULL,
    filters JSON,
    custom_filename VARCHAR(255),
    record_count INT,
    status ENUM('pending', 'success', 'error') DEFAULT 'pending',
    export_id VARCHAR(255),
    file_name VARCHAR(255),
    file_size INT,
    processing_time DECIMAL(10,3),
    error_message TEXT,
    expires_at TIMESTAMP NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    INDEX idx_program_id (program_id),
    INDEX idx_user_id (user_id),
    INDEX idx_status (status),
    INDEX idx_created_at (created_at),
    
    FOREIGN KEY (program_id) REFERENCES programs(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);
```

### 5. Frontend JavaScript Updates

Update your JavaScript to handle the enhanced export responses:

```javascript
// Enhanced export handling
class ExportManager {
    constructor() {
        this.currentExports = new Map();
        this.initializeEventHandlers();
    }
    
    initializeEventHandlers() {
        // Export button handlers
        $('.export-btn').on('click', (e) => {
            e.preventDefault();
            this.handleExportRequest(e.target);
        });
        
        // Download handlers  
        $(document).on('click', '.download-btn', (e) => {
            e.preventDefault();
            this.handleDownload(e.target);
        });
    }
    
    handleExportRequest(button) {
        const $btn = $(button);
        const exportType = $btn.data('export-type');
        const programId = $btn.data('program-id');
        
        // Show loading state
        this.showExportLoading($btn);
        
        // Get current filters
        const filters = this.collectFilters();
        
        // Build export URL
        const exportUrl = `/admin/export/${exportType}/${programId}`;
        
        // Add filters as query parameters
        const queryParams = new URLSearchParams(filters);
        const fullUrl = `${exportUrl}?${queryParams.toString()}`;
        
        // Send AJAX request
        $.ajax({
            url: fullUrl,
            method: 'POST',
            dataType: 'json',
            timeout: 300000, // 5 minutes timeout
            success: (response) => {
                this.handleExportSuccess(response, $btn);
            },
            error: (xhr, status, error) => {
                this.handleExportError(xhr, $btn);
            }
        });
    }
    
    handleExportSuccess(response, $btn) {
        this.hideExportLoading($btn);
        
        if (response.export_type === 'single_file') {
            this.showSingleFileExportResult(response);
        } else if (response.export_type === 'multi_file') {
            this.showMultiFileExportResult(response);
        }
        
        // Store export info for future reference
        this.currentExports.set(response.data.export_id, response);
    }
    
    showSingleFileExportResult(response) {
        const data = response.data;
        
        const html = `
            <div class="export-result success">
                <div class="export-header">
                    <h4><i class="fas fa-check-circle text-success"></i> Export Completed Successfully</h4>
                    <p class="mb-0">Your export has been generated and is ready for download.</p>
                </div>
                
                <div class="export-details">
                    <div class="row">
                        <div class="col-md-6">
                            <strong>File:</strong> ${data.file_name}<br>
                            <strong>Size:</strong> ${data.file_size}<br>
                            <strong>Records:</strong> ${data.record_count}
                        </div>
                        <div class="col-md-6">
                            <strong>Expires:</strong> ${data.expires_at}<br>
                            <strong>Export ID:</strong> <code>${data.export_id}</code>
                        </div>
                    </div>
                </div>
                
                <div class="export-actions mt-3">
                    <a href="${data.download_url}" class="btn btn-success download-btn">
                        <i class="fas fa-download"></i> Download File
                    </a>
                    <button type="button" class="btn btn-outline-secondary" onclick="this.closest('.export-result').remove()">
                        <i class="fas fa-times"></i> Dismiss
                    </button>
                </div>
            </div>
        `;
        
        $('#export-results').html(html);
        $('html, body').animate({ scrollTop: $('#export-results').offset().top }, 500);
    }
    
    showMultiFileExportResult(response) {
        const data = response.data;
        
        // Build individual file list
        const fileList = data.individual_files.map(file => `
            <tr>
                <td>Batch ${file.batch_number}</td>
                <td>${file.file_name}</td>
                <td>${file.record_count}</td>
                <td>${file.record_range}</td>
                <td>${file.file_size}</td>
                <td>
                    <a href="${file.download_url}" class="btn btn-sm btn-outline-primary">
                        <i class="fas fa-download"></i> Download
                    </a>
                </td>
            </tr>
        `).join('');
        
        const html = `
            <div class="export-result success multi-file">
                <div class="export-header">
                    <h4><i class="fas fa-check-circle text-success"></i> Large Export Completed</h4>
                    <p class="mb-0">Your large dataset has been split into multiple files for easier handling.</p>
                </div>
                
                <div class="export-summary">
                    <div class="row">
                        <div class="col-md-3">
                            <div class="stat-card">
                                <div class="stat-value">${data.total_records}</div>
                                <div class="stat-label">Total Records</div>
                            </div>
                        </div>
                        <div class="col-md-3">
                            <div class="stat-card">
                                <div class="stat-value">${data.total_files}</div>
                                <div class="stat-label">Files Generated</div>
                            </div>
                        </div>
                        <div class="col-md-3">
                            <div class="stat-card">
                                <div class="stat-value">${data.archive.zip_file_size}</div>
                                <div class="stat-label">Archive Size</div>
                            </div>
                        </div>
                        <div class="col-md-3">
                            <div class="stat-card">
                                <div class="stat-value">${data.archive.compression_ratio}</div>
                                <div class="stat-label">Compression</div>
                            </div>
                        </div>
                    </div>
                </div>
                
                <div class="download-options mt-4">
                    <h5>Download Options</h5>
                    <div class="row">
                        <div class="col-md-6">
                            <div class="download-option recommended">
                                <h6><i class="fas fa-file-archive"></i> Complete Archive (Recommended)</h6>
                                <p>Download all files in a single ZIP archive</p>
                                <a href="${data.archive.download_url}" class="btn btn-success">
                                    <i class="fas fa-download"></i> Download ZIP (${data.archive.zip_file_size})
                                </a>
                            </div>
                        </div>
                        <div class="col-md-6">
                            <div class="download-option">
                                <h6><i class="fas fa-files-o"></i> Individual Files</h6>
                                <p>Download specific batch files individually</p>
                                <button type="button" class="btn btn-outline-primary" data-toggle="collapse" data-target="#individual-files">
                                    <i class="fas fa-list"></i> Show Individual Files
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
                
                <div class="collapse mt-3" id="individual-files">
                    <div class="table-responsive">
                        <table class="table table-striped">
                            <thead>
                                <tr>
                                    <th>Batch</th>
                                    <th>Filename</th>
                                    <th>Records</th>
                                    <th>Range</th>
                                    <th>Size</th>
                                    <th>Action</th>
                                </tr>
                            </thead>
                            <tbody>
                                ${fileList}
                            </tbody>
                        </table>
                    </div>
                </div>
                
                <div class="export-actions mt-3">
                    <button type="button" class="btn btn-outline-secondary" onclick="this.closest('.export-result').remove()">
                        <i class="fas fa-times"></i> Dismiss
                    </button>
                </div>
            </div>
        `;
        
        $('#export-results').html(html);
        $('html, body').animate({ scrollTop: $('#export-results').offset().top }, 500);
    }
    
    handleExportError(xhr, $btn) {
        this.hideExportLoading($btn);
        
        let errorMessage = 'An unknown error occurred';
        
        if (xhr.responseJSON && xhr.responseJSON.message) {
            errorMessage = xhr.responseJSON.message;
        } else if (xhr.statusText) {
            errorMessage = xhr.statusText;
        }
        
        const html = `
            <div class="export-result error">
                <div class="export-header">
                    <h4><i class="fas fa-exclamation-circle text-danger"></i> Export Failed</h4>
                    <p class="mb-0 text-danger">${errorMessage}</p>
                </div>
                <div class="export-actions mt-3">
                    <button type="button" class="btn btn-outline-secondary" onclick="this.closest('.export-result').remove()">
                        <i class="fas fa-times"></i> Dismiss
                    </button>
                </div>
            </div>
        `;
        
        $('#export-results').html(html);
    }
    
    showExportLoading($btn) {
        $btn.prop('disabled', true)
            .find('.btn-text').text('Generating Export...')
            .siblings('.fas').removeClass('fa-download').addClass('fa-spinner fa-spin');
    }
    
    hideExportLoading($btn) {
        $btn.prop('disabled', false)
            .find('.btn-text').text('Export')
            .siblings('.fas').removeClass('fa-spinner fa-spin').addClass('fa-download');
    }
    
    collectFilters() {
        const filters = {};
        
        // Collect filter values from form
        $('#export-filters input, #export-filters select').each(function() {
            const $input = $(this);
            const name = $input.attr('name');
            const value = $input.val();
            
            if (name && value) {
                filters[name] = value;
            }
        });
        
        return filters;
    }
}

// Initialize export manager
$(document).ready(() => {
    window.exportManager = new ExportManager();
});
```

### 6. Configuration Updates

Update your CodeIgniter configuration:

```php
// application/config/config.php

// Python API configuration
$config['python_api_url'] = 'http://localhost:5000'; // Update with your Python service URL
$config['export_timeout'] = 300; // 5 minutes timeout for exports
$config['max_export_records'] = 10000; // Maximum records before chunking
```

### 7. View Templates Updates

Update your export views to handle the enhanced functionality:

```php
<!-- application/views/admin/exports/participants.php -->
<div class="card">
    <div class="card-header">
        <h4><i class="fas fa-users"></i> Export Participants</h4>
    </div>
    <div class="card-body">
        <!-- Export filters form -->
        <form id="export-filters" class="mb-4">
            <div class="row">
                <div class="col-md-3">
                    <label>Status</label>
                    <select name="status" class="form-control">
                        <option value="">All Statuses</option>
                        <option value="approved">Approved</option>
                        <option value="pending">Pending</option>
                        <option value="rejected">Rejected</option>
                    </select>
                </div>
                
                <div class="col-md-3">
                    <label>Payment Status</label>
                    <select name="has_paid" class="form-control">
                        <option value="">All</option>
                        <option value="1">Paid</option>
                        <option value="0">Unpaid</option>
                    </select>
                </div>
                
                <div class="col-md-3">
                    <label>Date From</label>
                    <input type="date" name="date_from" class="form-control">
                </div>
                
                <div class="col-md-3">
                    <label>Date To</label>
                    <input type="date" name="date_to" class="form-control">
                </div>
            </div>
            
            <div class="row mt-3">
                <div class="col-md-3">
                    <label>Template</label>
                    <select name="template" class="form-control">
                        <option value="standard">Standard</option>
                        <option value="detailed">Detailed</option>
                        <option value="summary">Summary</option>
                        <option value="complete">Complete</option>
                    </select>
                </div>
                
                <div class="col-md-3">
                    <label>Sort By</label>
                    <select name="sort_by" class="form-control">
                        <option value="created_at">Registration Date</option>
                        <option value="name">Name</option>
                        <option value="email">Email</option>
                    </select>
                </div>
                
                <div class="col-md-3">
                    <label>Sort Order</label>
                    <select name="sort_order" class="form-control">
                        <option value="desc">Newest First</option>
                        <option value="asc">Oldest First</option>
                    </select>
                </div>
                
                <div class="col-md-3">
                    <label>&nbsp;</label>
                    <button type="button" class="btn btn-primary export-btn d-block" 
                            data-export-type="participants" 
                            data-program-id="<?= $program->id ?>">
                        <i class="fas fa-download"></i>
                        <span class="btn-text">Export Participants</span>
                    </button>
                </div>
            </div>
        </form>
        
        <!-- Export results will be displayed here -->
        <div id="export-results"></div>
    </div>
</div>

<!-- Add CSS for styling -->
<style>
.export-result {
    border: 1px solid #ddd;
    border-radius: 8px;
    padding: 20px;
    margin: 20px 0;
}

.export-result.success {
    border-color: #28a745;
    background-color: #f8fff9;
}

.export-result.error {
    border-color: #dc3545;
    background-color: #fff8f8;
}

.export-header h4 {
    margin-bottom: 10px;
}

.export-details, .export-summary {
    margin: 15px 0;
    padding: 15px;
    background-color: #f8f9fa;
    border-radius: 5px;
}

.stat-card {
    text-align: center;
    padding: 15px;
    background: white;
    border-radius: 5px;
    margin-bottom: 10px;
}

.stat-value {
    font-size: 2em;
    font-weight: bold;
    color: #007bff;
}

.stat-label {
    color: #6c757d;
    font-size: 0.9em;
}

.download-option {
    padding: 15px;
    border: 1px solid #ddd;
    border-radius: 5px;
    margin-bottom: 10px;
}

.download-option.recommended {
    border-color: #28a745;
    background-color: #f8fff9;
}

.download-option h6 {
    color: #007bff;
    margin-bottom: 10px;
}
</style>
```

## 🔄 Processing Time Handling

### Enhanced Processing Time Display

Update your views to show processing time information:

```php
<!-- Processing time indicator -->
<div class="processing-info" style="display: none;">
    <div class="progress mb-3">
        <div class="progress-bar progress-bar-striped progress-bar-animated" 
             role="progressbar" style="width: 100%">
            Processing export...
        </div>
    </div>
    <div class="processing-details">
        <small class="text-muted">
            <i class="fas fa-clock"></i> Started: <span id="start-time"></span> |
            <i class="fas fa-hourglass-half"></i> Elapsed: <span id="elapsed-time">0s</span>
        </small>
    </div>
</div>
```

### JavaScript for Processing Time Tracking

```javascript
class ProcessingTimeTracker {
    constructor() {
        this.startTime = null;
        this.intervalId = null;
    }
    
    start() {
        this.startTime = new Date();
        $('#start-time').text(this.startTime.toLocaleTimeString());
        $('.processing-info').show();
        
        // Update elapsed time every second
        this.intervalId = setInterval(() => {
            const elapsed = Math.floor((new Date() - this.startTime) / 1000);
            $('#elapsed-time').text(elapsed + 's');
        }, 1000);
    }
    
    stop(processingTime = null) {
        if (this.intervalId) {
            clearInterval(this.intervalId);
            this.intervalId = null;
        }
        
        $('.processing-info').hide();
        
        if (processingTime) {
            this.showProcessingComplete(processingTime);
        }
    }
    
    showProcessingComplete(processingTime) {
        const completedHtml = `
            <div class="alert alert-success alert-dismissible fade show" role="alert">
                <i class="fas fa-check-circle"></i>
                <strong>Export completed!</strong> 
                Processing time: ${processingTime}s
                <button type="button" class="close" data-dismiss="alert">
                    <span>&times;</span>
                </button>
            </div>
        `;
        
        $('.processing-info').after(completedHtml);
    }
}
```

## 🚨 Error Handling Improvements

### Enhanced Error Display

```php
// Handle specific error types
switch($error_type) {
    case 'filename_validation':
        $message = "Invalid filename. Please avoid special characters like < > : \" / \\ | ? *";
        break;
    case 'large_dataset':
        $message = "Dataset is too large. The export has been split into multiple files.";
        break;
    case 'timeout':
        $message = "Export is taking longer than expected. Please try again or contact support.";
        break;
    default:
        $message = "An error occurred during export. Please try again.";
}
```

## 📊 Export Analytics

Track export usage and performance:

```php
// Export analytics model
class Export_analytics_model extends CI_Model {
    
    public function log_export_metrics($data) {
        $metrics = [
            'program_id' => $data['program_id'],
            'export_type' => $data['export_type'],
            'record_count' => $data['record_count'],
            'file_size' => $data['file_size'],
            'processing_time' => $data['processing_time'],
            'custom_filename_used' => !empty($data['custom_filename']),
            'multi_file_export' => $data['export_strategy'] === 'multi_file',
            'user_id' => $this->session->userdata('user_id'),
            'created_at' => date('Y-m-d H:i:s')
        ];
        
        $this->db->insert('export_analytics', $metrics);
    }
    
    public function get_export_statistics($program_id = null, $days = 30) {
        $this->db->select('
            COUNT(*) as total_exports,
            AVG(processing_time) as avg_processing_time,
            MAX(processing_time) as max_processing_time,
            AVG(record_count) as avg_record_count,
            SUM(file_size) as total_file_size,
            SUM(CASE WHEN custom_filename_used = 1 THEN 1 ELSE 0 END) as custom_filename_count,
            SUM(CASE WHEN multi_file_export = 1 THEN 1 ELSE 0 END) as multi_file_count
        ');
        
        if ($program_id) {
            $this->db->where('program_id', $program_id);
        }
        
        $this->db->where('created_at >=', date('Y-m-d H:i:s', strtotime("-{$days} days")));
        
        return $this->db->get('export_analytics')->row();
    }
}
```

## 🎯 Summary of Required Changes

1. **✅ Enhanced Export Payload**: Include filename and sheet_name parameters
2. **✅ Filename Generation**: Add descriptive filename generation logic
3. **✅ Response Handling**: Handle both single-file and multi-file exports
4. **✅ Frontend Updates**: Enhanced JavaScript for better UX
5. **✅ Database Updates**: Add export tracking table
6. **✅ Processing Time**: Display and track processing times
7. **✅ Error Handling**: Improved error messages and handling
8. **✅ Analytics**: Export usage tracking and metrics

## 🚀 Deployment Checklist

- [ ] Update CodeIgniter export controllers
- [ ] Add ExportFilenameHelper class
- [ ] Create export_requests database table
- [ ] Update frontend JavaScript and CSS
- [ ] Update view templates
- [ ] Test with Python Flask service
- [ ] Configure API timeout settings
- [ ] Update user documentation

The enhanced integration provides a much better user experience with descriptive filenames, improved processing feedback, and robust error handling while maintaining backward compatibility.
