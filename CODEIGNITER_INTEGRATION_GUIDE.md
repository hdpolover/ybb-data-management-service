# YBB Export API - CodeIgniter Integration Guide

## Overview

This guide provides comprehensive documentation for integrating the YBB Export API with your CodeIgniter application for production use.

## Table of Contents

1. [API Service Overview](#api-service-overview)
2. [CodeIgniter Integration](#codeigniter-integration)
3. [PHP Client Class](#php-client-class)
4. [Usage Examples](#usage-examples)
5. [Error Handling](#error-handling)
6. [Performance Considerations](#performance-considerations)
7. [Security Guidelines](#security-guidelines)
8. [Production Deployment](#production-deployment)

## API Service Overview

The YBB Export API is a Python Flask service specifically designed to handle large-scale data exports for the YBB (Young Business Builder) platform. It provides efficient data processing, Excel generation, and handles large datasets through intelligent chunking.

### Key Features

- **Multi-format Export**: Excel (.xlsx) and CSV formats
- **Template-based Export**: Predefined templates for different data types
- **Large Dataset Handling**: Automatic chunking for datasets > 5,000 records
- **Memory Optimization**: Efficient processing to handle 50,000+ records
- **Professional Excel Formatting**: Headers, styling, and column auto-sizing
- **ZIP Archive Support**: Multi-file exports compressed into ZIP archives

### Supported Data Types

1. **Participants**: YBB program participants with various export templates
2. **Payments**: Payment records with detailed financial information
3. **Ambassadors**: Ambassador program data with commission tracking

## CodeIgniter Integration

### 1. Environment Configuration

Add the following to your CodeIgniter `.env` file:

```bash
# YBB Export API Configuration
YBB_EXPORT_API_URL=http://localhost:5000
YBB_EXPORT_API_TIMEOUT=300
YBB_EXPORT_MAX_RECORDS=50000
```

### 2. Create Config File

Create `application/config/ybb_export.php`:

```php
<?php
defined('BASEPATH') OR exit('No direct script access allowed');

/*
|--------------------------------------------------------------------------
| YBB Export API Configuration
|--------------------------------------------------------------------------
*/

$config['ybb_export'] = array(
    'api_url' => getenv('YBB_EXPORT_API_URL') ?: 'http://localhost:5000',
    'timeout' => (int) (getenv('YBB_EXPORT_API_TIMEOUT') ?: 300),
    'max_records' => (int) (getenv('YBB_EXPORT_MAX_RECORDS') ?: 50000),
    'chunk_threshold' => 5000,
    'retry_attempts' => 3,
    'retry_delay' => 2, // seconds
    'download_timeout' => 600, // 10 minutes for large files
    'temp_storage_path' => APPPATH . 'cache/exports/',
    'cleanup_after_hours' => 24
);
```

### 3. Create Export Library

Create `application/libraries/Ybb_export.php`:

```php
<?php
defined('BASEPATH') OR exit('No direct script access allowed');

/**
 * YBB Export Library for CodeIgniter
 * 
 * Provides seamless integration with the YBB Export API service
 * for handling large-scale data exports.
 */
class Ybb_export 
{
    private $CI;
    private $config;
    private $api_url;
    
    public function __construct($config = array())
    {
        $this->CI =& get_instance();
        $this->CI->load->config('ybb_export');
        
        $this->config = array_merge(
            $this->CI->config->item('ybb_export'),
            $config
        );
        
        $this->api_url = rtrim($this->config['api_url'], '/');
        
        // Ensure temp storage directory exists
        $this->_ensure_temp_directory();
        
        log_message('info', 'YBB Export Library initialized');
    }
    
    /**
     * Export participants data
     */
    public function export_participants($data, $options = array())
    {
        return $this->_create_export('participants', $data, $options);
    }
    
    /**
     * Export payments data
     */
    public function export_payments($data, $options = array())
    {
        return $this->_create_export('payments', $data, $options);
    }
    
    /**
     * Export ambassadors data
     */
    public function export_ambassadors($data, $options = array())
    {
        return $this->_create_export('ambassadors', $data, $options);
    }
    
    /**
     * Get export status
     */
    public function get_export_status($export_id)
    {
        $url = $this->api_url . "/api/ybb/export/{$export_id}/status";
        
        return $this->_make_request('GET', $url);
    }
    
    /**
     * Download export file
     */
    public function download_export($export_id, $save_path = null)
    {
        $url = $this->api_url . "/api/ybb/export/{$export_id}/download";
        
        return $this->_download_file($url, $save_path);
    }
    
    /**
     * Download ZIP archive (for large exports)
     */
    public function download_export_zip($export_id, $save_path = null)
    {
        $url = $this->api_url . "/api/ybb/export/{$export_id}/download/zip";
        
        return $this->_download_file($url, $save_path);
    }
    
    /**
     * Download specific batch file
     */
    public function download_batch_file($export_id, $batch_number, $save_path = null)
    {
        $url = $this->api_url . "/api/ybb/export/{$export_id}/download/batch/{$batch_number}";
        
        return $this->_download_file($url, $save_path);
    }
    
    /**
     * Get available templates
     */
    public function get_templates($export_type = null)
    {
        if ($export_type) {
            $url = $this->api_url . "/api/ybb/templates/{$export_type}";
        } else {
            $url = $this->api_url . "/api/ybb/templates";
        }
        
        return $this->_make_request('GET', $url);
    }
    
    /**
     * Get status mappings
     */
    public function get_status_mappings()
    {
        $url = $this->api_url . "/api/ybb/status-mappings";
        
        return $this->_make_request('GET', $url);
    }
    
    /**
     * Test API connectivity
     */
    public function test_connection()
    {
        $url = $this->api_url . "/health";
        
        return $this->_make_request('GET', $url);
    }
    
    /**
     * Create export request
     */
    private function _create_export($export_type, $data, $options = array())
    {
        if (empty($data)) {
            return array(
                'success' => false,
                'message' => 'No data provided for export'
            );
        }
        
        if (count($data) > $this->config['max_records']) {
            return array(
                'success' => false,
                'message' => "Data exceeds maximum limit of {$this->config['max_records']} records"
            );
        }
        
        $payload = array_merge(array(
            'data' => $data,
            'template' => 'standard',
            'format' => 'excel'
        ), $options);
        
        $url = $this->api_url . "/api/ybb/export/{$export_type}";
        
        return $this->_make_request('POST', $url, $payload);
    }
    
    /**
     * Make HTTP request to API
     */
    private function _make_request($method, $url, $data = null)
    {
        $curl = curl_init();
        
        $curl_options = array(
            CURLOPT_URL => $url,
            CURLOPT_RETURNTRANSFER => true,
            CURLOPT_TIMEOUT => $this->config['timeout'],
            CURLOPT_CUSTOMREQUEST => $method,
            CURLOPT_HTTPHEADER => array(
                'Content-Type: application/json',
                'Accept: application/json'
            ),
            CURLOPT_SSL_VERIFYPEER => false,
            CURLOPT_FOLLOWLOCATION => true
        );
        
        if ($data && in_array($method, array('POST', 'PUT', 'PATCH'))) {
            $curl_options[CURLOPT_POSTFIELDS] = json_encode($data);
        }
        
        curl_setopt_array($curl, $curl_options);
        
        $response = curl_exec($curl);
        $http_code = curl_getinfo($curl, CURLINFO_HTTP_CODE);
        $error = curl_error($curl);
        
        curl_close($curl);
        
        if ($response === false || !empty($error)) {
            log_message('error', "YBB Export API request failed: " . $error);
            return array(
                'success' => false,
                'message' => 'API request failed: ' . $error
            );
        }
        
        $decoded_response = json_decode($response, true);
        
        if ($http_code >= 200 && $http_code < 300) {
            return array(
                'success' => true,
                'data' => $decoded_response,
                'http_code' => $http_code
            );
        } else {
            $error_message = isset($decoded_response['message']) 
                ? $decoded_response['message'] 
                : 'Unknown API error';
                
            log_message('error', "YBB Export API error (HTTP {$http_code}): " . $error_message);
            
            return array(
                'success' => false,
                'message' => $error_message,
                'http_code' => $http_code,
                'raw_response' => $decoded_response
            );
        }
    }
    
    /**
     * Download file from API
     */
    private function _download_file($url, $save_path = null)
    {
        if (!$save_path) {
            $save_path = $this->config['temp_storage_path'] . 'export_' . time() . '_' . rand(1000, 9999);
        }
        
        $curl = curl_init();
        $file_handle = fopen($save_path, 'w+');
        
        if (!$file_handle) {
            return array(
                'success' => false,
                'message' => 'Could not create file for download'
            );
        }
        
        curl_setopt_array($curl, array(
            CURLOPT_URL => $url,
            CURLOPT_RETURNTRANSFER => false,
            CURLOPT_TIMEOUT => $this->config['download_timeout'],
            CURLOPT_FILE => $file_handle,
            CURLOPT_FOLLOWLOCATION => true,
            CURLOPT_SSL_VERIFYPEER => false
        ));
        
        $result = curl_exec($curl);
        $http_code = curl_getinfo($curl, CURLINFO_HTTP_CODE);
        $error = curl_error($curl);
        
        curl_close($curl);
        fclose($file_handle);
        
        if ($result === false || !empty($error) || $http_code >= 400) {
            unlink($save_path); // Clean up failed download
            
            return array(
                'success' => false,
                'message' => "Download failed: " . ($error ?: "HTTP {$http_code}")
            );
        }
        
        return array(
            'success' => true,
            'file_path' => $save_path,
            'file_size' => filesize($save_path),
            'message' => 'File downloaded successfully'
        );
    }
    
    /**
     * Ensure temp directory exists
     */
    private function _ensure_temp_directory()
    {
        $temp_dir = $this->config['temp_storage_path'];
        
        if (!is_dir($temp_dir)) {
            if (!mkdir($temp_dir, 0755, true)) {
                log_message('error', 'Could not create YBB export temp directory: ' . $temp_dir);
            }
        }
    }
    
    /**
     * Clean up old temporary files
     */
    public function cleanup_temp_files()
    {
        $temp_dir = $this->config['temp_storage_path'];
        $cleanup_threshold = time() - ($this->config['cleanup_after_hours'] * 3600);
        $cleaned_count = 0;
        
        if (is_dir($temp_dir)) {
            $files = glob($temp_dir . '*');
            
            foreach ($files as $file) {
                if (is_file($file) && filemtime($file) < $cleanup_threshold) {
                    if (unlink($file)) {
                        $cleaned_count++;
                    }
                }
            }
        }
        
        log_message('info', "YBB Export: Cleaned up {$cleaned_count} temporary files");
        
        return $cleaned_count;
    }
}
```

## Usage Examples

### 1. Basic Participant Export

```php
// In your controller
public function export_participants()
{
    $this->load->library('ybb_export');
    $this->load->model('Participant_model');
    
    // Get participant data
    $participants = $this->Participant_model->get_all_participants();
    
    // Export with standard template
    $result = $this->ybb_export->export_participants($participants, array(
        'template' => 'standard',
        'format' => 'excel',
        'filename' => 'participants_export.xlsx'
    ));
    
    if ($result['success']) {
        $export_data = $result['data'];
        
        // Store export ID for later download
        $this->session->set_userdata('last_export_id', $export_data['data']['export_id']);
        
        // Redirect to download or status page
        redirect('exports/download/' . $export_data['data']['export_id']);
    } else {
        $this->session->set_flashdata('error', $result['message']);
        redirect('exports');
    }
}
```

### 2. Large Dataset Export with Progress Tracking

```php
public function export_large_participants()
{
    $this->load->library('ybb_export');
    $this->load->model('Participant_model');
    
    // Get large dataset
    $participants = $this->Participant_model->get_all_participants_for_export();
    
    if (count($participants) > 5000) {
        // This will automatically use chunking
        $result = $this->ybb_export->export_participants($participants, array(
            'template' => 'complete',
            'format' => 'excel'
        ));
        
        if ($result['success']) {
            $export_data = $result['data'];
            
            if (isset($export_data['export_strategy']) && $export_data['export_strategy'] === 'multi_file') {
                // Large export with multiple files
                $this->_handle_large_export($export_data);
            } else {
                // Single file export
                $this->_handle_single_export($export_data);
            }
        }
    }
}

private function _handle_large_export($export_data)
{
    $data = array(
        'export_id' => $export_data['data']['export_id'],
        'total_records' => $export_data['data']['total_records'],
        'total_files' => $export_data['data']['total_files'],
        'individual_files' => $export_data['data']['individual_files'],
        'archive_info' => $export_data['data']['archive']
    );
    
    $this->load->view('exports/large_export_complete', $data);
}
```

### 3. Export Status Monitoring

```php
public function check_export_status($export_id)
{
    $this->load->library('ybb_export');
    
    $result = $this->ybb_export->get_export_status($export_id);
    
    if ($result['success']) {
        $status_data = $result['data'];
        
        // Return JSON for AJAX calls
        $this->output
            ->set_content_type('application/json')
            ->set_output(json_encode(array(
                'success' => true,
                'status' => $status_data['status'],
                'export_type' => $status_data['export_type'],
                'record_count' => $status_data['record_count'],
                'created_at' => $status_data['created_at']
            )));
    } else {
        $this->output
            ->set_content_type('application/json')
            ->set_output(json_encode(array(
                'success' => false,
                'message' => $result['message']
            )));
    }
}
```

### 4. Download Handling

```php
public function download_export($export_id)
{
    $this->load->library('ybb_export');
    
    // Download to temporary location
    $download_result = $this->ybb_export->download_export($export_id);
    
    if ($download_result['success']) {
        $file_path = $download_result['file_path'];
        
        // Get file info
        $file_name = basename($file_path);
        $file_size = $download_result['file_size'];
        
        // Set headers for download
        header('Content-Description: File Transfer');
        header('Content-Type: application/vnd.openxmlformats-officedocument.spreadsheetml.sheet');
        header('Content-Disposition: attachment; filename="' . $file_name . '"');
        header('Content-Length: ' . $file_size);
        header('Cache-Control: must-revalidate');
        header('Pragma: public');
        
        // Output file
        readfile($file_path);
        
        // Clean up temporary file
        unlink($file_path);
        
        exit;
    } else {
        show_404();
    }
}
```

## Error Handling

### Comprehensive Error Handling Example

```php
public function robust_export_participants()
{
    $this->load->library('ybb_export');
    
    try {
        // Test API connection first
        $connection_test = $this->ybb_export->test_connection();
        
        if (!$connection_test['success']) {
            throw new Exception('Export service is not available');
        }
        
        // Get data
        $participants = $this->Participant_model->get_participants_for_export();
        
        if (empty($participants)) {
            throw new Exception('No participants found for export');
        }
        
        // Validate data size
        if (count($participants) > 50000) {
            throw new Exception('Dataset too large. Please apply filters to reduce the number of records.');
        }
        
        // Create export
        $result = $this->ybb_export->export_participants($participants, array(
            'template' => $this->input->post('template') ?: 'standard',
            'format' => $this->input->post('format') ?: 'excel'
        ));
        
        if (!$result['success']) {
            throw new Exception($result['message']);
        }
        
        // Success handling
        $this->session->set_flashdata('success', 'Export created successfully');
        $this->session->set_userdata('export_id', $result['data']['data']['export_id']);
        
        redirect('exports/status/' . $result['data']['data']['export_id']);
        
    } catch (Exception $e) {
        log_message('error', 'Export failed: ' . $e->getMessage());
        $this->session->set_flashdata('error', $e->getMessage());
        redirect('exports');
    }
}
```

## Performance Considerations

### 1. Memory Management

```php
// For very large datasets, process in batches
public function export_participants_in_batches()
{
    $this->load->library('ybb_export');
    $batch_size = 10000;
    $offset = 0;
    $export_ids = array();
    
    do {
        $participants = $this->Participant_model->get_participants_batch($batch_size, $offset);
        
        if (!empty($participants)) {
            $result = $this->ybb_export->export_participants($participants, array(
                'template' => 'standard',
                'filename' => "participants_batch_" . ($offset / $batch_size + 1) . ".xlsx"
            ));
            
            if ($result['success']) {
                $export_ids[] = $result['data']['data']['export_id'];
            }
        }
        
        $offset += $batch_size;
        
    } while (count($participants) === $batch_size);
    
    // Store all export IDs for batch download
    $this->session->set_userdata('batch_export_ids', $export_ids);
}
```

### 2. Asynchronous Processing

```php
// Use CodeIgniter's queue system or background jobs
public function queue_large_export()
{
    $export_job = array(
        'job_type' => 'ybb_export_participants',
        'data' => array(
            'filters' => $this->input->post('filters'),
            'template' => $this->input->post('template'),
            'user_id' => $this->session->userdata('user_id')
        ),
        'created_at' => date('Y-m-d H:i:s')
    );
    
    $this->load->model('Job_queue_model');
    $job_id = $this->Job_queue_model->add_job($export_job);
    
    $this->session->set_flashdata('info', 'Export has been queued. You will be notified when complete.');
    redirect('exports/queue-status/' . $job_id);
}
```

## Security Guidelines

### 1. Input Validation

```php
private function _validate_export_request()
{
    $this->load->library('form_validation');
    
    $this->form_validation->set_rules('template', 'Template', 'required|in_list[standard,detailed,summary,complete]');
    $this->form_validation->set_rules('format', 'Format', 'required|in_list[excel,csv]');
    $this->form_validation->set_rules('filters', 'Filters', 'valid_json');
    
    if (!$this->form_validation->run()) {
        return array(
            'valid' => false,
            'errors' => validation_errors()
        );
    }
    
    return array('valid' => true);
}
```

### 2. Access Control

```php
// Add to your controller constructor or method
private function _check_export_permissions($export_type)
{
    $user_role = $this->session->userdata('user_role');
    $allowed_exports = $this->config->item('export_permissions')[$user_role] ?? array();
    
    if (!in_array($export_type, $allowed_exports)) {
        show_error('Access denied. You do not have permission to export ' . $export_type . ' data.', 403);
    }
}
```

### 3. Rate Limiting

```php
private function _check_rate_limit()
{
    $user_id = $this->session->userdata('user_id');
    $cache_key = "export_rate_limit_{$user_id}";
    
    $current_requests = $this->cache->get($cache_key) ?: 0;
    
    if ($current_requests >= 10) { // 10 exports per hour
        show_error('Rate limit exceeded. Please try again later.', 429);
    }
    
    $this->cache->save($cache_key, $current_requests + 1, 3600); // 1 hour
}
```

## Production Deployment

### 1. Environment Setup

```bash
# Production environment variables
YBB_EXPORT_API_URL=https://api.ybb-exports.your-domain.com
YBB_EXPORT_API_TIMEOUT=600
YBB_EXPORT_MAX_RECORDS=100000
```

### 2. Nginx Configuration

```nginx
# Proxy configuration for YBB Export API
location /api/ybb/ {
    proxy_pass http://ybb-export-service:5000;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
    
    # Increase timeouts for large exports
    proxy_connect_timeout 60s;
    proxy_send_timeout 600s;
    proxy_read_timeout 600s;
    
    # Increase max body size for large datasets
    client_max_body_size 500M;
}
```

### 3. Monitoring and Logging

```php
// Add to your main export controller
public function __construct()
{
    parent::__construct();
    
    // Log all export activities
    $this->load->library('user_agent');
    
    log_message('info', sprintf(
        'Export request from User ID: %s, IP: %s, User Agent: %s',
        $this->session->userdata('user_id') ?: 'anonymous',
        $this->input->ip_address(),
        $this->agent->agent_string()
    ));
}
```

### 4. Health Monitoring

```php
// Create a cron job to monitor API health
public function monitor_api_health()
{
    $this->load->library('ybb_export');
    
    $health_check = $this->ybb_export->test_connection();
    
    if (!$health_check['success']) {
        // Send alert to administrators
        $this->load->library('email');
        
        $this->email->to('admin@your-domain.com');
        $this->email->subject('YBB Export API Health Alert');
        $this->email->message('The YBB Export API service is not responding. Please check the service status.');
        $this->email->send();
        
        log_message('error', 'YBB Export API health check failed');
    }
}
```

## Troubleshooting

### Common Issues and Solutions

1. **Connection Timeout**
   - Increase timeout values in configuration
   - Check network connectivity to API service
   - Verify API service is running

2. **Large File Download Failures**
   - Increase PHP memory limit and execution time
   - Use chunked downloading for very large files
   - Implement resume capability for interrupted downloads

3. **Memory Issues**
   - Process data in smaller batches
   - Use streaming for large datasets
   - Monitor memory usage and implement limits

4. **API Rate Limiting**
   - Implement client-side rate limiting
   - Use queuing for bulk operations
   - Add retry logic with exponential backoff

---

*This documentation covers the complete integration of the YBB Export API with CodeIgniter for production use. For additional support, please refer to the API service logs and error messages.*
