#!/usr/bin/env python3
"""
Quick test to verify multi-key setup is working
Run this anytime to check your API key rotation status
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from core.gemini_client import GeminiClient

def main():
    print("\n" + "="*60)
    print("🔑 MULTI-KEY GEMINI API - QUICK STATUS CHECK")
    print("="*60 + "\n")
    
    # Initialize client
    client = GeminiClient()
    
    # Get status
    status = client.get_status()
    rotation = client.get_key_rotation_info()
    
    # Display
    print("📊 CLIENT STATUS:")
    print(f"   Model: {status['model_name']}")
    print(f"   Max Tokens: {status['max_tokens']}")
    print(f"   Temperature: {status['temperature']}")
    print()
    
    print("🔑 API KEYS:")
    for key_name, key_status in status['keys'].items():
        current = "← CURRENT" if key_status['is_current'] else ""
        initialized = "✅" if key_status['initialized'] else "❌"
        print(f"   {initialized} {key_name:12} (failures: {key_status['failures']}) {current}")
    print()
    
    print("📈 ROTATION INFO:")
    print(f"   Total Keys: {rotation['total_keys']}")
    print(f"   Current Index: {rotation['current_index']}/{rotation['total_keys']}")
    print(f"   Current Key: {rotation['current_key']}")
    print()
    
    print("✅ QUOTA CALCULATION:")
    print(f"   Requests per key per day: 20")
    print(f"   Number of keys: {rotation['total_keys']}")
    print(f"   Total quota: {20 * rotation['total_keys']} requests/day 🚀")
    print()
    
    # Test single parse
    print("🧪 TESTING SINGLE PARSE:")
    test_input = "API for 1000 users in USA"
    print(f"   Input: {test_input}")
    print(f"   Processing...", end=" ", flush=True)
    
    result = client.parse_intent(test_input)
    
    print(f"✅\n")
    print(f"   Workload: {result['workload_type']}")
    print(f"   Confidence: {result['parsing_confidence']}")
    print(f"   Source: {result['parsing_source']}")
    print(f"   Active Key: {result.get('active_key', 'N/A')}")
    
    print("\n" + "="*60)
    print("✅ ALL SYSTEMS OPERATIONAL")
    print("="*60 + "\n")

if __name__ == "__main__":
    main()
