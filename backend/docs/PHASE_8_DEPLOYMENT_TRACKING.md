# Phase 8: How Deployment Tracking Actually Works

## Overview

Phase 8 needs to bridge the gap between:
1. **User's Independent Deployment** - Running on their GCP account
2. **Cloud Sentinel Backend** - Our analysis system
3. **Feedback Collection** - Learning from real deployment data

```
┌────────────────────────────────────────────────────────────────────────────┐
│                         THE COMPLETE DATA FLOW                             │
└────────────────────────────────────────────────────────────────────────────┘

USER'S GCP ACCOUNT                      CLOUD SENTINEL BACKEND
┌──────────────────────────────────┐   ┌──────────────────────────────────┐
│                                  │   │                                  │
│  Cloud Run                        │   │  Deployment Registry             │
│  ├── Receiving requests           │   │  ├── decision_id: dec_123        │
│  ├── CPU: 45%                     │   │  ├── user_id: user_456          │
│  ├── Memory: 60%                  │   │  ├── gcp_project_id: abc-xyz    │
│  └── RPS: 850                     │   │  └── deployed_at: 2025-12-31    │
│                                  │   │                                  │
│                                  │   │  Metrics Collector               │
│  GCP Monitoring (Cloud Logging)  │   │  ├── Polls GCP APIs             │
│  ├── CPU, Memory, RPS            │   │  ├── Fetches metrics            │
│  ├── Error rates                 │   │  └── Stores in database         │
│  ├── Latency                     │   │                                  │
│  └── Custom metrics              │   │  Feedback Collection            │
│                                  │   │  ├── Email to user              │
│  GCP Billing API                 │   │  ├── In-app survey              │
│  └── Actual costs                │   │  └── API webhook from user      │
│                                  │   │                                  │
└──────────────────────────────────┘   └──────────────────────────────────┘
         ▲                                       │
         │                                       │
         └─ Authenticated API Calls ────────────┘
              (Using provided credentials)
```

## The 3 Pillars of Phase 8

### 1. Deployment Registry (Store the Connection)

**Problem**: We need to remember which recommendation led to which deployment.

**Solution**: Store deployment info when user accepts recommendation.

```python
# backend/src/core/deployment_registry.py

from dataclasses import dataclass
from datetime import datetime
import json

@dataclass
class DeploymentRecord:
    """Stores the connection between recommendation and deployment"""
    
    decision_id: str                    # From Phase 7 (e.g., "dec_123")
    user_id: str                        # User's ID from auth
    session_id: str                     # Original analysis session
    
    # Deployment identification
    gcp_project_id: str                 # Where they deployed
    deployment_region: str              # e.g., "us-west1"
    
    # What was recommended
    recommended_architecture: str       # "serverless", "containers", etc.
    recommended_cost: float             # $169.78
    recommended_specs: dict             # Full specs from Phase 3
    
    # When deployed
    deployed_at: datetime               # When Phase 7 happened
    expected_deployment_date: datetime  # When we expect metrics to start
    
    # Credentials for metric collection
    gcp_credentials: dict              # JSON credentials (encrypted in DB)
    should_collect_metrics: bool        # Default: True
    
    # Feedback tracking
    feedback_collected: bool            # Has user given feedback?
    feedback_date: Optional[datetime]   # When did they respond?
    feedback_type: Optional[str]        # "perfect_fit", "over_provisioned", etc.


class DeploymentRegistry:
    """Singleton that tracks all deployments"""
    
    def __init__(self, db_connection):
        self.db = db_connection
    
    def register_deployment(self, decision_id: str, deployment_info: dict) -> DeploymentRecord:
        """
        Called when user clicks ACCEPT in Phase 7
        
        Input from user:
        {
            "gcp_project_id": "my-project-abc123",
            "gcp_credentials": {...},  # Service account JSON
            "expected_launch_date": "2025-12-31"
        }
        """
        record = DeploymentRecord(
            decision_id=decision_id,
            user_id=deployment_info["user_id"],
            session_id=deployment_info["session_id"],
            gcp_project_id=deployment_info["gcp_project_id"],
            gcp_credentials=deployment_info["gcp_credentials"],  # Encrypted in DB
            deployed_at=datetime.now(),
            expected_deployment_date=deployment_info.get("expected_launch_date"),
            should_collect_metrics=True
        )
        
        # Store in database
        self.db.deployments.insert_one(record.to_dict())
        
        return record
    
    def get_pending_deployments(self) -> List[DeploymentRecord]:
        """Get deployments that haven't been evaluated yet"""
        return self.db.deployments.find({
            "should_collect_metrics": True,
            "feedback_collected": False,
            "deployed_at": {
                "$lt": datetime.now() - timedelta(days=7)  # At least 7 days old
            }
        })
    
    def mark_feedback_collected(self, decision_id: str, feedback_type: str):
        """Mark that feedback was collected for this deployment"""
        self.db.deployments.update_one(
            {"decision_id": decision_id},
            {
                "$set": {
                    "feedback_collected": True,
                    "feedback_date": datetime.now(),
                    "feedback_type": feedback_type
                }
            }
        )
```

### 2. Metrics Collector (Fetch Real Data)

**Problem**: How do we get metrics from their GCP account?

**Solution**: Use their credentials to call GCP APIs.

```python
# backend/src/core/metrics_collector.py

from google.cloud import monitoring_v3, billing_v1
import asyncio

class MetricsCollector:
    """Collects metrics from user's GCP deployment"""
    
    def __init__(self):
        pass
    
    async def collect_metrics(self, deployment_record: DeploymentRecord) -> dict:
        """
        Fetch real metrics from their GCP project
        
        Uses their credentials to access their project
        """
        
        project_id = deployment_record.gcp_project_id
        credentials = deployment_record.gcp_credentials  # Decrypt from DB
        
        # Initialize GCP clients with their credentials
        monitoring_client = monitoring_v3.MetricServiceClient(
            credentials=credentials
        )
        
        # Query Cloud Run metrics
        cloud_run_metrics = await self._get_cloud_run_metrics(
            monitoring_client, project_id
        )
        
        # Query Cloud SQL metrics
        cloud_sql_metrics = await self._get_cloud_sql_metrics(
            monitoring_client, project_id
        )
        
        # Query billing data
        billing_data = await self._get_billing_data(project_id, credentials)
        
        return {
            "cloud_run": cloud_run_metrics,
            "cloud_sql": cloud_sql_metrics,
            "billing": billing_data,
            "collected_at": datetime.now()
        }
    
    async def _get_cloud_run_metrics(self, client, project_id: str) -> dict:
        """Get CPU, memory, RPS from Cloud Run"""
        
        interval = monitoring_v3.TimeInterval({
            "end_time": {"seconds": int(time.time())},
            "start_time": {"seconds": int(time.time()) - 86400}  # Last 24 hours
        })
        
        results = client.list_time_series(
            name=f"projects/{project_id}",
            filter='resource.type = "cloud_run_revision"',
            interval=interval
        )
        
        metrics = {
            "cpu_utilization": None,
            "memory_utilization": None,
            "request_count": None,
            "error_rate": None
        }
        
        for result in results:
            metric_type = result.metric.type
            
            if "cpu" in metric_type:
                metrics["cpu_utilization"] = result.points[0].value.double_value
            elif "memory" in metric_type:
                metrics["memory_utilization"] = result.points[0].value.double_value
            elif "request" in metric_type:
                metrics["request_count"] = result.points[0].value.int64_value
        
        return metrics
    
    async def _get_billing_data(self, project_id: str, credentials) -> dict:
        """Get actual costs from GCP Billing API"""
        
        billing_client = billing_v1.CloudBillingClient(credentials=credentials)
        
        # Get this month's costs
        costs = billing_client.get_billing_account_summary(
            name=f"billingAccounts/{project_id}"
        )
        
        return {
            "current_month_cost": costs.current_month_cost,
            "projected_monthly_cost": costs.projected_monthly_cost
        }
```

### 3. Feedback Collection (Two Methods)

**Problem**: How do we ask the user for feedback?

**Solution**: Two independent methods.

#### Method 1: Email Notification (Async)

```python
# backend/src/core/feedback_collector.py

class FeedbackCollector:
    """Collects feedback from users about their deployments"""
    
    async def send_feedback_request(self, deployment_record: DeploymentRecord):
        """
        Send email to user asking for feedback (30 days after deployment)
        
        Email contains:
        1. Link to feedback form
        2. Their metrics summary
        3. Comparison: Predicted vs Actual
        """
        
        metrics = await self.metrics_collector.collect_metrics(deployment_record)
        
        email_body = f"""
        Hi {deployment_record.user_id},
        
        Your infrastructure has been running for 30 days! 🎉
        
        📊 HERE'S HOW IT'S PERFORMING:
        
        ACTUAL METRICS:
        • CPU Utilization: {metrics['cloud_run']['cpu_utilization']}%
        • Memory Usage: {metrics['cloud_run']['memory_utilization']}%
        • Actual Cost: ${metrics['billing']['current_month_cost']}
        
        PREDICTED METRICS (From AI):
        • Expected CPU: 65%
        • Expected Cost: ${deployment_record.recommended_cost}
        
        ✅ FEEDBACK LINK:
        https://cloud-sentinel.app/feedback/{deployment_record.decision_id}
        
        Please let us know:
        • Is the recommendation accurate?
        • Are resources over/under-provisioned?
        • How satisfied are you?
        
        [CLICK HERE TO PROVIDE FEEDBACK]
        """
        
        await self.email_service.send(
            to=deployment_record.user_id,
            subject="Your Cloud Sentinel Deployment Report - 30 Day Review",
            body=email_body
        )
```

#### Method 2: Webhook from User's Side (Proactive)

User can also push metrics to us from their deployment:

```python
# User's deployment can call this endpoint:
# POST /api/v1/feedback/{decision_id}

{
    "deployment_metrics": {
        "cpu_utilization": 45,
        "memory_utilization": 60,
        "requests_per_second": 850
    },
    "cost_data": {
        "actual_monthly_cost": 162.30,
        "currency": "USD"
    },
    "user_feedback": {
        "type": "perfect_fit",
        "satisfaction": 9,
        "comments": "Works perfectly!"
    }
}
```

---

## Complete Phase 8 Flow (Detailed)

```
┌────────────────────────────────────────────────────────────────────────────┐
│                         PHASE 8 TIMELINE                                   │
└────────────────────────────────────────────────────────────────────────────┘

DAY 0: User Accepts Recommendation
┌──────────────────────────────────┐
│ Phase 7 Output → DeploymentRegistry
│                                  │
│ ✅ Creates DeploymentRecord:    │
│    - decision_id: dec_123       │
│    - user_id: user@example.com  │
│    - gcp_credentials: {...}     │
│    - deployed_at: 2025-12-31    │
│                                  │
└──────────────────────────────────┘
         │
         │ (User downloads Terraform)
         │ (User runs: terraform apply)
         ▼

DAY 1-7: Deployment Running
┌──────────────────────────────────┐
│ User's GCP Account               │
│ ├── Cloud Run serving requests   │
│ ├── Metrics accumulating         │
│ └── Billing charges happening    │
│                                  │
│ Cloud Sentinel (Passive):        │
│ └── Waiting... (DB marked)       │
│                                  │
└──────────────────────────────────┘
         │
         ▼

DAY 7: Scheduled Job Triggers
┌──────────────────────────────────┐
│ Cloud Sentinel Scheduler:        │
│ 1. Query DB for 7+ day old      │
│    deployments                  │
│ 2. Find: DeploymentRecord(      │
│    decision_id: dec_123)        │
│                                 │
└──────────────────────────────────┘
         │
         ▼

DAY 7: MetricsCollector Runs
┌──────────────────────────────────┐
│ For each pending deployment:    │
│                                 │
│ 1. Decrypt credentials          │
│ 2. Call GCP Monitoring API      │
│    → Get CPU, Memory, RPS       │
│ 3. Call GCP Billing API         │
│    → Get actual costs           │
│                                 │
│ Store metrics in DB:            │
│ {                               │
│   "decision_id": "dec_123",    │
│   "metrics": {...},             │
│   "collected_at": "2025-12-31" │
│ }                               │
│                                 │
└──────────────────────────────────┘
         │
         ▼

DAY 7: Send Feedback Request
┌──────────────────────────────────┐
│ Email user:                      │
│ "Your infrastructure is running!│
│  How's it performing?"          │
│                                 │
│ Include:                        │
│ • Their actual metrics          │
│ • Predicted vs Actual comparison│
│ • Link to feedback form         │
│                                 │
└──────────────────────────────────┘
         │
         ▼

DAY 8-14: User Responds
┌──────────────────────────────────┐
│ User clicks link in email       │
│ User rates: "Perfect fit" ⭐⭐⭐⭐⭐
│ User comments: "Exactly what... │
│                                 │
│ POST /api/v1/feedback/dec_123   │
│ {                               │
│   "feedback_type": "perfect_fit",
│   "satisfaction": 9,            │
│   "comments": "..."             │
│ }                               │
│                                 │
└──────────────────────────────────┘
         │
         ▼

DAY 14: Phase 8 Processes Feedback
┌──────────────────────────────────┐
│ Phase 8 Process:               │
│                                 │
│ 1. Load metrics from DB        │
│ 2. Load user feedback          │
│ 3. Compare:                    │
│    - Predicted: $169.78        │
│    - Actual: $162.30           │
│    - Difference: 4.2% (GOOD!)  │
│                                 │
│ 4. Generate insights:          │
│    "Serverless recommendation  │
│     was 95% accurate. Cost     │
│     prediction improved by 4%" │
│                                 │
│ 5. Update model:               │
│    - Increase confidence for   │
│      similar workloads        │
│    - Adjust cost model bias   │
│                                 │
│ 6. Store in Learning DB:      │
│    learning_id: learn_456     │
│    updates_generated: 3       │
│    impact: "moderate"         │
│                                 │
└──────────────────────────────────┘
         │
         ▼

RESULT: AI Model Improved!
```

---

## Database Schema

You need two new collections to track this:

```python
# MongoDB Collections

# 1. deployments - Tracks user deployments
db.deployments = {
    "_id": ObjectId(),
    "decision_id": "dec_123",
    "user_id": "user@example.com",
    "session_id": "sess_abc",
    
    # Deployment info
    "gcp_project_id": "my-project-xyz",
    "gcp_credentials": "{encrypted_json}",  # Encrypted
    "deployment_region": "us-west1",
    
    # Recommendation info
    "recommended_architecture": "serverless",
    "recommended_cost": 169.78,
    "recommended_specs": {...},
    
    # Timing
    "deployed_at": ISODate("2025-12-31T10:00:00Z"),
    "expected_deployment_date": ISODate("2025-12-31T20:00:00Z"),
    
    # Tracking
    "feedback_collected": false,
    "feedback_date": null,
    "feedback_type": null,
    "should_collect_metrics": true,
    
    "created_at": ISODate(),
    "updated_at": ISODate()
}

# 2. deployment_metrics - Stores collected metrics
db.deployment_metrics = {
    "_id": ObjectId(),
    "decision_id": "dec_123",
    
    # Collected metrics
    "cloud_run": {
        "cpu_utilization": 45,
        "memory_utilization": 60,
        "request_count": 850,
        "error_rate": 0.02
    },
    
    "cloud_sql": {
        "cpu_utilization": 30,
        "memory_utilization": 50,
        "connections": 25
    },
    
    "billing": {
        "current_month_cost": 162.30,
        "projected_monthly_cost": 165.00
    },
    
    "collected_at": ISODate("2025-12-31T15:00:00Z")
}
```

---

## API Endpoints Needed

```python
# 1. Register deployment (called from Phase 7)
POST /api/v1/deployments/register
{
    "decision_id": "dec_123",
    "user_id": "user@example.com",
    "session_id": "sess_abc",
    "gcp_project_id": "my-project",
    "gcp_credentials": {...},  # Service account JSON
    "expected_launch_date": "2025-12-31"
}
→ Returns: {"deployment_id": "dep_123"}

# 2. Submit feedback (called by user via email)
POST /api/v1/feedback/{decision_id}
{
    "feedback_type": "perfect_fit" | "over_provisioned" | "under_provisioned",
    "satisfaction_score": 9,
    "comments": "Exactly what we needed",
    "deployment_metrics": {
        "cpu_utilization": 45,
        "memory_utilization": 60
    }
}

# 3. Get deployment status (for frontend dashboard)
GET /api/v1/deployments/{decision_id}
→ Returns: {
    "status": "running" | "pending_feedback" | "feedback_collected",
    "metrics": {...},
    "feedback": {...}
}

# 4. Webhook from user's side (optional, proactive)
POST /api/v1/metrics/webhook/{decision_id}
{
    "source": "user_deployment",
    "metrics": {...},
    "cost": {...}
}
```

---

## Summary: How Phase 8 Actually Works

| Component | What It Does |
|-----------|------------|
| **DeploymentRegistry** | Stores the connection between Phase 7 decision and GCP project |
| **MetricsCollector** | Uses user's credentials to fetch metrics from their GCP account |
| **FeedbackCollector** | Sends email asking for feedback 7-30 days after deployment |
| **Scheduled Jobs** | Runs periodic checks for deployments needing metrics collection |
| **Database** | Stores deployment records, metrics, and feedback |

**Key Insight**: 
- User's deployment is independent ✅
- We maintain a **persistent connection** via stored credentials ✅
- We **proactively collect metrics** via scheduled jobs ✅
- We **ask for feedback** via email/webhook ✅
- This creates the bridge between their deployment and our learning system ✅
