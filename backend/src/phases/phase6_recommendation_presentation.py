"""
Phase 6: Recommendation Presentation
Production-grade implementation with structured presentation data
"""

import time
import logging
import json
from datetime import datetime
from typing import Dict, Any, Optional, List
import uuid
import random

from ..core.gemini_client import GeminiClient
from ..telemetry.datadog_client import TelemetryClient, TelemetryConfig, TelemetryMode

logger = logging.getLogger(__name__)

class RecommendationPresentationPhase:
    """Complete Phase 6: Recommendation Presentation"""
    
    def __init__(self, telemetry_config: Optional[TelemetryConfig] = None):
        self.phase_name = "recommendation_presentation"
        self.phase_version = "1.0.0"
        
        # Initialize clients
        self.gemini = GeminiClient()
        self.telemetry = TelemetryClient(telemetry_config)
        
        # Presentation templates
        self.presentation_templates = self._initialize_templates()
        
        # Visual component generators
        self.visual_generators = self._initialize_visual_generators()
        
        # Statistics
        self.stats = {
            "total_presentations": 0,
            "executive_presentations": 0,
            "detailed_presentations": 0,
            "technical_presentations": 0,
            "total_processing_time_ms": 0,
            "avg_presentation_quality": 0.0
        }
        
        logger.info(f"✅ Phase 6 initialized: {self.phase_name} v{self.phase_version}")
        logger.info(f"🎨 Presentation templates: {len(self.presentation_templates)}")
    
    def _initialize_templates(self) -> Dict[str, Dict[str, Any]]:
        """Initialize presentation templates"""
        return {
            "executive": {
                "name": "Executive Summary",
                "audience": "business_decision_makers",
                "focus": ["cost", "timeline", "risk", "roi"],
                "depth": "high_level",
                "visuals": ["cost_summary", "timeline", "risk_matrix"]
            },
            "detailed": {
                "name": "Detailed Recommendation",
                "audience": "technical_managers",
                "focus": ["architecture", "specifications", "performance", "scalability"],
                "depth": "comprehensive",
                "visuals": ["architecture_diagram", "spec_table", "performance_chart", "scalability_graph"]
            },
            "technical": {
                "name": "Technical Specification",
                "audience": "engineers_devops",
                "focus": ["configuration", "deployment", "monitoring", "security"],
                "depth": "granular",
                "visuals": ["configuration_table", "deployment_steps", "monitoring_setup", "security_matrix"]
            }
        }
    
    def _initialize_visual_generators(self) -> Dict[str, callable]:
        """Initialize visual component generators"""
        return {
            "cost_summary": self._generate_cost_summary,
            "architecture_diagram": self._generate_architecture_diagram,
            "spec_table": self._generate_specification_table,
            "performance_chart": self._generate_performance_chart,
            "scalability_graph": self._generate_scalability_graph,
            "timeline": self._generate_timeline,
            "risk_matrix": self._generate_risk_matrix,
            "comparison_table": self._generate_comparison_table,
            "configuration_table": self._generate_configuration_table,
            "deployment_steps": self._generate_deployment_steps,
            "monitoring_setup": self._generate_monitoring_setup,
            "security_matrix": self._generate_security_matrix
        }
    
    async def process(self, phase1_result: Dict[str, Any], 
                     phase2_result: Dict[str, Any],
                     phase3_result: Dict[str, Any],
                     phase4_result: Dict[str, Any],
                     phase5_result: Dict[str, Any],
                     presentation_type: str = "detailed",
                     user_id: Optional[str] = None,
                     session_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Create presentation-ready recommendation
        
        Args:
            phase1_result: Complete output from Phase 1
            phase2_result: Complete output from Phase 2
            phase3_result: Complete output from Phase 3
            phase4_result: Complete output from Phase 4
            phase5_result: Complete output from Phase 5
            presentation_type: executive/detailed/technical
            user_id: User identifier
            session_id: Session identifier
            
        Returns:
            Dict containing presentation-ready recommendation
        """
        start_time = time.time()
        
        # Validate inputs
        self._validate_inputs(phase1_result, phase2_result, phase3_result, phase4_result, phase5_result)
        
        # Validate presentation type
        if presentation_type not in self.presentation_templates:
            presentation_type = "detailed"
        
        self.stats["total_presentations"] += 1
        self.stats[f"{presentation_type}_presentations"] += 1
        
        # Extract data from all phases
        intent_analysis = phase1_result["intent_analysis"]
        business_context = phase1_result.get("business_context", {})
        architecture_analysis = phase2_result["architecture_analysis"]
        specification_analysis = phase3_result["specification_analysis"]
        configuration = phase3_result["configuration"]
        pricing_result = phase4_result
        tradeoff_analysis = phase5_result
        
        # Use IDs from previous phases
        request_id = phase1_result.get("request_id", f"req_{int(time.time())}_{uuid.uuid4().hex[:6]}")
        user_id = user_id or phase1_result.get("user_id", f"user_{uuid.uuid4().hex[:8]}")
        session_id = session_id or phase1_result.get("session_id", f"session_{uuid.uuid4().hex[:8]}")
        
        try:
            logger.info(f"🎯 Creating {presentation_type} presentation for {intent_analysis['workload_type']}")
            
            # Step 1: Prepare consolidated data
            consolidated_data = self._consolidate_phase_data(
                phase1_result, phase2_result, phase3_result, phase4_result, phase5_result
            )
            
            # Step 2: Generate presentation based on type
            presentation_method = "structured"
            try:
                presentation = self._generate_presentation(
                    consolidated_data, presentation_type
                )
            except Exception as e:
                logger.warning(f"Presentation generation failed, using template: {e}")
                presentation = self._generate_template_presentation(
                    consolidated_data, presentation_type
                )
                presentation_method = "template_fallback"
            
            # Step 3: Generate visual components
            visual_components = self._generate_visual_components(
                consolidated_data, presentation_type
            )
            
            # Step 4: Calculate processing time
            processing_time_ms = int((time.time() - start_time) * 1000)
            
            # Step 5: Enhance with metadata
            enhanced_result = self._enhance_presentation_result(
                presentation,
                visual_components,
                consolidated_data,
                presentation_type,
                presentation_method,
                phase1_result,
                phase2_result,
                phase3_result,
                phase4_result,
                phase5_result,
                processing_time_ms=processing_time_ms,
                user_id=user_id,
                session_id=session_id,
                request_id=request_id
            )
            
            # Step 6: Update statistics
            presentation_quality = self._calculate_presentation_quality(presentation, visual_components)
            self._update_statistics(presentation_quality, processing_time_ms)
            
            # Step 7: Emit telemetry
            self._emit_success_telemetry(enhanced_result, processing_time_ms)
            
            logger.info(f"✅ Presentation created: {presentation_type}")
            logger.info(f"   Visual components: {len(visual_components)}")
            logger.info(f"   Method: {presentation_method}")
            logger.info(f"   Time: {processing_time_ms}ms")
            
            return enhanced_result
            
        except Exception as e:
            # Handle failures gracefully
            processing_time_ms = int((time.time() - start_time) * 1000)
            
            error_result = self._create_error_result(
                user_id, session_id, request_id, 
                phase1_result, phase2_result, phase3_result,
                phase4_result, phase5_result,
                error_message=str(e), processing_time_ms=processing_time_ms
            )
            
            self._emit_error_telemetry(error_result, str(e))
            
            logger.error(f"❌ Presentation creation failed: {e}")
            raise
    
    def _validate_inputs(self, *phase_results):
        """Validate all input phases"""
        required_phases = [
            ("Phase 1", phase_results[0], "intent_analysis"),
            ("Phase 2", phase_results[1], "architecture_analysis"),
            ("Phase 3", phase_results[2], "specification_analysis"),
            ("Phase 4", phase_results[3], "primary_price"),
            ("Phase 5", phase_results[4], "qualitative_analysis")
        ]
        
        for phase_name, phase_data, required_field in required_phases:
            if not phase_data or required_field not in phase_data:
                raise ValueError(f"Invalid {phase_name} result. Missing {required_field}")
    
    def _consolidate_phase_data(self, *phase_results) -> Dict[str, Any]:
        """Consolidate data from all phases with resilient field access"""
        phase1, phase2, phase3, phase4, phase5 = phase_results
        
        # Helper to safely get nested values
        def safe_get(d, *keys, default=None):
            current = d
            for key in keys:
                if isinstance(current, dict):
                    current = current.get(key, default)
                else:
                    return default
                if current is None:
                    return default
            return current if current is not None else default
        
        # Extract intent analysis with defaults
        intent = phase1.get("intent_analysis", {})
        arch = phase2.get("architecture_analysis", {})
        spec = phase3.get("specification_analysis", {})
        config = phase3.get("configuration", {})
        primary_price = phase4.get("primary_price", {})
        pricing_acc = phase4.get("pricing_accuracy", {})
        qual = phase5.get("qualitative_analysis", {})
        quant = phase5.get("quantitative_analysis", {})
        
        return {
            "workload": {
                "type": intent.get("workload_type", "unknown"),
                "description": intent.get("raw_input", "No description provided"),
                "scale": intent.get("scale", {"monthly_users": 0, "estimated_rps": 0}),
                "requirements": intent.get("requirements", {}),
                "constraints": intent.get("constraints", {}),
                "business_context": phase1.get("business_context", {})
            },
            "architecture": {
                "primary": arch.get("primary_architecture", "unknown"),
                "confidence": arch.get("confidence", 0.5),
                "reasoning": arch.get("reasoning", "No reasoning provided"),
                "alternatives": arch.get("alternatives", []),
                "selection_method": arch.get("selection_method", "unknown")
            },
            "specification": {
                "machine_type": spec.get("exact_type", spec.get("machine_type", "unknown")),
                "machine_family": spec.get("machine_family", "general"),
                "machine_size": spec.get("machine_size", "medium"),
                "cpu": spec.get("cpu", 4),
                "ram": spec.get("ram", 8),
                "configuration": config,
                "selection_method": spec.get("selection_method", "unknown")
            },
            "pricing": {
                "primary_price": primary_price.get("total_monthly_usd", 0.0),
                "price_accuracy": pricing_acc.get("estimated_accuracy", 0.5),
                "alternative_prices": phase4.get("alternative_prices", {}),
                "savings_analysis": phase4.get("savings_analysis", {}),
                "calculation_method": primary_price.get("calculation_method", "unknown")
            },
            "analysis": {
                "executive_summary": qual.get("executive_summary", qual.get("summary", "Analysis summary not available")),
                "recommendation_strength": qual.get("recommendation_strength", "medium"),
                "advantages": qual.get("primary_advantages", qual.get("key_strengths", [])),
                "risks": qual.get("primary_risks", qual.get("key_weaknesses", [])),
                "tradeoff_matrix": qual.get("tradeoff_matrix", []),
                "decision_factors": qual.get("decision_factors", []),
                "risk_assessment": qual.get("risk_assessment", {}),
                "next_steps": qual.get("next_step_recommendations", []),
                "quantitative_scores": quant.get("tradeoff_scores", {})
            },
            "metadata": {
                "user_id": phase1.get("user_id", "unknown"),
                "session_id": phase1.get("session_id", "unknown"),
                "request_id": phase1.get("request_id", "unknown"),
                "timestamp": datetime.utcnow().isoformat()
            }
        }
    
    def _generate_presentation(self, consolidated_data: Dict[str, Any],
                             presentation_type: str) -> Dict[str, Any]:
        """Generate presentation based on type"""
        template = self.presentation_templates[presentation_type]
        
        if presentation_type == "executive":
            return self._generate_executive_presentation(consolidated_data, template)
        elif presentation_type == "detailed":
            return self._generate_detailed_presentation(consolidated_data, template)
        elif presentation_type == "technical":
            return self._generate_technical_presentation(consolidated_data, template)
        else:
            return self._generate_detailed_presentation(consolidated_data, template)
    
    def _generate_executive_presentation(self, data: Dict[str, Any],
                                        template: Dict[str, Any]) -> Dict[str, Any]:
        """Generate executive presentation for business decision makers"""
        
        workload = data["workload"]
        architecture = data["architecture"]
        pricing = data["pricing"]
        analysis = data["analysis"]
        
        # Calculate ROI
        monthly_cost = pricing["primary_price"]
        estimated_savings = pricing["savings_analysis"].get("potential_monthly_savings", 0)
        roi_months = self._calculate_roi_months(monthly_cost, estimated_savings)
        
        # Determine priority level
        priority = self._determine_priority(workload, analysis)
        
        presentation = {
            "title": f"Infrastructure Recommendation: {workload['type'].replace('_', ' ').title()}",
            "subtitle": f"Designed for {workload['scale']['monthly_users']:,} monthly users",
            "audience": template["audience"],
            "presentation_type": "executive",
            
            "executive_summary": {
                "one_liner": f"Recommend {architecture['primary']} architecture at ${monthly_cost:.2f}/month",
                "key_benefits": [
                    f"Optimized for {workload['requirements']['latency']} latency requirements",
                    f"Matches {workload['constraints']['team_experience']} team expertise",
                    f"Within {workload['constraints']['budget_sensitivity']} budget constraints"
                ],
                "expected_outcomes": [
                    f"Handle {workload['scale']['monthly_users']:,} users efficiently",
                    f"Provide {workload['requirements']['availability']} availability",
                    f"Scale to {workload['scale']['estimated_rps']} requests/second"
                ]
            },
            
            "business_case": {
                "investment": {
                    "monthly_cost": monthly_cost,
                    "estimated_setup_cost": monthly_cost * 2,  # 2 months setup cost
                    "annual_cost": monthly_cost * 12,
                    "cost_comparison": f"${estimated_savings:.2f}/month savings vs alternatives"
                },
                "returns": {
                    "roi_months": roi_months,
                    "time_to_value": "2-4 weeks",
                    "efficiency_gains": "30-50% reduction in operational overhead",
                    "risk_reduction": "Built-in cloud reliability and scalability"
                },
                "alignment": {
                    "budget": f"Aligns with {workload['constraints']['budget_sensitivity']} budget sensitivity",
                    "timeline": f"Supports {workload['constraints']['time_to_market']} deployment",
                    "strategy": "Cloud-first, scalable architecture"
                }
            },
            
            "risk_assessment": {
                "overall_risk": analysis["risk_assessment"]["overall_risk"],
                "key_risks": analysis["risk_assessment"]["primary_risk_factors"][:3],
                "mitigation": analysis["risk_assessment"]["mitigation_strategies"][:2],
                "risk_reward": "Favorable" if analysis["recommendation_strength"] > 70 else "Moderate"
            },
            
            "recommendation": {
                "strength": f"{analysis['recommendation_strength']}/100",
                "confidence": f"{architecture['confidence']:.0%}",
                "priority": priority,
                "timeline": self._generate_implementation_timeline(workload, architecture),
                "next_steps": analysis["next_steps"][:3]
            },
            
            "visual_highlights": {
                "cost_summary": f"${monthly_cost:.2f}/month",
                "savings_potential": f"${estimated_savings:.2f}/month vs alternatives",
                "architecture": architecture["primary"].title(),
                "timeline": f"{roi_months} month ROI"
            }
        }
        
        return presentation
    
    def _calculate_roi_months(self, monthly_cost: float, monthly_savings: float) -> int:
        """Calculate ROI in months"""
        if monthly_savings <= 0:
            return 12
        
        # Assume initial setup cost of 2x monthly cost
        setup_cost = monthly_cost * 2
        roi_months = setup_cost / monthly_savings
        
        return min(max(int(roi_months), 3), 24)
    
    def _determine_priority(self, workload: Dict[str, Any], analysis: Dict[str, Any]) -> str:
        """Determine implementation priority"""
        recommendation_strength = analysis["recommendation_strength"]
        time_to_market = workload["constraints"]["time_to_market"]
        
        if recommendation_strength >= 85:
            if time_to_market == "immediate":
                return "critical"
            else:
                return "high"
        elif recommendation_strength >= 70:
            return "medium"
        else:
            return "low"
    
    def _generate_implementation_timeline(self, workload: Dict[str, Any],
                                         architecture: Dict[str, Any]) -> Dict[str, Any]:
        """Generate implementation timeline"""
        
        # Base timelines by architecture
        base_timelines = {
            "serverless": {"planning": 1, "implementation": 2, "testing": 1, "deployment": 1},
            "containers": {"planning": 2, "implementation": 3, "testing": 2, "deployment": 1},
            "virtual_machines": {"planning": 1, "implementation": 2, "testing": 1, "deployment": 1}
        }
        
        base = base_timelines.get(architecture["primary"], {"planning": 2, "implementation": 3, "testing": 2, "deployment": 1})
        
        # Adjust for team experience
        team_exp = workload["constraints"]["team_experience"]
        if team_exp in ["beginner", "junior"]:
            base["implementation"] += 1
            base["testing"] += 1
        elif team_exp in ["expert"]:
            base["implementation"] = max(1, base["implementation"] - 1)
        
        # Adjust for time to market
        timeline = workload["constraints"]["time_to_market"]
        if timeline == "immediate":
            # Compress timeline
            for phase in base:
                base[phase] = max(1, int(base[phase] * 0.7))
        elif timeline == "1_week":
            # Very compressed
            for phase in base:
                base[phase] = max(1, int(base[phase] * 0.5))
        
        total_weeks = sum(base.values())
        
        return {
            "phases": base,
            "total_weeks": total_weeks,
            "estimated_start": "Immediately",
            "estimated_completion": f"{total_weeks} weeks from start",
            "critical_path": "Implementation → Testing"
        }
    
    def _generate_detailed_presentation(self, data: Dict[str, Any],
                                      template: Dict[str, Any]) -> Dict[str, Any]:
        """Generate detailed presentation for technical managers"""
        
        workload = data["workload"]
        architecture = data["architecture"]
        specification = data["specification"]
        pricing = data["pricing"]
        analysis = data["analysis"]
        
        presentation = {
            "title": f"Technical Recommendation: {workload['type'].replace('_', ' ').title()} on {architecture['primary'].title()}",
            "subtitle": f"Comprehensive analysis for {workload['scale']['monthly_users']:,} monthly users",
            "audience": template["audience"],
            "presentation_type": "detailed",
            
            "overview": {
                "problem_statement": workload["description"],
                "solution_summary": f"{architecture['primary'].title()} architecture with {specification['machine_type']}",
                "key_objectives": [
                    f"Achieve {workload['requirements']['latency']} latency",
                    f"Ensure {workload['requirements']['availability']} availability",
                    f"Support {workload['scale']['estimated_rps']} RPS",
                    f"Align with {workload['constraints']['budget_sensitivity']} budget"
                ]
            },
            
            "architecture_details": {
                "selected_architecture": {
                    "type": architecture["primary"],
                    "confidence": f"{architecture['confidence']:.0%}",
                    "reasoning": architecture["reasoning"],
                    "strengths": analysis["advantages"][:4],
                    "considerations": analysis["risks"][:3]
                },
                "alternatives": self._format_alternatives(data),
                "decision_factors": analysis["decision_factors"]
            },
            
            "technical_specifications": {
                "compute": {
                    "machine_type": specification["machine_type"],
                    "cpu": specification["cpu"],
                    "ram_gb": specification["ram"],
                    "family": specification["machine_family"],
                    "size": specification["machine_size"]
                },
                "configuration": specification["configuration"],
                "performance_characteristics": {
                    "estimated_rps_capacity": self._estimate_rps_capacity(specification, workload),
                    "concurrent_users": self._estimate_concurrent_users(specification, workload),
                    "latency_profile": self._determine_latency_profile(workload, architecture),
                    "scaling_capability": self._assess_scaling_capacity(architecture, workload)
                }
            },
            
            "cost_analysis": {
                "breakdown": {
                    "compute": f"${pricing['primary_price'] * 0.6:.2f}/month",
                    "storage": f"${pricing['primary_price'] * 0.2:.2f}/month",
                    "networking": f"${pricing['primary_price'] * 0.1:.2f}/month",
                    "services": f"${pricing['primary_price'] * 0.1:.2f}/month",
                    "total": f"${pricing['primary_price']:.2f}/month"
                },
                "comparison": self._format_price_comparison(pricing),
                "optimization_opportunities": pricing["savings_analysis"].get("optimization_opportunities", []),
                "accuracy": f"{pricing['price_accuracy']:.1%} estimated accuracy"
            },
            
            "implementation_plan": {
                "phases": [
                    {"phase": "Planning & Design", "duration": "1-2 weeks", "activities": ["Architecture review", "Capacity planning", "Security assessment"]},
                    {"phase": "Environment Setup", "duration": "1 week", "activities": ["Cloud account configuration", "Networking setup", "Security policies"]},
                    {"phase": "Development & Configuration", "duration": "2-3 weeks", "activities": ["Infrastructure as Code", "CI/CD pipeline", "Monitoring setup"]},
                    {"phase": "Testing & Validation", "duration": "1-2 weeks", "activities": ["Load testing", "Security testing", "Disaster recovery testing"]},
                    {"phase": "Deployment & Go-Live", "duration": "1 week", "activities": ["Phased rollout", "Monitoring activation", "Documentation"]}
                ],
                "team_requirements": {
                    "roles": ["Cloud Architect", "DevOps Engineer", "Security Specialist"],
                    "experience_level": workload["constraints"]["team_experience"],
                    "training_needs": self._identify_training_needs(architecture, workload)
                }
            },
            
            "risk_mitigation": {
                "identified_risks": analysis["risk_assessment"]["primary_risk_factors"],
                "mitigation_strategies": analysis["risk_assessment"]["mitigation_strategies"],
                "monitoring_requirements": self._define_monitoring_requirements(workload, architecture),
                "contingency_plan": self._create_contingency_plan(architecture, workload)
            },
            
            "success_metrics": {
                "performance": ["Latency < 100ms p95", "Availability > 99.9%", "Error rate < 0.1%"],
                "cost": ["Monthly spend within budget", "Cost per user < $0.10", "Infrastructure efficiency > 70%"],
                "operational": ["Deployment frequency > weekly", "Mean time to recovery < 1 hour", "Automation coverage > 80%"]
            }
        }
        
        return presentation
    
    def _format_alternatives(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Format alternative architectures for presentation"""
        alternatives = []
        
        architecture = data["architecture"]
        pricing = data["pricing"]
        
        for alt_arch, alt_price in pricing["alternative_prices"].items():
            if alt_arch != architecture["primary"]:
                primary_price = pricing["primary_price"]
                price_diff = alt_price - primary_price
                price_diff_percent = (price_diff / primary_price * 100) if primary_price > 0 else 0
                
                alternatives.append({
                    "architecture": alt_arch,
                    "price": alt_price,
                    "price_difference": f"{'+' if price_diff > 0 else ''}{price_diff_percent:.1f}%",
                    "when_to_consider": self._get_alternative_reasoning(alt_arch, data["workload"]),
                    "key_differences": self._get_architecture_differences(architecture["primary"], alt_arch)
                })
        
        return alternatives
    
    def _get_alternative_reasoning(self, architecture: str, workload: Dict[str, Any]) -> str:
        """Get reasoning for considering alternative"""
        reasonings = {
            "serverless": "Consider for variable traffic, minimal ops, rapid deployment",
            "containers": "Consider for portability, Kubernetes ecosystem, fine-grained control",
            "virtual_machines": "Consider for legacy apps, specific OS requirements, full control"
        }
        
        base_reason = reasonings.get(architecture, "Consider based on specific requirements")
        
        # Add workload-specific context
        if workload["type"] == "ml_inference" and architecture == "containers":
            base_reason += ", GPU access requirements"
        elif workload["requirements"]["latency"] == "ultra_low" and architecture == "virtual_machines":
            base_reason += ", predictable performance needs"
        
        return base_reason
    
    def _get_architecture_differences(self, primary: str, alternative: str) -> List[str]:
        """Get key differences between architectures"""
        differences = {
            ("serverless", "containers"): [
                "Automatic vs manual scaling",
                "Higher vs lower operational overhead",
                "Event-driven vs always-on",
                "Limited vs full runtime control"
            ],
            ("serverless", "virtual_machines"): [
                "No infrastructure management vs full control",
                "Pay-per-use vs reserved capacity pricing",
                "Rapid deployment vs longer setup",
                "Vendor-specific vs portable"
            ],
            ("containers", "virtual_machines"): [
                "Application vs OS isolation",
                "Kubernetes ecosystem vs traditional management",
                "Faster deployment vs longer provisioning",
                "Resource efficiency vs resource overhead"
            ]
        }
        
        key = (primary, alternative) if (primary, alternative) in differences else (alternative, primary)
        return differences.get(key, ["Different architectural approaches"])
    
    def _estimate_rps_capacity(self, specification: Dict[str, Any], workload: Dict[str, Any]) -> Dict[str, Any]:
        """Estimate RPS capacity"""
        cpu = specification["cpu"]
        workload_type = workload["type"]
        
        # Base capacity per CPU core by workload type
        base_capacities = {
            "api_backend": 50,
            "web_app": 30,
            "data_processing": 10,
            "ml_inference": 5,
            "batch_processing": 20,
            "realtime_streaming": 40,
            "mobile_backend": 40,
            "gaming_server": 20
        }
        
        base_rps = base_capacities.get(workload_type, 25)
        estimated = cpu * base_rps
        
        return {
            "conservative": int(estimated * 0.7),
            "optimal": estimated,
            "maximum": int(estimated * 1.3),
            "recommended_max": int(estimated * 0.8)  # 80% utilization
        }
    
    def _estimate_concurrent_users(self, specification: Dict[str, Any], workload: Dict[str, Any]) -> Dict[str, Any]:
        """Estimate concurrent user capacity"""
        cpu = specification["cpu"]
        workload_type = workload["type"]
        
        users_per_cpu = {
            "api_backend": 1000,
            "web_app": 500,
            "data_processing": 100,
            "ml_inference": 50,
            "batch_processing": 200,
            "realtime_streaming": 800,
            "mobile_backend": 600,
            "gaming_server": 200
        }
        
        base_users = users_per_cpu.get(workload_type, 300)
        estimated = cpu * base_users
        
        return {
            "concurrent_users": estimated,
            "recommended_max": int(estimated * 0.7),  # 70% utilization
            "peak_capacity": int(estimated * 1.5)
        }
    
    def _determine_latency_profile(self, workload: Dict[str, Any], architecture: Dict[str, Any]) -> Dict[str, Any]:
        """Determine latency profile"""
        latency_req = workload["requirements"]["latency"]
        arch_type = architecture["primary"]
        
        profiles = {
            "ultra_low": {"p50": "1-5ms", "p95": "5-10ms", "p99": "10-20ms"},
            "low": {"p50": "10-50ms", "p95": "50-100ms", "p99": "100-200ms"},
            "medium": {"p50": "50-100ms", "p95": "100-200ms", "p99": "200-500ms"},
            "high": {"p50": "100-500ms", "p95": "500-1000ms", "p99": "1000-2000ms"}
        }
        
        base_profile = profiles.get(latency_req, profiles["medium"])
        
        # Adjust for architecture
        if arch_type == "serverless" and latency_req in ["ultra_low", "low"]:
            # Add cold start consideration
            return {
                **base_profile,
                "cold_start": "100-1000ms (occasional)",
                "note": "Cold starts may affect latency for infrequent requests"
            }
        elif arch_type == "virtual_machines" and latency_req in ["ultra_low", "low"]:
            return {
                **base_profile,
                "note": "Predictable performance, no cold starts"
            }
        else:
            return base_profile
    
    def _assess_scaling_capacity(self, architecture: Dict[str, Any], workload: Dict[str, Any]) -> Dict[str, Any]:
        """Assess scaling capability"""
        arch_type = architecture["primary"]
        traffic_pattern = workload["scale"]["traffic_pattern"]
        
        scaling_profiles = {
            "serverless": {
                "scale_out": "Seconds",
                "scale_in": "Minutes",
                "max_scale": "Virtually unlimited",
                "granularity": "Per request",
                "automation": "Fully automatic"
            },
            "containers": {
                "scale_out": "Minutes",
                "scale_in": "Minutes",
                "max_scale": "Thousands of pods",
                "granularity": "Per pod/replica",
                "automation": "Configurable automatic"
            },
            "virtual_machines": {
                "scale_out": "Minutes to hours",
                "scale_in": "Minutes to hours",
                "max_scale": "Hundreds of instances",
                "granularity": "Per instance",
                "automation": "Manual or scheduled"
            }
        }
        
        base_profile = scaling_profiles.get(arch_type, scaling_profiles["containers"])
        
        # Add traffic pattern considerations
        if traffic_pattern == "bursty" and arch_type == "serverless":
            base_profile["strength"] = "Excellent for bursty traffic"
        elif traffic_pattern == "steady" and arch_type == "virtual_machines":
            base_profile["strength"] = "Cost-effective for steady traffic"
        
        return base_profile
    
    def _format_price_comparison(self, pricing: Dict[str, Any]) -> Dict[str, Any]:
        """Format price comparison data"""
        primary_price = pricing["primary_price"]
        alternative_prices = pricing["alternative_prices"]
        
        comparisons = []
        for arch, price in alternative_prices.items():
            if price > 0:
                diff = price - primary_price
                diff_percent = (diff / primary_price * 100) if primary_price > 0 else 0
                
                comparisons.append({
                    "architecture": arch,
                    "price": price,
                    "difference": f"{'+' if diff > 0 else ''}${diff:.2f}",
                    "percentage": f"{'+' if diff > 0 else ''}{diff_percent:.1f}%",
                    "comparison": "More expensive" if diff > 0 else "Cheaper"
                })
        
        # Find best alternative
        if comparisons:
            best_alt = min(comparisons, key=lambda x: x["price"])
        else:
            best_alt = None
        
        return {
            "comparisons": comparisons,
            "best_alternative": best_alt,
            "primary_is_cheapest": all(c["price"] >= primary_price for c in comparisons) if comparisons else True
        }
    
    def _identify_training_needs(self, architecture: Dict[str, Any], workload: Dict[str, Any]) -> List[str]:
        """Identify training needs based on architecture and team"""
        arch_type = architecture["primary"]
        team_exp = workload["constraints"]["team_experience"]
        
        training_needs = []
        
        if arch_type == "serverless":
            if team_exp in ["beginner", "junior"]:
                training_needs.append("Serverless concepts and best practices")
                training_needs.append("Cloud Run/Cloud Functions specific training")
            training_needs.append("Event-driven architecture patterns")
        
        elif arch_type == "containers":
            if team_exp in ["beginner", "junior", "intermediate"]:
                training_needs.append("Kubernetes fundamentals")
                training_needs.append("Container best practices")
            training_needs.append("GKE-specific features and operations")
        
        elif arch_type == "virtual_machines":
            if team_exp in ["beginner", "junior"]:
                training_needs.append("Cloud infrastructure fundamentals")
            training_needs.append("GCP Compute Engine operations")
        
        # Add security training for all
        training_needs.append("Cloud security best practices")
        
        return training_needs
    
    def _define_monitoring_requirements(self, workload: Dict[str, Any], architecture: Dict[str, Any]) -> Dict[str, Any]:
        """Define monitoring requirements"""
        availability = workload["requirements"]["availability"]
        arch_type = architecture["primary"]
        
        requirements = {
            "metrics": [
                "CPU/Memory utilization",
                "Request latency (p50, p95, p99)",
                "Error rates",
                "Cost metrics"
            ],
            "alerts": [
                "High error rate (>1%)",
                "High latency (> SLA)",
                "Cost exceeding budget",
                "Infrastructure failures"
            ],
            "dashboards": [
                "Performance overview",
                "Cost analysis",
                "User experience",
                "System health"
            ]
        }
        
        if availability == "critical":
            requirements["metrics"].append("Availability SLI/SLO")
            requirements["alerts"].append("Availability below 99.9%")
        
        if arch_type == "serverless":
            requirements["metrics"].append("Cold start frequency")
            requirements["metrics"].append("Concurrent executions")
        
        return requirements
    
    def _create_contingency_plan(self, architecture: Dict[str, Any], workload: Dict[str, Any]) -> Dict[str, Any]:
        """Create contingency plan"""
        arch_type = architecture["primary"]
        
        plans = {
            "serverless": {
                "failure_scenarios": ["Provider outage", "Cold start storms", "Cost overruns"],
                "mitigations": ["Multi-region deployment", "Warm-up strategies", "Budget alerts"],
                "fallback": "Switch to container-based deployment",
                "recovery_time": "Minutes to hours"
            },
            "containers": {
                "failure_scenarios": ["Cluster failures", "Node failures", "Image vulnerabilities"],
                "mitigations": ["Multi-zone deployment", "Auto-scaling", "Security scanning"],
                "fallback": "Manual VM deployment",
                "recovery_time": "Hours"
            },
            "virtual_machines": {
                "failure_scenarios": ["Instance failures", "Zone outages", "Storage failures"],
                "mitigations": ["Instance groups", "Persistent disks", "Backup strategies"],
                "fallback": "Manual recovery or cloud migration",
                "recovery_time": "Hours to days"
            }
        }
        
        base_plan = plans.get(arch_type, plans["containers"])
        
        # Add workload-specific considerations
        if workload["requirements"]["availability"] == "critical":
            base_plan["mitigations"].append("Multi-region disaster recovery")
            base_plan["recovery_time"] = "Minutes"
        
        return base_plan
    
    def _generate_technical_presentation(self, data: Dict[str, Any],
                                       template: Dict[str, Any]) -> Dict[str, Any]:
        """Generate technical presentation for engineers"""
        
        workload = data["workload"]
        architecture = data["architecture"]
        specification = data["specification"]
        pricing = data["pricing"]
        analysis = data["analysis"]
        
        presentation = {
            "title": f"Technical Implementation Specification: {workload['type'].replace('_', ' ').title()}",
            "subtitle": f"{architecture['primary'].title()} on {specification['machine_type']}",
            "audience": template["audience"],
            "presentation_type": "technical",
            
            "implementation_specification": {
                "infrastructure_as_code": self._generate_terraform_spec(data),
                "configuration_management": self._generate_configuration_spec(data),
                "deployment_pipeline": self._generate_deployment_spec(data),
                "monitoring_setup": self._generate_monitoring_spec(data)
            },
            
            "technical_details": {
                "network_configuration": self._generate_network_spec(data),
                "security_configuration": self._generate_security_spec(data),
                "storage_configuration": self._generate_storage_spec(data),
                "scaling_configuration": self._generate_scaling_spec(data)
            },
            
            "operational_procedures": {
                "deployment": self._generate_deployment_procedures(data),
                "monitoring": self._generate_monitoring_procedures(data),
                "maintenance": self._generate_maintenance_procedures(data),
                "troubleshooting": self._generate_troubleshooting_guide(data)
            },
            
            "performance_characteristics": {
                "benchmarks": self._generate_benchmarks(data),
                "capacity_planning": self._generate_capacity_planning(data),
                "load_testing": self._generate_load_testing_plan(data),
                "optimization_guidelines": self._generate_optimization_guidelines(data)
            },
            
            "cost_optimization": {
                "cost_drivers": self._identify_cost_drivers(data),
                "optimization_techniques": self._list_optimization_techniques(data),
                "monitoring_metrics": self._list_cost_metrics(data),
                "budget_controls": self._define_budget_controls(data)
            },
            
            "compliance_security": {
                "security_controls": self._list_security_controls(data),
                "compliance_requirements": self._list_compliance_requirements(data),
                "audit_logging": self._define_audit_logging(data),
                "incident_response": self._define_incident_response(data)
            }
        }
        
        return presentation
    
    def _generate_terraform_spec(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate Terraform specification"""
        architecture = data["architecture"]["primary"]
        specification = data["specification"]
        
        templates = {
            "serverless": {
                "main_tf": "terraform/google/cloud_run",
                "variables": ["project_id", "region", "service_name", "image"],
                "outputs": ["service_url", "service_status"],
                "modules": ["cloud-run", "cloud-sql", "vpc"]
            },
            "containers": {
                "main_tf": "terraform/google/gke",
                "variables": ["project_id", "region", "cluster_name", "node_count"],
                "outputs": ["cluster_endpoint", "cluster_ca_certificate"],
                "modules": ["gke-cluster", "node-pool", "vpc"]
            },
            "virtual_machines": {
                "main_tf": "terraform/google/compute",
                "variables": ["project_id", "zone", "instance_name", "machine_type"],
                "outputs": ["instance_ip", "instance_status"],
                "modules": ["compute-instance", "firewall", "vpc"]
            }
        }
        
        spec = templates.get(architecture, templates["containers"])
        
        # Add machine type if available
        if "machine_type" in specification:
            spec["variables"].append("machine_type")
            spec["variables"].append(f"default_machine_type = \"{specification['machine_type']}\"")
        
        return spec
    
    def _generate_configuration_spec(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate configuration specification"""
        architecture = data["architecture"]["primary"]
        
        specs = {
            "serverless": {
                "runtime": "Python 3.11 / Node.js 18",
                "environment_variables": ["NODE_ENV=production", "LOG_LEVEL=info"],
                "scaling": {"min_instances": 0, "max_instances": 10, "concurrency": 80},
                "timeout": "300s",
                "memory": "1Gi"
            },
            "containers": {
                "dockerfile": "FROM python:3.11-slim",
                "resources": {"requests": {"cpu": "100m", "memory": "128Mi"}},
                "probes": {"liveness": "/health", "readiness": "/ready"},
                "ports": [{"containerPort": 8080}]
            },
            "virtual_machines": {
                "os_image": "debian-cloud/debian-11",
                "disk_size": "100GB",
                "disk_type": "pd-ssd",
                "tags": ["http-server", "https-server"],
                "metadata": {"enable-oslogin": "TRUE"}
            }
        }
        
        return specs.get(architecture, specs["containers"])
    
    # Additional technical specification methods would follow similar patterns
    # For brevity, I'll provide stubs for the remaining methods
    
    def _generate_deployment_spec(self, data: Dict[str, Any]) -> Dict[str, Any]:
        return {"pipeline": "Cloud Build", "stages": ["test", "build", "deploy"]}
    
    def _generate_monitoring_spec(self, data: Dict[str, Any]) -> Dict[str, Any]:
        return {"tools": ["Cloud Monitoring", "Cloud Logging"], "dashboards": ["performance", "cost"]}
    
    def _generate_network_spec(self, data: Dict[str, Any]) -> Dict[str, Any]:
        return {"vpc": "default", "subnet": "us-central1", "firewall": ["allow-http", "allow-https"]}
    
    def _generate_security_spec(self, data: Dict[str, Any]) -> Dict[str, Any]:
        return {"iam_roles": ["roles/cloudrun.developer"], "secrets": "Secret Manager"}
    
    def _generate_storage_spec(self, data: Dict[str, Any]) -> Dict[str, Any]:
        return {"type": "Cloud Storage", "bucket": "app-data", "class": "STANDARD"}
    
    def _generate_scaling_spec(self, data: Dict[str, Any]) -> Dict[str, Any]:
        return {"min_replicas": 2, "max_replicas": 10, "cpu_utilization": 70}
    
    def _generate_template_presentation(self, data: Dict[str, Any],
                                      presentation_type: str) -> Dict[str, Any]:
        """Generate template-based presentation (fallback)"""
        logger.info("📄 Using template-based presentation")
        
        workload = data["workload"]
        architecture = data["architecture"]
        
        template = {
            "title": f"Infrastructure Recommendation",
            "subtitle": f"{workload['type']} on {architecture['primary']}",
            "audience": "general",
            "presentation_type": presentation_type,
            
            "summary": {
                "recommendation": f"Use {architecture['primary']} architecture",
                "reasoning": "Selected based on workload requirements and constraints",
                "confidence": f"{architecture['confidence']:.0%} confidence"
            },
            
            "key_points": [
                f"Designed for {workload['scale']['monthly_users']} monthly users",
                f"Targets {workload['requirements']['latency']} latency",
                f"Matches {workload['constraints']['team_experience']} team experience",
                f"Aligns with {workload['constraints']['budget_sensitivity']} budget"
            ],
            
            "next_steps": [
                "Review detailed specifications",
                "Plan implementation timeline",
                "Set up monitoring and alerts",
                "Schedule team training if needed"
            ],
            
            "template_used": True,
            "generation_method": "template_fallback"
        }
        
        return template
    
    def _generate_visual_components(self, data: Dict[str, Any],
                                  presentation_type: str) -> Dict[str, Any]:
        """Generate visual components for presentation"""
        template = self.presentation_templates[presentation_type]
        required_visuals = template["visuals"]
        
        components = {}
        
        for visual_type in required_visuals:
            if visual_type in self.visual_generators:
                try:
                    components[visual_type] = self.visual_generators[visual_type](data)
                except Exception as e:
                    logger.warning(f"Failed to generate visual {visual_type}: {e}")
                    components[visual_type] = {"error": f"Could not generate {visual_type}"}
            else:
                components[visual_type] = {"type": visual_type, "status": "not_implemented"}
        
        return components
    
    def _generate_cost_summary(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate cost summary visual"""
        pricing = data["pricing"]
        
        return {
            "type": "cost_summary",
            "data": {
                "primary_price": pricing["primary_price"],
                "alternative_prices": pricing["alternative_prices"],
                "savings": pricing["savings_analysis"].get("potential_monthly_savings", 0),
                "components": [
                    {"name": "Compute", "percentage": 60},
                    {"name": "Storage", "percentage": 20},
                    {"name": "Networking", "percentage": 10},
                    {"name": "Services", "percentage": 10}
                ]
            },
            "visualization": "pie_chart",
            "title": "Monthly Cost Breakdown"
        }
    
    def _generate_architecture_diagram(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate architecture diagram"""
        architecture = data["architecture"]["primary"]
        
        diagrams = {
            "serverless": {
                "components": ["Cloud Run", "Cloud SQL", "Cloud Storage", "Load Balancer"],
                "connections": [
                    "User → Load Balancer → Cloud Run",
                    "Cloud Run → Cloud SQL",
                    "Cloud Run → Cloud Storage"
                ],
                "style": "serverless_flow"
            },
            "containers": {
                "components": ["GKE Cluster", "Node Pool", "Cloud SQL", "Persistent Disk"],
                "connections": [
                    "User → Ingress → Service → Pod",
                    "Pod → Cloud SQL",
                    "Pod → Persistent Disk"
                ],
                "style": "kubernetes_cluster"
            },
            "virtual_machines": {
                "components": ["Compute Engine", "Instance Group", "Load Balancer", "Cloud SQL"],
                "connections": [
                    "User → Load Balancer → Instance Group",
                    "Instance → Cloud SQL",
                    "Instance → Cloud Storage"
                ],
                "style": "traditional_infrastructure"
            }
        }
        
        return {
            "type": "architecture_diagram",
            "data": diagrams.get(architecture, diagrams["serverless"]),
            "visualization": "mermaid_diagram",
            "title": f"{architecture.title()} Architecture"
        }
    
    def _generate_specification_table(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate specification table"""
        spec = data["specification"]
        
        return {
            "type": "specification_table",
            "data": {
                "headers": ["Component", "Specification", "Value"],
                "rows": [
                    ["Machine Type", spec.get("machine_type", "N/A"), "Primary compute"],
                    ["CPU", f"{spec.get('cpu', 4)} vCPUs", "Processing capacity"],
                    ["RAM", f"{spec.get('ram', 8)} GB", "Memory capacity"],
                    ["Family", spec["machine_family"].replace('_', ' ').title(), "Machine category"],
                    ["Size", spec["machine_size"].title(), "Instance size tier"]
                ]
            },
            "visualization": "data_table",
            "title": "Technical Specifications"
        }
    
    def _generate_performance_chart(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate performance chart"""
        workload = data["workload"]
        
        return {
            "type": "performance_chart",
            "data": {
                "metrics": [
                    {"name": "Latency", "target": workload["requirements"]["latency"], "current": "TBD"},
                    {"name": "Availability", "target": workload["requirements"]["availability"], "current": "TBD"},
                    {"name": "RPS Capacity", "target": workload["scale"]["estimated_rps"], "current": "TBD"},
                    {"name": "User Capacity", "target": workload["scale"]["monthly_users"], "current": "TBD"}
                ]
            },
            "visualization": "gauge_chart",
            "title": "Performance Targets"
        }
    
    def _generate_scalability_graph(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate scalability graph"""
        architecture = data["architecture"]["primary"]
        
        scaling_profiles = {
            "serverless": {"scale_out": 1, "scale_in": 1, "max_scale": 100},
            "containers": {"scale_out": 5, "scale_in": 5, "max_scale": 50},
            "virtual_machines": {"scale_out": 10, "scale_in": 10, "max_scale": 20}
        }
        
        return {
            "type": "scalability_graph",
            "data": scaling_profiles.get(architecture, scaling_profiles["containers"]),
            "visualization": "line_chart",
            "title": "Scaling Characteristics"
        }
    
    def _generate_timeline(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate timeline visual"""
        workload = data["workload"]
        
        return {
            "type": "timeline",
            "data": {
                "phases": [
                    {"name": "Planning", "duration": "1-2 weeks", "milestones": ["Requirements finalization", "Architecture sign-off"]},
                    {"name": "Implementation", "duration": "2-3 weeks", "milestones": ["Infrastructure setup", "Application deployment"]},
                    {"name": "Testing", "duration": "1-2 weeks", "milestones": ["Load testing", "Security validation"]},
                    {"name": "Deployment", "duration": "1 week", "milestones": ["Production rollout", "Monitoring activation"]}
                ]
            },
            "visualization": "gantt_chart",
            "title": "Implementation Timeline"
        }
    
    def _generate_risk_matrix(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate risk matrix"""
        analysis = data["analysis"]
        
        return {
            "type": "risk_matrix",
            "data": {
                "risks": [
                    {"name": risk, "impact": "Medium", "probability": "Low"}
                    for risk in analysis["risk_assessment"]["primary_risk_factors"][:5]
                ],
                "overall_risk": analysis["risk_assessment"]["overall_risk"]
            },
            "visualization": "risk_matrix_chart",
            "title": "Risk Assessment"
        }
    
    def _generate_comparison_table(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate comparison table for architectures"""
        architecture = data["architecture"]
        pricing = data["pricing"]
        
        rows = []
        for arch, price in pricing["alternative_prices"].items():
            rows.append({
                "architecture": arch.replace("_", " ").title(),
                "price": f"${price:.2f}/month",
                "is_primary": arch == architecture["primary"],
                "recommendation": "Recommended" if arch == architecture["primary"] else "Alternative"
            })
        
        return {
            "type": "comparison_table",
            "data": {
                "headers": ["Architecture", "Monthly Cost", "Status"],
                "rows": rows
            },
            "visualization": "data_table",
            "title": "Architecture Comparison"
        }
    
    def _generate_configuration_table(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate configuration table"""
        spec = data["specification"]
        config = spec.get("configuration", {})
        
        return {
            "type": "configuration_table",
            "data": {
                "headers": ["Setting", "Value", "Description"],
                "rows": [
                    {"setting": "Architecture", "value": config.get("architecture", "N/A"), "description": "Primary architecture type"},
                    {"setting": "Machine Type", "value": spec.get("machine_type", "N/A"), "description": "GCP machine type"},
                    {"setting": "vCPUs", "value": str(spec.get("cpu", 4)), "description": "Virtual CPUs allocated"},
                    {"setting": "Memory", "value": f"{spec.get('ram', 8)} GB", "description": "RAM allocated"},
                    {"setting": "Region", "value": config.get("region", "us-central1"), "description": "Deployment region"},
                    {"setting": "Scaling", "value": config.get("scaling_strategy", "automatic"), "description": "Scaling strategy"}
                ]
            },
            "visualization": "data_table",
            "title": "Configuration Details"
        }
    
    def _generate_deployment_steps(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate deployment steps"""
        architecture = data["architecture"]["primary"]
        
        steps = {
            "serverless": [
                {"step": 1, "name": "Configure Cloud Run service", "duration": "30 min"},
                {"step": 2, "name": "Deploy container image", "duration": "10 min"},
                {"step": 3, "name": "Set up Cloud SQL connection", "duration": "20 min"},
                {"step": 4, "name": "Configure load balancer", "duration": "15 min"},
                {"step": 5, "name": "Enable monitoring", "duration": "10 min"}
            ],
            "containers": [
                {"step": 1, "name": "Create GKE cluster", "duration": "15 min"},
                {"step": 2, "name": "Configure node pools", "duration": "10 min"},
                {"step": 3, "name": "Deploy workloads", "duration": "20 min"},
                {"step": 4, "name": "Set up ingress", "duration": "15 min"},
                {"step": 5, "name": "Configure monitoring", "duration": "15 min"}
            ],
            "virtual_machines": [
                {"step": 1, "name": "Create instance template", "duration": "10 min"},
                {"step": 2, "name": "Configure instance group", "duration": "15 min"},
                {"step": 3, "name": "Set up load balancer", "duration": "20 min"},
                {"step": 4, "name": "Deploy application", "duration": "30 min"},
                {"step": 5, "name": "Configure monitoring", "duration": "15 min"}
            ]
        }
        
        return {
            "type": "deployment_steps",
            "data": {
                "steps": steps.get(architecture, steps["serverless"]),
                "total_duration": "~90 minutes"
            },
            "visualization": "step_list",
            "title": "Deployment Steps"
        }
    
    def _generate_monitoring_setup(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate monitoring setup configuration"""
        workload = data["workload"]
        
        return {
            "type": "monitoring_setup",
            "data": {
                "metrics": [
                    {"name": "CPU Utilization", "threshold": "80%", "action": "Scale up"},
                    {"name": "Memory Usage", "threshold": "85%", "action": "Alert"},
                    {"name": "Request Latency (p95)", "threshold": "200ms", "action": "Alert"},
                    {"name": "Error Rate", "threshold": "1%", "action": "Alert + Page"}
                ],
                "dashboards": ["Performance Overview", "Cost Analysis", "Error Tracking"],
                "alerting": {
                    "channels": ["Email", "Slack", "PagerDuty"],
                    "escalation": "15 min → 30 min → 1 hour"
                }
            },
            "visualization": "monitoring_config",
            "title": "Monitoring Setup"
        }
    
    def _generate_security_matrix(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate security matrix"""
        architecture = data["architecture"]["primary"]
        
        security_controls = {
            "serverless": [
                {"control": "IAM Policies", "status": "Required", "implementation": "Cloud IAM"},
                {"control": "Network Security", "status": "Enabled", "implementation": "VPC Connector"},
                {"control": "Secret Management", "status": "Required", "implementation": "Secret Manager"},
                {"control": "SSL/TLS", "status": "Automatic", "implementation": "Managed certificates"}
            ],
            "containers": [
                {"control": "IAM Policies", "status": "Required", "implementation": "Workload Identity"},
                {"control": "Network Policies", "status": "Required", "implementation": "GKE Network Policy"},
                {"control": "Pod Security", "status": "Required", "implementation": "Pod Security Standards"},
                {"control": "Image Scanning", "status": "Enabled", "implementation": "Container Analysis"}
            ],
            "virtual_machines": [
                {"control": "IAM Policies", "status": "Required", "implementation": "Service Accounts"},
                {"control": "Firewall Rules", "status": "Required", "implementation": "VPC Firewall"},
                {"control": "OS Hardening", "status": "Recommended", "implementation": "CIS Benchmarks"},
                {"control": "Encryption", "status": "Enabled", "implementation": "CMEK/Default encryption"}
            ]
        }
        
        return {
            "type": "security_matrix",
            "data": {
                "controls": security_controls.get(architecture, security_controls["serverless"]),
                "compliance": ["SOC2 Type II", "ISO 27001"]
            },
            "visualization": "security_table",
            "title": "Security Controls"
        }
    
    # Additional technical spec generators (stubs for remaining methods)
    
    def _generate_deployment_procedures(self, data: Dict[str, Any]) -> Dict[str, Any]:
        return {"procedure": "Blue-green deployment", "rollback": "Automatic", "approval": "Required"}
    
    def _generate_monitoring_procedures(self, data: Dict[str, Any]) -> Dict[str, Any]:
        return {"frequency": "Real-time", "retention": "30 days", "alerting": "Multi-channel"}
    
    def _generate_maintenance_procedures(self, data: Dict[str, Any]) -> Dict[str, Any]:
        return {"schedule": "Weekly", "window": "Sunday 2-6 AM", "automation": "Enabled"}
    
    def _generate_troubleshooting_guide(self, data: Dict[str, Any]) -> Dict[str, Any]:
        return {"runbooks": ["High CPU", "High Memory", "Slow Response"], "escalation": "Defined"}
    
    def _generate_benchmarks(self, data: Dict[str, Any]) -> Dict[str, Any]:
        return {"latency_target": "< 100ms p95", "throughput_target": "1000 RPS", "availability_target": "99.9%"}
    
    def _generate_capacity_planning(self, data: Dict[str, Any]) -> Dict[str, Any]:
        return {"current_capacity": "100%", "growth_projection": "20%/quarter", "scaling_headroom": "30%"}
    
    def _generate_load_testing_plan(self, data: Dict[str, Any]) -> Dict[str, Any]:
        return {"tool": "Cloud Load Testing", "scenarios": ["Normal load", "Peak load", "Stress test"]}
    
    def _generate_optimization_guidelines(self, data: Dict[str, Any]) -> Dict[str, Any]:
        return {"techniques": ["Caching", "Connection pooling", "Async processing"], "priority": "High"}
    
    def _identify_cost_drivers(self, data: Dict[str, Any]) -> List[str]:
        return ["Compute instances", "Network egress", "Storage", "Database operations"]
    
    def _list_optimization_techniques(self, data: Dict[str, Any]) -> List[str]:
        return ["Committed use discounts", "Spot/Preemptible instances", "Autoscaling", "Right-sizing"]
    
    def _list_cost_metrics(self, data: Dict[str, Any]) -> List[str]:
        return ["Cost per request", "Cost per user", "Utilization efficiency", "Waste identification"]
    
    def _define_budget_controls(self, data: Dict[str, Any]) -> Dict[str, Any]:
        return {"alerts": [50, 80, 100], "actions": ["Notify", "Alert", "Cap spending"]}
    
    def _list_security_controls(self, data: Dict[str, Any]) -> List[str]:
        return ["IAM", "VPC", "Encryption", "Audit logging", "DDoS protection"]
    
    def _list_compliance_requirements(self, data: Dict[str, Any]) -> List[str]:
        return ["SOC2", "GDPR", "HIPAA (if applicable)", "PCI-DSS (if applicable)"]
    
    def _define_audit_logging(self, data: Dict[str, Any]) -> Dict[str, Any]:
        return {"enabled": True, "retention": "365 days", "export": "BigQuery"}
    
    def _define_incident_response(self, data: Dict[str, Any]) -> Dict[str, Any]:
        return {"severity_levels": [1, 2, 3, 4], "response_times": ["15 min", "1 hour", "4 hours", "24 hours"]}

    def _enhance_presentation_result(self, presentation: Dict[str, Any],
                                   visual_components: Dict[str, Any],
                                   consolidated_data: Dict[str, Any],
                                   presentation_type: str,
                                   presentation_method: str,
                                   *phase_results,
                                   processing_time_ms: int,
                                   user_id: str,
                                   session_id: str,
                                   request_id: str) -> Dict[str, Any]:
        """Enhance presentation result with metadata"""
        
        phase1 = phase_results[0]
        
        enhanced = {
            "request_id": request_id,
            "user_id": user_id,
            "session_id": session_id,
            "phase": self.phase_name,
            "phase_version": self.phase_version,
            "timestamp": datetime.utcnow().isoformat(),
            "status": "completed",
            
            "presentation_id": f"pres_{uuid.uuid4().hex[:8]}",
            
            "presentation_metadata": {
                "type": presentation_type,
                "audience": presentation["audience"],
                "generation_method": presentation_method,
                "template_used": presentation.get("template_used", False),
                "presentation_timestamp": datetime.utcnow().isoformat()
            },
            
            "presentation_data": presentation,
            
            "visual_components": visual_components,
            
            "processing_metadata": {
                "processing_time_ms": processing_time_ms,
                "presentation_method": presentation_method,
                "visual_components_generated": len(visual_components),
                "presentation_completeness": self._calculate_presentation_completeness(presentation, visual_components),
                "template_version": self.phase_version
            },
            
            "frontend_ready": {
                "title": presentation.get("title", "Infrastructure Recommendation"),
                "summary": self._extract_presentation_summary(presentation),
                "key_visuals": self._identify_key_visuals(visual_components),
                "action_items": self._extract_action_items(presentation),
                "navigation": self._generate_navigation_structure(presentation_type)
            },
            
            "next_phase": "user_decision",
            "phase_transition": {
                "recommended": True,
                "estimated_time_seconds": 30,
                "prerequisites_met": True,
                "required_input": {
                    "presentation_id": f"pres_{uuid.uuid4().hex[:8]}",
                    "presentation_type": presentation_type,
                    "recommendation_summary": self._extract_recommendation_summary(presentation)
                }
            }
        }
        
        return enhanced
    
    def _calculate_presentation_completeness(self, presentation: Dict[str, Any],
                                           visual_components: Dict[str, Any]) -> float:
        """Calculate presentation completeness percentage"""
        # Check required sections
        required_sections = ["title", "audience", "presentation_type"]
        present_sections = sum(1 for section in required_sections if section in presentation)
        
        # Check visual components
        expected_visuals = len(self.presentation_templates[presentation["presentation_type"]]["visuals"])
        generated_visuals = len(visual_components)
        
        section_score = (present_sections / len(required_sections)) * 50
        visual_score = (generated_visuals / max(expected_visuals, 1)) * 50
        
        return round(section_score + visual_score, 1)
    
    def _extract_presentation_summary(self, presentation: Dict[str, Any]) -> Dict[str, Any]:
        """Extract presentation summary for frontend"""
        summary_keys = ["executive_summary", "overview", "summary"]
        
        for key in summary_keys:
            if key in presentation:
                if isinstance(presentation[key], dict):
                    return presentation[key]
                else:
                    return {"text": str(presentation[key])}
        
        # Fallback summary
        return {
            "text": f"{presentation.get('title', 'Infrastructure recommendation')} ready for review",
            "type": presentation.get("presentation_type", "detailed")
        }
    
    def _identify_key_visuals(self, visual_components: Dict[str, Any]) -> List[str]:
        """Identify key visual components for frontend"""
        priority_visuals = ["cost_summary", "architecture_diagram", "specification_table", "timeline"]
        
        key_visuals = []
        for visual in priority_visuals:
            if visual in visual_components:
                key_visuals.append(visual)
        
        # Add any other visuals
        for visual in visual_components:
            if visual not in key_visuals:
                key_visuals.append(visual)
        
        return key_visuals[:5]  # Limit to top 5
    
    def _extract_action_items(self, presentation: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract action items from presentation"""
        action_sources = ["next_steps", "recommendation", "implementation_plan", "business_case"]
        
        actions = []
        
        for source in action_sources:
            if source in presentation:
                items = presentation[source]
                if isinstance(items, list):
                    for item in items[:3]:  # Take first 3
                        actions.append({"text": str(item), "source": source})
                elif isinstance(items, dict):
                    if "next_steps" in items:
                        for step in items["next_steps"][:2]:
                            actions.append({"text": str(step), "source": source})
        
        # Ensure at least 2 actions
        if len(actions) < 2:
            actions.extend([
                {"text": "Review detailed specifications", "source": "default"},
                {"text": "Schedule implementation planning", "source": "default"}
            ])
        
        return actions[:5]  # Limit to 5 actions
    
    def _generate_navigation_structure(self, presentation_type: str) -> Dict[str, Any]:
        """Generate navigation structure for frontend"""
        structures = {
            "executive": [
                {"id": "summary", "label": "Executive Summary", "icon": "📊"},
                {"id": "business_case", "label": "Business Case", "icon": "💰"},
                {"id": "risk", "label": "Risk Assessment", "icon": "⚠️"},
                {"id": "recommendation", "label": "Recommendation", "icon": "✅"}
            ],
            "detailed": [
                {"id": "overview", "label": "Overview", "icon": "👁️"},
                {"id": "architecture", "label": "Architecture", "icon": "🏗️"},
                {"id": "specifications", "label": "Specifications", "icon": "⚙️"},
                {"id": "cost", "label": "Cost Analysis", "icon": "💰"},
                {"id": "implementation", "label": "Implementation", "icon": "🚀"},
                {"id": "risks", "label": "Risks & Mitigation", "icon": "🛡️"}
            ],
            "technical": [
                {"id": "specification", "label": "Specification", "icon": "📋"},
                {"id": "implementation", "label": "Implementation", "icon": "🔧"},
                {"id": "operations", "label": "Operations", "icon": "🔄"},
                {"id": "performance", "label": "Performance", "icon": "⚡"},
                {"id": "cost", "label": "Cost Optimization", "icon": "📉"},
                {"id": "security", "label": "Security & Compliance", "icon": "🔒"}
            ]
        }
        
        return {
            "sections": structures.get(presentation_type, structures["detailed"]),
            "default_section": structures.get(presentation_type, structures["detailed"])[0]["id"],
            "allow_collapse": True,
            "show_progress": True
        }
    
    def _extract_recommendation_summary(self, presentation: Dict[str, Any]) -> Dict[str, Any]:
        """Extract recommendation summary for phase transition"""
        summary_sources = ["executive_summary", "summary", "overview", "recommendation"]
        
        for source in summary_sources:
            if source in presentation:
                content = presentation[source]
                if isinstance(content, dict):
                    return {
                        "source": source,
                        "content": content.get("one_liner", str(content))
                    }
                else:
                    return {
                        "source": source,
                        "content": str(content)[:200]  # Limit length
                    }
        
        return {
            "source": "presentation",
            "content": presentation.get("title", "Recommendation ready for review")
        }
    
    def _calculate_presentation_quality(self, presentation: Dict[str, Any],
                                      visual_components: Dict[str, Any]) -> float:
        """Calculate presentation quality score"""
        quality_factors = []
        
        # Content completeness
        required_keys = ["title", "audience", "presentation_type"]
        present_keys = sum(1 for key in required_keys if key in presentation)
        quality_factors.append(present_keys / len(required_keys))
        
        # Visual components quality
        if visual_components:
            quality_factors.append(min(1.0, len(visual_components) / 5))
        else:
            quality_factors.append(0.3)
        
        # Content depth
        content_keys = len(presentation.keys())
        quality_factors.append(min(1.0, content_keys / 10))
        
        # Calculate average quality
        avg_quality = sum(quality_factors) / len(quality_factors)
        
        return round(avg_quality * 100, 1)  # Convert to 0-100 scale
    
    def _emit_success_telemetry(self, result: Dict[str, Any], processing_time_ms: int):
        """Emit success telemetry"""
        presentation_meta = result["presentation_metadata"]
        frontend_ready = result["frontend_ready"]
        
        # Emit presentation type metric
        self.telemetry.submit_metric(
            name="recommendation.presentation.generated",
            value=1.0,
            tags=[
                f"presentation_type:{presentation_meta['type']}",
                f"audience:{presentation_meta['audience']}",
                f"phase:{self.phase_name}",
                f"generation_method:{presentation_meta['generation_method']}",
                f"template_used:{presentation_meta.get('template_used', False)}"
            ]
        )
        
        # Emit visual components metric
        visual_count = len(result["visual_components"])
        self.telemetry.submit_metric(
            name="recommendation.presentation.visual_components",
            value=visual_count,
            tags=[
                f"presentation_type:{presentation_meta['type']}",
                f"phase:{self.phase_name}"
            ]
        )
        
        # Emit processing time metric
        self.telemetry.submit_metric(
            name="recommendation.presentation.processing.time_ms",
            value=processing_time_ms,
            tags=[
                f"presentation_type:{presentation_meta['type']}",
                f"phase:{self.phase_name}",
                f"success:true"
            ]
        )
        
        # Emit success log
        self.telemetry.submit_log(
            source="cloud-sentinel",
            message={
                "event": "recommendation_presentation_generated",
                "presentation_id": result["presentation_id"],
                "request_id": result["request_id"],
                "user_id": result["user_id"],
                "session_id": result["session_id"],
                "presentation_type": presentation_meta["type"],
                "audience": presentation_meta["audience"],
                "visual_components_count": visual_count,
                "processing_time_ms": processing_time_ms,
                "frontend_title": frontend_ready["title"],
                "action_items_count": len(frontend_ready["action_items"])
            },
            tags=[
                "recommendation_presentation", 
                "success", 
                presentation_meta["type"],
                f"phase:{self.phase_name}",
                f"audience:{presentation_meta['audience']}"
            ]
        )
        
        # Emit success event
        self.telemetry.emit_event(
            title="Recommendation Presentation Generated",
            text=f"Created {presentation_meta['type']} presentation for {presentation_meta['audience']} audience with {visual_count} visual components",
            tags=[
                "recommendation_presented",
                presentation_meta["type"],
                f"audience:{presentation_meta['audience']}",
                f"visuals:{visual_count}",
                f"user:{result['user_id']}",
                f"phase:{self.phase_name}"
            ],
            alert_type="success"
        )
    
    def _create_error_result(self, user_id: str, session_id: str, request_id: str,
                           *phase_results,
                           error_message: str, processing_time_ms: int) -> Dict[str, Any]:
        """Create error result structure"""
        phase1 = phase_results[0]
        
        return {
            "request_id": request_id,
            "user_id": user_id,
            "session_id": session_id,
            "phase": self.phase_name,
            "timestamp": datetime.utcnow().isoformat(),
            "status": "error",
            "error": {
                "message": error_message,
                "code": "PRESENTATION_GENERATION_FAILED",
                "phase_summary": {
                    "workload_type": phase1.get("intent_analysis", {}).get("workload_type", "unknown")
                }
            },
            "processing_metadata": {
                "processing_time_ms": processing_time_ms,
                "presentation_method": "failed",
                "attempted_retry": False
            },
            "fallback_presentation": {
                "title": "Infrastructure Recommendation",
                "summary": "System temporarily unavailable. Basic recommendation details are available.",
                "key_points": [
                    "Review previous phase outputs for details",
                    "Contact support if assistance is needed"
                ],
                "next_steps": ["Retry presentation generation", "Review raw phase outputs"]
            }
        }
    
    def _emit_error_telemetry(self, error_result: Dict[str, Any], error_message: str):
        """Emit error telemetry"""
        self.telemetry.submit_metric(
            name="recommendation.presentation.processing.time_ms",
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
                "event": "recommendation_presentation_failed",
                "request_id": error_result["request_id"],
                "user_id": error_result["user_id"],
                "error": error_result["error"],
                "processing_time_ms": error_result["processing_metadata"]["processing_time_ms"]
            },
            tags=[
                "recommendation_presentation", 
                "error", 
                error_result["error"]["code"],
                f"phase:{self.phase_name}"
            ]
        )
        
        self.telemetry.emit_event(
            title="Recommendation Presentation Failed",
            text=f"Failed to create presentation: {error_message}",
            tags=[
                "presentation_error",
                f"error_code:{error_result['error']['code']}",
                f"user:{error_result['user_id']}",
                f"phase:{self.phase_name}"
            ],
            alert_type="error",
            priority="high"
        )
    
    def _update_statistics(self, presentation_quality: float, processing_time_ms: int):
        """Update phase statistics"""
        self.stats["avg_presentation_quality"] = (
            (self.stats["avg_presentation_quality"] * (self.stats["total_presentations"] - 1) + presentation_quality) 
            / self.stats["total_presentations"]
            if self.stats["total_presentations"] > 0 
            else presentation_quality
        )
        
        self.stats["total_processing_time_ms"] += processing_time_ms
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get phase statistics"""
        total = self.stats["total_presentations"]
        
        stats = self.stats.copy()
        
        if total > 0:
            stats["avg_processing_time_ms"] = self.stats["total_processing_time_ms"] / total
            stats["executive_percent"] = (self.stats["executive_presentations"] / total * 100) if total > 0 else 0
            stats["detailed_percent"] = (self.stats["detailed_presentations"] / total * 100) if total > 0 else 0
            stats["technical_percent"] = (self.stats["technical_presentations"] / total * 100) if total > 0 else 0
        else:
            stats["avg_processing_time_ms"] = 0.0
            stats["executive_percent"] = 0.0
            stats["detailed_percent"] = 0.0
            stats["technical_percent"] = 0.0
        
        stats["phase_name"] = self.phase_name
        stats["phase_version"] = self.phase_version
        stats["presentation_templates"] = len(self.presentation_templates)
        stats["visual_generators"] = len(self.visual_generators)
        stats["telemetry_status"] = self.telemetry.get_status()
        
        return stats
    
    def reset_statistics(self):
        """Reset phase statistics"""
        self.stats = {
            "total_presentations": 0,
            "executive_presentations": 0,
            "detailed_presentations": 0,
            "technical_presentations": 0,
            "total_processing_time_ms": 0,
            "avg_presentation_quality": 0.0
        }
        logger.info("📊 Phase 6 statistics reset")
    
    def get_status(self) -> Dict[str, Any]:
        """Get complete phase status"""
        return {
            "phase": self.phase_name,
            "version": self.phase_version,
            "initialized": True,
            "telemetry_available": self.telemetry.config.mode != TelemetryMode.DISABLED,
            "presentation_templates_available": len(self.presentation_templates),
            "visual_generators_available": len(self.visual_generators),
            "statistics": self.get_statistics()
        }