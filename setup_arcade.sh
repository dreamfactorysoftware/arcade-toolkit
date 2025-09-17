#!/bin/bash

# Arcade DreamFactory Toolkit Setup Script
# This script automates the setup process for testing the toolkit with Arcade

set -e

echo "================================================"
echo "🚀 Arcade DreamFactory Toolkit Setup"
echo "================================================"
echo ""

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to prompt for input with a default value
prompt_with_default() {
    local prompt="$1"
    local default="$2"
    local response

    read -p "$prompt [$default]: " response
    echo "${response:-$default}"
}

# Step 1: Check Python version
echo "📦 Checking Python version..."
if command_exists python3; then
    python_version=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
    echo "   ✅ Python $python_version found"
else
    echo "   ❌ Python 3 not found. Please install Python 3.10+"
    exit 1
fi

# Step 2: Create virtual environment
echo ""
echo "🔧 Setting up virtual environment..."

# Check if we're in the right directory
if [ ! -f "pyproject.toml" ]; then
    echo "   ❌ Error: Not in the arcade-toolkit directory"
    echo "   Please run this script from the arcade-toolkit folder"
    exit 1
fi

# Try to create virtual environment
if [ ! -d ".venv" ]; then
    echo "   Creating virtual environment..."
    if command_exists python3; then
        python3 -m venv .venv
        if [ $? -ne 0 ]; then
            echo "   ❌ Failed to create virtual environment"
            echo "   Trying alternative method..."
            # Try with explicit venv module
            python3 -m pip install --user virtualenv
            python3 -m virtualenv .venv
        fi
    else
        echo "   ❌ Python 3 not found"
        exit 1
    fi

    # Verify venv was created
    if [ ! -d ".venv" ]; then
        echo "   ❌ Virtual environment creation failed"
        echo ""
        echo "   Manual fix:"
        echo "   1. Install python3-venv: sudo apt-get install python3-venv (Ubuntu/Debian)"
        echo "      or: brew install python3 (macOS)"
        echo "   2. Create venv manually: python3 -m venv .venv"
        echo "   3. Run this script again"
        exit 1
    fi
    echo "   ✅ Virtual environment created"
else
    echo "   ✅ Virtual environment already exists"
fi

# Activate virtual environment - handle different platforms
echo "   Activating virtual environment..."
if [ -f ".venv/bin/activate" ]; then
    source .venv/bin/activate
elif [ -f ".venv/Scripts/activate" ]; then
    # Windows Git Bash / MSYS
    source .venv/Scripts/activate
else
    echo "   ❌ Cannot find activation script"
    echo "   Looking for activate script..."
    find .venv -name "activate" -type f 2>/dev/null
    echo ""
    echo "   Manual activation:"
    echo "   - Linux/Mac: source .venv/bin/activate"
    echo "   - Windows: .venv\\Scripts\\activate"
    echo ""
    echo "   Continuing without activation - you may need to activate manually"

    # Set a flag to use .venv/bin/python directly
    USE_VENV_PYTHON=1
fi

if [ -z "$USE_VENV_PYTHON" ]; then
    echo "   ✅ Virtual environment activated"
fi

# Step 3: Install dependencies
echo ""
echo "📦 Installing dependencies..."

# Use venv python directly if not activated
if [ ! -z "$USE_VENV_PYTHON" ]; then
    echo "   Using virtual environment Python directly..."
    .venv/bin/python -m pip install --upgrade pip >/dev/null 2>&1
    .venv/bin/python -m pip install -r requirements.txt
    PIP_CMD=".venv/bin/python -m pip"
    PYTHON_CMD=".venv/bin/python"
else
    pip install --upgrade pip >/dev/null 2>&1
    pip install -r requirements.txt
    PIP_CMD="pip"
    PYTHON_CMD="python"
fi
echo "   ✅ Dependencies installed"

# Step 4: Get configuration from user
echo ""
echo "🔐 DreamFactory Configuration"
echo "================================"
echo "Please provide your DreamFactory credentials:"
echo ""

# Get DreamFactory URL
default_url="http://localhost:8080"
echo "Enter your DreamFactory URL (without /api/v2)"
df_url=$(prompt_with_default "URL" "$default_url")

# Get API Key
echo ""
echo "Enter your DreamFactory API Key"
echo "(To create one: DreamFactory Admin → Apps → Create New App)"
read -s -p "API Key: " df_api_key
echo ""

# Step 5: Create .env file
echo ""
echo "📝 Creating configuration file..."
cat > .env <<EOF
# DreamFactory Configuration
DREAM_FACTORY_BASE_URL=$df_url
DREAM_FACTORY_API_KEY=$df_api_key

# Arcade Configuration (optional)
# ARCADE_API_KEY=your-arcade-api-key
EOF
echo "   ✅ Configuration saved to .env"

# Step 6: Test DreamFactory connection
echo ""
echo "🔍 Testing DreamFactory connection..."
response=$(curl -s -o /dev/null -w "%{http_code}" \
    -X GET "$df_url/api/v2/system/environment" \
    -H "X-DreamFactory-API-Key: $df_api_key" \
    -H "Content-Type: application/json" 2>/dev/null || echo "000")

if [ "$response" = "200" ]; then
    echo "   ✅ Successfully connected to DreamFactory!"
else
    echo "   ⚠️  Could not connect to DreamFactory (HTTP $response)"
    echo "   Please check your URL and API key"
fi

# Step 7: Create test script
echo ""
echo "📄 Creating test script..."
cat > test_local.py <<'EOF'
#!/usr/bin/env python3
"""Test script for DreamFactory Arcade Toolkit - Local Testing"""

import os
import sys
import json
from dotenv import load_dotenv

# Add the current directory to path to import our toolkit
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Load environment variables
load_dotenv()

# Import our toolkit modules
from arcade_dreamfactory.tools import (
    list_services,
    list_database_tables,
    list_storage_services,
    list_files
)

# Mock context for local testing
class MockContext:
    """Mock context for testing without Arcade server"""
    def get_secret(self, key):
        env_key = key.replace("DREAM_FACTORY_", "DREAM_FACTORY_")
        value = os.getenv(env_key)
        if not value:
            raise ValueError(f"Missing environment variable: {env_key}")
        return value

def test_toolkit():
    """Test toolkit functions locally"""
    context = MockContext()

    print("🧪 Testing DreamFactory Toolkit (Local Mode)")
    print("=" * 50)

    # Test 1: List services
    print("\n1. Testing list_services...")
    try:
        result = list_services(context)
        data = json.loads(result)
        print(f"   ✅ Found {data['count']} services")
        if data['services']:
            for svc in data['services'][:3]:
                print(f"      - {svc['name']} ({svc['type']})")
    except Exception as e:
        print(f"   ❌ Error: {e}")

    # Test 2: List storage services
    print("\n2. Testing list_storage_services...")
    try:
        result = list_storage_services(context)
        data = json.loads(result)
        print(f"   ✅ Found {data['count']} storage services")
        if data['storage_services']:
            for svc in data['storage_services'][:3]:
                print(f"      - {svc['name']} ({svc['type']})")
    except Exception as e:
        print(f"   ❌ Error: {e}")

    # Test 3: List database tables (if available)
    print("\n3. Testing database operations...")
    try:
        services_result = list_services(context, service_type="mysql")
        services = json.loads(services_result)

        if services['services']:
            db_name = services['services'][0]['name']
            print(f"   Using database: {db_name}")

            tables_result = list_database_tables(context, db_name)
            tables = json.loads(tables_result)
            print(f"   ✅ Found {tables['count']} tables")
            if tables['tables']:
                for table in tables['tables'][:5]:
                    print(f"      - {table}")
        else:
            print("   ⚠️  No MySQL services found")
    except Exception as e:
        print(f"   ❌ Error: {e}")

    # Test 4: List files (if storage available)
    print("\n4. Testing file operations...")
    try:
        # First check if 'local' storage exists
        storage_result = list_storage_services(context)
        storage_data = json.loads(storage_result)

        storage_service = None
        for svc in storage_data.get('storage_services', []):
            if svc['type'] == 'local' or 'local' in svc['name'].lower():
                storage_service = svc['name']
                break

        if storage_service:
            print(f"   Using storage service: {storage_service}")
            files_result = list_files(context, storage_service, "/")
            files = json.loads(files_result)
            print(f"   ✅ Found {files['file_count']} files")
        else:
            print("   ⚠️  No local storage service found")
    except Exception as e:
        print(f"   ❌ Error: {e}")

    print("\n" + "=" * 50)
    print("✅ Local testing complete!")
    print("\nNext steps:")
    print("1. Install Arcade CLI: pip install arcade-ai")
    print("2. Set up Arcade secrets: arcade secret set DREAM_FACTORY_BASE_URL '...'")
    print("3. Deploy toolkit: arcade deploy")
    print("4. Test with agents: See ARCADE_SETUP.md for examples")

if __name__ == "__main__":
    test_toolkit()
EOF

chmod +x test_local.py
echo "   ✅ Test script created: test_local.py"

# Step 8: Install Arcade CLI (optional)
echo ""
echo "📦 Arcade CLI Installation"
read -p "Would you like to install Arcade CLI now? (y/n): " install_arcade
if [[ "$install_arcade" =~ ^[Yy]$ ]]; then
    if [ ! -z "$USE_VENV_PYTHON" ]; then
        .venv/bin/python -m pip install arcade-ai
    else
        pip install arcade-ai
    fi
    echo "   ✅ Arcade CLI installed"
    echo ""
    echo "   Next: Run 'arcade login' to connect to your Arcade account"
else
    echo "   ⚠️  Skipping Arcade CLI installation"
    echo "   You can install it later with: ${PIP_CMD} install arcade-ai"
fi

# Step 9: Summary
echo ""
echo "================================================"
echo "✅ Setup Complete!"
echo "================================================"
echo ""
echo "Your toolkit is configured and ready to test!"
echo ""
echo "📋 Quick Start Commands:"
echo ""
if [ ! -z "$USE_VENV_PYTHON" ]; then
    echo "⚠️  Virtual environment not activated. Use these commands:"
    echo ""
    echo "1. Activate virtual environment first:"
    echo "   source .venv/bin/activate  # Linux/Mac"
    echo "   OR"
    echo "   .venv\\Scripts\\activate  # Windows"
    echo ""
    echo "2. Then test locally:"
    echo "   python test_local.py"
    echo ""
    echo "   OR run directly without activation:"
    echo "   .venv/bin/python test_local.py"
else
    echo "1. Test locally (without Arcade):"
    echo "   python test_local.py"
fi
echo ""
echo "2. Set up Arcade secrets (if Arcade CLI installed):"
echo "   arcade secret set DREAM_FACTORY_BASE_URL '$df_url'"
echo "   arcade secret set DREAM_FACTORY_API_KEY 'your-api-key'"
echo ""
echo "3. Deploy to Arcade:"
echo "   arcade deploy"
echo ""
echo "4. Serve locally with Arcade:"
echo "   arcade serve"
echo ""
echo "📚 Documentation:"
echo "   - Setup Guide: ARCADE_SETUP.md"
echo "   - README: README.md"
echo "   - Arcade Docs: https://docs.arcade.dev"
echo ""
echo "Need help? Check ARCADE_SETUP.md for troubleshooting tips!"
echo "================================================"