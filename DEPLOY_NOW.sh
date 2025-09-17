#!/bin/bash

echo "🚀 Arcade Toolkit Deployment Script"
echo "===================================="
echo ""

# Check if arcade is installed globally
if command -v arcade &> /dev/null; then
    echo "✅ Found global arcade CLI"
    ARCADE_CMD="arcade"
else
    echo "❌ Arcade CLI not found globally"
    echo "Install with: pip install arcade-ai"
    exit 1
fi

# Check login status
echo ""
echo "📝 Checking login status..."
if $ARCADE_CMD worker list &> /dev/null; then
    echo "✅ Already logged in"
else
    echo "⚠️  Not logged in. Running login..."
    $ARCADE_CMD login
fi

# Validate files exist
echo ""
echo "🔍 Validating configuration files..."
if [ ! -f "worker.toml" ]; then
    echo "❌ worker.toml not found"
    exit 1
fi
echo "✅ worker.toml found"

if [ ! -f "pyproject.toml" ]; then
    echo "❌ pyproject.toml not found"
    exit 1
fi
echo "✅ pyproject.toml found"

if [ ! -d "arcade_dreamfactory" ]; then
    echo "❌ arcade_dreamfactory directory not found"
    exit 1
fi
echo "✅ arcade_dreamfactory package found"

# Display current configuration
echo ""
echo "📋 Current Configuration:"
echo "------------------------"
echo "Worker ID: $(grep '^id' worker.toml | cut -d'"' -f2)"
echo "Package: arcade_dreamfactory"
echo ""

# Deploy
echo "🚀 Starting deployment..."
echo "========================"
$ARCADE_CMD deploy

# Check deployment status
if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Deployment successful!"
    echo ""
    echo "📊 View your deployment:"
    echo "  - Dashboard: $ARCADE_CMD dashboard"
    echo "  - Workers: $ARCADE_CMD worker list"
    echo "  - Logs: $ARCADE_CMD worker logs dreamfactory-toolkit"
else
    echo ""
    echo "❌ Deployment failed"
    echo ""
    echo "Troubleshooting steps:"
    echo "1. Ensure you're logged in: $ARCADE_CMD login"
    echo "2. Check worker.toml format"
    echo "3. Verify package structure"
    echo "4. Try verbose mode: $ARCADE_CMD deploy --verbose"
fi