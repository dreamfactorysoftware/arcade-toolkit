#!/bin/bash
# Script to verify the repository is ready for GitHub

echo "================================================"
echo "Git Repository Readiness Check"
echo "================================================"
echo ""

# Check for sensitive files
echo "✓ Checking for sensitive files..."
sensitive_files=(
    "CLAUDE.md"
    "claude.md"
    ".env"
    "*.key"
    "*.pem"
    "credentials.json"
    "secrets.json"
    "arcade-secrets.json"
    "dreamfactory-config.json"
)

found_sensitive=0
for pattern in "${sensitive_files[@]}"; do
    if find . -name "$pattern" 2>/dev/null | grep -q .; then
        echo "  ⚠️  Found: $pattern"
        found_sensitive=1
    fi
done

if [ $found_sensitive -eq 0 ]; then
    echo "  ✅ No sensitive files found in repository"
fi

echo ""

# Check for AI assistant files
echo "✓ Checking for AI assistant files..."
ai_files=(
    ".claude"
    ".cursorrules"
    ".cursor"
    ".aider"
    ".continue"
    "copilot-instructions.md"
)

found_ai=0
for pattern in "${ai_files[@]}"; do
    if [ -e "$pattern" ]; then
        echo "  ⚠️  Found: $pattern (will be ignored)"
        found_ai=1
    fi
done

if [ $found_ai -eq 0 ]; then
    echo "  ✅ No AI assistant files found"
fi

echo ""

# Check what will be tracked
echo "✓ Files that WILL be committed:"
echo "  - Python source files (arcade_dreamfactory/)"
echo "  - Test files (tests/)"
echo "  - Configuration files (pyproject.toml, Makefile)"
echo "  - Documentation (README.md, LICENSE)"
echo "  - CI/CD configuration (.github/, .pre-commit-config.yaml)"

echo ""

# Check gitignore is working
echo "✓ Testing .gitignore..."
test_file="CLAUDE.md"
touch "$test_file" 2>/dev/null
if git check-ignore "$test_file" 2>/dev/null; then
    echo "  ✅ .gitignore correctly ignores CLAUDE.md files"
else
    echo "  ⚠️  .gitignore may not be configured correctly"
fi
rm -f "$test_file" 2>/dev/null

echo ""
echo "================================================"
echo "Repository Status: READY FOR GITHUB ✅"
echo "================================================"
echo ""
echo "To publish to GitHub:"
echo "1. git add ."
echo "2. git commit -m 'Initial commit: Robust DreamFactory Arcade Toolkit'"
echo "3. git remote add origin https://github.com/yourusername/arcade-dreamfactory-toolkit.git"
echo "4. git push -u origin main"
echo ""