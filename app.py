from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import pandas as pd
import json
import os
from datetime import datetime
import tempfile
from io import BytesIO
from werkzeug.utils import secure_filename
import logging
import uuid
import shutil

# Import YBB routes
from api.ybb_routes import ybb_bp

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Register blueprints
app.register_blueprint(ybb_bp)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100MB max file size
app.config['UPLOAD_FOLDER'] = tempfile.gettempdir()

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'service': 'YBB Data Processing Service',
        'version': '1.0.0'
    })

@app.route('/api/export/excel', methods=['POST'])
def export_to_excel():
    """
    Export data to Excel file
    Expected payload:
    {
        "data": [...],  # Array of objects
        "filename": "export.xlsx",  # Optional filename
        "sheet_name": "Data",  # Optional sheet name
        "columns": [...],  # Optional column configuration
        "format_options": {...}  # Optional formatting options
    }
    """
    try:
        data = request.get_json()
        
        if not data or 'data' not in data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Extract parameters
        export_data = data['data']
        filename = data.get('filename', f'export_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx')
        sheet_name = data.get('sheet_name', 'Data')
        columns = data.get('columns')
        format_options = data.get('format_options', {})
        
        # Check data size and warn if large
        data_size = len(export_data)
        if data_size > 10000:
            logger.warning(f"Large dataset detected: {data_size} rows. Consider using chunked processing.")
        
        # Convert data to DataFrame
        df = pd.DataFrame(export_data)
        
        # Apply column selection if specified
        if columns:
            df = df[columns] if all(col in df.columns for col in columns) else df
        
        # Create Excel file in memory
        output = BytesIO()
        
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name=sheet_name, index=False)
            
            # Apply formatting if specified
            if format_options:
                worksheet = writer.sheets[sheet_name]
                
                # Auto-adjust column widths
                for column in worksheet.columns:
                    max_length = 0
                    column = [cell for cell in column]
                    for cell in column:
                        try:
                            if len(str(cell.value)) > max_length:
                                max_length = len(str(cell.value))
                        except:
                            pass
                    adjusted_width = (max_length + 2)
                    worksheet.column_dimensions[column[0].column_letter].width = adjusted_width
        
        output.seek(0)
        
        # Ensure filename is secure
        secure_name = secure_filename(filename)
        
        return send_file(
            output,
            as_attachment=True,
            download_name=secure_name,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        
    except Exception as e:
        logger.error(f"Excel export error: {str(e)}")
        return jsonify({'error': f'Export failed: {str(e)}'}), 500

@app.route('/api/data/process', methods=['POST'])
def process_data():
    """
    Process and transform data
    Expected payload:
    {
        "data": [...],
        "operations": [
            {"type": "filter", "column": "status", "value": "active"},
            {"type": "sort", "column": "date", "order": "desc"},
            {"type": "group", "column": "category", "aggregate": "count"}
        ]
    }
    """
    try:
        request_data = request.get_json()
        
        if not request_data or 'data' not in request_data:
            return jsonify({'error': 'No data provided'}), 400
        
        df = pd.DataFrame(request_data['data'])
        operations = request_data.get('operations', [])
        
        # Apply operations
        for operation in operations:
            op_type = operation.get('type')
            
            if op_type == 'filter':
                column = operation['column']
                value = operation['value']
                df = df[df[column] == value]
                
            elif op_type == 'sort':
                column = operation['column']
                order = operation.get('order', 'asc')
                ascending = order == 'asc'
                df = df.sort_values(by=column, ascending=ascending)
                
            elif op_type == 'group':
                column = operation['column']
                aggregate = operation.get('aggregate', 'count')
                if aggregate == 'count':
                    df = df.groupby(column).size().reset_index(name='count')
                elif aggregate == 'sum':
                    sum_column = operation.get('sum_column')
                    if sum_column:
                        df = df.groupby(column)[sum_column].sum().reset_index()
        
        return jsonify({
            'data': df.to_dict('records'),
            'columns': list(df.columns),
            'row_count': len(df)
        })
        
    except Exception as e:
        logger.error(f"Data processing error: {str(e)}")
        return jsonify({'error': f'Processing failed: {str(e)}'}), 500

# New endpoints for file-based data processing
@app.route('/api/upload/csv', methods=['POST'])
def upload_csv():
    """
    Upload CSV file and convert to Excel or process data
    """
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not file.filename.lower().endswith('.csv'):
            return jsonify({'error': 'Only CSV files are allowed'}), 400
        
        # Read CSV data
        df = pd.read_csv(file)
        
        # Get additional parameters
        output_format = request.form.get('format', 'excel')
        filename = request.form.get('filename', 'converted_file')
        
        if output_format.lower() == 'excel':
            # Convert to Excel
            output = BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name='Data', index=False)
                
                # Auto-adjust column widths
                worksheet = writer.sheets['Data']
                for column in worksheet.columns:
                    max_length = 0
                    column = [cell for cell in column]
                    for cell in column:
                        try:
                            if len(str(cell.value)) > max_length:
                                max_length = len(str(cell.value))
                        except:
                            pass
                    adjusted_width = min(max_length + 2, 50)
                    worksheet.column_dimensions[column[0].column_letter].width = adjusted_width
            
            output.seek(0)
            excel_filename = filename if filename.endswith('.xlsx') else f"{filename}.xlsx"
            
            return send_file(
                output,
                as_attachment=True,
                download_name=secure_filename(excel_filename),
                mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )
        else:
            # Return JSON data
            return jsonify({
                'data': df.to_dict('records'),
                'columns': list(df.columns),
                'row_count': len(df),
                'message': 'CSV data processed successfully'
            })
            
    except Exception as e:
        logger.error(f"CSV upload error: {str(e)}")
        return jsonify({'error': f'CSV processing failed: {str(e)}'}), 500

@app.route('/api/data/validate', methods=['POST'])
def validate_data():
    """
    Validate data structure and provide statistics
    """
    try:
        data = request.get_json()
        
        if not data or 'data' not in data:
            return jsonify({'error': 'No data provided'}), 400
        
        df = pd.DataFrame(data['data'])
        
        # Generate data statistics
        stats = {
            'row_count': len(df),
            'column_count': len(df.columns),
            'columns': list(df.columns),
            'data_types': df.dtypes.astype(str).to_dict(),
            'null_counts': df.isnull().sum().to_dict(),
            'memory_usage_mb': df.memory_usage(deep=True).sum() / 1024 / 1024,
            'sample_data': df.head(5).to_dict('records') if len(df) > 0 else []
        }
        
        # Recommendations
        recommendations = []
        if len(df) > 10000:
            recommendations.append("Consider using chunked processing for better performance")
        if df.memory_usage(deep=True).sum() / 1024 / 1024 > 100:
            recommendations.append("Large dataset detected - chunked processing recommended")
        if df.isnull().sum().sum() > 0:
            recommendations.append("Dataset contains null values - consider data cleaning")
        
        stats['recommendations'] = recommendations
        
        return jsonify(stats)
        
    except Exception as e:
        logger.error(f"Data validation error: {str(e)}")
        return jsonify({'error': f'Data validation failed: {str(e)}'}), 500
@app.route('/api/export/excel/chunked', methods=['POST'])
def export_to_excel_chunked():
    """
    Export large datasets to Excel using chunked processing
    Expected payload:
    {
        "session_id": "unique_session_id",
        "chunk_data": [...],  # Current chunk of data
        "chunk_index": 0,     # Current chunk number
        "total_chunks": 5,    # Total number of chunks
        "filename": "export.xlsx",
        "sheet_name": "Data",
        "format_options": {...}
    }
    """
    try:
        data = request.get_json()
        
        if not data or 'chunk_data' not in data:
            return jsonify({'error': 'No chunk data provided'}), 400
        
        session_id = data.get('session_id', f'session_{datetime.now().strftime("%Y%m%d_%H%M%S")}')
        chunk_data = data['chunk_data']
        chunk_index = data.get('chunk_index', 0)
        total_chunks = data.get('total_chunks', 1)
        filename = data.get('filename', f'export_{session_id}.xlsx')
        sheet_name = data.get('sheet_name', 'Data')
        format_options = data.get('format_options', {})
        
        # Create temporary directory for session files
        temp_dir = tempfile.gettempdir()
        session_dir = os.path.join(temp_dir, f'excel_session_{session_id}')
        os.makedirs(session_dir, exist_ok=True)
        
        # Save current chunk as CSV for later processing
        chunk_file = os.path.join(session_dir, f'chunk_{chunk_index}.csv')
        df_chunk = pd.DataFrame(chunk_data)
        df_chunk.to_csv(chunk_file, index=False)
        
        # If this is the last chunk, combine all chunks and create Excel
        if chunk_index == total_chunks - 1:
            # Read all chunk files
            all_chunks = []
            for i in range(total_chunks):
                chunk_path = os.path.join(session_dir, f'chunk_{i}.csv')
                if os.path.exists(chunk_path):
                    chunk_df = pd.read_csv(chunk_path)
                    all_chunks.append(chunk_df)
            
            # Combine all chunks
            combined_df = pd.concat(all_chunks, ignore_index=True)
            
            # Create Excel file
            output = BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                combined_df.to_excel(writer, sheet_name=sheet_name, index=False)
                
                # Apply formatting
                if format_options:
                    worksheet = writer.sheets[sheet_name]
                    for column in worksheet.columns:
                        max_length = 0
                        column = [cell for cell in column]
                        for cell in column:
                            try:
                                if len(str(cell.value)) > max_length:
                                    max_length = len(str(cell.value))
                            except:
                                pass
                        adjusted_width = min(max_length + 2, 50)
                        worksheet.column_dimensions[column[0].column_letter].width = adjusted_width
            
            output.seek(0)
            
            # Cleanup session files
            import shutil
            shutil.rmtree(session_dir, ignore_errors=True)
            
            return send_file(
                output,
                as_attachment=True,
                download_name=secure_filename(filename),
                mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )
        else:
            return jsonify({
                'status': 'chunk_received',
                'session_id': session_id,
                'chunk_index': chunk_index,
                'total_chunks': total_chunks
            })
        
    except Exception as e:
        logger.error(f"Chunked Excel export error: {str(e)}")
        return jsonify({'error': f'Chunked export failed: {str(e)}'}), 500

@app.route('/api/data/process/chunked', methods=['POST'])
def process_data_chunked():
    """
    Process large datasets in chunks
    """
    try:
        request_data = request.get_json()
        
        if not request_data or 'chunk_data' not in request_data:
            return jsonify({'error': 'No chunk data provided'}), 400
        
        session_id = request_data.get('session_id', f'session_{datetime.now().strftime("%Y%m%d_%H%M%S")}')
        chunk_data = request_data['chunk_data']
        chunk_index = request_data.get('chunk_index', 0)
        total_chunks = request_data.get('total_chunks', 1)
        operations = request_data.get('operations', [])
        
        # Process current chunk
        df_chunk = pd.DataFrame(chunk_data)
        
        # Apply operations to chunk
        for operation in operations:
            op_type = operation.get('type')
            
            if op_type == 'filter':
                column = operation['column']
                value = operation['value']
                df_chunk = df_chunk[df_chunk[column] == value]
                
            elif op_type == 'sort':
                column = operation['column']
                order = operation.get('order', 'asc')
                ascending = order == 'asc'
                df_chunk = df_chunk.sort_values(by=column, ascending=ascending)
        
        # Create temporary directory for session files
        temp_dir = tempfile.gettempdir()
        session_dir = os.path.join(temp_dir, f'process_session_{session_id}')
        os.makedirs(session_dir, exist_ok=True)
        
        # Save processed chunk
        chunk_file = os.path.join(session_dir, f'processed_chunk_{chunk_index}.csv')
        df_chunk.to_csv(chunk_file, index=False)
        
        # If this is the last chunk, combine results
        if chunk_index == total_chunks - 1:
            all_chunks = []
            for i in range(total_chunks):
                chunk_path = os.path.join(session_dir, f'processed_chunk_{i}.csv')
                if os.path.exists(chunk_path):
                    chunk_df = pd.read_csv(chunk_path)
                    all_chunks.append(chunk_df)
            
            # Combine all processed chunks
            combined_df = pd.concat(all_chunks, ignore_index=True)
            
            # Apply global operations (like final sorting)
            for operation in operations:
                if operation.get('type') == 'sort' and operation.get('global', False):
                    column = operation['column']
                    order = operation.get('order', 'asc')
                    ascending = order == 'asc'
                    combined_df = combined_df.sort_values(by=column, ascending=ascending)
            
            # Cleanup session files
            import shutil
            shutil.rmtree(session_dir, ignore_errors=True)
            
            return jsonify({
                'status': 'completed',
                'data': combined_df.to_dict('records'),
                'columns': list(combined_df.columns),
                'row_count': len(combined_df),
                'session_id': session_id
            })
        else:
            return jsonify({
                'status': 'chunk_processed',
                'session_id': session_id,
                'chunk_index': chunk_index,
                'total_chunks': total_chunks,
                'chunk_row_count': len(df_chunk)
            })
        
    except Exception as e:
        logger.error(f"Chunked data processing error: {str(e)}")
        return jsonify({'error': f'Chunked processing failed: {str(e)}'}), 500

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
