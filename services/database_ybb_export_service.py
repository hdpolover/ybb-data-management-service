"""
Database-integrated YBB Export Service
Connects directly to the database to fetch and export data
"""
import os
import mysql.connector
from mysql.connector import Error
import pandas as pd
import logging
from datetime import datetime, timedelta
from services.ybb_export_service import YBBExportService

logger = logging.getLogger('ybb_api.db_service')

class DatabaseYBBExportService:
    """
    Enhanced export service with direct database connectivity
    Frontend only sends filters and options, backend handles data retrieval
    """
    
    def __init__(self):
        self.export_service = YBBExportService()
        self.db_config = {
            'host': os.getenv('DB_HOST', 'localhost'),
            'port': int(os.getenv('DB_PORT', 3306)),
            'user': os.getenv('DB_USER', 'root'),
            'password': os.getenv('DB_PASSWORD', ''),
            'database': os.getenv('DB_NAME', 'ybb_database'),
            'charset': 'utf8mb4',
            'autocommit': True
        }
        
    def get_database_connection(self):
        """Get database connection"""
        try:
            connection = mysql.connector.connect(**self.db_config)
            if connection.is_connected():
                return connection
        except Error as e:
            logger.error(f"Database connection error: {e}")
            raise Exception(f"Database connection failed: {e}")
    
    def export_participants_from_db(self, filters=None, options=None):
        """
        Export participants directly from database
        
        Args:
            filters (dict): Filter criteria for participants
            options (dict): Export configuration options
            
        Returns:
            dict: Export result with download information
        """
        filters = filters or {}
        options = options or {}
        
        # Default export options
        export_config = {
            'template': options.get('template', 'standard'),
            'format': options.get('format', 'excel'),
            'filename': options.get('filename'),
            'sheet_name': options.get('sheet_name', 'Participants Data'),
            'include_related': options.get('include_related', True)
        }
        
        try:
            logger.info(f"Starting participants export from database with filters: {filters}")
            
            # Fetch participants data from database
            participants_data = self._fetch_participants_data(filters, export_config)
            
            if not participants_data:
                return {
                    'status': 'error',
                    'message': 'No participants found matching the specified criteria'
                }
            
            logger.info(f"Fetched {len(participants_data)} participants from database")
            
            # Generate filename if not provided
            if not export_config['filename']:
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                export_config['filename'] = f"YBB_Participants_Export_{timestamp}.xlsx"
            
            # Create export payload for the export service
            export_payload = {
                'data': participants_data,
                'template': export_config['template'],
                'format': export_config['format'],
                'filename': export_config['filename'],
                'sheet_name': export_config['sheet_name'],
                'export_type': 'participants'
            }
            
            # Use existing export service to create the file
            result = self.export_service.create_export(export_payload)
            
            if result['status'] == 'success':
                logger.info(f"Participants export completed successfully: {result['data']['export_id']}")
            
            return result
            
        except Exception as e:
            logger.error(f"Participants export from database failed: {str(e)}")
            return {
                'status': 'error',
                'message': f'Export failed: {str(e)}'
            }
    
    def export_payments_from_db(self, filters=None, options=None):
        """Export payments directly from database"""
        filters = filters or {}
        options = options or {}
        
        export_config = {
            'template': options.get('template', 'standard'),
            'format': options.get('format', 'excel'),
            'filename': options.get('filename'),
            'sheet_name': options.get('sheet_name', 'Payments Data'),
            'include_related': options.get('include_related', True)
        }
        
        try:
            logger.info(f"Starting payments export from database with filters: {filters}")
            
            # Fetch payments data from database
            payments_data = self._fetch_payments_data(filters, export_config)
            
            if not payments_data:
                return {
                    'status': 'error',
                    'message': 'No payments found matching the specified criteria'
                }
            
            logger.info(f"Fetched {len(payments_data)} payments from database")
            
            # Generate filename if not provided
            if not export_config['filename']:
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                export_config['filename'] = f"YBB_Payments_Export_{timestamp}.xlsx"
            
            # Create export payload
            export_payload = {
                'data': payments_data,
                'template': export_config['template'],
                'format': export_config['format'],
                'filename': export_config['filename'],
                'sheet_name': export_config['sheet_name'],
                'export_type': 'payments'
            }
            
            # Use existing export service to create the file
            result = self.export_service.create_export(export_payload)
            
            if result['status'] == 'success':
                logger.info(f"Payments export completed successfully: {result['data']['export_id']}")
            
            return result
            
        except Exception as e:
            logger.error(f"Payments export from database failed: {str(e)}")
            return {
                'status': 'error',
                'message': f'Export failed: {str(e)}'
            }
    
    def _fetch_participants_data(self, filters, config):
        """Fetch participants data from database with filters"""
        connection = None
        try:
            connection = self.get_database_connection()
            cursor = connection.cursor(dictionary=True)
            
            # Base query for participants (correct schema with users table join)
            base_query = """
            SELECT DISTINCT
                p.id,
                p.user_id,
                p.account_id,
                p.full_name,
                u.email,
                p.birthdate,
                p.gender,
                p.nationality,
                p.nationality_code,
                p.nationality_flag,
                CONCAT(COALESCE(p.country_code, ''), ' ', COALESCE(p.phone_number, '')) as phone,
                p.phone_number,
                p.country_code,
                p.phone_flag,
                p.origin_address,
                p.current_address,
                p.institution,
                p.major,
                p.occupation,
                p.education_level,
                p.organizations,
                p.picture_url,
                p.instagram_account,
                p.emergency_account,
                CONCAT(COALESCE(p.emergency_country_code, ''), ' ', COALESCE(p.emergency_account, '')) as emergency_contact,
                p.emergency_country_code,
                p.emergency_phone_flag,
                p.contact_relation,
                p.disease_history,
                p.tshirt_size,
                p.category,
                p.experiences,
                p.achievements,
                p.resume_url,
                p.knowledge_source,
                p.source_account_name,
                p.twibbon_link,
                p.requirement_link,
                p.ref_code_ambassador,
                p.program_id,
                p.score_status,
                p.score_total,
                p.is_active,
                p.is_deleted,
                p.created_at,
                p.updated_at,
                ps.form_status,
                CASE 
                    WHEN EXISTS (
                        SELECT 1 FROM payments pay 
                        WHERE pay.participant_id = p.id 
                        AND pay.status = 2 
                        AND pay.is_active = 1 
                        AND pay.is_deleted = 0
                    ) THEN 2
                    ELSE 0
                END as payment_status,
                CASE 
                    WHEN EXISTS (
                        SELECT 1 FROM payments pay 
                        WHERE pay.participant_id = p.id 
                        AND pay.status = 2 
                        AND pay.is_active = 1 
                        AND pay.is_deleted = 0
                    ) THEN 'Yes'
                    ELSE 'No'
                END as has_successful_payment,
                (
                    SELECT COUNT(*) FROM payments pay
                    WHERE pay.participant_id = p.id
                    AND pay.status = 2
                    AND pay.is_active = 1
                    AND pay.is_deleted = 0
                ) as successful_payment_count,
                (
                    SELECT SUM(pay.amount) FROM payments pay
                    WHERE pay.participant_id = p.id
                    AND pay.status = 2
                    AND pay.is_active = 1
                    AND pay.is_deleted = 0
                ) as total_paid_amount
            """
            
            # Include related data if requested
            if config.get('include_related', True):
                base_query += """,
                prog.name as program_name,
                prog.theme as program_theme,
                prog.start_date as program_start_date,
                prog.end_date as program_end_date,
                prog.program_category_id,
                (
                    SELECT GROUP_CONCAT(
                        CONCAT(pay.amount, ' ', pay.currency, ' (', 
                        CASE pay.status
                            WHEN 0 THEN 'Pending'
                            WHEN 1 THEN 'Processing'
                            WHEN 2 THEN 'Success'
                            WHEN 3 THEN 'Failed'
                            WHEN 4 THEN 'Cancelled'
                        END, ')')
                        SEPARATOR '; '
                    )
                    FROM payments pay
                    WHERE pay.participant_id = p.id
                    AND pay.is_active = 1
                    AND pay.is_deleted = 0
                ) as payment_details
                """
            
            base_query += " FROM participants p"
            base_query += " LEFT JOIN users u ON p.user_id = u.id AND u.is_active = 1 AND u.is_deleted = 0"
            base_query += " LEFT JOIN participant_statuses ps ON p.id = ps.participant_id AND ps.is_active = 1 AND ps.is_deleted = 0"
            
            # Add joins for related data
            if config.get('include_related', True):
                base_query += " LEFT JOIN programs prog ON p.program_id = prog.id AND prog.is_active = 1 AND prog.is_deleted = 0"
            
            # Build WHERE clause based on filters
            where_conditions = ["p.is_active = 1", "p.is_deleted = 0"]
            params = []
            
            if filters.get('program_id'):
                where_conditions.append("p.program_id = %s")
                params.append(filters['program_id'])
            
            if filters.get('status'):
                if filters['status'] != 'all':
                    if filters['status'] in ['go_to_interview', 'rejected', 'no_score']:
                        where_conditions.append("p.score_status = %s")
                        params.append(filters['status'])
                    else:
                        # Assume it's a general status filter
                        where_conditions.append("ps.general_status = %s")
                        params.append(int(filters['status']))
            
            if filters.get('country'):
                where_conditions.append("p.nationality = %s")
                params.append(filters['country'])
            
            if filters.get('category'):
                where_conditions.append("p.category = %s")
                params.append(filters['category'])
            
            if filters.get('date_from'):
                where_conditions.append("p.created_at >= %s")
                params.append(filters['date_from'])
            
            if filters.get('date_to'):
                where_conditions.append("p.created_at <= %s")
                params.append(filters['date_to'] + ' 23:59:59')
            
            if filters.get('search'):
                where_conditions.append("(p.full_name LIKE %s OR u.email LIKE %s)")
                search_term = f"%{filters['search']}%"
                params.extend([search_term, search_term])
            
            # Filter for participants who have submitted registration forms
            if filters.get('has_submitted_form'):
                if filters['has_submitted_form'] == 'yes' or filters['has_submitted_form'] is True:
                    where_conditions.append("ps.form_status = 2")
                elif filters['has_submitted_form'] == 'no' or filters['has_submitted_form'] is False:
                    where_conditions.append("(ps.form_status IS NULL OR ps.form_status != 2)")
            
            # Filter for participants who have made successful payments
            if filters.get('has_paid'):
                if filters['has_paid'] == 'yes' or filters['has_paid'] is True:
                    where_conditions.append("EXISTS (SELECT 1 FROM payments pay_check WHERE pay_check.participant_id = p.id AND pay_check.status = 2)")
                elif filters['has_paid'] == 'no' or filters['has_paid'] is False:
                    where_conditions.append("NOT EXISTS (SELECT 1 FROM payments pay_check WHERE pay_check.participant_id = p.id AND pay_check.status = 2)")
            
            # Filter by registration form status from participant_statuses table
            if filters.get('registration_form_status') is not None:
                if filters['registration_form_status'] == 'all':
                    pass  # No filter
                elif filters['registration_form_status'] == 'not_started':
                    where_conditions.append("(ps.form_status IS NULL OR ps.form_status = 0)")
                elif filters['registration_form_status'] == 'in_progress':
                    where_conditions.append("ps.form_status = 1")
                elif filters['registration_form_status'] == 'submitted':
                    where_conditions.append("ps.form_status = 2")
                else:
                    # If numeric value provided directly
                    where_conditions.append("ps.form_status = %s")
                    params.append(int(filters['registration_form_status']))
            
            # Add WHERE clause if we have conditions
            if where_conditions:
                base_query += " WHERE " + " AND ".join(where_conditions)
            
            # Add ORDER BY (map to actual column names)
            sort_field_mapping = {
                'created_at': 'p.created_at',
                'name': 'p.full_name',
                'email': 'u.email',
                'updated_at': 'p.updated_at',
                'form_status': 'ps.form_status'
            }
            order_by = filters.get('sort_by', 'created_at')
            actual_sort_field = sort_field_mapping.get(order_by, f'p.{order_by}')
            order_direction = filters.get('sort_order', 'desc').upper()
            base_query += f" ORDER BY {actual_sort_field} {order_direction}"
            
            # Add LIMIT if specified
            if filters.get('limit'):
                base_query += " LIMIT %s"
                params.append(filters['limit'])
            
            logger.info(f"Executing participants query with {len(params)} parameters")
            cursor.execute(base_query, params)
            
            participants = cursor.fetchall()
            
            # Convert dates to strings for JSON serialization
            for participant in participants:
                for key, value in participant.items():
                    if isinstance(value, (datetime, )):
                        participant[key] = value.strftime('%Y-%m-%d %H:%M:%S')
                    elif value is None:
                        participant[key] = ''
            
            return participants
            
        except Error as e:
            logger.error(f"Database error while fetching participants: {e}")
            raise Exception(f"Database query failed: {e}")
        finally:
            if connection and connection.is_connected():
                connection.close()
    
    def _fetch_payments_data(self, filters, config):
        """Fetch payments data from database with filters"""
        connection = None
        try:
            connection = self.get_database_connection()
            cursor = connection.cursor(dictionary=True)
            
            # Base query for payments (enhanced with all fields and names instead of IDs)
            base_query = """
            SELECT 
                pay.id,
                pay.transaction_code,
                pay.order_id,
                pay.participant_id,
                p.full_name as participant_name,
                u.email as participant_email,
                pay.program_payment_id,
                pp.name as program_payment_name,
                pp.category as payment_category,
                pp.type as payment_type,
                pay.payment_method_id,
                pm.name as payment_method,
                pay.amount,
                pay.usd_amount,
                pay.currency,
                pay.status,
                CASE pay.status
                    WHEN 0 THEN 'Pending'
                    WHEN 1 THEN 'Processing'
                    WHEN 2 THEN 'Success'
                    WHEN 3 THEN 'Failed'
                    WHEN 4 THEN 'Cancelled'
                    ELSE 'Unknown'
                END as status_text,
                pay.payment_date,
                pay.payment_url,
                pay.proof_url,
                pay.account_name,
                pay.source_name,
                pay.notes,
                pay.rejection_reason,
                pay.created_at,
                pay.updated_at,
                prog.name as program_name,
                prog.theme as program_theme
            """
            
            base_query += " FROM payments pay"
            base_query += " LEFT JOIN participants p ON pay.participant_id = p.id"
            base_query += " LEFT JOIN users u ON p.user_id = u.id"
            base_query += " LEFT JOIN payment_methods pm ON pay.payment_method_id = pm.id"
            base_query += " LEFT JOIN program_payments pp ON pay.program_payment_id = pp.id"
            base_query += " LEFT JOIN programs prog ON p.program_id = prog.id"
            
            # Build WHERE clause based on filters
            where_conditions = ["pay.is_active = 1", "pay.is_deleted = 0"]
            params = []
            
            if filters.get('participant_id'):
                where_conditions.append("pay.participant_id = %s")
                params.append(filters['participant_id'])
            
            if filters.get('program_id'):
                where_conditions.append("p.program_id = %s")
                params.append(filters['program_id'])
            
            if filters.get('status'):
                if filters['status'] != 'all':
                    where_conditions.append("pay.status = %s")
                    params.append(int(filters['status']))
            
            if filters.get('payment_method_id'):
                where_conditions.append("pay.payment_method_id = %s")
                params.append(filters['payment_method_id'])
            
            if filters.get('date_from'):
                where_conditions.append("pay.payment_date >= %s")
                params.append(filters['date_from'])
            
            if filters.get('date_to'):
                where_conditions.append("pay.payment_date <= %s")
                params.append(filters['date_to'])
            
            if filters.get('amount_min'):
                where_conditions.append("pay.amount >= %s")
                params.append(filters['amount_min'])
            
            if filters.get('amount_max'):
                where_conditions.append("pay.amount <= %s")
                params.append(filters['amount_max'])
            
            # Add WHERE clause if we have conditions
            if where_conditions:
                base_query += " WHERE " + " AND ".join(where_conditions)
            
            # Add ORDER BY with field mapping
            sort_field_mapping = {
                'payment_date': 'pay.payment_date',
                'amount': 'pay.amount',
                'created_at': 'pay.created_at',
                'status': 'pay.status',
                'participant_name': 'p.full_name'
            }
            order_by = filters.get('sort_by', 'payment_date')
            actual_sort_field = sort_field_mapping.get(order_by, f'pay.{order_by}')
            order_direction = filters.get('sort_order', 'desc').upper()
            base_query += f" ORDER BY {actual_sort_field} {order_direction}"
            
            # Add LIMIT if specified
            if filters.get('limit'):
                base_query += " LIMIT %s"
                params.append(filters['limit'])
            
            logger.info(f"Executing payments query with {len(params)} parameters")
            cursor.execute(base_query, params)
            
            payments = cursor.fetchall()
            
            # Convert dates and decimals to strings for JSON serialization
            for payment in payments:
                for key, value in payment.items():
                    if isinstance(value, (datetime, )):
                        payment[key] = value.strftime('%Y-%m-%d %H:%M:%S')
                    elif value is None:
                        payment[key] = ''
                    elif key in ['amount', 'usd_amount'] and value is not None:
                        payment[key] = float(value)
            
            return payments
            
        except Error as e:
            logger.error(f"Database error while fetching payments: {e}")
            raise Exception(f"Database query failed: {e}")
        finally:
            if connection and connection.is_connected():
                connection.close()
    
    def get_export_statistics(self, export_type='participants', filters=None):
        """Get statistics about data before exporting"""
        filters = filters or {}
        connection = None
        
        try:
            connection = self.get_database_connection()
            cursor = connection.cursor(dictionary=True)
            
            if export_type == 'participants':
                count_query = "SELECT COUNT(*) as total FROM participants p LEFT JOIN participant_statuses ps ON p.id = ps.participant_id AND ps.is_active = 1 AND ps.is_deleted = 0"
                status_query = """
                SELECT 
                    ps.form_status, 
                    COUNT(*) as count,
                    p.score_status,
                    COUNT(CASE WHEN p.score_status = 'go_to_interview' THEN 1 END) as interview_count,
                    COUNT(CASE WHEN p.category = 'fully_funded' THEN 1 END) as fully_funded_count
                FROM participants p 
                LEFT JOIN participant_statuses ps ON p.id = ps.participant_id AND ps.is_active = 1 AND ps.is_deleted = 0
                WHERE p.is_active = 1 AND p.is_deleted = 0
                GROUP BY ps.form_status, p.score_status
                """
            elif export_type == 'payments':
                count_query = "SELECT COUNT(*) as total FROM payments pay"
                status_query = """
                SELECT status, COUNT(*) as count, SUM(amount) as total_amount
                FROM payments pay
                GROUP BY status
                """
            
            # Apply filters to count query
            where_conditions = []
            params = []
            
            if filters.get('program_id'):
                if export_type == 'participants':
                    where_conditions.append("p.program_id = %s")
                else:
                    count_query = count_query.replace("FROM payments pay", 
                        "FROM payments pay LEFT JOIN participants p ON pay.participant_id = p.id")
                    status_query = status_query.replace("FROM payments pay", 
                        "FROM payments pay LEFT JOIN participants p ON pay.participant_id = p.id")
                    where_conditions.append("p.program_id = %s")
                params.append(filters['program_id'])
            
            if filters.get('status') and filters['status'] != 'all':
                if export_type == 'participants':
                    if filters['status'] in ['go_to_interview', 'rejected', 'no_score']:
                        where_conditions.append("p.score_status = %s")
                        params.append(filters['status'])
                    else:
                        where_conditions.append("ps.form_status = %s")
                        params.append(int(filters['status']))
                else:
                    where_conditions.append("pay.status = %s")
                    params.append(int(filters['status']))
            
            if filters.get('date_from'):
                date_field = 'p.created_at' if export_type == 'participants' else 'pay.payment_date'
                where_conditions.append(f"{date_field} >= %s")
                params.append(filters['date_from'])
            
            if filters.get('date_to'):
                date_field = 'p.created_at' if export_type == 'participants' else 'pay.payment_date'
                where_conditions.append(f"{date_field} <= %s")
                params.append(filters['date_to'] + ' 23:59:59' if export_type == 'participants' else filters['date_to'])
            
            # Add base WHERE conditions for active/non-deleted records
            base_where_conditions = []
            if export_type == 'participants':
                base_where_conditions.append("p.is_active = 1 AND p.is_deleted = 0")
            else:
                base_where_conditions.append("pay.is_active = 1 AND pay.is_deleted = 0")
            
            # Combine with filter conditions
            all_conditions = base_where_conditions + where_conditions
            
            # Add WHERE clause
            if all_conditions:
                where_clause = " WHERE " + " AND ".join(all_conditions)
                count_query += where_clause
                # Status query already has WHERE clause for participants
                if export_type == 'payments':
                    status_query += where_clause + " GROUP BY pay.status"
                elif export_type == 'participants' and where_conditions:
                    # Update the existing WHERE in status_query
                    status_query = status_query.replace(
                        "WHERE p.is_active = 1 AND p.is_deleted = 0",
                        "WHERE " + " AND ".join(all_conditions)
                    )
            
            # Get total count
            cursor.execute(count_query, params)
            total_result = cursor.fetchone()
            total_count = total_result['total'] if total_result else 0
            
            # Get status breakdown
            cursor.execute(status_query, params)
            status_breakdown = cursor.fetchall()
            
            return {
                'status': 'success',
                'data': {
                    'total_count': total_count,
                    'status_breakdown': status_breakdown,
                    'export_type': export_type,
                    'filters_applied': filters
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting export statistics: {e}")
            return {
                'status': 'error',
                'message': f'Failed to get statistics: {str(e)}'
            }
        finally:
            if connection and connection.is_connected():
                connection.close()
    
    def test_database_connection(self):
        """Test database connectivity"""
        try:
            connection = self.get_database_connection()
            cursor = connection.cursor()
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
            connection.close()
            
            return {
                'status': 'success',
                'message': 'Database connection successful',
                'database': self.db_config['database'],
                'host': self.db_config['host']
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'message': f'Database connection failed: {str(e)}'
            }