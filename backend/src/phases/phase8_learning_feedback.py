"""
Phase 8: Learning Feedback & Continuous Improvement
Production-grade implementation for learning from user decisions and improving recommendations
"""

import time
import logging
import json
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
import uuid
import random
import hashlib

from ..core.gemini_client import GeminiClient
from ..telemetry.datadog_client import TelemetryClient, TelemetryConfig, TelemetryMode

logger = logging.getLogger(__name__)


class LearningFeedbackPhase:
    """Complete Phase 8: Learning Feedback & Continuous Improvement"""
    
    def __init__(self, telemetry_config: Optional[TelemetryConfig] = None):
        self.phase_name = "learning_feedback"
        self.phase_version = "1.0.0"
        
        # Initialize clients
        self.gemini = GeminiClient()
        self.telemetry = TelemetryClient(telemetry_config)
        
        # Learning model configuration
        self.model_version = "1.2"
        self.learning_parameters = self._initialize_learning_parameters()
        
        # Feedback categories
        self.feedback_categories = {
            "over_provisioned": {
                "description": "Resources were more than needed",
                "adjustment_direction": "decrease",
                "parameters_affected": ["cpu", "ram", "instance_count"],
                "confidence_impact": -0.15,
                "learning_priority": "high"
            },
            "under_provisioned": {
                "description": "Resources were insufficient",
                "adjustment_direction": "increase",
                "parameters_affected": ["cpu", "ram", "instance_count"],
                "confidence_impact": -0.20,
                "learning_priority": "critical"
            },
            "cost_higher_than_expected": {
                "description": "Actual cost exceeded estimate",
                "adjustment_direction": "recalibrate",
                "parameters_affected": ["pricing_model", "usage_estimation"],
                "confidence_impact": -0.10,
                "learning_priority": "high"
            },
            "cost_lower_than_expected": {
                "description": "Actual cost was less than estimate",
                "adjustment_direction": "recalibrate",
                "parameters_affected": ["pricing_model"],
                "confidence_impact": 0.05,
                "learning_priority": "medium"
            },
            "performance_issues": {
                "description": "Performance did not meet expectations",
                "adjustment_direction": "optimize",
                "parameters_affected": ["architecture", "configuration", "scaling"],
                "confidence_impact": -0.25,
                "learning_priority": "critical"
            },
            "architecture_mismatch": {
                "description": "Architecture choice was not optimal",
                "adjustment_direction": "revise",
                "parameters_affected": ["architecture_selection", "workload_mapping"],
                "confidence_impact": -0.30,
                "learning_priority": "critical"
            },
            "perfect_fit": {
                "description": "Recommendation was exactly right",
                "adjustment_direction": "reinforce",
                "parameters_affected": [],
                "confidence_impact": 0.10,
                "learning_priority": "low"
            },
            "minor_adjustments_needed": {
                "description": "Small tweaks were required",
                "adjustment_direction": "fine_tune",
                "parameters_affected": ["configuration"],
                "confidence_impact": -0.05,
                "learning_priority": "medium"
            }
        }
        
        # Learning history (in production, this would be persisted)
        self.learning_history = []
        self.model_updates = []
        
        # Statistics
        self.stats = {
            "total_feedback_processed": 0,
            "positive_feedback": 0,
            "negative_feedback": 0,
            "neutral_feedback": 0,
            "model_updates_applied": 0,
            "avg_confidence_change": 0.0,
            "learning_signals_processed": 0
        }
        
        logger.info(f"✅ Phase 8 initialized: {self.phase_name} v{self.phase_version}")
        logger.info(f"📚 Feedback categories: {len(self.feedback_categories)}")
        logger.info(f"🧠 Model version: {self.model_version}")
    
    def _initialize_learning_parameters(self) -> Dict[str, Any]:
        """Initialize learning parameters for the recommendation model"""
        return {
            "cpu_allocation": {
                "base_multiplier": 1.0,
                "workload_adjustments": {
                    "api_backend": 0.0,
                    "web_app": -0.1,
                    "ml_inference": 0.2,
                    "data_pipeline": 0.1,
                    "batch_processing": -0.1
                },
                "feedback_count": 0,
                "last_updated": None
            },
            "ram_allocation": {
                "base_multiplier": 1.0,
                "workload_adjustments": {
                    "api_backend": 0.0,
                    "web_app": -0.1,
                    "ml_inference": 0.3,
                    "data_pipeline": 0.2,
                    "batch_processing": 0.0
                },
                "feedback_count": 0,
                "last_updated": None
            },
            "pricing_accuracy": {
                "adjustment_factor": 1.0,
                "region_adjustments": {},
                "service_adjustments": {},
                "feedback_count": 0,
                "last_updated": None
            },
            "architecture_selection": {
                "confidence_thresholds": {
                    "serverless": 0.75,
                    "containers": 0.70,
                    "virtual_machines": 0.65
                },
                "workload_preferences": {},
                "feedback_count": 0,
                "last_updated": None
            },
            "scaling_predictions": {
                "base_scaling_factor": 1.0,
                "peak_buffer": 0.2,
                "minimum_instances": 1,
                "feedback_count": 0,
                "last_updated": None
            }
        }
    
    async def process(self, phase7_result: Dict[str, Any],
                     deployment_feedback: Optional[Dict[str, Any]] = None,
                     performance_metrics: Optional[Dict[str, Any]] = None,
                     cost_actuals: Optional[Dict[str, Any]] = None,
                     user_satisfaction: Optional[str] = None,
                     feedback_delay_days: int = 0,
                     user_id: Optional[str] = None,
                     session_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Process learning feedback and update recommendation model
        
        Args:
            phase7_result: Complete output from Phase 7
            deployment_feedback: Post-deployment feedback (e.g., "over_provisioned")
            performance_metrics: Actual performance metrics after deployment
            cost_actuals: Actual costs vs. estimates
            user_satisfaction: Overall user satisfaction rating
            feedback_delay_days: Days since deployment (for weighting)
            user_id: User identifier
            session_id: Session identifier
            
        Returns:
            Dict containing learning analysis and model updates
        """
        start_time = time.time()
        
        # Validate inputs
        if not phase7_result:
            raise ValueError("Phase 7 result is required")
        
        self.stats["total_feedback_processed"] += 1
        
        # Extract data from Phase 7
        decision_id = phase7_result.get("decision_id", f"dec_{uuid.uuid4().hex[:8]}")
        decision_type = phase7_result.get("decision_type", "unknown")
        learning_signals = phase7_result.get("learning_signals", [])
        consolidated_data = phase7_result.get("consolidated_data", {})
        
        # Use IDs from Phase 7
        request_id = phase7_result.get("request_id", f"req_{int(time.time())}_{uuid.uuid4().hex[:6]}")
        user_id = user_id or phase7_result.get("user_id", f"user_{uuid.uuid4().hex[:8]}")
        session_id = session_id or phase7_result.get("session_id", f"session_{uuid.uuid4().hex[:8]}")
        
        try:
            logger.info(f"📚 Processing learning feedback for decision: {decision_id}")
            logger.info(f"   Decision type: {decision_type}")
            logger.info(f"   Learning signals: {len(learning_signals)}")
            
            # Step 1: Process learning signals from Phase 7
            signals_analysis = self._analyze_learning_signals(learning_signals)
            self.stats["learning_signals_processed"] += len(learning_signals)
            
            # Step 2: Process deployment feedback if provided
            feedback_analysis = None
            if deployment_feedback:
                feedback_analysis = self._analyze_deployment_feedback(
                    deployment_feedback, consolidated_data
                )
                self._categorize_feedback(feedback_analysis)
            
            # Step 3: Process performance metrics if provided
            performance_analysis = None
            if performance_metrics:
                performance_analysis = self._analyze_performance_metrics(
                    performance_metrics, consolidated_data
                )
            
            # Step 4: Process cost actuals if provided
            cost_analysis = None
            if cost_actuals:
                cost_analysis = self._analyze_cost_actuals(
                    cost_actuals, consolidated_data
                )
            
            # Step 5: Generate learning updates
            learning_updates = self._generate_learning_updates(
                signals_analysis,
                feedback_analysis,
                performance_analysis,
                cost_analysis,
                consolidated_data,
                decision_type
            )
            
            # Step 6: Apply updates to model
            model_changes = self._apply_learning_updates(learning_updates)
            
            # Step 7: Calculate confidence adjustments
            confidence_adjustments = self._calculate_confidence_adjustments(
                learning_updates, feedback_analysis
            )
            
            # Step 8: Generate improvement insights
            insights = self._generate_improvement_insights(
                learning_updates, model_changes, consolidated_data
            )
            
            # Calculate processing time
            processing_time_ms = int((time.time() - start_time) * 1000)
            
            # Step 9: Build enhanced result
            enhanced_result = self._enhance_learning_result(
                decision_id=decision_id,
                request_id=request_id,
                user_id=user_id,
                session_id=session_id,
                signals_analysis=signals_analysis,
                feedback_analysis=feedback_analysis,
                performance_analysis=performance_analysis,
                cost_analysis=cost_analysis,
                learning_updates=learning_updates,
                model_changes=model_changes,
                confidence_adjustments=confidence_adjustments,
                insights=insights,
                processing_time_ms=processing_time_ms,
                decision_type=decision_type,
                user_satisfaction=user_satisfaction,
                feedback_delay_days=feedback_delay_days
            )
            
            # Step 10: Emit telemetry
            self._emit_learning_telemetry(enhanced_result, processing_time_ms)
            
            logger.info(f"✅ Learning feedback processed: {len(learning_updates)} updates")
            logger.info(f"   Model changes: {len(model_changes)}")
            logger.info(f"   Insights generated: {len(insights)}")
            logger.info(f"   Time: {processing_time_ms}ms")
            
            return enhanced_result
            
        except Exception as e:
            processing_time_ms = int((time.time() - start_time) * 1000)
            
            error_result = self._create_error_result(
                decision_id, request_id, user_id, session_id,
                str(e), processing_time_ms
            )
            
            self._emit_error_telemetry(error_result, str(e))
            
            logger.error(f"❌ Learning feedback processing failed: {e}")
            raise
    
    def _analyze_learning_signals(self, signals: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze learning signals from Phase 7"""
        analysis = {
            "total_signals": len(signals),
            "signal_types": {},
            "key_learnings": [],
            "priority_signals": [],
            "reinforcement_signals": [],
            "correction_signals": []
        }
        
        for signal in signals:
            signal_type = signal.get("signal_type", "unknown")
            analysis["signal_types"][signal_type] = analysis["signal_types"].get(signal_type, 0) + 1
            
            if signal_type == "reinforcement":
                analysis["reinforcement_signals"].append(signal)
                analysis["key_learnings"].append({
                    "type": "positive",
                    "message": "Recommendation accepted - parameters validated",
                    "strength": signal.get("reinforcement_strength", "medium")
                })
                
            elif signal_type == "correction":
                analysis["correction_signals"].append(signal)
                analysis["key_learnings"].append({
                    "type": "correction",
                    "message": f"User customized - {signal.get('correction_type', 'unknown')} needed",
                    "impact_level": signal.get("impact_level", "medium"),
                    "learning_focus": signal.get("learning_focus", "unknown")
                })
                
            elif signal_type == "negative_feedback":
                analysis["priority_signals"].append(signal)
                analysis["key_learnings"].append({
                    "type": "negative",
                    "message": "Recommendation rejected - investigation needed",
                    "reasons": signal.get("rejection_reasons", []),
                    "gap_areas": signal.get("model_gap_areas", [])
                })
                
            elif signal_type == "user_feedback":
                if signal.get("has_actionable_content", False):
                    analysis["priority_signals"].append(signal)
        
        return analysis
    
    def _analyze_deployment_feedback(self, feedback: Dict[str, Any],
                                     consolidated_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze post-deployment feedback"""
        feedback_type = feedback.get("type", "unknown")
        feedback_details = feedback.get("details", "")
        
        # Get feedback category info
        category_info = self.feedback_categories.get(
            feedback_type, 
            self.feedback_categories.get("minor_adjustments_needed")
        )
        
        analysis = {
            "feedback_type": feedback_type,
            "feedback_details": feedback_details,
            "category_info": category_info,
            "workload_type": consolidated_data.get("workload_type", "unknown"),
            "architecture": consolidated_data.get("architecture", "unknown"),
            "adjustment_needed": category_info.get("adjustment_direction", "none"),
            "parameters_to_adjust": category_info.get("parameters_affected", []),
            "confidence_impact": category_info.get("confidence_impact", 0),
            "priority": category_info.get("learning_priority", "medium")
        }
        
        # Determine sentiment
        if feedback_type in ["perfect_fit", "cost_lower_than_expected"]:
            analysis["sentiment"] = "positive"
            self.stats["positive_feedback"] += 1
        elif feedback_type in ["over_provisioned", "minor_adjustments_needed"]:
            analysis["sentiment"] = "neutral"
            self.stats["neutral_feedback"] += 1
        else:
            analysis["sentiment"] = "negative"
            self.stats["negative_feedback"] += 1
        
        return analysis
    
    def _categorize_feedback(self, feedback_analysis: Dict[str, Any]):
        """Categorize feedback for tracking"""
        sentiment = feedback_analysis.get("sentiment", "neutral")
        if sentiment == "positive":
            self.stats["positive_feedback"] += 1
        elif sentiment == "negative":
            self.stats["negative_feedback"] += 1
        else:
            self.stats["neutral_feedback"] += 1
    
    def _analyze_performance_metrics(self, metrics: Dict[str, Any],
                                     consolidated_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze actual performance metrics"""
        analysis = {
            "metrics_provided": True,
            "actual_vs_predicted": {},
            "performance_gaps": [],
            "optimization_opportunities": []
        }
        
        # Compare actual vs predicted metrics
        predicted_rps = consolidated_data.get("estimated_rps", 100)
        actual_rps = metrics.get("actual_rps", predicted_rps)
        
        rps_accuracy = min(actual_rps, predicted_rps) / max(actual_rps, predicted_rps) if max(actual_rps, predicted_rps) > 0 else 1.0
        
        analysis["actual_vs_predicted"]["rps"] = {
            "predicted": predicted_rps,
            "actual": actual_rps,
            "accuracy": rps_accuracy,
            "gap": abs(actual_rps - predicted_rps)
        }
        
        # Check latency
        predicted_latency = 50  # ms baseline
        actual_latency = metrics.get("actual_latency_ms", 50)
        
        if actual_latency > predicted_latency * 1.5:
            analysis["performance_gaps"].append({
                "metric": "latency",
                "issue": "Higher than expected",
                "predicted": predicted_latency,
                "actual": actual_latency,
                "recommendation": "Consider scaling or architecture optimization"
            })
        
        # Check CPU utilization
        actual_cpu = metrics.get("avg_cpu_utilization", 50)
        if actual_cpu < 30:
            analysis["optimization_opportunities"].append({
                "metric": "cpu",
                "issue": "Underutilized",
                "current": actual_cpu,
                "recommendation": "Consider reducing CPU allocation"
            })
        elif actual_cpu > 80:
            analysis["performance_gaps"].append({
                "metric": "cpu",
                "issue": "High utilization",
                "current": actual_cpu,
                "recommendation": "Consider scaling or adding capacity"
            })
        
        # Check memory utilization
        actual_memory = metrics.get("avg_memory_utilization", 50)
        if actual_memory < 30:
            analysis["optimization_opportunities"].append({
                "metric": "memory",
                "issue": "Underutilized",
                "current": actual_memory,
                "recommendation": "Consider reducing memory allocation"
            })
        elif actual_memory > 85:
            analysis["performance_gaps"].append({
                "metric": "memory",
                "issue": "High utilization",
                "current": actual_memory,
                "recommendation": "Consider increasing memory"
            })
        
        return analysis
    
    def _analyze_cost_actuals(self, cost_data: Dict[str, Any],
                             consolidated_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze actual costs vs estimates"""
        estimated_cost = consolidated_data.get("monthly_cost", 0)
        actual_cost = cost_data.get("actual_monthly_cost", estimated_cost)
        
        variance = actual_cost - estimated_cost
        variance_percent = (variance / estimated_cost * 100) if estimated_cost > 0 else 0
        
        analysis = {
            "estimated_cost": estimated_cost,
            "actual_cost": actual_cost,
            "variance": variance,
            "variance_percent": variance_percent,
            "accuracy": 1 - abs(variance_percent) / 100,
            "cost_breakdown_analysis": {}
        }
        
        # Determine cost accuracy category
        if abs(variance_percent) < 5:
            analysis["accuracy_category"] = "excellent"
            analysis["adjustment_needed"] = False
        elif abs(variance_percent) < 15:
            analysis["accuracy_category"] = "good"
            analysis["adjustment_needed"] = False
        elif abs(variance_percent) < 30:
            analysis["accuracy_category"] = "moderate"
            analysis["adjustment_needed"] = True
        else:
            analysis["accuracy_category"] = "poor"
            analysis["adjustment_needed"] = True
        
        # Identify cost drivers
        if variance > 0:
            analysis["primary_driver"] = "underestimation"
            analysis["recommendations"] = [
                "Review pricing model accuracy",
                "Check for unaccounted services",
                "Validate usage assumptions"
            ]
        elif variance < 0:
            analysis["primary_driver"] = "overestimation"
            analysis["recommendations"] = [
                "Adjust safety margins",
                "Review utilization patterns",
                "Consider committed use discounts"
            ]
        else:
            analysis["primary_driver"] = "accurate"
            analysis["recommendations"] = ["Maintain current estimation approach"]
        
        return analysis
    
    def _generate_learning_updates(self, signals_analysis: Dict[str, Any],
                                   feedback_analysis: Optional[Dict[str, Any]],
                                   performance_analysis: Optional[Dict[str, Any]],
                                   cost_analysis: Optional[Dict[str, Any]],
                                   consolidated_data: Dict[str, Any],
                                   decision_type: str) -> List[Dict[str, Any]]:
        """Generate learning updates based on all analyses"""
        updates = []
        workload_type = consolidated_data.get("workload_type", "unknown")
        architecture = consolidated_data.get("architecture", "unknown")
        
        # Updates from signals
        for signal in signals_analysis.get("correction_signals", []):
            correction_type = signal.get("correction_type", "")
            
            if correction_type == "cost_optimization":
                updates.append({
                    "update_id": f"upd_{uuid.uuid4().hex[:8]}",
                    "parameter": "pricing_accuracy",
                    "workload_pattern": f"{workload_type}_{architecture}",
                    "adjustment": "increase_estimate_buffer",
                    "adjustment_value": 0.05,
                    "confidence_change": -0.10,
                    "feedback_source": "user_customization",
                    "trigger": "cost_concerns",
                    "priority": "medium"
                })
                
            elif correction_type == "performance_enhancement":
                updates.append({
                    "update_id": f"upd_{uuid.uuid4().hex[:8]}",
                    "parameter": "cpu_allocation",
                    "workload_pattern": f"{workload_type}_{architecture}",
                    "adjustment": "+1 vCPU",
                    "adjustment_value": 1,
                    "confidence_change": -0.15,
                    "feedback_source": "user_customization",
                    "trigger": "performance_needs",
                    "priority": "high"
                })
        
        # Updates from feedback
        if feedback_analysis:
            feedback_type = feedback_analysis.get("feedback_type", "")
            
            if feedback_type == "over_provisioned":
                updates.append({
                    "update_id": f"upd_{uuid.uuid4().hex[:8]}",
                    "parameter": "cpu_allocation",
                    "workload_pattern": f"{workload_type}_{architecture}",
                    "adjustment": "-1 vCPU",
                    "adjustment_value": -1,
                    "confidence_change": -0.15,
                    "feedback_source": "user_feedback",
                    "trigger": "over_provisioned",
                    "priority": "high"
                })
                
            elif feedback_type == "under_provisioned":
                updates.append({
                    "update_id": f"upd_{uuid.uuid4().hex[:8]}",
                    "parameter": "cpu_allocation",
                    "workload_pattern": f"{workload_type}_{architecture}",
                    "adjustment": "+2 vCPU",
                    "adjustment_value": 2,
                    "confidence_change": -0.20,
                    "feedback_source": "user_feedback",
                    "trigger": "under_provisioned",
                    "priority": "critical"
                })
                updates.append({
                    "update_id": f"upd_{uuid.uuid4().hex[:8]}",
                    "parameter": "ram_allocation",
                    "workload_pattern": f"{workload_type}_{architecture}",
                    "adjustment": "+4 GB",
                    "adjustment_value": 4,
                    "confidence_change": -0.15,
                    "feedback_source": "user_feedback",
                    "trigger": "under_provisioned",
                    "priority": "critical"
                })
                
            elif feedback_type == "perfect_fit":
                updates.append({
                    "update_id": f"upd_{uuid.uuid4().hex[:8]}",
                    "parameter": "architecture_selection",
                    "workload_pattern": f"{workload_type}_{architecture}",
                    "adjustment": "reinforce",
                    "adjustment_value": 0.10,
                    "confidence_change": 0.10,
                    "feedback_source": "user_feedback",
                    "trigger": "perfect_fit",
                    "priority": "low"
                })
        
        # Updates from performance analysis
        if performance_analysis:
            for gap in performance_analysis.get("performance_gaps", []):
                if gap["metric"] == "cpu":
                    updates.append({
                        "update_id": f"upd_{uuid.uuid4().hex[:8]}",
                        "parameter": "cpu_allocation",
                        "workload_pattern": f"{workload_type}_{architecture}",
                        "adjustment": "increase_baseline",
                        "adjustment_value": 1,
                        "confidence_change": -0.10,
                        "feedback_source": "performance_metrics",
                        "trigger": "high_cpu_utilization",
                        "priority": "high"
                    })
            
            for opp in performance_analysis.get("optimization_opportunities", []):
                if opp["metric"] == "cpu":
                    updates.append({
                        "update_id": f"upd_{uuid.uuid4().hex[:8]}",
                        "parameter": "cpu_allocation",
                        "workload_pattern": f"{workload_type}_{architecture}",
                        "adjustment": "decrease_baseline",
                        "adjustment_value": -1,
                        "confidence_change": 0.05,
                        "feedback_source": "performance_metrics",
                        "trigger": "low_cpu_utilization",
                        "priority": "medium"
                    })
        
        # Updates from cost analysis
        if cost_analysis and cost_analysis.get("adjustment_needed", False):
            variance_percent = cost_analysis.get("variance_percent", 0)
            updates.append({
                "update_id": f"upd_{uuid.uuid4().hex[:8]}",
                "parameter": "pricing_accuracy",
                "workload_pattern": f"{workload_type}_{architecture}",
                "adjustment": "recalibrate" if variance_percent > 0 else "reduce_buffer",
                "adjustment_value": variance_percent / 100,
                "confidence_change": -abs(variance_percent) / 200,
                "feedback_source": "cost_actuals",
                "trigger": "cost_variance",
                "priority": "high" if abs(variance_percent) > 20 else "medium"
            })
        
        # Updates from decision type
        if decision_type == "rejected":
            updates.append({
                "update_id": f"upd_{uuid.uuid4().hex[:8]}",
                "parameter": "architecture_selection",
                "workload_pattern": f"{workload_type}",
                "adjustment": "reduce_confidence",
                "adjustment_value": -0.20,
                "confidence_change": -0.20,
                "feedback_source": "rejection",
                "trigger": "recommendation_rejected",
                "priority": "critical"
            })
        
        return updates
    
    def _apply_learning_updates(self, updates: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Apply learning updates to the model parameters"""
        changes = []
        
        for update in updates:
            parameter = update.get("parameter", "")
            workload_pattern = update.get("workload_pattern", "")
            adjustment_value = update.get("adjustment_value", 0)
            
            if parameter in self.learning_parameters:
                param_config = self.learning_parameters[parameter]
                
                # Record the change
                change = {
                    "update_id": update["update_id"],
                    "parameter": parameter,
                    "workload_pattern": workload_pattern,
                    "previous_value": None,
                    "new_value": None,
                    "change_applied": False,
                    "timestamp": datetime.now().isoformat()
                }
                
                # Apply workload-specific adjustment
                if "workload_adjustments" in param_config:
                    workload_key = workload_pattern.split("_")[0] if "_" in workload_pattern else workload_pattern
                    if workload_key in param_config["workload_adjustments"]:
                        previous = param_config["workload_adjustments"][workload_key]
                        new_value = previous + (adjustment_value * 0.1)  # Apply scaled adjustment
                        param_config["workload_adjustments"][workload_key] = new_value
                        
                        change["previous_value"] = previous
                        change["new_value"] = new_value
                        change["change_applied"] = True
                
                # Update metadata
                param_config["feedback_count"] = param_config.get("feedback_count", 0) + 1
                param_config["last_updated"] = datetime.now().isoformat()
                
                changes.append(change)
                
                if change["change_applied"]:
                    self.stats["model_updates_applied"] += 1
        
        # Store in history
        self.model_updates.extend(changes)
        
        return changes
    
    def _calculate_confidence_adjustments(self, updates: List[Dict[str, Any]],
                                          feedback_analysis: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate overall confidence adjustments"""
        total_confidence_change = 0.0
        adjustment_count = 0
        
        for update in updates:
            confidence_change = update.get("confidence_change", 0)
            total_confidence_change += confidence_change
            adjustment_count += 1
        
        if feedback_analysis:
            total_confidence_change += feedback_analysis.get("confidence_impact", 0)
            adjustment_count += 1
        
        avg_change = total_confidence_change / adjustment_count if adjustment_count > 0 else 0
        
        # Update running average
        self.stats["avg_confidence_change"] = (
            (self.stats["avg_confidence_change"] * (self.stats["total_feedback_processed"] - 1) + avg_change)
            / self.stats["total_feedback_processed"]
        ) if self.stats["total_feedback_processed"] > 0 else avg_change
        
        return {
            "total_confidence_change": total_confidence_change,
            "average_confidence_change": avg_change,
            "adjustment_count": adjustment_count,
            "direction": "positive" if total_confidence_change > 0 else "negative" if total_confidence_change < 0 else "neutral",
            "magnitude": abs(total_confidence_change),
            "impact_level": "high" if abs(total_confidence_change) > 0.2 else "medium" if abs(total_confidence_change) > 0.1 else "low"
        }
    
    def _generate_improvement_insights(self, updates: List[Dict[str, Any]],
                                       changes: List[Dict[str, Any]],
                                       consolidated_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate actionable improvement insights"""
        insights = []
        workload_type = consolidated_data.get("workload_type", "unknown")
        architecture = consolidated_data.get("architecture", "unknown")
        
        # Analyze update patterns
        param_updates = {}
        for update in updates:
            param = update.get("parameter", "")
            if param not in param_updates:
                param_updates[param] = []
            param_updates[param].append(update)
        
        # Generate insights per parameter
        if "cpu_allocation" in param_updates:
            cpu_updates = param_updates["cpu_allocation"]
            directions = [u.get("adjustment_value", 0) for u in cpu_updates]
            avg_direction = sum(directions) / len(directions) if directions else 0
            
            if avg_direction < 0:
                insights.append({
                    "insight_id": f"ins_{uuid.uuid4().hex[:8]}",
                    "category": "resource_optimization",
                    "title": "CPU Over-provisioning Pattern",
                    "description": f"For {workload_type} workloads on {architecture}, CPU is consistently over-provisioned",
                    "recommendation": "Consider reducing base CPU allocation by 1 vCPU for this workload pattern",
                    "expected_impact": "cost_reduction",
                    "confidence": 0.75,
                    "priority": "medium"
                })
            elif avg_direction > 0:
                insights.append({
                    "insight_id": f"ins_{uuid.uuid4().hex[:8]}",
                    "category": "performance_optimization",
                    "title": "CPU Under-provisioning Pattern",
                    "description": f"For {workload_type} workloads on {architecture}, CPU is consistently under-provisioned",
                    "recommendation": "Consider increasing base CPU allocation by 1-2 vCPUs for this workload pattern",
                    "expected_impact": "performance_improvement",
                    "confidence": 0.80,
                    "priority": "high"
                })
        
        if "pricing_accuracy" in param_updates:
            insights.append({
                "insight_id": f"ins_{uuid.uuid4().hex[:8]}",
                "category": "pricing_calibration",
                "title": "Pricing Model Adjustment Needed",
                "description": "Cost estimates are showing variance from actuals",
                "recommendation": "Review pricing model for this architecture type",
                "expected_impact": "accuracy_improvement",
                "confidence": 0.70,
                "priority": "medium"
            })
        
        if "architecture_selection" in param_updates:
            arch_updates = param_updates["architecture_selection"]
            for update in arch_updates:
                if update.get("trigger") == "recommendation_rejected":
                    insights.append({
                        "insight_id": f"ins_{uuid.uuid4().hex[:8]}",
                        "category": "architecture_mapping",
                        "title": "Architecture Selection Review Needed",
                        "description": f"Recommendation for {workload_type} was rejected",
                        "recommendation": "Review workload-to-architecture mapping rules",
                        "expected_impact": "acceptance_rate_improvement",
                        "confidence": 0.85,
                        "priority": "high"
                    })
        
        # Add general insights based on feedback patterns
        if self.stats["negative_feedback"] > self.stats["positive_feedback"]:
            insights.append({
                "insight_id": f"ins_{uuid.uuid4().hex[:8]}",
                "category": "model_health",
                "title": "High Negative Feedback Rate",
                "description": "Negative feedback is exceeding positive feedback",
                "recommendation": "Conduct comprehensive model review and recalibration",
                "expected_impact": "overall_improvement",
                "confidence": 0.90,
                "priority": "critical"
            })
        
        return insights
    
    def _enhance_learning_result(self, decision_id: str, request_id: str,
                                 user_id: str, session_id: str,
                                 signals_analysis: Dict[str, Any],
                                 feedback_analysis: Optional[Dict[str, Any]],
                                 performance_analysis: Optional[Dict[str, Any]],
                                 cost_analysis: Optional[Dict[str, Any]],
                                 learning_updates: List[Dict[str, Any]],
                                 model_changes: List[Dict[str, Any]],
                                 confidence_adjustments: Dict[str, Any],
                                 insights: List[Dict[str, Any]],
                                 processing_time_ms: int,
                                 decision_type: str,
                                 user_satisfaction: Optional[str],
                                 feedback_delay_days: int) -> Dict[str, Any]:
        """Build enhanced learning result"""
        learning_id = f"learn_{int(time.time())}_{uuid.uuid4().hex[:6]}"
        
        return {
            "learning_id": learning_id,
            "decision_id": decision_id,
            "request_id": request_id,
            "user_id": user_id,
            "session_id": session_id,
            "phase": self.phase_name,
            "phase_version": self.phase_version,
            "model_version": self.model_version,
            "status": "completed",
            
            # Analysis results
            "signals_analysis": signals_analysis,
            "feedback_analysis": feedback_analysis,
            "performance_analysis": performance_analysis,
            "cost_analysis": cost_analysis,
            
            # Learning outputs
            "learning_updates": learning_updates,
            "model_changes": model_changes,
            "confidence_adjustments": confidence_adjustments,
            "insights": insights,
            
            # Context
            "decision_context": {
                "decision_type": decision_type,
                "user_satisfaction": user_satisfaction,
                "feedback_delay_days": feedback_delay_days
            },
            
            # Summary statistics
            "learning_summary": {
                "updates_generated": len(learning_updates),
                "changes_applied": sum(1 for c in model_changes if c.get("change_applied", False)),
                "insights_generated": len(insights),
                "high_priority_insights": sum(1 for i in insights if i.get("priority") in ["high", "critical"]),
                "confidence_direction": confidence_adjustments["direction"],
                "overall_impact": self._calculate_overall_impact(learning_updates, insights)
            },
            
            # Current model state
            "model_state": {
                "version": self.model_version,
                "parameters_updated": list(set(u.get("parameter") for u in learning_updates)),
                "total_feedback_processed": self.stats["total_feedback_processed"],
                "positive_feedback_rate": (
                    self.stats["positive_feedback"] / self.stats["total_feedback_processed"]
                ) if self.stats["total_feedback_processed"] > 0 else 0
            },
            
            # Processing metadata
            "processing_metadata": {
                "processing_time_ms": processing_time_ms,
                "timestamp": datetime.now().isoformat(),
                "learning_parameters_count": len(self.learning_parameters)
            },
            
            # No next phase - this is the final phase
            "workflow_complete": True,
            "workflow_summary": {
                "phases_completed": 8,
                "final_phase": self.phase_name,
                "learning_cycle": "complete"
            }
        }
    
    def _calculate_overall_impact(self, updates: List[Dict[str, Any]],
                                  insights: List[Dict[str, Any]]) -> str:
        """Calculate overall impact level"""
        high_priority_updates = sum(1 for u in updates if u.get("priority") in ["high", "critical"])
        critical_insights = sum(1 for i in insights if i.get("priority") == "critical")
        
        if critical_insights > 0 or high_priority_updates > 2:
            return "significant"
        elif high_priority_updates > 0 or len(insights) > 2:
            return "moderate"
        else:
            return "minor"
    
    def _emit_learning_telemetry(self, result: Dict[str, Any], processing_time_ms: int):
        """Emit comprehensive telemetry for learning"""
        learning_id = result["learning_id"]
        summary = result["learning_summary"]
        
        # Emit learning event
        self.telemetry.emit_event(
            title="AI Learning Update Processed",
            text=f"Processed learning feedback with {summary['updates_generated']} updates, "
                 f"{summary['changes_applied']} applied, {summary['insights_generated']} insights",
            tags=[
                f"learning_id:{learning_id}",
                f"model_version:{self.model_version}",
                f"updates:{summary['updates_generated']}",
                f"impact:{summary['overall_impact']}"
            ]
        )
        
        # Emit metrics
        metrics = [
            {
                "name": "ai.model.learning.updates",
                "value": float(summary["updates_generated"]),
                "tags": [f"model_version:{self.model_version}"]
            },
            {
                "name": "ai.model.learning.changes_applied",
                "value": float(summary["changes_applied"]),
                "tags": [f"model_version:{self.model_version}"]
            },
            {
                "name": "ai.model.learning.insights",
                "value": float(summary["insights_generated"]),
                "tags": [f"priority:high" if summary["high_priority_insights"] > 0 else "priority:normal"]
            },
            {
                "name": "phase8.processing_time_ms",
                "value": float(processing_time_ms),
                "tags": []
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
            source="ai.learning.update",
            message={
                "learning_id": learning_id,
                "model_version": self.model_version,
                "updates_generated": summary["updates_generated"],
                "changes_applied": summary["changes_applied"],
                "insights_generated": summary["insights_generated"],
                "confidence_direction": summary["confidence_direction"],
                "overall_impact": summary["overall_impact"],
                "processing_time_ms": processing_time_ms
            },
            tags=["ai_learning", "continuous_improvement", "feedback_driven"],
            level="info"
        )
    
    def _create_error_result(self, decision_id: str, request_id: str,
                            user_id: str, session_id: str,
                            error_message: str, processing_time_ms: int) -> Dict[str, Any]:
        """Create error result for failed processing"""
        return {
            "learning_id": f"learn_error_{int(time.time())}_{uuid.uuid4().hex[:6]}",
            "decision_id": decision_id,
            "request_id": request_id,
            "user_id": user_id,
            "session_id": session_id,
            "phase": self.phase_name,
            "phase_version": self.phase_version,
            "model_version": self.model_version,
            "status": "failed",
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
            title="Phase 8 Learning Processing Failed",
            text=f"Learning feedback processing failed: {error_message}",
            tags=["error", "phase8", "learning"],
            alert_type="error"
        )
        
        self.telemetry.submit_metric(
            name="phase8.errors",
            value=1.0,
            tags=["error_type:processing"]
        )
    
    async def request_feedback(self, deployment_id: str,
                               days_since_deployment: int = 7) -> Dict[str, Any]:
        """
        Request feedback for a deployment (for scheduled follow-ups)
        
        This would be called by a scheduled job after deployment
        """
        return {
            "feedback_request_id": f"fbr_{uuid.uuid4().hex[:8]}",
            "deployment_id": deployment_id,
            "days_since_deployment": days_since_deployment,
            "feedback_categories": list(self.feedback_categories.keys()),
            "suggested_questions": [
                "How would you rate the resource allocation?",
                "Was the cost estimate accurate?",
                "Did the performance meet expectations?",
                "Would you use the same architecture again?"
            ],
            "timestamp": datetime.now().isoformat()
        }
    
    def get_learning_parameters(self) -> Dict[str, Any]:
        """Get current learning parameters state"""
        return {
            "model_version": self.model_version,
            "parameters": self.learning_parameters,
            "last_updates": self.model_updates[-10:] if self.model_updates else [],
            "statistics": self.stats
        }
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get current phase statistics"""
        return {
            "phase_name": self.phase_name,
            "phase_version": self.phase_version,
            "model_version": self.model_version,
            "statistics": self.stats,
            "feedback_categories": list(self.feedback_categories.keys()),
            "parameters_tracked": list(self.learning_parameters.keys())
        }
    
    def flush_buffers(self):
        """Flush telemetry buffers"""
        self.telemetry.flush_buffers()
