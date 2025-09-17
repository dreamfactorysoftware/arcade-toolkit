#!/usr/bin/env python3
"""Test that the environment is properly set up"""

import sys
import os

print("✅ Python version:", sys.version)
print("✅ Python executable:", sys.executable)

# Test imports
try:
    import httpx
    print("✅ httpx installed")
except ImportError as e:
    print("❌ httpx not installed:", e)

try:
    import loguru
    print("✅ loguru installed")
except ImportError as e:
    print("❌ loguru not installed:", e)

try:
    import dotenv
    print("✅ python-dotenv installed")
except ImportError as e:
    print("❌ python-dotenv not installed:", e)

try:
    import arcadepy
    import arcade_tdk
    print("✅ arcade packages installed (arcadepy and arcade-tdk)")
except ImportError as e:
    print("❌ arcade packages not installed:", e)

# Test local imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from arcade_dreamfactory.tools import list_services
    print("✅ arcade_dreamfactory toolkit importable")
except ImportError as e:
    print("❌ Could not import toolkit:", e)

print("\n✅ Environment setup complete! Ready to configure DreamFactory.")