# YBB Data Processing Service - Implementation Guide

## 🚀 Service Overview

This Python Flask service is designed specifically for **data processing and Excel export**. It handles:
- Converting JSON data to Excel files
- Data transformation (filtering, sorting, grouping)
- Large dataset processing with chunking
- File format conversions

**No database dependencies** - Pure data processing focus!

## 📋 Quick Start Guide

### 1. Start the Service

```bash
# Activate virtual environment (if not already active)
.\.venv\Scripts\activate

# Run the service
python app.py
```

Service will be available at: `http://localhost:5000`

### 2. Test the Service

```bash
python quick_test.py
```

## 🔌 API Endpoints

### Health Check
```
GET /health
```
Returns service status and version info.

### Excel Export (Small Datasets)
```
POST /api/export/excel
```
**Request:**
```json
{
  "data": [
    {"name": "John", "age": 30, "city": "New York"},
    {"name": "Jane", "age": 25, "city": "Los Angeles"}
  ],
  "filename": "report.xlsx",
  "sheet_name": "Users",
  "format_options": {
    "auto_width": true,
    "header_style": {
      "bold": true,
      "font_color": "FFFFFF",
      "bg_color": "366092"
    }
  }
}
```
**Response:** Excel file (binary)

### Excel Export (Large Datasets - Chunked)
```
POST /api/export/excel/chunked
```
**For datasets > 5,000 records**
```json
{
  "session_id": "unique_session_id",
  "chunk_data": [...],
  "chunk_index": 0,
  "total_chunks": 5,
  "filename": "large_report.xlsx"
}
```

### Data Processing
```
POST /api/data/process
```
**Request:**
```json
{
  "data": [...],
  "operations": [
    {"type": "filter", "column": "status", "value": "active"},
    {"type": "sort", "column": "date", "order": "desc"},
    {"type": "group", "column": "category", "aggregate": "count"}
  ]
}
```

### Data Validation
```
POST /api/data/validate
```
Returns data statistics, column info, and recommendations.

### CSV Upload
```
POST /api/upload/csv
```
Upload CSV file and convert to Excel or JSON.

## 🐘 PHP Integration

### Basic Usage

```php
<?php
require_once 'examples/simple_php_integration.php';

$processor = new YBBDataProcessor('http://localhost:5000');

// 1. Convert array to Excel
$data = [
    ['name' => 'John', 'age' => 30],
    ['name' => 'Jane', 'age' => 25]
];

$excelData = $processor->arrayToExcel($data, 'users.xlsx');
file_put_contents('downloads/users.xlsx', $excelData);

// 2. For large datasets (auto-chunking)
$largeData = []; // 50,000+ records
$excelData = $processor->largeArrayToExcel($largeData, 'large_report.xlsx');

// 3. Direct browser download
$processor->downloadExcel($excelData, 'report.xlsx');
?>
```

### Integration in Your Existing PHP App

```php
// In your controller or function
function exportDataToExcel($data, $filename = 'export.xlsx') {
    try {
        $processor = new YBBDataProcessor();
        
        // Automatically handles chunking for large datasets
        if (count($data) > 5000) {
            $excelData = $processor->largeArrayToExcel($data, $filename);
        } else {
            $excelData = $processor->arrayToExcel($data, $filename);
        }
        
        // Download in browser
        header('Content-Type: application/vnd.openxmlformats-officedocument.spreadsheetml.sheet');
        header('Content-Disposition: attachment; filename="' . $filename . '"');
        echo $excelData;
        exit;
        
    } catch (Exception $e) {
        // Handle error
        error_log("Excel export failed: " . $e->getMessage());
        return false;
    }
}
```

## 📊 Performance Guidelines

### Dataset Size Recommendations:

| Records | Method | Performance |
|---------|--------|-------------|
| < 1,000 | Regular API | Instant |
| 1,000 - 5,000 | Regular API | 1-3 seconds |
| 5,000 - 50,000 | Chunked API | 5-30 seconds |
| 50,000+ | Chunked + CSV | 30+ seconds |

### Memory Usage:
- **Small datasets** (< 5K): ~10-50 MB
- **Medium datasets** (5-20K): ~50-200 MB  
- **Large datasets** (20K+): ~200-500 MB (with chunking)

## 🔧 Configuration

### Environment Variables (.env)
```bash
# Flask configuration
FLASK_ENV=development
FLASK_DEBUG=True
API_HOST=0.0.0.0
API_PORT=5000

# Performance settings
MAX_CHUNK_SIZE=1000
MAX_MEMORY_MB=500
TEMP_DIR=/tmp/processing
```

### Production Settings
```python
# For production deployment
CHUNK_SIZE = 1000
MAX_MEMORY_MB = 1000
ENABLE_MONITORING = True
LOG_LEVEL = "INFO"
```

## 🚀 Deployment

### Development
```bash
python app.py
```

### Production (with Gunicorn)
```bash
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

### Docker (Optional)
```dockerfile
FROM python:3.10
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 5000
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:app"]
```

## 🔍 Monitoring & Debugging

### Check Service Status
```bash
curl http://localhost:5000/health
```

### Monitor Performance
```php
// In PHP
$validation = $processor->validateData($data);
if (!empty($validation['recommendations'])) {
    foreach ($validation['recommendations'] as $rec) {
        echo "Recommendation: {$rec}\n";
    }
}
```

### Log Files
- Flask logs: Console output
- Performance logs: `utils/performance.py`

## ⚡ Best Practices

### 1. Data Preparation
```php
// Clean your data before sending
$cleanData = array_map(function($row) {
    // Remove null values, clean strings, etc.
    return array_filter($row, function($value) {
        return $value !== null && $value !== '';
    });
}, $rawData);
```

### 2. Error Handling
```php
try {
    $result = $processor->arrayToExcel($data);
    return $result;
} catch (Exception $e) {
    error_log("Excel export failed: " . $e->getMessage());
    
    // Fallback to CSV or show error message
    return false;
}
```

### 3. Progress Indication (for large datasets)
```php
// For large datasets, implement progress feedback
if (count($data) > 10000) {
    echo "Processing large dataset, please wait...\n";
    $result = $processor->largeArrayToExcel($data);
} else {
    $result = $processor->arrayToExcel($data);
}
```

## 🎯 Common Use Cases

### 1. Database Export to Excel
```php
// Export database query results
$pdo = new PDO($dsn, $user, $pass);
$stmt = $pdo->query("SELECT * FROM users WHERE active = 1");
$data = $stmt->fetchAll(PDO::FETCH_ASSOC);

$processor = new YBBDataProcessor();
$excelData = $processor->arrayToExcel($data, 'active_users.xlsx');
```

### 2. Report Generation
```php
// Generate monthly reports
$reportData = [
    ['month' => 'Jan', 'sales' => 50000, 'profit' => 12000],
    ['month' => 'Feb', 'sales' => 60000, 'profit' => 15000],
    // ... more data
];

$processor->downloadExcel(
    $processor->arrayToExcel($reportData, 'monthly_report.xlsx'),
    'monthly_report.xlsx'
);
```

### 3. Data Transformation
```php
// Filter and sort data before export
$processed = $processor->processData($data, [
    ['type' => 'filter', 'column' => 'status', 'value' => 'completed'],
    ['type' => 'sort', 'column' => 'date', 'order' => 'desc']
]);

$excelData = $processor->arrayToExcel($processed['data']);
```

## 🆘 Troubleshooting

### Service Won't Start
```bash
# Check if port is in use
netstat -an | findstr :5000

# Check Python virtual environment
which python
pip list
```

### Excel Export Fails
- Check data format (must be array of objects)
- Verify service is running (`/health` endpoint)
- Check network connectivity
- Review error logs

### Performance Issues
- Use chunked processing for large datasets
- Monitor memory usage
- Consider data pagination in PHP
- Implement caching for repeated exports

---

## 📞 Support

If you encounter issues:
1. Check the `/health` endpoint
2. Review console logs
3. Test with `quick_test.py`
4. Verify PHP integration with small datasets first
