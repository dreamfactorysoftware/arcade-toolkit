#!/usr/bin/env python3
"""Test deployment by checking what arcade deploy actually does."""

import subprocess
import json
import os
import sys

def run_command(cmd):
    """Run a command and return output."""
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            timeout=30
        )
        return result.stdout, result.stderr, result.returncode
    except Exception as e:
        return "", str(e), 1

def main():
    print("🔍 Arcade Deployment Debugger")
    print("=" * 50)

    # 1. Check arcade version
    print("\n1️⃣ Arcade Version:")
    stdout, stderr, code = run_command("arcade --version")
    print(f"   {stdout.strip()}")

    # 2. Check if logged in
    print("\n2️⃣ Login Status:")
    stdout, stderr, code = run_command("arcade worker list 2>&1")
    if "Not logged in" in stdout or "Not logged in" in stderr:
        print("   ❌ Not logged in")
        print("   Run: arcade login")
        return
    else:
        print("   ✅ Logged in")

    # 3. Try to get more verbose output
    print("\n3️⃣ Attempting deployment with debugging:")

    # Set debug environment variables
    env = os.environ.copy()
    env['ARCADE_DEBUG'] = '1'
    env['DEBUG'] = '1'

    # Try deployment with subprocess to capture all output
    process = subprocess.Popen(
        ["arcade", "deploy", "--verbose"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        env=env
    )

    stdout, stderr = process.communicate(timeout=60)

    print("\n📝 STDOUT:")
    print("-" * 40)
    print(stdout[:2000])  # First 2000 chars

    print("\n📝 STDERR:")
    print("-" * 40)
    print(stderr[:2000])  # First 2000 chars

    # 4. Check for common issues
    print("\n4️⃣ Common Issues Check:")

    if "Expecting value" in stdout or "Expecting value" in stderr:
        print("   ⚠️  JSON parsing error detected")
        print("   → This usually means authentication failed")
        print("   → Try: arcade logout && arcade login")

    if "404" in stdout or "404" in stderr:
        print("   ⚠️  404 error detected")
        print("   → API endpoint might be wrong")

    if "401" in stdout or "401" in stderr:
        print("   ⚠️  401 Unauthorized detected")
        print("   → Authentication token is invalid")
        print("   → Try: arcade logout && arcade login")

    if "500" in stdout or "500" in stderr:
        print("   ⚠️  500 Server Error detected")
        print("   → Arcade API might be having issues")

    # 5. Alternative approach
    print("\n5️⃣ Alternative Approach:")
    print("   If deployment continues to fail, try:")
    print("   1. arcade serve (test locally)")
    print("   2. Contact Arcade support")
    print("   3. Check https://status.arcade.dev")

if __name__ == "__main__":
    main()