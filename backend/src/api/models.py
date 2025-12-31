"""
Pydantic models for API requests and responses
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, Dict, Any, List
from enum import Enum
from datetime import datetime

class PhaseStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"

class IntentRequest(BaseModel):
    """Request model for intent capture"""
    
    description: str = Field(
        ...,
        min_length=10,
        max_length=2000,
        description="Natural language description of infrastructure needs"
    )
    
    user_id: Optional[str] = Field(
        None,
        description="Optional user identifier"
    )
    
    session_id: Optional[str] = Field(
        None,
        description="Optional session identifier"
    )
    
    metadata: Optional[Dict[str, Any]] = Field(
        None,
        description="Optional additional metadata"
    )
    
    @validator('description')
    def validate_description(cls, v):
        if len(v.strip()) < 10:
            raise ValueError('Description must be at least 10 characters')
        return v.strip()

class IntentResponse(BaseModel):
    """Response model for intent capture"""
    
    request_id: str = Field(..., description="Unique request identifier")
    user_id: str = Field(..., description="User identifier")
    session_id: str = Field(..., description="Session identifier")
    phase: str = Field(..., description="Phase name")
    status: PhaseStatus = Field(..., description="Phase status")
    
    intent_analysis: Dict[str, Any] = Field(
        ...,
        description="Parsed intent analysis"
    )
    
    business_context: Dict[str, Any] = Field(
        ...,
        description="Business context and insights"
    )
    
    processing_metadata: Dict[str, Any] = Field(
        ...,
        description="Processing metadata"
    )
    
    input_metadata: Dict[str, Any] = Field(
        ...,
        description="Input metadata"
    )
    
    timestamp: datetime = Field(..., description="Response timestamp")
    phase_version: str = Field(..., description="Phase implementation version")
    
    next_phase: str = Field(..., description="Next phase in workflow")
    phase_transition: Dict[str, Any] = Field(
        ...,
        description="Phase transition information"
    )

class ErrorResponse(BaseModel):
    """Error response model"""
    
    error: bool = Field(True, description="Error flag")
    message: str = Field(..., description="Error message")
    code: str = Field(..., description="Error code")
    request_id: Optional[str] = Field(None, description="Request identifier")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
    
    def dict(self, *args, **kwargs):
        """Override dict to ensure datetime is serialized"""
        d = super().dict(*args, **kwargs)
        if isinstance(d.get('timestamp'), datetime):
            d['timestamp'] = d['timestamp'].isoformat()
        return d

class HealthResponse(BaseModel):
    """Health check response"""
    
    status: str = Field(..., description="Service status")
    service: str = Field(..., description="Service name")
    version: str = Field(..., description="Service version")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    uptime_seconds: float = Field(..., description="Service uptime in seconds")
    phases_available: List[str] = Field(..., description="Available phases")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
    
    def dict(self, *args, **kwargs):
        """Override dict to ensure datetime is serialized"""
        d = super().dict(*args, **kwargs)
        if isinstance(d.get('timestamp'), datetime):
            d['timestamp'] = d['timestamp'].isoformat()
        return d

class PhaseStatistics(BaseModel):
    """Phase statistics response"""
    
    phase_name: str = Field(..., description="Phase name")
    phase_version: str = Field(..., description="Phase version")
    
    total_requests: int = Field(..., description="Total requests processed")
    successful_parses: int = Field(..., description="Successful parses")
    failed_parses: int = Field(..., description="Failed parses")
    success_rate: float = Field(..., description="Success rate (0-1)")
    avg_confidence: float = Field(..., description="Average parsing confidence")
    avg_processing_time_ms: float = Field(..., description="Average processing time")
    
    gemini_status: Dict[str, Any] = Field(..., description="Gemini client status")
    telemetry_status: Dict[str, Any] = Field(..., description="Telemetry status")


# Phase 2: Architecture Sommelier Models

class ArchitectureRequest(BaseModel):
    """Request model for architecture selection"""
    
    phase1_result: Dict[str, Any] = Field(
        ...,
        description="Complete output from Phase 1"
    )
    
    user_id: Optional[str] = Field(
        None,
        description="Optional user identifier"
    )
    
    session_id: Optional[str] = Field(
        None,
        description="Optional session identifier"
    )


class ArchitectureResponse(BaseModel):
    """Response model for architecture selection"""
    
    request_id: str = Field(..., description="Unique request identifier")
    user_id: str = Field(..., description="User identifier")
    session_id: str = Field(..., description="Session identifier")
    phase: str = Field(..., description="Phase name")
    status: PhaseStatus = Field(..., description="Phase status")
    
    phase1_input: Dict[str, Any] = Field(
        ...,
        description="Summary of Phase 1 input"
    )
    
    architecture_analysis: Dict[str, Any] = Field(
        ...,
        description="Architecture selection analysis"
    )
    
    business_impact: Dict[str, Any] = Field(
        ...,
        description="Business impact assessment"
    )
    
    processing_metadata: Dict[str, Any] = Field(
        ...,
        description="Processing metadata"
    )
    
    timestamp: datetime = Field(..., description="Response timestamp")
    phase_version: str = Field(..., description="Phase implementation version")
    
    next_phase: str = Field(..., description="Next phase in workflow")
    phase_transition: Dict[str, Any] = Field(
        ...,
        description="Phase transition information"
    )


# Phase 3: Machine Specification Models

class MachineSpecificationRequest(BaseModel):
    """Request model for machine specification"""
    
    phase1_result: Dict[str, Any] = Field(
        ...,
        description="Complete output from Phase 1"
    )
    
    phase2_result: Dict[str, Any] = Field(
        ...,
        description="Complete output from Phase 2"
    )
    
    user_id: Optional[str] = Field(
        None,
        description="Optional user identifier"
    )
    
    session_id: Optional[str] = Field(
        None,
        description="Optional session identifier"
    )


class MachineSpecificationResponse(BaseModel):
    """Response model for machine specification"""
    
    request_id: str = Field(..., description="Unique request identifier")
    user_id: str = Field(..., description="User identifier")
    session_id: str = Field(..., description="Session identifier")
    phase: str = Field(..., description="Phase name")
    status: PhaseStatus = Field(..., description="Phase status")
    
    phase_inputs: Dict[str, Any] = Field(
        ...,
        description="Summary of Phase 1 & 2 inputs"
    )
    
    specification_analysis: Dict[str, Any] = Field(
        ...,
        description="Machine specification analysis"
    )
    
    configuration: Dict[str, Any] = Field(
        ...,
        description="Complete configuration details"
    )
    
    performance_assessment: Dict[str, Any] = Field(
        ...,
        description="Performance assessment"
    )
    
    cost_estimation_preview: Dict[str, Any] = Field(
        ...,
        description="Cost estimation preview"
    )
    
    processing_metadata: Dict[str, Any] = Field(
        ...,
        description="Processing metadata"
    )
    
    timestamp: datetime = Field(..., description="Response timestamp")
    phase_version: str = Field(..., description="Phase implementation version")
    
    next_phase: str = Field(..., description="Next phase in workflow")
    phase_transition: Dict[str, Any] = Field(
        ...,
        description="Phase transition information"
    )


# Phase 5: Tradeoff Analysis Models

class TradeoffAnalysisRequest(BaseModel):
    """Request model for tradeoff analysis"""
    
    phase1_result: Dict[str, Any] = Field(
        ...,
        description="Complete output from Phase 1"
    )
    
    phase2_result: Dict[str, Any] = Field(
        ...,
        description="Complete output from Phase 2"
    )
    
    phase3_result: Dict[str, Any] = Field(
        ...,
        description="Complete output from Phase 3"
    )
    
    phase4_result: Dict[str, Any] = Field(
        ...,
        description="Complete output from Phase 4"
    )
    
    user_id: Optional[str] = Field(
        None,
        description="Optional user identifier"
    )
    
    session_id: Optional[str] = Field(
        None,
        description="Optional session identifier"
    )


class TradeoffAnalysisResponse(BaseModel):
    """Response model for tradeoff analysis"""
    
    request_id: str = Field(..., description="Unique request identifier")
    user_id: str = Field(..., description="User identifier")
    session_id: str = Field(..., description="Session identifier")
    phase: str = Field(..., description="Phase name")
    status: PhaseStatus = Field(..., description="Phase status")
    
    analysis_id: str = Field(..., description="Analysis identifier")
    
    analysis_inputs: Dict[str, Any] = Field(
        ...,
        description="Summary of analysis inputs"
    )
    
    qualitative_analysis: Dict[str, Any] = Field(
        ...,
        description="Qualitative tradeoff analysis"
    )
    
    quantitative_analysis: Dict[str, Any] = Field(
        ...,
        description="Quantitative analysis and scores"
    )
    
    presentation_ready: Dict[str, Any] = Field(
        ...,
        description="Presentation-ready summary"
    )
    
    processing_metadata: Dict[str, Any] = Field(
        ...,
        description="Processing metadata"
    )
    
    timestamp: datetime = Field(..., description="Response timestamp")
    phase_version: str = Field(..., description="Phase implementation version")
    
    next_phase: str = Field(..., description="Next phase in workflow")
    phase_transition: Dict[str, Any] = Field(
        ...,
        description="Phase transition information"
    )



# Phase 4: Pricing Calculation Models

class PricingCalculationRequest(BaseModel):
    """Request model for pricing calculation"""
    
    phase1_result: Dict[str, Any] = Field(
        ...,
        description="Complete output from Phase 1"
    )
    
    phase2_result: Dict[str, Any] = Field(
        ...,
        description="Complete output from Phase 2"
    )
    
    phase3_result: Dict[str, Any] = Field(
        ...,
        description="Complete output from Phase 3"
    )
    
    user_id: Optional[str] = Field(
        None,
        description="Optional user identifier"
    )
    
    session_id: Optional[str] = Field(
        None,
        description="Optional session identifier"
    )


class PricingCalculationResponse(BaseModel):
    """Response model for pricing calculation"""
    
    request_id: str = Field(..., description="Unique request identifier")
    user_id: str = Field(..., description="User identifier")
    session_id: str = Field(..., description="Session identifier")
    phase: str = Field(..., description="Phase name")
    status: PhaseStatus = Field(..., description="Phase status")
    
    pricing_inputs: Dict[str, Any] = Field(
        ...,
        description="Summary of pricing inputs"
    )
    
    primary_price: Dict[str, Any] = Field(
        ...,
        description="Primary price calculation"
    )
    
    alternative_prices: Dict[str, float] = Field(
        ...,
        description="Alternative architecture prices"
    )
    
    pricing_accuracy: Dict[str, Any] = Field(
        ...,
        description="Pricing accuracy assessment"
    )
    
    savings_analysis: Dict[str, Any] = Field(
        ...,
        description="Savings potential analysis"
    )
    
    business_impact: Dict[str, Any] = Field(
        ...,
        description="Business impact assessment"
    )
    
    processing_metadata: Dict[str, Any] = Field(
        ...,
        description="Processing metadata"
    )
    
    timestamp: datetime = Field(..., description="Response timestamp")
    phase_version: str = Field(..., description="Phase implementation version")
    
    next_phase: str = Field(..., description="Next phase in workflow")
    phase_transition: Dict[str, Any] = Field(
        ...,
        description="Phase transition information"
    )


# Phase 6: Recommendation Presentation Models

class PresentationType(str, Enum):
    EXECUTIVE = "executive"
    DETAILED = "detailed"
    TECHNICAL = "technical"


class RecommendationPresentationRequest(BaseModel):
    """Request model for recommendation presentation"""
    
    phase1_result: Dict[str, Any] = Field(
        ...,
        description="Complete output from Phase 1"
    )
    
    phase2_result: Dict[str, Any] = Field(
        ...,
        description="Complete output from Phase 2"
    )
    
    phase3_result: Dict[str, Any] = Field(
        ...,
        description="Complete output from Phase 3"
    )
    
    phase4_result: Dict[str, Any] = Field(
        ...,
        description="Complete output from Phase 4"
    )
    
    phase5_result: Dict[str, Any] = Field(
        ...,
        description="Complete output from Phase 5"
    )
    
    presentation_type: PresentationType = Field(
        default=PresentationType.DETAILED,
        description="Type of presentation to generate"
    )
    
    user_id: Optional[str] = Field(
        None,
        description="Optional user identifier"
    )
    
    session_id: Optional[str] = Field(
        None,
        description="Optional session identifier"
    )


class RecommendationPresentationResponse(BaseModel):
    """Response model for recommendation presentation"""
    
    request_id: str = Field(..., description="Unique request identifier")
    user_id: str = Field(..., description="User identifier")
    session_id: str = Field(..., description="Session identifier")
    phase: str = Field(..., description="Phase name")
    status: PhaseStatus = Field(..., description="Phase status")
    
    presentation_id: str = Field(..., description="Presentation identifier")
    
    presentation_metadata: Dict[str, Any] = Field(
        ...,
        description="Presentation metadata"
    )
    
    presentation_data: Dict[str, Any] = Field(
        ...,
        description="Complete presentation data"
    )
    
    visual_components: Dict[str, Any] = Field(
        ...,
        description="Visual components and charts"
    )
    
    frontend_ready: Dict[str, Any] = Field(
        ...,
        description="Frontend-ready presentation data"
    )
    
    processing_metadata: Dict[str, Any] = Field(
        ...,
        description="Processing metadata"
    )
    
    timestamp: str = Field(..., description="Response timestamp")
    phase_version: str = Field(..., description="Phase implementation version")
    
    next_phase: str = Field(..., description="Next phase in workflow")
    phase_transition: Dict[str, Any] = Field(
        ...,
        description="Phase transition information"
    )


# Phase 7: User Decision & Telemetry Models

class DecisionType(str, Enum):
    """Decision type enum for Phase 7"""
    ACCEPTED = "accepted"
    CUSTOMIZED = "customized"
    REJECTED = "rejected"


class CustomizationDetails(BaseModel):
    """Customization details for user modifications"""
    
    changes: List[Dict[str, Any]] = Field(
        default=[],
        description="List of changes made by user"
    )
    
    reasoning: Optional[str] = Field(
        None,
        description="User's reasoning for customizations"
    )


class UserDecisionRequest(BaseModel):
    """Request model for user decision capture"""
    
    phase1_result: Dict[str, Any] = Field(
        ...,
        description="Complete output from Phase 1"
    )
    
    phase2_result: Dict[str, Any] = Field(
        ...,
        description="Complete output from Phase 2"
    )
    
    phase3_result: Dict[str, Any] = Field(
        ...,
        description="Complete output from Phase 3"
    )
    
    phase4_result: Dict[str, Any] = Field(
        ...,
        description="Complete output from Phase 4"
    )
    
    phase5_result: Dict[str, Any] = Field(
        ...,
        description="Complete output from Phase 5"
    )
    
    phase6_result: Dict[str, Any] = Field(
        ...,
        description="Complete output from Phase 6"
    )
    
    decision_type: DecisionType = Field(
        ...,
        description="User's decision (accepted, customized, rejected)"
    )
    
    customization_details: Optional[CustomizationDetails] = Field(
        None,
        description="Customization details if decision_type is customized"
    )
    
    user_feedback: Optional[str] = Field(
        None,
        description="Optional user feedback or comments"
    )
    
    decision_time_seconds: Optional[int] = Field(
        None,
        description="Time taken to make decision in seconds"
    )
    
    user_id: Optional[str] = Field(
        None,
        description="Optional user identifier"
    )
    
    session_id: Optional[str] = Field(
        None,
        description="Optional session identifier"
    )


class UserDecisionResponse(BaseModel):
    """Response model for user decision processing"""
    
    decision_id: str = Field(..., description="Unique decision identifier")
    request_id: str = Field(..., description="Unique request identifier")
    user_id: str = Field(..., description="User identifier")
    session_id: str = Field(..., description="Session identifier")
    phase: str = Field(..., description="Phase name")
    status: PhaseStatus = Field(..., description="Phase status")
    
    decision_type: DecisionType = Field(..., description="User's decision")
    decision_time_seconds: int = Field(..., description="Time to decision")
    
    decision_processing: Dict[str, Any] = Field(
        ...,
        description="Decision processing analysis"
    )
    
    customization_details: Optional[Dict[str, Any]] = Field(
        None,
        description="Customization details if applicable"
    )
    
    user_feedback: Dict[str, Any] = Field(
        ...,
        description="User feedback data"
    )
    
    artifacts: Dict[str, Any] = Field(
        ...,
        description="Generated deployment artifacts"
    )
    
    learning_signals: List[Dict[str, Any]] = Field(
        ...,
        description="Learning signals for Phase 8"
    )
    
    next_actions: List[Dict[str, Any]] = Field(
        ...,
        description="Recommended next actions"
    )
    
    processing_metadata: Dict[str, Any] = Field(
        ...,
        description="Processing metadata"
    )
    
    timestamp: str = Field(..., description="Response timestamp")
    phase_version: str = Field(..., description="Phase implementation version")
    
    next_phase: str = Field(..., description="Next phase in workflow")
    phase_transition: Dict[str, Any] = Field(
        ...,
        description="Phase transition information"
    )


# Phase 8: Learning Feedback & Continuous Improvement Models

class FeedbackType(str, Enum):
    """Feedback type enum for Phase 8"""
    OVER_PROVISIONED = "over_provisioned"
    UNDER_PROVISIONED = "under_provisioned"
    COST_HIGHER_THAN_EXPECTED = "cost_higher_than_expected"
    COST_LOWER_THAN_EXPECTED = "cost_lower_than_expected"
    PERFORMANCE_ISSUES = "performance_issues"
    ARCHITECTURE_MISMATCH = "architecture_mismatch"
    PERFECT_FIT = "perfect_fit"
    MINOR_ADJUSTMENTS_NEEDED = "minor_adjustments_needed"


class DeploymentFeedback(BaseModel):
    """Deployment feedback model"""
    
    type: FeedbackType = Field(
        ...,
        description="Type of feedback"
    )
    
    details: Optional[str] = Field(
        None,
        description="Additional feedback details"
    )


class PerformanceMetrics(BaseModel):
    """Actual performance metrics after deployment"""
    
    actual_rps: Optional[float] = Field(
        None,
        description="Actual requests per second"
    )
    
    actual_latency_ms: Optional[float] = Field(
        None,
        description="Actual latency in milliseconds"
    )
    
    avg_cpu_utilization: Optional[float] = Field(
        None,
        description="Average CPU utilization percentage"
    )
    
    avg_memory_utilization: Optional[float] = Field(
        None,
        description="Average memory utilization percentage"
    )


class CostActuals(BaseModel):
    """Actual cost data after deployment"""
    
    actual_monthly_cost: float = Field(
        ...,
        description="Actual monthly cost in USD"
    )


class LearningFeedbackRequest(BaseModel):
    """Request model for learning feedback processing"""
    
    phase7_result: Dict[str, Any] = Field(
        ...,
        description="Complete output from Phase 7"
    )
    
    deployment_feedback: Optional[DeploymentFeedback] = Field(
        None,
        description="Post-deployment feedback"
    )
    
    performance_metrics: Optional[PerformanceMetrics] = Field(
        None,
        description="Actual performance metrics"
    )
    
    cost_actuals: Optional[CostActuals] = Field(
        None,
        description="Actual cost data"
    )
    
    user_satisfaction: Optional[str] = Field(
        None,
        description="Overall user satisfaction rating"
    )
    
    feedback_delay_days: int = Field(
        default=0,
        description="Days since deployment"
    )
    
    user_id: Optional[str] = Field(
        None,
        description="Optional user identifier"
    )
    
    session_id: Optional[str] = Field(
        None,
        description="Optional session identifier"
    )


class LearningFeedbackResponse(BaseModel):
    """Response model for learning feedback processing"""
    
    learning_id: str = Field(..., description="Unique learning identifier")
    decision_id: str = Field(..., description="Related decision identifier")
    request_id: str = Field(..., description="Unique request identifier")
    user_id: str = Field(..., description="User identifier")
    session_id: str = Field(..., description="Session identifier")
    phase: str = Field(..., description="Phase name")
    phase_version: str = Field(..., description="Phase implementation version")
    model_version: str = Field(..., description="Learning model version")
    status: PhaseStatus = Field(..., description="Phase status")
    
    signals_analysis: Dict[str, Any] = Field(
        ...,
        description="Analysis of learning signals"
    )
    
    feedback_analysis: Optional[Dict[str, Any]] = Field(
        None,
        description="Deployment feedback analysis"
    )
    
    performance_analysis: Optional[Dict[str, Any]] = Field(
        None,
        description="Performance metrics analysis"
    )
    
    cost_analysis: Optional[Dict[str, Any]] = Field(
        None,
        description="Cost actuals analysis"
    )
    
    learning_updates: List[Dict[str, Any]] = Field(
        ...,
        description="Generated learning updates"
    )
    
    model_changes: List[Dict[str, Any]] = Field(
        ...,
        description="Applied model changes"
    )
    
    confidence_adjustments: Dict[str, Any] = Field(
        ...,
        description="Confidence adjustment data"
    )
    
    insights: List[Dict[str, Any]] = Field(
        ...,
        description="Improvement insights"
    )
    
    learning_summary: Dict[str, Any] = Field(
        ...,
        description="Summary of learning process"
    )
    
    model_state: Dict[str, Any] = Field(
        ...,
        description="Current model state"
    )
    
    processing_metadata: Dict[str, Any] = Field(
        ...,
        description="Processing metadata"
    )
    
    workflow_complete: bool = Field(
        ...,
        description="Whether the full workflow is complete"
    )
    
    workflow_summary: Dict[str, Any] = Field(
        ...,
        description="Summary of complete workflow"
    )