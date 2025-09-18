#!/usr/bin/env python3
"""Validate Arcade API connection."""

import httpx
import json
import os

def check_arcade_api():
    """Check if we can connect to the Arcade API."""

    # Try to find auth token
    auth_file = os.path.expanduser("~/.arcade/auth.json")

    if os.path.exists(auth_file):
        print(f"✅ Auth file found: {auth_file}")
        try:
            with open(auth_file) as f:
                auth_data = json.load(f)
                if "token" in auth_data:
                    print("✅ Auth token found")
                else:
                    print("❌ No token in auth file")
        except Exception as e:
            print(f"❌ Error reading auth file: {e}")
    else:
        print(f"❌ Auth file not found at {auth_file}")

    # Try to connect to Arcade API
    print("\n🔍 Testing API connection...")

    try:
        # Try the Arcade API endpoint
        response = httpx.get("https://api.arcade.dev/health", timeout=5)
        if response.status_code == 200:
            print("✅ API is reachable")
        else:
            print(f"⚠️  API returned status {response.status_code}")
    except Exception as e:
        print(f"❌ Could not connect to API: {e}")

    print("\n📝 Checking worker configuration...")

    # Check worker.toml
    if os.path.exists("worker.toml"):
        with open("worker.toml") as f:
            content = f.read()
            print("worker.toml content:")
            print(content)

            # Basic validation
            if "[[worker]]" in content:
                print("✅ Worker section found")
            if "secret =" in content:
                print("✅ Secret field found")
            if "packages =" in content:
                print("✅ Packages field found")
    else:
        print("❌ worker.toml not found")

if __name__ == "__main__":
    check_arcade_api()