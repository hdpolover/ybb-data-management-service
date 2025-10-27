#!/bin/bash
# Test script for payment export using curl
# This script tests the payment export functionality and compares it with participant export

set -e  # Exit on error

BASE_URL="http://localhost:5000"
OUTPUT_DIR="/tmp/ybb_export_tests"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Create output directory
mkdir -p "$OUTPUT_DIR"

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}YBB Payment Export Test Suite${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Test 1: Health Check
echo -e "${YELLOW}Test 1: Health Check${NC}"
curl -s -X GET "$BASE_URL/health" | python3 -m json.tool || echo -e "${RED}❌ Health check failed${NC}"
echo -e "${GREEN}✅ Server is running${NC}"
echo ""
sleep 1

# Test 2: Payment Export (Metadata Mode)
echo -e "${YELLOW}Test 2: Payment Export - Metadata Mode${NC}"
PAYMENT_METADATA=$(curl -s -X POST "$BASE_URL/api/ybb/db/export/payments" \
  -H "Content-Type: application/json" \
  -d '{
    "filters": {
      "status": "all"
    },
    "options": {
      "template": "standard",
      "format": "excel",
      "filename": "Test_Payments_Export.xlsx",
      "sheet_name": "Payments"
    },
    "response_mode": "metadata"
  }')

echo "$PAYMENT_METADATA" | python3 -m json.tool || echo -e "${RED}❌ Failed to parse JSON${NC}"

# Extract export_id
PAYMENT_EXPORT_ID=$(echo "$PAYMENT_METADATA" | python3 -c "import sys, json; data=json.load(sys.stdin); print(data.get('data', {}).get('export_id', ''))" 2>/dev/null || echo "")

if [ -z "$PAYMENT_EXPORT_ID" ]; then
    echo -e "${RED}❌ Failed to get export_id from payment export${NC}"
    echo "Response: $PAYMENT_METADATA"
else
    echo -e "${GREEN}✅ Export ID: $PAYMENT_EXPORT_ID${NC}"
fi
echo ""
sleep 2

# Test 3: Download Payment Export (if we got an export_id)
if [ -n "$PAYMENT_EXPORT_ID" ]; then
    echo -e "${YELLOW}Test 3: Download Payment Export${NC}"
    PAYMENT_FILE="$OUTPUT_DIR/payment_export_${PAYMENT_EXPORT_ID:0:8}.xlsx"
    
    HTTP_CODE=$(curl -s -w "%{http_code}" -o "$PAYMENT_FILE" \
      -X GET "$BASE_URL/api/ybb/export/$PAYMENT_EXPORT_ID/download")
    
    echo "HTTP Status Code: $HTTP_CODE"
    
    if [ "$HTTP_CODE" = "200" ]; then
        if [ -f "$PAYMENT_FILE" ] && [ -s "$PAYMENT_FILE" ]; then
            FILE_SIZE=$(stat -f%z "$PAYMENT_FILE" 2>/dev/null || stat -c%s "$PAYMENT_FILE" 2>/dev/null)
            echo -e "${GREEN}✅ File downloaded successfully${NC}"
            echo "   File: $PAYMENT_FILE"
            echo "   Size: $FILE_SIZE bytes"
            
            # Check if it's a valid Excel file
            if xxd -l 2 "$PAYMENT_FILE" | grep -q "504b"; then
                echo -e "${GREEN}✅ Valid Excel file (PK signature found)${NC}"
            else
                echo -e "${RED}❌ Invalid Excel file (missing PK signature)${NC}"
                echo "First 100 bytes:"
                xxd -l 100 "$PAYMENT_FILE"
            fi
        else
            echo -e "${RED}❌ Download failed - file is empty or doesn't exist${NC}"
            cat "$PAYMENT_FILE"
        fi
    else
        echo -e "${RED}❌ Download failed with HTTP $HTTP_CODE${NC}"
        cat "$PAYMENT_FILE"
    fi
else
    echo -e "${YELLOW}⚠️  Skipping download test (no export_id)${NC}"
fi
echo ""
sleep 2

# Test 4: Direct Payment Export (File Response)
echo -e "${YELLOW}Test 4: Direct Payment Export - File Response${NC}"
PAYMENT_DIRECT_FILE="$OUTPUT_DIR/payment_export_direct.xlsx"

curl -v -X POST "$BASE_URL/api/ybb/db/export/payments" \
  -H "Content-Type: application/json" \
  -d '{
    "filters": {
      "status": "all"
    },
    "options": {
      "template": "standard",
      "format": "excel",
      "filename": "Direct_Payment_Export.xlsx",
      "sheet_name": "Payment Data"
    }
  }' \
  -o "$PAYMENT_DIRECT_FILE" 2>&1 | tee "$OUTPUT_DIR/payment_direct.log"

if [ -f "$PAYMENT_DIRECT_FILE" ] && [ -s "$PAYMENT_DIRECT_FILE" ]; then
    FILE_SIZE=$(stat -f%z "$PAYMENT_DIRECT_FILE" 2>/dev/null || stat -c%s "$PAYMENT_DIRECT_FILE" 2>/dev/null)
    echo -e "${GREEN}✅ Direct file export successful${NC}"
    echo "   File: $PAYMENT_DIRECT_FILE"
    echo "   Size: $FILE_SIZE bytes"
    
    # Check if it's Excel or JSON error
    if xxd -l 2 "$PAYMENT_DIRECT_FILE" | grep -q "504b"; then
        echo -e "${GREEN}✅ Valid Excel file${NC}"
    elif grep -q '"status"' "$PAYMENT_DIRECT_FILE"; then
        echo -e "${RED}❌ Received JSON error response instead of Excel file:${NC}"
        cat "$PAYMENT_DIRECT_FILE" | python3 -m json.tool
    else
        echo -e "${RED}❌ Unknown file format${NC}"
        echo "First 200 bytes:"
        xxd -l 200 "$PAYMENT_DIRECT_FILE"
    fi
else
    echo -e "${RED}❌ Direct export failed${NC}"
fi
echo ""
sleep 2

# Test 5: Participant Export for Comparison
echo -e "${YELLOW}Test 5: Participant Export - For Comparison${NC}"
PARTICIPANT_FILE="$OUTPUT_DIR/participant_export_comparison.xlsx"

HTTP_CODE=$(curl -s -w "%{http_code}" -o "$PARTICIPANT_FILE" \
  -X POST "$BASE_URL/api/ybb/db/export/participants" \
  -H "Content-Type: application/json" \
  -d '{
    "filters": {
      "status": "all"
    },
    "options": {
      "template": "standard",
      "format": "excel",
      "filename": "Test_Participants_Export.xlsx"
    }
  }')

echo "HTTP Status Code: $HTTP_CODE"

if [ "$HTTP_CODE" = "200" ] && [ -f "$PARTICIPANT_FILE" ] && [ -s "$PARTICIPANT_FILE" ]; then
    FILE_SIZE=$(stat -f%z "$PARTICIPANT_FILE" 2>/dev/null || stat -c%s "$PARTICIPANT_FILE" 2>/dev/null)
    echo -e "${GREEN}✅ Participant export successful${NC}"
    echo "   File: $PARTICIPANT_FILE"
    echo "   Size: $FILE_SIZE bytes"
else
    echo -e "${RED}❌ Participant export failed${NC}"
fi
echo ""

# Test 6: Payment Export with Detailed Template
echo -e "${YELLOW}Test 6: Payment Export - Detailed Template${NC}"
PAYMENT_DETAILED_FILE="$OUTPUT_DIR/payment_export_detailed.xlsx"

curl -s -X POST "$BASE_URL/api/ybb/db/export/payments" \
  -H "Content-Type: application/json" \
  -d '{
    "filters": {
      "status": "all"
    },
    "options": {
      "template": "detailed",
      "format": "excel",
      "filename": "Payment_Export_Detailed.xlsx",
      "sheet_name": "Detailed Payments"
    }
  }' \
  -o "$PAYMENT_DETAILED_FILE"

if [ -f "$PAYMENT_DETAILED_FILE" ] && [ -s "$PAYMENT_DETAILED_FILE" ]; then
    FILE_SIZE=$(stat -f%z "$PAYMENT_DETAILED_FILE" 2>/dev/null || stat -c%s "$PAYMENT_DETAILED_FILE" 2>/dev/null)
    if xxd -l 2 "$PAYMENT_DETAILED_FILE" | grep -q "504b"; then
        echo -e "${GREEN}✅ Detailed template export successful${NC}"
        echo "   File: $PAYMENT_DETAILED_FILE"
        echo "   Size: $FILE_SIZE bytes"
    else
        echo -e "${RED}❌ Not a valid Excel file${NC}"
    fi
else
    echo -e "${RED}❌ Detailed export failed${NC}"
fi
echo ""

# Summary
echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Test Summary${NC}"
echo -e "${BLUE}========================================${NC}"
echo "Output directory: $OUTPUT_DIR"
echo ""
echo "Files created:"
ls -lh "$OUTPUT_DIR"
echo ""
echo -e "${GREEN}✅ Tests completed!${NC}"
echo ""
echo "To view the Excel files, run:"
echo "  open $OUTPUT_DIR/*.xlsx"
echo ""
echo "To view logs:"
echo "  cat $OUTPUT_DIR/*.log"
