# How to Use the Arcade CLI Tool

The Arcade CLI (`arcade-ai` package) is already installed in your virtual environment!

## Option 1: Activate Virtual Environment (Recommended)

```bash
# Activate the virtual environment
source .venv/bin/activate

# Now you can use arcade directly
arcade --help
arcade login
arcade secret set DREAM_FACTORY_BASE_URL "http://localhost:8080"
arcade secret set DREAM_FACTORY_API_KEY "your-api-key"
arcade deploy
```

## Option 2: Use Without Activation

```bash
# Use the full path to arcade in the virtual environment
.venv/bin/arcade --help
.venv/bin/arcade login
.venv/bin/arcade secret set DREAM_FACTORY_BASE_URL "http://localhost:8080"
.venv/bin/arcade secret set DREAM_FACTORY_API_KEY "your-api-key"
.venv/bin/arcade deploy
```

## Option 3: Create an Alias (Convenient)

Add this to your ~/.bashrc or ~/.zshrc:

```bash
alias arcade="/root/arcade-dev/arcade-toolkit/.venv/bin/arcade"
```

Then reload your shell:
```bash
source ~/.bashrc  # or source ~/.zshrc
```

Now you can use `arcade` from anywhere!

## Option 4: Install Globally (Not Recommended)

If you really want it globally (outside the virtual environment):

```bash
# Install globally with pip
pip install --user arcade-ai

# Or with sudo (system-wide)
sudo pip install arcade-ai
```

⚠️ **Note**: Global installation can cause conflicts with other Python projects.

## Quick Test

Test that the CLI is working:

```bash
# With activated venv
source .venv/bin/activate
arcade --version

# Without activation
.venv/bin/arcade --version
```

You should see:
```
arcade-ai version 2.2.1
```

## Common Arcade CLI Commands

### Authentication
```bash
# Login to Arcade Cloud
arcade login

# Check login status
arcade whoami

# Logout
arcade logout
```

### Secret Management
```bash
# Set secrets for your toolkit
arcade secret set DREAM_FACTORY_BASE_URL "http://localhost:8080"
arcade secret set DREAM_FACTORY_API_KEY "your-api-key"

# List all secrets
arcade secret list

# Remove a secret
arcade secret remove SECRET_NAME
```

### Toolkit Development
```bash
# Create a new toolkit
arcade new my_toolkit

# Show installed toolkits
arcade show

# Deploy your toolkit
arcade deploy

# Serve toolkit locally
arcade serve

# Test tools with chat interface
arcade chat

# Open dashboard
arcade dashboard
```

## Troubleshooting

### "arcade: command not found"
You're not in the virtual environment. Run:
```bash
source .venv/bin/activate
```

### "No module named 'arcade_ai'"
The import name changed. Use:
- CLI package: `arcade-ai` (with hyphen)
- Import in Python: `import arcade_tdk` or `import arcadepy`

### "Permission denied"
Make sure the arcade binary is executable:
```bash
chmod +x .venv/bin/arcade
```

### Check Installation
Verify everything is installed:
```bash
.venv/bin/pip list | grep arcade
```

Should show:
- arcade-ai (CLI tool)
- arcade-core (Core library)
- arcade-tdk (Tool Development Kit)
- arcadepy (Python client)

## Next Steps

1. **Login to Arcade**:
   ```bash
   source .venv/bin/activate
   arcade login
   ```

2. **Configure Secrets**:
   ```bash
   arcade secret set DREAM_FACTORY_BASE_URL "http://your-instance"
   arcade secret set DREAM_FACTORY_API_KEY "your-key"
   ```

3. **Deploy Your Toolkit**:
   ```bash
   arcade deploy
   ```

The Arcade CLI is ready to use! 🚀