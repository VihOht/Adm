#!/bin/bash

# Railway deployment test script
echo "🚀 Testing Railway deployment configuration..."

# Set environment variables for production-like testing
export DEBUG=false
export SECRET_KEY="test-secret-key-for-deployment"

# Collect static files
echo "📦 Collecting static files..."
python manage.py collectstatic --noinput

# Run database migrations
echo "🗄️ Running database migrations..."
python manage.py migrate

# Test Gunicorn configuration
echo "🌐 Testing Gunicorn configuration..."
echo "Starting server with Gunicorn (press Ctrl+C to stop)..."
gunicorn Adm.wsgi:application -c gunicorn.conf.py
