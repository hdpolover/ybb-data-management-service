"""
Database Query Builder for YBB Exports
Builds secure, optimized SQL queries for export operations
"""
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, date

logger = logging.getLogger(__name__)

class YBBQueryBuilder:
    """Builds SQL queries for YBB export operations"""
    
    # Define table mappings and allowed fields for security
    TABLE_CONFIGS = {
        'participants': {
            'table': 'participants',
            'primary_key': 'id',
            'allowed_fields': [
                'id', 'user_id', 'account_id', 'full_name', 'birthdate', 'gender',
                'nationality', 'nationality_flag', 'nationality_code', 'occupation', 
                'education_level', 'major', 'institution', 'organizations',
                'phone_number', 'phone_flag', 'country_code', 'current_address', 'origin_address',
                'picture_url', 'instagram_account', 'emergency_account', 'emergency_country_code',
                'emergency_phone_flag', 'contact_relation', 'disease_history', 'tshirt_size', 
                'category', 'experiences', 'achievements', 'resume_url', 'knowledge_source', 
                'source_account_name', 'twibbon_link', 'requirement_link', 'ref_code_ambassador', 
                'program_id', 'score_total', 'score_status', 'is_active', 'is_deleted', 
                'created_at', 'updated_at'
            ],
            'joins': {
                'users': 'LEFT JOIN users ON participants.user_id = users.id',
                'payments': 'LEFT JOIN payments ON participants.id = payments.participant_id',
                'programs': 'LEFT JOIN programs ON participants.program_id = programs.id'
            }
        },
        'payments': {
            'table': 'payments',
            'primary_key': 'id',
            'allowed_fields': [
                'id', 'transaction_code', 'order_id', 'participant_id', 'program_payment_id',
                'payment_method_id', 'payment_url', 'payment_date', 'status', 'proof_url',
                'account_name', 'amount', 'usd_amount', 'currency', 'source_name', 'notes',
                'rejection_reason', 'is_active', 'is_deleted', 'created_at', 'updated_at'
            ],
            'joins': {
                'participants': 'LEFT JOIN participants ON payments.participant_id = participants.id'
            }
        },
        'ambassadors': {
            'table': 'ambassadors',
            'primary_key': 'id',
            'allowed_fields': [
                'id', 'name', 'email', 'phone_number', 'ref_code', 'program_id',
                'institution', 'gender', 'notes', 'is_active', 'is_deleted', 
                'created_at', 'updated_at'
            ]
        }
    }
    
    def __init__(self):
        self.query_cache = {}
    
    def build_export_query(self, 
                          export_type: str, 
                          template_fields: List[str],
                          filters: Dict[str, Any] = None,
                          limit: Optional[int] = None,
                          offset: Optional[int] = None,
                          order_by: Optional[str] = None) -> tuple:
        """
        Build secure SQL query for export operations
        Returns: (query_string, parameters_dict)
        """
        try:
            # Validate export type
            if export_type not in self.TABLE_CONFIGS:
                raise ValueError(f"Invalid export type: {export_type}")
            
            table_config = self.TABLE_CONFIGS[export_type]
            
            # Validate and sanitize fields
            safe_fields = self._validate_fields(template_fields, table_config['allowed_fields'])
            
            # Build SELECT clause
            select_clause = f"SELECT {', '.join(safe_fields)}"
            
            # Build FROM clause with joins if needed
            from_clause = f"FROM {table_config['table']}"
            
            # Add joins if template requires fields from other tables
            join_clause = self._build_joins(safe_fields, table_config)
            if join_clause:
                from_clause += f" {join_clause}"
            
            # Build WHERE clause
            where_clause, params = self._build_where_clause(filters or {}, table_config)
            
            # Build ORDER BY clause
            order_clause = self._build_order_clause(order_by, table_config)
            
            # Build LIMIT/OFFSET clause
            limit_clause, limit_params = self._build_limit_clause(limit, offset)
            params.update(limit_params)
            
            # Combine all clauses
            query_parts = [select_clause, from_clause]
            if where_clause:
                query_parts.append(where_clause)
            if order_clause:
                query_parts.append(order_clause)
            if limit_clause:
                query_parts.append(limit_clause)
            
            query = " ".join(query_parts)
            
            logger.info(f"Built export query for {export_type}: {len(safe_fields)} fields, {len(params)} parameters")
            
            return query, params
            
        except Exception as e:
            logger.error(f"Error building export query: {e}")
            raise
    
    def build_count_query(self, 
                         export_type: str,
                         filters: Dict[str, Any] = None) -> tuple:
        """Build COUNT query to get total records"""
        try:
            table_config = self.TABLE_CONFIGS[export_type]
            
            # Simple count query
            query = f"SELECT COUNT(*) as total FROM {table_config['table']}"
            
            # Add WHERE clause if filters provided
            where_clause, params = self._build_where_clause(filters or {}, table_config)
            if where_clause:
                query += f" {where_clause}"
            
            return query, params
            
        except Exception as e:
            logger.error(f"Error building count query: {e}")
            raise
    
    def _validate_fields(self, requested_fields: List[str], allowed_fields: List[str]) -> List[str]:
        """Validate and sanitize field names for security"""
        safe_fields = []
        for field in requested_fields:
            # Remove any potential SQL injection characters
            clean_field = field.replace(';', '').replace('--', '').replace('/*', '').replace('*/', '')
            
            if clean_field in allowed_fields:
                safe_fields.append(clean_field)
            else:
                logger.warning(f"Skipping invalid field: {field}")
        
        if not safe_fields:
            # Fallback to basic fields if none are valid
            safe_fields = ['id', 'created_at']
        
        return safe_fields
    
    def _build_joins(self, fields: List[str], table_config: Dict) -> str:
        """Build JOIN clauses based on required fields"""
        joins = []
        join_configs = table_config.get('joins', {})
        
        # For now, keep it simple - add logic later if you need cross-table fields
        # This can be extended based on your actual schema relationships
        
        return " ".join(joins)
    
    def _build_where_clause(self, filters: Dict[str, Any], table_config: Dict) -> tuple:
        """Build WHERE clause with parameter binding for security"""
        conditions = []
        params = {}
        
        # Always exclude soft-deleted records if applicable
        if 'is_deleted' in table_config['allowed_fields']:
            conditions.append("is_deleted = %(is_deleted)s")
            params['is_deleted'] = 0
        
        # Process filter conditions
        for field, value in filters.items():
            if field not in table_config['allowed_fields']:
                logger.warning(f"Skipping invalid filter field: {field}")
                continue
            
            param_name = f"filter_{field}"
            
            if isinstance(value, list):
                # IN clause for multiple values
                placeholders = []
                for i, v in enumerate(value):
                    placeholder = f"{param_name}_{i}"
                    placeholders.append(f"%({placeholder})s")
                    params[placeholder] = v
                conditions.append(f"{field} IN ({', '.join(placeholders)})")
            
            elif isinstance(value, dict):
                # Handle range queries, operators, etc.
                if 'min' in value and 'max' in value:
                    conditions.append(f"{field} BETWEEN %({param_name}_min)s AND %({param_name}_max)s")
                    params[f"{param_name}_min"] = value['min']
                    params[f"{param_name}_max"] = value['max']
                elif 'operator' in value:
                    op = value.get('operator', '=')
                    if op in ['=', '!=', '>', '<', '>=', '<=', 'LIKE']:
                        conditions.append(f"{field} {op} %({param_name})s")
                        params[param_name] = value.get('value', '')
            
            else:
                # Simple equality
                conditions.append(f"{field} = %({param_name})s")
                params[param_name] = value
        
        where_clause = ""
        if conditions:
            where_clause = f"WHERE {' AND '.join(conditions)}"
        
        return where_clause, params
    
    def _build_order_clause(self, order_by: Optional[str], table_config: Dict) -> str:
        """Build ORDER BY clause"""
        if not order_by:
            # Default ordering by primary key
            return f"ORDER BY {table_config['primary_key']} ASC"
        
        # Sanitize order_by field
        parts = order_by.split()
        field = parts[0]
        direction = parts[1].upper() if len(parts) > 1 else 'ASC'
        
        if field in table_config['allowed_fields'] and direction in ['ASC', 'DESC']:
            return f"ORDER BY {field} {direction}"
        
        # Fallback to default ordering
        return f"ORDER BY {table_config['primary_key']} ASC"
    
    def _build_limit_clause(self, limit: Optional[int], offset: Optional[int]) -> tuple:
        """Build LIMIT/OFFSET clause"""
        params = {}
        clauses = []
        
        if offset is not None and offset > 0:
            clauses.append("OFFSET %(query_offset)s")
            params['query_offset'] = offset
        
        if limit is not None and limit > 0:
            clauses.append("LIMIT %(query_limit)s")
            params['query_limit'] = limit
        
        return " ".join(clauses), params

# Global query builder instance
query_builder = YBBQueryBuilder()

# Convenience function
def build_export_query(export_type: str, template_fields: List[str], **kwargs):
    """Build export query - convenience function"""
    return query_builder.build_export_query(export_type, template_fields, **kwargs)

def build_count_query(export_type: str, **kwargs):
    """Build count query - convenience function"""
    return query_builder.build_count_query(export_type, **kwargs)