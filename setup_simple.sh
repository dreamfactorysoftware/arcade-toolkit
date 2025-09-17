#!/bin/bash

# Simple Setup Script - No virtual environment
# For users who prefer system Python or have venv issues

echo "================================================"
echo "🚀 Simple Arcade DreamFactory Toolkit Setup"
echo "   (No virtual environment)"
echo "================================================"
echo ""

# Check Python
echo "📦 Checking Python..."
if ! command -v python3 >/dev/null 2>&1; then
    echo "❌ Python 3 not found. Please install Python 3.10+"
    exit 1
fi

python_version=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
echo "✅ Python $python_version found"
echo ""

# Install dependencies
echo "📦 Installing dependencies..."
echo "This will install packages to your system/user Python"
read -p "Continue? (y/n): " confirm
if [[ ! "$confirm" =~ ^[Yy]$ ]]; then
    echo "Installation cancelled"
    exit 0
fi

python3 -m pip install --user --upgrade pip
python3 -m pip install --user arcade-ai httpx loguru python-dotenv

echo "✅ Dependencies installed"
echo ""

# Get DreamFactory configuration
echo "🔐 DreamFactory Configuration"
echo "================================"
read -p "DreamFactory URL (without /api/v2) [http://localhost:8080]: " df_url
df_url=${df_url:-http://localhost:8080}

echo "Enter your DreamFactory API Key:"
read -s -p "API Key: " df_api_key
echo ""
echo ""

# Create .env file
echo "📝 Creating .env file..."
cat > .env <<EOF
DREAM_FACTORY_BASE_URL=$df_url
DREAM_FACTORY_API_KEY=$df_api_key
EOF
echo "✅ Configuration saved"
echo ""

# Test connection
echo "🔍 Testing DreamFactory connection..."
response=$(curl -s -o /dev/null -w "%{http_code}" \
    -X GET "$df_url/api/v2/system/environment" \
    -H "X-DreamFactory-API-Key: $df_api_key" \
    -H "Content-Type: application/json" 2>/dev/null || echo "000")

if [ "$response" = "200" ]; then
    echo "✅ Successfully connected to DreamFactory!"
else
    echo "⚠️  Could not connect (HTTP $response)"
    echo "Please check your URL and API key"
fi
echo ""

# Create simple test script
cat > test_simple.py <<'EOF'
#!/usr/bin/env python3
"""Simple test script - no virtual environment needed"""

import os
import json
import sys

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Load environment
from dotenv import load_dotenv
load_dotenv()

# Import toolkit
from arcade_dreamfactory.tools import list_services

# Mock context
class MockContext:
    def get_secret(self, key):
        return os.getenv(key)

# Test
print("Testing DreamFactory connection...")
try:
    context = MockContext()
    result = list_services(context)
    data = json.loads(result)
    print(f"✅ Success! Found {data['count']} services")
    for svc in data.get('services', [])[:3]:
        print(f"   - {svc['name']} ({svc['type']})")
except Exception as e:
    print(f"❌ Error: {e}")
    print("\nTroubleshooting:")
    print("1. Check .env file has correct URL and API key")
    print("2. Ensure DreamFactory is running")
    print("3. Verify API key has system permissions")
EOF

chmod +x test_simple.py

echo "================================================"
echo "✅ Simple Setup Complete!"
echo "================================================"
echo ""
echo "Test your setup:"
echo "   python3 test_simple.py"
echo ""
echo "Your configuration is in .env"
echo ""
echo "To use with Arcade CLI:"
echo "   arcade secret set DREAM_FACTORY_BASE_URL '$df_url'"
echo "   arcade secret set DREAM_FACTORY_API_KEY '<your-key>'"
echo ""
echo "================================================"