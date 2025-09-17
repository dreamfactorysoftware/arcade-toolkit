# 🚀 Quick Start Guide - Arcade DreamFactory Toolkit

## 5-Minute Setup

### 1️⃣ Cross-Platform Python Setup (Most Compatible)

```bash
# Works on Windows, macOS, and Linux
python3 setup.py

# Follow the prompts to enter:
# - DreamFactory URL (e.g., http://localhost:8080)
# - DreamFactory API Key
```

### 2️⃣ Bash Setup (Linux/macOS)

```bash
# Full setup with virtual environment
./setup_arcade.sh

# OR simple setup without venv (if having issues)
./setup_simple.sh
```

### 3️⃣ Manual Setup

```bash
# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Copy and configure environment
cp .env.example .env
# Edit .env with your DreamFactory credentials
```

## 🧪 Test Your Setup

### Local Testing (No Arcade Required)

```bash
# Run the local test script
python test_local.py

# You should see:
# ✅ Found X services
# ✅ Found X storage services
# ✅ Found X tables
```

### With Arcade CLI

```bash
# Install Arcade CLI
pip install arcade-ai

# Login to Arcade
arcade login

# Set secrets
arcade secret set DREAM_FACTORY_BASE_URL "http://localhost:8080"
arcade secret set DREAM_FACTORY_API_KEY "your-api-key"

# Deploy toolkit
arcade deploy

# Or serve locally
arcade serve
```

## 📝 Your First API

### Create Complete Database API (One Command!)

```python
from arcade_dreamfactory.tools import create_database_api_complete

# This single command:
# 1. Creates database service
# 2. Sets up role with permissions
# 3. Generates API key
result = create_database_api_complete(
    context,
    service_name="my_api",
    database_type="mysql",
    host="localhost",
    database="mydb",
    username="user",
    password="pass"
)

# Returns:
# {
#   "api_endpoint": "http://localhost:8080/api/v2/my_api",
#   "api_key": "generated-key-abc123",
#   "usage": { ... examples ... }
# }
```

## 🔧 Common Operations

### List Everything

```python
# See all services
list_services(context)

# See all database tables
list_database_tables(context, "service_name")

# See all files
list_files(context, "storage_service", "/")
```

### Database Operations

```python
# Query data
query_database_table(
    context,
    service_name="mysql_prod",
    table_name="users",
    filter="active = true",
    limit=10
)

# Insert data
insert_records(
    context,
    service_name="mysql_prod",
    table_name="events",
    records=[{"event": "login", "user_id": 123}]
)
```

### File Operations

```python
# Read file
read_file(context, "local", "config.json")

# Write file
write_file(
    context,
    "s3_bucket",
    "reports/new.txt",
    "Report content"
)

# Search files
search_files(context, "local", "*.pdf")
```

## 🎯 Quick Wins

### 1. Get Your API Running (2 min)
```bash
./setup_arcade.sh
python test_local.py
```

### 2. Create Your First Database API (30 sec)
Use `create_database_api_complete()` - it does everything!

### 3. Query Your Data (10 sec)
Use the generated API key to start querying immediately

## 📚 Next Steps

- **Full Setup Guide**: See [ARCADE_SETUP.md](ARCADE_SETUP.md)
- **All Tools Reference**: See [README.md](README.md)
- **Integrate with AI**: Use with LangChain, CrewAI, or OpenAI

## ⚡ Pro Tips

1. **Use `create_database_api_complete`** - It's a one-stop solution
2. **Service names are dynamic** - One config, access all services
3. **Test locally first** - Use `test_local.py` before deploying
4. **Check service names** - They're case-sensitive

## 🆘 Troubleshooting

| Issue | Solution |
|-------|----------|
| ".venv/bin/activate: No such file or directory" | Use `python3 setup.py` instead, or `./setup_simple.sh` |
| "Module 'venv' not found" | Install: `sudo apt-get install python3-venv` (Ubuntu) or use `setup_simple.sh` |
| "Module not found" | Run `pip install -r requirements.txt` |
| "Authentication failed" | Check API key has system permissions |
| "Service not found" | Run `list_services()` to see exact names |
| "No tables found" | Check database service is configured correctly |
| Virtual environment issues | Use `python3 setup.py` - it handles venv problems automatically |

## 🔗 Links

- **Arcade Docs**: https://docs.arcade.dev
- **DreamFactory Admin**: http://your-instance/admin
- **Get API Key**: DreamFactory → Apps → Create New App → Copy Key

---

**Ready in 5 minutes!** 🎉 Run `./setup_arcade.sh` and start building!