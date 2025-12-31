"""
Analysis API router
"""

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from typing import Optional, Dict, Any

from ...phases.phase1_intent_capture import IntentCapturePhase
from ...phases.phase2_architecture_sommelier import ArchitectureSommelierPhase
from ...phases.phase3_machine_specification import MachineSpecificationPhase
from ...phases.phase4_pricing_calculation import PricingCalculationPhase
from ...phases.phase5_tradeoff_analysis import TradeoffAnalysisPhase
from ...phases.phase6_recommendation_presentation import RecommendationPresentationPhase
from ..models import (
    IntentRequest, IntentResponse, 
    ArchitectureRequest, ArchitectureResponse,
    MachineSpecificationRequest, MachineSpecificationResponse,
    PricingCalculationRequest, PricingCalculationResponse,
    TradeoffAnalysisRequest, TradeoffAnalysisResponse,
    RecommendationPresentationRequest, RecommendationPresentationResponse,
    ErrorResponse, PhaseStatistics
)

router = APIRouter(prefix="/analysis", tags=["analysis"])

# Initialize phases (singleton)
phase1 = IntentCapturePhase()
phase2 = ArchitectureSommelierPhase()
phase3 = MachineSpecificationPhase()
phase4 = PricingCalculationPhase()
phase5 = TradeoffAnalysisPhase()
phase6 = RecommendationPresentationPhase()

@router.post("/intent", response_model=IntentResponse, summary="Capture User Intent")
async def capture_intent(
    request: IntentRequest,
    background_tasks: BackgroundTasks
):
    """
    Capture and parse user infrastructure intent (Phase 1)
    
    This endpoint:
    1. Accepts natural language description of infrastructure needs
    2. Uses Gemini AI to parse intent into structured format
    3. Provides business insights and context
    4. Emits comprehensive telemetry
    5. Prepares for next phase (architecture selection)
    
    Returns complete intent analysis with metadata.
    """
    try:
        # Process intent
        result = await phase1.process(
            user_input=request.description,
            user_id=request.user_id,
            session_id=request.session_id,
            metadata=request.metadata
        )
        
        # Schedule telemetry flush in background
        background_tasks.add_task(phase1.telemetry.flush_buffers)
        
        return IntentResponse(**result)
        
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=ErrorResponse(
                error=True,
                message=str(e),
                code="VALIDATION_ERROR"
            ).dict()
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=ErrorResponse(
                error=True,
                message=f"Intent processing failed: {str(e)}",
                code="PROCESSING_ERROR"
            ).dict()
        )

@router.get("/intent/statistics", response_model=PhaseStatistics)
async def get_intent_statistics():
    """
    Get Phase 1 statistics
    
    Returns performance metrics, success rates, and system status.
    """
    try:
        stats = phase1.get_statistics()
        return PhaseStatistics(**stats)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=ErrorResponse(
                error=True,
                message=f"Failed to get statistics: {str(e)}",
                code="STATISTICS_ERROR"
            ).dict()
        )

@router.post("/intent/reset-statistics")
async def reset_intent_statistics():
    """
    Reset Phase 1 statistics
    
    Clears all accumulated statistics. Useful for testing.
    """
    try:
        phase1.reset_statistics()
        return {"message": "Statistics reset successfully", "success": True}
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=ErrorResponse(
                error=True,
                message=f"Failed to reset statistics: {str(e)}",
                code="RESET_ERROR"
            ).dict()
        )

@router.get("/intent/status")
async def get_intent_status():
    """
    Get Phase 1 status
    
    Returns system status including Gemini availability and telemetry configuration.
    """
    try:
        return phase1.get_status()
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=ErrorResponse(
                error=True,
                message=f"Failed to get status: {str(e)}",
                code="STATUS_ERROR"
            ).dict()
        )


# Phase 2: Architecture Sommelier Endpoints

@router.post("/architecture", response_model=ArchitectureResponse, summary="Select Optimal Architecture")
async def select_architecture(
    request: ArchitectureRequest,
    background_tasks: BackgroundTasks
):
    """
    Select optimal cloud architecture (Phase 2)
    
    This endpoint:
    1. Takes parsed intent from Phase 1
    2. Uses AI to select optimal architecture (serverless/containers/VMs)
    3. Provides confidence score and reasoning
    4. Emits comprehensive telemetry
    5. Prepares for next phase (machine specification)
    
    Returns complete architecture analysis with metadata.
    """
    try:
        # Process architecture selection
        result = phase2.process(
            phase1_result=request.phase1_result,
            user_id=request.user_id,
            session_id=request.session_id
        )
        
        # Schedule telemetry flush in background
        background_tasks.add_task(phase2.telemetry.flush_buffers)
        
        return ArchitectureResponse(**result)
        
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=ErrorResponse(
                error=True,
                message=str(e),
                code="VALIDATION_ERROR"
            ).dict()
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=ErrorResponse(
                error=True,
                message=f"Architecture selection failed: {str(e)}",
                code="PROCESSING_ERROR"
            ).dict()
        )


@router.get("/architecture/statistics")
async def get_architecture_statistics():
    """
    Get Phase 2 statistics
    
    Returns performance metrics, success rates, and system status.
    """
    try:
        return phase2.get_statistics()
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=ErrorResponse(
                error=True,
                message=f"Failed to get statistics: {str(e)}",
                code="STATISTICS_ERROR"
            ).dict()
        )


@router.post("/architecture/reset-statistics")
async def reset_architecture_statistics():
    """
    Reset Phase 2 statistics
    
    Clears all accumulated statistics. Useful for testing.
    """
    try:
        phase2.reset_statistics()
        return {"message": "Phase 2 statistics reset successfully", "success": True}
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=ErrorResponse(
                error=True,
                message=f"Failed to reset statistics: {str(e)}",
                code="RESET_ERROR"
            ).dict()
        )


@router.get("/architecture/status")
async def get_architecture_status():
    """
    Get Phase 2 status
    
    Returns system status including architecture catalog and telemetry.
    """
    try:
        return phase2.get_status()
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=ErrorResponse(
                error=True,
                message=f"Failed to get status: {str(e)}",
                code="STATUS_ERROR"
            ).dict()
        )
# Phase 3 Machine Specification
from ...phases.phase3_machine_specification import MachineSpecificationPhase
from ..models import MachineSpecificationRequest, MachineSpecificationResponse

# Initialize Phase 3
phase3 = MachineSpecificationPhase()

@router.post('/machine-specification', response_model=MachineSpecificationResponse, summary='Specify Machine Details')
async def specify_machine(request: MachineSpecificationRequest, background_tasks: BackgroundTasks):
    try:
        result = await phase3.process(
            phase1_result=request.phase1_result,
            phase2_result=request.phase2_result,
            user_id=request.user_id,
            session_id=request.session_id
        )
        background_tasks.add_task(phase3.telemetry.flush_buffers)
        return MachineSpecificationResponse(**result)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=ErrorResponse(error=True, message=str(e), code='VALIDATION_ERROR').dict())
    except Exception as e:
        raise HTTPException(status_code=500, detail=ErrorResponse(error=True, message=f'Machine specification failed: {str(e)}', code='PROCESSING_ERROR').dict())

@router.get('/machine-specification/statistics')
async def get_machine_specification_statistics():
    try:
        return phase3.get_statistics()
    except Exception as e:
        raise HTTPException(status_code=500, detail=ErrorResponse(error=True, message=f'Failed to get statistics: {str(e)}', code='STATISTICS_ERROR').dict())

@router.post('/machine-specification/reset-statistics')
async def reset_machine_specification_statistics():
    try:
        phase3.reset_statistics()
        return {'message': 'Phase 3 statistics reset successfully', 'success': True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=ErrorResponse(error=True, message=f'Failed to reset statistics: {str(e)}', code='RESET_ERROR').dict())

@router.get('/machine-specification/status')
async def get_machine_specification_status():
    try:
        return phase3.get_status()
    except Exception as e:
        raise HTTPException(status_code=500, detail=ErrorResponse(error=True, message=f'Failed to get status: {str(e)}', code='STATUS_ERROR').dict())


# ==================== Phase 4: Pricing Calculation Endpoints ====================

@router.post("/pricing-calculation", response_model=PricingCalculationResponse, summary="Calculate Real Pricing")
async def calculate_pricing(
    request: PricingCalculationRequest,
    background_tasks: BackgroundTasks
):
    """
    Calculate real pricing using GCP Billing API (Phase 4)
    
    This endpoint:
    1. Takes outputs from Phases 1-3
    2. Uses GCP Billing API to calculate real-time pricing
    3. Calculates alternative architecture prices for comparison
    4. Assesses pricing accuracy and savings potential
    5. Emits comprehensive telemetry
    6. Prepares for next phase (tradeoff analysis)
    
    Returns complete pricing calculation with metadata.
    """
    try:
        # Process pricing calculation
        result = await phase4.process(
            phase1_result=request.phase1_result,
            phase2_result=request.phase2_result,
            phase3_result=request.phase3_result,
            user_id=request.user_id,
            session_id=request.session_id
        )
        
        # Schedule telemetry flush in background
        background_tasks.add_task(phase4.telemetry.flush_buffers)
        
        return PricingCalculationResponse(**result)
        
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=ErrorResponse(
                error=True,
                message=str(e),
                code="VALIDATION_ERROR"
            ).dict()
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=ErrorResponse(
                error=True,
                message=f"Pricing calculation failed: {str(e)}",
                code="PROCESSING_ERROR"
            ).dict()
        )


@router.get("/pricing-calculation/statistics")
async def get_pricing_calculation_statistics():
    """
    Get Phase 4 statistics
    
    Returns performance metrics, accuracy rates, and system status.
    """
    try:
        return phase4.get_statistics()
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=ErrorResponse(
                error=True,
                message=f"Failed to get statistics: {str(e)}",
                code="STATISTICS_ERROR"
            ).dict()
        )


@router.post("/pricing-calculation/reset-statistics")
async def reset_pricing_calculation_statistics():
    """
    Reset Phase 4 statistics
    
    Clears all accumulated statistics. Useful for testing.
    """
    try:
        phase4.reset_statistics()
        return {"message": "Phase 4 statistics reset successfully", "success": True}
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=ErrorResponse(
                error=True,
                message=f"Failed to reset statistics: {str(e)}",
                code="RESET_ERROR"
            ).dict()
        )


@router.get("/pricing-calculation/status")
async def get_pricing_calculation_status():
    """
    Get Phase 4 status
    
    Returns system status including GCP Billing API availability.
    """
    try:
        return phase4.get_status()
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=ErrorResponse(
                error=True,
                message=f"Failed to get status: {str(e)}",
                code="STATUS_ERROR"
            ).dict()
        )


# Phase 5: Tradeoff Analysis

@router.post("/tradeoff-analysis", response_model=TradeoffAnalysisResponse, summary="Generate Tradeoff Analysis")
async def generate_tradeoff_analysis(
    request: TradeoffAnalysisRequest,
    background_tasks: BackgroundTasks
):
    """
    Generate AI-powered tradeoff analysis (Phase 5)
    
    This endpoint:
    1. Takes outputs from Phases 1-4
    2. Uses Gemini to generate comprehensive tradeoff analysis
    3. Compares primary recommendation with alternatives
    4. Provides qualitative and quantitative analysis
    5. Generates presentation-ready summary
    6. Emits comprehensive telemetry
    7. Prepares for next phase (recommendation presentation)
    
    Returns complete tradeoff analysis with metadata.
    """
    try:
        # Process tradeoff analysis
        result = await phase5.process(
            phase1_result=request.phase1_result,
            phase2_result=request.phase2_result,
            phase3_result=request.phase3_result,
            phase4_result=request.phase4_result,
            user_id=request.user_id,
            session_id=request.session_id
        )
        
        # Schedule telemetry flush in background
        background_tasks.add_task(phase5.telemetry.flush_buffers)
        
        return TradeoffAnalysisResponse(**result)
        
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=ErrorResponse(
                error=True,
                message=str(e),
                code="VALIDATION_ERROR"
            ).dict()
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=ErrorResponse(
                error=True,
                message=f"Tradeoff analysis failed: {str(e)}",
                code="PROCESSING_ERROR"
            ).dict()
        )


@router.get("/tradeoff-analysis/statistics")
async def get_tradeoff_analysis_statistics():
    """
    Get Phase 5 statistics
    
    Returns performance metrics, analysis quality, and system status.
    """
    try:
        return phase5.get_statistics()
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=ErrorResponse(
                error=True,
                message=f"Failed to get statistics: {str(e)}",
                code="STATISTICS_ERROR"
            ).dict()
        )


@router.post("/tradeoff-analysis/reset-statistics")
async def reset_tradeoff_analysis_statistics():
    """
    Reset Phase 5 statistics
    
    Clears all accumulated statistics. Useful for testing.
    """
    try:
        phase5.reset_statistics()
        return {"message": "Phase 5 statistics reset successfully", "success": True}
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=ErrorResponse(
                error=True,
                message=f"Failed to reset statistics: {str(e)}",
                code="RESET_ERROR"
            ).dict()
        )


@router.get("/tradeoff-analysis/status")
async def get_tradeoff_analysis_status():
    """
    Get Phase 5 status
    
    Returns system status including tradeoff factors and Gemini availability.
    """
    try:
        return phase5.get_status()
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=ErrorResponse(
                error=True,
                message=f"Failed to get status: {str(e)}",
                code="STATUS_ERROR"
            ).dict()
        )


# ==================== Phase 6: Recommendation Presentation Endpoints ====================

@router.post("/recommendation-presentation", response_model=RecommendationPresentationResponse, summary="Generate Recommendation Presentation")
async def generate_recommendation_presentation(
    request: RecommendationPresentationRequest,
    background_tasks: BackgroundTasks
):
    """
    Generate presentation-ready recommendation (Phase 6)
    
    This endpoint:
    1. Takes outputs from Phases 1-5
    2. Creates presentation-ready recommendation based on type
    3. Generates visual components (charts, tables, diagrams)
    4. Formats data for frontend consumption
    5. Provides executive, detailed, or technical presentations
    6. Emits comprehensive telemetry
    7. Prepares for next phase (user decision)
    
    Returns complete presentation with metadata and visuals.
    """
    try:
        # Process recommendation presentation
        result = await phase6.process(
            phase1_result=request.phase1_result,
            phase2_result=request.phase2_result,
            phase3_result=request.phase3_result,
            phase4_result=request.phase4_result,
            phase5_result=request.phase5_result,
            presentation_type=request.presentation_type.value,
            user_id=request.user_id,
            session_id=request.session_id
        )
        
        # Schedule telemetry flush in background
        background_tasks.add_task(phase6.telemetry.flush_buffers)
        
        return RecommendationPresentationResponse(**result)
        
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=ErrorResponse(
                error=True,
                message=str(e),
                code="VALIDATION_ERROR"
            ).dict()
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=ErrorResponse(
                error=True,
                message=f"Presentation generation failed: {str(e)}",
                code="PROCESSING_ERROR"
            ).dict()
        )


@router.get("/recommendation-presentation/statistics")
async def get_recommendation_presentation_statistics():
    """
    Get Phase 6 statistics
    
    Returns performance metrics, presentation types, and system status.
    """
    try:
        return phase6.get_statistics()
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=ErrorResponse(
                error=True,
                message=f"Failed to get statistics: {str(e)}",
                code="STATISTICS_ERROR"
            ).dict()
        )


@router.post("/recommendation-presentation/reset-statistics")
async def reset_recommendation_presentation_statistics():
    """
    Reset Phase 6 statistics
    
    Clears all accumulated statistics. Useful for testing.
    """
    try:
        phase6.reset_statistics()
        return {"message": "Phase 6 statistics reset successfully", "success": True}
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=ErrorResponse(
                error=True,
                message=f"Failed to reset statistics: {str(e)}",
                code="RESET_ERROR"
            ).dict()
        )


@router.get("/recommendation-presentation/status")
async def get_recommendation_presentation_status():
    """
    Get Phase 6 status
    
    Returns system status including presentation templates and visual generators.
    """
    try:
        return phase6.get_status()
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=ErrorResponse(
                error=True,
                message=f"Failed to get status: {str(e)}",
                code="STATUS_ERROR"
            ).dict()
        )


# Combined Endpoint: Run All Phases

def log_phase_decision(phase_name: str, phase_num: int, decision: str, confidence: float = None, 
                       reason: str = None, key_values: dict = None):
    """Print structured phase decision to terminal for validation"""
    separator = "=" * 60
    print(f"\n{separator}")
    print(f"[PHASE {phase_num} - {phase_name.upper()}]")
    print(separator)
    print(f"Decision: {decision}")
    if confidence is not None:
        print(f"Confidence: {confidence * 100:.0f}%")
    if reason:
        print(f"Reason: {reason}")
    if key_values:
        print("Key Values:")
        for k, v in key_values.items():
            print(f"  - {k}: {v}")
    print(separator)


@router.post("/complete", summary="Complete Analysis Pipeline")
async def complete_analysis(
    request: IntentRequest,
    background_tasks: BackgroundTasks
):
    """
    Run complete analysis pipeline (Phases 1-6)
    
    This endpoint:
    1. Captures user intent
    2. Selects optimal architecture
    3. Specifies machine configurations
    4. Calculates pricing
    5. Analyzes trade-offs
    6. Presents final recommendation
    
    Returns all phase results in a single response.
    """
    try:
        print("\n" + "=" * 60)
        print("INFRONAI ANALYSIS PIPELINE - START")
        print(f"Input: {request.description[:80]}...")
        print("=" * 60)
        
        results = {
            "status": "processing",
            "phases": {}
        }
        
        # Phase 1: Intent Capture
        phase1_result = await phase1.process(
            user_input=request.description,
            user_id=request.user_id,
            session_id=request.session_id,
            metadata=request.metadata
        )
        results["phases"]["phase1"] = phase1_result
        
        # Log Phase 1 decision
        intent = phase1_result.get("intent_analysis", {})
        log_phase_decision(
            "Intent Capture", 1,
            decision=f"Workload: {intent.get('workload_type', 'unknown')}",
            confidence=intent.get("parsing_confidence", 0.85),
            key_values={
                "Scale": f"{intent.get('scale', {}).get('monthly_users', 0):,} users/month",
                "RPS": intent.get('scale', {}).get('estimated_rps', 0),
                "Geography": intent.get('requirements', {}).get('geography', 'unknown'),
                "Latency": intent.get('requirements', {}).get('latency', 'medium'),
                "Availability": intent.get('requirements', {}).get('availability', 'high')
            }
        )
        
        # Phase 2: Architecture Selection
        phase2_result = await phase2.process(
            phase1_result=phase1_result,
            user_id=request.user_id,
            session_id=request.session_id
        )
        results["phases"]["phase2"] = phase2_result
        
        # Log Phase 2 decision
        arch = phase2_result.get("architecture_analysis", {})
        alternatives = arch.get("alternatives", [])
        alt_names = [a.get("architecture", "") for a in alternatives[:2]]
        log_phase_decision(
            "Architecture Selection", 2,
            decision=f"Selected: {arch.get('primary_architecture', 'unknown').upper()}",
            confidence=arch.get("confidence", 0.85),
            reason=arch.get("reasoning", "")[:100],
            key_values={
                "Alternatives Considered": ", ".join(alt_names) if alt_names else "None"
            }
        )
        
        # Phase 3: Machine Specification
        phase3_result = await phase3.process(
            phase1_result=phase1_result,
            phase2_result=phase2_result,
            user_id=request.user_id,
            session_id=request.session_id
        )
        results["phases"]["phase3"] = phase3_result
        
        # Log Phase 3 decision
        spec = phase3_result.get("specification_analysis", {})
        config = phase3_result.get("configuration", {})
        log_phase_decision(
            "Machine Specification", 3,
            decision=f"Machine: {spec.get('exact_type', 'unknown')}",
            confidence=spec.get("confidence", 0.85),
            reason=spec.get("sizing_rationale", "")[:100],
            key_values={
                "vCPU": spec.get("cpu", 0),
                "RAM": f"{spec.get('ram', 0)} GB",
                "Region": config.get("region", "unknown"),
                "Instances": f"{config.get('instances', 1)} (auto-scale: {config.get('auto_scaling', {}).get('min_instances', 1)}-{config.get('auto_scaling', {}).get('max_instances', 10)})"
            }
        )
        
        # Phase 4: Pricing Calculation
        phase4_result = await phase4.process(
            phase1_result=phase1_result,
            phase2_result=phase2_result,
            phase3_result=phase3_result,
            user_id=request.user_id,
            session_id=request.session_id
        )
        results["phases"]["phase4"] = phase4_result
        
        # Log Phase 4 decision
        price = phase4_result.get("primary_price", {})
        breakdown = price.get("breakdown", {})
        alt_prices = phase4_result.get("alternative_prices", {})
        log_phase_decision(
            "Pricing Calculation", 4,
            decision=f"Monthly Cost: ${price.get('total_monthly_usd', 0):,.2f}",
            confidence=phase4_result.get("accuracy_estimate", 0.85),
            key_values={
                "Compute": f"${breakdown.get('compute', 0):,.2f}",
                "Storage": f"${breakdown.get('storage', 0):,.2f}",
                "Networking": f"${breakdown.get('networking', 0):,.2f}",
                "Alternatives": ", ".join([f"{arch}: ${cost:,.2f}" for arch, cost in list(alt_prices.items())[:2]])
            }
        )
        
        # Phase 5: Trade-off Analysis
        phase5_result = await phase5.process(
            phase1_result=phase1_result,
            phase2_result=phase2_result,
            phase3_result=phase3_result,
            phase4_result=phase4_result,
            user_id=request.user_id,
            session_id=request.session_id
        )
        results["phases"]["phase5"] = phase5_result
        
        # Log Phase 5 decision
        tradeoff = phase5_result.get("tradeoff_analysis", {})
        pros = tradeoff.get("pros", [])
        cons = tradeoff.get("cons", [])
        log_phase_decision(
            "Trade-off Analysis", 5,
            decision=f"Recommendation Strength: {tradeoff.get('recommendation_strength', 'moderate').upper()}",
            key_values={
                "Pros": len(pros),
                "Cons": len(cons),
                "Top Pro": (pros[0].get("point", "") if pros and isinstance(pros[0], dict) else str(pros[0]) if pros else "N/A")[:50],
                "Top Con": (cons[0].get("point", "") if cons and isinstance(cons[0], dict) else str(cons[0]) if cons else "N/A")[:50]
            }
        )
        
        # Phase 6: Recommendation Presentation
        phase6_result = await phase6.process(
            phase1_result=phase1_result,
            phase2_result=phase2_result,
            phase3_result=phase3_result,
            phase4_result=phase4_result,
            phase5_result=phase5_result,
            user_id=request.user_id,
            session_id=request.session_id
        )
        results["phases"]["phase6"] = phase6_result
        
        # Log Phase 6 decision
        presentation = phase6_result.get("presentation", {})
        recommendation = presentation.get("recommendation", {})
        consolidated = phase6_result.get("consolidated_data", {})
        log_phase_decision(
            "Final Recommendation", 6,
            decision=recommendation.get("headline", "Use recommended architecture"),
            confidence=recommendation.get("confidence_score", 0.88),
            key_values={
                "Architecture": consolidated.get("architecture", "serverless"),
                "Machine": consolidated.get("machine_type", "n2-standard-4"),
                "Monthly Cost": f"${consolidated.get('monthly_cost', 0):,.2f}",
                "Region": consolidated.get("region", "us-east1")
            }
        )
        
        print("\n" + "=" * 60)
        print("INFRONAI ANALYSIS PIPELINE - COMPLETE")
        print("=" * 60 + "\n")
        
        results["status"] = "completed"
        results["session_id"] = request.session_id
        
        # Schedule telemetry flush in background
        background_tasks.add_task(phase1.telemetry.flush_buffers)
        background_tasks.add_task(phase2.telemetry.flush_buffers)
        background_tasks.add_task(phase3.telemetry.flush_buffers)
        background_tasks.add_task(phase4.telemetry.flush_buffers)
        background_tasks.add_task(phase5.telemetry.flush_buffers)
        background_tasks.add_task(phase6.telemetry.flush_buffers)
        
        return results
        
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=ErrorResponse(
                error=True,
                message=str(e),
                code="VALIDATION_ERROR"
            ).dict()
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=ErrorResponse(
                error=True,
                message=f"Analysis pipeline failed: {str(e)}",
                code="PROCESSING_ERROR"
            ).dict()
        )
