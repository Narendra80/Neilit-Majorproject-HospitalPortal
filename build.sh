#!/usr/bin/env bash
set -o errexit

echo "📦 Installing Python dependencies..."
pip install -r requirements.txt

echo "🎨 Collecting static files..."
python manage.py collectstatic --no-input

echo "🗄️ Running database migrations..."
python manage.py migrate

echo "👤 Creating admin user (if needed)..."
python create_superuser.py

echo "✅ Build completed successfully!"