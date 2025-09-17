#!/usr/bin/env python3
"""Test script for DreamFactory Arcade Toolkit - Local Testing"""

import os
import sys
import json
from dotenv import load_dotenv

# Add the current directory to path to import our toolkit
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Load environment variables
load_dotenv()

# Import our toolkit modules
from arcade_dreamfactory.tools import (
    list_services,
    list_database_tables,
    list_storage_services,
    list_files
)

# Mock context for local testing
class MockContext:
    """Mock context for testing without Arcade server"""
    def get_secret(self, key):
        env_key = key.replace("DREAM_FACTORY_", "DREAM_FACTORY_")
        value = os.getenv(env_key)
        if not value:
            raise ValueError(f"Missing environment variable: {env_key}")
        return value

def test_toolkit():
    """Test toolkit functions locally"""
    context = MockContext()

    print("🧪 Testing DreamFactory Toolkit (Local Mode)")
    print("=" * 50)

    # Test 1: List services
    print("\n1. Testing list_services...")
    try:
        result = list_services(context)
        data = json.loads(result)
        print(f"   ✅ Found {data['count']} services")
        if data['services']:
            for svc in data['services'][:3]:
                print(f"      - {svc['name']} ({svc['type']})")
    except Exception as e:
        print(f"   ❌ Error: {e}")

    # Test 2: List storage services
    print("\n2. Testing list_storage_services...")
    try:
        result = list_storage_services(context)
        data = json.loads(result)
        print(f"   ✅ Found {data['count']} storage services")
        if data['storage_services']:
            for svc in data['storage_services'][:3]:
                print(f"      - {svc['name']} ({svc['type']})")
    except Exception as e:
        print(f"   ❌ Error: {e}")

    # Test 3: List database tables (if available)
    print("\n3. Testing database operations...")
    try:
        services_result = list_services(context, service_type="mysql")
        services = json.loads(services_result)

        if services['services']:
            db_name = services['services'][0]['name']
            print(f"   Using database: {db_name}")

            tables_result = list_database_tables(context, db_name)
            tables = json.loads(tables_result)
            print(f"   ✅ Found {tables['count']} tables")
            if tables['tables']:
                for table in tables['tables'][:5]:
                    print(f"      - {table}")
        else:
            print("   ⚠️  No MySQL services found")
    except Exception as e:
        print(f"   ❌ Error: {e}")

    # Test 4: List files (if storage available)
    print("\n4. Testing file operations...")
    try:
        # First check if 'local' storage exists
        storage_result = list_storage_services(context)
        storage_data = json.loads(storage_result)

        storage_service = None
        for svc in storage_data.get('storage_services', []):
            if svc['type'] == 'local' or 'local' in svc['name'].lower():
                storage_service = svc['name']
                break

        if storage_service:
            print(f"   Using storage service: {storage_service}")
            files_result = list_files(context, storage_service, "/")
            files = json.loads(files_result)
            print(f"   ✅ Found {files['file_count']} files")
        else:
            print("   ⚠️  No local storage service found")
    except Exception as e:
        print(f"   ❌ Error: {e}")

    print("\n" + "=" * 50)
    print("✅ Local testing complete!")
    print("\nNext steps:")
    print("1. Install Arcade CLI: pip install arcade-ai")
    print("2. Set up Arcade secrets: arcade secret set DREAM_FACTORY_BASE_URL '...'")
    print("3. Deploy toolkit: arcade deploy")
    print("4. Test with agents: See ARCADE_SETUP.md for examples")

if __name__ == "__main__":
    test_toolkit()
