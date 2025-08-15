# YBB Certificate Generation API Documentation

## Overview
The YBB Certificate Generation API provides endpoints for creating certificates from templates with dynamic content blocks. This service integrates with the existing YBB export system and follows the same URL structure.

## Base URL
All certificate endpoints are prefixed with `/api/ybb/certificates/`

## Authentication
Currently uses the same authentication mechanism as other YBB export endpoints.

## Endpoints

### 1. Certificate Generation
**POST** `/api/ybb/certificates/generate`

Generate a certificate from template and content blocks.

#### Request Headers
```
Content-Type: application/json
```

#### Request Body
```json
{
  "participant": {
    "id": 12345,
    "full_name": "John Doe",
    "birthdate": "1995-03-15",
    "gender": "male",
    "nationality": "Indonesia",
    "nationality_code": "ID",
    "education_level": "bachelor",
    "major": "Computer Science",
    "institution": "University of Technology",
    "occupation": "Student",
    "category": "fully_funded"
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
    "title": "Certificate of Participation",
    "description": "Awarded for successful completion",
    "award_type": "other",
    "order_number": 1
  },
  "certificate_template": {
    "id": 2,
    "template_url": "https://storage.ybbfoundation.com/certificates/template.pdf",
    "template_type": "pdf",
    "issue_date": "2024-08-15"
  },
  "content_blocks": [
    {
      "id": 1,
      "type": "text",
      "value": "CERTIFICATE OF ACHIEVEMENT",
      "x": 300,
      "y": 100,
      "font_size": 24,
      "font_family": "Arial",
      "font_weight": "bold",
      "text_align": "center",
      "color": "#1a365d"
    },
    {
      "id": 2,
      "type": "placeholder",
      "value": "{{participant_name}}",
      "x": 300,
      "y": 220,
      "font_size": 28,
      "font_family": "Times New Roman",
      "font_weight": "bold",
      "text_align": "center",
      "color": "#2d3748"
    }
  ],
  "assignment_info": {
    "assigned_by": 1,
    "assigned_at": "2024-08-15T10:00:00Z",
    "notes": "Completed all requirements"
  }
}
```

#### Success Response (200)
```json
{
  "success": true,
  "data": {
    "certificate_id": "cert_abc123def456",
    "participant_id": 12345,
    "award_id": 1,
    "file_name": "Certificate-John-Doe-Participation-20240815.pdf",
    "mime_type": "application/pdf",
    "file_data": "<base64_encoded_pdf_content>",
    "file_size": 62629,
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

#### Error Response (400)
```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid certificate data",
    "details": {
      "participant.full_name": ["Full name is required"]
    }
  }
}
```

---

### 2. Health Check
**GET** `/api/ybb/certificates/health`

Check the health and availability of the certificate generation service.

#### Success Response (200)
```json
{
  "service": "Certificate Generation Service",
  "status": "healthy",
  "timestamp": 1691764800.123,
  "request_id": "abc123",
  "dependencies": {
    "reportlab": true,
    "pillow": true,
    "pypdf2": true
  }
}
```

---

### 3. Template Validation
**POST** `/api/ybb/certificates/templates/validate`

Validate a certificate template URL and accessibility.

#### Request Body
```json
{
  "template_url": "https://storage.ybbfoundation.com/certificates/template.pdf",
  "template_type": "pdf"
}
```

#### Success Response (200)
```json
{
  "success": true,
  "data": {
    "template_url": "https://storage.ybbfoundation.com/certificates/template.pdf",
    "template_type": "pdf",
    "file_size": 1048576,
    "status": "valid"
  },
  "message": "Template is valid and accessible"
}
```

---

### 4. Content Blocks Validation
**POST** `/api/ybb/certificates/content-blocks/validate`

Validate content blocks structure and positioning.

#### Request Body
```json
{
  "content_blocks": [
    {
      "type": "text",
      "value": "Sample text",
      "x": 300,
      "y": 100,
      "font_size": 16
    }
  ],
  "template_dimensions": {
    "width": 595,
    "height": 842
  }
}
```

#### Success Response (200)
```json
{
  "success": true,
  "data": {
    "total_blocks": 1,
    "valid_blocks": 1,
    "invalid_blocks": 0,
    "warnings": [],
    "errors": []
  }
}
```

---

### 5. Available Placeholders
**GET** `/api/ybb/certificates/placeholders`

Get list of available placeholders for certificate content.

#### Success Response (200)
```json
{
  "success": true,
  "data": {
    "participant": [
      {
        "placeholder": "{{participant_name}}",
        "description": "Participant full name"
      },
      {
        "placeholder": "{{participant_institution}}",
        "description": "Participant institution"
      }
    ],
    "program": [
      {
        "placeholder": "{{program_name}}",
        "description": "Program name"
      }
    ],
    "award": [
      {
        "placeholder": "{{award_title}}",
        "description": "Award title"
      }
    ],
    "general": [
      {
        "placeholder": "{{date}}",
        "description": "Issue date or current date"
      }
    ]
  },
  "message": "Available certificate placeholders"
}
```

## Available Placeholders

### Participant Placeholders
- `{{participant_name}}` - Participant's full name
- `{{participant_institution}}` - Institution name
- `{{participant_category}}` - Funding category
- `{{participant_nationality}}` - Nationality
- `{{participant_education_level}}` - Education level
- `{{participant_major}}` - Major/field of study
- `{{participant_occupation}}` - Occupation

### Program Placeholders
- `{{program_name}}` - Program name
- `{{program_theme}}` - Program theme
- `{{program_dates}}` - Program date range

### Award Placeholders
- `{{award_title}}` - Award title
- `{{award_description}}` - Award description
- `{{award_type}}` - Award type

### General Placeholders
- `{{date}}` - Issue date (formatted as "Month DD, YYYY")

## Content Block Types

### Text Blocks
Static text that appears exactly as entered.
```json
{
  "type": "text",
  "value": "This is to certify that",
  "x": 300,
  "y": 200
}
```

### Placeholder Blocks
Dynamic content that gets replaced with actual data.
```json
{
  "type": "placeholder",
  "value": "{{participant_name}}",
  "x": 300,
  "y": 250
}
```

## Styling Options

### Font Properties
- `font_size`: Integer (6-200, default: 12)
- `font_family`: String ("Arial", "Times New Roman", "Courier New")
- `font_weight`: String ("normal", "bold")
- `text_align`: String ("left", "center", "right")
- `color`: String (hex color like "#000000" or named colors)

### Positioning
- `x`: Integer (horizontal position from left edge, 0+)
- `y`: Integer (vertical position from top edge, 0+)

## Template Types

### PDF Templates
- Supported format: PDF files
- Background PDF with content overlaid on top
- Maintains original PDF quality and dimensions

### Image Templates
- Supported formats: JPG, JPEG, PNG, TIFF, BMP
- Converted to PDF with content overlaid
- Automatically scaled to fit standard page sizes

## Error Codes

- `VALIDATION_ERROR` - Request data validation failed
- `TEMPLATE_NOT_FOUND` - Certificate template not accessible
- `GENERATION_FAILED` - Certificate generation process failed
- `SERVICE_UNAVAILABLE` - Certificate service dependencies missing

## Integration Example

### PHP Integration (CodeIgniter)
```php
$certificateData = [
    'participant' => $participantData,
    'program' => $programData,
    'award' => $awardData,
    'certificate_template' => $templateData,
    'content_blocks' => $contentBlocks
];

$response = $this->http->post('http://python-service/api/ybb/certificates/generate', [
    'json' => $certificateData,
    'timeout' => 60
]);

if ($response->getStatusCode() === 200) {
    $result = json_decode($response->getBody(), true);
    $pdfData = base64_decode($result['data']['file_data']);
    // Save or return PDF
}
```

### JavaScript Integration
```javascript
const generateCertificate = async (certificateData) => {
  try {
    const response = await fetch('/api/ybb/certificates/generate', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(certificateData)
    });
    
    if (response.ok) {
      const result = await response.json();
      const pdfData = atob(result.data.file_data);
      // Handle PDF data
      return result;
    }
  } catch (error) {
    console.error('Certificate generation failed:', error);
  }
};
```

## Performance Notes

- Certificate generation typically takes 500-2000ms
- Template files are temporarily cached for performance
- Supports concurrent certificate generation
- Maximum template size: 50MB
- Generated certificates are optimized for web delivery

## Security Considerations

- Template URLs must be from approved domains
- All input data is validated and sanitized
- XSS protection for content blocks
- Rate limiting applied to prevent abuse
- Temporary files are automatically cleaned up
