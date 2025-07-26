<?php
/**
 * CodeIgniter Integration Examples
 * Demonstrates how to send enhanced requests to Python Flask export service
 */

class Export_Examples {
    
    /**
     * Example 1: Participants Export with Custom Filename
     */
    public function participants_export_example() {
        // Sample participant data (this would come from your database)
        $participants = [
            [
                'id' => 1,
                'name' => 'Alice Johnson',
                'email' => 'alice@summit2025.com',
                'phone' => '+1-555-0101',
                'program_id' => 101,
                'form_status' => 'approved',
                'birthdate' => '1999-03-15',
                'created_at' => '2025-07-26 09:30:00',
                'updated_at' => '2025-07-26 10:15:00'
            ],
            [
                'id' => 2,
                'name' => 'Bob Chen',
                'email' => 'bob@summit2025.com',
                'phone' => '+1-555-0102',
                'program_id' => 101,
                'form_status' => 'pending',
                'birthdate' => '1998-11-22',
                'created_at' => '2025-07-26 10:00:00',
                'updated_at' => '2025-07-26 10:30:00'
            ]
        ];
        
        // Enhanced payload with filename customization
        $payload = [
            'data' => $participants,
            'template' => 'standard',
            'format' => 'excel',
            'filename' => 'Japan_Youth_Summit_2025_Participants_Complete_Registration_Data_26-07-2025.xlsx',
            'sheet_name' => 'Participants Data Jul 2025',
            'filters' => [
                'program_id' => 101,
                'status' => 'all',
                'date_from' => '2025-07-01',
                'date_to' => '2025-07-26'
            ],
            'options' => [
                'include_related' => true,
                'batch_size' => 5000,
                'sort_by' => 'created_at',
                'sort_order' => 'desc'
            ]
        ];
        
        // Send to Python API
        $response = $this->send_to_python_api('/api/ybb/export/participants', $payload);
        
        return $response;
    }
    
    /**
     * Example 2: Payments Export with Custom Filename
     */
    public function payments_export_example() {
        $payments = [
            [
                'id' => 1,
                'participant_id' => 1,
                'amount' => 250.00,
                'usd_amount' => 250.00,
                'payment_method_id' => 1,
                'status' => 'success',
                'payment_date' => '2025-07-25',
                'created_at' => '2025-07-25 14:30:00'
            ],
            [
                'id' => 2,
                'participant_id' => 2,
                'amount' => 250.00,
                'usd_amount' => 250.00,
                'payment_method_id' => 2,
                'status' => 'pending',
                'payment_date' => '2025-07-26',
                'created_at' => '2025-07-26 09:15:00'
            ]
        ];
        
        $payload = [
            'data' => $payments,
            'template' => 'standard',
            'format' => 'excel',
            'filename' => 'Japan_Youth_Summit_2025_Payments_Complete_Transaction_Report_26-07-2025.xlsx',
            'sheet_name' => 'Payment Records Jul 2025',
            'filters' => [
                'status' => 'success',
                'currency' => 'USD'
            ]
        ];
        
        $response = $this->send_to_python_api('/api/ybb/export/payments', $payload);
        
        return $response;
    }
    
    /**
     * Example 3: Large Dataset Export (will trigger multi-file)
     */
    public function large_export_example() {
        // Simulate large dataset (6000+ records)
        $large_dataset = [];
        for ($i = 1; $i <= 6000; $i++) {
            $large_dataset[] = [
                'id' => $i,
                'name' => "Participant {$i}",
                'email' => "participant{$i}@summit2025.com",
                'phone' => "+1-555-" . str_pad($i, 4, '0', STR_PAD_LEFT),
                'program_id' => 101,
                'form_status' => ($i % 3 == 0) ? 'approved' : 'pending',
                'created_at' => '2025-07-' . str_pad(($i % 26) + 1, 2, '0', STR_PAD_LEFT) . ' 10:30:00'
            ];
        }
        
        $payload = [
            'data' => $large_dataset,
            'template' => 'detailed',
            'format' => 'excel',
            'filename' => 'Japan_Youth_Summit_2025_Large_Participants_Dataset_26-07-2025.xlsx',
            'sheet_name' => 'All Participants Jul 2025',
            'options' => [
                'batch_size' => 2000  // Force chunking into multiple files
            ]
        ];
        
        $response = $this->send_to_python_api('/api/ybb/export/participants', $payload);
        
        return $response;
    }
    
    /**
     * Example 4: Legacy Export (backward compatibility)
     */
    public function legacy_export_example() {
        $participants = [
            [
                'id' => 99,
                'name' => 'Legacy User',
                'email' => 'legacy@example.com',
                'form_status' => 'approved',
                'created_at' => '2025-07-26 12:00:00'
            ]
        ];
        
        // Old payload format (no filename/sheet_name) - should still work
        $payload = [
            'data' => $participants,
            'template' => 'standard',
            'format' => 'excel'
            // No filename or sheet_name - API will auto-generate
        ];
        
        $response = $this->send_to_python_api('/api/ybb/export/participants', $payload);
        
        return $response;
    }
    
    /**
     * Send request to Python API
     */
    private function send_to_python_api($endpoint, $payload) {
        $api_url = 'http://localhost:5000' . $endpoint;
        
        $ch = curl_init();
        curl_setopt_array($ch, [
            CURLOPT_URL => $api_url,
            CURLOPT_POST => true,
            CURLOPT_POSTFIELDS => json_encode($payload),
            CURLOPT_RETURNTRANSFER => true,
            CURLOPT_TIMEOUT => 300, // 5 minute timeout
            CURLOPT_HTTPHEADER => [
                'Content-Type: application/json',
                'Accept: application/json'
            ]
        ]);
        
        $response = curl_exec($ch);
        $http_code = curl_getinfo($ch, CURLINFO_HTTP_CODE);
        $error = curl_error($ch);
        curl_close($ch);
        
        if ($error) {
            return [
                'status' => 'error',
                'message' => "cURL Error: {$error}"
            ];
        }
        
        $decoded_response = json_decode($response, true);
        
        if (json_last_error() !== JSON_ERROR_NONE) {
            return [
                'status' => 'error',
                'message' => 'Invalid JSON response from API'
            ];
        }
        
        return $decoded_response;
    }
    
    /**
     * Handle different types of responses
     */
    public function handle_export_response($response) {
        if ($response['status'] === 'success') {
            
            // Check if it's a multi-file export
            if (isset($response['export_strategy']) && $response['export_strategy'] === 'multi_file') {
                return $this->handle_multi_file_response($response);
            } else {
                return $this->handle_single_file_response($response);
            }
            
        } else {
            return $this->handle_error_response($response);
        }
    }
    
    /**
     * Handle single file export response
     */
    private function handle_single_file_response($response) {
        $data = $response['data'];
        $metadata = $response['metadata'] ?? [];
        
        return [
            'type' => 'single_file',
            'message' => 'Export completed successfully',
            'export_id' => $data['export_id'],
            'filename' => $data['file_name'],
            'download_url' => $data['download_url'],
            'file_size' => $this->format_file_size($data['file_size']),
            'record_count' => number_format($data['record_count']),
            'processing_time' => $metadata['processing_time'] ?? null,
            'expires_at' => $data['expires_at'] ?? null
        ];
    }
    
    /**
     * Handle multi-file export response
     */
    private function handle_multi_file_response($response) {
        $data = $response['data'];
        
        return [
            'type' => 'multi_file',
            'message' => 'Large export completed - multiple files generated',
            'export_id' => $data['export_id'],
            'total_records' => number_format($data['total_records']),
            'total_files' => $data['total_files'],
            'individual_files' => array_map(function($file) {
                return [
                    'batch_number' => $file['batch_number'],
                    'filename' => $file['file_name'],
                    'download_url' => str_replace('/api/ybb/', '/export/', $file['file_url']), // Convert to CodeIgniter URL
                    'file_size' => $this->format_file_size($file['file_size']),
                    'record_count' => number_format($file['record_count']),
                    'record_range' => $file['record_range']
                ];
            }, $data['individual_files']),
            'zip_archive' => [
                'filename' => $data['archive']['zip_file_name'],
                'download_url' => str_replace('/api/ybb/', '/export/', $data['archive']['zip_file_url']),
                'file_size' => $this->format_file_size($data['archive']['zip_file_size']),
                'compression_ratio' => $data['archive']['compression_ratio'] . '%'
            ]
        ];
    }
    
    /**
     * Handle error response
     */
    private function handle_error_response($response) {
        return [
            'type' => 'error',
            'message' => $response['message'] ?? 'Export failed',
            'request_id' => $response['request_id'] ?? null
        ];
    }
    
    /**
     * Format file size for display
     */
    private function format_file_size($bytes) {
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
}

// Usage examples in your controller:
/*

class Admin_Export extends CI_Controller {
    
    public function participants($program_id) {
        $examples = new Export_Examples();
        
        // Use the enhanced export method
        $response = $examples->participants_export_example();
        
        // Handle the response
        $result = $examples->handle_export_response($response);
        
        if ($result['type'] === 'single_file') {
            // Show single file download
            $this->session->set_flashdata('success', 
                "Export completed: {$result['filename']} ({$result['record_count']} records)"
            );
            redirect("admin/download/{$result['export_id']}");
            
        } elseif ($result['type'] === 'multi_file') {
            // Show multi-file options
            $this->load->view('admin/exports/multi_file_result', ['result' => $result]);
            
        } else {
            // Show error
            $this->session->set_flashdata('error', $result['message']);
            redirect('admin/exports');
        }
    }
}

*/

/**
 * Expected Response Examples
 */

// Single File Response:
$single_file_response = [
    'status' => 'success',
    'message' => 'Export completed successfully',
    'data' => [
        'export_id' => 'ae86c75b-4301-47a1-8128-ced78adc665c',
        'file_name' => 'Japan_Youth_Summit_2025_Participants_Complete_Registration_Data_26-07-2025.xlsx',
        'file_url' => '/api/ybb/export/ae86c75b-4301-47a1-8128-ced78adc665c/download',
        'file_size' => 5316,
        'record_count' => 2,
        'expires_at' => '2025-07-27T10:30:00Z'
    ],
    'metadata' => [
        'export_type' => 'participants',
        'template' => 'standard',
        'processing_time' => 2.5,
        'generated_at' => '2025-07-26T10:30:00Z'
    ]
];

// Multi-File Response:
$multi_file_response = [
    'status' => 'success',
    'message' => 'Large export completed successfully',
    'export_strategy' => 'multi_file',
    'data' => [
        'export_id' => 'large-export-123',
        'total_records' => 6000,
        'total_files' => 3,
        'individual_files' => [
            [
                'batch_number' => 1,
                'file_name' => 'Japan_Youth_Summit_2025_Large_Participants_Dataset_26-07-2025_batch_1_of_3.xlsx',
                'file_url' => '/api/ybb/export/large-export-123/download/batch/1',
                'file_size' => 2048576,
                'record_count' => 2000,
                'record_range' => '1-2000'
            ]
            // ... more batch files
        ],
        'archive' => [
            'zip_file_name' => 'Japan_Youth_Summit_2025_Large_Participants_Dataset_26-07-2025_complete_export.zip',
            'zip_file_url' => '/api/ybb/export/large-export-123/download/zip',
            'zip_file_size' => 5242880,
            'compression_ratio' => '75.0'
        ]
    ]
];

// Error Response:
$error_response = [
    'status' => 'error',
    'message' => 'Filename contains potentially dangerous pattern: ../',
    'request_id' => 'req-123456789'
];

?>
