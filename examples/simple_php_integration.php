<?php
/**
 * Simple PHP Integration for YBB Data Processing Service
 * Focused on data transformation and Excel export
 */

class YBBDataProcessor {
    private $apiBaseUrl;
    private $timeout;
    
    public function __construct($baseUrl = 'http://localhost:5000', $timeout = 300) {
        $this->apiBaseUrl = rtrim($baseUrl, '/');
        $this->timeout = $timeout;
    }
    
    /**
     * Check if the service is running
     */
    public function isServiceRunning() {
        try {
            $response = $this->makeGetRequest('/health');
            $data = json_decode($response, true);
            return isset($data['status']) && $data['status'] === 'healthy';
        } catch (Exception $e) {
            return false;
        }
    }
    
    /**
     * Convert array data to Excel file
     */
    public function arrayToExcel($data, $filename = null, $options = []) {
        if (empty($data)) {
            throw new Exception('No data provided for Excel export');
        }
        
        $payload = [
            'data' => $data,
            'filename' => $filename ?: 'export_' . date('Y-m-d_H-i-s') . '.xlsx',
            'sheet_name' => $options['sheet_name'] ?? 'Data',
            'format_options' => $options['format_options'] ?? [
                'auto_width' => true,
                'header_style' => [
                    'bold' => true,
                    'font_color' => 'FFFFFF',
                    'bg_color' => '366092'
                ]
            ]
        ];
        
        return $this->makePostRequest('/api/export/excel', $payload);
    }
    
    /**
     * Convert large array data to Excel using chunked processing
     */
    public function largeArrayToExcel($data, $filename = null, $chunkSize = 1000) {
        $totalRecords = count($data);
        
        // Use regular export for small datasets
        if ($totalRecords <= 5000) {
            return $this->arrayToExcel($data, $filename);
        }
        
        // Use chunked processing for large datasets
        $chunks = array_chunk($data, $chunkSize);
        $totalChunks = count($chunks);
        $sessionId = uniqid('export_');
        
        foreach ($chunks as $index => $chunk) {
            $isLastChunk = ($index === $totalChunks - 1);
            
            $payload = [
                'session_id' => $sessionId,
                'chunk_data' => $chunk,
                'chunk_index' => $index,
                'total_chunks' => $totalChunks,
                'filename' => $filename ?: 'large_export_' . date('Y-m-d_H-i-s') . '.xlsx',
                'sheet_name' => 'Data'
            ];
            
            $response = $this->makePostRequest('/api/export/excel/chunked', $payload);
            
            if ($isLastChunk) {
                return $response; // Excel file binary data
            }
            // Continue with next chunk
        }
        
        throw new Exception('Failed to complete chunked export');
    }
    
    /**
     * Process and filter data
     */
    public function processData($data, $operations = []) {
        $payload = [
            'data' => $data,
            'operations' => $operations
        ];
        
        $response = $this->makePostRequest('/api/data/process', $payload);
        return json_decode($response, true);
    }
    
    /**
     * Process large datasets with chunked operations
     */
    public function processLargeData($data, $operations = [], $chunkSize = 1000) {
        $totalRecords = count($data);
        
        // Use regular processing for small datasets
        if ($totalRecords <= 5000) {
            return $this->processData($data, $operations);
        }
        
        // Use chunked processing
        $chunks = array_chunk($data, $chunkSize);
        $totalChunks = count($chunks);
        $sessionId = uniqid('process_');
        
        foreach ($chunks as $index => $chunk) {
            $isLastChunk = ($index === $totalChunks - 1);
            
            $payload = [
                'session_id' => $sessionId,
                'chunk_data' => $chunk,
                'chunk_index' => $index,
                'total_chunks' => $totalChunks,
                'operations' => $operations
            ];
            
            $response = $this->makePostRequest('/api/data/process/chunked', $payload);
            $result = json_decode($response, true);
            
            if ($isLastChunk) {
                return $result;
            }
        }
        
        throw new Exception('Failed to complete chunked processing');
    }
    
    /**
     * Validate data structure and get statistics
     */
    public function validateData($data) {
        $payload = ['data' => $data];
        $response = $this->makePostRequest('/api/data/validate', $payload);
        return json_decode($response, true);
    }
    
    /**
     * Upload CSV file and convert to Excel
     */
    public function csvToExcel($csvFilePath, $outputFilename = null) {
        if (!file_exists($csvFilePath)) {
            throw new Exception('CSV file not found: ' . $csvFilePath);
        }
        
        $url = $this->apiBaseUrl . '/api/upload/csv';
        
        $postData = [
            'file' => new CURLFile($csvFilePath, 'text/csv'),
            'format' => 'excel',
            'filename' => $outputFilename ?: 'converted_' . date('Y-m-d_H-i-s') . '.xlsx'
        ];
        
        $ch = curl_init();
        curl_setopt($ch, CURLOPT_URL, $url);
        curl_setopt($ch, CURLOPT_POST, true);
        curl_setopt($ch, CURLOPT_POSTFIELDS, $postData);
        curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
        curl_setopt($ch, CURLOPT_TIMEOUT, $this->timeout);
        
        $response = curl_exec($ch);
        $httpCode = curl_getinfo($ch, CURLINFO_HTTP_CODE);
        curl_close($ch);
        
        if ($httpCode !== 200) {
            throw new Exception('CSV upload failed with HTTP code: ' . $httpCode);
        }
        
        return $response;
    }
    
    /**
     * Download Excel file and save to disk
     */
    public function saveExcelFile($excelBinaryData, $filePath) {
        $bytesWritten = file_put_contents($filePath, $excelBinaryData);
        if ($bytesWritten === false) {
            throw new Exception('Failed to save Excel file to: ' . $filePath);
        }
        return $bytesWritten;
    }
    
    /**
     * Return Excel file for download in browser
     */
    public function downloadExcel($excelBinaryData, $filename = 'export.xlsx') {
        header('Content-Type: application/vnd.openxmlformats-officedocument.spreadsheetml.sheet');
        header('Content-Disposition: attachment; filename="' . $filename . '"');
        header('Content-Length: ' . strlen($excelBinaryData));
        echo $excelBinaryData;
        exit;
    }
    
    private function makePostRequest($endpoint, $data) {
        $url = $this->apiBaseUrl . $endpoint;
        
        $context = stream_context_create([
            'http' => [
                'method' => 'POST',
                'header' => 'Content-Type: application/json',
                'content' => json_encode($data),
                'timeout' => $this->timeout
            ]
        ]);
        
        $response = file_get_contents($url, false, $context);
        
        if ($response === false) {
            throw new Exception("Failed to make request to {$endpoint}");
        }
        
        return $response;
    }
    
    private function makeGetRequest($endpoint) {
        $url = $this->apiBaseUrl . $endpoint;
        
        $context = stream_context_create([
            'http' => [
                'method' => 'GET',
                'timeout' => 30
            ]
        ]);
        
        $response = file_get_contents($url, false, $context);
        
        if ($response === false) {
            throw new Exception("Failed to make request to {$endpoint}");
        }
        
        return $response;
    }
}

// ==========================================
// USAGE EXAMPLES
// ==========================================

try {
    $processor = new YBBDataProcessor('http://localhost:5000');
    
    // Check if service is running
    if (!$processor->isServiceRunning()) {
        die("❌ Data processing service is not running!\n");
    }
    echo "✅ Data processing service is running\n\n";
    
    // Example 1: Simple array to Excel conversion
    echo "Example 1: Converting array data to Excel\n";
    $userData = [
        ['id' => 1, 'name' => 'John Doe', 'email' => 'john@example.com', 'salary' => 50000],
        ['id' => 2, 'name' => 'Jane Smith', 'email' => 'jane@example.com', 'salary' => 60000],
        ['id' => 3, 'name' => 'Bob Johnson', 'email' => 'bob@example.com', 'salary' => 55000]
    ];
    
    $excelData = $processor->arrayToExcel($userData, 'users_export.xlsx');
    $processor->saveExcelFile($excelData, 'downloads/users_export.xlsx');
    echo "✅ Excel file saved: downloads/users_export.xlsx\n\n";
    
    // Example 2: Data processing with filtering
    echo "Example 2: Processing data with filtering\n";
    $processedData = $processor->processData($userData, [
        ['type' => 'filter', 'column' => 'salary', 'value' => 55000], // This won't work as expected
        ['type' => 'sort', 'column' => 'salary', 'order' => 'desc']
    ]);
    
    echo "Processed " . $processedData['row_count'] . " records\n";
    print_r($processedData['data']);
    echo "\n";
    
    // Example 3: Large dataset processing (uncomment to test)
    /*
    echo "Example 3: Large dataset processing\n";
    $largeData = [];
    for ($i = 0; $i < 10000; $i++) {
        $largeData[] = [
            'id' => $i,
            'name' => 'User ' . $i,
            'value' => rand(1, 1000),
            'category' => ['A', 'B', 'C'][rand(0, 2)]
        ];
    }
    
    $excelData = $processor->largeArrayToExcel($largeData, 'large_export.xlsx');
    $processor->saveExcelFile($excelData, 'downloads/large_export.xlsx');
    echo "✅ Large Excel file saved: downloads/large_export.xlsx\n";
    */
    
    // Example 4: Data validation
    echo "Example 4: Data validation\n";
    $validation = $processor->validateData($userData);
    echo "Data has {$validation['row_count']} rows and {$validation['column_count']} columns\n";
    echo "Columns: " . implode(', ', $validation['columns']) . "\n";
    if (!empty($validation['recommendations'])) {
        echo "Recommendations:\n";
        foreach ($validation['recommendations'] as $rec) {
            echo "- {$rec}\n";
        }
    }
    
} catch (Exception $e) {
    echo "❌ Error: " . $e->getMessage() . "\n";
}

// ==========================================
// QUICK INTEGRATION FUNCTIONS
// ==========================================

/**
 * Quick function to convert any PHP array to Excel
 */
function quickArrayToExcel($data, $filename = null) {
    $processor = new YBBDataProcessor();
    $excelData = $processor->arrayToExcel($data, $filename);
    
    if ($filename) {
        file_put_contents($filename, $excelData);
        return $filename;
    } else {
        return $excelData;
    }
}

/**
 * Quick function to download Excel in browser
 */
function downloadArrayAsExcel($data, $filename = 'export.xlsx') {
    $processor = new YBBDataProcessor();
    $excelData = $processor->arrayToExcel($data, $filename);
    $processor->downloadExcel($excelData, $filename);
}

?>
