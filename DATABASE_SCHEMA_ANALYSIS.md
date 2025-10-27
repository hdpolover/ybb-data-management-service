# Database Schema Analysis - YBB Master App

## 🗄️ **Actual Database Structure Discovered**

### **Key Tables Identified:**

#### **1. `participants` Table** (Main participant data)
**Key Columns:**
- `id` (Primary Key)
- `user_id`, `account_id` 
- `full_name`, `birthdate`, `gender`
- `program_id` (Foreign Key to programs)
- `nationality`, `phone_number`, `institution`, `major`
- `category` ('fully_funded', 'self_funded')
- `score_status` ('go_to_interview', 'rejected', 'no_score')
- `created_at`, `updated_at`

#### **2. `participant_statuses` Table** (Status tracking)
**Key Columns:**
- `id` (Primary Key)
- `participant_id` (Foreign Key to participants)
- `form_status` (0=not started, 1=in progress, 2=submitted)
- `general_status`, `document_status`, `payment_status`
- `created_at`, `updated_at`

#### **3. `payments` Table** (Payment records)
**Key Columns:**
- `id` (Primary Key)
- `participant_id` (Foreign Key to participants)
- `status` (0,1,2,3,4 - where 2 appears to be success)
- `amount`, `usd_amount`, `currency`
- `payment_date`, `payment_method_id`
- `created_at`, `updated_at`

#### **4. `programs` Table** (Program information)
**Key Columns:**
- `id` (Primary Key)
- `name`, `description`, `theme`
- `start_date`, `end_date`
- `is_registration_open`

### **Status Value Mappings:**

#### **Form Status (participant_statuses.form_status):**
- `0` = Not started
- `1` = In progress  
- `2` = Submitted ✅

#### **Payment Status (payments.status):**
- `0` = Pending/Initiated
- `1` = Processing
- `2` = Success/Completed ✅
- `3` = Failed
- `4` = Cancelled

### **Schema Differences from Original Design:**

1. **❌ Issue**: Database service was looking for `form_status` in `participants` table
   **✅ Fix**: Need to JOIN with `participant_statuses` table

2. **❌ Issue**: Column names don't match expected format
   **✅ Fix**: Update queries to use actual column names (`full_name` not `name`)

3. **❌ Issue**: Additional complexity with multiple status tables
   **✅ Fix**: Need proper JOINs for complete participant data

### **Required Database Service Updates:**

1. Update participant queries to JOIN participant_statuses
2. Use correct column names (`full_name`, not `name`)
3. Adjust status filtering logic for actual values
4. Update export templates to match real columns

This analysis shows we need to significantly update the database service to match the actual YBB database schema.