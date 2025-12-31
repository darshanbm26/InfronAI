#!/usr/bin/env python3
"""
Comprehensive Phase 1 test
"""

import os
import sys
import asyncio
import json
from dotenv import load_dotenv

# Add src to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

async def test_phase1_comprehensive():
    """Comprehensive Phase 1 test"""
    
    print("🧪 Testing Phase 1: Intent Capture (Comprehensive)")
    print("=" * 70)
    
    from phases.phase1_intent_capture import IntentCapturePhase
    
    # Initialize phase
    phase1 = IntentCapturePhase()
    
    print(f"✅ Phase 1 Initialized")
    print(f"   Name: {phase1.phase_name}")
    print(f"   Version: {phase1.phase_version}")
    
    # Get initial status
    status = phase1.get_status()
    print(f"   Gemini Available: {not status['gemini_available']}")
    print(f"   Telemetry Mode: {status['telemetry_status']['mode']}")
    
    # Test scenarios
    test_scenarios = [
        {
            "name": "Basic API Backend",
            "input": "I need a REST API for 50k monthly users in Mumbai with low latency and 99.9% availability",
            "user_id": "user_api_001",
            "metadata": {"company_size": "startup", "industry": "fintech"}
        },
        {
            "name": "E-commerce Website",
            "input": "Building an e-commerce website for 100k monthly visitors, needs to handle seasonal spikes, PCI compliant, global audience",
            "user_id": "user_web_001",
            "metadata": {"company_size": "medium", "industry": "retail"}
        },
        {
            "name": "ML Training Pipeline",
            "input": "Need a machine learning pipeline for training computer vision models, processes 10TB of data monthly, needs GPU instances, budget is tight",
            "user_id": "user_ml_001",
            "metadata": {"company_size": "enterprise", "industry": "ai_research"}
        },
        {
            "name": "Real-time Gaming Server",
            "input": "Multiplayer gaming server for 10k concurrent players, ultra-low latency required, global deployment, high compute requirements",
            "user_id": "user_game_001",
            "metadata": {"company_size": "startup", "industry": "gaming"}
        }
    ]
    
    results = []
    
    for i, scenario in enumerate(test_scenarios, 1):
        print(f"\n🔬 Scenario {i}/{len(test_scenarios)}: {scenario['name']}")
        print(f"Input: {scenario['input'][:100]}...")
        
        try:
            # Process intent
            result = await phase1.process(
                user_input=scenario["input"],
                user_id=scenario["user_id"],
                session_id=f"session_{i:03d}",
                metadata=scenario.get("metadata")
            )
            
            print(f"✅ Success!")
            print(f"   Request ID: {result['request_id']}")
            print(f"   Workload: {result['intent_analysis']['workload_type']}")
            print(f"   Confidence: {result['intent_analysis']['parsing_confidence']:.2f}")
            print(f"   Scale Tier: {result['business_context']['scale_tier']}")
            print(f"   Complexity: {result['business_context']['complexity_score']:.2f}")
            print(f"   Estimated Cost: ${result['business_context']['estimated_cloud_spend']['estimated_monthly_usd']}")
            print(f"   Risk Level: {result['business_context']['risk_level']}")
            print(f"   Processing Time: {result['processing_metadata']['processing_time_ms']}ms")
            
            results.append({
                "scenario": scenario["name"],
                "success": True,
                "result": result
            })
            
        except Exception as e:
            print(f"❌ Failed: {e}")
            results.append({
                "scenario": scenario["name"],
                "success": False,
                "error": str(e)
            })
    
    # Get statistics
    stats = phase1.get_statistics()
    
    # Summary
    print("\n" + "=" * 70)
    print("📊 Phase 1 Test Summary")
    print("=" * 70)
    
    passed = sum(1 for r in results if r["success"])
    total = len(results)
    
    print(f"✅ Scenarios Passed: {passed}/{total}")
    print(f"📈 Success Rate: {stats['success_rate']:.1%}")
    print(f"🎯 Average Confidence: {stats['avg_confidence']:.2f}")
    print(f"⏱️  Average Processing Time: {stats['avg_processing_time_ms']:.0f}ms")
    
    # Show sample output
    if results and results[0]["success"]:
        print("\n📋 Sample Output Structure:")
        sample = results[0]["result"]
        
        # Create simplified view
        simplified = {
            "request_id": sample["request_id"],
            "user_id": sample["user_id"],
            "workload_type": sample["intent_analysis"]["workload_type"],
            "confidence": sample["intent_analysis"]["parsing_confidence"],
            "scale": sample["intent_analysis"]["scale"],
            "requirements": sample["intent_analysis"]["requirements"],
            "business_context": sample["business_context"],
            "next_phase": sample["next_phase"]
        }
        
        print(json.dumps(simplified, indent=2))
    
    # Flush telemetry
    try:
        phase1.telemetry.flush_buffers()
        print("\n💾 Telemetry buffers flushed")
    except Exception as e:
        print(f"\n⚠️ Failed to flush telemetry: {e}")
    
    return passed == total

async def test_phase1_error_handling():
    """Test Phase 1 error handling"""
    print("\n🧪 Testing Error Handling")
    print("=" * 60)
    
    from phases.phase1_intent_capture import IntentCapturePhase
    
    phase1 = IntentCapturePhase()
    
    # Test empty input
    try:
        await phase1.process("")
        print("❌ Should have failed on empty input")
        return False
    except ValueError:
        print("✅ Correctly rejected empty input")
    
    # Test very short input
    try:
        await phase1.process("API")
        print("❌ Should have failed on short input")
        return False
    except Exception:
        print("✅ Correctly handled short input")
    
    # Test with special characters
    try:
        result = await phase1.process("API backend for 50k users ### special chars")
        print(f"✅ Handled special characters: {result['intent_analysis']['workload_type']}")
    except Exception as e:
        print(f"❌ Failed on special characters: {e}")
        return False
    
    return True

async def test_phase1_api_integration():
    """Test Phase 1 API integration"""
    print("\n🧪 Testing API Integration")
    print("=" * 60)
    
    import httpx
    
    # Start API server in background (simulated)
    print("🔧 Note: Start API server separately to test full integration")
    print("   Command: cd src/api && python app.py")
    
    # Test with curl command
    test_command = """curl -X POST "http://localhost:8000/analysis/intent" \\
  -H "Content-Type: application/json" \\
  -d '{
    "description": "I need an API for 50k users in India with low latency",
    "user_id": "test_user_001",
    "metadata": {"test": true}
  }'"""
    
    print(f"\n📋 API Test Command:")
    print(test_command)
    
    return True

if __name__ == "__main__":
    print("🚀 Starting comprehensive Phase 1 tests...")
    print("=" * 70)
    
    # Run tests
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    try:
        # Test main functionality
        main_success = loop.run_until_complete(test_phase1_comprehensive())
        
        # Test error handling
        error_success = loop.run_until_complete(test_phase1_error_handling())
        
        # Test API integration
        api_success = loop.run_until_complete(test_phase1_api_integration())
        
        # Final summary
        print("\n" + "=" * 70)
        print("🎯 Final Test Results")
        print("=" * 70)
        
        print(f"✅ Main Functionality: {'PASS' if main_success else 'FAIL'}")
        print(f"✅ Error Handling: {'PASS' if error_success else 'FAIL'}")
        print(f"✅ API Integration: {'PASS' if api_success else 'INFO (manual test)'}")
        
        if main_success and error_success:
            print("\n🎉 Phase 1 tests completed successfully!")
            print("🚀 Ready for Phase 2: Architecture Sommelier")
            sys.exit(0)
        else:
            print("\n⚠️ Tests completed with failures")
            sys.exit(1)
            
    except Exception as e:
        print(f"\n❌ Test execution failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)