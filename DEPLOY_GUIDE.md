# Arcade Toolkit Deployment Guide

## Prerequisites Complete ✅
- `arcade.toml` - Toolkit configuration
- `worker.toml` - Worker deployment configuration
- `pyproject.toml` - Package dependencies
- Arcade CLI installed and accessible via `./arcade`

## Deploy Your Toolkit

### 1. Login to Arcade
```bash
./arcade login
```

### 2. Set Required Secrets
```bash
# Set your DreamFactory credentials
./arcade secret set DREAM_FACTORY_BASE_URL "https://your-instance.dreamfactory.com"
./arcade secret set DREAM_FACTORY_API_KEY "your-api-key-here"

# Verify secrets are set
./arcade secret list
```

### 3. Deploy the Toolkit
```bash
# Deploy to Arcade Cloud
./arcade deploy

# Or test locally first
./arcade serve
```

### 4. Test Your Deployed Toolkit
```bash
# Open the Arcade dashboard
./arcade dashboard

# Or test with chat interface
./arcade chat
```

## Deployment Status Commands
```bash
# Check deployment status
./arcade status

# View deployment logs
./arcade logs

# List deployed toolkits
./arcade show
```

## Troubleshooting

### Authentication Issues
If you get "Not logged in" errors:
```bash
./arcade logout
./arcade login
```

### Secret Validation
Ensure your secrets match the names in `arcade.toml`:
- `DREAM_FACTORY_BASE_URL`
- `DREAM_FACTORY_API_KEY`

### Local Testing
Before deploying to cloud, test locally:
```bash
# Set secrets locally
export DREAM_FACTORY_BASE_URL="https://your-instance.dreamfactory.com"
export DREAM_FACTORY_API_KEY="your-api-key"

# Serve locally
./arcade serve --port 8000
```

## Next Steps After Deployment
1. Access the Arcade dashboard to see your toolkit
2. Test individual tools through the UI
3. Share your toolkit ID with team members
4. Monitor usage and errors through the dashboard