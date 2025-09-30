# Certificate Generation API Specification

## Overview
This document specifies the requirements for implementing certificate generation functionality in the Python service to replace the current PHP-based certificate generation system in the YBB admin platform.

## Current System Context
The YBB (Youth Break the Boundaries) admin system currently generates certificates using PHP with Dompdf. This functionality needs to be migrated to the existing Python data management service to centralize document processing capabilities.

## Database Schema Analysis

### Core Tables for Certificate Generation

#### 1. `participants` Table
```sql
CREATE TABLE `participants` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) NOT NULL,
  `account_id` varchar(255) NOT NULL,
  `full_name` varchar(255) NOT NULL,
  `birthdate` date DEFAULT NULL,
  `program_id` int(11) NOT NULL,
  `gender` enum('male','female','prefer-not','other') NOT NULL,
  `nationality` varchar(100) DEFAULT NULL,
  `nationality_code` varchar(100) DEFAULT NULL,
  `education_level` varchar(100) DEFAULT NULL,
  `major` varchar(100) DEFAULT NULL,
  `institution` varchar(100) DEFAULT NULL,
  `occupation` varchar(100) DEFAULT NULL,
  `category` enum('fully_funded','self_funded') DEFAULT 'fully_funded',
  `picture_url` varchar(255) DEFAULT NULL,
  `instagram_account` varchar(50) DEFAULT NULL,
  `experiences` text DEFAULT NULL,
  `achievements` text DEFAULT NULL,
  `tshirt_size` varchar(10) DEFAULT NULL,
  `created_at` datetime DEFAULT NULL,
  -- Additional fields...
)
```

#### 2. `participant_awards` Table
```sql
-- This table is handled in section 3.1 below
```

#### 3. `program_awards` Table
```sql
CREATE TABLE `program_awards` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `program_id` int(11) NOT NULL,
  `title` varchar(255) NOT NULL,
  `description` mediumtext DEFAULT NULL,
  `award_type` enum('winner','runner_up','mention','other') DEFAULT 'winner',
  `order_number` int(11) DEFAULT 0,
  `is_active` tinyint(1) DEFAULT 1,
  `is_deleted` tinyint(1) DEFAULT 0,
  `created_at` datetime DEFAULT current_timestamp(),
  `updated_at` datetime DEFAULT current_timestamp() ON UPDATE current_timestamp()
)
```

#### 3.1. `participant_awards` Table (Junction table linking participants to awards)
```sql
CREATE TABLE `participant_awards` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `participant_id` int(11) NOT NULL,
  `award_id` int(11) NOT NULL,
  `assigned_by` int(11) DEFAULT NULL,
  `assigned_at` datetime DEFAULT current_timestamp(),
  `notes` mediumtext DEFAULT NULL,
  `is_active` tinyint(1) DEFAULT 1,
  `is_deleted` tinyint(1) DEFAULT 0,
  `created_at` datetime DEFAULT current_timestamp(),
  `updated_at` datetime DEFAULT current_timestamp() ON UPDATE current_timestamp()
)
```

#### 4. `programs` Table
```sql
CREATE TABLE `programs` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(255) NOT NULL,
  `theme` varchar(255) DEFAULT NULL,
  `start_date` date DEFAULT NULL,
  `end_date` date DEFAULT NULL
)
```

#### 5. `program_certificates` Table (Background Templates)
```sql
CREATE TABLE `program_certificates` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `program_id` int(11) NOT NULL,
  `award_id` int(11) NULL,                   -- Can be NULL for generic certificates
  `template_url` varchar(255) NOT NULL,     -- Background image/PDF URL
  `template_type` enum('image','pdf') NOT NULL DEFAULT 'pdf',
  `preview_url` varchar(255) DEFAULT NULL,
  `issue_date` date DEFAULT NULL,
  `published_at` datetime DEFAULT NULL,
  `is_active` tinyint(1) DEFAULT 1,
  `is_deleted` tinyint(1) DEFAULT 0,
  `created_at` datetime DEFAULT current_timestamp(),
  `updated_at` datetime DEFAULT current_timestamp() ON UPDATE current_timestamp()
)
```

#### 6. `program_certificate_content_blocks` Table (Dynamic Content Positioning)
```sql
CREATE TABLE `program_certificate_content_blocks` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `certificate_id` int(11) NOT NULL,         -- References program_certificates.id
  `type` enum('text','placeholder') NOT NULL,
  `value` mediumtext NOT NULL,               -- Static text OR placeholder like {{participant_name}}
  `x` int(11) NOT NULL,                      -- X coordinate for positioning
  `y` int(11) NOT NULL,                      -- Y coordinate for positioning
  `font_size` int(11) DEFAULT 16,
  `font_family` varchar(100) DEFAULT 'Arial',
  `font_weight` varchar(50) DEFAULT 'normal',
  `text_align` varchar(20) DEFAULT 'left',
  `color` varchar(10) DEFAULT '#000000',
  `is_active` tinyint(1) DEFAULT 1,
  `is_deleted` tinyint(1) DEFAULT 0,
  `created_at` datetime DEFAULT current_timestamp(),
  `updated_at` datetime DEFAULT current_timestamp() ON UPDATE current_timestamp()
)
```

## Certificate Generation System Architecture

### Overview of Current System
The YBB certificate generation system uses a **template + content blocks** approach:

1. **Background Template**: An image or PDF file stored in `program_certificates.template_url`
2. **Content Blocks**: Positioned text elements stored in `program_certificate_content_blocks` table
3. **Dynamic Placeholders**: Special content blocks with placeholder values like `{{participant_name}}`

### Certificate Generation Flow

```
1. Admin creates certificate template (background image/PDF)
2. Admin places content blocks on template using visual designer
3. Content blocks can be:
   - Static text (type: 'text')
   - Dynamic placeholders (type: 'placeholder')
4. When certificate is generated:
   - Background template is loaded
   - Content blocks are positioned at X,Y coordinates
   - Placeholder values are replaced with actual participant data
   - Final certificate PDF is generated
```

### Real-World Database Example

Based on actual database data, here's how the system works:

#### Program: "Korea Youth Summit 2025" (ID: 5)
**Available Awards:**
- Participation Certificate (ID: 1, type: 'other')  
- The Best Project (1st Place) (ID: 10, type: 'winner')

**Certificate Templates:**
- Template ID: 2 → Program 5, Award 1 → `certificates/5/template_1751206119.pdf`
- Template ID: 3 → Program 5, Award 10 → `https://storage.ybbfoundation.com/certificates/5/template_1751378248.pdf`

**Sample Content Block (Template ID: 3):**
```json
{
  "id": 1,
  "certificate_id": 3,
  "type": "text", 
  "value": "Sample Text",
  "x": 803,
  "y": 65,
  "font_size": 14,
  "font_family": "Arial",
  "font_weight": "normal",
  "text_align": "left",
  "color": "#000000"
}
```

**Sample Participants:**
- Charles Zander Deluna (ID: 33407) from Philippines
- Matkarimova Zebo (ID: 33926)

### Content Block Types

#### Static Text Blocks (`type: 'text'`)
- Fixed text that appears exactly as entered
- Examples: "This is to certify that", "has successfully completed"
- Rich text formatting supported

#### Dynamic Placeholder Blocks (`type: 'placeholder'`)  
- Template placeholders that get replaced with real data
- Standard placeholders:
  - `{{participant_name}}` → Participant's full name
  - `{{award_title}}` → Award title from program_awards table
  - `{{program_name}}` → Program name
  - `{{date}}` → Current date or issue date
- Values are replaced during certificate generation

## API Endpoint Specification

### Endpoint: Certificate Generation
```
POST /api/v1/certificates/generate
```

### Request Headers
```
Content-Type: application/json
Authorization: Bearer <token>
```

### Request Payload Structure
```json
{
  "participant": {
    "id": 12345,
    "account_id": "abc123def456",
    "full_name": "Jane Smith",
    "birthdate": "1995-03-15",
    "gender": "female",
    "nationality": "Indonesia",
    "nationality_code": "ID",
    "education_level": "bachelor",
    "major": "Computer Science",
    "institution": "University of Technology",
    "occupation": "Student",
    "category": "fully_funded",
    "picture_url": "https://storage.ybbfoundation.com/participants/photo.jpg",
    "instagram_account": "janesmith",
    "experiences": "Software development intern at Tech Corp...",
    "achievements": "Dean's List, Programming Competition Winner...",
    "tshirt_size": "M",
    "registration_date": "2024-06-01T10:00:00Z"
  },
  "program": {
    "id": 5,
    "name": "Youth Break the Boundaries 2025",
    "theme": "Innovation and Leadership",
    "start_date": "2024-08-01",
    "end_date": "2024-08-15"
  },
  "award": {
    "id": 1,
    "title": "Participation Certificate",
    "description": "Certificate of completion for program participation",
    "award_type": "other",
    "order_number": 1
  },
  "certificate_template": {
    "id": 2,
    "template_url": "https://storage.ybbfoundation.com/certificates/template.pdf",
    "template_type": "pdf",
    "issue_date": "2024-08-15",
    "published_at": "2024-08-15T12:00:00Z"
  },
  "content_blocks": [
    {
      "id": 1,
      "type": "placeholder", 
      "value": "{{participant_name}}",
      "x": 300,
      "y": 250,
      "font_size": 24,
      "font_family": "Arial",
      "font_weight": "bold",
      "text_align": "center",
      "color": "#000000"
    },
    {
      "id": 2,
      "type": "text",
      "value": "This is to certify that",
      "x": 300,
      "y": 200,
      "font_size": 14,
      "font_family": "Arial",
      "font_weight": "normal",
      "text_align": "center",
      "color": "#666666"
    },
    {
      "id": 3,
      "type": "placeholder",
      "value": "{{award_title}}",
      "x": 300,
      "y": 350,
      "font_size": 20,
      "font_family": "Times New Roman",
      "font_weight": "bold",
      "text_align": "center",
      "color": "#1a5490"
    },
    {
      "id": 4,
      "type": "placeholder",
      "value": "{{program_name}}",
      "x": 300,
      "y": 400,
      "font_size": 16,
      "font_family": "Arial",
      "font_weight": "normal",
      "text_align": "center",
      "color": "#333333"
    },
    {
      "id": 5,
      "type": "placeholder",
      "value": "{{date}}",
      "x": 300,
      "y": 500,
      "font_size": 12,
      "font_family": "Arial",
      "font_weight": "normal",
      "text_align": "center",
      "color": "#666666"
    }
  ],
  "assignment_info": {
    "assigned_by": 1,
    "assigned_at": "2024-08-15T10:00:00Z",
    "notes": "Completed all program requirements"
  }
}
```

### Response Structure

#### Success Response (200 OK)
```json
{
  "success": true,
  "data": {
    "certificate_id": "cert_abc123def456",
    "participant_id": 12345,
    "award_id": 1,
    "file_name": "Certificate-Jane-Smith-Participation-20240815.pdf",
    "mime_type": "application/pdf",
    "file_data": "<base64_encoded_pdf_content>",
    "file_size": 1234567,
    "generated_at": "2024-08-15T14:30:00Z",
    "template_used": {
      "id": 2,
      "type": "pdf",
      "version": "1.0"
    }
  },
  "message": "Certificate generated successfully"
}
```

#### Error Response (400 Bad Request)
```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid participant data",
    "details": {
      "participant.full_name": ["Full name is required"],
      "program.id": ["Program ID must be a positive integer"]
    }
  }
}
```

#### Error Response (404 Not Found)
```json
{
  "success": false,
  "error": {
    "code": "TEMPLATE_NOT_FOUND",
    "message": "Certificate template not found or inaccessible",
    "template_url": "https://storage.ybbfoundation.com/certificates/template.pdf"
  }
}
```

#### Error Response (500 Internal Server Error)
```json
{
  "success": false,
  "error": {
    "code": "GENERATION_FAILED",
    "message": "Failed to generate certificate due to internal error",
    "request_id": "req_abc123def456"
  }
}
```

## Certificate Content Requirements

### Certificate Generation Process
1. **Download Background Template**: Fetch the image/PDF from `certificate_template.template_url`
2. **Process Content Blocks**: For each content block in the array:
   - If `type: 'text'` → Render the static text as-is
   - If `type: 'placeholder'` → Replace placeholder with actual data
3. **Position Elements**: Place each content block at specified X,Y coordinates
4. **Apply Styling**: Use font properties (size, family, weight, align, color)
5. **Generate PDF**: Combine background + positioned content blocks

### Placeholder Data Mapping
```javascript
const placeholderMappings = {
  "{{participant_name}}": participant.full_name,
  "{{award_title}}": award.title,
  "{{program_name}}": program.name,
  "{{date}}": formatDate(certificate_template.issue_date),
  "{{program_theme}}": program.theme,
  "{{program_dates}}": `${formatDate(program.start_date)} to ${formatDate(program.end_date)}`,
  "{{participant_institution}}": participant.institution,
  "{{participant_category}}": participant.category
}
```

### Content Block Processing Rules
- **Static Text Blocks**: Render exactly as provided (may contain HTML formatting)
- **Placeholder Blocks**: 
  - Match placeholder pattern `{{placeholder_name}}`
  - Replace with mapped participant/award/program data
  - Apply text formatting (font size, color, alignment, etc.)
  - Handle missing data gracefully (fallback to empty string or default text)

### Coordinate System
- **Origin Point**: Top-left corner (0,0)
- **X Coordinate**: Horizontal position from left edge (pixels)
- **Y Coordinate**: Vertical position from top edge (pixels) 
- **Template Size**: Varies based on background image/PDF dimensions

## Technical Implementation Requirements

### 1. PDF Generation
- **Library**: Use a robust PDF generation library (e.g., ReportLab for Python)
- **Background Templates**: Support both image overlays and PDF manipulation
- **Content Positioning**: Precise X,Y coordinate positioning system
- **Font Support**: Support for multiple font families (Arial, Times New Roman, etc.)
- **Quality**: Minimum 300 DPI for print quality
- **File Size**: Optimize for web delivery (target <2MB per certificate)

### 2. Template Processing
- **Image Templates**: Load as background, overlay positioned content blocks
- **PDF Templates**: Use existing PDF as base, add content blocks as overlay elements
- **Content Block Rendering**: Support both static text and dynamic placeholder replacement
- **Font Rendering**: Apply specified font properties (size, family, weight, color, alignment)
- **Coordinate System**: Implement precise pixel-based positioning

### 3. Placeholder System
- **Pattern Matching**: Detect `{{placeholder_name}}` patterns in content blocks
- **Data Mapping**: Map placeholders to actual participant/award/program data
- **Fallback Handling**: Provide defaults for missing data
- **Format Functions**: Date formatting, text casing, etc.

### 4. Security & Validation
- **Input Validation**: Strict validation of all input fields and coordinates
- **XSS Prevention**: Sanitize all text content before rendering
- **Template Validation**: Verify template URLs are accessible and valid
- **Rate Limiting**: Implement rate limiting to prevent abuse
- **Authentication**: Verify API token validity

### 4. Performance Requirements
- **Response Time**: <10 seconds for certificate generation
- **Concurrent Requests**: Support at least 50 concurrent certificate generations
- **Memory Management**: Efficient memory usage for large batch operations
- **Caching**: Cache templates and fonts for improved performance

### 5. Error Handling
- **Template Errors**: Graceful handling of inaccessible template URLs
- **Missing Data**: Handle missing placeholder data with fallbacks
- **Font Issues**: Fallback to system fonts if specified fonts unavailable
- **Coordinate Validation**: Ensure content blocks fit within template boundaries
- **Memory Limits**: Handle large template files gracefully
- **Logging**: Comprehensive error logging for debugging

## Integration Points

### Current PHP System Integration
The Python service will be called from:
- **File**: `app/Controllers/Api/CertificatesApiController.php`
- **Method**: `generateCertificate()`
- **Replacement**: Replace `generateCertificatePdf()` method call

### Configuration
Update the YBB Export configuration to include certificate endpoint:

```php
// app/Config/YbbExport.php
public string $certificateEndpoint = '/api/v1/certificates/generate';
```

### Environment Variables
```env
# Python service configuration
YBB_PYTHON_SERVICE_URL=https://your-python-service.your-deployment-service.com
YBB_PYTHON_SERVICE_TOKEN=your-api-token
YBB_CERTIFICATE_TIMEOUT=30
```

## Sample Certificate Generation Example

### Template Configuration
```json
{
  "certificate_template": {
    "id": 3,
    "template_url": "https://storage.ybbfoundation.com/certificates/5/template_bg.pdf",
    "template_type": "pdf"
  },
  "content_blocks": [
    {
      "type": "text",
      "value": "CERTIFICATE OF ACHIEVEMENT",
      "x": 400, "y": 100,
      "font_size": 28, "font_weight": "bold", 
      "text_align": "center", "color": "#1a365d"
    },
    {
      "type": "text", 
      "value": "This is to certify that",
      "x": 400, "y": 180,
      "font_size": 16, "text_align": "center", "color": "#4a5568"
    },
    {
      "type": "placeholder",
      "value": "{{participant_name}}",
      "x": 400, "y": 220,
      "font_size": 24, "font_weight": "bold",
      "text_align": "center", "color": "#2d3748"
    },
    {
      "type": "text",
      "value": "has successfully completed all requirements for the",
      "x": 400, "y": 280,
      "font_size": 14, "text_align": "center", "color": "#4a5568"
    },
    {
      "type": "placeholder",
      "value": "{{program_name}}",
      "x": 400, "y": 320,
      "font_size": 20, "font_weight": "bold",
      "text_align": "center", "color": "#1a365d"
    },
    {
      "type": "placeholder",
      "value": "{{award_title}}",
      "x": 400, "y": 380,
      "font_size": 18, "text_align": "center", "color": "#e53e3e"
    },
    {
      "type": "text",
      "value": "Issued on:",
      "x": 300, "y": 450,
      "font_size": 12, "text_align": "right", "color": "#718096"
    },
    {
      "type": "placeholder",
      "value": "{{date}}",
      "x": 320, "y": 450,
      "font_size": 12, "font_weight": "bold", 
      "text_align": "left", "color": "#2d3748"
    }
  ]
}
```

### Generated Output
When processed with participant data:
- `{{participant_name}}` → "Jane Smith"
- `{{program_name}}` → "Youth Break the Boundaries 2025"
- `{{award_title}}` → "Outstanding Performance Award"
- `{{date}}` → "August 15, 2024"

Results in a certificate with the background template and positioned text elements.

## Testing Requirements

### 1. Unit Tests
- Input validation for all fields
- Template processing logic
- PDF generation functionality
- Error handling scenarios

### 2. Integration Tests
- End-to-end certificate generation
- Template download and processing
- API response format validation
- Authentication and authorization

### 3. Performance Tests
- Load testing with concurrent requests
- Memory usage during large operations
- Response time measurements
- Template caching effectiveness

### 4. Manual Testing Scenarios
- Various participant data combinations
- Different award types and templates
- Missing or invalid template URLs
- Large batch certificate generation

## Deployment Considerations

### 1. Dependencies
- PDF generation library
- Image processing library (if supporting image templates)
- HTTP client for template downloads
- Template caching system

### 2. Infrastructure
- Adequate memory allocation (minimum 1GB recommended)
- Temporary file storage for template processing
- Content delivery network for template storage
- Monitoring and alerting setup

### 3. Monitoring
- Certificate generation success/failure rates
- Response time metrics
- Template download failures
- Memory and CPU usage

## Migration Plan

### Phase 1: Development
1. Implement the certificate generation endpoint
2. Create comprehensive unit tests
3. Set up development environment testing

### Phase 2: Integration
1. Update PHP code to call Python service
2. Implement fallback mechanism to current PHP generation
3. Conduct integration testing

### Phase 3: Deployment
1. Deploy Python service updates
2. Update PHP configuration to use Python service
3. Monitor system performance and error rates

### Phase 4: Cleanup
1. Remove PHP certificate generation code
2. Archive old certificate templates
3. Update documentation

## Support and Maintenance

### 1. Template Management
- Version control for certificate templates
- Template validation before deployment
- Backup and recovery procedures

### 2. Troubleshooting
- Comprehensive logging for issue diagnosis
- Template and content validation tools
- Performance monitoring dashboards

### 3. Future Enhancements
- Batch certificate generation endpoint
- Certificate verification API
- Custom template upload functionality
- Multi-language certificate support

---

**Document Version**: 1.0  
**Last Updated**: August 11, 2025  
**Author**: System Integration Team  
**Review Date**: Monthly review recommended
