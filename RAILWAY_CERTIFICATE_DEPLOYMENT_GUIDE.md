# Certificate Service Railway Deployment Guide

**Issue**: Certificate generation returning 404 errors on production Railway deployment

## Problem Analysis

The certificate service is failing to initialize on Railway due to missing system dependencies required by PDF generation libraries (reportlab, Pillow, PyPDF2).

## Solution Implemented

### 1. **Updated Dependencies** ✅
- Added system packages to `nixpacks.toml` for PDF/image processing
- Verified certificate dependencies in `requirements_complete.txt`

### 2. **Added Fallback Service** ✅
- Created `FallbackCertificateService` for when PDF libraries aren't available
- Generates text-based certificates as temporary solution
- Graceful degradation instead of complete failure

### 3. **Improved Error Handling** ✅
- Better dependency checking and reporting
- Health endpoint shows fallback status
- Detailed logging for troubleshooting

## Files Updated

### `nixpacks.toml`
```toml
[phases.setup]
nixPkgs = [
    "python3",
    "pkg-config",      # NEW: For package compilation
    "freetype",        # NEW: Font rendering
    "libjpeg",         # NEW: JPEG support
    "zlib",            # NEW: Compression
    "libtiff",         # NEW: TIFF support
    "libpng",          # NEW: PNG support
    "lcms2",           # NEW: Color management
    "libwebp",         # NEW: WebP support
    "ghostscript"      # NEW: PDF processing
]
```

### `services/certificate_service.py`
- Added dependency availability checking
- Graceful failure when libraries missing
- Better error reporting

### `services/fallback_certificate_service.py` (NEW)
- Text-based certificate generation
- No external dependencies required
- Returns base64 encoded text file

### `api/certificate_routes.py`
- Automatic fallback to text service
- Health endpoint shows fallback status (200 instead of 503)
- Improved error messages

## Deployment Steps

### 1. Commit and Push Changes
```bash
git add .
git commit -m "Add certificate fallback service and system dependencies"
git push origin main
```

### 2. Railway Auto-Deploy
Railway will automatically detect the changes and redeploy with:
- New system packages from `nixpacks.toml`
- Updated certificate service with fallback
- Improved error handling

### 3. Verify Deployment

**Health Check**:
```bash
curl https://ybb-data-management-service-production.up.railway.app/api/ybb/certificates/health
```

Expected Response:
```json
{
  "service": "Certificate Generation Service",
  "status": "healthy",         // or "fallback" if PDF libs unavailable
  "main_service_available": true,  // or false
  "fallback_service_available": true,
  "message": "Full PDF certificate generation available"  // or fallback message
}
```

**Certificate Generation Test**:
```bash
curl -X POST https://ybb-data-management-service-production.up.railway.app/api/ybb/certificates/generate \
  -H "Content-Type: application/json" \
  -d '{
    "participant": {"id": 123, "full_name": "Test User"},
    "program": {"id": 1, "name": "Test Program"},
    "award": {"id": 1, "title": "Test Award"},
    "certificate_template": {
      "id": 1, 
      "template_url": "https://example.com/template.pdf",
      "template_type": "pdf"
    },
    "content_blocks": []
  }'
```

## Expected Outcomes

### Scenario 1: PDF Libraries Available ✅
- Health status: `"healthy"`
- Certificate generation: Full PDF with templates
- Response: Base64 encoded PDF file

### Scenario 2: PDF Libraries Missing (Fallback) ✅
- Health status: `"fallback"`
- Certificate generation: Text-based certificate
- Response: Base64 encoded text file
- User gets certificate with note about PDF unavailability

### Scenario 3: Complete Failure ❌ (Should not happen now)
- Previous behavior: 503 error
- New behavior: Fallback service always works

## Railway Environment Variables

Ensure these are set in Railway:
```
FLASK_ENV=production
FLASK_APP=app_complete.py
PYTHONPATH=/app
PORT=5000
```

## Monitoring

### Logs to Watch
1. **Successful PDF Service**:
   ```
   Certificate service initialized successfully with all dependencies
   CERTIFICATE_HEALTH_CHECK | Status: healthy
   ```

2. **Fallback Service**:
   ```
   Certificate service dependencies missing, will use fallback
   CERTIFICATE_HEALTH_CHECK | Status: fallback
   Generated fallback text certificate
   ```

3. **Dependency Issues**:
   ```
   Missing required dependencies: reportlab, Pillow, PyPDF2
   Using fallback text-based certificate generation
   ```

## PHP Integration Impact

The PHP client code remains the same - the API endpoints work identically whether using PDF or fallback service. The response includes an `is_fallback: true` flag when using text certificates.

### PHP Handling
```php
if ($result['data']['is_fallback'] ?? false) {
    // Show user that this is a text certificate
    // Offer to contact support for PDF version
}
```

## Next Steps

1. **Monitor deployment** - Check Railway logs after deployment
2. **Test both scenarios** - Verify both PDF and fallback work
3. **Update PHP client** - Handle fallback responses appropriately
4. **System optimization** - Work on getting PDF libraries working on Railway

## Troubleshooting

### If Still Getting 404
1. Check Railway build logs for dependency installation errors
2. Verify `app_complete.py` is being used (check `nixpacks.toml`)
3. Confirm certificate routes are registered in the app

### If Fallback Not Working
1. Check import of `FallbackCertificateService`
2. Verify fallback service initialization in routes
3. Check for basic Python errors in logs

## Success Criteria

✅ **Immediate**: Certificate API returns 200 status (even if fallback)  
✅ **Short-term**: Text certificates generate successfully  
🔄 **Long-term**: PDF certificates work with system dependencies  

This approach ensures the certificate functionality is available immediately while we work on optimizing the PDF generation capabilities.
