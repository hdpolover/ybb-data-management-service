# Certificate Generation with Name and Certificate Number Only

## Quick Guide for Simple Certificate Generation

This guide shows how to generate certificates with **just 2 fields**:
1. **Participant Name**
2. **Certificate Number**

---

## ✅ What Was Added

### New Placeholder
- `{{certificate_number}}` - Certificate number or identifier

### API Support
The certificate generation API now supports minimal certificate generation with just name and number fields.

---

## 🎯 How to Use (Python Test)

### Single Certificate
```bash
python test_real_certificate.py
```

### Batch Certificates
```bash
python test_real_certificate.py batch
```

---

## 📋 PHP/CodeIgniter Integration

### Minimal Certificate Data Structure

```php
<?php
// Simplified certificate generation with just name and number

public function generateSimpleCertificate($participantId, $certificateNumber)
{
    $certificateService = new CertificateService();
    
    // Get participant data
    $participantModel = new ParticipantModel();
    $participant = $participantModel->find($participantId);
    
    // Minimal certificate data - only what's required by API
    $certificateData = [
        'participant' => [
            'id' => $participant['id'],
            'full_name' => $participant['full_name'],
            // Other fields can use defaults
            'birthdate' => $participant['birthdate'] ?? '1990-01-01',
            'gender' => $participant['gender'] ?? 'other',
            'nationality' => $participant['nationality'] ?? 'Indonesia',
            'nationality_code' => $participant['nationality_code'] ?? 'ID',
            'education_level' => $participant['education_level'] ?? 'bachelor',
            'major' => $participant['major'] ?? 'General',
            'institution' => $participant['institution'] ?? 'University',
            'occupation' => $participant['occupation'] ?? 'Student',
            'category' => $participant['category'] ?? 'other'
        ],
        'program' => [
            'id' => $participant['program_id'],
            'name' => 'Youth Break the Boundaries 2025',
            'theme' => 'Leadership Development',
            'start_date' => '2025-08-01',
            'end_date' => '2025-08-15'
        ],
        'award' => [
            'id' => 1,
            'title' => 'Certificate of Participation',
            'description' => 'Successfully completed the program',
            'award_type' => 'other',
            'order_number' => 1
        ],
        'certificate_template' => [
            'id' => 1,
            'template_url' => 'https://your-cdn.com/templates/kys_certificate.pdf',
            'template_type' => 'pdf',
            'issue_date' => date('Y-m-d'),
            'certificate_number' => $certificateNumber  // ✨ NEW
        ],
        // ONLY 2 content blocks needed!
        'content_blocks' => [
            [
                'id' => 1,
                'type' => 'placeholder',
                'value' => '{{participant_name}}',
                'x' => 421,        // Center X for landscape A4 (842px width)
                'y' => 268,        // Name position
                'font_size' => 24,
                'font_family' => 'Times New Roman',
                'font_weight' => 'bold',
                'text_align' => 'center',
                'color' => '#000000'
            ],
            [
                'id' => 2,
                'type' => 'placeholder',
                'value' => '{{certificate_number}}',
                'x' => 100,        // Left position
                'y' => 89,         // Bottom position
                'font_size' => 12,
                'font_family' => 'Arial',
                'font_weight' => 'normal',
                'text_align' => 'left',
                'color' => '#000000'
            ]
        ]
    ];
    
    // Generate certificate
    $result = $certificateService->generateCertificate($certificateData);
    
    if ($result['success']) {
        // Return the certificate data for download
        return [
            'success' => true,
            'certificate_id' => $result['data']['certificate_id'],
            'file_name' => $result['data']['file_name'],
            'file_data' => $result['data']['file_data'],
            'file_size' => $result['data']['file_size']
        ];
    }
    
    return $result;
}
```

---

## 🎨 Positioning Guide for Your Template

Your template is **landscape A4** (842 x 595 points).

### Recommended Positions:

| Field | Position | Explanation |
|-------|----------|-------------|
| **Participant Name** | X: 421 (center)<br>Y: 268 (middle) | Centered horizontally, approximately middle of page |
| **Certificate Number** | X: 100 (left)<br>Y: 89 (bottom) | Left-aligned, near bottom |

### Adjust Y Coordinates Based on Your Template:
- Measure from **top** of the page
- Y=0 is the **top**, Y=595 is the **bottom**
- For **center vertically**: Y ≈ 297
- For **upper third**: Y ≈ 200
- For **lower third**: Y ≈ 400

---

## 📊 Testing Results

✅ **5 test certificates generated successfully**

| Participant | Certificate Number | File Size | Status |
|-------------|-------------------|-----------|--------|
| John Michael Anderson | KYS/2025/001 | 1.04 MB | ✅ Generated |
| Sarah Elizabeth Thompson | KYS/2025/002 | 1.04 MB | ✅ Generated |
| Ahmad Faisal Ibrahim | KYS/2025/003 | 1.04 MB | ✅ Generated |
| Maria Sofia Rodriguez | KYS/2025/004 | 1.04 MB | ✅ Generated |
| David Chen Wei | KYS/2025/005 | 1.04 MB | ✅ Generated |

---

## 🔧 Configuration for Your Template

### 1. Upload Template to CDN/Storage
```bash
# Upload your template to cloud storage (S3, CloudFront, etc.)
# Example: https://storage.ybbfoundation.com/certificates/kys_template.pdf
```

### 2. Update Database
```sql
-- Store template configuration in your database
INSERT INTO program_certificates (
    program_id, 
    template_url, 
    template_type,
    is_active
) VALUES (
    1,
    'https://storage.ybbfoundation.com/certificates/kys_template.pdf',
    'pdf',
    1
);

-- Store content blocks (name and certificate number positions)
INSERT INTO program_certificate_content_blocks (
    certificate_id,
    type,
    value,
    x,
    y,
    font_size,
    font_family,
    font_weight,
    text_align,
    color
) VALUES 
-- Block 1: Participant Name
(1, 'placeholder', '{{participant_name}}', 421, 268, 24, 'Times New Roman', 'bold', 'center', '#000000'),
-- Block 2: Certificate Number
(1, 'placeholder', '{{certificate_number}}', 100, 89, 12, 'Arial', 'normal', 'left', '#000000');
```

### 3. Generate Certificates
```php
// In your controller
$participantId = 12345;
$certificateNumber = "KYS/2025/" . str_pad($participantId, 4, '0', STR_PAD_LEFT);

$result = $this->generateSimpleCertificate($participantId, $certificateNumber);

if ($result['success']) {
    // Download or display certificate
    $this->downloadCertificatePDF($result['file_data'], $result['file_name']);
}
```

---

## 💡 Tips

### Certificate Number Formats
```php
// Sequential format
"KYS/2025/001"
"KYS/2025/002"

// Participant ID based
"KYS/2025/" . str_pad($participantId, 4, '0', STR_PAD_LEFT)

// Date-based
"KYS/" . date('Y') . "/" . str_pad($sequence, 3, '0', STR_PAD_LEFT)

// UUID-based (unique)
"KYS-" . substr(uniqid(), -8)
```

### Font Recommendations
- **Name**: Use serif fonts (Times New Roman, Georgia) for elegance
- **Certificate Number**: Use sans-serif (Arial, Helvetica) for clarity

### Size Recommendations
- **Name**: 20-32pt (24pt works well)
- **Certificate Number**: 10-14pt (12pt is standard)

---

## 📁 Files

- `test_real_certificate.py` - Python test script
- `static/templates/kys_certificate_template.pdf` - Your template
- `certificate_*.pdf` - Generated certificates

---

## 🎉 Summary

✅ Certificate generation working with your template
✅ Supports **just 2 fields**: name and certificate number
✅ New placeholder: `{{certificate_number}}`
✅ Tested with 5 sample certificates
✅ Ready for PHP/CodeIgniter integration

**Next Step**: Upload your template to cloud storage and configure the PHP integration!
