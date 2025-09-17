#!/usr/bin/env python3
"""
Cross-platform setup script for Arcade DreamFactory Toolkit
Works on Windows, macOS, and Linux
"""

import os
import sys
import subprocess
import json
from pathlib import Path


def run_command(cmd, capture=True, shell=False):
    """Run a command and return the result"""
    try:
        if capture:
            result = subprocess.run(
                cmd,
                shell=shell,
                capture_output=True,
                text=True,
                check=True
            )
            return result.stdout.strip()
        else:
            subprocess.run(cmd, shell=shell, check=True)
            return True
    except subprocess.CalledProcessError as e:
        if capture:
            return None
        return False
    except FileNotFoundError:
        return None


def check_python():
    """Check Python version"""
    print("📦 Checking Python version...")
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 10):
        print(f"❌ Python 3.10+ required (you have {version.major}.{version.minor})")
        return False
    print(f"✅ Python {version.major}.{version.minor} found")
    return True


def create_venv():
    """Create virtual environment"""
    print("\n🔧 Setting up virtual environment...")

    venv_path = Path(".venv")

    if venv_path.exists():
        print("✅ Virtual environment already exists")
        return venv_path

    print("Creating virtual environment...")

    # Try to create venv
    try:
        subprocess.run([sys.executable, "-m", "venv", ".venv"], check=True)
        print("✅ Virtual environment created")
        return venv_path
    except subprocess.CalledProcessError:
        print("⚠️  Failed to create virtual environment")
        print("\nTrying alternative method...")

        # Try installing virtualenv
        subprocess.run([sys.executable, "-m", "pip", "install", "--user", "virtualenv"], check=False)

        try:
            subprocess.run([sys.executable, "-m", "virtualenv", ".venv"], check=True)
            print("✅ Virtual environment created with virtualenv")
            return venv_path
        except:
            print("❌ Could not create virtual environment")
            print("\nYou may need to install python3-venv:")
            print("  Ubuntu/Debian: sudo apt-get install python3-venv")
            print("  macOS: Should work by default")
            print("  Windows: Should work by default")
            return None


def get_pip_command(venv_path):
    """Get the correct pip command for the platform"""
    if venv_path:
        if os.name == 'nt':  # Windows
            pip = venv_path / "Scripts" / "pip.exe"
            python = venv_path / "Scripts" / "python.exe"
        else:  # Unix-like
            pip = venv_path / "bin" / "pip"
            python = venv_path / "bin" / "python"

        if pip.exists():
            return str(python), [str(python), "-m", "pip"]

    # Fallback to system Python
    return sys.executable, [sys.executable, "-m", "pip"]


def install_dependencies(venv_path):
    """Install required dependencies"""
    print("\n📦 Installing dependencies...")

    python_cmd, pip_cmd = get_pip_command(venv_path)

    # Upgrade pip
    print("Upgrading pip...")
    subprocess.run(pip_cmd + ["install", "--upgrade", "pip"],
                   capture_output=True, check=False)

    # Install dependencies
    deps = ["arcade-ai", "httpx", "loguru", "python-dotenv"]

    for dep in deps:
        print(f"Installing {dep}...")
        result = subprocess.run(
            pip_cmd + ["install", dep],
            capture_output=True,
            text=True,
            check=False
        )
        if result.returncode != 0:
            print(f"⚠️  Failed to install {dep}")

    print("✅ Dependencies installed")
    return python_cmd


def get_dreamfactory_config():
    """Get DreamFactory configuration from user"""
    print("\n🔐 DreamFactory Configuration")
    print("=" * 40)

    # Get URL
    df_url = input("DreamFactory URL (without /api/v2) [http://localhost:8080]: ").strip()
    if not df_url:
        df_url = "http://localhost:8080"

    # Get API Key
    print("\nEnter your DreamFactory API Key")
    print("(Create one in: DreamFactory Admin → Apps → Create New App)")
    import getpass
    df_api_key = getpass.getpass("API Key: ").strip()

    return df_url, df_api_key


def test_connection(df_url, df_api_key):
    """Test DreamFactory connection"""
    print("\n🔍 Testing DreamFactory connection...")

    try:
        import httpx
        url = f"{df_url}/api/v2/system/environment"
        headers = {"X-DreamFactory-API-Key": df_api_key}

        response = httpx.get(url, headers=headers, timeout=5)

        if response.status_code == 200:
            print("✅ Successfully connected to DreamFactory!")
            return True
        else:
            print(f"⚠️  Connection returned status {response.status_code}")
            return False
    except Exception as e:
        print(f"⚠️  Could not connect: {e}")
        return False


def create_env_file(df_url, df_api_key):
    """Create .env file"""
    print("\n📝 Creating .env file...")

    env_content = f"""# DreamFactory Configuration
DREAM_FACTORY_BASE_URL={df_url}
DREAM_FACTORY_API_KEY={df_api_key}

# Optional: Arcade Configuration
# ARCADE_API_KEY=your-arcade-api-key
"""

    with open(".env", "w") as f:
        f.write(env_content)

    print("✅ Configuration saved to .env")


def create_test_script(python_cmd):
    """Create test script"""
    print("\n📄 Creating test script...")

    test_script = '''#!/usr/bin/env python3
"""Test script for DreamFactory Arcade Toolkit"""

import os
import sys
import json

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Load environment
from dotenv import load_dotenv
load_dotenv()

# Import toolkit
from arcade_dreamfactory.tools import list_services, list_storage_services

# Mock context
class MockContext:
    def get_secret(self, key):
        value = os.getenv(key)
        if not value:
            raise ValueError(f"Missing environment variable: {key}")
        return value

def test():
    """Run tests"""
    print("🧪 Testing DreamFactory Toolkit")
    print("=" * 50)

    context = MockContext()

    # Test 1: List services
    print("\\n1. Testing list_services...")
    try:
        result = list_services(context)
        data = json.loads(result)
        print(f"   ✅ Found {data['count']} services")
        for svc in data.get('services', [])[:3]:
            print(f"      - {svc['name']} ({svc['type']})")
    except Exception as e:
        print(f"   ❌ Error: {e}")

    # Test 2: List storage
    print("\\n2. Testing list_storage_services...")
    try:
        result = list_storage_services(context)
        data = json.loads(result)
        print(f"   ✅ Found {data['count']} storage services")
    except Exception as e:
        print(f"   ❌ Error: {e}")

    print("\\n" + "=" * 50)
    print("✅ Testing complete!")

if __name__ == "__main__":
    test()
'''

    with open("test_toolkit.py", "w") as f:
        f.write(test_script)

    # Make executable on Unix-like systems
    if os.name != 'nt':
        os.chmod("test_toolkit.py", 0o755)

    print("✅ Test script created: test_toolkit.py")


def main():
    """Main setup process"""
    print("=" * 50)
    print("🚀 Arcade DreamFactory Toolkit Setup")
    print("=" * 50)

    # Check Python
    if not check_python():
        sys.exit(1)

    # Create virtual environment
    venv_path = create_venv()

    # Install dependencies
    if venv_path:
        python_cmd = install_dependencies(venv_path)
    else:
        print("\n⚠️  Continuing without virtual environment")
        print("Installing to user Python...")
        python_cmd = install_dependencies(None)

    # Get configuration
    df_url, df_api_key = get_dreamfactory_config()

    # Create .env file
    create_env_file(df_url, df_api_key)

    # Test connection
    test_connection(df_url, df_api_key)

    # Create test script
    create_test_script(python_cmd)

    # Final instructions
    print("\n" + "=" * 50)
    print("✅ Setup Complete!")
    print("=" * 50)
    print("\n📋 Quick Start:")

    if venv_path:
        if os.name == 'nt':  # Windows
            activate = ".venv\\Scripts\\activate"
        else:
            activate = "source .venv/bin/activate"

        print(f"\n1. Activate virtual environment:")
        print(f"   {activate}")
        print("\n2. Run test:")
        print("   python test_toolkit.py")
        print("\nOR run directly:")
        print(f"   {python_cmd} test_toolkit.py")
    else:
        print("\nRun test:")
        print("   python3 test_toolkit.py")

    print("\n📚 Documentation:")
    print("   - Quick Start: QUICKSTART.md")
    print("   - Full Setup: ARCADE_SETUP.md")
    print("   - README: README.md")
    print("\n" + "=" * 50)


if __name__ == "__main__":
    main()