# Certificate Generation API Integration Guide for CodeIgniter 4

**Document Version**: 1.0  
**Last Updated**: August 11, 2025  
**API Service**: YBB Data Management Service  
**Target Framework**: CodeIgniter 4  

## Overview

This document provides implementation guidance for integrating the Certificate Generation API endpoints into the existing YBB CodeIgniter 4 admin platform. The certificate generation functionality has been implemented in the Python service and is ready for integration.

## API Endpoint Changes

### Base URL Structure
The certificate generation endpoints follow the same URL pattern as existing YBB export endpoints:

```
Base URL: /api/ybb/certificates/
```

### Available Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/ybb/certificates/generate` | POST | Generate certificate from template and data |
| `/api/ybb/certificates/health` | GET | Health check for certificate service |
| `/api/ybb/certificates/templates/validate` | POST | Validate certificate template URL |
| `/api/ybb/certificates/content-blocks/validate` | POST | Validate content blocks structure |
| `/api/ybb/certificates/placeholders` | GET | Get available placeholder variables |

## CodeIgniter 4 Implementation

### 1. Update Configuration

Update your YBB Export configuration file to include certificate endpoints:

```php
<?php
// app/Config/YbbExport.php

namespace Config;

use CodeIgniter\Config\BaseConfig;

class YbbExport extends BaseConfig
{
    public string $pythonServiceUrl = 'https://your-python-service.railway.app';
    
    public string $apiKey = 'your-api-key';
    
    // Existing endpoints
    public string $participantsEndpoint = '/api/ybb/export/participants';
    public string $paymentsEndpoint = '/api/ybb/export/payments';
    public string $ambassadorsEndpoint = '/api/ybb/export/ambassadors';
    
    // NEW: Certificate endpoints
    public string $certificateGenerateEndpoint = '/api/ybb/certificates/generate';
    public string $certificateHealthEndpoint = '/api/ybb/certificates/health';
    public string $certificateValidateTemplateEndpoint = '/api/ybb/certificates/templates/validate';
    public string $certificateValidateBlocksEndpoint = '/api/ybb/certificates/content-blocks/validate';
    public string $certificatePlaceholdersEndpoint = '/api/ybb/certificates/placeholders';
    
    // Certificate settings
    public int $certificateTimeout = 60; // seconds
    public int $maxCertificateSize = 10 * 1024 * 1024; // 10MB
    public array $allowedTemplateFormats = ['pdf', 'jpg', 'jpeg', 'png'];
}
```

### 2. Create Certificate Service Class

Create a new service class for certificate generation:

```php
<?php
// app/Services/CertificateService.php

namespace App\Services;

use Config\YbbExport;
use CodeIgniter\HTTP\CURLRequest;
use CodeIgniter\Config\Services;

class CertificateService
{
    protected YbbExport $config;
    protected CURLRequest $client;
    
    public function __construct()
    {
        $this->config = config('YbbExport');
        $this->client = Services::curlrequest([
            'timeout' => $this->config->certificateTimeout,
            'headers' => [
                'Content-Type' => 'application/json',
                'Authorization' => 'Bearer ' . $this->config->apiKey
            ]
        ]);
    }
    
    /**
     * Generate certificate for participant and award
     */
    public function generateCertificate(array $certificateData): array
    {
        $url = $this->config->pythonServiceUrl . $this->config->certificateGenerateEndpoint;
        
        try {
            log_message('info', 'Certificate generation requested for participant: ' . 
                       ($certificateData['participant']['full_name'] ?? 'Unknown'));
            
            $response = $this->client->post($url, [
                'json' => $certificateData
            ]);
            
            $statusCode = $response->getStatusCode();
            $responseBody = json_decode($response->getBody(), true);
            
            if ($statusCode === 200 && $responseBody['success']) {
                log_message('info', 'Certificate generated successfully: ' . 
                           $responseBody['data']['certificate_id']);
                return [
                    'success' => true,
                    'data' => $responseBody['data']
                ];
            } else {
                log_message('error', 'Certificate generation failed: ' . 
                           ($responseBody['error']['message'] ?? 'Unknown error'));
                return [
                    'success' => false,
                    'error' => $responseBody['error'] ?? ['message' => 'Unknown error']
                ];
            }
            
        } catch (\Exception $e) {
            log_message('error', 'Certificate generation exception: ' . $e->getMessage());
            return [
                'success' => false,
                'error' => ['message' => 'Certificate generation failed: ' . $e->getMessage()]
            ];
        }
    }
    
    /**
     * Validate certificate template
     */
    public function validateTemplate(string $templateUrl, string $templateType = 'pdf'): array
    {
        $url = $this->config->pythonServiceUrl . $this->config->certificateValidateTemplateEndpoint;
        
        try {
            $response = $this->client->post($url, [
                'json' => [
                    'template_url' => $templateUrl,
                    'template_type' => $templateType
                ]
            ]);
            
            return json_decode($response->getBody(), true);
            
        } catch (\Exception $e) {
            return [
                'success' => false,
                'error' => ['message' => 'Template validation failed: ' . $e->getMessage()]
            ];
        }
    }
    
    /**
     * Get available placeholders
     */
    public function getAvailablePlaceholders(): array
    {
        $url = $this->config->pythonServiceUrl . $this->config->certificatePlaceholdersEndpoint;
        
        try {
            $response = $this->client->get($url);
            return json_decode($response->getBody(), true);
        } catch (\Exception $e) {
            return [
                'success' => false,
                'error' => ['message' => 'Failed to get placeholders: ' . $e->getMessage()]
            ];
        }
    }
    
    /**
     * Check certificate service health
     */
    public function checkHealth(): array
    {
        $url = $this->config->pythonServiceUrl . $this->config->certificateHealthEndpoint;
        
        try {
            $response = $this->client->get($url);
            return json_decode($response->getBody(), true);
        } catch (\Exception $e) {
            return [
                'service' => 'Certificate Generation Service',
                'status' => 'error',
                'error' => $e->getMessage()
            ];
        }
    }
}
```

### 3. Update/Create Certificate Controller

Create or update your certificate controller:

```php
<?php
// app/Controllers/Api/CertificatesApiController.php

namespace App\Controllers\Api;

use App\Controllers\BaseController;
use App\Services\CertificateService;
use App\Models\ParticipantModel;
use App\Models\ProgramModel;
use App\Models\ProgramAwardModel;
use App\Models\ProgramCertificateModel;
use App\Models\ProgramCertificateContentBlockModel;

class CertificatesApiController extends BaseController
{
    protected CertificateService $certificateService;
    
    public function __construct()
    {
        $this->certificateService = new CertificateService();
    }
    
    /**
     * Generate certificate for participant and award
     * POST /api/certificates/generate
     */
    public function generate()
    {
        try {
            $data = $this->request->getJSON(true);
            
            // Validate required parameters
            $participantId = $data['participant_id'] ?? null;
            $awardId = $data['award_id'] ?? null;
            
            if (!$participantId || !$awardId) {
                return $this->response->setJSON([
                    'success' => false,
                    'message' => 'Participant ID and Award ID are required'
                ])->setStatusCode(400);
            }
            
            // Load data from database
            $certificateData = $this->buildCertificateData($participantId, $awardId);
            
            if (!$certificateData['success']) {
                return $this->response->setJSON($certificateData)->setStatusCode(404);
            }
            
            // Generate certificate
            $result = $this->certificateService->generateCertificate($certificateData['data']);
            
            if ($result['success']) {
                // Save certificate record (optional)
                $this->saveCertificateRecord($participantId, $awardId, $result['data']);
                
                return $this->response->setJSON($result);
            } else {
                return $this->response->setJSON($result)->setStatusCode(400);
            }
            
        } catch (\Exception $e) {
            log_message('error', 'Certificate generation controller error: ' . $e->getMessage());
            return $this->response->setJSON([
                'success' => false,
                'message' => 'Certificate generation failed'
            ])->setStatusCode(500);
        }
    }
    
    /**
     * Build certificate data from database
     */
    protected function buildCertificateData(int $participantId, int $awardId): array
    {
        try {
            // Load models
            $participantModel = new ParticipantModel();
            $programModel = new ProgramModel();
            $awardModel = new ProgramAwardModel();
            $certificateModel = new ProgramCertificateModel();
            $contentBlockModel = new ProgramCertificateContentBlockModel();
            
            // Get participant data
            $participant = $participantModel->find($participantId);
            if (!$participant) {
                return ['success' => false, 'message' => 'Participant not found'];
            }
            
            // Get program data
            $program = $programModel->find($participant['program_id']);
            if (!$program) {
                return ['success' => false, 'message' => 'Program not found'];
            }
            
            // Get award data
            $award = $awardModel->find($awardId);
            if (!$award) {
                return ['success' => false, 'message' => 'Award not found'];
            }
            
            // Get certificate template
            $certificateTemplate = $certificateModel
                ->where('program_id', $program['id'])
                ->where('award_id', $awardId)
                ->where('is_active', 1)
                ->first();
                
            if (!$certificateTemplate) {
                return ['success' => false, 'message' => 'Certificate template not found'];
            }
            
            // Get content blocks
            $contentBlocks = $contentBlockModel
                ->where('certificate_id', $certificateTemplate['id'])
                ->where('is_active', 1)
                ->orderBy('id', 'ASC')
                ->findAll();
            
            // Build certificate data structure
            $certificateData = [
                'participant' => [
                    'id' => (int)$participant['id'],
                    'account_id' => $participant['account_id'],
                    'full_name' => $participant['full_name'],
                    'birthdate' => $participant['birthdate'],
                    'gender' => $participant['gender'],
                    'nationality' => $participant['nationality'],
                    'nationality_code' => $participant['nationality_code'],
                    'education_level' => $participant['education_level'],
                    'major' => $participant['major'],
                    'institution' => $participant['institution'],
                    'occupation' => $participant['occupation'],
                    'category' => $participant['category'],
                    'picture_url' => $participant['picture_url'],
                    'instagram_account' => $participant['instagram_account'],
                    'experiences' => $participant['experiences'],
                    'achievements' => $participant['achievements'],
                    'tshirt_size' => $participant['tshirt_size'],
                    'registration_date' => $participant['created_at']
                ],
                'program' => [
                    'id' => (int)$program['id'],
                    'name' => $program['name'],
                    'theme' => $program['theme'],
                    'start_date' => $program['start_date'],
                    'end_date' => $program['end_date']
                ],
                'award' => [
                    'id' => (int)$award['id'],
                    'title' => $award['title'],
                    'description' => $award['description'],
                    'award_type' => $award['award_type'],
                    'order_number' => (int)$award['order_number']
                ],
                'certificate_template' => [
                    'id' => (int)$certificateTemplate['id'],
                    'template_url' => $certificateTemplate['template_url'],
                    'template_type' => $certificateTemplate['template_type'],
                    'issue_date' => $certificateTemplate['issue_date'],
                    'published_at' => $certificateTemplate['published_at']
                ],
                'content_blocks' => array_map(function($block) {
                    return [
                        'id' => (int)$block['id'],
                        'type' => $block['type'],
                        'value' => $block['value'],
                        'x' => (int)$block['x'],
                        'y' => (int)$block['y'],
                        'font_size' => (int)$block['font_size'],
                        'font_family' => $block['font_family'],
                        'font_weight' => $block['font_weight'],
                        'text_align' => $block['text_align'],
                        'color' => $block['color']
                    ];
                }, $contentBlocks),
                'assignment_info' => [
                    'assigned_by' => session('user_id'),
                    'assigned_at' => date('c'),
                    'notes' => 'Generated via admin panel'
                ]
            ];
            
            return ['success' => true, 'data' => $certificateData];
            
        } catch (\Exception $e) {
            log_message('error', 'Build certificate data error: ' . $e->getMessage());
            return ['success' => false, 'message' => 'Failed to build certificate data'];
        }
    }
    
    /**
     * Save certificate generation record (optional)
     */
    protected function saveCertificateRecord(int $participantId, int $awardId, array $certificateData): void
    {
        try {
            // Save to participant_awards table or certificate_generations table
            $data = [
                'participant_id' => $participantId,
                'award_id' => $awardId,
                'certificate_id' => $certificateData['certificate_id'],
                'file_name' => $certificateData['file_name'],
                'file_size' => $certificateData['file_size'],
                'generated_at' => $certificateData['generated_at'],
                'created_at' => date('Y-m-d H:i:s')
            ];
            
            // Insert into your certificate_generations table or update participant_awards
            // Implementation depends on your database schema
            
        } catch (\Exception $e) {
            log_message('error', 'Save certificate record error: ' . $e->getMessage());
        }
    }
    
    /**
     * Download certificate as PDF
     * GET /api/certificates/{certificateId}/download
     */
    public function download($certificateId)
    {
        try {
            // Get certificate data from your database
            // This is a placeholder - implement based on your storage strategy
            
            // If you're storing the base64 data, decode and serve it
            // If you're storing file paths, serve the file
            // If you're generating on-demand, call the certificate service again
            
            return $this->response
                ->setHeader('Content-Type', 'application/pdf')
                ->setHeader('Content-Disposition', 'attachment; filename="certificate.pdf"')
                ->setBody($pdfContent);
                
        } catch (\Exception $e) {
            return $this->response->setJSON([
                'success' => false,
                'message' => 'Certificate download failed'
            ])->setStatusCode(404);
        }
    }
    
    /**
     * Health check endpoint
     * GET /api/certificates/health
     */
    public function health()
    {
        $health = $this->certificateService->checkHealth();
        return $this->response->setJSON($health);
    }
}
```

### 4. Update Routes

Add certificate routes to your API routes:

```php
<?php
// app/Config/Routes.php

// Existing YBB API routes
$routes->group('api/ybb', ['namespace' => 'App\Controllers\Api'], function($routes) {
    // Existing export routes
    $routes->post('export/participants', 'YbbExportController::exportParticipants');
    $routes->post('export/payments', 'YbbExportController::exportPayments');
    $routes->post('export/ambassadors', 'YbbExportController::exportAmbassadors');
    
    // NEW: Certificate routes
    $routes->group('certificates', function($routes) {
        $routes->post('generate', 'CertificatesApiController::generate');
        $routes->get('health', 'CertificatesApiController::health');
        $routes->get('(:segment)/download', 'CertificatesApiController::download/$1');
        $routes->get('placeholders', 'CertificatesApiController::getPlaceholders');
    });
});
```

### 5. Frontend Integration

Update your admin panel JavaScript to call the new certificate endpoints:

```javascript
// public/assets/js/certificate-manager.js

class CertificateManager {
    constructor() {
        this.baseUrl = '/api/ybb/certificates';
    }
    
    /**
     * Generate certificate for participant and award
     */
    async generateCertificate(participantId, awardId) {
        try {
            const response = await fetch(`${this.baseUrl}/generate`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-Requested-With': 'XMLHttpRequest'
                },
                body: JSON.stringify({
                    participant_id: participantId,
                    award_id: awardId
                })
            });
            
            const result = await response.json();
            
            if (result.success) {
                // Handle successful generation
                this.downloadCertificate(result.data);
                return result;
            } else {
                throw new Error(result.message || 'Certificate generation failed');
            }
            
        } catch (error) {
            console.error('Certificate generation error:', error);
            throw error;
        }
    }
    
    /**
     * Download certificate as PDF
     */
    downloadCertificate(certificateData) {
        // Convert base64 to blob and download
        const binaryString = atob(certificateData.file_data);
        const bytes = new Uint8Array(binaryString.length);
        
        for (let i = 0; i < binaryString.length; i++) {
            bytes[i] = binaryString.charCodeAt(i);
        }
        
        const blob = new Blob([bytes], { type: 'application/pdf' });
        const url = URL.createObjectURL(blob);
        
        const link = document.createElement('a');
        link.href = url;
        link.download = certificateData.file_name;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        URL.revokeObjectURL(url);
    }
    
    /**
     * Check certificate service health
     */
    async checkHealth() {
        try {
            const response = await fetch(`${this.baseUrl}/health`);
            return await response.json();
        } catch (error) {
            return {
                service: 'Certificate Generation Service',
                status: 'error',
                error: error.message
            };
        }
    }
}

// Usage in your admin panel
const certificateManager = new CertificateManager();

// Add to participant action buttons
function generateCertificate(participantId, awardId) {
    certificateManager.generateCertificate(participantId, awardId)
        .then(result => {
            showSuccessMessage('Certificate generated successfully');
        })
        .catch(error => {
            showErrorMessage('Certificate generation failed: ' + error.message);
        });
}
```

## Database Schema Updates

Ensure your database has the required tables and relationships as specified in the original documentation:

### Required Tables
- `participants` - Existing table
- `programs` - Existing table  
- `program_awards` - May need to be created
- `participant_awards` - Junction table for participant-award relationships
- `program_certificates` - Template storage
- `program_certificate_content_blocks` - Content positioning

### Sample Queries to Check/Create Tables

```sql
-- Check if program_awards table exists
SHOW TABLES LIKE 'program_awards';

-- Create program_awards if missing
CREATE TABLE IF NOT EXISTS `program_awards` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `program_id` int(11) NOT NULL,
  `title` varchar(255) NOT NULL,
  `description` mediumtext DEFAULT NULL,
  `award_type` enum('winner','runner_up','mention','other') DEFAULT 'winner',
  `order_number` int(11) DEFAULT 0,
  `is_active` tinyint(1) DEFAULT 1,
  `is_deleted` tinyint(1) DEFAULT 0,
  `created_at` datetime DEFAULT current_timestamp(),
  `updated_at` datetime DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  PRIMARY KEY (`id`),
  KEY `program_id` (`program_id`)
);

-- Create program_certificates table for templates
CREATE TABLE IF NOT EXISTS `program_certificates` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `program_id` int(11) NOT NULL,
  `award_id` int(11) NULL,
  `template_url` varchar(255) NOT NULL,
  `template_type` enum('image','pdf') NOT NULL DEFAULT 'pdf',
  `preview_url` varchar(255) DEFAULT NULL,
  `issue_date` date DEFAULT NULL,
  `published_at` datetime DEFAULT NULL,
  `is_active` tinyint(1) DEFAULT 1,
  `is_deleted` tinyint(1) DEFAULT 0,
  `created_at` datetime DEFAULT current_timestamp(),
  `updated_at` datetime DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  PRIMARY KEY (`id`),
  KEY `program_id` (`program_id`),
  KEY `award_id` (`award_id`)
);

-- Create content blocks table
CREATE TABLE IF NOT EXISTS `program_certificate_content_blocks` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `certificate_id` int(11) NOT NULL,
  `type` enum('text','placeholder') NOT NULL,
  `value` mediumtext NOT NULL,
  `x` int(11) NOT NULL,
  `y` int(11) NOT NULL,
  `font_size` int(11) DEFAULT 16,
  `font_family` varchar(100) DEFAULT 'Arial',
  `font_weight` varchar(50) DEFAULT 'normal',
  `text_align` varchar(20) DEFAULT 'left',
  `color` varchar(10) DEFAULT '#000000',
  `is_active` tinyint(1) DEFAULT 1,
  `is_deleted` tinyint(1) DEFAULT 0,
  `created_at` datetime DEFAULT current_timestamp(),
  `updated_at` datetime DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  PRIMARY KEY (`id`),
  KEY `certificate_id` (`certificate_id`)
);
```

## Testing the Integration

### 1. Health Check Test
```bash
curl -X GET "https://your-domain.com/api/ybb/certificates/health"
```

### 2. Certificate Generation Test
```bash
curl -X POST "https://your-domain.com/api/ybb/certificates/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "participant_id": 12345,
    "award_id": 1
  }'
```

## Migration Steps

### Phase 1: Setup (Week 1)
1. ✅ Update configuration files
2. ✅ Create CertificateService class
3. ✅ Add database tables if missing
4. ✅ Test connection to Python service

### Phase 2: Controller Implementation (Week 2)
1. ✅ Create/update CertificatesApiController
2. ✅ Implement certificate generation endpoint
3. ✅ Add route configurations
4. ✅ Test API endpoints

### Phase 3: Frontend Integration (Week 2)
1. ✅ Update admin panel JavaScript
2. ✅ Add certificate generation buttons
3. ✅ Implement download functionality
4. ✅ Test user interface

### Phase 4: Production Deployment (Week 3)
1. ✅ Deploy to staging environment
2. ✅ Conduct integration testing
3. ✅ Deploy to production
4. ✅ Monitor performance

## Error Handling

The Python service returns structured error responses. Handle these in your PHP code:

```php
// Example error handling
if (!$result['success']) {
    $errorCode = $result['error']['code'] ?? 'UNKNOWN_ERROR';
    $errorMessage = $result['error']['message'] ?? 'Unknown error occurred';
    
    switch ($errorCode) {
        case 'VALIDATION_ERROR':
            return $this->response->setJSON([
                'success' => false,
                'message' => 'Invalid certificate data: ' . $errorMessage
            ])->setStatusCode(400);
            
        case 'TEMPLATE_NOT_FOUND':
            return $this->response->setJSON([
                'success' => false,
                'message' => 'Certificate template not accessible: ' . $errorMessage
            ])->setStatusCode(404);
            
        case 'GENERATION_FAILED':
            return $this->response->setJSON([
                'success' => false,
                'message' => 'Certificate generation failed: ' . $errorMessage
            ])->setStatusCode(500);
            
        default:
            return $this->response->setJSON([
                'success' => false,
                'message' => 'Certificate processing error: ' . $errorMessage
            ])->setStatusCode(500);
    }
}
```

## Support and Troubleshooting

### Common Issues

1. **Connection Refused**: Check Python service URL and network connectivity
2. **Template Not Found**: Verify template URLs are accessible and valid
3. **Invalid Payload**: Ensure all required fields are present and properly formatted
4. **Timeout**: Increase timeout settings for large certificates

### Debugging

Enable debug logging in CodeIgniter:

```php
// app/Config/Logger.php
public $threshold = 1; // Enable debug logging
```

Monitor Python service logs for detailed error information.

## Security Considerations

1. **Authentication**: Ensure API requests are properly authenticated
2. **Authorization**: Verify user permissions before certificate generation
3. **Input Validation**: Sanitize all input data before sending to Python service
4. **Rate Limiting**: Implement rate limiting to prevent abuse
5. **Template Security**: Validate template URLs are from trusted domains

---

**Next Steps**: After implementing these changes, the YBB admin platform will have full certificate generation capabilities integrated with the Python service using the standardized `/api/ybb/certificates/` endpoint structure.
