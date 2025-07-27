"""
YBB Export Service - Handles YBB-specific data export logic
"""
import pandas as pd
import uuid
from datetime import datetime, timedelta
import os
import tempfile
import zipfile
from io import BytesIO
import logging
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment
from config.ybb_export_config import (
    EXPORT_TEMPLATES, STATUS_MAPPINGS, SYSTEM_CONFIG, 
    get_template, get_status_label, get_chunk_size, should_use_chunked_processing,
    get_cleanup_config, get_storage_limits
)
from utils.file_manager import ExportFileManager

logger = logging.getLogger(__name__)

class YBBExportService:
    """Main service for handling YBB data exports"""
    
    def __init__(self):
        self.temp_dir = tempfile.gettempdir()
        self.exports_storage = {}  # In production, use Redis or database
        self.file_manager = ExportFileManager()
        
        # Get cleanup configuration from config file
        cleanup_config = get_cleanup_config()
        storage_limits = get_storage_limits()
        
        self.max_concurrent_exports = storage_limits.get('max_concurrent_exports', 20)
        self.auto_cleanup_enabled = cleanup_config.get('auto_cleanup_enabled', True)
        self.cleanup_on_startup = cleanup_config.get('cleanup_on_startup', True)
        self.cleanup_on_export = cleanup_config.get('cleanup_on_export', False)
        self.cleanup_interval_minutes = cleanup_config.get('cleanup_interval_minutes', 30)
        self.min_export_age_minutes = cleanup_config.get('min_export_age_minutes', 10)
        
        # Track last cleanup time
        self.last_cleanup_time = datetime.now()
        
        # Perform startup cleanup if enabled
        if self.cleanup_on_startup:
            self._cleanup_old_exports()
    
    def create_export(self, export_request):
        """Main export creation method"""
        try:
            # Periodic cleanup based on time interval (not before every export)
            if self.auto_cleanup_enabled and self._should_run_cleanup():
                self._cleanup_old_exports()
            
            # Validate request
            validation_result = self._validate_export_request(export_request)
            if not validation_result["valid"]:
                return {"status": "error", "message": validation_result["message"]}
            
            export_id = str(uuid.uuid4())
            export_type = export_request["export_type"]
            template_name = export_request.get("template", "standard")
            
            # Get template configuration
            template_config = get_template(export_type, template_name)
            if not template_config:
                return {"status": "error", "message": f"Template '{template_name}' not found for {export_type}"}
            
            # Process data based on size
            data = export_request["data"]
            record_count = len(data)
            
            if should_use_chunked_processing(record_count, template_config):
                return self._create_large_export(export_id, export_request, template_config)
            else:
                return self._create_standard_export(export_id, export_request, template_config)
                
        except Exception as e:
            logger.error(f"Export creation failed: {str(e)}")
            return {"status": "error", "message": f"Export failed: {str(e)}"}
    
    def _validate_export_request(self, request):
        """Validate export request structure"""
        required_fields = ["export_type", "data"]
        
        for field in required_fields:
            if field not in request:
                return {"valid": False, "message": f"Missing required field: {field}"}
        
        valid_export_types = ["participants", "payments", "ambassadors"]
        if request["export_type"] not in valid_export_types:
            return {"valid": False, "message": f"Invalid export_type. Must be one of: {valid_export_types}"}
        
        if not isinstance(request["data"], list):
            return {"valid": False, "message": "Data must be an array/list"}
        
        # Validate filename parameters using file manager
        filename_validation = self.file_manager.validate_filename_params(request)
        if not filename_validation['valid']:
            return filename_validation
        
        return {"valid": True}
    
    def _create_standard_export(self, export_id, export_request, template_config):
        """Create standard single-file export"""
        try:
            data = export_request["data"]
            export_type = export_request["export_type"]
            template_name = export_request.get("template", "standard")
            format_type = export_request.get("format", "excel")
            
            # Transform data
            processed_data = self._transform_data(data, export_type, template_config)
            
            # Create file
            if format_type.lower() == "excel":
                file_content, filename = self._create_excel_file(
                    processed_data, export_type, template_name, export_request
                )
            else:
                file_content, filename = self._create_csv_file(
                    processed_data, export_type, template_name, export_request
                )
            
            # Store export info
            export_info = {
                "export_id": export_id,
                "status": "success",
                "export_type": export_type,
                "template": template_name,
                "format": format_type,
                "record_count": len(data),
                "file_content": file_content,
                "filename": filename,
                "created_at": datetime.now(),
                "expires_at": datetime.now() + timedelta(days=SYSTEM_CONFIG["limits"]["file_retention_days"])
            }
            
            self.exports_storage[export_id] = export_info
            
            return {
                "status": "success",
                "message": "Export completed successfully",
                "data": {
                    "export_id": export_id,
                    "file_name": filename,
                    "file_size": len(file_content),
                    "record_count": len(data),
                    "download_url": f"/api/ybb/export/{export_id}/download",
                    "expires_at": export_info["expires_at"].isoformat()
                },
                "metadata": {
                    "export_type": export_type,
                    "template": template_name,
                    "filters_applied": export_request.get("filters", {}),
                    "generated_at": export_info["created_at"].isoformat(),
                    "processing_time": 0.5  # Placeholder
                }
            }
            
        except Exception as e:
            logger.error(f"Standard export creation failed: {str(e)}")
            raise
    
    def _create_large_export(self, export_id, export_request, template_config):
        """Create large export with chunking"""
        try:
            data = export_request["data"]
            export_type = export_request["export_type"]
            template_name = export_request.get("template", "standard")
            record_count = len(data)
            
            # Calculate chunk size
            chunk_size = get_chunk_size(export_type, template_name, record_count)
            
            # Split data into chunks
            chunks = [data[i:i + chunk_size] for i in range(0, len(data), chunk_size)]
            total_chunks = len(chunks)
            
            # Create individual files
            files_info = []
            temp_files = []
            
            for i, chunk in enumerate(chunks):
                processed_chunk = self._transform_data(chunk, export_type, template_config)
                
                # Create chunk file
                file_content, chunk_filename = self._create_excel_file(
                    processed_chunk, export_type, template_name, export_request, 
                    batch_info={"number": i + 1, "total": total_chunks}
                )
                
                # Save to temp file
                temp_file_path = os.path.join(self.temp_dir, f"{export_id}_chunk_{i+1}.xlsx")
                with open(temp_file_path, 'wb') as f:
                    f.write(file_content)
                
                temp_files.append(temp_file_path)
                
                files_info.append({
                    "batch_number": i + 1,
                    "file_name": chunk_filename,
                    "file_path": temp_file_path,
                    "file_size": len(file_content),
                    "record_count": len(chunk),
                    "record_range": f"{i * chunk_size + 1}-{min((i + 1) * chunk_size, record_count)}"
                })
            
            # Create ZIP archive
            zip_filename = self.file_manager.generate_zip_filename(export_request, export_id)
            zip_path = os.path.join(self.temp_dir, f"{export_id}_complete.zip")
            
            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for file_info in files_info:
                    zipf.write(file_info["file_path"], file_info["file_name"])
            
            # Get ZIP file size
            zip_size = os.path.getsize(zip_path)
            
            # Store export info
            export_info = {
                "export_id": export_id,
                "status": "success",
                "export_strategy": "multi_file",
                "export_type": export_type,
                "template": template_name,
                "record_count": record_count,
                "total_chunks": total_chunks,
                "files_info": files_info,
                "zip_path": zip_path,
                "zip_filename": zip_filename,
                "zip_size": zip_size,
                "temp_files": temp_files,
                "created_at": datetime.now(),
                "expires_at": datetime.now() + timedelta(days=SYSTEM_CONFIG["limits"]["file_retention_days"])
            }
            
            self.exports_storage[export_id] = export_info
            
            return {
                "status": "success",
                "message": "Large export completed successfully",
                "export_strategy": "multi_file",
                "data": {
                    "export_id": export_id,
                    "total_records": record_count,
                    "total_files": total_chunks,
                    "individual_files": [
                        {
                            "batch_number": f["batch_number"],
                            "file_name": f["file_name"],
                            "file_size": f["file_size"],
                            "record_count": f["record_count"],
                            "record_range": f["record_range"],
                            "download_url": f"/api/ybb/export/{export_id}/download/batch/{f['batch_number']}"
                        } for f in files_info
                    ],
                    "archive": {
                        "zip_file_name": zip_filename,
                        "zip_file_size": zip_size,
                        "download_url": f"/api/ybb/export/{export_id}/download/zip",
                        "compression_ratio": self.file_manager.calculate_compression_ratio(files_info, zip_path)
                    },
                    "expires_at": export_info["expires_at"].isoformat()
                },
                "metadata": {
                    "export_type": export_type,
                    "template": template_name,
                    "chunk_size": chunk_size,
                    "compression_used": "zip",
                    "processing_time": 5.0,  # Placeholder
                    "memory_peak": "200MB"  # Placeholder
                }
            }
            
        except Exception as e:
            logger.error(f"Large export creation failed: {str(e)}")
            raise
    
    def _transform_data(self, data, export_type, template_config):
        """Transform raw data according to template configuration with sanitization"""
        if not data:
            return []
        
        fields = template_config.get("fields", [])
        headers = template_config.get("headers", fields)
        
        transformed_data = []
        
        for record in data:
            transformed_record = {}
            
            for i, field in enumerate(fields):
                header = headers[i] if i < len(headers) else field
                value = record.get(field, "N/A")
                
                # Apply transformations based on field type
                if field in ["created_at", "updated_at", "payment_date", "birthdate"]:
                    if value and value != "N/A":
                        try:
                            if isinstance(value, str):
                                # Try to parse different date formats
                                for fmt in ["%Y-%m-%d %H:%M:%S", "%Y-%m-%d", "%d/%m/%Y"]:
                                    try:
                                        parsed_date = datetime.strptime(value, fmt)
                                        value = parsed_date.strftime("%Y-%m-%d")
                                        break
                                    except ValueError:
                                        continue
                        except:
                            value = str(value) if value else ""
                
                elif field in ["amount", "usd_amount"]:
                    if value and value != "N/A":
                        try:
                            value = f"{float(value):,.2f}"
                        except:
                            value = str(value) if value else ""
                
                elif field in ["form_status", "status"]:
                    if export_type == "participants":
                        value = get_status_label("form_status", value)
                    elif export_type == "payments":
                        value = get_status_label("payment_status", value)
                
                elif field == "payment_method_id":
                    value = get_status_label("payment_method", value)
                
                elif field in ["is_active", "is_deleted"]:
                    value = get_status_label("boolean_status", value)
                
                elif field == "category":
                    value = get_status_label("category", value)
                
                # Ensure value is not None and convert to string
                if value is None:
                    value = ""
                else:
                    value = str(value)
                
                # Clean and sanitize the value for Excel compatibility
                value = self._sanitize_excel_value(value)
                
                transformed_record[header] = value
            
            transformed_data.append(transformed_record)
        
        return transformed_data
    
    def _sanitize_excel_value(self, value):
        """
        Sanitize a single value for Excel compatibility
        
        Args:
            value: Raw value to sanitize
            
        Returns:
            Sanitized value safe for Excel
        """
        if value is None:
            return ""
        
        # Convert to string if not already
        str_value = str(value)
        
        # Handle empty strings
        if not str_value.strip():
            return ""
        
        # Remove problematic characters for Excel
        # Excel doesn't support characters below ASCII 32 except tab (9), newline (10), carriage return (13)
        cleaned_value = ""
        for char in str_value:
            char_code = ord(char)
            if char_code < 32:
                if char_code in [9, 10, 13]:  # Tab, newline, carriage return
                    cleaned_value += char
                else:
                    # Replace with space for other control characters
                    cleaned_value += " "
            elif char_code == 127:  # DEL character
                cleaned_value += " "
            else:
                cleaned_value += char
        
        # Remove excessive whitespace
        import re
        cleaned_value = re.sub(r'\s+', ' ', cleaned_value).strip()
        
        # Excel cell limit (32,767 characters)
        if len(cleaned_value) > 32767:
            cleaned_value = cleaned_value[:32764] + "..."
        
        return cleaned_value
    
    def _create_excel_file(self, data, export_type, template_name, export_request, batch_info=None):
        """Create Excel file from processed data with enhanced error handling"""
        if not data:
            raise ValueError("No data to export")
        
        try:
            # Import the improved Excel exporter
            from utils.excel_exporter import ExcelExporter
            
            # Generate filename using file manager
            filename = self.file_manager.generate_filename(export_request, str(uuid.uuid4())[:8], batch_info)
            filename = self.file_manager.sanitize_filename(filename)
            
            # Get sheet name using file manager
            sheet_name = self.file_manager.get_sheet_name(export_request, batch_info)
            
            # Create Excel file using the improved exporter
            excel_output = ExcelExporter.create_excel_file(
                data=data,
                filename=filename,
                sheet_name=sheet_name,
                format_options=None  # Use default formatting
            )
            
            return excel_output.getvalue(), filename
            
        except Exception as e:
            logger.error(f"Excel file creation failed: {str(e)}")
            # Fallback to pandas-only approach with minimal formatting
            try:
                logger.info("Attempting fallback Excel creation method")
                
                # Create DataFrame and sanitize data
                df = pd.DataFrame(data)
                
                # Basic data cleaning
                for col in df.columns:
                    df[col] = df[col].astype(str).apply(lambda x: self._sanitize_excel_value(x))
                
                # Generate filename
                filename = self.file_manager.generate_filename(export_request, str(uuid.uuid4())[:8], batch_info)
                filename = self.file_manager.sanitize_filename(filename)
                
                # Get sheet name
                sheet_name = self.file_manager.get_sheet_name(export_request, batch_info)
                
                # Create basic Excel file
                output = BytesIO()
                with pd.ExcelWriter(output, engine='openpyxl', options={'remove_timezone': True}) as writer:
                    df.to_excel(writer, sheet_name=sheet_name, index=False)
                
                output.seek(0)
                logger.info("Fallback Excel creation successful")
                return output.getvalue(), filename
                
            except Exception as fallback_error:
                logger.error(f"Fallback Excel creation also failed: {str(fallback_error)}")
                raise Exception(f"Excel file creation failed: {str(e)}. Fallback also failed: {str(fallback_error)}")
    
    def _create_csv_file(self, data, export_type, template_name, export_request):
        """Create CSV file from processed data with enhanced error handling"""
        try:
            # Create DataFrame and sanitize data
            df = pd.DataFrame(data)
            
            # Basic data cleaning for CSV
            for col in df.columns:
                df[col] = df[col].astype(str).apply(lambda x: self._sanitize_csv_value(x))
            
            # Generate filename using file manager
            filename = self.file_manager.generate_filename(export_request, str(uuid.uuid4())[:8])
            filename = self.file_manager.sanitize_filename(filename.replace('.xlsx', '.csv'))
            
            output = BytesIO()
            df.to_csv(output, index=False, encoding='utf-8')
            output.seek(0)
            
            return output.getvalue(), filename
            
        except Exception as e:
            logger.error(f"CSV file creation failed: {str(e)}")
            raise Exception(f"CSV file creation failed: {str(e)}")
    
    def _sanitize_csv_value(self, value):
        """
        Sanitize a single value for CSV compatibility
        
        Args:
            value: Raw value to sanitize
            
        Returns:
            Sanitized value safe for CSV
        """
        if value is None:
            return ""
        
        # Convert to string if not already
        str_value = str(value)
        
        # Handle empty strings
        if not str_value.strip():
            return ""
        
        # Remove problematic characters for CSV
        import re
        cleaned_value = re.sub(r'[\r\n]+', ' ', str_value)  # Replace newlines with spaces
        cleaned_value = cleaned_value.strip()
        
        return cleaned_value
    
    def get_export_status(self, export_id):
        """Get export status and download information"""
        if export_id not in self.exports_storage:
            return {"status": "error", "message": "Export not found"}
        
        export_info = self.exports_storage[export_id]
        
        # Check if expired
        if datetime.now() > export_info["expires_at"]:
            self._cleanup_export(export_id)
            return {"status": "error", "message": "Export has expired"}
        
        return {
            "status": export_info["status"],
            "export_id": export_id,
            "export_type": export_info["export_type"],
            "template": export_info["template"],
            "record_count": export_info["record_count"],
            "created_at": export_info["created_at"].isoformat(),
            "expires_at": export_info["expires_at"].isoformat()
        }
    
    def download_export(self, export_id, file_type="single"):
        """Download export file(s)"""
        if export_id not in self.exports_storage:
            return None, None

        export_info = self.exports_storage[export_id]

        # For multi-file exports, automatically use ZIP if single file requested
        if file_type == "single" and "zip_path" in export_info and "file_content" not in export_info:
            file_type = "zip"

        if file_type == "zip" and "zip_path" in export_info:
            with open(export_info["zip_path"], 'rb') as f:
                return f.read(), export_info["zip_filename"]

        elif file_type == "single" and "file_content" in export_info:
            return export_info["file_content"], export_info["filename"]

        return None, None
    
    def download_batch_file(self, export_id, batch_number):
        """Download specific batch file"""
        if export_id not in self.exports_storage:
            return None, None
        
        export_info = self.exports_storage[export_id]
        
        if "files_info" in export_info:
            for file_info in export_info["files_info"]:
                if file_info["batch_number"] == batch_number:
                    with open(file_info["file_path"], 'rb') as f:
                        return f.read(), file_info["file_name"]
        
        return None, None
    
    def _should_run_cleanup(self):
        """Check if cleanup should run based on time interval"""
        current_time = datetime.now()
        time_since_last_cleanup = (current_time - self.last_cleanup_time).total_seconds() / 60  # in minutes
        
        return time_since_last_cleanup >= self.cleanup_interval_minutes

    def _cleanup_old_exports(self):
        """Clean up old exports while respecting minimum age and time intervals"""
        if not self.exports_storage:
            return
            
        try:
            # Update last cleanup time
            self.last_cleanup_time = datetime.now()
            current_time = datetime.now()
            
            # Sort exports by creation time (newest first)
            exports_by_time = sorted(
                self.exports_storage.items(), 
                key=lambda x: x[1].get("created_at", datetime.min), 
                reverse=True
            )
            
            # Filter out exports that are too young to cleanup
            cleanable_exports = []
            protected_exports = []
            
            for export_id, export_info in exports_by_time:
                created_at = export_info.get("created_at", datetime.min)
                age_minutes = (current_time - created_at).total_seconds() / 60
                
                if age_minutes >= self.min_export_age_minutes:
                    cleanable_exports.append((export_id, export_info))
                else:
                    protected_exports.append((export_id, export_info))
            
            # Calculate how many we can keep
            total_exports = len(cleanable_exports) + len(protected_exports)
            
            # Only cleanup if we exceed the limit and have cleanable exports
            if total_exports > self.max_concurrent_exports and cleanable_exports:
                # Keep all protected exports + some cleanable ones
                keep_cleanable_count = max(0, self.max_concurrent_exports - len(protected_exports))
                exports_to_remove = cleanable_exports[keep_cleanable_count:]
                
                if exports_to_remove:
                    logger.info(f"Cleaning up {len(exports_to_remove)} old exports (total: {total_exports}, limit: {self.max_concurrent_exports}, protected: {len(protected_exports)})")
                    
                    for export_id, export_info in exports_to_remove:
                        age_minutes = (current_time - export_info.get('created_at', datetime.min)).total_seconds() / 60
                        logger.info(f"Cleaning up export {export_id} (age: {age_minutes:.1f} minutes)")
                        self._cleanup_export(export_id)
                        
        except Exception as e:
            logger.error(f"Error during old exports cleanup: {str(e)}")

    def _old_cleanup_old_exports(self):
        """Clean up old exports to maintain only the most recent ones"""
        try:
            # Get list of exports sorted by creation time (newest first)
            exports_by_time = sorted(
                self.exports_storage.items(), 
                key=lambda x: x[1].get("created_at", datetime.min), 
                reverse=True
            )
            
            # If we have more exports than the limit, clean up the old ones
            if len(exports_by_time) >= self.max_concurrent_exports:
                exports_to_remove = exports_by_time[self.max_concurrent_exports-1:]  # Keep one slot for new export
                
                for export_id, export_info in exports_to_remove:
                    logger.info(f"Cleaning up old export: {export_id}")
                    self._cleanup_export(export_id)
                    
        except Exception as e:
            logger.error(f"Error during old exports cleanup: {str(e)}")
    
    def _cleanup_export(self, export_id):
        """Clean up export files and data"""
        if export_id not in self.exports_storage:
            return
            
        export_info = self.exports_storage[export_id]
        files_cleaned = 0
        
        try:
            # Clean up temp files
            if "temp_files" in export_info:
                for temp_file in export_info["temp_files"]:
                    try:
                        if os.path.exists(temp_file):
                            os.remove(temp_file)
                            files_cleaned += 1
                            logger.debug(f"Deleted temp file: {temp_file}")
                    except Exception as e:
                        logger.warning(f"Failed to delete temp file {temp_file}: {str(e)}")
            
            # Clean up ZIP file
            if "zip_path" in export_info:
                try:
                    if os.path.exists(export_info["zip_path"]):
                        os.remove(export_info["zip_path"])
                        files_cleaned += 1
                        logger.debug(f"Deleted ZIP file: {export_info['zip_path']}")
                except Exception as e:
                    logger.warning(f"Failed to delete ZIP file {export_info['zip_path']}: {str(e)}")
                    
            # Clean up individual batch files (if stored separately)
            if "files_info" in export_info:
                for file_info in export_info["files_info"]:
                    file_path = file_info.get("file_path")
                    if file_path and os.path.exists(file_path):
                        try:
                            os.remove(file_path)
                            files_cleaned += 1
                            logger.debug(f"Deleted batch file: {file_path}")
                        except Exception as e:
                            logger.warning(f"Failed to delete batch file {file_path}: {str(e)}")
            
            # Remove from storage
            del self.exports_storage[export_id]
            
            logger.info(f"Cleaned up export {export_id}: {files_cleaned} files deleted")
            
        except Exception as e:
            logger.error(f"Error cleaning up export {export_id}: {str(e)}")
            # Still try to remove from storage even if file cleanup failed
            if export_id in self.exports_storage:
                del self.exports_storage[export_id]
    
    def cleanup_expired_exports(self):
        """Clean up all expired exports"""
        expired_exports = []
        current_time = datetime.now()
        
        for export_id, export_info in self.exports_storage.items():
            if current_time > export_info["expires_at"]:
                expired_exports.append(export_id)
        
        for export_id in expired_exports:
            logger.info(f"Cleaning up expired export: {export_id}")
            self._cleanup_export(export_id)
        
        logger.info(f"Cleaned up {len(expired_exports)} expired exports")
        return len(expired_exports)
    
    def force_cleanup_all_exports(self):
        """Force cleanup of all exports (admin function)"""
        export_ids = list(self.exports_storage.keys())
        
        for export_id in export_ids:
            self._cleanup_export(export_id)
        
        logger.info(f"Force cleaned up {len(export_ids)} exports")
        return len(export_ids)
    
    def get_storage_info(self):
        """Get information about current storage usage"""
        total_exports = len(self.exports_storage)
        total_files = 0
        total_size = 0
        
        for export_info in self.exports_storage.values():
            # Count temp files
            if "temp_files" in export_info:
                for temp_file in export_info["temp_files"]:
                    if os.path.exists(temp_file):
                        total_files += 1
                        try:
                            total_size += os.path.getsize(temp_file)
                        except:
                            pass
            
            # Count ZIP files
            if "zip_path" in export_info and os.path.exists(export_info["zip_path"]):
                total_files += 1
                try:
                    total_size += os.path.getsize(export_info["zip_path"])
                except:
                    pass
        
        return {
            "total_exports": total_exports,
            "total_files": total_files,
            "total_size_bytes": total_size,
            "total_size_mb": round(total_size / (1024 * 1024), 2),
            "max_concurrent_exports": self.max_concurrent_exports
        }
