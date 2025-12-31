"""
Phase 7: User Decision & Telemetry
Production-grade implementation for capturing user decisions and telemetry
"""

import time
import logging
import json
from datetime import datetime
from typing import Dict, Any, Optional, List
import uuid
import random
import hashlib

from ..core.gemini_client import GeminiClient
from ..telemetry.datadog_client import TelemetryClient, TelemetryConfig, TelemetryMode

logger = logging.getLogger(__name__)

class UserDecisionPhase:
    """Complete Phase 7: User Decision & Telemetry"""
    
    def __init__(self, telemetry_config: Optional[TelemetryConfig] = None):
        self.phase_name = "user_decision"
        self.phase_version = "1.0.0"
        
        # Initialize clients
        self.gemini = GeminiClient()
        self.telemetry = TelemetryClient(telemetry_config)
        
        # Decision type definitions
        self.decision_types = {
            "accepted": {
                "description": "User accepted the AI recommendation without changes",
                "weight": 0.6,  # 60% expected acceptance rate
                "telemetry_impact": "positive",
                "learning_signal": "reinforcement"
            },
            "customized": {
                "description": "User accepted but made modifications",
                "weight": 0.3,  # 30% expected customization rate
                "telemetry_impact": "neutral",
                "learning_signal": "partial_reinforcement"
            },
            "rejected": {
                "description": "User rejected the AI recommendation",
                "weight": 0.1,  # 10% expected rejection rate
                "telemetry_impact": "negative",
                "learning_signal": "correction"
            }
        }
        
        # Customization categories
        self.customization_categories = {
            "cost_optimization": {
                "description": "User modified for cost savings",
                "common_changes": ["reduced_cpu", "reduced_ram", "changed_storage_tier", "changed_region"],
                "learning_focus": "pricing_accuracy"
            },
            "performance_enhancement": {
                "description": "User modified for better performance",
                "common_changes": ["increased_cpu", "increased_ram", "added_gpu", "changed_architecture"],
                "learning_focus": "performance_prediction"
            },
            "operational_preference": {
                "description": "User modified based on operational preferences",
                "common_changes": ["changed_architecture", "modified_scaling", "added_monitoring", "changed_deployment"],
                "learning_focus": "operational_complexity"
            },
            "compliance_requirement": {
                "description": "User modified for compliance reasons",
                "common_changes": ["changed_region", "added_security", "modified_storage", "changed_services"],
                "learning_focus": "compliance_mapping"
            }
        }
        
        # Statistics
        self.stats = {
            "total_decisions": 0,
            "accepted_decisions": 0,
            "customized_decisions": 0,
            "rejected_decisions": 0,
            "total_decision_time_ms": 0,
            "avg_decision_time_ms": 0,
            "user_feedback_count": 0
        }
        
        logger.info(f"✅ Phase 7 initialized: {self.phase_name} v{self.phase_version}")
        logger.info(f"🤔 Decision types: {len(self.decision_types)} with expected distribution")
    
    async def process(self, phase1_result: Dict[str, Any], 
                     phase2_result: Dict[str, Any],
                     phase3_result: Dict[str, Any],
                     phase4_result: Dict[str, Any],
                     phase5_result: Dict[str, Any],
                     phase6_result: Dict[str, Any],
                     decision_type: str,
                     customization_details: Optional[Dict[str, Any]] = None,
                     user_feedback: Optional[str] = None,
                     decision_time_seconds: Optional[int] = None,
                     user_id: Optional[str] = None,
                     session_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Process user decision and emit comprehensive telemetry
        
        Args:
            phase1_result: Complete output from Phase 1
            phase2_result: Complete output from Phase 2
            phase3_result: Complete output from Phase 3
            phase4_result: Complete output from Phase 4
            phase5_result: Complete output from Phase 5
            phase6_result: Complete output from Phase 6
            decision_type: accept/customize/reject
            customization_details: Details of customizations if any
            user_feedback: Optional user comments
            decision_time_seconds: Time taken to make decision
            user_id: User identifier
            session_id: Session identifier
            
        Returns:
            Dict containing decision processing results and telemetry
        """
        start_time = time.time()
        
        # Validate inputs
        self._validate_inputs(
            phase1_result, phase2_result, phase3_result, 
            phase4_result, phase5_result, phase6_result,
            decision_type=decision_type
        )
        
        self.stats["total_decisions"] += 1
        
        # Extract data from all phases
        consolidated_data = self._consolidate_phase_data(
            phase1_result, phase2_result, phase3_result,
            phase4_result, phase5_result, phase6_result
        )
        
        # Use IDs from previous phases
        request_id = phase1_result.get("request_id", f"req_{int(time.time())}_{uuid.uuid4().hex[:6]}")
        user_id = user_id or phase1_result.get("user_id", f"user_{uuid.uuid4().hex[:8]}")
        session_id = session_id or phase1_result.get("session_id", f"session_{uuid.uuid4().hex[:8]}")
        
        # Calculate decision time if not provided
        if decision_time_seconds is None:
            # Estimate based on presentation complexity
            decision_time_seconds = self._estimate_decision_time(
                consolidated_data, decision_type, customization_details
            )
        
        try:
            logger.info(f"🤔 Processing user decision: {decision_type} for {consolidated_data['workload']['type']}")
            
            # Step 1: Validate decision type
            if decision_type not in self.decision_types:
                raise ValueError(f"Invalid decision type: {decision_type}. Must be one of {list(self.decision_types.keys())}")
            
            # Step 2: Process based on decision type
            decision_method = "user_provided"
            decision_processing = None
            
            if decision_type == "accepted":
                decision_processing = await self._process_accepted_decision(
                    consolidated_data, decision_time_seconds
                )
                self.stats["accepted_decisions"] += 1
                
            elif decision_type == "customized":
                if not customization_details:
                    raise ValueError("Customization details required for 'customized' decision type")
                
                decision_processing = await self._process_customized_decision(
                    consolidated_data, customization_details, decision_time_seconds
                )
                self.stats["customized_decisions"] += 1
                
            elif decision_type == "rejected":
                decision_processing = await self._process_rejected_decision(
                    consolidated_data, user_feedback, decision_time_seconds
                )
                self.stats["rejected_decisions"] += 1
            
            # Step 3: Generate decision artifacts
            artifacts = await self._generate_decision_artifacts(
                decision_type, consolidated_data, decision_processing, customization_details
            )
            
            # Step 4: Calculate processing time
            processing_time_ms = int((time.time() - start_time) * 1000)
            
            # Step 5: Generate learning signals
            learning_signals = self._generate_learning_signals(
                decision_type, consolidated_data, decision_processing, user_feedback
            )
            
            # Step 6: Enhance with metadata
            enhanced_result = self._enhance_decision_result(
                decision_processing,
                artifacts,
                learning_signals,
                consolidated_data,
                decision_type,
                decision_time_seconds,
                user_feedback,
                customization_details,
                processing_time_ms,
                decision_method,
                user_id,
                session_id,
                request_id
            )
            
            # Step 7: Update statistics
            self._update_statistics(decision_type, decision_time_seconds, user_feedback)
            
            # Step 8: Emit comprehensive telemetry
            self._emit_decision_telemetry(enhanced_result, processing_time_ms)
            
            logger.info(f"✅ Decision processed: {decision_type}")
            logger.info(f"   Decision time: {decision_time_seconds}s")
            logger.info(f"   Learning signals: {len(learning_signals)}")
            logger.info(f"   Time: {processing_time_ms}ms")
            
            return enhanced_result
            
        except Exception as e:
            # Handle failures gracefully
            processing_time_ms = int((time.time() - start_time) * 1000)
            
            error_result = self._create_error_result(
                user_id, session_id, request_id, 
                consolidated_data, decision_type, str(e), processing_time_ms
            )
            
            self._emit_error_telemetry(error_result, str(e))
            
            logger.error(f"❌ Decision processing failed: {e}")
            raise
    
    def _validate_inputs(self, *phase_results, decision_type: str):
        """Validate all input phases and decision type"""
        # Validate phases
        required_phases = [
            ("Phase 1", phase_results[0], "intent_analysis"),
            ("Phase 2", phase_results[1], "architecture_analysis"),
            ("Phase 3", phase_results[2], "specification_analysis"),
            ("Phase 4", phase_results[3], "primary_price"),
            ("Phase 5", phase_results[4], "qualitative_analysis"),
            ("Phase 6", phase_results[5], "presentation_id")
        ]
        
        for phase_name, phase_data, required_field in required_phases:
            if not phase_data or required_field not in phase_data:
                raise ValueError(f"Invalid {phase_name} result. Missing {required_field}")
        
        # Validate decision type
        if decision_type not in self.decision_types:
            raise ValueError(f"Invalid decision type: {decision_type}. Must be one of {list(self.decision_types.keys())}")
    
    def _consolidate_phase_data(self, *phase_results) -> Dict[str, Any]:
        """Consolidate data from all phases"""
        phase1, phase2, phase3, phase4, phase5, phase6 = phase_results
        
        return {
            "workload": {
                "type": phase1["intent_analysis"]["workload_type"],
                "scale": phase1["intent_analysis"]["scale"],
                "requirements": phase1["intent_analysis"]["requirements"],
                "constraints": phase1["intent_analysis"]["constraints"],
                "business_context": phase1.get("business_context", {})
            },
            "architecture": {
                "primary": phase2["architecture_analysis"]["primary_architecture"],
                "confidence": phase2["architecture_analysis"]["confidence"],
                "reasoning": phase2["architecture_analysis"]["reasoning"],
                "alternatives": phase2["architecture_analysis"].get("alternatives", [])
            },
            "specification": {
                "machine_type": phase3["specification_analysis"].get("exact_type", "unknown"),
                "machine_family": phase3["specification_analysis"]["machine_family"],
                "machine_size": phase3["specification_analysis"]["machine_size"],
                "cpu": phase3["specification_analysis"].get("cpu", 4),
                "ram": phase3["specification_analysis"].get("ram", 8),
                "configuration": phase3["configuration"]
            },
            "pricing": {
                "primary_price": phase4["primary_price"]["total_monthly_usd"],
                "price_accuracy": phase4["pricing_accuracy"]["estimated_accuracy"],
                "alternative_prices": phase4["alternative_prices"],
                "savings_analysis": phase4["savings_analysis"]
            },
            "analysis": {
                "executive_summary": phase5["qualitative_analysis"]["executive_summary"],
                "recommendation_strength": phase5["qualitative_analysis"]["recommendation_strength"],
                "advantages": phase5["qualitative_analysis"]["primary_advantages"],
                "risks": phase5["qualitative_analysis"]["primary_risks"],
                "risk_assessment": phase5["qualitative_analysis"]["risk_assessment"]
            },
            "presentation": {
                "id": phase6["presentation_id"],
                "type": phase6["presentation_metadata"]["type"],
                "audience": phase6["presentation_metadata"]["audience"],
                "title": phase6["presentation_data"].get("title", "Infrastructure Recommendation")
            },
            "metadata": {
                "user_id": phase1.get("user_id", "unknown"),
                "session_id": phase1.get("session_id", "unknown"),
                "request_id": phase1.get("request_id", "unknown"),
                "all_phase_ids": {
                    "phase1": phase1.get("request_id", "unknown"),
                    "phase2": phase2.get("request_id", phase1.get("request_id", "unknown")),
                    "phase3": phase3.get("request_id", phase1.get("request_id", "unknown")),
                    "phase4": phase4.get("request_id", phase1.get("request_id", "unknown")),
                    "phase5": phase5.get("request_id", phase1.get("request_id", "unknown")),
                    "phase6": phase6.get("request_id", phase1.get("request_id", "unknown"))
                }
            }
        }
    
    def _estimate_decision_time(self, consolidated_data: Dict[str, Any],
                              decision_type: str,
                              customization_details: Optional[Dict[str, Any]]) -> int:
        """Estimate decision time based on complexity"""
        base_times = {
            "accepted": 30,  # 30 seconds for simple acceptance
            "customized": 120,  # 2 minutes for customization review
            "rejected": 60  # 1 minute for rejection
        }
        
        base_time = base_times.get(decision_type, 60)
        
        # Adjust for presentation complexity
        presentation_type = consolidated_data["presentation"]["type"]
        if presentation_type == "technical":
            base_time *= 1.5  # Technical presentations take longer
        elif presentation_type == "executive":
            base_time *= 0.8  # Executive summaries are quicker
        
        # Adjust for workload complexity
        complexity = consolidated_data["workload"]["business_context"].get("complexity_score", 0.5)
        base_time *= (1 + complexity)  # More complex = more time
        
        # Adjust for customization complexity
        if decision_type == "customized" and customization_details:
            changes_count = len(customization_details.get("changes", []))
            base_time += changes_count * 15  # 15 seconds per change
        
        return int(base_time)
    
    async def _process_accepted_decision(self, consolidated_data: Dict[str, Any],
                                       decision_time_seconds: int) -> Dict[str, Any]:
        """Process accepted decision"""
        logger.info("✅ Processing accepted decision")
        
        # Calculate acceptance metrics
        recommendation_strength = consolidated_data["analysis"]["recommendation_strength"]
        architecture_confidence = consolidated_data["architecture"]["confidence"]
        price_accuracy = consolidated_data["pricing"]["price_accuracy"]
        
        # Calculate overall confidence
        overall_confidence = (recommendation_strength/100 * 0.4 + 
                            architecture_confidence * 0.4 + 
                            price_accuracy * 0.2)
        
        # Calculate potential savings realized
        potential_savings = consolidated_data["pricing"]["savings_analysis"].get("potential_monthly_savings", 0)
        
        return {
            "decision_analysis": {
                "type": "accepted",
                "overall_confidence": round(overall_confidence, 3),
                "acceptance_factors": {
                    "recommendation_strength": recommendation_strength,
                    "architecture_confidence": architecture_confidence,
                    "price_accuracy": price_accuracy,
                    "risk_alignment": consolidated_data["analysis"]["risk_assessment"]["overall_risk"]
                },
                "savings_realized": potential_savings,
                "user_satisfaction_prediction": min(0.95, overall_confidence + 0.1)
            },
            "deployment_readiness": {
                "status": "ready",
                "estimated_deployment_time": "1-2 weeks",
                "complexity": "medium",
                "success_probability": 0.85
            },
            "business_impact": {
                "immediate_impact": "Positive - proceeding with AI recommendation",
                "long_term_value": "Standardized, optimized infrastructure",
                "risk_level": "Low",
                "recommendation": "Proceed with deployment as planned"
            }
        }
    
    async def _process_customized_decision(self, consolidated_data: Dict[str, Any],
                                         customization_details: Dict[str, Any],
                                         decision_time_seconds: int) -> Dict[str, Any]:
        """Process customized decision"""
        logger.info("🔄 Processing customized decision")
        
        # Analyze customization details
        customization_analysis = self._analyze_customizations(
            customization_details, consolidated_data
        )
        
        # Calculate impact
        impact_analysis = self._calculate_customization_impact(
            customization_analysis, consolidated_data
        )
        
        # Determine customization category
        category = self._categorize_customization(customization_analysis)
        
        # Calculate learning value
        learning_value = self._assess_learning_value(customization_analysis, category)
        
        return {
            "decision_analysis": {
                "type": "customized",
                "customization_category": category,
                "customization_analysis": customization_analysis,
                "impact_analysis": impact_analysis,
                "learning_value": learning_value,
                "user_motivation": customization_details.get("reasoning", "Not specified")
            },
            "deployment_readiness": {
                "status": "requires_review",
                "estimated_deployment_time": "2-3 weeks",
                "complexity": "high",
                "success_probability": 0.75,
                "review_required": True
            },
            "business_impact": {
                "immediate_impact": "Modified - user customized AI recommendation",
                "long_term_value": "User-preference aligned infrastructure",
                "risk_level": "Medium",
                "recommendation": "Review customizations before deployment"
            }
        }
    
    def _analyze_customizations(self, customization_details: Dict[str, Any],
                               consolidated_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze user customizations"""
        changes = customization_details.get("changes", [])
        reasoning = customization_details.get("reasoning", "")
        
        analysis = {
            "changes_count": len(changes),
            "changes_by_type": {},
            "impact_level": "low",
            "departure_from_ai": 0.0,
            "key_modifications": []
        }
        
        # Categorize changes
        for change in changes:
            change_type = change.get("type", "unknown")
            analysis["changes_by_type"][change_type] = analysis["changes_by_type"].get(change_type, 0) + 1
            
            if change_type in ["architecture", "machine_type", "region"]:
                analysis["impact_level"] = "high"
                analysis["departure_from_ai"] += 0.3
            elif change_type in ["cpu", "ram", "storage"]:
                analysis["impact_level"] = "medium"
                analysis["departure_from_ai"] += 0.2
            else:
                analysis["departure_from_ai"] += 0.1
            
            analysis["key_modifications"].append({
                "type": change_type,
                "from": change.get("from", "unknown"),
                "to": change.get("to", "unknown"),
                "reason": change.get("reason", "Not specified")
            })
        
        # Cap departure score
        analysis["departure_from_ai"] = min(analysis["departure_from_ai"], 1.0)
        
        # Analyze reasoning
        reasoning_analysis = self._analyze_customization_reasoning(reasoning)
        analysis.update(reasoning_analysis)
        
        return analysis
    
    def _analyze_customization_reasoning(self, reasoning: str) -> Dict[str, Any]:
        """Analyze customization reasoning text"""
        if not reasoning:
            return {"reasoning_analysis": "No reasoning provided"}
        
        reasoning_lower = reasoning.lower()
        
        analysis = {
            "reasoning_present": True,
            "word_count": len(reasoning.split()),
            "key_themes": [],
            "sentiment": "neutral"
        }
        
        # Detect common themes
        themes = {
            "cost": ["cheaper", "cost", "budget", "expensive", "save money"],
            "performance": ["faster", "performance", "latency", "speed", "throughput"],
            "experience": ["experience", "familiar", "comfortable", "used to"],
            "compliance": ["compliance", "regulation", "security", "policy"],
            "future": ["future", "scale", "growth", "expand"]
        }
        
        for theme, keywords in themes.items():
            if any(keyword in reasoning_lower for keyword in keywords):
                analysis["key_themes"].append(theme)
        
        # Detect sentiment
        positive_words = ["better", "improved", "optimized", "enhanced", "prefer"]
        negative_words = ["worse", "insufficient", "inadequate", "don't like", "not good"]
        
        positive_count = sum(1 for word in positive_words if word in reasoning_lower)
        negative_count = sum(1 for word in negative_words if word in reasoning_lower)
        
        if positive_count > negative_count:
            analysis["sentiment"] = "positive"
        elif negative_count > positive_count:
            analysis["sentiment"] = "negative"
        
        return analysis
    
    def _calculate_customization_impact(self, customization_analysis: Dict[str, Any],
                                       consolidated_data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate impact of customizations"""
        impact = {
            "cost_impact": 0,
            "performance_impact": "neutral",
            "risk_impact": "neutral",
            "operational_impact": "neutral"
        }
        
        # Estimate cost impact (simplified)
        changes_count = customization_analysis["changes_count"]
        departure_score = customization_analysis["departure_from_ai"]
        
        base_price = consolidated_data["pricing"]["primary_price"]
        
        # Very rough estimation
        if "cost" in customization_analysis.get("key_themes", []):
            impact["cost_impact"] = -base_price * 0.1  # 10% savings
        elif "performance" in customization_analysis.get("key_themes", []):
            impact["cost_impact"] = base_price * 0.15  # 15% increase
        else:
            impact["cost_impact"] = 0
        
        # Performance impact
        if customization_analysis["impact_level"] == "high":
            impact["performance_impact"] = "significant"
            impact["risk_impact"] = "increased"
        elif customization_analysis["impact_level"] == "medium":
            impact["performance_impact"] = "moderate"
            impact["risk_impact"] = "slightly_increased"
        
        # Operational impact
        if customization_analysis["changes_count"] > 3:
            impact["operational_impact"] = "increased_complexity"
        
        return impact
    
    def _categorize_customization(self, customization_analysis: Dict[str, Any]) -> str:
        """Categorize customization type"""
        themes = customization_analysis.get("key_themes", [])
        
        if "cost" in themes:
            return "cost_optimization"
        elif "performance" in themes:
            return "performance_enhancement"
        elif "compliance" in themes:
            return "compliance_requirement"
        elif "experience" in themes or "familiar" in str(themes).lower():
            return "operational_preference"
        else:
            # Default based on impact
            if customization_analysis["impact_level"] == "high":
                return "performance_enhancement"
            else:
                return "operational_preference"
    
    def _assess_learning_value(self, customization_analysis: Dict[str, Any],
                              category: str) -> Dict[str, Any]:
        """Assess learning value from customization"""
        learning_value = {
            "value_score": 0,
            "primary_learning": "",
            "data_quality": "medium",
            "actionable": False
        }
        
        # Score based on various factors
        score = 0
        
        # Reasoning quality
        if customization_analysis.get("reasoning_present", False):
            score += 20
            word_count = customization_analysis.get("word_count", 0)
            if word_count > 10:
                score += 10
                learning_value["data_quality"] = "high"
        
        # Impact level
        if customization_analysis["impact_level"] == "high":
            score += 30
            learning_value["actionable"] = True
        elif customization_analysis["impact_level"] == "medium":
            score += 20
        
        # Departure from AI
        departure = customization_analysis["departure_from_ai"]
        score += int(departure * 20)
        
        # Category specific bonus
        category_bonus = {
            "cost_optimization": 15,
            "performance_enhancement": 20,
            "operational_preference": 10,
            "compliance_requirement": 25
        }
        
        score += category_bonus.get(category, 10)
        
        learning_value["value_score"] = min(score, 100)
        
        # Determine primary learning
        if category == "cost_optimization":
            learning_value["primary_learning"] = "pricing_accuracy_improvement"
        elif category == "performance_enhancement":
            learning_value["primary_learning"] = "performance_prediction_refinement"
        elif category == "operational_preference":
            learning_value["primary_learning"] = "user_preference_pattern"
        elif category == "compliance_requirement":
            learning_value["primary_learning"] = "compliance_mapping_gap"
        
        return learning_value
    
    async def _process_rejected_decision(self, consolidated_data: Dict[str, Any],
                                       user_feedback: Optional[str],
                                       decision_time_seconds: int) -> Dict[str, Any]:
        """Process rejected decision"""
        logger.info("❌ Processing rejected decision")
        
        # Analyze rejection
        rejection_analysis = self._analyze_rejection(
            consolidated_data, user_feedback
        )
        
        # Generate alternatives
        alternatives = self._generate_alternatives(consolidated_data, rejection_analysis)
        
        # Calculate learning opportunity
        learning_opportunity = self._assess_rejection_learning(
            rejection_analysis, consolidated_data
        )
        
        return {
            "decision_analysis": {
                "type": "rejected",
                "rejection_analysis": rejection_analysis,
                "primary_rejection_reasons": rejection_analysis.get("primary_reasons", []),
                "confidence_gap": 1.0 - consolidated_data["architecture"]["confidence"],
                "user_dissatisfaction_level": rejection_analysis.get("dissatisfaction_level", "medium")
            },
            "alternatives": alternatives,
            "learning_opportunity": learning_opportunity,
            "deployment_readiness": {
                "status": "not_ready",
                "estimated_deployment_time": "TBD",
                "complexity": "very_high",
                "success_probability": 0.3,
                "action_required": "Major revision needed"
            },
            "business_impact": {
                "immediate_impact": "Negative - AI recommendation rejected",
                "long_term_value": "Learning opportunity for model improvement",
                "risk_level": "High",
                "recommendation": "Engage with user to understand concerns and revise approach"
            }
        }
    
    def _analyze_rejection(self, consolidated_data: Dict[str, Any],
                          user_feedback: Optional[str]) -> Dict[str, Any]:
        """Analyze rejection reasons"""
        analysis = {
            "has_feedback": bool(user_feedback),
            "feedback_length": len(user_feedback) if user_feedback else 0,
            "primary_reasons": [],
            "dissatisfaction_level": "medium",
            "model_gap_areas": []
        }
        
        # Extract reasons from feedback if available
        if user_feedback:
            feedback_lower = user_feedback.lower()
            
            # Common rejection reasons
            rejection_patterns = {
                "cost_concerns": ["expensive", "cost", "budget", "price", "cheaper"],
                "complexity": ["complex", "complicated", "difficult", "hard"],
                "misalignment": ["not what", "different", "wrong", "doesn't fit"],
                "trust_issues": ["trust", "confidence", "believe", "uncertain"],
                "timing": ["time", "schedule", "timeline", "later", "not now"]
            }
            
            for reason, keywords in rejection_patterns.items():
                if any(keyword in feedback_lower for keyword in keywords):
                    analysis["primary_reasons"].append(reason)
            
            # Sentiment analysis
            negative_words = ["bad", "poor", "wrong", "incorrect", "disappointed", "unsatisfied"]
            strong_negative = ["terrible", "awful", "horrible", "useless", "waste"]
            
            negative_count = sum(1 for word in negative_words if word in feedback_lower)
            strong_count = sum(1 for word in strong_negative if word in feedback_lower)
            
            if strong_count > 0:
                analysis["dissatisfaction_level"] = "very_high"
            elif negative_count > 2:
                analysis["dissatisfaction_level"] = "high"
            elif negative_count > 0:
                analysis["dissatisfaction_level"] = "medium"
            else:
                analysis["dissatisfaction_level"] = "low"
        
        # If no feedback, infer from data
        if not analysis["primary_reasons"]:
            # Check confidence levels
            if consolidated_data["architecture"]["confidence"] < 0.7:
                analysis["primary_reasons"].append("low_confidence")
            
            # Check price vs alternatives
            primary_price = consolidated_data["pricing"]["primary_price"]
            alternative_prices = consolidated_data["pricing"]["alternative_prices"]
            
            if alternative_prices:
                min_alt_price = min(alternative_prices.values())
                if primary_price > min_alt_price * 1.2:  # 20% more expensive
                    analysis["primary_reasons"].append("high_cost")
            
            # Check risk assessment
            risk_level = consolidated_data["analysis"]["risk_assessment"]["overall_risk"]
            if risk_level == "high":
                analysis["primary_reasons"].append("high_risk")
        
        # Identify model gap areas
        if "cost_concerns" in analysis["primary_reasons"]:
            analysis["model_gap_areas"].append("pricing_accuracy")
        if "misalignment" in analysis["primary_reasons"]:
            analysis["model_gap_areas"].append("requirement_understanding")
        if "trust_issues" in analysis["primary_reasons"]:
            analysis["model_gap_areas"].append("confidence_calibration")
        
        return analysis
    
    def _generate_alternatives(self, consolidated_data: Dict[str, Any],
                              rejection_analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate alternative recommendations based on rejection"""
        alternatives = []
        primary_arch = consolidated_data["architecture"]["primary"]
        primary_price = consolidated_data["pricing"]["primary_price"]
        alternative_prices = consolidated_data["pricing"]["alternative_prices"]
        
        # If cost was an issue, suggest cheaper alternatives
        if "cost_concerns" in rejection_analysis["primary_reasons"]:
            for arch, price in alternative_prices.items():
                if price < primary_price and arch != primary_arch:
                    alternatives.append({
                        "type": "cost_optimized",
                        "architecture": arch,
                        "estimated_price": price,
                        "savings_vs_primary": primary_price - price,
                        "reasoning": f"Lower cost alternative to address budget concerns"
                    })
        
        # If complexity was an issue, suggest simpler architectures
        if "complexity" in rejection_analysis["primary_reasons"]:
            if primary_arch != "serverless":
                alternatives.append({
                    "type": "simplified",
                    "architecture": "serverless",
                    "estimated_price": alternative_prices.get("serverless", primary_price * 0.8),
                    "complexity_reduction": "High - minimal operations required",
                    "reasoning": "Serverless provides simplest operational model"
                })
        
        # If trust was an issue, suggest more conventional approaches
        if "trust_issues" in rejection_analysis["primary_reasons"]:
            alternatives.append({
                "type": "conventional",
                "architecture": "virtual_machines",
                "estimated_price": alternative_prices.get("virtual_machines", primary_price),
                "trust_factors": ["Well-understood technology", "Predictable performance", "Full control"],
                "reasoning": "Traditional VMs provide familiarity and control"
            })
        
        # Always include manual consultation as fallback
        alternatives.append({
            "type": "consultation",
            "description": "Manual architecture review with cloud expert",
            "estimated_time": "2-4 hours",
            "cost": "Variable based on complexity",
            "reasoning": "Human expert review for complex or high-stakes decisions"
        })
        
        return alternatives
    
    def _assess_rejection_learning(self, rejection_analysis: Dict[str, Any],
                                  consolidated_data: Dict[str, Any]) -> Dict[str, Any]:
        """Assess learning opportunity from rejection"""
        learning = {
            "opportunity_score": 0,
            "key_insights": [],
            "model_improvement_areas": [],
            "data_collection_priority": "medium"
        }
        
        score = 0
        
        # Feedback quality
        if rejection_analysis["has_feedback"]:
            score += 30
            if rejection_analysis["feedback_length"] > 20:
                score += 20
                learning["data_collection_priority"] = "high"
        
        # Clear rejection reasons
        reasons_count = len(rejection_analysis["primary_reasons"])
        score += reasons_count * 15
        
        # Model gap identification
        gap_areas = rejection_analysis.get("model_gap_areas", [])
        score += len(gap_areas) * 20
        learning["model_improvement_areas"] = gap_areas
        
        # Dissatisfaction level
        dissatisfaction_scores = {
            "very_high": 40,
            "high": 30,
            "medium": 20,
            "low": 10
        }
        dissatisfaction = rejection_analysis.get("dissatisfaction_level", "medium")
        score += dissatisfaction_scores.get(dissatisfaction, 20)
        
        learning["opportunity_score"] = min(score, 100)
        
        # Generate key insights
        if "cost_concerns" in rejection_analysis.get("primary_reasons", []):
            learning["key_insights"].append("Pricing may not align with user budget expectations")
        if "complexity" in rejection_analysis.get("primary_reasons", []):
            learning["key_insights"].append("Architecture complexity exceeded user comfort level")
        if "misalignment" in rejection_analysis.get("primary_reasons", []):
            learning["key_insights"].append("Requirements may have been misinterpreted")
        if "trust_issues" in rejection_analysis.get("primary_reasons", []):
            learning["key_insights"].append("AI confidence may need recalibration")
        
        return learning
    
    async def _generate_decision_artifacts(self, decision_type: str,
                                          consolidated_data: Dict[str, Any],
                                          decision_processing: Dict[str, Any],
                                          customization_details: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate deployment artifacts based on decision"""
        artifacts = {
            "generated": False,
            "artifacts_list": [],
            "generation_time_ms": 0,
            "download_urls": {}
        }
        
        start_time = time.time()
        
        if decision_type == "accepted":
            # Generate full deployment artifacts
            artifacts["generated"] = True
            artifacts["artifacts_list"] = [
                "terraform_main.tf",
                "terraform_variables.tf",
                "terraform_outputs.tf",
                "Dockerfile",
                "docker-compose.yml",
                "README.md",
                "DEPLOYMENT_GUIDE.md",
                "monitoring_config.yaml"
            ]
            
            # Generate Terraform configuration
            artifacts["terraform_config"] = self._generate_terraform_config(consolidated_data)
            
            # Generate Docker configuration
            artifacts["docker_config"] = self._generate_docker_config(consolidated_data)
            
            # Generate README
            artifacts["readme"] = self._generate_readme(consolidated_data)
            
        elif decision_type == "customized":
            # Generate modified artifacts
            artifacts["generated"] = True
            artifacts["artifacts_list"] = [
                "terraform_main_customized.tf",
                "terraform_variables_customized.tf",
                "CUSTOMIZATION_NOTES.md"
            ]
            
            # Generate customized config
            artifacts["terraform_config"] = self._generate_customized_terraform(
                consolidated_data, customization_details
            )
            
        else:  # rejected
            artifacts["generated"] = False
            artifacts["artifacts_list"] = []
            artifacts["message"] = "Artifacts not generated for rejected recommendations"
        
        artifacts["generation_time_ms"] = int((time.time() - start_time) * 1000)
        
        return artifacts
    
    def _generate_terraform_config(self, consolidated_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate Terraform configuration"""
        arch = consolidated_data["architecture"]["primary"]
        spec = consolidated_data["specification"]
        
        config = {
            "provider": "google",
            "version": ">= 4.0",
            "project": "${var.project_id}",
            "region": "${var.region}",
            "resources": []
        }
        
        if arch == "serverless":
            config["resources"].append({
                "type": "google_cloud_run_v2_service",
                "name": "main_service",
                "config": {
                    "location": "${var.region}",
                    "template": {
                        "containers": [{
                            "image": "${var.container_image}",
                            "resources": {
                                "limits": {
                                    "cpu": str(spec.get("cpu", 2)),
                                    "memory": f"{spec.get('ram', 4)}Gi"
                                }
                            }
                        }],
                        "scaling": {
                            "min_instance_count": 0,
                            "max_instance_count": 100
                        }
                    }
                }
            })
        elif arch == "containers":
            config["resources"].append({
                "type": "google_container_cluster",
                "name": "primary_cluster",
                "config": {
                    "location": "${var.region}",
                    "initial_node_count": 3,
                    "node_config": {
                        "machine_type": spec.get("machine_type", "n2-standard-4"),
                        "disk_size_gb": 100,
                        "disk_type": "pd-ssd"
                    }
                }
            })
        else:  # virtual_machines
            config["resources"].append({
                "type": "google_compute_instance_template",
                "name": "main_template",
                "config": {
                    "machine_type": spec.get("machine_type", "n2-standard-4"),
                    "disk": {
                        "source_image": "projects/debian-cloud/global/images/family/debian-11",
                        "disk_size_gb": 50,
                        "disk_type": "pd-ssd"
                    }
                }
            })
        
        return config
    
    def _generate_docker_config(self, consolidated_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate Docker configuration"""
        spec = consolidated_data["specification"]
        
        return {
            "dockerfile": {
                "base_image": "python:3.11-slim",
                "workdir": "/app",
                "exposed_port": 8080,
                "healthcheck": {
                    "test": ["CMD", "curl", "-f", "http://localhost:8080/health"],
                    "interval": "30s",
                    "timeout": "10s",
                    "retries": 3
                }
            },
            "docker_compose": {
                "version": "3.8",
                "services": {
                    "app": {
                        "build": ".",
                        "ports": ["8080:8080"],
                        "environment": {
                            "PORT": 8080,
                            "ENV": "production"
                        },
                        "deploy": {
                            "resources": {
                                "limits": {
                                    "cpus": str(spec.get("cpu", 2)),
                                    "memory": f"{spec.get('ram', 4)}G"
                                }
                            }
                        }
                    }
                }
            }
        }
    
    def _generate_customized_terraform(self, consolidated_data: Dict[str, Any],
                                       customization_details: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate customized Terraform config"""
        base_config = self._generate_terraform_config(consolidated_data)
        
        # Apply customizations
        if customization_details:
            changes = customization_details.get("changes", [])
            for change in changes:
                change_type = change.get("type", "")
                new_value = change.get("to", "")
                
                if change_type == "region":
                    base_config["region"] = new_value
                elif change_type == "cpu":
                    for resource in base_config.get("resources", []):
                        if "template" in resource.get("config", {}):
                            resource["config"]["template"]["containers"][0]["resources"]["limits"]["cpu"] = str(new_value)
                elif change_type == "ram":
                    for resource in base_config.get("resources", []):
                        if "template" in resource.get("config", {}):
                            resource["config"]["template"]["containers"][0]["resources"]["limits"]["memory"] = f"{new_value}Gi"
        
        base_config["customized"] = True
        base_config["customization_applied"] = datetime.now().isoformat()
        
        return base_config
    
    def _generate_readme(self, consolidated_data: Dict[str, Any]) -> str:
        """Generate deployment README"""
        arch = consolidated_data["architecture"]["primary"]
        price = consolidated_data["pricing"]["primary_price"]
        workload = consolidated_data["workload"]["type"]
        
        return f"""# Infrastructure Deployment Guide

## Overview
This deployment package was generated by Google Cloud Sentinel AI.

**Workload Type:** {workload}
**Architecture:** {arch}
**Estimated Monthly Cost:** ${price:,.2f}

## Prerequisites
- Google Cloud SDK installed
- Terraform >= 1.0.0
- Docker (for containerized deployments)

## Quick Start
1. Set your GCP project: `gcloud config set project YOUR_PROJECT`
2. Initialize Terraform: `terraform init`
3. Plan deployment: `terraform plan`
4. Apply: `terraform apply`

## Files Included
- `terraform_main.tf` - Main infrastructure configuration
- `terraform_variables.tf` - Configurable variables
- `terraform_outputs.tf` - Output definitions
- `Dockerfile` - Container build configuration
- `docker-compose.yml` - Local development setup
- `monitoring_config.yaml` - Monitoring and alerting

## Support
Generated by Google Cloud Sentinel v1.0.0
"""
    
    def _generate_learning_signals(self, decision_type: str,
                                   consolidated_data: Dict[str, Any],
                                   decision_processing: Dict[str, Any],
                                   user_feedback: Optional[str]) -> List[Dict[str, Any]]:
        """Generate learning signals for Phase 8"""
        signals = []
        
        # Base signal for all decisions
        base_signal = {
            "signal_id": f"signal_{uuid.uuid4().hex[:8]}",
            "signal_type": "decision",
            "decision_type": decision_type,
            "timestamp": datetime.now().isoformat(),
            "workload_type": consolidated_data["workload"]["type"],
            "architecture": consolidated_data["architecture"]["primary"],
            "confidence": consolidated_data["architecture"]["confidence"],
            "price": consolidated_data["pricing"]["primary_price"]
        }
        signals.append(base_signal)
        
        # Decision-specific signals
        if decision_type == "accepted":
            signals.append({
                "signal_id": f"signal_{uuid.uuid4().hex[:8]}",
                "signal_type": "reinforcement",
                "reinforcement_strength": "strong",
                "parameters_validated": [
                    "architecture_selection",
                    "machine_specification",
                    "pricing_estimation"
                ],
                "recommendation_strength": consolidated_data["analysis"]["recommendation_strength"]
            })
            
        elif decision_type == "customized":
            customization_analysis = decision_processing.get("decision_analysis", {}).get("customization_analysis", {})
            signals.append({
                "signal_id": f"signal_{uuid.uuid4().hex[:8]}",
                "signal_type": "correction",
                "correction_type": decision_processing.get("decision_analysis", {}).get("customization_category", "unknown"),
                "changes_count": customization_analysis.get("changes_count", 0),
                "impact_level": customization_analysis.get("impact_level", "unknown"),
                "departure_from_ai": customization_analysis.get("departure_from_ai", 0),
                "learning_focus": decision_processing.get("decision_analysis", {}).get("learning_value", {}).get("primary_learning", "unknown")
            })
            
        elif decision_type == "rejected":
            rejection_analysis = decision_processing.get("decision_analysis", {}).get("rejection_analysis", {})
            signals.append({
                "signal_id": f"signal_{uuid.uuid4().hex[:8]}",
                "signal_type": "negative_feedback",
                "rejection_reasons": rejection_analysis.get("primary_reasons", []),
                "model_gap_areas": rejection_analysis.get("model_gap_areas", []),
                "dissatisfaction_level": rejection_analysis.get("dissatisfaction_level", "unknown"),
                "priority": "high"
            })
        
        # User feedback signal
        if user_feedback:
            signals.append({
                "signal_id": f"signal_{uuid.uuid4().hex[:8]}",
                "signal_type": "user_feedback",
                "feedback_text": user_feedback,
                "feedback_length": len(user_feedback),
                "has_actionable_content": len(user_feedback) > 20
            })
        
        return signals
    
    def _enhance_decision_result(self, decision_processing: Dict[str, Any],
                                  artifacts: Dict[str, Any],
                                  learning_signals: List[Dict[str, Any]],
                                  consolidated_data: Dict[str, Any],
                                  decision_type: str,
                                  decision_time_seconds: int,
                                  user_feedback: Optional[str],
                                  customization_details: Optional[Dict[str, Any]],
                                  processing_time_ms: int,
                                  decision_method: str,
                                  user_id: str,
                                  session_id: str,
                                  request_id: str) -> Dict[str, Any]:
        """Enhance decision result with all metadata"""
        decision_id = f"dec_{int(time.time())}_{uuid.uuid4().hex[:6]}"
        
        return {
            "decision_id": decision_id,
            "request_id": request_id,
            "user_id": user_id,
            "session_id": session_id,
            "phase": self.phase_name,
            "phase_version": self.phase_version,
            "status": "completed",
            
            # Decision data
            "decision_type": decision_type,
            "decision_time_seconds": decision_time_seconds,
            "decision_method": decision_method,
            
            # Processing results
            "decision_processing": decision_processing,
            
            # Customization if applicable
            "customization_details": customization_details if decision_type == "customized" else None,
            
            # User feedback
            "user_feedback": {
                "provided": bool(user_feedback),
                "content": user_feedback,
                "length": len(user_feedback) if user_feedback else 0
            },
            
            # Artifacts
            "artifacts": artifacts,
            
            # Learning signals for Phase 8
            "learning_signals": learning_signals,
            
            # Reference data from previous phases
            "consolidated_data": {
                "workload_type": consolidated_data["workload"]["type"],
                "architecture": consolidated_data["architecture"]["primary"],
                "monthly_cost": consolidated_data["pricing"]["primary_price"],
                "recommendation_strength": consolidated_data["analysis"]["recommendation_strength"]
            },
            
            # Next actions
            "next_actions": self._generate_next_actions(decision_type, artifacts),
            
            # Processing metadata
            "processing_metadata": {
                "processing_time_ms": processing_time_ms,
                "timestamp": datetime.now().isoformat(),
                "decision_type_info": self.decision_types[decision_type]
            },
            
            # Phase transition
            "next_phase": "learning_feedback",
            "phase_transition": {
                "from_phase": "user_decision",
                "to_phase": "learning_feedback",
                "transition_data": {
                    "learning_signals_count": len(learning_signals),
                    "feedback_provided": bool(user_feedback),
                    "artifacts_generated": artifacts["generated"]
                }
            }
        }
    
    def _generate_next_actions(self, decision_type: str, artifacts: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate next actions based on decision"""
        actions = []
        
        if decision_type == "accepted":
            actions = [
                {
                    "action": "download_artifacts",
                    "description": "Download deployment artifacts",
                    "priority": "high",
                    "estimated_time": "1 minute"
                },
                {
                    "action": "review_terraform",
                    "description": "Review Terraform configuration",
                    "priority": "high",
                    "estimated_time": "15 minutes"
                },
                {
                    "action": "setup_cicd",
                    "description": "Setup CI/CD pipeline",
                    "priority": "medium",
                    "estimated_time": "2 hours"
                },
                {
                    "action": "deploy",
                    "description": "Deploy to GCP",
                    "priority": "high",
                    "estimated_time": "30 minutes"
                },
                {
                    "action": "configure_monitoring",
                    "description": "Configure monitoring and alerts",
                    "priority": "medium",
                    "estimated_time": "1 hour"
                }
            ]
            
        elif decision_type == "customized":
            actions = [
                {
                    "action": "review_customizations",
                    "description": "Review customization impact",
                    "priority": "high",
                    "estimated_time": "30 minutes"
                },
                {
                    "action": "validate_configuration",
                    "description": "Validate customized configuration",
                    "priority": "high",
                    "estimated_time": "1 hour"
                },
                {
                    "action": "recalculate_pricing",
                    "description": "Recalculate pricing with customizations",
                    "priority": "medium",
                    "estimated_time": "5 minutes"
                },
                {
                    "action": "test_deployment",
                    "description": "Test deployment in staging",
                    "priority": "high",
                    "estimated_time": "2 hours"
                }
            ]
            
        elif decision_type == "rejected":
            actions = [
                {
                    "action": "provide_feedback",
                    "description": "Provide detailed feedback",
                    "priority": "high",
                    "estimated_time": "5 minutes"
                },
                {
                    "action": "explore_alternatives",
                    "description": "Explore alternative recommendations",
                    "priority": "high",
                    "estimated_time": "15 minutes"
                },
                {
                    "action": "request_consultation",
                    "description": "Request expert consultation",
                    "priority": "medium",
                    "estimated_time": "Schedule"
                },
                {
                    "action": "restart_analysis",
                    "description": "Restart with refined requirements",
                    "priority": "low",
                    "estimated_time": "10 minutes"
                }
            ]
        
        return actions
    
    def _update_statistics(self, decision_type: str, decision_time_seconds: int,
                          user_feedback: Optional[str]):
        """Update internal statistics"""
        self.stats["total_decision_time_ms"] += decision_time_seconds * 1000
        self.stats["avg_decision_time_ms"] = (
            self.stats["total_decision_time_ms"] / self.stats["total_decisions"]
        )
        
        if user_feedback:
            self.stats["user_feedback_count"] += 1
    
    def _emit_decision_telemetry(self, result: Dict[str, Any], processing_time_ms: int):
        """Emit comprehensive telemetry for decision"""
        decision_type = result["decision_type"]
        decision_id = result["decision_id"]
        
        # Emit decision event
        self.telemetry.emit_event(
            title=f"User {decision_type.title()} AI Recommendation",
            text=f"User {decision_type} recommendation for {result['consolidated_data']['workload_type']} "
                 f"with {result['consolidated_data']['architecture']} architecture",
            tags=[
                f"decision:{decision_type}",
                f"architecture:{result['consolidated_data']['architecture']}",
                f"workload:{result['consolidated_data']['workload_type']}",
                f"decision_id:{decision_id}",
                f"time_to_decision:{result['decision_time_seconds']}s"
            ],
            alert_type="info" if decision_type == "accepted" else "warning"
        )
        
        # Emit metrics
        metrics = [
            {
                "name": f"ai.recommendation.{decision_type}_rate",
                "value": 1.0,
                "tags": [
                    f"architecture:{result['consolidated_data']['architecture']}",
                    f"workload:{result['consolidated_data']['workload_type']}"
                ]
            },
            {
                "name": "user.decision.time",
                "value": float(result["decision_time_seconds"]),
                "tags": [f"decision_type:{decision_type}"]
            },
            {
                "name": "phase7.processing_time_ms",
                "value": float(processing_time_ms),
                "tags": [f"decision_type:{decision_type}"]
            }
        ]
        
        for metric in metrics:
            self.telemetry.submit_metric(
                name=metric["name"],
                value=metric["value"],
                tags=metric.get("tags", [])
            )
        
        # Emit detailed log
        self.telemetry.submit_log(
            source="user.decision.processed",
            message={
                "decision_id": decision_id,
                "decision_type": decision_type,
                "workload_type": result["consolidated_data"]["workload_type"],
                "architecture": result["consolidated_data"]["architecture"],
                "monthly_cost": result["consolidated_data"]["monthly_cost"],
                "decision_time_seconds": result["decision_time_seconds"],
                "feedback_provided": result["user_feedback"]["provided"],
                "artifacts_generated": result["artifacts"]["generated"],
                "learning_signals_count": len(result["learning_signals"]),
                "processing_time_ms": processing_time_ms
            },
            tags=["decision", "telemetry", f"phase7_{decision_type}"],
            level="info"
        )
    
    def _create_error_result(self, user_id: str, session_id: str, request_id: str,
                            consolidated_data: Dict[str, Any], decision_type: str,
                            error_message: str, processing_time_ms: int) -> Dict[str, Any]:
        """Create error result for failed processing"""
        return {
            "decision_id": f"dec_error_{int(time.time())}_{uuid.uuid4().hex[:6]}",
            "request_id": request_id,
            "user_id": user_id,
            "session_id": session_id,
            "phase": self.phase_name,
            "phase_version": self.phase_version,
            "status": "failed",
            "decision_type": decision_type,
            "error": {
                "message": error_message,
                "timestamp": datetime.now().isoformat()
            },
            "processing_metadata": {
                "processing_time_ms": processing_time_ms,
                "timestamp": datetime.now().isoformat()
            }
        }
    
    def _emit_error_telemetry(self, error_result: Dict[str, Any], error_message: str):
        """Emit error telemetry"""
        self.telemetry.emit_event(
            title="Phase 7 Processing Failed",
            text=f"Decision processing failed: {error_message}",
            tags=["error", "phase7", f"decision_type:{error_result.get('decision_type', 'unknown')}"],
            alert_type="error"
        )
        
        self.telemetry.submit_metric(
            name="phase7.errors",
            value=1.0,
            tags=[f"decision_type:{error_result.get('decision_type', 'unknown')}"]
        )
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get current phase statistics"""
        return {
            "phase_name": self.phase_name,
            "phase_version": self.phase_version,
            "statistics": self.stats,
            "decision_type_definitions": self.decision_types,
            "customization_categories": list(self.customization_categories.keys())
        }
    
    def flush_buffers(self):
        """Flush telemetry buffers"""
        self.telemetry.flush_buffers()