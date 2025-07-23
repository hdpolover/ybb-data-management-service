<?php
/**
 * Enhanced PHP Integration for Large Dataset Processing
 * Handles chunked processing for tens of thousands of records
 */

class YBBDataAPIAdvanced {
    private $apiBaseUrl;
    private $chunkSize;
    
    public function __construct($baseUrl = 'http://localhost:5000', $chunkSize = 1000) {
        $this->apiBaseUrl = rtrim($baseUrl, '/');
        $this->chunkSize = $chunkSize;
    }
    
    /**
     * Export large dataset to Excel using chunked processing
     */
    public function exportLargeDataset($data, $filename = null, $sheetName = 'Data', $formatOptions = []) {
        $totalRecords = count($data);
        
        // For small datasets, use regular export
        if ($totalRecords <= 5000) {
            return $this->exportToExcel($data, $filename, $sheetName, $formatOptions);
        }
        
        // For large datasets, use chunked processing
        $chunks = array_chunk($data, $this->chunkSize);
        $totalChunks = count($chunks);
        $sessionId = uniqid('excel_session_');
        
        echo "Processing {$totalRecords} records in {$totalChunks} chunks...\n";
        
        foreach ($chunks as $index => $chunk) {
            $isLastChunk = ($index === $totalChunks - 1);
            
            $payload = [
                'session_id' => $sessionId,
                'chunk_data' => $chunk,
                'chunk_index' => $index,
                'total_chunks' => $totalChunks,
                'filename' => $filename ?: 'large_export_' . date('Y-m-d_H-i-s') . '.xlsx',
                'sheet_name' => $sheetName,
                'format_options' => $formatOptions
            ];
            
            $response = $this->makeRequest('/api/export/excel/chunked', $payload);
            
            if ($isLastChunk) {
                // Last chunk returns the Excel file
                return $response;
            } else {
                // Intermediate chunks return status
                $result = json_decode($response, true);
                echo "Processed chunk {$index}/{$totalChunks}\n";
            }
        }
        
        throw new Exception('Failed to complete chunked export');
    }
    
    /**
     * Process large dataset in chunks
     */
    public function processLargeDataset($data, $operations = []) {
        $totalRecords = count($data);
        
        // For small datasets, use regular processing
        if ($totalRecords <= 5000) {
            return $this->processData($data, $operations);
        }
        
        // For large datasets, use chunked processing
        $chunks = array_chunk($data, $this->chunkSize);
        $totalChunks = count($chunks);
        $sessionId = uniqid('process_session_');
        
        echo "Processing {$totalRecords} records in {$totalChunks} chunks...\n";
        
        foreach ($chunks as $index => $chunk) {
            $isLastChunk = ($index === $totalChunks - 1);
            
            $payload = [
                'session_id' => $sessionId,
                'chunk_data' => $chunk,
                'chunk_index' => $index,
                'total_chunks' => $totalChunks,
                'operations' => $operations
            ];
            
            $response = $this->makeRequest('/api/data/process/chunked', $payload);
            $result = json_decode($response, true);
            
            if ($isLastChunk) {
                // Last chunk returns the processed data
                return $result;
            } else {
                echo "Processed chunk {$index}/{$totalChunks} - {$result['chunk_row_count']} rows\n";
            }
        }
        
        throw new Exception('Failed to complete chunked processing');
    }
    
    /**
     * Optimized data streaming from database
     */
    public function exportFromDatabase($query, $params = [], $filename = null, $batchSize = 1000) {
        // This method would work with your existing database
        // and stream data in batches to avoid memory issues
        
        $sessionId = uniqid('db_export_');
        $chunkIndex = 0;
        $allData = [];
        
        // Simulate database pagination (adjust for your actual DB setup)
        $offset = 0;
        $hasMore = true;
        
        while ($hasMore) {
            // Get batch from database
            $batchQuery = $query . " LIMIT {$batchSize} OFFSET {$offset}";
            $batchData = $this->executeDatabaseQuery($batchQuery, $params);
            
            if (empty($batchData)) {
                $hasMore = false;
                break;
            }
            
            $allData = array_merge($allData, $batchData);
            $offset += $batchSize;
            
            echo "Fetched batch: " . count($batchData) . " records\n";
        }
        
        // Now export using chunked processing
        return $this->exportLargeDataset($allData, $filename);
    }
    
    /**
     * Memory-efficient CSV to Excel conversion
     */
    public function csvToExcel($csvFilePath, $excelFilename = null) {
        if (!file_exists($csvFilePath)) {
            throw new Exception('CSV file not found');
        }
        
        $sessionId = uniqid('csv_convert_');
        $chunkIndex = 0;
        $handle = fopen($csvFilePath, 'r');
        
        if (!$handle) {
            throw new Exception('Cannot open CSV file');
        }
        
        // Read CSV headers
        $headers = fgetcsv($handle);
        $chunkData = [];
        $totalChunks = 0;
        
        // First pass: count total records and prepare chunks
        while (($row = fgetcsv($handle)) !== false) {
            $chunkData[] = array_combine($headers, $row);
            
            if (count($chunkData) >= $this->chunkSize) {
                $totalChunks++;
                $chunkData = []; // Reset for counting
            }
        }
        
        if (!empty($chunkData)) {
            $totalChunks++; // Last partial chunk
        }
        
        // Reset file pointer
        fseek($handle, 0);
        fgetcsv($handle); // Skip headers again
        
        $chunkData = [];
        $chunkIndex = 0;
        
        while (($row = fgetcsv($handle)) !== false) {
            $chunkData[] = array_combine($headers, $row);
            
            if (count($chunkData) >= $this->chunkSize) {
                $this->sendChunkToAPI($sessionId, $chunkData, $chunkIndex, $totalChunks, $excelFilename);
                $chunkData = [];
                $chunkIndex++;
            }
        }
        
        // Send last chunk if any
        if (!empty($chunkData)) {
            return $this->sendChunkToAPI($sessionId, $chunkData, $chunkIndex, $totalChunks, $excelFilename);
        }
        
        fclose($handle);
    }
    
    private function sendChunkToAPI($sessionId, $chunkData, $chunkIndex, $totalChunks, $filename) {
        $isLastChunk = ($chunkIndex === $totalChunks - 1);
        
        $payload = [
            'session_id' => $sessionId,
            'chunk_data' => $chunkData,
            'chunk_index' => $chunkIndex,
            'total_chunks' => $totalChunks,
            'filename' => $filename ?: 'csv_export_' . date('Y-m-d_H-i-s') . '.xlsx'
        ];
        
        $response = $this->makeRequest('/api/export/excel/chunked', $payload);
        
        if ($isLastChunk) {
            return $response; // Excel file
        } else {
            echo "Sent chunk {$chunkIndex}/{$totalChunks}\n";
            return null;
        }
    }
    
    private function makeRequest($endpoint, $data) {
        $url = $this->apiBaseUrl . $endpoint;
        
        $context = stream_context_create([
            'http' => [
                'method' => 'POST',
                'header' => [
                    'Content-Type: application/json',
                    'Connection: keep-alive'
                ],
                'content' => json_encode($data),
                'timeout' => 300 // 5 minutes for large operations
            ]
        ]);
        
        $result = file_get_contents($url, false, $context);
        
        if ($result === false) {
            throw new Exception("Failed to make request to {$endpoint}");
        }
        
        return $result;
    }
    
    // Legacy methods for backward compatibility
    public function exportToExcel($data, $filename = null, $sheetName = 'Data', $formatOptions = []) {
        $payload = [
            'data' => $data,
            'filename' => $filename ?: 'export_' . date('Y-m-d_H-i-s') . '.xlsx',
            'sheet_name' => $sheetName,
            'format_options' => $formatOptions
        ];
        
        return $this->makeRequest('/api/export/excel', $payload);
    }
    
    public function processData($data, $operations = []) {
        $payload = [
            'data' => $data,
            'operations' => $operations
        ];
        
        $result = $this->makeRequest('/api/data/process', $payload);
        return json_decode($result, true);
    }
    
    private function executeDatabaseQuery($query, $params) {
        // Implement your database query logic here
        // This is just a placeholder
        return [];
    }
}

// Usage Examples for Large Datasets
try {
    $api = new YBBDataAPIAdvanced('http://localhost:5000', 1000); // 1000 records per chunk
    
    // Example 1: Export 50,000 records efficiently
    /*
    $largeDataset = [];
    for ($i = 0; $i < 50000; $i++) {
        $largeDataset[] = [
            'id' => $i,
            'name' => 'User ' . $i,
            'email' => 'user' . $i . '@example.com',
            'status' => ($i % 2 === 0) ? 'active' : 'inactive'
        ];
    }
    
    echo "Starting export of 50,000 records...\n";
    $excelData = $api->exportLargeDataset($largeDataset, 'large_export.xlsx');
    file_put_contents('downloads/large_export.xlsx', $excelData);
    echo "Large export completed!\n";
    */
    
    // Example 2: Process large dataset with filtering
    /*
    $processedData = $api->processLargeDataset($largeDataset, [
        ['type' => 'filter', 'column' => 'status', 'value' => 'active']
    ]);
    
    echo "Processed " . $processedData['row_count'] . " active users\n";
    */
    
    // Example 3: Convert large CSV to Excel
    /*
    if (file_exists('large_data.csv')) {
        $excelData = $api->csvToExcel('large_data.csv', 'converted_data.xlsx');
        file_put_contents('downloads/converted_data.xlsx', $excelData);
        echo "CSV to Excel conversion completed!\n";
    }
    */
    
} catch (Exception $e) {
    echo "Error: " . $e->getMessage() . "\n";
}

// Performance monitoring function
function measurePerformance($callback, $description = 'Operation') {
    $startTime = microtime(true);
    $startMemory = memory_get_usage(true);
    
    $result = $callback();
    
    $endTime = microtime(true);
    $endMemory = memory_get_usage(true);
    
    echo "\n{$description} Performance:\n";
    echo "Time: " . number_format($endTime - $startTime, 2) . " seconds\n";
    echo "Memory used: " . number_format(($endMemory - $startMemory) / 1024 / 1024, 2) . " MB\n";
    echo "Peak memory: " . number_format(memory_get_peak_usage(true) / 1024 / 1024, 2) . " MB\n\n";
    
    return $result;
}
?>
