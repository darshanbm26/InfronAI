#!/usr/bin/env python3
"""
Comprehensive Gemini client test
"""

import os
import sys
import asyncio
from dotenv import load_dotenv

# Add src to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

async def test_gemini_connection():
    """Test Gemini client connection and functionality"""
    
    print("🧪 Testing Gemini Client Connection")
    print("=" * 60)
    
    from core.gemini_client import GeminiClient
    
    # Initialize client
    client = GeminiClient()
    status = client.get_status()
    
    print(f"✅ Gemini Client Initialized")
    print(f"   Model: {status['model_name']}")
    print(f"   Mock Mode: {status['mock_mode']}")
    print(f"   API Key Configured: {status['api_key_configured']}")
    
    # Test cases
    test_cases = [
        {
            "name": "Simple API Backend",
            "input": "I need an API for 50,000 monthly users in India with low latency"
        },
        {
            "name": "Complex ML Workload",
            "input": "Building a machine learning inference service for image recognition with 100k requests per day, needs GPU acceleration and high availability"
        },
        {
            "name": "Data Processing Pipeline",
            "input": "Create a data pipeline to process 1TB of data daily, batch processing, cost-sensitive, European data residency required"
        }
    ]
    
    results = []
    
    for test in test_cases:
        print(f"\n🔍 Test: {test['name']}")
        print(f"Input: {test['input'][:80]}...")
        
        try:
            result = client.parse_intent(test["input"])
            
            print(f"✅ Success!")
            print(f"   Workload: {result['workload_type']}")
            print(f"   Confidence: {result['parsing_confidence']:.2f}")
            print(f"   Source: {result.get('parsing_source', 'unknown')}")
            print(f"   Monthly Users: {result['scale']['monthly_users']:,}")
            print(f"   Geography: {result['requirements']['geography']}")
            
            results.append({
                "test": test["name"],
                "success": True,
                "workload": result["workload_type"],
                "confidence": result["parsing_confidence"]
            })
            
        except Exception as e:
            print(f"❌ Failed: {e}")
            results.append({
                "test": test["name"],
                "success": False,
                "error": str(e)
            })
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 Test Summary")
    print("=" * 60)
    
    passed = sum(1 for r in results if r["success"])
    total = len(results)
    
    print(f"✅ Passed: {passed}/{total}")
    
    if passed == total:
        print("\n🎉 All Gemini tests passed!")
        return True
    else:
        print("\n⚠️ Some tests failed")
        for result in results:
            if not result["success"]:
                print(f"   - {result['test']}: {result['error']}")
        return False

async def test_gemini_models():
    """Test available Gemini models"""
    print("\n🔬 Testing Available Gemini Models")
    print("=" * 60)
    
    import google.generativeai as genai
    
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("❌ No GEMINI_API_KEY found in environment")
        return
    
    genai.configure(api_key=api_key)
    
    try:
        models = genai.list_models()
        
        print("📋 Available models:")
        for model in models:
            if 'generateContent' in model.supported_generation_methods:
                print(f"  - {model.name}")
        
        # Test specific models
        test_models = ["gemini-2.5-flash", "gemini-2.0-flash", "gemini-2.5-flash-lite"]
        
        print("\n🧪 Testing specific models:")
        for model_name in test_models:
            try:
                model = genai.GenerativeModel(model_name)
                response = model.generate_content("Say 'OK' if working")
                if response.text:
                    print(f"  ✅ {model_name}: Working")
                else:
                    print(f"  ⚠️  {model_name}: No response")
            except Exception as e:
                print(f"  ❌ {model_name}: Failed - {str(e)[:50]}...")
    
    except Exception as e:
        print(f"❌ Failed to list models: {e}")

if __name__ == "__main__":
    print("🚀 Starting comprehensive Gemini tests...")
    print("=" * 60)
    
    # Run tests
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    try:
        # Test connection
        success = loop.run_until_complete(test_gemini_connection())
        
        # Test models (optional)
        loop.run_until_complete(test_gemini_models())
        
        if success:
            print("\n🎉 All tests completed successfully!")
            sys.exit(0)
        else:
            print("\n⚠️ Tests completed with failures")
            sys.exit(1)
            
    except Exception as e:
        print(f"\n❌ Test execution failed: {e}")
        sys.exit(1)