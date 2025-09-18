#!/bin/bash

echo "🔍 DEBUG: Arcade Deployment Diagnostics"
echo "========================================"
echo ""

# 1. Check environment
echo "1️⃣ Environment Check:"
echo "----------------------"
echo "Current directory: $(pwd)"
echo "Python version: $(python3 --version)"
echo "Arcade CLI version: $(arcade --version 2>&1)"
echo ""

# 2. Check authentication
echo "2️⃣ Authentication Check:"
echo "-------------------------"
arcade worker list 2>&1 | head -5
echo ""

# 3. Validate configuration files
echo "3️⃣ Configuration Files:"
echo "------------------------"
echo "worker.toml exists: $([ -f worker.toml ] && echo '✅' || echo '❌')"
echo "pyproject.toml exists: $([ -f pyproject.toml ] && echo '✅' || echo '❌')"
echo "arcade_dreamfactory exists: $([ -d arcade_dreamfactory ] && echo '✅' || echo '❌')"
echo ""

# 4. Show worker.toml content
echo "4️⃣ worker.toml Content:"
echo "------------------------"
cat worker.toml
echo ""

# 5. Test package import
echo "5️⃣ Package Import Test:"
echo "------------------------"
python3 -c "
import sys
sys.path.insert(0, '.')
try:
    from arcade_dreamfactory import *
    print('✅ Package imports successfully')
except Exception as e:
    print(f'❌ Import error: {e}')
"
echo ""

# 6. Try deployment with verbose output
echo "6️⃣ Attempting Deployment (verbose):"
echo "------------------------------------"
arcade deploy --verbose 2>&1

echo ""
echo "7️⃣ Alternative: Try with debug environment:"
echo "--------------------------------------------"
ARCADE_DEBUG=1 arcade deploy 2>&1 | head -50