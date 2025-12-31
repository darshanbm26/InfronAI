"""
Registry of all metrics for Google Cloud Sentinel
"""

from typing import Dict, List, Any
from dataclasses import dataclass
from enum import Enum

class MetricType(Enum):
    GAUGE = "gauge"
    COUNT = "count"
    RATE = "rate"
    HISTOGRAM = "histogram"

@dataclass
class MetricDefinition:
    name: str
    type: MetricType
    description: str
    tags: List[str]
    unit: str = ""

# Phase 1: Intent Capture Metrics
INTENT_CAPTURE_METRICS = [
    MetricDefinition(
        name="ai.intent.parsing.confidence",
        type=MetricType.GAUGE,
        description="Confidence score of AI intent parsing (0.0-1.0)",
        tags=["workload_type", "parsing_source", "phase"],
        unit="percentage"
    ),
    MetricDefinition(
        name="ai.intent.processing.time_ms",
        type=MetricType.HISTOGRAM,
        description="Time taken to parse user intent in milliseconds",
        tags=["workload_type", "phase", "success"],
        unit="milliseconds"
    ),
    MetricDefinition(
        name="user.input.length",
        type=MetricType.HISTOGRAM,
        description="Length of user input in characters",
        tags=["phase"],
        unit="characters"
    ),
    MetricDefinition(
        name="ai.parsing.success.rate",
        type=MetricType.RATE,
        description="Success rate of intent parsing",
        tags=["workload_type", "phase"],
        unit="percentage"
    )
]

# Phase 2: Architecture Sommelier Metrics
ARCHITECTURE_METRICS = [
    MetricDefinition(
        name="ai.architecture.selection.confidence",
        type=MetricType.GAUGE,
        description="Confidence score of architecture selection (0.0-1.0)",
        tags=["architecture", "workload_type", "selection_method", "phase"],
        unit="percentage"
    ),
    MetricDefinition(
        name="ai.architecture.processing.time_ms",
        type=MetricType.HISTOGRAM,
        description="Time taken to select architecture in milliseconds",
        tags=["architecture", "workload_type", "phase", "success"],
        unit="milliseconds"
    ),
    MetricDefinition(
        name="business.architecture.distribution",
        type=MetricType.GAUGE,
        description="Distribution of selected architectures by workload type",
        tags=["architecture", "workload_type", "scale_tier"],
        unit="percentage"
    ),
    MetricDefinition(
        name="ai.architecture.selection.rate",
        type=MetricType.RATE,
        description="Success rate of architecture selection",
        tags=["workload_type", "phase"],
        unit="percentage"
    )
]

# Business Metrics
BUSINESS_METRICS = [
    MetricDefinition(
        name="business.user.session.start",
        type=MetricType.COUNT,
        description="Count of user sessions started",
        tags=["user_experience", "phase"],
        unit="count"
    ),
    MetricDefinition(
        name="business.workload.distribution",
        type=MetricType.GAUGE,
        description="Distribution of workload types requested",
        tags=["workload_type", "geography"],
        unit="percentage"
    )
]

# Phase 3: Machine Specification Metrics
MACHINE_SPECIFICATION_METRICS = [
    MetricDefinition(
        name="ai.machine.specification.confidence",
        type=MetricType.GAUGE,
        description="Confidence score of machine specification (0.0-1.0)",
        tags=["machine_family", "workload_type", "selection_method", "phase"],
        unit="percentage"
    ),
    MetricDefinition(
        name="ai.machine.specification.processing.time_ms",
        type=MetricType.HISTOGRAM,
        description="Time taken to specify machine in milliseconds",
        tags=["workload_type", "phase", "success"],
        unit="milliseconds"
    ),
    MetricDefinition(
        name="ai.machine.specification.type",
        type=MetricType.COUNT,
        description="Distribution of machine types selected",
        tags=["machine_type", "architecture", "workload_type", "phase", "selection_method", "catalog_match"],
        unit="count"
    ),
    MetricDefinition(
        name="ai.machine.specification.cpu",
        type=MetricType.GAUGE,
        description="CPU cores specified for workload",
        tags=["machine_family", "workload_type", "phase"],
        unit="cores"
    ),
    MetricDefinition(
        name="ai.machine.specification.ram",
        type=MetricType.GAUGE,
        description="RAM (GB) specified for workload",
        tags=["machine_family", "workload_type", "phase"],
        unit="gigabytes"
    )
]

# Phase 4: Pricing Calculation Metrics
PRICING_CALCULATION_METRICS = [
    MetricDefinition(
        name="pricing.calculation.total",
        type=MetricType.GAUGE,
        description="Total monthly price calculated in USD",
        tags=["architecture", "workload_type", "phase", "calculation_method", "region", "affordability_tier"],
        unit="usd"
    ),
    MetricDefinition(
        name="pricing.calculation.accuracy",
        type=MetricType.GAUGE,
        description="Estimated pricing accuracy (0.0-1.0)",
        tags=["architecture", "workload_type", "phase", "calculation_method", "api_available"],
        unit="percentage"
    ),
    MetricDefinition(
        name="pricing.calculation.processing.time_ms",
        type=MetricType.HISTOGRAM,
        description="Time taken to calculate pricing in milliseconds",
        tags=["workload_type", "phase", "success", "calculation_method"],
        unit="milliseconds"
    ),
    MetricDefinition(
        name="pricing.savings.potential",
        type=MetricType.GAUGE,
        description="Potential monthly savings vs alternatives in USD",
        tags=["architecture", "workload_type", "phase"],
        unit="usd"
    )
]

# Phase 5: Tradeoff Analysis Metrics
TRADEOFF_ANALYSIS_METRICS = [
    MetricDefinition(
        name="ai.tradeoff.analysis.strength",
        type=MetricType.GAUGE,
        description="Recommendation strength score (0-100)",
        tags=["architecture", "workload_type", "phase", "analysis_method", "team_experience", "budget_sensitivity"],
        unit="score"
    ),
    MetricDefinition(
        name="ai.tradeoff.analysis.quality",
        type=MetricType.GAUGE,
        description="Analysis quality score (0-100)",
        tags=["architecture", "workload_type", "phase", "analysis_method"],
        unit="score"
    ),
    MetricDefinition(
        name="ai.tradeoff.analysis.overall_score",
        type=MetricType.GAUGE,
        description="Overall tradeoff score (0-100)",
        tags=["architecture", "workload_type", "phase", "recommendation_category"],
        unit="score"
    ),
    MetricDefinition(
        name="ai.tradeoff.analysis.processing.time_ms",
        type=MetricType.HISTOGRAM,
        description="Time taken to generate tradeoff analysis in milliseconds",
        tags=["workload_type", "phase", "success", "analysis_method"],
        unit="milliseconds"
    )
]

# Combine all metrics
ALL_METRICS = (
    INTENT_CAPTURE_METRICS + 
    ARCHITECTURE_METRICS + 
    MACHINE_SPECIFICATION_METRICS + 
    PRICING_CALCULATION_METRICS +
    TRADEOFF_ANALYSIS_METRICS +
    BUSINESS_METRICS
)

def get_metric_definitions() -> Dict[str, MetricDefinition]:
    """Get all metric definitions as a dictionary"""
    return {metric.name: metric for metric in ALL_METRICS}

def validate_metric_name(metric_name: str) -> bool:
    """Validate if a metric name exists in registry"""
    return metric_name in get_metric_definitions()