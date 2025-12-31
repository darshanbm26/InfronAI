"""
Phase 1: User Intent Capture
Production-grade implementation with full telemetry
"""

import time
import logging
import hashlib
import uuid
from typing import Dict, Any, Optional
from datetime import datetime

from ..core.gemini_client import GeminiClient
from ..telemetry.datadog_client import TelemetryClient, TelemetryConfig, TelemetryMode

logger = logging.getLogger(__name__)

class IntentCapturePhase:
    """Complete Phase 1: User Intent Capture"""
    
    def __init__(self, telemetry_config: Optional[TelemetryConfig] = None):
        self.phase_name = "intent_capture"
        self.phase_version = "1.0.0"
        
        # Initialize clients
        self.gemini = GeminiClient()
        self.telemetry = TelemetryClient(telemetry_config)
        
        # Statistics
        self.stats = {
            "total_requests": 0,
            "successful_parses": 0,
            "failed_parses": 0,
            "total_processing_time_ms": 0,
            "avg_confidence": 0.0
        }
        
        logger.info(f"✅ Phase 1 initialized: {self.phase_name} v{self.phase_version}")
        logger.info(f"   Gemini Mode: {'API' if not self.gemini.mock_mode else 'Mock'}")
        logger.info(f"   Telemetry Mode: {self.telemetry.config.mode.value}")
    
    async def process(self, user_input: str, user_id: Optional[str] = None,
                     session_id: Optional[str] = None, metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Process user intent with comprehensive telemetry
        
        Args:
            user_input: Natural language description of infrastructure needs
            user_id: Optional user identifier
            session_id: Optional session identifier
            metadata: Optional additional metadata
            
        Returns:
            Dict containing parsed intent with full context
        """
        start_time = time.time()
        
        # Validate input before processing
        if not user_input or len(user_input.strip()) < 10:
            raise ValueError(
                "Description must be at least 10 characters. "
                f"Received: '{user_input[:50] if user_input else ''}...' ({len(user_input) if user_input else 0} chars)"
            )
        
        self.stats["total_requests"] += 1
        
        # Generate IDs if not provided
        user_id = user_id or f"user_{uuid.uuid4().hex[:8]}"
        session_id = session_id or f"session_{uuid.uuid4().hex[:8]}"
        request_id = f"req_{int(time.time())}_{hashlib.md5(user_input.encode()).hexdigest()[:6]}"
        
        # Emit session start event
        self._emit_session_start(user_id, session_id, request_id, metadata)
        
        try:
            logger.info(f"🔍 Processing intent - User: {user_id}, Session: {session_id}")
            
            # Step 1: Parse intent
            intent_result = self.gemini.parse_intent(user_input)
            
            # Step 2: Enhance with metadata
            enhanced_result = self._enhance_intent_result(
                intent_result, user_id, session_id, request_id, user_input, metadata
            )
            
            # Step 3: Calculate processing time
            processing_time_ms = int((time.time() - start_time) * 1000)
            enhanced_result["processing_metadata"]["processing_time_ms"] = processing_time_ms
            
            # Step 4: Update statistics
            self._update_statistics(enhanced_result, processing_time_ms, success=True)
            
            # Step 5: Emit telemetry
            self._emit_success_telemetry(enhanced_result, processing_time_ms)
            
            logger.info(f"✅ Intent captured successfully")
            logger.info(f"   Workload: {enhanced_result['intent_analysis']['workload_type']}")
            logger.info(f"   Confidence: {enhanced_result['intent_analysis']['parsing_confidence']}")
            logger.info(f"   Time: {processing_time_ms}ms")
            
            return enhanced_result
            
        except Exception as e:
            # Handle failures gracefully
            processing_time_ms = int((time.time() - start_time) * 1000)
            self.stats["failed_parses"] += 1
            
            error_result = self._create_error_result(
                user_id, session_id, request_id, user_input, str(e), processing_time_ms
            )
            
            self._emit_error_telemetry(error_result, str(e))
            
            logger.error(f"❌ Intent capture failed: {e}")
            raise
    
    def _enhance_intent_result(self, intent_result: Dict[str, Any], user_id: str,
                              session_id: str, request_id: str, user_input: str,
                              metadata: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Enhance raw intent result with metadata"""
        
        # Calculate input metrics
        input_length = len(user_input)
        word_count = len(user_input.split())
        
        # Create enhanced structure
        enhanced = {
            "request_id": request_id,
            "user_id": user_id,
            "session_id": session_id,
            "phase": self.phase_name,
            "phase_version": self.phase_version,
            "timestamp": datetime.utcnow().isoformat(),
            "status": "completed",
            
            "input_metadata": {
                "raw_input": user_input,
                "input_length": input_length,
                "word_count": word_count,
                "language": "en",  # Could detect language
                "has_special_chars": any(not c.isalnum() and not c.isspace() for c in user_input)
            },
            
            "intent_analysis": intent_result,
            
            "processing_metadata": {
                "gemini_mode": "api" if not self.gemini.mock_mode else "mock",
                "llm_model": intent_result.get("llm_model", "unknown"),
                "parsing_source": intent_result.get("parsing_source", "unknown"),
                "processing_start_time": time.time(),
                "cache_hit": False  # Could implement caching later
            },
            
            "business_context": {
                "workload_category": self._categorize_workload(intent_result["workload_type"]),
                "scale_tier": self._determine_scale_tier(intent_result["scale"]["monthly_users"]),
                "complexity_score": self._calculate_complexity_score(intent_result),
                "estimated_cloud_spend": self._estimate_cloud_spend(intent_result),
                "risk_level": self._assess_risk_level(intent_result)
            },
            
            "next_phase": "architecture_selection",
            "phase_transition": {
                "recommended": True,
                "estimated_time_seconds": 15,
                "prerequisites_met": True
            }
        }
        
        # Add metadata if provided
        if metadata:
            enhanced["user_metadata"] = metadata
        
        return enhanced
    
    def _categorize_workload(self, workload_type: str) -> str:
        """Categorize workload into broader categories"""
        categories = {
            "api_backend": "compute_intensive",
            "web_app": "compute_intensive",
            "data_processing": "data_intensive",
            "ml_inference": "ai_ml",
            "batch_processing": "data_intensive",
            "realtime_streaming": "realtime",
            "mobile_backend": "compute_intensive",
            "gaming_server": "realtime"
        }
        return categories.get(workload_type, "general")
    
    def _determine_scale_tier(self, monthly_users: int) -> str:
        """Determine scale tier based on monthly users"""
        if monthly_users < 1000:
            return "tier_1_tiny"
        elif monthly_users < 10000:
            return "tier_2_small"
        elif monthly_users < 100000:
            return "tier_3_medium"
        elif monthly_users < 1000000:
            return "tier_4_large"
        else:
            return "tier_5_enterprise"
    
    def _calculate_complexity_score(self, intent_result: Dict[str, Any]) -> float:
        """Calculate complexity score (0-1) based on requirements"""
        score = 0.0
        
        # Base score from workload type
        workload_scores = {
            "api_backend": 0.3,
            "web_app": 0.3,
            "data_processing": 0.5,
            "ml_inference": 0.7,
            "batch_processing": 0.4,
            "realtime_streaming": 0.6,
            "mobile_backend": 0.4,
            "gaming_server": 0.8
        }
        score += workload_scores.get(intent_result["workload_type"], 0.5)
        
        # Adjust based on requirements
        if intent_result["requirements"]["latency"] in ["low", "ultra_low"]:
            score += 0.2
        if intent_result["requirements"]["availability"] in ["high", "critical"]:
            score += 0.2
        if intent_result["requirements"]["compliance"]:
            score += 0.1 * len(intent_result["requirements"]["compliance"])
        
        # Adjust based on constraints
        if intent_result["constraints"]["budget_sensitivity"] == "high":
            score += 0.1
        if intent_result["constraints"]["team_experience"] in ["beginner", "junior"]:
            score += 0.2
        
        return min(score, 1.0)
    
    def _estimate_cloud_spend(self, intent_result: Dict[str, Any]) -> Dict[str, Any]:
        """Estimate cloud spend based on intent"""
        monthly_users = intent_result["scale"]["monthly_users"]
        workload_type = intent_result["workload_type"]
        
        # Base estimates (simplified - will be refined in Phase 4)
        estimates = {
            "api_backend": monthly_users * 0.05,
            "web_app": monthly_users * 0.03,
            "data_processing": monthly_users * 0.08,
            "ml_inference": monthly_users * 0.15,
            "batch_processing": monthly_users * 0.04,
            "realtime_streaming": monthly_users * 0.10,
            "mobile_backend": monthly_users * 0.06,
            "gaming_server": monthly_users * 0.20
        }
        
        base_cost = estimates.get(workload_type, monthly_users * 0.05)
        
        # Adjustments
        if intent_result["requirements"]["geography"] == "global":
            base_cost *= 1.3
        if intent_result["requirements"]["availability"] == "critical":
            base_cost *= 1.5
        
        return {
            "estimated_monthly_usd": round(base_cost, 2),
            "confidence": "low",  # Will be high after Phase 4
            "cost_drivers": ["compute", "bandwidth", "storage"],
            "optimization_potential": 0.3  # 30% potential savings
        }
    
    def _assess_risk_level(self, intent_result: Dict[str, Any]) -> str:
        """Assess risk level based on constraints and requirements"""
        risk_factors = 0
        
        if intent_result["constraints"]["team_experience"] in ["beginner", "junior"]:
            risk_factors += 1
        if intent_result["requirements"]["availability"] == "critical":
            risk_factors += 1
        if intent_result["requirements"]["compliance"]:
            risk_factors += 1
        if intent_result["constraints"]["time_to_market"] == "immediate":
            risk_factors += 1
        
        if risk_factors == 0:
            return "low"
        elif risk_factors <= 2:
            return "medium"
        else:
            return "high"
    
    def _emit_session_start(self, user_id: str, session_id: str, request_id: str,
                           metadata: Optional[Dict[str, Any]]):
        """Emit session start telemetry"""
        self.telemetry.emit_event(
            title="User Session Started",
            text=f"User {user_id} started infrastructure analysis session",
            tags=["session_start", f"user:{user_id}", f"session:{session_id}", "phase:intent_capture"],
            alert_type="info"
        )
        
        self.telemetry.submit_metric(
            name="business.user.session.start",
            value=1.0,
            tags=[f"user:{user_id}", "phase:intent_capture"]
        )
    
    def _emit_success_telemetry(self, result: Dict[str, Any], processing_time_ms: int):
        """Emit success telemetry"""
        intent = result["intent_analysis"]
        business = result["business_context"]
        
        # Emit confidence metric
        self.telemetry.submit_metric(
            name="ai.intent.parsing.confidence",
            value=intent["parsing_confidence"],
            tags=[
                f"workload_type:{intent['workload_type']}",
                f"parsing_source:{intent.get('parsing_source', 'unknown')}",
                f"phase:{self.phase_name}",
                f"scale_tier:{business['scale_tier']}",
                f"complexity:{business['complexity_score']:.2f}"
            ]
        )
        
        # Emit processing time metric
        self.telemetry.submit_metric(
            name="ai.intent.processing.time_ms",
            value=processing_time_ms,
            tags=[
                f"workload_type:{intent['workload_type']}",
                f"phase:{self.phase_name}",
                f"success:true",
                f"gemini_mode:{'api' if not self.gemini.mock_mode else 'mock'}"
            ]
        )
        
        # Emit input length metric
        self.telemetry.submit_metric(
            name="user.input.length",
            value=result["input_metadata"]["input_length"],
            tags=[f"phase:{self.phase_name}", f"workload_type:{intent['workload_type']}"]
        )
        
        # Emit workload distribution metric
        self.telemetry.submit_metric(
            name="business.workload.distribution",
            value=1.0,
            tags=[
                f"workload_type:{intent['workload_type']}",
                f"geography:{intent['requirements']['geography']}",
                f"scale_tier:{business['scale_tier']}"
            ]
        )
        
        # Emit success log
        self.telemetry.submit_log(
            source="cloud-sentinel",
            message={
                "event": "intent_parsed_success",
                "request_id": result["request_id"],
                "user_id": result["user_id"],
                "session_id": result["session_id"],
                "workload_type": intent["workload_type"],
                "parsing_confidence": intent["parsing_confidence"],
                "processing_time_ms": processing_time_ms,
                "scale_tier": business["scale_tier"],
                "estimated_cost_usd": business["estimated_cloud_spend"]["estimated_monthly_usd"],
                "risk_level": business["risk_level"]
            },
            tags=["intent_parsing", "success", intent["workload_type"], f"phase:{self.phase_name}"]
        )
        
        # Emit success event
        self.telemetry.emit_event(
            title="Intent Successfully Parsed",
            text=f"Parsed {intent['workload_type']} workload with {intent['parsing_confidence']*100:.1f}% confidence",
            tags=[
                "intent_parsed", 
                intent["workload_type"],
                f"confidence:{intent['parsing_confidence']:.2f}",
                f"user:{result['user_id']}",
                f"phase:{self.phase_name}"
            ],
            alert_type="success"
        )
    
    def _create_error_result(self, user_id: str, session_id: str, request_id: str,
                            user_input: str, error_message: str, processing_time_ms: int) -> Dict[str, Any]:
        """Create error result structure"""
        return {
            "request_id": request_id,
            "user_id": user_id,
            "session_id": session_id,
            "phase": self.phase_name,
            "timestamp": datetime.utcnow().isoformat(),
            "status": "error",
            "error": {
                "message": error_message,
                "code": "INTENT_PARSING_FAILED",
                "user_input": user_input[:500]  # Truncate long inputs
            },
            "processing_metadata": {
                "processing_time_ms": processing_time_ms,
                "gemini_mode": "api" if not self.gemini.mock_mode else "mock",
                "attempted_retry": False
            },
            "fallback_suggestion": {
                "suggested_workload": "api_backend",
                "estimated_confidence": 0.5,
                "recommendation": "Please rephrase your request with more specific details about your infrastructure needs."
            }
        }
    
    def _emit_error_telemetry(self, error_result: Dict[str, Any], error_message: str):
        """Emit error telemetry"""
        self.telemetry.submit_metric(
            name="ai.intent.processing.time_ms",
            value=error_result["processing_metadata"]["processing_time_ms"],
            tags=[
                f"phase:{self.phase_name}",
                f"success:false",
                f"error_code:{error_result['error']['code']}"
            ]
        )
        
        self.telemetry.submit_log(
            source="cloud-sentinel",
            message={
                "event": "intent_parsing_failed",
                "request_id": error_result["request_id"],
                "user_id": error_result["user_id"],
                "error": error_result["error"],
                "processing_time_ms": error_result["processing_metadata"]["processing_time_ms"]
            },
            tags=["intent_parsing", "error", error_result["error"]["code"], f"phase:{self.phase_name}"]
        )
        
        self.telemetry.emit_event(
            title="Intent Parsing Failed",
            text=f"Failed to parse user intent: {error_message}",
            tags=[
                "intent_error",
                f"error_code:{error_result['error']['code']}",
                f"user:{error_result['user_id']}",
                f"phase:{self.phase_name}"
            ],
            alert_type="error",
            priority="high"
        )
    
    def _update_statistics(self, result: Dict[str, Any], processing_time_ms: int, success: bool):
        """Update phase statistics"""
        if success:
            self.stats["successful_parses"] += 1
            
            # Update average confidence
            confidence = result["intent_analysis"]["parsing_confidence"]
            current_avg = self.stats["avg_confidence"]
            total_success = self.stats["successful_parses"]
            
            self.stats["avg_confidence"] = ((current_avg * (total_success - 1)) + confidence) / total_success
        else:
            self.stats["failed_parses"] += 1
        
        self.stats["total_processing_time_ms"] += processing_time_ms
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get phase statistics"""
        total = self.stats["total_requests"]
        successful = self.stats["successful_parses"]
        
        stats = self.stats.copy()
        
        if total > 0:
            stats["success_rate"] = successful / total
            stats["avg_processing_time_ms"] = self.stats["total_processing_time_ms"] / total
        else:
            stats["success_rate"] = 0.0
            stats["avg_processing_time_ms"] = 0.0
        
        stats["phase_name"] = self.phase_name
        stats["phase_version"] = self.phase_version
        stats["gemini_status"] = self.gemini.get_status()
        stats["telemetry_status"] = self.telemetry.get_status()
        
        return stats
    
    def reset_statistics(self):
        """Reset phase statistics"""
        self.stats = {
            "total_requests": 0,
            "successful_parses": 0,
            "failed_parses": 0,
            "total_processing_time_ms": 0,
            "avg_confidence": 0.0
        }
        logger.info("📊 Phase statistics reset")
    
    def get_status(self) -> Dict[str, Any]:
        """Get complete phase status"""
        return {
            "phase": self.phase_name,
            "version": self.phase_version,
            "initialized": True,
            "gemini_available": not self.gemini.mock_mode,
            "telemetry_available": self.telemetry.config.mode != TelemetryMode.DISABLED,
            "telemetry_status": {
                "mode": self.telemetry.config.mode.value if hasattr(self.telemetry.config.mode, 'value') else str(self.telemetry.config.mode),
                "available": self.telemetry.config.mode != TelemetryMode.DISABLED
            },
            "statistics": self.get_statistics()
        }