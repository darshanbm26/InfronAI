"""
Phase 2: Architecture Sommelier
Production-grade implementation with full telemetry
"""

import time
import logging
import json
import re
from datetime import datetime
from typing import Dict, Any, Optional, List
import uuid

from ..core.gemini_client import GeminiClient
from ..telemetry.datadog_client import TelemetryClient, TelemetryConfig, TelemetryMode

logger = logging.getLogger(__name__)

class ArchitectureSommelierPhase:
    """Complete Phase 2: Architecture Selection"""
    
    def __init__(self, telemetry_config: Optional[TelemetryConfig] = None):
        self.phase_name = "architecture_sommelier"
        self.phase_version = "1.0.0"
        
        # Initialize clients
        self.gemini = GeminiClient()
        self.telemetry = TelemetryClient(telemetry_config)
        
        # Architecture catalog
        self.architectures = ["serverless", "containers", "virtual_machines"]
        
        # Architecture selection rules (for fallback)
        self.architecture_rules = {
            "api_backend": {
                "serverless": 0.9,
                "containers": 0.7,
                "virtual_machines": 0.4
            },
            "web_app": {
                "serverless": 0.8,
                "containers": 0.9,
                "virtual_machines": 0.6
            },
            "data_processing": {
                "serverless": 0.6,
                "containers": 0.8,
                "virtual_machines": 0.9
            },
            "ml_inference": {
                "serverless": 0.5,
                "containers": 0.9,
                "virtual_machines": 0.8
            },
            "batch_processing": {
                "serverless": 0.7,
                "containers": 0.8,
                "virtual_machines": 0.9
            },
            "realtime_streaming": {
                "serverless": 0.3,
                "containers": 0.9,
                "virtual_machines": 0.7
            },
            "mobile_backend": {
                "serverless": 0.9,
                "containers": 0.8,
                "virtual_machines": 0.5
            },
            "gaming_server": {
                "serverless": 0.2,
                "containers": 0.7,
                "virtual_machines": 0.9
            }
        }
        
        # Statistics
        self.stats = {
            "total_requests": 0,
            "gemini_selections": 0,
            "rule_fallback_selections": 0,
            "total_processing_time_ms": 0,
            "avg_confidence": 0.0
        }
        
        logger.info(f"✅ Phase 2 initialized: {self.phase_name} v{self.phase_version}")
    
    async def process(self, phase1_result: Dict[str, Any], 
                user_id: Optional[str] = None,
                session_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Select optimal architecture based on parsed intent
        
        Args:
            phase1_result: Complete output from Phase 1
            user_id: User identifier
            session_id: Session identifier
            
        Returns:
            Dict containing architecture selection with full context
        """
        start_time = time.time()
        
        # Validate input
        if not phase1_result or "intent_analysis" not in phase1_result:
            raise ValueError("Invalid Phase 1 result. Missing intent_analysis")
        
        self.stats["total_requests"] += 1
        
        # Extract data from Phase 1
        intent_analysis = phase1_result["intent_analysis"]
        workload_type = intent_analysis["workload_type"]
        requirements = intent_analysis["requirements"]
        constraints = intent_analysis["constraints"]
        
        # Use IDs from Phase 1 or generate new
        request_id = phase1_result.get("request_id", f"req_{int(time.time())}_{uuid.uuid4().hex[:6]}")
        user_id = user_id or phase1_result.get("user_id", f"user_{uuid.uuid4().hex[:8]}")
        session_id = session_id or phase1_result.get("session_id", f"session_{uuid.uuid4().hex[:8]}")
        
        try:
            logger.info(f"🏗️  Architecture selection - Workload: {workload_type}, User: {user_id}")
            
            # Step 1: Select architecture (try Gemini first, then fallback)
            selection_method = "gemini_api"
            try:
                architecture_result = self._select_with_gemini(
                    intent_analysis, user_id, session_id
                )
                self.stats["gemini_selections"] += 1
            except Exception as e:
                logger.warning(f"Gemini architecture selection failed, using rule-based: {e}")
                architecture_result = self._select_with_rules(intent_analysis)
                selection_method = "rule_fallback"
                self.stats["rule_fallback_selections"] += 1
            
            # Step 2: Calculate processing time
            processing_time_ms = int((time.time() - start_time) * 1000)
            
            # Step 3: Enhance result with metadata
            enhanced_result = self._enhance_architecture_result(
                architecture_result, 
                phase1_result,
                processing_time_ms,
                selection_method,
                user_id,
                session_id,
                request_id
            )
            
            # Step 4: Update statistics
            self._update_statistics(architecture_result, processing_time_ms)
            
            # Step 5: Emit telemetry
            self._emit_success_telemetry(enhanced_result, processing_time_ms)
            
            logger.info(f"✅ Architecture selected: {architecture_result['primary_architecture']}")
            logger.info(f"   Confidence: {architecture_result['confidence']}")
            logger.info(f"   Method: {selection_method}")
            logger.info(f"   Time: {processing_time_ms}ms")
            
            return enhanced_result
            
        except Exception as e:
            # Handle failures gracefully
            processing_time_ms = int((time.time() - start_time) * 1000)
            
            error_result = self._create_error_result(
                user_id, session_id, request_id, phase1_result, str(e), processing_time_ms
            )
            
            self._emit_error_telemetry(error_result, str(e))
            
            logger.error(f"❌ Architecture selection failed: {e}")
            raise
    
    def _select_with_gemini(self, intent_analysis: Dict[str, Any], 
                           user_id: str, session_id: str) -> Dict[str, Any]:
        """Select architecture using Gemini API"""
        workload_type = intent_analysis["workload_type"]
        requirements = intent_analysis["requirements"]
        constraints = intent_analysis["constraints"]
        
        prompt = self._create_architecture_prompt(
            workload_type, requirements, constraints
        )
        
        try:
            # Call Gemini with retry logic
            response = self.gemini.call_with_retry(prompt)
            
            if not response:
                raise ValueError("Empty response from Gemini")
            
            # Extract text from response
            response_text = ""
            if hasattr(response, 'text'):
                response_text = response.text
            elif hasattr(response, 'candidates') and response.candidates:
                candidate = response.candidates[0]
                if hasattr(candidate, 'content') and hasattr(candidate.content, 'parts'):
                    parts = candidate.content.parts
                    if parts:
                        response_text = parts[0].text
            
            if not response_text:
                raise ValueError("Could not extract text from Gemini response")
            
            # Extract JSON from response
            json_pattern = r'(\{.*\})'
            match = re.search(json_pattern, response_text, re.DOTALL)
            
            if not match:
                raise ValueError("Could not extract JSON from response")
            
            json_text = match.group(1)
            result = json.loads(json_text)
            
            # Validate result
            self._validate_architecture_result(result)
            
            # Add metadata
            result["selection_method"] = "gemini_api"
            result["llm_model"] = self.gemini.model_name
            result["active_key"] = self.gemini._get_current_key_name()
            
            return result
            
        except Exception as e:
            logger.error(f"Gemini architecture selection error: {e}")
            raise
    
    def _create_architecture_prompt(self, workload_type: str, 
                                   requirements: Dict[str, Any], 
                                   constraints: Dict[str, Any]) -> str:
        """Create prompt for Gemini architecture selection"""
        return f"""You are an expert cloud architect at Google. Select the optimal cloud architecture.

WORKLOAD TYPE: {workload_type}

REQUIREMENTS:
- Latency: {requirements.get('latency', 'medium')}
- Availability: {requirements.get('availability', 'high')}
- Geography: {requirements.get('geography', 'global')}
- Compliance: {requirements.get('compliance', [])}

CONSTRAINTS:
- Budget Sensitivity: {constraints.get('budget_sensitivity', 'medium')}
- Team Experience: {constraints.get('team_experience', 'intermediate')}
- Time to Market: {constraints.get('time_to_market', '1_week')}

Available Architectures:
1. SERVERLESS (Cloud Run, Cloud Functions): Best for variable traffic, low ops overhead
2. CONTAINERS (GKE, Cloud Run for Anthos): Best for control, Kubernetes expertise needed
3. VIRTUAL_MACHINES (GCE, VM instances): Best for legacy apps, specific OS requirements

Return ONLY a valid JSON object with these exact fields:
- primary_architecture (must be: serverless, containers, or virtual_machines)
- confidence (number between 0.0 and 1.0 with 2 decimal places)
- reasoning (string explaining your choice)
- alternatives (array of objects, each with: architecture, when_to_consider)

Example:
{{
    "primary_architecture": "serverless",
    "confidence": 0.91,
    "reasoning": "Serverless provides optimal cost-performance for API workload with variable traffic and matches intermediate team experience.",
    "alternatives": [
        {{
            "architecture": "containers",
            "when_to_consider": "If Kubernetes expertise exists or need more control over runtime"
        }},
        {{
            "architecture": "virtual_machines",
            "when_to_consider": "For specific OS requirements or legacy applications"
        }}
    ]
}}

CRITICAL INSTRUCTIONS:
1. Return ONLY the JSON object, no markdown, no code blocks
2. Confidence should reflect certainty based on available information
3. Include at least 2 alternatives
4. Reasoning should be specific to this workload

JSON OUTPUT:"""
    
    def _validate_architecture_result(self, result: Dict[str, Any]) -> None:
        """Validate architecture selection result"""
        required_fields = [
            "primary_architecture", "confidence", "reasoning", "alternatives"
        ]
        
        for field in required_fields:
            if field not in result:
                raise ValueError(f"Missing required field: {field}")
        
        if result["primary_architecture"] not in self.architectures:
            raise ValueError(f"Invalid architecture: {result['primary_architecture']}")
        
        confidence = result["confidence"]
        if not isinstance(confidence, (int, float)) or not 0.0 <= confidence <= 1.0:
            raise ValueError(f"Invalid confidence: {confidence}")
    
    def _select_with_rules(self, intent_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Rule-based architecture selection (fallback)"""
        workload_type = intent_analysis["workload_type"]
        requirements = intent_analysis["requirements"]
        constraints = intent_analysis["constraints"]
        
        # Get scores for this workload type
        workload_scores = self.architecture_rules.get(workload_type, {
            "serverless": 0.7,
            "containers": 0.8,
            "virtual_machines": 0.6
        })
        
        # Adjust scores based on requirements and constraints
        adjusted_scores = workload_scores.copy()
        
        # Budget sensitivity adjustments
        if constraints.get("budget_sensitivity") == "high":
            adjusted_scores["serverless"] *= 1.2  # Serverless is cost-effective
            adjusted_scores["virtual_machines"] *= 0.8
        
        # Team experience adjustments
        team_exp = constraints.get("team_experience", "intermediate")
        if team_exp in ["beginner", "junior"]:
            adjusted_scores["serverless"] *= 1.3  # Serverless is easier
            adjusted_scores["containers"] *= 0.7
        elif team_exp in ["expert"]:
            adjusted_scores["containers"] *= 1.2  # Experts can handle Kubernetes
        
        # Latency requirements
        if requirements.get("latency") in ["ultra_low", "low"]:
            adjusted_scores["virtual_machines"] *= 1.1  # VMs can have predictable latency
            adjusted_scores["serverless"] *= 0.9
        
        # Time to market
        if constraints.get("time_to_market") == "immediate":
            adjusted_scores["serverless"] *= 1.3  # Faster deployment
        
        # Select highest score
        primary_architecture = max(adjusted_scores, key=adjusted_scores.get)
        confidence = adjusted_scores[primary_architecture]
        
        # Ensure confidence is within bounds
        confidence = min(max(confidence, 0.3), 0.95)
        
        # Generate alternatives
        alternatives = []
        for arch in self.architectures:
            if arch != primary_architecture:
                when_text = self._get_alternative_reasoning(arch, workload_type)
                alternatives.append({
                    "architecture": arch,
                    "when_to_consider": when_text
                })
        
        return {
            "primary_architecture": primary_architecture,
            "confidence": round(confidence, 2),
            "reasoning": f"Rule-based selection: {primary_architecture} scored highest for {workload_type} workload considering budget sensitivity ({constraints.get('budget_sensitivity')}), team experience ({team_exp}), and latency requirements ({requirements.get('latency')}).",
            "alternatives": alternatives,
            "selection_method": "rule_based",
            "llm_model": "rule_engine_v1"
        }
    
    def _get_alternative_reasoning(self, architecture: str, workload_type: str) -> str:
        """Get reasoning for alternative architectures"""
        reasonings = {
            "serverless": {
                "api_backend": "When you have variable traffic and want minimal operations overhead",
                "web_app": "For web apps with unpredictable traffic patterns",
                "data_processing": "For event-driven or sporadic data processing",
                "ml_inference": "For low-volume or batch inference workloads",
                "default": "When you need automatic scaling and minimal operations"
            },
            "containers": {
                "api_backend": "When you need fine-grained control and Kubernetes expertise is available",
                "web_app": "For complex web apps requiring custom runtime environments",
                "data_processing": "For data pipelines requiring specific dependencies",
                "ml_inference": "For ML workloads requiring GPU access and custom environments",
                "default": "When you need portability and Kubernetes ecosystem benefits"
            },
            "virtual_machines": {
                "api_backend": "For legacy applications or specific OS requirements",
                "web_app": "When migrating existing on-premise applications",
                "data_processing": "For data processing requiring specific kernel versions",
                "ml_inference": "For ML workloads with custom hardware requirements",
                "default": "When you need full control over the operating system"
            }
        }
        
        arch_reasons = reasonings.get(architecture, {})
        return arch_reasons.get(workload_type, arch_reasons.get("default", "Consider based on specific requirements"))
    
    def _enhance_architecture_result(self, architecture_result: Dict[str, Any],
                                   phase1_result: Dict[str, Any],
                                   processing_time_ms: int,
                                   selection_method: str,
                                   user_id: str,
                                   session_id: str,
                                   request_id: str) -> Dict[str, Any]:
        """Enhance architecture result with metadata"""
        
        intent_analysis = phase1_result["intent_analysis"]
        business_context = phase1_result.get("business_context", {})
        
        enhanced = {
            "request_id": request_id,
            "user_id": user_id,
            "session_id": session_id,
            "phase": self.phase_name,
            "phase_version": self.phase_version,
            "timestamp": datetime.utcnow().isoformat(),
            "status": "completed",
            
            "phase1_input": {
                "workload_type": intent_analysis["workload_type"],
                "scale_tier": business_context.get("scale_tier", "unknown"),
                "complexity_score": business_context.get("complexity_score", 0.0),
                "risk_level": business_context.get("risk_level", "medium")
            },
            
            "architecture_analysis": architecture_result,
            
            "processing_metadata": {
                "processing_time_ms": processing_time_ms,
                "selection_method": selection_method,
                "gemini_mode": "api" if not self.gemini.mock_mode else "mock",
                "llm_model": architecture_result.get("llm_model", "unknown"),
                "active_key": architecture_result.get("active_key", "unknown")
            },
            
            "business_impact": {
                "estimated_cost_savings_percent": self._estimate_cost_savings(
                    architecture_result["primary_architecture"],
                    intent_analysis["workload_type"]
                ),
                "operational_complexity": self._assess_operational_complexity(
                    architecture_result["primary_architecture"],
                    intent_analysis["constraints"]["team_experience"]
                ),
                "time_to_deploy_days": self._estimate_deployment_time(
                    architecture_result["primary_architecture"],
                    intent_analysis["constraints"]["team_experience"]
                )
            },
            
            "next_phase": "machine_specification",
            "phase_transition": {
                "recommended": True,
                "estimated_time_seconds": 15,
                "prerequisites_met": True,
                "required_input": {
                    "architecture": architecture_result["primary_architecture"],
                    "workload_type": intent_analysis["workload_type"],
                    "scale": intent_analysis["scale"]
                }
            }
        }
        
        return enhanced
    
    def _estimate_cost_savings(self, architecture: str, workload_type: str) -> float:
        """Estimate cost savings percentage vs alternatives"""
        savings_map = {
            "serverless": {
                "api_backend": 0.25,
                "web_app": 0.20,
                "data_processing": 0.15,
                "ml_inference": 0.10,
                "default": 0.20
            },
            "containers": {
                "api_backend": 0.15,
                "web_app": 0.10,
                "data_processing": 0.20,
                "ml_inference": 0.25,
                "default": 0.15
            },
            "virtual_machines": {
                "api_backend": 0.0,
                "web_app": 0.0,
                "data_processing": 0.0,
                "ml_inference": 0.0,
                "default": 0.0
            }
        }
        
        arch_savings = savings_map.get(architecture, {})
        return arch_savings.get(workload_type, arch_savings.get("default", 0.0))
    
    def _assess_operational_complexity(self, architecture: str, team_experience: str) -> str:
        """Assess operational complexity"""
        complexity_scores = {
            "serverless": 1.0,
            "containers": 3.0,
            "virtual_machines": 2.0
        }
        
        experience_modifier = {
            "beginner": 2.0,
            "junior": 1.5,
            "intermediate": 1.0,
            "senior": 0.7,
            "expert": 0.5
        }
        
        base_complexity = complexity_scores.get(architecture, 2.0)
        modifier = experience_modifier.get(team_experience, 1.0)
        
        adjusted_complexity = base_complexity * modifier
        
        if adjusted_complexity < 1.5:
            return "low"
        elif adjusted_complexity < 2.5:
            return "medium"
        else:
            return "high"
    
    def _estimate_deployment_time(self, architecture: str, team_experience: str) -> int:
        """Estimate deployment time in days"""
        base_times = {
            "serverless": 1,
            "containers": 3,
            "virtual_machines": 2
        }
        
        experience_modifier = {
            "beginner": 2.0,
            "junior": 1.5,
            "intermediate": 1.0,
            "senior": 0.8,
            "expert": 0.6
        }
        
        base_days = base_times.get(architecture, 2)
        modifier = experience_modifier.get(team_experience, 1.0)
        
        return int(base_days * modifier)
    
    def _emit_success_telemetry(self, result: Dict[str, Any], processing_time_ms: int):
        """Emit success telemetry"""
        architecture_analysis = result["architecture_analysis"]
        phase1_input = result["phase1_input"]
        
        # Emit confidence metric
        self.telemetry.submit_metric(
            name="ai.architecture.selection.confidence",
            value=architecture_analysis["confidence"],
            tags=[
                f"architecture:{architecture_analysis['primary_architecture']}",
                f"workload_type:{phase1_input['workload_type']}",
                f"phase:{self.phase_name}",
                f"selection_method:{architecture_analysis.get('selection_method', 'unknown')}",
                f"scale_tier:{phase1_input['scale_tier']}",
                f"risk_level:{phase1_input['risk_level']}"
            ]
        )
        
        # Emit processing time metric
        self.telemetry.submit_metric(
            name="ai.architecture.processing.time_ms",
            value=processing_time_ms,
            tags=[
                f"architecture:{architecture_analysis['primary_architecture']}",
                f"workload_type:{phase1_input['workload_type']}",
                f"phase:{self.phase_name}",
                f"success:true"
            ]
        )
        
        # Emit architecture distribution metric
        self.telemetry.submit_metric(
            name="business.architecture.distribution",
            value=1.0,
            tags=[
                f"architecture:{architecture_analysis['primary_architecture']}",
                f"workload_type:{phase1_input['workload_type']}",
                f"scale_tier:{phase1_input['scale_tier']}"
            ]
        )
        
        # Emit success log
        self.telemetry.submit_log(
            source="cloud-sentinel",
            message={
                "event": "architecture_selected",
                "request_id": result["request_id"],
                "user_id": result["user_id"],
                "session_id": result["session_id"],
                "workload_type": phase1_input["workload_type"],
                "selected_architecture": architecture_analysis["primary_architecture"],
                "confidence": architecture_analysis["confidence"],
                "selection_method": architecture_analysis.get("selection_method", "unknown"),
                "processing_time_ms": processing_time_ms,
                "estimated_cost_savings_percent": result["business_impact"]["estimated_cost_savings_percent"],
                "operational_complexity": result["business_impact"]["operational_complexity"]
            },
            tags=[
                "architecture_selection", 
                "success", 
                architecture_analysis["primary_architecture"],
                f"phase:{self.phase_name}"
            ]
        )
        
        # Emit success event
        self.telemetry.emit_event(
            title="Architecture Selected",
            text=f"Selected {architecture_analysis['primary_architecture']} for {phase1_input['workload_type']} with {architecture_analysis['confidence']*100:.1f}% confidence",
            tags=[
                "architecture_selected",
                architecture_analysis["primary_architecture"],
                f"confidence:{architecture_analysis['confidence']:.2f}",
                f"workload:{phase1_input['workload_type']}",
                f"user:{result['user_id']}",
                f"phase:{self.phase_name}"
            ],
            alert_type="success"
        )
    
    def _create_error_result(self, user_id: str, session_id: str, request_id: str,
                           phase1_result: Dict[str, Any], error_message: str, 
                           processing_time_ms: int) -> Dict[str, Any]:
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
                "code": "ARCHITECTURE_SELECTION_FAILED",
                "phase1_summary": {
                    "workload_type": phase1_result.get("intent_analysis", {}).get("workload_type", "unknown"),
                    "scale_tier": phase1_result.get("business_context", {}).get("scale_tier", "unknown")
                }
            },
            "processing_metadata": {
                "processing_time_ms": processing_time_ms,
                "selection_method": "failed",
                "attempted_retry": False
            },
            "fallback_suggestion": {
                "suggested_architecture": "serverless",
                "estimated_confidence": 0.5,
                "recommendation": "System temporarily unavailable. Using default serverless architecture recommendation."
            }
        }
    
    def _emit_error_telemetry(self, error_result: Dict[str, Any], error_message: str):
        """Emit error telemetry"""
        self.telemetry.submit_metric(
            name="ai.architecture.processing.time_ms",
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
                "event": "architecture_selection_failed",
                "request_id": error_result["request_id"],
                "user_id": error_result["user_id"],
                "error": error_result["error"],
                "processing_time_ms": error_result["processing_metadata"]["processing_time_ms"]
            },
            tags=[
                "architecture_selection", 
                "error", 
                error_result["error"]["code"],
                f"phase:{self.phase_name}"
            ]
        )
        
        self.telemetry.emit_event(
            title="Architecture Selection Failed",
            text=f"Failed to select architecture: {error_message}",
            tags=[
                "architecture_error",
                f"error_code:{error_result['error']['code']}",
                f"user:{error_result['user_id']}",
                f"phase:{self.phase_name}"
            ],
            alert_type="error",
            priority="high"
        )
    
    def _update_statistics(self, result: Dict[str, Any], processing_time_ms: int):
        """Update phase statistics"""
        if "confidence" in result:
            confidence = result["confidence"]
            
            # Update average confidence
            current_avg = self.stats["avg_confidence"]
            total_success = self.stats["gemini_selections"] + self.stats["rule_fallback_selections"]
            
            if total_success > 0:
                self.stats["avg_confidence"] = ((current_avg * (total_success - 1)) + confidence) / total_success
            else:
                self.stats["avg_confidence"] = confidence
        
        self.stats["total_processing_time_ms"] += processing_time_ms
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get phase statistics"""
        total = self.stats["total_requests"]
        successful = self.stats["gemini_selections"] + self.stats["rule_fallback_selections"]
        
        stats = self.stats.copy()
        
        if total > 0:
            stats["success_rate"] = successful / total if total > 0 else 0.0
            stats["avg_processing_time_ms"] = self.stats["total_processing_time_ms"] / total
            stats["gemini_success_rate"] = self.stats["gemini_selections"] / total
        else:
            stats["success_rate"] = 0.0
            stats["avg_processing_time_ms"] = 0.0
            stats["gemini_success_rate"] = 0.0
        
        stats["phase_name"] = self.phase_name
        stats["phase_version"] = self.phase_version
        stats["gemini_status"] = self.gemini.get_status()
        stats["telemetry_status"] = self.telemetry.get_status()
        
        return stats
    
    def reset_statistics(self):
        """Reset phase statistics"""
        self.stats = {
            "total_requests": 0,
            "gemini_selections": 0,
            "rule_fallback_selections": 0,
            "total_processing_time_ms": 0,
            "avg_confidence": 0.0
        }
        logger.info("📊 Phase 2 statistics reset")
    
    def get_status(self) -> Dict[str, Any]:
        """Get complete phase status"""
        return {
            "phase": self.phase_name,
            "version": self.phase_version,
            "initialized": True,
            "gemini_available": not self.gemini.mock_mode,
            "telemetry_available": self.telemetry.config.mode != TelemetryMode.DISABLED,
            "architecture_catalog": self.architectures,
            "statistics": self.get_statistics()
        }
