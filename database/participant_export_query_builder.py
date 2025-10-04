"""
Enhanced YBB Query Builder for Participant Export
Builds complex SQL queries for participant export with proper joins and filters
"""
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, date

logger = logging.getLogger(__name__)

class ParticipantExportQueryBuilder:
    """Specialized query builder for participant export requirements"""
    
    def build_participant_export_query(self, 
                                     template_fields: List[str],
                                     filters: Dict[str, Any] = None,
                                     limit: Optional[int] = None,
                                     offset: Optional[int] = None) -> tuple:
        """
        Build comprehensive participant export query based on specifications
        
        Args:
            template_fields: List of fields to select
            filters: Dictionary of filters including:
                - program_id (required)
                - category: self_funded, fully_funded
                - form_status: 0=not started, 1=in_progress, 2=submitted
                - payment_done: array of program payment ids
                - with_essay: boolean (controls data inclusion, not participant filtering)
                - created_at: date range dict with min/max
            limit: Optional limit for pagination
            offset: Optional offset for pagination
            
        Returns:
            Tuple of (query_string, parameters_dict)
        """
        try:
            # Base SELECT with field mapping
            include_essays = (filters or {}).get('with_essay', False)
            select_fields = self._build_select_fields(template_fields, include_essays)
            
            # FROM clause with main joins (conditionally include essay joins)
            include_essays = (filters or {}).get('with_essay', False)
            from_clause = self._build_from_clause(include_essay_joins=include_essays)
            
            # WHERE clause with filters
            where_clause, params = self._build_where_clause(filters or {})
            
            # ORDER BY clause
            order_clause = "ORDER BY p.created_at DESC, p.id ASC"
            
            # LIMIT/OFFSET clause
            limit_clause, limit_params = self._build_limit_clause(limit, offset)
            params.update(limit_params)
            
            # Combine all parts
            query_parts = [select_fields, from_clause, where_clause, order_clause]
            if limit_clause:
                query_parts.append(limit_clause)
            
            query = " ".join(query_parts)
            
            logger.info(f"Built participant export query with {len(template_fields)} fields, {len(params)} parameters")
            
            return query, params
            
        except Exception as e:
            logger.error(f"Error building participant export query: {e}")
            raise
    
    def build_participant_count_query(self, filters: Dict[str, Any] = None) -> tuple:
        """Build COUNT query for participants"""
        try:
            # Use conditional essay joins for count query too
            include_essays = (filters or {}).get('with_essay', False)
            from_clause = self._build_from_clause(include_essay_joins=include_essays)
            where_clause, params = self._build_where_clause(filters or {})
            
            query = f"SELECT COUNT(DISTINCT p.id) as total {from_clause} {where_clause}"
            
            return query, params
            
        except Exception as e:
            logger.error(f"Error building participant count query: {e}")
            raise
    
    def _build_select_fields(self, template_fields: List[str], include_essay_fields: bool = True) -> str:
        """Build SELECT clause with field mapping (conditionally include essay fields)"""
        
        # Field mappings from template fields to actual database columns
        field_mappings = {
            'id': 'p.id',
            'user_id': 'p.user_id',
            'account_id': 'p.account_id',
            'full_name': 'p.full_name',
            'email': 'u.email',
            'phone_number': "CONCAT(COALESCE(p.country_code, ''), ' ', COALESCE(p.phone_number, '')) as phone_number",
            'phone_number_raw': 'p.phone_number',
            'country_code': 'p.country_code',
            'phone_flag': 'p.phone_flag',
            'gender': 'p.gender',
            'birthdate': 'p.birthdate',
            'nationality': 'p.nationality',
            'nationality_flag': 'p.nationality_flag',
            'nationality_code': 'p.nationality_code',
            'occupation': 'p.occupation',
            'institution': 'p.institution',
            'major': 'p.major',
            'organizations': 'p.organizations',
            'current_address': 'p.current_address',
            'origin_address': 'p.origin_address',
            'picture_url': 'p.picture_url',
            'instagram_account': 'p.instagram_account',
            'emergency_account': 'p.emergency_account',
            'emergency_country_code': 'p.emergency_country_code',
            'emergency_phone_flag': 'p.emergency_phone_flag',
            'emergency_contact_full': 'CONCAT(COALESCE(p.emergency_country_code, \"\"), \" \", COALESCE(p.emergency_account, \"\")) as emergency_contact_full',
            'contact_relation': 'p.contact_relation',
            'disease_history': 'p.disease_history',
            'tshirt_size': 'p.tshirt_size',
            'category': 'p.category',
            'experiences': 'p.experiences',
            'achievements': 'p.achievements',
            'resume_url': 'p.resume_url',
            'education_level': 'p.education_level',
            'knowledge_source': 'p.knowledge_source',
            'source_account_name': 'p.source_account_name',
            'twibbon_link': 'p.twibbon_link',
            'requirement_link': 'p.requirement_link',
            'ref_code_ambassador': 'p.ref_code_ambassador',
            'program_id': 'p.program_id',
            'program_name': 'pr.name as program_name',
            'score_total': 'p.score_total',
            'score_status': 'p.score_status',
            'is_active': 'p.is_active',
            'is_deleted': 'p.is_deleted',
            'created_at': 'p.created_at',
            'updated_at': 'p.updated_at',
            
            # Status fields from participant_statuses
            'general_status': 'ps.general_status',
            'form_status': 'ps.form_status',
            'document_status': 'ps.document_status',
            'payment_status': 'ps.payment_status',
            
            # Additional computed fields (always available)
            'payment_successful': 'CASE WHEN pay_status.successful_payments > 0 THEN 1 ELSE 0 END as payment_successful',
            'successful_payment_count': 'COALESCE(pay_status.successful_payments, 0) as successful_payment_count',
        }
        
        # Add essay-related fields only if essay joins are included
        if include_essay_fields:
            essay_fields = {
                'has_essays': 'CASE WHEN pe_count.essay_count > 0 THEN 1 ELSE 0 END as has_essays',
                'essay_count': 'COALESCE(pe_count.essay_count, 0) as essay_count',
                'subtheme_names': 'GROUP_CONCAT(DISTINCT pst.name SEPARATOR \", \") as subtheme_names',
                'competition_categories': 'GROUP_CONCAT(DISTINCT cc.category SEPARATOR \", \") as competition_categories',
            }
            field_mappings.update(essay_fields)
        
        # Map template fields to actual database fields
        selected_fields = []
        for field in template_fields:
            if field in field_mappings:
                selected_fields.append(field_mappings[field])
            elif not include_essay_fields and field in ['has_essays', 'essay_count', 'subtheme_names', 'competition_categories']:
                # Skip essay fields when not including essay data
                logger.info(f"Skipping essay field '{field}' - not included in basic export")
            else:
                logger.warning(f"Unknown field in template: {field}")
        
        # Always include essential fields for joining
        essential_fields = ['p.id', 'p.program_id']
        for essential in essential_fields:
            if essential not in selected_fields:
                selected_fields.append(essential)
        
        return f"SELECT {', '.join(selected_fields)}"
    
    def _build_from_clause(self, include_essay_joins: bool = True) -> str:
        """Build FROM clause with JOINs (conditionally include essay-related joins)"""
        
        # Base joins (always included)
        base_joins = """
        FROM participants p
        
        -- User information (email)
        LEFT JOIN users u ON p.user_id = u.id
        
        -- Participant statuses (form_status, payment_status, etc.)
        LEFT JOIN participant_statuses ps ON p.id = ps.participant_id 
            AND ps.is_active = 1 AND ps.is_deleted = 0
        
        -- Program information
        LEFT JOIN programs pr ON p.program_id = pr.id 
            AND pr.is_active = 1 AND pr.is_deleted = 0
        
        -- Payment status subquery (successful payments)
        LEFT JOIN (
            SELECT 
                participant_id,
                COUNT(*) as successful_payments,
                GROUP_CONCAT(program_payment_id SEPARATOR ',') as paid_program_payment_ids
            FROM payments 
            WHERE status = 2 AND is_active = 1 AND is_deleted = 0
            GROUP BY participant_id
        ) pay_status ON p.id = pay_status.participant_id"""
        
        # Essay-related joins (only when needed)
        if include_essay_joins:
            essay_joins = """
        
        -- Essay count subquery
        LEFT JOIN (
            SELECT 
                participant_id, 
                COUNT(*) as essay_count
            FROM participant_essays 
            WHERE is_active = 1 AND is_deleted = 0
            GROUP BY participant_id
        ) pe_count ON p.id = pe_count.participant_id
        
        -- Subthemes
        LEFT JOIN participant_subthemes psub ON p.id = psub.participant_id 
            AND psub.is_active = 1 AND psub.is_deleted = 0
        LEFT JOIN program_subthemes pst ON psub.program_subtheme_id = pst.id 
            AND pst.is_active = 1 AND pst.is_deleted = 0
        
        -- Competition categories
        LEFT JOIN participant_competition_categories pcc ON p.id = pcc.participant_id 
            AND pcc.is_active = 1 AND pcc.is_deleted = 0
        LEFT JOIN competition_categories cc ON pcc.competition_category_id = cc.id 
            AND cc.is_active = 1 AND cc.is_deleted = 0"""
            return base_joins + essay_joins
        
        return base_joins
    
    def _build_where_clause(self, filters: Dict[str, Any]) -> tuple:
        """Build WHERE clause with all filters"""
        conditions = []
        params = {}
        
        # Always exclude soft-deleted participants
        conditions.append("p.is_deleted = %(is_deleted)s")
        params['is_deleted'] = 0
        
        # Program ID (required filter)
        program_id = filters.get('program_id')
        if program_id:
            conditions.append("p.program_id = %(program_id)s")
            params['program_id'] = program_id
        else:
            raise ValueError("program_id is required for participant export")
        
        # Category filter (self_funded, fully_funded)
        category = filters.get('category')
        if category:
            if isinstance(category, list):
                placeholders = []
                for i, cat in enumerate(category):
                    param_name = f"category_{i}"
                    placeholders.append(f"%({param_name})s")
                    params[param_name] = cat
                conditions.append(f"p.category IN ({', '.join(placeholders)})")
            else:
                conditions.append("p.category = %(category)s")
                params['category'] = category
        
        # Form status filter (0=not started, 1=in_progress, 2=submitted)
        form_status = filters.get('form_status')
        if form_status is not None:
            if isinstance(form_status, list):
                placeholders = []
                for i, status in enumerate(form_status):
                    param_name = f"form_status_{i}"
                    placeholders.append(f"%({param_name})s")
                    params[param_name] = status
                conditions.append(f"ps.form_status IN ({', '.join(placeholders)})")
            else:
                conditions.append("ps.form_status = %(form_status)s")
                params['form_status'] = form_status
        
        # Payment done filter (array of program payment ids)
        payment_done = filters.get('payment_done')
        if payment_done:
            if isinstance(payment_done, list) and payment_done:
                # Check if participant has successful payments for any of these program payment ids
                placeholders = []
                for i, payment_id in enumerate(payment_done):
                    param_name = f"payment_done_{i}"
                    placeholders.append(f"%({param_name})s")
                    params[param_name] = payment_id
                
                payment_subquery = f"""
                EXISTS (
                    SELECT 1 FROM payments pay 
                    WHERE pay.participant_id = p.id 
                    AND pay.program_payment_id IN ({', '.join(placeholders)})
                    AND pay.status = 2 
                    AND pay.is_active = 1 
                    AND pay.is_deleted = 0
                )
                """
                conditions.append(payment_subquery)
        
        # Note: with_essay filter removed - it now only controls data inclusion, not participant filtering
        
        # Created at date range
        created_at = filters.get('created_at')
        if created_at and isinstance(created_at, dict):
            if 'min' in created_at and created_at['min']:
                conditions.append("p.created_at >= %(created_at_min)s")
                params['created_at_min'] = created_at['min']
            if 'max' in created_at and created_at['max']:
                conditions.append("p.created_at <= %(created_at_max)s")
                params['created_at_max'] = created_at['max']
        
        # Additional filters for active status
        conditions.append("p.is_active = %(p_is_active)s")
        params['p_is_active'] = 1
        
        # Build WHERE clause
        where_clause = ""
        if conditions:
            where_clause = f"WHERE {' AND '.join(conditions)}"
        
        # Add GROUP BY for aggregated fields
        where_clause += " GROUP BY p.id"
        
        return where_clause, params
    
    def _build_limit_clause(self, limit: Optional[int], offset: Optional[int]) -> tuple:
        """Build LIMIT/OFFSET clause"""
        params = {}
        clauses = []
        
        if limit is not None and limit > 0:
            clauses.append("LIMIT %(query_limit)s")
            params['query_limit'] = limit
        
        if offset is not None and offset > 0:
            clauses.append("OFFSET %(query_offset)s")
            params['query_offset'] = offset
        
        return " ".join(clauses), params

# Global instance
participant_query_builder = ParticipantExportQueryBuilder()