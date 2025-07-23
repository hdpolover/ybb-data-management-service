<?php
/**
 * PHP Integration examples for YBB Data Management API
 * 
 * This file contains examples of how to integrate the Python Flask API
 * with your existing PHP application.
 */

class YBBDataAPI {
    private $apiBaseUrl;
    
    public function __construct($baseUrl = 'http://localhost:5000') {
        $this->apiBaseUrl = rtrim($baseUrl, '/');
    }
    
    /**
     * Check API health status
     */
    public function checkHealth() {
        $url = $this->apiBaseUrl . '/health';
        
        $response = file_get_contents($url);
        return json_decode($response, true);
    }
    
    /**
     * Export data to Excel
     */
    public function exportToExcel($data, $filename = null, $sheetName = 'Data', $formatOptions = []) {
        $url = $this->apiBaseUrl . '/api/export/excel';
        
        $payload = [
            'data' => $data,
            'filename' => $filename ?: 'export_' . date('Y-m-d_H-i-s') . '.xlsx',
            'sheet_name' => $sheetName,
            'format_options' => $formatOptions
        ];
        
        $context = stream_context_create([
            'http' => [
                'method' => 'POST',
                'header' => 'Content-Type: application/json',
                'content' => json_encode($payload)
            ]
        ]);
        
        $result = file_get_contents($url, false, $context);
        
        if ($result === false) {
            throw new Exception('Failed to export data to Excel');
        }
        
        return $result; // Binary Excel data
    }
    
    /**
     * Execute database query
     */
    public function executeQuery($query, $params = [], $format = 'json') {
        $url = $this->apiBaseUrl . '/api/query';
        
        $payload = [
            'query' => $query,
            'params' => $params,
            'format' => $format
        ];
        
        $context = stream_context_create([
            'http' => [
                'method' => 'POST',
                'header' => 'Content-Type: application/json',
                'content' => json_encode($payload)
            ]
        ]);
        
        $result = file_get_contents($url, false, $context);
        
        if ($result === false) {
            throw new Exception('Failed to execute query');
        }
        
        if ($format === 'json') {
            return json_decode($result, true);
        } else {
            return $result; // Binary Excel data
        }
    }
    
    /**
     * Process data with operations
     */
    public function processData($data, $operations = []) {
        $url = $this->apiBaseUrl . '/api/data/process';
        
        $payload = [
            'data' => $data,
            'operations' => $operations
        ];
        
        $context = stream_context_create([
            'http' => [
                'method' => 'POST',
                'header' => 'Content-Type: application/json',
                'content' => json_encode($payload)
            ]
        ]);
        
        $result = file_get_contents($url, false, $context);
        
        if ($result === false) {
            throw new Exception('Failed to process data');
        }
        
        return json_decode($result, true);
    }
}

// Usage Examples
try {
    $api = new YBBDataAPI('http://localhost:5000');
    
    // Example 1: Export user data to Excel
    $userData = [
        ['name' => 'John Doe', 'email' => 'john@example.com', 'age' => 30],
        ['name' => 'Jane Smith', 'email' => 'jane@example.com', 'age' => 25],
        ['name' => 'Bob Johnson', 'email' => 'bob@example.com', 'age' => 35]
    ];
    
    $excelData = $api->exportToExcel(
        $userData, 
        'users_export.xlsx', 
        'Users',
        [
            'auto_width' => true,
            'header_style' => [
                'bold' => true,
                'font_color' => 'FFFFFF',
                'bg_color' => '366092'
            ]
        ]
    );
    
    // Save the Excel file
    file_put_contents('downloads/users_export.xlsx', $excelData);
    echo "Excel file created successfully!\n";
    
    // Example 2: Process data with filtering and sorting
    $processedData = $api->processData($userData, [
        ['type' => 'filter', 'column' => 'age', 'value' => 30],
        ['type' => 'sort', 'column' => 'name', 'order' => 'asc']
    ]);
    
    echo "Processed data:\n";
    print_r($processedData);
    
    // Example 3: Execute database query (if database is configured)
    /*
    $queryResult = $api->executeQuery(
        "SELECT * FROM users WHERE status = :status",
        ['status' => 'active']
    );
    
    echo "Query results:\n";
    print_r($queryResult);
    */
    
} catch (Exception $e) {
    echo "Error: " . $e->getMessage() . "\n";
}

// Example integration with existing PHP functions
function exportDataToExcel($data, $filename = null) {
    $api = new YBBDataAPI();
    
    try {
        $excelData = $api->exportToExcel($data, $filename);
        
        // Set headers for download
        header('Content-Type: application/vnd.openxmlformats-officedocument.spreadsheetml.sheet');
        header('Content-Disposition: attachment; filename="' . ($filename ?: 'export.xlsx') . '"');
        header('Content-Length: ' . strlen($excelData));
        
        echo $excelData;
        exit;
        
    } catch (Exception $e) {
        // Handle error - perhaps log it and show user-friendly message
        error_log("Excel export failed: " . $e->getMessage());
        return false;
    }
}

// Usage in your existing PHP application:
// exportDataToExcel($yourData, 'report.xlsx');
?>
