<?php
/**
 * CodeIgniter Download Handler for YBB Export Service
 * Use this after receiving a successful status response
 */

class ExportDownloadHandler extends CI_Controller 
{
    public function download_export($export_id) 
    {
        // Load the YBB Export library
        $this->load->library('ybb_export');
        
        try {
            // Check status one more time to ensure it's ready
            $status = $this->ybb_export->get_export_status($export_id);
            
            if (!$status['success'] || $status['data']['status'] !== 'success') {
                show_error('Export not ready for download', 400);
                return;
            }
            
            // Get export details
            $export_data = $status['data'];
            $file_size = $export_data['file_size'];
            $record_count = $export_data['record_count'];
            $export_type = $export_data['export_type'];
            
            // Download the file
            $download_result = $this->ybb_export->download_export($export_id);
            
            if (!$download_result['success']) {
                show_error('Failed to download export: ' . $download_result['message'], 500);
                return;
            }
            
            // Get the file content and suggested filename
            $file_content = $download_result['data']['content'];
            $suggested_filename = $download_result['data']['filename'];
            
            // Determine content type based on file extension
            $file_extension = pathinfo($suggested_filename, PATHINFO_EXTENSION);
            $content_type = $this->get_content_type($file_extension);
            
            // Set headers for file download
            $this->output
                ->set_content_type($content_type)
                ->set_header('Content-Disposition: attachment; filename="' . $suggested_filename . '"')
                ->set_header('Content-Length: ' . strlen($file_content))
                ->set_header('Cache-Control: no-cache, must-revalidate')
                ->set_header('Expires: 0')
                ->set_output($file_content);
                
            // Log successful download
            log_message('info', "Export downloaded successfully: ID={$export_id}, filename={$suggested_filename}, size=" . strlen($file_content));
            
        } catch (Exception $e) {
            log_message('error', 'Export download failed: ' . $e->getMessage());
            show_error('Download failed: ' . $e->getMessage(), 500);
        }
    }
    
    /**
     * AJAX endpoint for download with progress tracking
     */
    public function ajax_download($export_id) 
    {
        $this->load->library('ybb_export');
        
        try {
            // Check status
            $status = $this->ybb_export->get_export_status($export_id);
            
            if (!$status['success'] || $status['data']['status'] !== 'success') {
                $this->output
                    ->set_content_type('application/json')
                    ->set_output(json_encode([
                        'success' => false,
                        'message' => 'Export not ready'
                    ]));
                return;
            }
            
            // Get download URL instead of content for large files
            $api_url = $this->ybb_export->get_api_url();
            $download_url = $api_url . "/api/ybb/export/{$export_id}/download";
            
            $this->output
                ->set_content_type('application/json')
                ->set_output(json_encode([
                    'success' => true,
                    'download_url' => $download_url,
                    'filename' => $status['data']['suggested_filename'] ?? "export_{$export_id}.xlsx",
                    'file_size' => $status['data']['file_size'],
                    'record_count' => $status['data']['record_count']
                ]));
                
        } catch (Exception $e) {
            $this->output
                ->set_content_type('application/json')
                ->set_output(json_encode([
                    'success' => false,
                    'message' => $e->getMessage()
                ]));
        }
    }
    
    private function get_content_type($extension) 
    {
        $mime_types = [
            'xlsx' => 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            'xls' => 'application/vnd.ms-excel',
            'csv' => 'text/csv',
            'pdf' => 'application/pdf'
        ];
        
        return $mime_types[strtolower($extension)] ?? 'application/octet-stream';
    }
}

/**
 * JavaScript frontend code for handling the download
 */
?>

<script>
// After successful status check, trigger download
function handleSuccessfulExport(exportId, exportData) {
    // Show download button or auto-download
    showDownloadOption(exportId, exportData);
}

function showDownloadOption(exportId, exportData) {
    const downloadBtn = document.getElementById('download-btn');
    const statusDiv = document.getElementById('export-status');
    
    // Update UI
    statusDiv.innerHTML = `
        <div class="alert alert-success">
            <h5>✅ Export Ready!</h5>
            <p><strong>Records:</strong> ${exportData.record_count.toLocaleString()}</p>
            <p><strong>File Size:</strong> ${formatFileSize(exportData.file_size)}</p>
            <p><strong>Created:</strong> ${formatDate(exportData.created_at)}</p>
        </div>
    `;
    
    // Enable download button
    downloadBtn.disabled = false;
    downloadBtn.innerHTML = '⬇️ Download Export';
    downloadBtn.onclick = () => downloadExport(exportId);
}

function downloadExport(exportId) {
    // Option 1: Direct download via window.open
    const downloadUrl = `<?= base_url('exports/download/') ?>${exportId}`;
    window.open(downloadUrl, '_blank');
    
    // Option 2: AJAX download with progress (for large files)
    // downloadWithProgress(exportId);
}

function downloadWithProgress(exportId) {
    fetch(`<?= base_url('exports/ajax_download/') ?>${exportId}`)
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Create invisible download link
                const link = document.createElement('a');
                link.href = data.download_url;
                link.download = data.filename;
                link.style.display = 'none';
                document.body.appendChild(link);
                link.click();
                document.body.removeChild(link);
                
                // Show success message
                showMessage('success', `Download started: ${data.filename}`);
            } else {
                showMessage('error', 'Download failed: ' + data.message);
            }
        })
        .catch(error => {
            showMessage('error', 'Download error: ' + error.message);
        });
}

function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

function formatDate(dateString) {
    return new Date(dateString).toLocaleString();
}

function showMessage(type, message) {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type === 'success' ? 'success' : 'danger'}`;
    alertDiv.textContent = message;
    document.getElementById('messages').appendChild(alertDiv);
    
    // Auto-remove after 5 seconds
    setTimeout(() => alertDiv.remove(), 5000);
}
</script>
