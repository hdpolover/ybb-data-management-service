# PYTHONPATH Configuration Guide

## 🎯 **Important Note: You Probably DON'T Need PYTHONPATH!**

If you're using a **virtual environment** (like `.venv`), Python automatically finds your modules and you typically **don't need to set PYTHONPATH**.

## 🔍 **When Do You Need PYTHONPATH?**

### ✅ **You DON'T need PYTHONPATH if:**
- Using a virtual environment (`.venv`, `venv`, `conda`, etc.)
- Your modules are in the same directory as your main app
- Running locally with `python app.py`

### ⚠️ **You MIGHT need PYTHONPATH if:**
- Running on shared hosting without virtual environment support
- Your hosting platform doesn't automatically include the current directory
- Getting `ModuleNotFoundError` even with proper file structure

## 🏠 **For Local Development (Virtual Environment)**
```bash
# NO PYTHONPATH needed!
# Just activate your virtual environment:
source .venv/bin/activate  # Linux/Mac
# or
.venv\Scripts\Activate.ps1  # Windows PowerShell
```

## 🚀 **For Production Hosting**

### Option 1: No PYTHONPATH (Recommended)
Most modern hosting platforms handle this automatically.

### Option 2: Set PYTHONPATH (Only if needed)
```bash
PYTHONPATH=/home/yourusername/public_html
```

## 🔧 **How to Set It Up:**

### In Hosting Control Panel:
1. Go to Environment Variables section
2. Add: `PYTHONPATH` = `/home/yourusername/public_html`
3. Replace `yourusername` with your actual hosting username

### In .env file:
```bash
# Add this line to your .env file
PYTHONPATH=/path/to/your/app/root
```

## 🚨 **Common Issues Without PYTHONPATH:**
- `ModuleNotFoundError: No module named 'config'`
- `ImportError: cannot import name 'get_config'`
- `No module named 'api'` or `'services'`

## ✅ **Test Your PYTHONPATH:**
```python
import sys
print("Python path:", sys.path)
```

Your application root should appear in the list.

## 📁 **File Structure Reference:**
```
/home/yourusername/public_html/
├── app.py                 ← Main Flask app
├── config/               ← Config package  
│   ├── __init__.py
│   ├── main_config.py
│   └── ybb_export_config.py
├── api/                  ← API routes
├── services/             ← Business logic
└── requirements.txt
```

With `PYTHONPATH=/home/yourusername/public_html`, Python can find all these modules.
