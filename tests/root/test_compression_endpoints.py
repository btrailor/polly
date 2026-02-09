#!/usr/bin/env python3
"""
Test script to verify compression endpoints are working.
Run this after restarting the server.
"""

import requests
import json

BASE_URL = "http://localhost:11436"

def test_endpoints():
    print("Testing Compression API Endpoints\n")
    print("=" * 60)
    
    # Test 1: GET compression settings
    print("\n1. GET /api/settings/compression")
    try:
        response = requests.get(f"{BASE_URL}/api/settings/compression")
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Success!")
            print(f"   Settings: {json.dumps(data, indent=6)}")
        else:
            print(f"   ❌ Failed: {response.text}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test 2: GET compression stats
    print("\n2. GET /api/settings/compression/stats")
    try:
        response = requests.get(f"{BASE_URL}/api/settings/compression/stats")
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Success!")
            print(f"   Stats: {json.dumps(data['stats'], indent=6)}")
        else:
            print(f"   ❌ Failed: {response.text}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test 3: POST compression settings (update)
    print("\n3. POST /api/settings/compression (test update)")
    try:
        test_settings = {
            "enabled": True,
            "message_threshold": 25,
            "age_hours": 48,
            "keep_recent": 15,
            "show_stats": True
        }
        response = requests.post(
            f"{BASE_URL}/api/settings/compression",
            json=test_settings
        )
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Success!")
            print(f"   Message: {data.get('message')}")
            print(f"   Updated settings: {json.dumps(data['settings'], indent=6)}")
        else:
            print(f"   ❌ Failed: {response.text}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    print("\n" + "=" * 60)
    print("\nIf all tests passed, the compression endpoints are working!")
    print("You should now see the Compression tab in the UI at:")
    print(f"{BASE_URL}/settings")

if __name__ == "__main__":
    print("\n⚠️  Make sure the Polly server is running first:")
    print("   python -m polly serve\n")
    
    input("Press Enter to run tests...")
    test_endpoints()
