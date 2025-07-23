<!-- Use this file to provide workspace-specific custom instructions to Copilot. For more details, visit https://code.visualstudio.com/docs/copilot/copilot-customization#_use-a-githubcopilotinstructionsmd-file -->

# YBB Data Management API - Copilot Instructions

This is a Python Flask API service designed for data processing and Excel export functionality. The service is intended to work alongside a PHP web application to handle complex data operations.

## Project Context
- **Purpose**: Dedicated API service for data processing, Excel exports, and database operations
- **Technology Stack**: Python Flask, pandas, openpyxl, SQLAlchemy, MySQL
- **Integration**: Designed to be consumed by a PHP web application via HTTP API calls

## Key Features
1. **Excel Export**: Generate Excel files from JSON data with formatting options
2. **Database Queries**: Execute SQL queries and return results in JSON or Excel format
3. **Data Processing**: Transform and manipulate data with filtering, sorting, and grouping operations
4. **Health Monitoring**: Health check endpoints for service monitoring

## Development Guidelines
- Follow Flask best practices for API development
- Use pandas for efficient data manipulation
- Implement proper error handling and logging
- Maintain RESTful API design patterns
- Include comprehensive input validation
- Use environment variables for configuration

## API Endpoints
- `GET /health` - Health check
- `POST /api/export/excel` - Export data to Excel
- `POST /api/query` - Execute database queries
- `POST /api/data/process` - Process and transform data

## Code Style
- Use Python PEP 8 style guidelines
- Include docstrings for all functions and classes
- Implement proper exception handling
- Use type hints where appropriate
- Follow Flask application factory pattern for larger applications
