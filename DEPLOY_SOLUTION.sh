#!/bin/bash

echo "🚀 ARCADE DEPLOYMENT SOLUTION"
echo "=============================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Step 1: Re-authenticate
echo -e "${YELLOW}Step 1: Re-authenticating...${NC}"
echo "------------------------------"
arcade logout 2>/dev/null
echo "Logged out. Now logging in..."
arcade login

if [ $? -ne 0 ]; then
    echo -e "${RED}❌ Login failed. Please check your credentials.${NC}"
    exit 1
fi
echo -e "${GREEN}✅ Login successful${NC}"
echo ""

# Step 2: Verify authentication
echo -e "${YELLOW}Step 2: Verifying authentication...${NC}"
echo "------------------------------------"
arcade worker list > /tmp/worker_list.txt 2>&1

if grep -q "Not logged in" /tmp/worker_list.txt; then
    echo -e "${RED}❌ Still not authenticated properly${NC}"
    echo "Try manual login: arcade login"
    exit 1
else
    echo -e "${GREEN}✅ Authentication verified${NC}"
    cat /tmp/worker_list.txt | head -5
fi
echo ""

# Step 3: Clean and prepare
echo -e "${YELLOW}Step 3: Preparing deployment...${NC}"
echo "---------------------------------"
# Ensure no .venv in directory
if [ -d ".venv" ]; then
    echo "Removing .venv directory..."
    rm -rf .venv
fi

# Validate files
if [ ! -f "worker.toml" ]; then
    echo -e "${RED}❌ worker.toml not found${NC}"
    exit 1
fi

if [ ! -f "pyproject.toml" ]; then
    echo -e "${RED}❌ pyproject.toml not found${NC}"
    exit 1
fi

if [ ! -d "arcade_dreamfactory" ]; then
    echo -e "${RED}❌ arcade_dreamfactory directory not found${NC}"
    exit 1
fi

echo -e "${GREEN}✅ All required files present${NC}"
echo ""

# Step 4: Deploy with multiple attempts
echo -e "${YELLOW}Step 4: Deploying toolkit...${NC}"
echo "------------------------------"

# First attempt - normal
echo "Attempt 1: Normal deployment"
arcade deploy 2>&1 | tee /tmp/deploy_output.txt

if grep -q "Successfully deployed" /tmp/deploy_output.txt; then
    echo -e "${GREEN}✅ Deployment successful!${NC}"
    exit 0
fi

# Check for specific errors
if grep -q "Expecting value" /tmp/deploy_output.txt; then
    echo -e "${YELLOW}⚠️  Got JSON parsing error. Trying alternative approach...${NC}"

    # Second attempt - with environment variables
    echo "Attempt 2: With debug environment"
    ARCADE_DEBUG=1 arcade deploy 2>&1 | tee /tmp/deploy_output2.txt

    if grep -q "Successfully deployed" /tmp/deploy_output2.txt; then
        echo -e "${GREEN}✅ Deployment successful!${NC}"
        exit 0
    fi
fi

# If still failing, provide diagnostics
echo ""
echo -e "${RED}❌ Deployment failed after multiple attempts${NC}"
echo ""
echo "📊 Diagnostics:"
echo "---------------"
echo "1. Error output:"
grep -E "Error|error|failed|Failed" /tmp/deploy_output.txt | head -5

echo ""
echo "2. Next steps to try:"
echo "   a) Test locally: arcade serve"
echo "   b) Check status: https://status.arcade.dev"
echo "   c) Get support: support@arcade.dev"
echo ""
echo "3. Alternative deployment:"
echo "   - Try from a different network"
echo "   - Use a VPN if behind a firewall"
echo "   - Create a new API key at https://arcade.dev/dashboard"
echo ""
echo "4. Manual verification:"
echo "   python3 -c 'from arcade_dreamfactory import *; print(\"✅ Package OK\")'"
echo ""
echo "Log saved to: /tmp/deploy_output.txt"