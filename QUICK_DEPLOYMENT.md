# 🚀 Quick Deployment Checklist for files.ybbfoundation.com

## ✅ **Environment Variables to Set:**

**Essential Variables:**
```bash
FLASK_ENV=production
FLASK_APP=app.py
SECRET_KEY=your-secure-secret-key-here
API_HOST=0.0.0.0
API_PORT=5000
LOG_LEVEL=INFO
```

**Optional Variables:**
```bash
MAX_CONTENT_LENGTH=104857600
CORS_ORIGINS=https://files.ybbfoundation.com,https://ybbfoundation.com
```

## ✅ **Files to Upload:**

1. **All your project files** (app.py, config/, api/, services/, etc.)
2. **requirements.txt** ✓
3. **runtime.txt** ✓ 
4. **Procfile** ✓
5. **Optional: .env.production** (rename to .env)

## ❌ **What You DON'T Need:**

- ~~PYTHONPATH~~ (virtual environments handle this automatically)
- ~~Complex path configurations~~
- ~~Manual sys.path modifications~~

## 🧪 **Test Your Deployment:**

1. Visit: `https://files.ybbfoundation.com/health`
2. Should return: `{"status": "healthy", ...}`
3. Check logs for any import errors

## 🔧 **If You Get Import Errors:**

Only then consider adding:
```bash
PYTHONPATH=/home/yourusername/public_html
```

But most likely, you won't need it!
