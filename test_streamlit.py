#!/usr/bin/env python3
"""Test script to check Streamlit app functionality."""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test if all imports work."""
    try:
        import streamlit as st
        import requests
        import json
        import pandas as pd
        print("✅ All imports successful")
        return True
    except Exception as e:
        print(f"❌ Import error: {e}")
        return False

def test_api_connection():
    """Test API connection."""
    try:
        import requests
        response = requests.get("http://127.0.0.1:8000/health", timeout=5)
        if response.status_code == 200:
            print("✅ API connection successful")
            return True
        else:
            print(f"❌ API returned status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ API connection failed: {e}")
        return False

def test_triage_api():
    """Test triage API call."""
    try:
        import requests
        response = requests.post(
            "http://127.0.0.1:8000/triage",
            json={"query": "fever and headache"},
            timeout=10
        )
        if response.status_code == 200:
            data = response.json()
            print("✅ Triage API call successful")
            print(f"  Response keys: {list(data.keys())}")
            print(f"  Next action: {data.get('next_action')}")
            return True
        else:
            print(f"❌ Triage API returned status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Triage API call failed: {e}")
        return False

def main():
    """Run all tests."""
    print("🧪 Testing Streamlit App Components")
    print("=" * 40)
    
    # Test imports
    if not test_imports():
        return False
    
    # Test API connection
    if not test_api_connection():
        return False
    
    # Test triage API
    if not test_triage_api():
        return False
    
    print("\n✅ All tests passed! Streamlit app should work.")
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
