#!/usr/bin/env python3
"""
API test suite
"""

import os
import sys
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

def test_api_health():
    """Test API health endpoint"""
    print("🧪 Testing API Health Endpoint")
    print("=" * 50)
    
    import requests
    
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Health check passed")
            print(f"   Status: {data['status']}")
            print(f"   Service: {data['service']}")
            print(f"   Version: {data['version']}")
            print(f"   Uptime: {data['uptime_seconds']:.1f}s")
            return True
        else:
            print(f"❌ Health check failed: HTTP {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ API server not running")
        print("💡 Start server with: cd src/api && python app.py")
        return False
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False

def test_api_intent():
    """Test API intent endpoint"""
    print("\n🧪 Testing API Intent Endpoint")
    print("=" * 50)
    
    import requests
    import json
    
    test_payload = {
        "description": "I need a customer-facing API for 50k monthly users in India with low latency and high availability. Budget is medium, team has intermediate experience.",
        "user_id": "api_test_user_001",
        "session_id": "api_test_session_001",
        "metadata": {
            "test": True,
            "environment": "testing",
            "source": "api_test"
        }
    }
    
    try:
        response = requests.post(
            "http://localhost:8000/analysis/intent",
            json=test_payload,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Intent capture successful")
            print(f"   Request ID: {data['request_id']}")
            print(f"   Workload: {data['intent_analysis']['workload_type']}")
            print(f"   Confidence: {data['intent_analysis']['parsing_confidence']:.2f}")
            print(f"   Processing Time: {data['processing_metadata']['processing_time_ms']}ms")
            
            # Save sample response
            with open("sample_api_response.json", "w") as f:
                json.dump(data, f, indent=2)
            print(f"💾 Sample response saved to sample_api_response.json")
            
            return True
        else:
            print(f"❌ Intent capture failed: HTTP {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ API server not running")
        return False
    except Exception as e:
        print(f"❌ Intent capture error: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Starting API tests...")
    
    # Test health endpoint
    health_ok = test_api_health()
    
    # Test intent endpoint if health is OK
    intent_ok = False
    if health_ok:
        intent_ok = test_api_intent()
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 API Test Summary")
    print("=" * 50)
    
    print(f"✅ Health Endpoint: {'PASS' if health_ok else 'FAIL'}")
    print(f"✅ Intent Endpoint: {'PASS' if intent_ok else 'FAIL'}")
    
    if health_ok and intent_ok:
        print("\n🎉 API tests passed!")
        print("🌐 API is ready for use")
        sys.exit(0)
    else:
        print("\n⚠️ API tests failed")
        sys.exit(1)