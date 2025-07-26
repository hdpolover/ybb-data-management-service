# 🧹 Automatic Cleanup System - Implementation Guide

## Overview

The YBB Data Management Flask API now includes an **Automatic Cleanup System** that prevents storage accumulation by automatically removing old export files while maintaining the most recent exports. This system ensures efficient storage management without manual intervention.

## 🚀 Key Features

### ✅ **Automatic File Cleanup**
- **Startup Cleanup**: Removes old files when the service starts
- **Export-Time Cleanup**: Cleans up before creating new exports  
- **Comprehensive Deletion**: Removes Excel files, ZIP archives, temporary files, and batch files
- **Configurable Limits**: Keep only the N most recent exports (default: 5)

### ✅ **Storage Management**
- **Storage Monitoring**: Track total files, size, and storage usage
- **Threshold Alerts**: Configurable warning and cleanup thresholds
- **Force Cleanup**: Admin endpoint for immediate cleanup
- **Flexible Configuration**: All settings configurable via config file

### ✅ **Smart Retention**
- **Recent Export Protection**: Always keeps the most recent exports
- **Time-Based Cleanup**: Optional cleanup based on file age
- **Selective Deletion**: Only removes export-related files
- **Safe Operations**: Handles file system errors gracefully

## 🛠️ Configuration Options

### Cleanup Settings (`config/ybb_export_config.py`)

```python
SYSTEM_CONFIG = {
    "cleanup": {
        "auto_cleanup_enabled": True,           # Enable/disable automatic cleanup
        "max_concurrent_exports": 5,           # Keep only the 5 most recent exports
        "cleanup_on_startup": True,            # Clean up when service starts
        "cleanup_on_export": True,             # Clean up before creating new exports
        "keep_temp_files_minutes": 30,         # How long to keep temp files
        "storage_warning_threshold_mb": 500,   # Warning threshold (500MB)
        "storage_cleanup_threshold_mb": 1000,  # Force cleanup threshold (1GB)
        "force_cleanup_after_days": 1          # Force cleanup after N days
    }
}
```

### Default Behavior
- ✅ **Enabled by default**: Cleanup runs automatically
- ✅ **5 Export Limit**: Keeps the 5 most recent exports
- ✅ **Startup & Export Cleanup**: Runs on service start and before new exports
- ✅ **30-Minute Temp Files**: Temporary files cleaned after 30 minutes

## 📋 How It Works

### 1. **Startup Process**
```
Service Starts → Check cleanup_on_startup → Clean Old Exports → Ready for Requests
```

### 2. **Export Creation Process**
```
New Export Request → Check cleanup_on_export → Clean Old Exports → Create New Export
```

### 3. **File Tracking**
- Service maintains a record of all exports with timestamps
- Files are sorted by creation time (newest first)
- Keeps only the N most recent exports (configurable)
- Deletes all associated files for older exports

## 🔧 API Endpoints

### Storage Information
```http
GET /api/ybb/storage/info
```

**Response:**
```json
{
  "total_exports": 3,
  "total_files": 8,
  "total_size_bytes": 245760,
  "total_size_mb": 0.23,
  "max_concurrent_exports": 5
}
```

### Force Cleanup
```http
POST /api/ybb/cleanup/force
```

**Response:**
```json
{
  "status": "success",
  "files_removed": 12,
  "message": "Cleanup completed successfully"
}
```

### Regular Cleanup
```http
POST /api/ybb/cleanup
```

**Response:**
```json
{
  "status": "success",
  "files_removed": 3,
  "message": "Expired exports cleaned up"
}
```

## 🧪 Testing the Cleanup System

### Manual Test
```bash
# Run the comprehensive test suite
python test_filename_enhancement.py
```

### Test Coverage
- ✅ **Configuration Loading**: Tests config-based cleanup settings
- ✅ **Multiple Exports**: Creates several exports to test cleanup
- ✅ **Storage Monitoring**: Verifies storage info tracking
- ✅ **Force Cleanup**: Tests immediate cleanup functionality
- ✅ **File Deletion**: Confirms files are actually removed

## ⚙️ Customization Examples

### 1. **Conservative Cleanup** (Keep more files)
```python
"cleanup": {
    "auto_cleanup_enabled": True,
    "max_concurrent_exports": 10,  # Keep 10 recent exports
    "cleanup_on_startup": False,   # Don't clean on startup
    "cleanup_on_export": True      # Only clean before new exports
}
```

### 2. **Aggressive Cleanup** (Minimal retention)
```python
"cleanup": {
    "auto_cleanup_enabled": True,
    "max_concurrent_exports": 2,   # Keep only 2 recent exports
    "cleanup_on_startup": True,
    "cleanup_on_export": True,
    "keep_temp_files_minutes": 5   # Clean temp files quickly
}
```

### 3. **Disabled Cleanup** (Manual only)
```python
"cleanup": {
    "auto_cleanup_enabled": False, # Disable automatic cleanup
    "max_concurrent_exports": 100, # High limit
    "cleanup_on_startup": False,
    "cleanup_on_export": False
}
```

## 🚨 Important Notes

### ⚠️ **Data Loss Prevention**
- Cleanup only removes **export files**, never source data
- Always keeps the most recent exports
- Configurable retention limits prevent accidental deletion
- Force cleanup requires explicit API call

### ⚠️ **Production Considerations**
- Monitor storage usage with `/api/ybb/storage/info`
- Set appropriate `max_concurrent_exports` based on usage patterns
- Consider daily cleanup jobs for high-volume environments
- Test cleanup behavior in staging before production deployment

### ⚠️ **File System Safety**
- Handles permission errors gracefully
- Logs all cleanup operations
- Continues operation even if some files can't be deleted
- Never deletes files outside the export directory

## 📊 Monitoring & Logging

### Log Messages
- `INFO`: Cleanup operations and file counts
- `WARNING`: Files that couldn't be deleted
- `ERROR`: Serious cleanup issues

### Example Log Output
```
INFO: Starting cleanup of old exports...
INFO: Found 8 total exports, keeping 5 most recent
INFO: Cleaned up 3 old exports, removed 7 files
WARNING: Could not delete temp_file.tmp: Permission denied
INFO: Cleanup completed successfully
```

## 🎯 Benefits

### ✅ **Automatic Storage Management**
- No manual intervention required
- Prevents storage accumulation
- Maintains recent exports for downloads

### ✅ **Configurable & Flexible**
- All settings configurable
- Enable/disable any cleanup feature
- Adapt to different usage patterns

### ✅ **Safe & Reliable**
- Never deletes source data
- Graceful error handling
- Comprehensive logging

### ✅ **Production Ready**
- Tested and validated
- API endpoints for monitoring
- Compatible with existing code

---

## 🔄 Migration from Previous Version

If you're upgrading from a version without automatic cleanup:

1. **Update Configuration**: Add cleanup settings to `ybb_export_config.py`
2. **Test Settings**: Run tests to verify cleanup behavior
3. **Monitor Initially**: Check storage info after deployment
4. **Adjust if Needed**: Modify `max_concurrent_exports` based on usage

The system is **backward compatible** and will work with existing export functionality while adding the new cleanup features.

---

*This cleanup system ensures your YBB Data Management Flask API maintains optimal storage usage while providing reliable export functionality.*
