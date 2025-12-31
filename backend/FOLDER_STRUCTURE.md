📦 COMPLETE FOLDER STRUCTURE
================================================================================

backend/
├── README.md
├── requirements.txt
├── .env (configuration file - DO NOT DELETE)
│
├── 📁 src/
│   │
│   ├── 📁 api/
│   │   └── app.py ✅ ACTIVE - FastAPI main application
│   │
│   ├── 📁 core/
│   │   ├── __init__.py
│   │   ├── gemini_client.py ✅ ACTIVE - Multi-key Gemini API client with rotation
│   │   ├
│   │   ├
│   │   ├
│   │   ├── config_validator.py 
│   │   ├── catalog_manager.py 
│   │   └── gcp_pricing_client.py 
│   │
│   ├── 📁 phases/
│   │   ├── phase1_intent_capture.py ✅ ACTIVE - Parse user intent
│   │   ├── phase2_architecture_sommelier.py ✅ ACTIVE - Suggest architecture
│   │   ├── phase3_machine_specification.py ✅ ACTIVE - Specify machines
│   │   ├── phase4_pricing_calculation.py ✅ ACTIVE - Calculate costs
│   │   ├── phase5_tradeoff_analysis.py ✅ ACTIVE - Analyze tradeoffs
│   │   ├── phase6_recommendation_presentation.py ✅ ACTIVE - Present recommendations
│   │   ├── phase7_user_decision.py ✅ ACTIVE - Get user decision
│   │   └── phase8_learning_feedback.py ✅ ACTIVE - Learning from feedback
│   │
│   ├── 📁 telemetry/
│   │   ├── datadog_client.py ✅ ACTIVE - Datadog metrics/logs/events
│   │   ├── event_schemas.py ✅ ACTIVE - Event data structures
│   │   └── metrics_registry.py ✅ ACTIVE - Metrics definitions
│   │
│   └── 
│
├── 📁 datadog-setup/
│   ├── mock_telemetry.py ✅ USED - Generate test telemetry
│   ├── setup_datadog.py ✅ USED - Configure Datadog
│   ├── alerts_config/ (dashboard configs)
│   └── dashboard_templates/ (JSON templates)
│
├── 📁 terraform/
│   └── (Cloud infrastructure files)
│
├── 📁 frontend/
│   └── (Web UI files)
│
└──


================================================================================
ARCHITECTURE OVERVIEW
================================================================================

FLOW:
┌─────────────────────────────────────────────────────────────────┐
│ USER REQUEST                                                    │
└──────────────────────┬──────────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────────┐
│ PHASE 1: Intent Capture (phase1_intent_capture.py)             │
│  └─ Uses: gemini_client.py (multi-key with rotation)           │
│  └─ Telemetry: datadog_client.py (metrics, logs, events)       │
└──────────────────────┬──────────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────────┐
│ PHASE 2-8: Architecture Analysis                               │
│  ├─ Phase 2: Architecture Recommendation                        │
│  ├─ Phase 3: Machine Specification                              │
│  ├─ Phase 4: Pricing Calculation                                │
│  ├─ Phase 5: Tradeoff Analysis                                  │
│  ├─ Phase 6: Present Recommendations                            │
│  ├─ Phase 7: Get User Decision                                  │
│  └─ Phase 8: Learning & Feedback                                │
│                                                                  │
│  All use: gemini_client.py for LLM calls                        │
│  All report: telemetry to datadog_client.py                     │
└──────────────────────┬──────────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────────┐
│ API LAYER (app.py)                                              │
│  ├─ REST endpoints for all phases                               │
│  ├─ Health checks & status                                      │
│  └─ Returns JSON responses                                      │
└──────────────────────┬──────────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────────┐
│ RESPONSE TO USER                                                │
└─────────────────────────────────────────────────────────────────┘


================================================================================
KEY FILES EXPLANATION
================================================================================

✅ ESSENTIAL FILES (KEEP):

1. src/core/gemini_client.py
   ├─ Loads 4 API keys (PRIMARY + BACKUP_1/2/3)
   ├─ Automatic key rotation on quota exhaustion
   ├─ Retry logic with exponential backoff
   ├─ Fallback to enhanced mock parsing
   └─ Returns: workload type, scale, requirements, constraints

2. src/api/app.py
   ├─ FastAPI main application
   ├─ REST endpoints for all 8 phases
   └─ Returns JSON responses

3. src/phases/*.py (8 files)
   ├─ Phase 1: Parse user intent
   ├─ Phase 2: Recommend architecture (Cloud Run, Cloud SQL, etc.)
   ├─ Phase 3: Specify machine types and sizes
   ├─ Phase 4: Calculate monthly/annual costs
   ├─ Phase 5: Analyze performance vs cost tradeoffs
   ├─ Phase 6: Present recommendations with details
   ├─ Phase 7: Get user decision and feedback
   └─ Phase 8: Learn from feedback to improve future recommendations

4. src/telemetry/*.py
   ├─ datadog_client.py - Send metrics, logs, events to Datadog
   ├─ event_schemas.py - Define event structures
   └─ metrics_registry.py - Define metric names and types

5. datadog-setup/*.py
   ├─ setup_datadog.py - Initial Datadog configuration
   └─ mock_telemetry.py - Generate test data




================================================================================
CONFIGURATION
================================================================================

.env file contains:
├─ GEMINI_API_KEY (PRIMARY account)
├─ GEMINI_API_KEY_1 (BACKUP_1 account)
├─ GEMINI_API_KEY_2 (BACKUP_2 account)
├─ GEMINI_API_KEY_3 (BACKUP_3 account)
├─ GEMINI_MODEL: gemini-2.5-flash-lite
├─ GOOGLE_PROJECT_ID: catalystai-482013
├─ DD_API_KEY: Datadog API key
├─ DD_APP_KEY: Datadog app key
├─ DD_SITE: datadoghq.com
├─ TELEMETRY_MODE: datadog (or console)
└─ Various other settings









. 🔄 FIX retry logic (OPTIONAL but RECOMMENDED)
   └─ Current: Retries 3 times per key before rotating
   └─ Better: Rotate immediately on 429 error
   └─ Saves quota usage


