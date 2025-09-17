# Arcade Toolkit Setup Guide

## Prerequisites

1. **Arcade Account**: Sign up at https://arcade.dev
2. **DreamFactory Instance**: Running locally or in cloud
3. **Python 3.10+** and **Poetry** installed
4. **uv** package manager (recommended by Arcade)

## Step 1: Install Dependencies

```bash
# Install uv if not already installed
curl -LsSf https://astral.sh/uv/install.sh | sh

# Or with pip
pip install uv

# Create virtual environment and install dependencies
cd arcade-toolkit
uv venv --seed -p 3.10
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install with Poetry
poetry install

# Or install arcade-ai directly
pip install arcade-ai
```

## Step 2: Configure DreamFactory API Access

### Get your DreamFactory API Key

1. Log into DreamFactory Admin Console
2. Navigate to **Apps** → **Create New App**
3. Configure:
   - **App Name**: `arcade_toolkit`
   - **Description**: `Arcade AI Toolkit Access`
   - **Role**: Select an admin role or create one with full permissions:
     - System Access: Full
     - Service Access: Full for all database and file services
4. Click **Create Application**
5. Copy the generated API key

### Test DreamFactory Connection

```bash
# Test your DreamFactory connection
curl -X GET "https://your-instance.dreamfactory.com/api/v2/system/service" \
  -H "X-DreamFactory-API-Key: your-api-key" \
  -H "Content-Type: application/json"
```

## Step 3: Configure Arcade Secrets

### Option A: Via Arcade CLI

```bash
# Install Arcade CLI
pip install arcade-ai

# Login to Arcade
arcade login

# Set your secrets
arcade secret set DREAM_FACTORY_BASE_URL "https://your-instance.dreamfactory.com"
arcade secret set DREAM_FACTORY_API_KEY "your-dreamfactory-api-key"

# Verify secrets are set
arcade secret list
```

### Option B: Via Arcade Web Dashboard

1. Go to https://arcade.dev/dashboard
2. Navigate to **Secrets** section
3. Add two secrets:
   - **Name**: `DREAM_FACTORY_BASE_URL`
     **Value**: `https://your-instance.dreamfactory.com` (no /api/v2)
   - **Name**: `DREAM_FACTORY_API_KEY`
     **Value**: Your DreamFactory API key

## Step 4: Build and Test the Toolkit

### Build the toolkit

```bash
# Build the package
make build

# Or manually with Poetry
poetry build
```

### Test locally with Arcade

```bash
# Start local Arcade server
arcade serve

# In another terminal, you can now use the Arcade client
python3 test_arcade.py
```

## Step 5: Create Test Script

Create `test_arcade.py`:

```python
from arcadepy import Arcade
import json

# Initialize Arcade client
client = Arcade()  # Uses ARCADE_API_KEY env var or ~/.arcade/config

def test_toolkit():
    """Test all major toolkit functions"""

    print("🔧 Testing DreamFactory Arcade Toolkit\n")

    # Test 1: List all services
    print("1. Listing all services...")
    try:
        result = client.tools.execute(
            tool_name="DreamFactory.list_services",
            input={}
        )
        services = json.loads(result.output.value)
        print(f"   ✅ Found {services['count']} services")
        for svc in services['services'][:3]:  # Show first 3
            print(f"      - {svc['name']} ({svc['type']})")
    except Exception as e:
        print(f"   ❌ Error: {e}")

    # Test 2: List storage services
    print("\n2. Listing storage services...")
    try:
        result = client.tools.execute(
            tool_name="DreamFactory.list_storage_services",
            input={}
        )
        storage = json.loads(result.output.value)
        print(f"   ✅ Found {storage['count']} storage services")
    except Exception as e:
        print(f"   ❌ Error: {e}")

    # Test 3: List tables (if you have a database service)
    print("\n3. Testing database operations...")
    try:
        # First, get a database service name
        services_result = client.tools.execute(
            tool_name="DreamFactory.list_services",
            input={"service_type": "mysql"}
        )
        services = json.loads(services_result.output.value)

        if services['services']:
            db_service = services['services'][0]['name']
            print(f"   Using database service: {db_service}")

            # List tables
            tables_result = client.tools.execute(
                tool_name="DreamFactory.list_database_tables",
                input={"service_name": db_service}
            )
            tables = json.loads(tables_result.output.value)
            print(f"   ✅ Found {tables['count']} tables")
        else:
            print("   ⚠️  No database services found")
    except Exception as e:
        print(f"   ❌ Error: {e}")

    # Test 4: File operations (if you have storage service)
    print("\n4. Testing file operations...")
    try:
        # List files in root
        files_result = client.tools.execute(
            tool_name="DreamFactory.list_files",
            input={
                "storage_service": "local",  # or your storage service name
                "path": "/"
            }
        )
        files = json.loads(files_result.output.value)
        print(f"   ✅ Found {files['file_count']} files")
    except Exception as e:
        print(f"   ❌ Error: {e}")

    print("\n✅ Toolkit testing complete!")

if __name__ == "__main__":
    test_toolkit()
```

## Step 6: Deploy to Arcade Cloud (Optional)

```bash
# Deploy your toolkit to Arcade cloud
arcade deploy

# You'll see output like:
# Deploying toolkit to Arcade...
# Toolkit deployed successfully!
# Toolkit ID: dreamfactory_toolkit_v1
# Status: Active
```

## Step 7: Use with AI Agents

### With LangChain

```python
from langchain_arcade import ArcadeToolManager
from langchain.agents import create_react_agent

# Initialize Arcade tools
manager = ArcadeToolManager(api_key="your-arcade-api-key")
tools = manager.get_tools(toolkits=["DreamFactory"])

# Create agent
agent = create_react_agent(tools=tools, llm=your_llm)

# Use the agent
result = agent.invoke({
    "input": "List all MySQL databases and show me the tables in the first one"
})
```

### With CrewAI

```python
from crewai import Agent, Task, Crew
from arcade_crewai import ArcadeToolkit

# Get DreamFactory tools
toolkit = ArcadeToolkit(toolkit_name="DreamFactory")

# Create agent with tools
database_agent = Agent(
    role="Database Administrator",
    goal="Manage database operations",
    tools=toolkit.get_tools(),
    llm=your_llm
)

# Create task
task = Task(
    description="Create a new MySQL service for production",
    agent=database_agent
)

# Execute
crew = Crew(agents=[database_agent], tasks=[task])
result = crew.kickoff()
```

## Step 8: Verify Everything Works

Run this verification script:

```bash
#!/bin/bash
# save as verify_setup.sh

echo "🔍 Verifying Arcade Toolkit Setup"
echo "=================================="

# Check Python
echo -n "✓ Python 3.10+: "
python3 --version

# Check Poetry
echo -n "✓ Poetry: "
poetry --version 2>/dev/null || echo "Not installed (optional)"

# Check uv
echo -n "✓ uv: "
uv --version 2>/dev/null || echo "Not installed (optional)"

# Check Arcade CLI
echo -n "✓ Arcade CLI: "
arcade --version 2>/dev/null || echo "Not installed - run: pip install arcade-ai"

# Check environment
echo -n "✓ Virtual env: "
if [[ "$VIRTUAL_ENV" != "" ]]; then
    echo "Active ✅"
else
    echo "Not active - run: source .venv/bin/activate"
fi

# Check Arcade secrets
echo "✓ Checking Arcade secrets..."
arcade secret list 2>/dev/null | grep -E "DREAM_FACTORY" || echo "   Secrets not configured"

echo ""
echo "Ready to test? Run: python3 test_arcade.py"
```

## Troubleshooting

### "Module not found" error
```bash
# Make sure arcade-ai is installed
pip install arcade-ai

# Or install from your built package
pip install dist/arcade_dreamfactory-*.whl
```

### "Authentication failed" error
- Verify your DreamFactory API key has system-level permissions
- Check the URL doesn't have /api/v2 at the end (toolkit adds it)
- Test with curl first to ensure DreamFactory is accessible

### "Tool not found" error
- Make sure toolkit is deployed: `arcade deploy`
- Or running locally: `arcade serve`
- Check tool names match exactly (case-sensitive)

### "Service not found" error
- Use `list_services()` first to see available services
- Service names are case-sensitive
- Ensure the service is active in DreamFactory

## Available Tools Reference

### System Management
- `list_services` - View all services
- `create_database_api_complete` - One-step API setup
- `create_database_service` - Create new database connection
- `create_role` - Define permissions
- `create_app` - Generate API keys

### Database Operations
- `list_database_tables` - Explore database structure
- `get_table_schema` - View table columns
- `query_database_table` - SELECT with filtering
- `insert_records` - INSERT data
- `update_records` - UPDATE data
- `delete_records` - DELETE data
- `execute_sql_query` - Custom SELECT queries

### File Storage
- `list_storage_services` - View storage backends
- `list_files` - Browse directories
- `read_file` - Get file content
- `write_file` - Create/update files
- `copy_file` - Duplicate files
- `move_file` - Relocate files
- `delete_file` - Remove files
- `search_files` - Find by pattern

## Next Steps

1. **Test basic operations** with the test script
2. **Create your first database API** using `create_database_api_complete`
3. **Integrate with your AI agents** using LangChain or CrewAI
4. **Build automation workflows** combining multiple tools

## Support

- Arcade Docs: https://docs.arcade.dev
- DreamFactory Docs: https://www.dreamfactory.com/docs/
- Arcade Discord: https://discord.gg/arcade-ai