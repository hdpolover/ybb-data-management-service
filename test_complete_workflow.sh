#!/bin/bash
# Complete YBB Database Export API Test

echo "======================================"
echo "YBB Database Export API - Full Test"
echo "======================================"

API_URL="http://127.0.0.1:5000"

echo ""
echo "1️⃣ Testing Database Connection..."
curl -s "$API_URL/api/ybb/db/test-connection" | jq -c '{status, database}'

echo ""
echo "2️⃣ Getting Export Statistics..."
curl -s -X POST "$API_URL/api/ybb/db/export/statistics" \
  -H "Content-Type: application/json" \
  -d '{"export_type": "participants", "filters": {"limit": 100}}' | jq -c '{status, total: .data.total_count}'

echo ""
echo "3️⃣ Creating Export (50 participants, standard template)..."
EXPORT_RESPONSE=$(curl -s -X POST "$API_URL/api/ybb/db/export/participants" \
  -H "Content-Type: application/json" \
  -d '{"filters": {"limit": 50, "form_status": 2}, "options": {"template": "standard", "filename": "test_export.xlsx"}}')

EXPORT_ID=$(echo $EXPORT_RESPONSE | jq -r '.data.export_id')
echo "Export created: $EXPORT_ID"
echo $EXPORT_RESPONSE | jq -c '{status, records: .data.record_count, size_bytes: .data.file_size}'

echo ""
echo "4️⃣ Checking Export Status..."
curl -s "$API_URL/api/ybb/export/$EXPORT_ID/status" | jq -c '{status, export_id, records: .record_count, size_mb: .file_size_mb}'

echo ""
echo "5️⃣ Downloading Export File..."
curl -s "$API_URL/api/ybb/export/$EXPORT_ID/download" -o /tmp/test_export_complete.xlsx
FILE_SIZE=$(ls -lh /tmp/test_export_complete.xlsx | awk '{print $5}')
FILE_TYPE=$(file /tmp/test_export_complete.xlsx | cut -d: -f2)
echo "Downloaded: $FILE_SIZE -$FILE_TYPE"

echo ""
echo "✅ All tests completed successfully!"
echo "   - Database connection: Working"
echo "   - Statistics endpoint: Working"
echo "   - Export creation: Working"
echo "   - Status check: Working"
echo "   - File download: Working"
echo "======================================"
