"""
Frontend Integration Examples - Database-Direct Export API
Shows how to use the new high-performance database endpoints
"""

# ============================================================================
# PHP/CodeIgniter Integration Examples
# ============================================================================

class Export_controller extends CI_Controller {
    
    private $python_api_base = 'http://python-service:5000/api/ybb/db';
    
    /**
     * NEW: Database-Direct Export (Recommended for Large Datasets)
     * Replaces sending 44k records via JSON with small parameter payload
     */
    public function export_participants_optimized() {
        // Instead of loading 44k records into memory and sending as JSON...
        // Just send query parameters!
        
        $export_request = [
            'template' => 'complete',           // Template determines chunking behavior
            'filters' => [
                'program_id' => 123,           // Filter by program
                'form_status' => ['completed', 'approved'],  // Multiple statuses
                'payment_status' => 'paid',     // Only paid participants
                'created_at' => [
                    'min' => '2024-01-01',     // Date range filtering
                    'max' => '2024-12-31'
                ],
                'is_active' => 1               // Only active records
            ],
            'filename' => 'participants_2024_export',
            'chunk_size' => 4000,             // Optimal chunk size for 44k records
            'force_chunking' => true          // Force chunking regardless of template
        ];
        
        // Small payload (~1KB vs 50-100MB with old method)
        $response = $this->http_client->post(
            $this->python_api_base . '/export/participants',
            [
                'headers' => ['Content-Type' => 'application/json'],
                'json' => $export_request,
                'timeout' => 60  // Much faster response now
            ]
        );
        
        $result = json_decode($response->getBody(), true);
        
        if ($result['status'] === 'success') {
            // Log performance improvement
            log_message('info', sprintf(
                'DB-Direct Export: %d records in %.2f seconds (%.0f rec/s)',
                $result['data']['total_records'] ?? $result['data']['record_count'],
                $result['performance_metrics']['total_processing_time_seconds'],
                $result['performance_metrics']['total_records_per_second'] ?? $result['performance_metrics']['records_per_second']
            ));
            
            // Handle response based on export strategy
            if ($result['export_strategy'] === 'multi_file') {
                $this->handle_chunked_export($result);
            } else {
                $this->handle_single_export($result);
            }
        }
    }
    
    /**
     * Preview export before processing (NEW)
     * Shows first 100 records to validate filters
     */
    public function preview_export() {
        $filters = $this->input->post('filters') ?: [];
        
        $preview_request = [
            'export_type' => 'participants',
            'template' => 'standard',
            'filters' => $filters
        ];
        
        $response = $this->http_client->post(
            $this->python_api_base . '/export/preview',
            ['json' => $preview_request]
        );
        
        $result = json_decode($response->getBody(), true);
        
        if ($result['status'] === 'success') {
            // Show preview to user before full export
            $this->output
                ->set_content_type('application/json')
                ->set_output(json_encode([
                    'preview_data' => array_slice($result['preview_data'], 0, 10), // First 10 records
                    'total_preview_count' => count($result['preview_data']),
                    'message' => 'Preview of export data (showing first 10 of 100 records)'
                ]));
        }
    }
    
    /**
     * Get export record count (NEW)
     * Fast count without processing data
     */
    public function get_export_count() {
        $count_request = [
            'export_type' => 'participants',
            'filters' => $this->input->post('filters') ?: []
        ];
        
        $response = $this->http_client->post(
            $this->python_api_base . '/export/count',
            ['json' => $count_request]
        );
        
        $result = json_decode($response->getBody(), true);
        
        if ($result['status'] === 'success') {
            $this->output
                ->set_content_type('application/json')
                ->set_output(json_encode([
                    'total_records' => $result['total_records'],
                    'estimates' => $result['estimates'],
                    'message' => "Found {$result['total_records']} records matching filters"
                ]));
        }
    }
    
    /**
     * Handle chunked export response
     */
    private function handle_chunked_export($result) {
        // Multiple files in ZIP
        $export_info = [
            'export_id' => $result['data']['export_id'],
            'type' => 'chunked',
            'total_files' => $result['data']['total_files'],
            'total_records' => $result['data']['total_records'],
            'compressed_size_mb' => round($result['data']['archive_info']['compressed_size'] / 1024 / 1024, 2),
            'compression_ratio' => $result['data']['archive_info']['compression_ratio'],
            'processing_time' => $result['performance_metrics']['total_processing_time_seconds'],
            'download_url' => base_url() . 'exports/download/' . $result['data']['export_id']
        ];
        
        // Store in session or database for user
        $this->session->set_userdata('last_export', $export_info);
        
        // Return success response
        $this->output
            ->set_content_type('application/json')
            ->set_output(json_encode([
                'status' => 'success',
                'export_info' => $export_info,
                'message' => "Export completed: {$export_info['total_records']} records in {$export_info['total_files']} files"
            ]));
    }
    
    /**
     * Handle single file export response  
     */
    private function handle_single_export($result) {
        // Single Excel file
        $export_info = [
            'export_id' => $result['data']['export_id'],
            'type' => 'single',
            'filename' => $result['data']['file_name'],
            'file_size_mb' => $result['data']['file_size_mb'],
            'record_count' => $result['data']['record_count'],
            'processing_time' => $result['performance_metrics']['total_processing_time_seconds'],
            'download_url' => base_url() . 'exports/download/' . $result['data']['export_id']
        ];
        
        $this->session->set_userdata('last_export', $export_info);
        
        $this->output
            ->set_content_type('application/json')  
            ->set_output(json_encode([
                'status' => 'success',
                'export_info' => $export_info,
                'message' => "Export completed: {$export_info['record_count']} records in single file"
            ]));
    }
}

# ============================================================================
# JavaScript/Frontend Integration Examples
# ============================================================================

/**
 * Database-Direct Export Class for Frontend
 */
class DatabaseExportAPI {
    constructor(baseURL) {
        this.baseURL = baseURL + '/api/ybb/db';
    }
    
    /**
     * NEW: Export large datasets efficiently
     */
    async exportParticipants(filters = {}, options = {}) {
        try {
            // Show loading with estimated time
            const countResponse = await this.getExportCount('participants', filters);
            const estimatedTime = countResponse.estimates?.estimated_processing_time_seconds || 30;
            
            this.showProgressModal(`Exporting ${countResponse.total_records} records (Est. ${estimatedTime}s)`);
            
            const exportRequest = {
                template: options.template || 'complete',
                filters: filters,
                filename: options.filename || 'participants_export',
                chunk_size: options.chunk_size || 4000,
                force_chunking: options.force_chunking || true
            };
            
            const response = await fetch(`${this.baseURL}/export/participants`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(exportRequest)
            });
            
            const result = await response.json();
            
            if (result.status === 'success') {
                this.handleExportSuccess(result);
            } else {
                this.handleExportError(result.message);
            }
            
        } catch (error) {
            this.handleExportError(`Export failed: ${error.message}`);
        }
    }
    
    /**
     * Get record count before export
     */
    async getExportCount(exportType, filters = {}) {
        const response = await fetch(`${this.baseURL}/export/count`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                export_type: exportType,
                filters: filters
            })
        });
        
        return await response.json();
    }
    
    /**
     * Preview export data
     */
    async previewExport(exportType, template, filters = {}) {
        const response = await fetch(`${this.baseURL}/export/preview`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                export_type: exportType,
                template: template,
                filters: filters
            })
        });
        
        return await response.json();
    }
    
    /**
     * Handle successful export
     */
    handleExportSuccess(result) {
        this.hideProgressModal();
        
        const data = result.data;
        const metrics = result.performance_metrics;
        
        if (result.export_strategy === 'multi_file') {
            // Chunked export - multiple files in ZIP
            this.showSuccessMessage(
                `Export completed successfully!
                
                📊 ${data.total_records} records processed in ${data.total_files} files
                ⏱️ Processing time: ${metrics.total_processing_time_seconds}s
                🗜️ Compression: ${data.archive_info.compression_ratio} (${(data.archive_info.compressed_size/1024/1024).toFixed(1)} MB)
                🚀 Speed: ${Math.round(metrics.total_records_per_second)} records/second
                
                Your ZIP file is ready for download.`
            );
        } else {
            // Single file export
            this.showSuccessMessage(
                `Export completed successfully!
                
                📊 ${data.record_count} records processed  
                ⏱️ Processing time: ${metrics.total_processing_time_seconds}s
                📄 File size: ${data.file_size_mb} MB
                🚀 Speed: ${Math.round(metrics.records_per_second)} records/second
                
                Your Excel file is ready for download.`
            );
        }
        
        // Auto-download after 2 seconds
        setTimeout(() => {
            window.location.href = result.download_url || `/api/ybb/export/${data.export_id}/download`;
        }, 2000);
    }
    
    /**
     * Smart export with automatic optimization
     */
    async smartExport(exportType, filters = {}) {
        try {
            // Step 1: Get count and estimates
            const countData = await this.getExportCount(exportType, filters);
            const totalRecords = countData.total_records;
            
            if (totalRecords === 0) {
                alert('No records found matching your filters.');
                return;
            }
            
            // Step 2: Show preview if dataset is large
            if (totalRecords > 10000) {
                const previewData = await this.previewExport(exportType, 'standard', filters);
                
                const confirm = await this.showPreviewConfirmation(
                    `Found ${totalRecords} records. Preview of first 10 records:`,
                    previewData.preview_data.slice(0, 10),
                    countData.estimates
                );
                
                if (!confirm) return;
            }
            
            // Step 3: Choose optimal settings based on size
            const optimizedOptions = {
                template: totalRecords > 20000 ? 'complete' : 'standard',
                chunk_size: totalRecords > 50000 ? 3000 : 4000,
                force_chunking: totalRecords > 15000,
                filename: `${exportType}_${new Date().toISOString().split('T')[0]}_export`
            };
            
            // Step 4: Execute optimized export
            await this.exportParticipants(filters, optimizedOptions);
            
        } catch (error) {
            this.handleExportError(error.message);
        }
    }
    
    // UI Helper Methods
    showProgressModal(message) {
        // Implementation depends on your UI framework
        console.log('Progress:', message);
    }
    
    hideProgressModal() {
        console.log('Progress complete');
    }
    
    showSuccessMessage(message) {
        alert(message); // Replace with proper modal/toast
    }
    
    handleExportError(message) {
        console.error('Export error:', message);
        alert(`Export failed: ${message}`);
    }
    
    async showPreviewConfirmation(title, previewData, estimates) {
        // Show preview data in modal and get user confirmation
        return confirm(`${title}
        
Estimated processing time: ${estimates.estimated_processing_time_seconds}s
Estimated file size: ${estimates.estimated_file_size_mb} MB

Continue with export?`);
    }
}

# ============================================================================
# Usage Examples
# ============================================================================

// Initialize API
const exportAPI = new DatabaseExportAPI('http://localhost:5000');

// Example 1: Simple optimized export
async function exportAllParticipants() {
    await exportAPI.smartExport('participants', {
        program_id: 123,
        form_status: ['completed', 'approved']
    });
}

// Example 2: Large dataset with custom settings
async function exportLargeDataset() {
    const filters = {
        created_at: {
            min: '2024-01-01',
            max: '2024-12-31'
        },
        payment_status: 'paid'
    };
    
    const options = {
        template: 'complete',
        chunk_size: 4000,
        force_chunking: true,
        filename: 'all_paid_participants_2024'
    };
    
    await exportAPI.exportParticipants(filters, options);
}

// Example 3: Preview before export
async function previewThenExport() {
    const filters = { program_id: 123 };
    
    // Get count
    const countData = await exportAPI.getExportCount('participants', filters);
    console.log(`Found ${countData.total_records} records`);
    
    // Show preview
    const previewData = await exportAPI.previewExport('participants', 'standard', filters);
    console.log('Preview:', previewData.preview_data.slice(0, 5));
    
    // Export if user confirms
    if (confirm(`Export ${countData.total_records} records?`)) {
        await exportAPI.exportParticipants(filters);
    }
}