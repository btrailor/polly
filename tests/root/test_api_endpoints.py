#!/usr/bin/env python3
"""
Test script for Obsidian Phase 3 API endpoints
"""

import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:11436"

def print_response(title, response):
    """Pretty print API response"""
    print(f"\n{'='*60}")
    print(f"{title}")
    print(f"{'='*60}")
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        print(json.dumps(response.json(), indent=2))
    else:
        print(f"Error: {response.text}")

def test_suggest_folder():
    """Test folder suggestion endpoint"""
    params = {
        "title": "Building an Audio Synthesis Engine",
        "content": "This note covers wavetable synthesis, DSP techniques, and oscillator design for norns and supercollider."
    }
    response = requests.get(f"{BASE_URL}/polly/obsidian/suggest-folder", params=params)
    print_response("Test 1: Suggest Folder", response)
    return response.status_code == 200

def test_suggest_tags():
    """Test tag suggestion endpoint"""
    params = {
        "title": "Wavetable Synthesis",
        "content": "Exploring wavetable synthesis techniques in SuperCollider",
        "existing_tags": "synthesis,audio"
    }
    response = requests.get(f"{BASE_URL}/polly/obsidian/suggest-tags", params=params)
    print_response("Test 2: Suggest Tags", response)
    return response.status_code == 200

def test_find_related():
    """Test find related notes endpoint"""
    params = {
        "note_path": "02-Signals/synthesis-notes.md",
        "content": "Building a modular synthesis engine with multiple oscillators",
        "limit": 5
    }
    response = requests.get(f"{BASE_URL}/polly/obsidian/find-related", params=params)
    print_response("Test 3: Find Related Notes", response)
    return response.status_code == 200

def test_daily_note_preview():
    """Test daily note creation (preview)"""
    payload = {
        "date": datetime.now().isoformat()[:10],
        "confirmed": False
    }
    response = requests.post(f"{BASE_URL}/polly/obsidian/daily-note", json=payload)
    print_response("Test 4: Daily Note (Preview)", response)
    return response.status_code == 200

def test_from_conversation_preview():
    """Test conversation to note (preview)"""
    payload = {
        "messages": [
            {"role": "user", "content": "How do I implement wavetable synthesis in Python?"},
            {"role": "assistant", "content": "Here's a basic wavetable synthesizer:\n```python\nimport numpy as np\nclass Wavetable:\n    def __init__(self, waveform):\n        self.waveform = waveform\n```\nThis creates a simple wavetable class."},
            {"role": "user", "content": "How do I add interpolation?"},
            {"role": "assistant", "content": "You can add linear interpolation like this:\n```python\ndef read(self, phase):\n    index = phase * len(self.waveform)\n    # Linear interpolation\n    return np.interp(index, range(len(self.waveform)), self.waveform)\n```"}
        ],
        "title": "Python Wavetable Synthesis Implementation",
        "confirmed": False
    }
    response = requests.post(f"{BASE_URL}/polly/obsidian/from-conversation", json=payload)
    print_response("Test 5: From Conversation (Preview)", response)
    return response.status_code == 200

def main():
    """Run all tests"""
    print("Testing Obsidian Phase 3 API Endpoints")
    print(f"Server: {BASE_URL}")
    
    results = {
        "suggest_folder": test_suggest_folder(),
        "suggest_tags": test_suggest_tags(),
        "find_related": test_find_related(),
        "daily_note": test_daily_note_preview(),
        "from_conversation": test_from_conversation_preview()
    }
    
    print(f"\n{'='*60}")
    print("Test Summary")
    print(f"{'='*60}")
    for test_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{test_name:25s}: {status}")
    
    total = len(results)
    passed = sum(results.values())
    print(f"\nPassed: {passed}/{total}")
    
    return all(results.values())

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
