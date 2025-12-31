"""
Main FastAPI application for Google Cloud Sentinel
"""

import time
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn

from .models import ErrorResponse, HealthResponse
from .routers import analysis

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('app.log')
    ]
)

logger = logging.getLogger(__name__)

# Application start time
start_time = time.time()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for startup/shutdown events
    """
    # Startup
    logger.info("🚀 Starting Google Cloud Sentinel API...")
    logger.info("📊 Initializing Phase 1: Intent Capture...")
    
    # Import here to avoid circular imports
    from ..phases.phase1_intent_capture import IntentCapturePhase
    from ..phases.phase2_architecture_sommelier import ArchitectureSommelierPhase
    from ..phases.phase3_machine_specification import MachineSpecificationPhase
    from ..phases.phase4_pricing_calculation import PricingCalculationPhase
    from ..phases.phase5_tradeoff_analysis import TradeoffAnalysisPhase
    from ..phases.phase6_recommendation_presentation import RecommendationPresentationPhase
    from ..phases.phase7_user_decision import UserDecisionPhase
    from ..phases.phase8_learning_feedback import LearningFeedbackPhase
    
    # Initialize phases (this will log their own status)
    phase1 = IntentCapturePhase()
    phase2 = ArchitectureSommelierPhase()
    phase3 = MachineSpecificationPhase()
    phase4 = PricingCalculationPhase()
    phase5 = TradeoffAnalysisPhase()
    phase6 = RecommendationPresentationPhase()
    phase7 = UserDecisionPhase()
    phase8 = LearningFeedbackPhase()
    
    logger.info("✅ API startup complete")
    logger.info("📈 Available phases: Intent Capture, Architecture Sommelier, Machine Specification, Pricing Calculation, Tradeoff Analysis, Recommendation Presentation, User Decision, Learning Feedback")
    logger.info(f"🌐 API Documentation: http://localhost:8000/docs")
    
    yield
    
    # Shutdown
    logger.info("👋 Google Cloud Sentinel API shutting down...")
    
    # Flush any remaining telemetry
    try:
        phase1.telemetry.flush_buffers()
        phase2.telemetry.flush_buffers()
        phase3.telemetry.flush_buffers()
        phase4.telemetry.flush_buffers()
        phase5.telemetry.flush_buffers()
        phase6.telemetry.flush_buffers()
        phase7.telemetry.flush_buffers()
        phase8.telemetry.flush_buffers()
        logger.info("📡 Telemetry buffers flushed")
    except Exception as e:
        logger.error(f"Failed to flush telemetry: {e}")

# Create FastAPI app
app = FastAPI(
    title="Google Cloud Sentinel API",
    description="AI-Powered Infrastructure Recommendation System",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001", "http://localhost:3002"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(analysis.router)

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    
    return JSONResponse(
        status_code=500,
        content=ErrorResponse(
            error=True,
            message="Internal server error",
            code="INTERNAL_ERROR"
        ).dict()
    )

# Root endpoint
@app.get("/", include_in_schema=False)
async def root():
    return {
        "message": "Google Cloud Sentinel API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }

# Health check endpoint
@app.get("/health", response_model=HealthResponse)
async def health():
    """
    Health check endpoint
    
    Returns service health status and available phases.
    """
    uptime = time.time() - start_time
    
    return HealthResponse(
        status="healthy",
        service="google-cloud-sentinel",
        version="1.0.0",
        uptime_seconds=uptime,
        phases_available=["intent_capture"]
    )

# API info endpoint
@app.get("/api")
async def api_info():
    """
    API information endpoint
    
    Returns available endpoints and API version.
    """
    return {
        "api": "Google Cloud Sentinel",
        "version": "1.0.0",
        "endpoints": {
            "/health": "Service health check",
            "/api": "This information",
            "/docs": "Interactive API documentation",
            "/analysis/intent": "Capture user intent (Phase 1)",
            "/analysis/intent/statistics": "Get Phase 1 statistics",
            "/analysis/intent/status": "Get Phase 1 status",
            "/analysis/intent/reset-statistics": "Reset Phase 1 statistics"
        },
        "phases": {
            "1": "Intent Capture - Parse natural language infrastructure requests",
            "2": "Architecture Sommelier - Select optimal cloud architecture",
            "3": "Machine Specification - Choose appropriate compute resources",
            "4": "Real Pricing Calculation - Calculate accurate costs using GCP APIs",
            "5": "AI Tradeoff Analysis - Analyze alternatives and tradeoffs",
            "6": "Recommendation Presentation - Present final recommendation to user",
            "7": "User Decision & Telemetry - Capture user decisions and feedback",
            "8": "Feedback Loop & Continuous Learning - Learn from user feedback"
        }
    }

if __name__ == "__main__":
    # Run the application
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info",
        access_log=True
    )