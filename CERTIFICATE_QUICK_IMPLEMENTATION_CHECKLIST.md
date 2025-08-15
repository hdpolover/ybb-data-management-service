# Certificate API Quick Implementation Checklist

**For CodeIgniter 4 Integration - Updated API Paths**

## ✅ API Endpoint Updates

**NEW Base URL**: `/api/ybb/certificates/` (matches existing export pattern)

| Old Path (if any) | New Path | Method |
|-------------------|----------|---------|
| N/A | `/api/ybb/certificates/generate` | POST |
| N/A | `/api/ybb/certificates/health` | GET |
| N/A | `/api/ybb/certificates/templates/validate` | POST |
| N/A | `/api/ybb/certificates/content-blocks/validate` | POST |
| N/A | `/api/ybb/certificates/placeholders` | GET |

## ✅ Required Changes in CodeIgniter

### 1. Configuration Update (5 minutes)
```php
// app/Config/YbbExport.php - ADD these lines:
public string $certificateGenerateEndpoint = '/api/ybb/certificates/generate';
public string $certificateHealthEndpoint = '/api/ybb/certificates/health';
public int $certificateTimeout = 60;
```

### 2. Route Addition (2 minutes)
```php
// app/Config/Routes.php - ADD to existing api/ybb group:
$routes->group('certificates', function($routes) {
    $routes->post('generate', 'CertificatesApiController::generate');
    $routes->get('health', 'CertificatesApiController::health');
});
```

### 3. Controller Creation (15 minutes)
Create `app/Controllers/Api/CertificatesApiController.php` - see full code in main guide.

**Minimal implementation**:
```php
public function generate()
{
    $data = $this->request->getJSON(true);
    $participantId = $data['participant_id'];
    $awardId = $data['award_id'];
    
    // Build certificate data from your database
    $certificateData = $this->buildCertificateData($participantId, $awardId);
    
    // Call Python service
    $result = $this->certificateService->generateCertificate($certificateData);
    
    return $this->response->setJSON($result);
}
```

### 4. Frontend JavaScript (10 minutes)
```javascript
// Add to your admin panel
async function generateCertificate(participantId, awardId) {
    const response = await fetch('/api/ybb/certificates/generate', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({
            participant_id: participantId,
            award_id: awardId
        })
    });
    
    const result = await response.json();
    if (result.success) {
        downloadCertificatePDF(result.data);
    }
}
```

## ✅ Data Structure Required

Your PHP code needs to send this structure to the Python service:

```php
$certificateData = [
    'participant' => [
        'id' => (int)$participant['id'],
        'full_name' => $participant['full_name'],
        'institution' => $participant['institution'],
        // ... other participant fields
    ],
    'program' => [
        'id' => (int)$program['id'],
        'name' => $program['name'],
        'theme' => $program['theme'],
        // ... other program fields
    ],
    'award' => [
        'id' => (int)$award['id'],
        'title' => $award['title'],
        'description' => $award['description'],
        // ... other award fields
    ],
    'certificate_template' => [
        'id' => (int)$template['id'],
        'template_url' => $template['template_url'],
        'template_type' => $template['template_type'], // 'pdf' or 'image'
    ],
    'content_blocks' => [
        [
            'type' => 'text', // or 'placeholder'
            'value' => 'Certificate Title',
            'x' => 300,
            'y' => 100,
            'font_size' => 24,
            'font_family' => 'Arial',
            'font_weight' => 'bold',
            'text_align' => 'center',
            'color' => '#000000'
        ],
        // ... more content blocks
    ]
];
```

## ✅ Database Tables Check

Ensure these tables exist:
- ✅ `participants` (existing)
- ✅ `programs` (existing)
- ⚠️ `program_awards` (may need creation)
- ⚠️ `program_certificates` (likely needs creation)
- ⚠️ `program_certificate_content_blocks` (likely needs creation)

## ✅ Testing Commands

1. **Health Check**:
   ```bash
   curl http://your-domain.com/api/ybb/certificates/health
   ```

2. **Generate Certificate**:
   ```bash
   curl -X POST http://your-domain.com/api/ybb/certificates/generate \
        -H "Content-Type: application/json" \
        -d '{"participant_id": 123, "award_id": 1}'
   ```

## ✅ Common Placeholders Available

- `{{participant_name}}` - Full name
- `{{program_name}}` - Program title
- `{{award_title}}` - Award name
- `{{date}}` - Issue date
- `{{program_theme}}` - Program theme
- `{{participant_institution}}` - School/University

## ✅ Error Handling

The service returns these error codes:
- `VALIDATION_ERROR` (400) - Invalid input data
- `TEMPLATE_NOT_FOUND` (404) - Template URL not accessible
- `GENERATION_FAILED` (500) - PDF generation failed
- `SERVICE_UNAVAILABLE` (503) - Python service down

## 🚀 Implementation Priority

1. **URGENT**: Update configuration and routes (7 minutes)
2. **HIGH**: Create minimal controller (15 minutes)
3. **MEDIUM**: Add frontend integration (10 minutes)
4. **LOW**: Full error handling and logging (30 minutes)

**Total minimum implementation time: ~32 minutes**

## 📞 Support

- Python service logs show detailed certificate generation process
- All endpoints return structured JSON responses
- Health endpoint shows service status and dependencies

**Ready for production use** ✅
