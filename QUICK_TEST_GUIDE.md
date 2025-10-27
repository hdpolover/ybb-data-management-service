# Quick Test Guide - Payment Export Fix

## 🚀 Quick Start (2 minutes)

### Step 1: Start the Server (if not running)
```bash
cd /Users/mit06/Desktop/personal-projects/ybb-data-management-service
python app.py
```

### Step 2: Run the Test Script
```bash
python test_payment_export.py
```

That's it! The script will test everything and show you the results.

---

## 🧪 Alternative: Manual Curl Test

### Test 1: Simple Payment Export
```bash
curl -X POST http://localhost:5000/api/ybb/db/export/payments \
  -H "Content-Type: application/json" \
  -d '{"filters": {"status": "all"}, "options": {"template": "standard"}}' \
  -o /tmp/payment_test.xlsx

# Check if it's a valid Excel file
file /tmp/payment_test.xlsx
# Should show: "Microsoft Excel 2007+"
```

### Test 2: With Custom Filename
```bash
curl -X POST http://localhost:5000/api/ybb/db/export/payments \
  -H "Content-Type: application/json" \
  -d '{
    "filters": {"status": "all"},
    "options": {
      "template": "standard",
      "filename": "My_Custom_Payment_Export.xlsx",
      "sheet_name": "Payment Data"
    }
  }' \
  -o /tmp/my_payments.xlsx

# Verify
ls -lh /tmp/my_payments.xlsx
open /tmp/my_payments.xlsx
```

### Test 3: Compare with Participant Export
```bash
# Payment export
curl -X POST http://localhost:5000/api/ybb/db/export/payments \
  -H "Content-Type: application/json" \
  -d '{"filters": {"status": "all"}}' \
  -o /tmp/payments.xlsx

# Participant export
curl -X POST http://localhost:5000/api/ybb/db/export/participants \
  -H "Content-Type: application/json" \
  -d '{"filters": {"status": "all"}}' \
  -o /tmp/participants.xlsx

# Check both
ls -lh /tmp/*.xlsx
```

---

## ✅ What to Look For

### Success Indicators:
- ✅ Status code: 200
- ✅ Content-Type: `application/vnd.openxmlformats-officedocument.spreadsheetml.sheet`
- ✅ File size: > 5000 bytes (depending on data)
- ✅ File starts with `PK` (ZIP header for Excel)
- ✅ Filename is descriptive (includes date, program ID)
- ✅ File opens in Excel/Numbers

### Failure Indicators:
- ❌ Status code: 404, 500
- ❌ JSON error response instead of file
- ❌ File size < 100 bytes
- ❌ File doesn't start with `PK`
- ❌ Generic filename without date/context

---

## 🔍 Quick Diagnostics

### Check Server Status:
```bash
curl http://localhost:5000/health | python3 -m json.tool
```

### Check Database Connection:
```bash
curl http://localhost:5000/api/ybb/db/test-connection | python3 -m json.tool
```

### Get Metadata (doesn't download file):
```bash
curl -X POST http://localhost:5000/api/ybb/db/export/payments \
  -H "Content-Type: application/json" \
  -d '{"filters": {"status": "all"}, "response_mode": "metadata"}' \
  | python3 -m json.tool
```

---

## 📝 What Was Fixed

1. **Better Filenames**: Now includes program ID and formatted date
   - Before: `YBB_Payments_Export_20251027_104523.xlsx`
   - After: `YBB_Payments_Export_ProgramAll_27-10-2025_104523.xlsx`

2. **File Availability**: Better error handling when file doesn't exist
   - Clear error messages with export_id
   - Helpful suggestions for users

3. **Validation**: Checks that file content exists before attempting download
   - Returns 404 with details if file missing
   - Logs export_id for debugging

---

## 🐛 Troubleshooting

### "Server not running"
```bash
# Check if Python is running
ps aux | grep python | grep app.py

# Start it
cd /Users/mit06/Desktop/personal-projects/ybb-data-management-service
python app.py
```

### "File not available" error
- Check logs: `tail -f logs/*.log`
- Export might have expired (default: 7 days)
- Try creating a new export
- Check if data exists in database

### "Connection refused"
- Server might be on different port
- Check app.py for port (default: 5000)
- Try: `http://localhost:5000` or `http://127.0.0.1:5000`

### Invalid Excel file
- Check first 2 bytes: `xxd -l 2 /tmp/payment_test.xlsx`
- Should show: `504b` (PK header)
- If JSON response, pipe to: `cat /tmp/payment_test.xlsx | python3 -m json.tool`

---

## 📊 Test Output Examples

### Successful Export:
```
✅ Server is running: YBB Data Processing Service
📤 Sending request to: http://localhost:5000/api/ybb/db/export/payments
📊 Status Code: 200
✅ Received Excel file: YBB_Payments_Export_Program101_27-10-2025_104523.xlsx
📏 File size: 45678 bytes
💾 Saved to: /tmp/YBB_Payments_Export_Program101_27-10-2025_104523.xlsx
✅ Valid Excel file (PK signature found)
```

### Failed Export:
```
❌ Export failed: Export file is not available. The file may have expired.
export_id: abc123-def456
suggestion: Please create a new export
```

---

## 🎯 Key Improvements

| Feature | Before | After |
|---------|--------|-------|
| Filename | `YBB_Payments_Export_timestamp.xlsx` | `YBB_Payments_Export_Program{id}_date_timestamp.xlsx` |
| Error Message | "File not found" | Detailed with export_id and suggestions |
| Logging | Minimal | Comprehensive with request tracking |
| Validation | None | Checks file content exists |
| Download Fallback | None | Default filename if missing |

---

## 📁 Output Files

After running tests, check:
```bash
ls -lh /tmp/*.xlsx
```

You should see files like:
- `Test_Payments_Export.xlsx`
- `YBB_Payments_Export_ProgramAll_27-10-2025_*.xlsx`
- `Direct_Payment_Export.xlsx`

Open them to verify content:
```bash
open /tmp/*.xlsx
```

---

## Need Help?

1. Run: `python test_payment_export.py`
2. Check output for specific errors
3. Review logs: `tail -50 logs/ybb_api.log`
4. Test database: `curl http://localhost:5000/api/ybb/db/test-connection`
