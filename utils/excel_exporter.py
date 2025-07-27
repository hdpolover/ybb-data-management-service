"""
Excel export utilities for YBB Data Management API
"""
import pandas as pd
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.utils.dataframe import dataframe_to_rows
from io import BytesIO
import logging
import re
import unicodedata

logger = logging.getLogger(__name__)

class ExcelExporter:
    """Handle Excel export operations with advanced formatting and data sanitization"""
    
    @staticmethod
    def sanitize_cell_value(value):
        """
        Sanitize cell values for Excel compatibility
        
        Args:
            value: Raw cell value
            
        Returns:
            Sanitized value safe for Excel
        """
        if value is None:
            return ""
        
        # Convert to string
        str_value = str(value)
        
        # Handle empty strings
        if not str_value.strip():
            return ""
        
        # Remove or replace problematic characters for Excel
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
        
        # Normalize Unicode characters
        try:
            cleaned_value = unicodedata.normalize('NFKC', cleaned_value)
        except Exception:
            # If normalization fails, try to encode/decode to remove problematic characters
            try:
                cleaned_value = cleaned_value.encode('utf-8', errors='ignore').decode('utf-8')
            except Exception:
                cleaned_value = str(value)  # Fallback to original string conversion
        
        # Remove excessive whitespace
        cleaned_value = re.sub(r'\s+', ' ', cleaned_value).strip()
        
        # Excel cell limit (32,767 characters)
        if len(cleaned_value) > 32767:
            cleaned_value = cleaned_value[:32764] + "..."
        
        return cleaned_value
    
    @staticmethod
    def sanitize_dataframe(df):
        """
        Sanitize entire DataFrame for Excel compatibility
        
        Args:
            df: Pandas DataFrame
            
        Returns:
            Sanitized DataFrame
        """
        df_copy = df.copy()
        
        # Sanitize column names
        sanitized_columns = []
        for col in df_copy.columns:
            sanitized_col = ExcelExporter.sanitize_cell_value(col)
            # Ensure column name is not empty
            if not sanitized_col:
                sanitized_col = "Column"
            sanitized_columns.append(sanitized_col)
        
        df_copy.columns = sanitized_columns
        
        # Sanitize all cell values
        for col in df_copy.columns:
            df_copy[col] = df_copy[col].apply(ExcelExporter.sanitize_cell_value)
        
        return df_copy
    
    @staticmethod
    def create_excel_file(data, filename=None, sheet_name="Data", format_options=None):
        """
        Create Excel file from data with formatting options and data sanitization
        
        Args:
            data: List of dictionaries or pandas DataFrame
            filename: Output filename
            sheet_name: Excel sheet name
            format_options: Dictionary with formatting options
        
        Returns:
            BytesIO object containing Excel file
        """
        try:
            # Convert to DataFrame if needed
            if isinstance(data, list):
                df = pd.DataFrame(data)
            else:
                df = data.copy()
            
            if df.empty:
                raise ValueError("No data to export")
            
            # Sanitize the DataFrame
            df = ExcelExporter.sanitize_dataframe(df)
            
            # Sanitize sheet name
            sheet_name = ExcelExporter.sanitize_cell_value(sheet_name)
            if not sheet_name:
                sheet_name = "Data"
            
            # Excel sheet name limitations
            sheet_name = re.sub(r'[\\/*\[\]:?]', '_', sheet_name)  # Replace invalid characters
            if len(sheet_name) > 31:
                sheet_name = sheet_name[:31]
            
            # Create Excel file in memory using openpyxl
            output = BytesIO()
            wb = Workbook()
            ws = wb.active
            ws.title = sheet_name
            
            # Write data to worksheet with proper error handling
            try:
                # Add headers
                for col_num, header in enumerate(df.columns, 1):
                    cell = ws.cell(row=1, column=col_num)
                    cell.value = header
                
                # Add data rows
                for row_num, row_data in enumerate(df.itertuples(index=False), 2):
                    for col_num, value in enumerate(row_data, 1):
                        cell = ws.cell(row=row_num, column=col_num)
                        cell.value = value
                        
            except Exception as e:
                logger.warning(f"Error writing data to Excel, falling back to dataframe_to_rows: {str(e)}")
                # Fallback method
                ws.delete_rows(1, ws.max_row)  # Clear existing data
                for r in dataframe_to_rows(df, index=False, header=True):
                    # Sanitize each row value
                    sanitized_row = [ExcelExporter.sanitize_cell_value(cell) for cell in r]
                    ws.append(sanitized_row)
            
            # Apply formatting if specified
            if format_options:
                ExcelExporter._apply_formatting(ws, df, format_options)
            else:
                # Apply default formatting
                ExcelExporter._apply_default_formatting(ws, df)
            
            # Save to BytesIO with error handling
            try:
                wb.save(output)
                output.seek(0)
            except Exception as e:
                logger.error(f"Failed to save Excel file: {str(e)}")
                # Try to create a basic Excel file without formatting
                output = BytesIO()
                with pd.ExcelWriter(output, engine='openpyxl', options={'remove_timezone': True}) as writer:
                    df.to_excel(writer, sheet_name=sheet_name, index=False)
                output.seek(0)
            
            logger.info(f"Excel file created successfully with {len(df)} rows")
            return output
            
        except Exception as e:
            logger.error(f"Excel export failed: {str(e)}")
            raise Exception(f"Excel export failed: {str(e)}")
    
    @staticmethod
    def _apply_default_formatting(worksheet, dataframe):
        """Apply default formatting to Excel worksheet with error handling"""
        try:
            # Header formatting
            header_font = Font(bold=True, color="FFFFFF")
            header_fill = PatternFill(start_color="366092", end_color="366092", fill_type="solid")
            header_alignment = Alignment(horizontal="center", vertical="center")
            
            # Apply header formatting
            for col_num, column in enumerate(dataframe.columns, 1):
                try:
                    cell = worksheet.cell(row=1, column=col_num)
                    cell.font = header_font
                    cell.fill = header_fill
                    cell.alignment = header_alignment
                except Exception as e:
                    logger.warning(f"Failed to format header cell {col_num}: {str(e)}")
            
            # Auto-adjust column widths with error handling
            ExcelExporter._adjust_column_widths_safe(worksheet)
            
        except Exception as e:
            logger.warning(f"Failed to apply default formatting: {str(e)}")
    
    @staticmethod
    def _adjust_column_widths_safe(worksheet):
        """Auto-adjust column widths with comprehensive error handling"""
        try:
            for column_cells in worksheet.columns:
                max_length = 0
                column_letter = None
                
                for cell in column_cells:
                    try:
                        if cell.value is not None:
                            cell_length = len(str(cell.value))
                            if cell_length > max_length:
                                max_length = cell_length
                        
                        # Get column letter from first cell
                        if column_letter is None:
                            column_letter = cell.column_letter
                            
                    except Exception as e:
                        logger.debug(f"Error processing cell in column width adjustment: {str(e)}")
                        continue
                
                # Set column width with reasonable limits
                if column_letter and max_length > 0:
                    try:
                        adjusted_width = min(max_length + 2, 50)  # Cap at 50 characters
                        adjusted_width = max(adjusted_width, 8)   # Minimum width of 8
                        worksheet.column_dimensions[column_letter].width = adjusted_width
                    except Exception as e:
                        logger.debug(f"Failed to set width for column {column_letter}: {str(e)}")
                        
        except Exception as e:
            logger.warning(f"Column width adjustment failed: {str(e)}")
    
    @staticmethod
    def _apply_formatting(worksheet, dataframe, format_options):
        """Apply custom formatting based on format_options with error handling"""
        try:
            # Header formatting
            if format_options.get('header_style'):
                header_style = format_options['header_style']
                
                try:
                    header_font = Font(
                        bold=header_style.get('bold', True),
                        color=header_style.get('font_color', "FFFFFF")
                    )
                    header_fill = PatternFill(
                        start_color=header_style.get('bg_color', "366092"),
                        end_color=header_style.get('bg_color', "366092"),
                        fill_type="solid"
                    )
                    
                    for col_num in range(1, len(dataframe.columns) + 1):
                        try:
                            cell = worksheet.cell(row=1, column=col_num)
                            cell.font = header_font
                            cell.fill = header_fill
                        except Exception as e:
                            logger.debug(f"Failed to format header cell {col_num}: {str(e)}")
                            
                except Exception as e:
                    logger.warning(f"Failed to create header formatting styles: {str(e)}")
            
            # Column width adjustment
            if format_options.get('auto_width', True):
                ExcelExporter._adjust_column_widths_safe(worksheet)
            
            # Custom column widths
            if format_options.get('column_widths'):
                try:
                    for col, width in format_options['column_widths'].items():
                        if col in dataframe.columns:
                            col_index = list(dataframe.columns).index(col) + 1
                            column_letter = worksheet.cell(row=1, column=col_index).column_letter
                            worksheet.column_dimensions[column_letter].width = width
                except Exception as e:
                    logger.warning(f"Failed to apply custom column widths: {str(e)}")
                    
        except Exception as e:
            logger.warning(f"Custom formatting failed: {str(e)}")
    
    @staticmethod
    def _adjust_column_widths(worksheet):
        """Auto-adjust column widths - kept for backward compatibility"""
        ExcelExporter._adjust_column_widths_safe(worksheet)
