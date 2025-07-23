"""
Excel export utilities for YBB Data Management API
"""
import pandas as pd
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.utils.dataframe import dataframe_to_rows
from io import BytesIO
import logging

logger = logging.getLogger(__name__)

class ExcelExporter:
    """Handle Excel export operations with advanced formatting"""
    
    @staticmethod
    def create_excel_file(data, filename=None, sheet_name="Data", format_options=None):
        """
        Create Excel file from data with formatting options
        
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
                df = data
            
            if df.empty:
                raise ValueError("No data to export")
            
            # Create Excel file in memory
            output = BytesIO()
            
            # Use openpyxl for better formatting control
            wb = Workbook()
            ws = wb.active
            ws.title = sheet_name
            
            # Add data to worksheet
            for r in dataframe_to_rows(df, index=False, header=True):
                ws.append(r)
            
            # Apply formatting if specified
            if format_options:
                ExcelExporter._apply_formatting(ws, df, format_options)
            else:
                # Apply default formatting
                ExcelExporter._apply_default_formatting(ws, df)
            
            # Save to BytesIO
            wb.save(output)
            output.seek(0)
            
            logger.info(f"Excel file created successfully with {len(df)} rows")
            return output
            
        except Exception as e:
            logger.error(f"Excel export failed: {str(e)}")
            raise Exception(f"Excel export failed: {str(e)}")
    
    @staticmethod
    def _apply_default_formatting(worksheet, dataframe):
        """Apply default formatting to Excel worksheet"""
        # Header formatting
        header_font = Font(bold=True, color="FFFFFF")
        header_fill = PatternFill(start_color="366092", end_color="366092", fill_type="solid")
        header_alignment = Alignment(horizontal="center", vertical="center")
        
        # Apply header formatting
        for col_num, column in enumerate(dataframe.columns, 1):
            cell = worksheet.cell(row=1, column=col_num)
            cell.font = header_font
            cell.fill = header_fill
            cell.alignment = header_alignment
        
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
            adjusted_width = min(max_length + 2, 50)  # Cap at 50 characters
            worksheet.column_dimensions[column[0].column_letter].width = adjusted_width
    
    @staticmethod
    def _apply_formatting(worksheet, dataframe, format_options):
        """Apply custom formatting based on format_options"""
        # Header formatting
        if format_options.get('header_style'):
            header_style = format_options['header_style']
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
                cell = worksheet.cell(row=1, column=col_num)
                cell.font = header_font
                cell.fill = header_fill
        
        # Column width adjustment
        if format_options.get('auto_width', True):
            ExcelExporter._adjust_column_widths(worksheet)
        
        # Custom column widths
        if format_options.get('column_widths'):
            for col, width in format_options['column_widths'].items():
                if col in dataframe.columns:
                    col_index = list(dataframe.columns).index(col) + 1
                    worksheet.column_dimensions[
                        worksheet.cell(row=1, column=col_index).column_letter
                    ].width = width
    
    @staticmethod
    def _adjust_column_widths(worksheet):
        """Auto-adjust column widths"""
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
