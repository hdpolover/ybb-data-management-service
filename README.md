# YBB Data Processing Service

A dedicated Python Flask service for **data processing and Excel export** functionality. Designed to work alongside PHP applications that need robust data transformation and file generation capabilities.

## 🎯 Purpose

This service focuses exclusively on:
- **Excel Export**: Convert JSON data to Excel files with professional formatting
- **Data Processing**: Filter, sort, and transform data efficiently
- **Large Dataset Handling**: Chunked processing for datasets with tens of thousands of records
- **File Conversions**: CSV to Excel, JSON to Excel, and more

**No database dependencies** - Pure data processing microservice!

## ✨ Key Features

- 🚀 **High Performance**: Handles 50,000+ records efficiently with chunked processing
- 📊 **Professional Excel Output**: Auto-formatting, styling, and column width adjustment
- 🔄 **Data Transformation**: Advanced filtering, sorting, and grouping operations
- 📈 **Scalable Architecture**: Memory-efficient processing with automatic optimization
- 🔌 **Easy Integration**: Simple REST API for seamless PHP integration
- ⚡ **Fast Processing**: Optimized pandas operations for data manipulation

## 🚀 Quick Start

### Installation

```bash
# 1. Clone/download the project
cd ybb-data-management-web-flask

# 2. Create virtual environment (if not exists)
python -m venv .venv

# 3. Activate virtual environment
.venv\Scripts\activate  # Windows
# source .venv/bin/activate  # Linux/Mac

# 4. Install dependencies
pip install -r requirements.txt

# 5. Start the service
python app.py
```

### Test the Service

```bash
python quick_test.py
```

The service will be available at `http://localhost:5000`

## 📡 API Endpoints

### Core Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/health` | GET | Service health check |
| `/api/export/excel` | POST | Convert data to Excel (< 5K records) |
| `/api/export/excel/chunked` | POST | Convert large datasets to Excel |
| `/api/data/process` | POST | Transform and filter data |
| `/api/data/validate` | POST | Validate data and get statistics |
| `/api/upload/csv` | POST | Upload CSV and convert to Excel |

### Example Usage

```bash
# Health check
curl http://localhost:5000/health

# Excel export
curl -X POST http://localhost:5000/api/export/excel \
  -H "Content-Type: application/json" \
  -d '{"data": [{"name": "John", "age": 30}]}' \
  --output export.xlsx
```

## 🐘 PHP Integration

### Simple Integration

```php
<?php
require_once 'examples/simple_php_integration.php';

$processor = new YBBDataProcessor('http://localhost:5000');

// Convert array to Excel
$data = [
    ['name' => 'John Doe', 'email' => 'john@example.com', 'salary' => 50000],
    ['name' => 'Jane Smith', 'email' => 'jane@example.com', 'salary' => 60000]
];

$excelData = $processor->arrayToExcel($data, 'employees.xlsx');
file_put_contents('downloads/employees.xlsx', $excelData);

// For large datasets (auto-chunking)
$largeData = getData(); // Your function that returns large array
$excelData = $processor->largeArrayToExcel($largeData, 'large_report.xlsx');

// Direct download in browser
$processor->downloadExcel($excelData, 'report.xlsx');
?>
```

### Advanced Processing

```php
// Filter and transform data
$processed = $processor->processData($data, [
    ['type' => 'filter', 'column' => 'status', 'value' => 'active'],
    ['type' => 'sort', 'column' => 'salary', 'order' => 'desc']
]);

// Convert processed data to Excel
$excelData = $processor->arrayToExcel($processed['data'], 'filtered_report.xlsx');
```

## 📊 Performance Benchmarks

| Dataset Size | Processing Method | Time | Memory Usage |
|--------------|-------------------|------|--------------|
| 1,000 records | Regular | 0.5s | 20 MB |
| 5,000 records | Regular | 2.1s | 50 MB |
| 10,000 records | Chunked | 5.2s | 80 MB |
| 50,000 records | Chunked | 25.8s | 200 MB |

## 🔧 Configuration

### Environment Variables

Create a `.env` file:

```bash
# Service configuration
API_HOST=0.0.0.0
API_PORT=5000
FLASK_DEBUG=True

# Performance settings
MAX_CHUNK_SIZE=1000
MAX_MEMORY_MB=500
```

### Production Deployment

```bash
# Using Gunicorn for production
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

## 📁 Project Structure

```
ybb-data-management-web-flask/
├── app.py                          # Main Flask application
├── requirements.txt                # Python dependencies
├── config/
│   ├── __init__.py
│   └── ybb_export_config.py       # Export templates & mappings
├── api/
│   ├── __init__.py
│   └── ybb_routes.py               # YBB API endpoints
├── services/
│   ├── __init__.py
│   └── ybb_export_service.py       # Core export logic
├── utils/
│   ├── __init__.py
│   ├── excel_exporter.py          # Excel generation utilities
│   └── performance.py             # Performance monitoring
├── examples/
│   └── simple_php_integration.php  # PHP integration class
├── test_ybb_api.py                 # Comprehensive test suite
├── deploy.sh                       # Production deployment script
├── YBB_API_CODEIGNITER_INTEGRATION.md # API documentation
└── PROJECT_IMPLEMENTATION_SUMMARY.md  # Project overview
```

## 🎯 Use Cases

### 1. Database Export
Export query results directly to Excel:
```php
$data = $pdo->query("SELECT * FROM users")->fetchAll(PDO::FETCH_ASSOC);
$processor->downloadExcel($processor->arrayToExcel($data), 'users.xlsx');
```

### 2. Report Generation
Generate formatted reports:
```php
$reportData = generateMonthlyReport(); // Your data function
$excelData = $processor->arrayToExcel($reportData, 'monthly_report.xlsx', [
    'format_options' => [
        'header_style' => ['bold' => true, 'bg_color' => '366092']
    ]
]);
```

### 3. Data Transformation
Process data before export:
```php
$cleanedData = $processor->processData($rawData, [
    ['type' => 'filter', 'column' => 'status', 'value' => 'approved'],
    ['type' => 'sort', 'column' => 'date', 'order' => 'desc']
]);
```

## 🔍 Monitoring

### Health Check
```bash
curl http://localhost:5000/health
```

### Data Validation
```php
$stats = $processor->validateData($data);
echo "Dataset has {$stats['row_count']} rows and {$stats['column_count']} columns";
```

## 🆘 Troubleshooting

### Common Issues

1. **Service not starting**: Check if port 5000 is available
2. **Import errors**: Ensure virtual environment is activated
3. **Excel export fails**: Verify data format (array of objects)
4. **Memory issues**: Use chunked processing for large datasets

### Getting Help

1. Run `python quick_test.py` to verify service functionality
2. Check console logs for error messages
3. Review the `IMPLEMENTATION_GUIDE.md` for detailed examples

## 🔄 Updates and Maintenance

### Adding New Features
- Extend API endpoints in `app.py`
- Add utility functions in `utils/` directory
- Update PHP integration class accordingly

### Performance Optimization
- Monitor memory usage with `/api/data/validate`
- Adjust chunk sizes based on your server capacity
- Implement caching for frequently processed data

## 📄 License

This project is open source and available under the MIT License.

---

## 🎉 Ready to Use!

The service is now ready for integration with your PHP application. Use the provided PHP integration class to start converting your data to Excel files efficiently!

For detailed implementation examples and advanced usage, see `IMPLEMENTATION_GUIDE.md`.
