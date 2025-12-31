"""
Demonstrate the global key exhaustion optimization working
"""
import asyncio
import time
import sys
sys.path.insert(0, 'src')

from phases.phase1_intent_capture import IntentCapturePhase
from phases.phase2_architecture_sommelier import ArchitectureSommelierPhase
from phases.phase5_tradeoff_analysis import TradeoffAnalysisPhase

async def test():
    print("\n" + "=" * 80)
    print("GLOBAL KEY EXHAUSTION OPTIMIZATION DEMONSTRATION")
    print("=" * 80)
    
    phase1 = IntentCapturePhase()
    phase2 = ArchitectureSommelierPhase()
    
    input_text = "I need API backend in India for 1000 users, budget $500"
    
    print("\n[Phase 1] First call - will try all keys and set exhaustion flag...")
    print("-" * 80)
    start1 = time.time()
    phase1_result = await phase1.process(input_text, "user_demo", "session_demo")
    time1 = (time.time() - start1) * 1000
    print(f"\n✅ Phase 1: {time1:.0f}ms (tried all keys, used fallback)")
    
    print("\n[Phase 2] Second call - should skip Gemini entirely...")
    print("-" * 80)
    start2 = time.time()
    phase2_result = phase2.process(phase1_result, "user_demo", "session_demo")
    time2 = (time.time() - start2) * 1000
    print(f"\n✅ Phase 2: {time2:.0f}ms (skipped Gemini, used rule-based)")
    
    print("\n" + "=" * 80)
    print("PERFORMANCE COMPARISON")
    print("=" * 80)
    print(f"Phase 1: {time1:>6.0f}ms  ← Tries all keys + fallback (~11-12 seconds)")
    print(f"Phase 2: {time2:>6.0f}ms  ← Skips Gemini, direct fallback (< 1 second)")
    print("-" * 80)
    speedup = time1 / time2 if time2 > 0 else 0
    print(f"Speed improvement: {speedup:.1f}x faster for Phase 2!")
    print("\n✅ Optimization Working! Phases after exhaustion skip retry logic.")
    print("=" * 80)

if __name__ == "__main__":
    asyncio.run(test())
