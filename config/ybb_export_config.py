"""
YBB Export Configuration - Templates and Mappings
"""

# Export templates for different data types
EXPORT_TEMPLATES = {
    "participants": {
        "basic": {
            "fields": [
                "id", "full_name", "email", "phone_number", "nationality", "category", 
                "form_status", "payment_successful", "created_at"
            ],
            "headers": [
                "ID", "Full Name", "Email", "Phone Number", "Country", "Category", 
                "Form Status", "Payment Complete", "Registration Date"
            ],
            "max_records_single_file": 20000,
            "recommended_chunk_size": 8000
        },
        "standard": {
            "fields": [
                "id", "full_name", "email", "phone_number", "nationality", "institution", 
                "category", "form_status", "payment_successful", "program_name", "created_at"
            ],
            "headers": [
                "ID", "Full Name", "Email", "Phone Number", "Country", "Institution", 
                "Category", "Form Status", "Payment Complete", "Program", "Registration Date"
            ],
            "max_records_single_file": 15000,
            "recommended_chunk_size": 6000
        },
        "detailed": {
            "fields": [
                "id", "full_name", "email", "gender", "birthdate", "nationality", 
                "education_level", "major", "institution", "organizations", 
                "phone_number", "current_address", "emergency_account", 
                "category", "form_status", "payment_successful", "subtheme_names",
                "has_essays", "ref_code_ambassador", "program_name", "created_at"
            ],
            "headers": [
                "ID", "Full Name", "Email", "Gender", "Birth Date", "Country", 
                "Education Level", "Major", "Institution", "Organizations", 
                "Phone Number", "Current Address", "Emergency Contact", 
                "Category", "Form Status", "Payment Complete", "Subthemes",
                "Has Essays", "Ambassador Ref", "Program", "Registration Date"
            ],
            "max_records_single_file": 10000,
            "recommended_chunk_size": 4000
        },
        "summary": {
            "fields": ["full_name", "email", "nationality", "category", "form_status", "payment_successful"],
            "headers": ["Name", "Email", "Country", "Category", "Form Status", "Payment Complete"],
            "max_records_single_file": 25000,
            "recommended_chunk_size": 10000,
            "optimized_for_large_datasets": True
        },
        "complete": {
            "fields": [
                "id", "user_id", "account_id", "full_name", "email", "gender", "birthdate",
                "nationality", "nationality_flag", "nationality_code", "occupation",
                "education_level", "major", "institution", "organizations", 
                "phone_number", "country_code", "phone_flag", "current_address", "origin_address", 
                "picture_url", "instagram_account", "emergency_account", "emergency_country_code",
                "emergency_phone_flag", "contact_relation", "disease_history", "tshirt_size", 
                "category", "experiences", "achievements", "resume_url", "knowledge_source", 
                "source_account_name", "twibbon_link", "requirement_link", "ref_code_ambassador", 
                "program_id", "program_name", "general_status", "form_status", "document_status", 
                "payment_status", "score_total", "score_status", "has_essays", "essay_count",
                "subtheme_names", "competition_categories", "payment_successful", 
                "successful_payment_count", "is_active", "created_at", "updated_at"
            ],
            "headers": [
                "ID", "User ID", "Account ID", "Full Name", "Email", "Gender", "Birth Date",
                "Nationality", "Flag", "Country Code", "Occupation", "Education Level", "Major",
                "Institution", "Organizations", "Phone Number", "Country Code", "Current Address",
                "Origin Address", "Picture URL", "Instagram", "Emergency Contact", "Contact Relation",
                "Disease History", "T-Shirt Size", "Category", "Experiences", "Achievements",
                "Resume URL", "Knowledge Source", "Source Account", "Twibbon Link", "Requirement Link",
                "Ambassador Ref", "Program ID", "Active", "Deleted", "Created At", "Updated At"
            ],
            "headers": [
                "ID", "User ID", "Account ID", "Full Name", "Email", "Gender", "Birth Date",
                "Country", "Country Flag", "Country Code", "Occupation", "Education Level", 
                "Major", "Institution", "Organizations", "Phone Number", "Country Code", 
                "Phone Flag", "Current Address", "Origin Address", "Picture URL", 
                "Instagram", "Emergency Contact", "Emergency Country Code", "Emergency Phone Flag",
                "Contact Relation", "Disease History", "T-Shirt Size", "Category", "Experiences", 
                "Achievements", "Resume URL", "Knowledge Source", "Source Account", "Twibbon Link", 
                "Requirement Link", "Ambassador Ref", "Program ID", "Program Name", "General Status", 
                "Form Status", "Document Status", "Payment Status", "Score Total", "Score Status", 
                "Has Essays", "Essay Count", "Subthemes", "Competition Categories", "Payment Successful", 
                "Successful Payment Count", "Active", "Created At", "Updated At"
            ],
            "max_records_single_file": 5000,
            "recommended_chunk_size": 3000
        }
    },
    "payments": {
        "standard": {
            "fields": [
                "id", "participant_name", "participant_email", "amount", "currency", 
                "usd_amount", "status", "payment_method", "payment_date", "transaction_code", "order_id"
            ],
            "headers": [
                "Payment ID", "Participant Name", "Email", "Amount", "Currency", 
                "USD Amount", "Status", "Payment Method", "Payment Date", "Transaction Code", "Order ID"
            ],
            "max_records_single_file": 20000,
            "recommended_chunk_size": 8000
        },
        "detailed": {
            "fields": [
                "id", "participant_id", "participant_name", "participant_email", "program_payment_id",
                "payment_method_id", "transaction_code", "order_id", "payment_date", "amount",
                "usd_amount", "currency", "status", "proof_url", "account_name", "source_name",
                "notes", "rejection_reason", "payment_url", "created_at"
            ],
            "headers": [
                "Payment ID", "Participant ID", "Participant Name", "Email", "Program Payment ID",
                "Payment Method ID", "Transaction Code", "Order ID", "Payment Date", "Amount",
                "USD Amount", "Currency", "Status", "Proof URL", "Account Name", "Source Name",
                "Notes", "Rejection Reason", "Payment URL", "Created At"
            ],
            "max_records_single_file": 15000,
            "recommended_chunk_size": 5000
        }
    },
    "ambassadors": {
        "standard": {
            "fields": [
                "id", "name", "email", "ref_code", "institution", "total_referrals", 
                "is_active", "created_at"
            ],
            "headers": [
                "ID", "Ambassador Name", "Email", "Reference Code", "Institution", 
                "Total Referrals", "Active Status", "Registration Date"
            ],
            "max_records_single_file": 25000,
            "recommended_chunk_size": 10000
        },
        "detailed": {
            "fields": [
                "id", "name", "email", "ref_code", "program_id", "institution", "gender",
                "phone_number", "notes", "total_referrals", "successful_referrals",
                "is_active", "created_at", "updated_at"
            ],
            "headers": [
                "ID", "Ambassador Name", "Email", "Reference Code", "Program ID", "Institution",
                "Gender", "Phone Number", "Notes", "Total Referrals", "Successful Referrals",
                "Active Status", "Created At", "Updated At"
            ],
            "max_records_single_file": 15000,
            "recommended_chunk_size": 5000
        }
    }
}

# Status mappings
STATUS_MAPPINGS = {
    "form_status": {
        0: "Not Started",
        1: "In Progress", 
        2: "Submitted"
    },
    "payment_status": {
        0: "Created",
        1: "Pending",
        2: "Success",
        3: "Cancelled",
        4: "Rejected"
    },
    "payment_method": {
        1: "Midtrans",
        2: "Manual Transfer"
    },
    "boolean_status": {
        0: "No",
        1: "Yes"
    },
    "category": {
        "fully_funded": "Fully Funded",
        "self_funded": "Self Funded"
    }
}

# System configuration
SYSTEM_CONFIG = {
    "limits": {
        "max_records_single_file": 25000,
        "max_records_immediate_processing": 1000,
        "max_file_size_mb": 50,
        "max_memory_usage_gb": 2,
        "max_processing_time_minutes": 30,
        "max_concurrent_large_exports": 3,
        "file_retention_days": 7
    },
    "cleanup": {
        "auto_cleanup_enabled": True,
        "max_concurrent_exports": 20,  # Keep more exports available
        "cleanup_on_startup": True,
        "cleanup_on_export": False,  # Don't cleanup before each export
        "keep_temp_files_minutes": 120,  # Keep temp files longer (2 hours)
        "storage_warning_threshold_mb": 500,
        "storage_cleanup_threshold_mb": 1000,
        "force_cleanup_after_days": 1,
        "cleanup_interval_minutes": 30,  # Only cleanup every 30 minutes
        "min_export_age_minutes": 10  # Don't cleanup exports less than 10 minutes old
    },
    "chunk_configurations": {
        "default_chunk_size": 10000,
        "min_chunk_size": 1000,
        "max_chunk_size": 25000,
        "memory_based_chunking": True,
        "adaptive_chunk_sizing": True
    },
    "format_limits": {
        "excel": {
            "max_rows_per_sheet": 1048576,
            "max_sheets_per_file": 10,
            "recommended_rows_per_sheet": 100000
        },
        "csv": {
            "no_row_limit": True,
            "recommended_chunk_size": 50000
        }
    }
}

# Data transformations
DATA_TRANSFORMATIONS = {
    "date_format": "%Y-%m-%d",
    "datetime_format": "%Y-%m-%d %H:%M:%S",
    "currency_format": "{:,.2f}",
    "boolean_format": "Yes/No",
    "null_values": "N/A"
}

def get_template(export_type, template_name):
    """Get export template configuration"""
    return EXPORT_TEMPLATES.get(export_type, {}).get(template_name, {})

def get_status_label(status_type, value):
    """Get human-readable status label"""
    return STATUS_MAPPINGS.get(status_type, {}).get(value, str(value))

def get_chunk_size(export_type, template_name, record_count):
    """Calculate optimal chunk size based on template and record count"""
    template = get_template(export_type, template_name)
    
    if record_count < 1000:
        return record_count
    elif record_count < 10000:
        return min(template.get("recommended_chunk_size", 5000), record_count)
    else:
        return template.get("recommended_chunk_size", 10000)

def should_use_chunked_processing(record_count, template_config):
    """Determine if chunked processing should be used"""
    max_single_file = template_config.get("max_records_single_file", 15000)
    return record_count > max_single_file

def get_cleanup_config(key=None):
    """Get cleanup configuration settings"""
    cleanup_config = SYSTEM_CONFIG.get("cleanup", {})
    if key:
        return cleanup_config.get(key)
    return cleanup_config

def get_storage_limits():
    """Get storage-related limits and thresholds"""
    cleanup_config = SYSTEM_CONFIG.get("cleanup", {})
    return {
        "max_concurrent_exports": cleanup_config.get("max_concurrent_exports", 5),
        "storage_warning_threshold_mb": cleanup_config.get("storage_warning_threshold_mb", 500),
        "storage_cleanup_threshold_mb": cleanup_config.get("storage_cleanup_threshold_mb", 1000),
        "file_retention_days": SYSTEM_CONFIG.get("limits", {}).get("file_retention_days", 7),
        "keep_temp_files_minutes": cleanup_config.get("keep_temp_files_minutes", 30)
    }
