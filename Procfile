web: gunicorn wsgi:application --bind 0.0.0.0:${PORT:-5000} --workers 2 --timeout 120 --preload
release: echo "Application ready for deployment"
