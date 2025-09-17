#!/bin/bash
# Clean deployment script for Arcade toolkit

echo "🧹 Cleaning and deploying..."

# Ensure no .venv in project
rm -rf .venv 2>/dev/null

# Deploy with global arcade
echo "🚀 Deploying with arcade..."
arcade deploy

echo "✅ Done!"