"""
Phase 5: AI Tradeoff Analysis
Production-grade implementation with Gemini-generated analysis
"""

import time
import logging
import json
from datetime import datetime
from typing import Dict, Any, Optional, List, Tuple
import uuid
import random

from ..core.gemini_client import GeminiClient
from ..telemetry.datadog_client import TelemetryClient, TelemetryConfig, TelemetryMode

logger = logging.getLogger(__name__)

class TradeoffAnalysisPhase:
    """Complete Phase 5: AI Tradeoff Analysis"""
    
    def __init__(self, telemetry_config: Optional[TelemetryConfig] = None):
        self.phase_name = "tradeoff_analysis"
        self.phase_version = "1.0.0"
        
        # Initialize clients
        self.gemini = GeminiClient()
        self.telemetry = TelemetryClient(telemetry_config)
        
        # Tradeoff factors with weights
        self.tradeoff_factors = {
            "cost": {
                "weight": 0.35,
                "description": "Total monthly cost including all services",
                "preference": "lower_is_better"
            },
            "performance": {
                "weight": 0.25,
                "description": "Latency, throughput, and response times",
                "preference": "higher_is_better"
            },
            "scalability": {
                "weight": 0.15,
                "description": "Ability to handle traffic spikes and growth",
                "preference": "higher_is_better"
            },
            "operational_complexity": {
                "weight": 0.10,
                "description": "Team effort required for maintenance and operations",
                "preference": "lower_is_better"
            },
            "reliability": {
                "weight": 0.10,
                "description": "Availability, fault tolerance, and disaster recovery",
                "preference": "higher_is_better"
            },
            "time_to_market": {
                "weight": 0.05,
                "description": "Speed of deployment and iteration",
                "preference": "higher_is_better"
            }
        }
        
        # Statistics
        self.stats = {
            "total_analyses": 0,
            "gemini_analyses": 0,
            "rule_based_analyses": 0,
            "total_processing_time_ms": 0,
            "avg_analysis_quality": 0.0
        }
        
        logger.info(f"✅ Phase 5 initialized: {self.phase_name} v{self.phase_version}")
        logger.info(f"📊 Tradeoff factors: {len(self.tradeoff_factors)} with weighted scoring")
    
    async def process(self, phase1_result: Dict[str, Any], 
                     phase2_result: Dict[str, Any],
                     phase3_result: Dict[str, Any],
                     phase4_result: Dict[str, Any],
                     user_id: Optional[str] = None,
                     session_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Generate AI-powered tradeoff analysis
        
        Args:
            phase1_result: Complete output from Phase 1
            phase2_result: Complete output from Phase 2
            phase3_result: Complete output from Phase 3
            phase4_result: Complete output from Phase 4
            user_id: User identifier
            session_id: Session identifier
            
        Returns:
            Dict containing tradeoff analysis with full context
        """
        start_time = time.time()
        
        # Validate inputs
        self._validate_inputs(phase1_result, phase2_result, phase3_result, phase4_result)
        
        self.stats["total_analyses"] += 1
        
        # Extract data from previous phases
        intent_analysis = phase1_result["intent_analysis"]
        architecture_analysis = phase2_result["architecture_analysis"]
        specification_analysis = phase3_result["specification_analysis"]
        pricing_result = phase4_result
        
        workload_type = intent_analysis["workload_type"]
        requirements = intent_analysis["requirements"]
        constraints = intent_analysis["constraints"]
        primary_architecture = architecture_analysis["primary_architecture"]
        primary_price = pricing_result["primary_price"]["total_monthly_usd"]
        alternative_prices = pricing_result["alternative_prices"]
        
        # Use IDs from previous phases
        request_id = phase1_result.get("request_id", f"req_{int(time.time())}_{uuid.uuid4().hex[:6]}")
        user_id = user_id or phase1_result.get("user_id", f"user_{uuid.uuid4().hex[:8]}")
        session_id = session_id or phase1_result.get("session_id", f"session_{uuid.uuid4().hex[:8]}")
        
        try:
            logger.info(f"⚖️  Tradeoff analysis - Primary: {primary_architecture}, Workload: {workload_type}")
            
            # Step 1: Prepare analysis data
            analysis_data = self._prepare_analysis_data(
                intent_analysis, architecture_analysis, 
                specification_analysis, pricing_result
            )
            
            # Step 2: Generate analysis (try Gemini first, then fallback)
            analysis_method = "gemini_api"
            try:
                gemini_analysis = await self._generate_gemini_analysis(analysis_data)
                structured_analysis = self._structure_gemini_analysis(gemini_analysis, analysis_data)
                structured_analysis["analysis_method"] = "gemini_api"
                self.stats["gemini_analyses"] += 1
            except Exception as e:
                logger.warning(f"Gemini analysis failed, using rule-based: {e}")
                structured_analysis = self._generate_rule_based_analysis(analysis_data)
                structured_analysis["analysis_method"] = "rule_based"
                self.stats["rule_based_analyses"] += 1
                analysis_method = "rule_based"
            
            # Step 3: Calculate tradeoff scores
            tradeoff_scores = self._calculate_tradeoff_scores(
                analysis_data, structured_analysis
            )
            
            # Step 4: Generate decision factors
            decision_factors = self._identify_decision_factors(
                analysis_data, tradeoff_scores
            )
            
            # Step 5: Calculate processing time
            processing_time_ms = int((time.time() - start_time) * 1000)
            
            # Step 6: Enhance result with metadata
            enhanced_result = self._enhance_analysis_result(
                structured_analysis,
                tradeoff_scores,
                decision_factors,
                phase1_result,
                phase2_result,
                phase3_result,
                phase4_result,
                processing_time_ms,
                analysis_method,
                user_id,
                session_id,
                request_id
            )
            
            # Step 7: Update statistics
            analysis_quality = self._calculate_analysis_quality(structured_analysis)
            self._update_statistics(analysis_quality, processing_time_ms)
            
            # Step 8: Emit telemetry
            self._emit_success_telemetry(enhanced_result, processing_time_ms)
            
            logger.info(f"✅ Tradeoff analysis generated")
            logger.info(f"   Recommendation strength: {structured_analysis.get('recommendation_strength', 'N/A')}")
            logger.info(f"   Method: {analysis_method}")
            logger.info(f"   Time: {processing_time_ms}ms")
            
            return enhanced_result
            
        except Exception as e:
            # Handle failures gracefully
            processing_time_ms = int((time.time() - start_time) * 1000)
            
            error_result = self._create_error_result(
                user_id, session_id, request_id, 
                phase1_result, phase2_result, phase3_result, 
                phase4_result, str(e), processing_time_ms
            )
            
            self._emit_error_telemetry(error_result, str(e))
            
            logger.error(f"❌ Tradeoff analysis failed: {e}")
            raise
    
    def _validate_inputs(self, phase1_result: Dict[str, Any], 
                        phase2_result: Dict[str, Any], 
                        phase3_result: Dict[str, Any],
                        phase4_result: Dict[str, Any]):
        """Validate all input phases"""
        required_phases = [
            ("Phase 1", phase1_result, "intent_analysis"),
            ("Phase 2", phase2_result, "architecture_analysis"),
            ("Phase 3", phase3_result, "specification_analysis"),
            ("Phase 4", phase4_result, "primary_price")
        ]
        
        for phase_name, phase_data, required_field in required_phases:
            if not phase_data or required_field not in phase_data:
                raise ValueError(f"Invalid {phase_name} result. Missing {required_field}")
    
    def _prepare_analysis_data(self, intent_analysis: Dict[str, Any],
                              architecture_analysis: Dict[str, Any],
                              specification_analysis: Dict[str, Any],
                              pricing_result: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare structured data for analysis"""
        
        # Get primary architecture details
        primary_arch = architecture_analysis["primary_architecture"]
        
        # Get alternative architectures
        alternatives = []
        for alt_arch in ["serverless", "containers", "virtual_machines"]:
            if alt_arch != primary_arch:
                alternatives.append({
                    "architecture": alt_arch,
                    "price": pricing_result["alternative_prices"].get(alt_arch, 0),
                    "when_to_consider": self._get_alternative_context(alt_arch, intent_analysis)
                })
        
        return {
            "workload": {
                "type": intent_analysis["workload_type"],
                "scale": intent_analysis["scale"],
                "requirements": intent_analysis["requirements"],
                "constraints": intent_analysis["constraints"]
            },
            "primary_recommendation": {
                "architecture": primary_arch,
                "confidence": architecture_analysis["confidence"],
                "reasoning": architecture_analysis["reasoning"],
                "machine_type": specification_analysis.get("exact_type", "unknown"),
                "cpu": specification_analysis.get("cpu", 4),
                "ram": specification_analysis.get("ram", 8),
                "price": pricing_result["primary_price"]["total_monthly_usd"],
                "price_accuracy": pricing_result["pricing_accuracy"]["estimated_accuracy"]
            },
            "alternatives": alternatives,
            "price_comparison": {
                "primary_price": pricing_result["primary_price"]["total_monthly_usd"],
                "alternative_prices": pricing_result["alternative_prices"],
                "savings_analysis": pricing_result["savings_analysis"]
            },
            "user_context": {
                "team_experience": intent_analysis["constraints"]["team_experience"],
                "budget_sensitivity": intent_analysis["constraints"]["budget_sensitivity"],
                "time_to_market": intent_analysis["constraints"]["time_to_market"],
                "risk_tolerance": self._assess_risk_tolerance(intent_analysis["constraints"])
            }
        }
    
    def _get_alternative_context(self, architecture: str, intent_analysis: Dict[str, Any]) -> str:
        """Get context for when to consider alternative"""
        contexts = {
            "serverless": {
                "api_backend": "When you have variable traffic patterns and want minimal operations",
                "web_app": "For web apps with unpredictable traffic and rapid iteration needs",
                "data_processing": "For event-driven data processing with sporadic workloads",
                "ml_inference": "For low-volume or batch inference with infrequent requests",
                "default": "When you need automatic scaling and want to focus on code, not infrastructure"
            },
            "containers": {
                "api_backend": "When you need fine-grained control and have Kubernetes expertise",
                "web_app": "For complex web apps requiring custom runtime environments",
                "data_processing": "For data pipelines with specific dependencies and resource requirements",
                "ml_inference": "For ML workloads requiring GPU access and custom environments",
                "default": "When you need portability, ecosystem benefits, and have container expertise"
            },
            "virtual_machines": {
                "api_backend": "For legacy applications or when you need specific OS requirements",
                "web_app": "When migrating existing on-premise applications to cloud",
                "data_processing": "For data processing requiring specific kernel versions or drivers",
                "ml_inference": "For ML workloads with custom hardware or licensing requirements",
                "default": "When you need full control over the operating system and runtime environment"
            }
        }
        
        workload_type = intent_analysis["workload_type"]
        arch_contexts = contexts.get(architecture, {})
        
        return arch_contexts.get(workload_type, arch_contexts.get("default", "Consider based on specific requirements"))
    
    def _assess_risk_tolerance(self, constraints: Dict[str, Any]) -> str:
        """Assess user's risk tolerance based on constraints"""
        risk_factors = {
            "team_experience": {
                "beginner": 2,  # Higher risk
                "junior": 1,
                "intermediate": 0,
                "senior": -1,
                "expert": -2   # Lower risk
            },
            "time_to_market": {
                "immediate": 2,
                "1_week": 1,
                "1_month": 0,
                "flexible": -1
            },
            "budget_sensitivity": {
                "very_low": -2,
                "low": -1,
                "medium": 0,
                "high": 1,
                "very_high": 2
            }
        }
        
        risk_score = 0
        for factor, mapping in risk_factors.items():
            value = constraints.get(factor, "medium")
            risk_score += mapping.get(value, 0)
        
        if risk_score >= 3:
            return "low"  # Low risk tolerance
        elif risk_score <= -3:
            return "high"  # High risk tolerance
        else:
            return "medium"
    
    async def _generate_gemini_analysis(self, analysis_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate tradeoff analysis using Gemini"""
        prompt = self._create_analysis_prompt(analysis_data)
        
        try:
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
            import re
            json_pattern = r'(\{.*\})'
            match = re.search(json_pattern, response_text, re.DOTALL)
            
            if not match:
                # Try to extract structured data from text
                return self._extract_structured_analysis(response_text, analysis_data)
            
            json_text = match.group(1)
            result = json.loads(json_text)
            
            # Validate result
            self._validate_analysis_result(result)
            
            # Add metadata
            result["analysis_source"] = "gemini_api"
            result["llm_model"] = self.gemini.model_name
            
            logger.info(f"✅ Gemini analysis generated successfully")
            return result
            
        except Exception as e:
            logger.error(f"Gemini analysis generation error: {e}")
            raise
    
    def _create_analysis_prompt(self, analysis_data: Dict[str, Any]) -> str:
        """Create prompt for Gemini tradeoff analysis"""
        
        workload = analysis_data["workload"]
        primary = analysis_data["primary_recommendation"]
        alternatives = analysis_data["alternatives"]
        user_context = analysis_data["user_context"]
        
        prompt = f"""You are an expert cloud architect at Google. Generate a comprehensive tradeoff analysis.

WORKLOAD DETAILS:
- Type: {workload['type']}
- Scale: {workload['scale']['monthly_users']} monthly users, {workload['scale']['estimated_rps']} RPS
- Requirements: Latency={workload['requirements']['latency']}, Availability={workload['requirements']['availability']}
- Constraints: Budget={workload['constraints']['budget_sensitivity']}, Team={workload['constraints']['team_experience']}, Time={workload['constraints']['time_to_market']}

PRIMARY RECOMMENDATION:
- Architecture: {primary['architecture']}
- Machine: {primary['machine_type']} ({primary['cpu']} vCPU, {primary['ram']}GB RAM)
- Price: ${primary['price']:.2f}/month
- Confidence: {primary['confidence']:.0%}
- Reasoning: {primary['reasoning']}

ALTERNATIVES:
{chr(10).join([f"- {alt['architecture']}: ${alt['price']:.2f}/month - {alt['when_to_consider']}" for alt in alternatives])}

USER CONTEXT:
- Team Experience: {user_context['team_experience']}
- Budget Sensitivity: {user_context['budget_sensitivity']}
- Time to Market: {user_context['time_to_market']}
- Risk Tolerance: {user_context['risk_tolerance']}

Generate a JSON analysis with these EXACT fields:

1. executive_summary (string): 2-3 sentence overview
2. recommendation_strength (number 0-100): How strong is this recommendation?
3. primary_advantages (array of strings): 3-5 key advantages
4. primary_risks (array of strings): 2-3 potential risks
5. tradeoff_matrix (object): Compare primary vs alternatives on:
   - cost_comparison (string): "significantly cheaper", "slightly more expensive", etc.
   - performance_implications (string)
   - scalability_differences (string)
   - operational_complexity (string)
   - reliability_comparison (string)
6. decision_factors (array of objects): Each with:
   - factor (string): e.g., "Cost", "Team Experience"
   - importance (string): "critical", "high", "medium", "low"
   - implication (string): How this affects the decision
7. risk_assessment (object):
   - overall_risk (string): "low", "medium", "high"
   - primary_risk_factors (array of strings)
   - mitigation_strategies (array of strings)
8. next_step_recommendations (array of strings): 3-5 actionable next steps

Example format:
{{
  "executive_summary": "The serverless architecture is recommended...",
  "recommendation_strength": 85,
  "primary_advantages": ["Cost-effective for variable traffic", "Minimal operations overhead", ...],
  "primary_risks": ["Cold start latency", "Vendor lock-in concerns", ...],
  "tradeoff_matrix": {{
    "cost_comparison": "Serverless is 30% cheaper than containers",
    "performance_implications": "Similar latency profile with occasional cold starts",
    ...
  }},
  "decision_factors": [
    {{"factor": "Budget", "importance": "high", "implication": "Serverless provides best cost efficiency"}},
    ...
  ],
  "risk_assessment": {{
    "overall_risk": "low",
    "primary_risk_factors": ["Team learning curve", "Vendor dependencies"],
    "mitigation_strategies": ["Start with non-critical workload", "Implement monitoring"]
  }},
  "next_step_recommendations": ["Deploy a prototype", "Set up cost monitoring", ...]
}}

CRITICAL INSTRUCTIONS:
1. Be objective and balanced
2. Consider the user's team experience and constraints
3. Highlight both pros and cons
4. Make recommendations actionable
5. Return ONLY valid JSON, no markdown, no code blocks
6. Recommendation_strength should reflect confidence given constraints

JSON OUTPUT:"""
        
        return prompt
    
    def _extract_structured_analysis(self, analysis_text: str, 
                                    analysis_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract structured analysis from text if JSON parsing fails"""
        logger.warning("Extracting structured analysis from text (JSON parse failed)")
        
        # Simple text analysis to extract key points
        lines = analysis_text.split('\n')
        
        # Extract key sections
        executive_summary = ""
        advantages = []
        risks = []
        
        current_section = None
        for line in lines:
            line_lower = line.lower()
            
            if "executive" in line_lower or "summary" in line_lower:
                current_section = "executive"
            elif "advantage" in line_lower or "pro" in line_lower or "benefit" in line_lower:
                current_section = "advantages"
            elif "risk" in line_lower or "con" in line_lower or "challenge" in line_lower:
                current_section = "risks"
            elif "recommend" in line_lower or "next step" in line_lower:
                current_section = "recommendations"
            
            # Clean and add content
            clean_line = line.strip('- •*').strip()
            if clean_line and len(clean_line) > 10:
                if current_section == "executive":
                    if not executive_summary:
                        executive_summary = clean_line
                    else:
                        executive_summary += " " + clean_line
                elif current_section == "advantages" and len(advantages) < 5:
                    advantages.append(clean_line)
                elif current_section == "risks" and len(risks) < 3:
                    risks.append(clean_line)
        
        # Create structured result
        result = {
            "executive_summary": executive_summary or "Analysis generated based on architectural best practices.",
            "recommendation_strength": 75,
            "primary_advantages": advantages or [
                f"{analysis_data['primary_recommendation']['architecture']} provides good cost-performance balance",
                "Matches the team's experience level",
                "Appropriate for the specified workload type"
            ],
            "primary_risks": risks or [
                "Standard risks associated with cloud adoption",
                "Team learning curve for new technologies"
            ],
            "tradeoff_matrix": {
                "cost_comparison": self._generate_cost_comparison(analysis_data),
                "performance_implications": "Standard performance for this workload type",
                "scalability_differences": "Adequate scalability for projected growth",
                "operational_complexity": "Matches team experience level",
                "reliability_comparison": "Standard cloud reliability"
            },
            "decision_factors": [
                {"factor": "Cost", "importance": "high", "implication": "Primary architecture selected for cost efficiency"},
                {"factor": "Team Experience", "importance": "medium", "implication": f"Matches {analysis_data['user_context']['team_experience']} team level"},
                {"factor": "Time to Market", "importance": "medium", "implication": f"Supports {analysis_data['user_context']['time_to_market']} timeline"}
            ],
            "risk_assessment": {
                "overall_risk": analysis_data['user_context']['risk_tolerance'],
                "primary_risk_factors": ["Standard cloud adoption risks", "Team adaptation period"],
                "mitigation_strategies": ["Start with non-critical workload", "Implement comprehensive monitoring"]
            },
            "next_step_recommendations": [
                "Deploy a proof-of-concept",
                "Set up cost and performance monitoring",
                "Plan knowledge transfer sessions for the team"
            ],
            "analysis_source": "text_extraction",
            "llm_model": "text_parser_v1"
        }
        
        return result
    
    def _generate_cost_comparison(self, analysis_data: Dict[str, Any]) -> str:
        """Generate cost comparison text"""
        primary = analysis_data["primary_recommendation"]
        price_comp = analysis_data["price_comparison"]
        
        primary_price = primary["price"]
        alternatives = price_comp["alternative_prices"]
        
        comparisons = []
        for arch, price in alternatives.items():
            if price > 0:
                diff_percent = ((price - primary_price) / primary_price * 100)
                if diff_percent > 10:
                    comparisons.append(f"{abs(diff_percent):.0f}% {'more expensive' if diff_percent > 0 else 'cheaper'} than {arch}")
        
        if comparisons:
            return f"Primary recommendation is {', '.join(comparisons)}"
        else:
            return "Competitive pricing compared to alternatives"
    
    def _validate_analysis_result(self, result: Dict[str, Any]) -> None:
        """Validate analysis result structure"""
        required_fields = [
            "executive_summary", "recommendation_strength",
            "primary_advantages", "primary_risks",
            "tradeoff_matrix", "decision_factors",
            "risk_assessment", "next_step_recommendations"
        ]
        
        for field in required_fields:
            if field not in result:
                raise ValueError(f"Missing required field in analysis: {field}")
        
        # Validate recommendation strength
        strength = result["recommendation_strength"]
        if not isinstance(strength, (int, float)) or not 0 <= strength <= 100:
            raise ValueError(f"Invalid recommendation_strength: {strength}")
    
    def _structure_gemini_analysis(self, gemini_result: Dict[str, Any],
                                  analysis_data: Dict[str, Any]) -> Dict[str, Any]:
        """Structure Gemini analysis with additional metadata"""
        
        # Add visual scorecard
        scorecard = self._generate_visual_scorecard(analysis_data, gemini_result)
        
        # Add quantitative metrics
        metrics = self._calculate_quantitative_metrics(analysis_data, gemini_result)
        
        structured = gemini_result.copy()
        structured.update({
            "visual_scorecard": scorecard,
            "quantitative_metrics": metrics,
            "analysis_timestamp": datetime.utcnow().isoformat(),
            "analysis_version": self.phase_version
        })
        
        return structured
    
    def _generate_visual_scorecard(self, analysis_data: Dict[str, Any],
                                  gemini_result: Dict[str, Any]) -> Dict[str, Any]:
        """Generate visual scorecard for easy comparison"""
        
        primary = analysis_data["primary_recommendation"]
        
        # Score factors (simplified)
        factors = {
            "Cost Efficiency": {
                "score": max(0, 100 - (primary["price"] / 1000 * 10)),  # Lower price = higher score
                "description": "Value for money"
            },
            "Performance": {
                "score": 85,  # Based on architecture
                "description": "Latency and throughput"
            },
            "Scalability": {
                "score": 90 if primary["architecture"] == "serverless" else 75,
                "description": "Handling growth and spikes"
            },
            "Operational Simplicity": {
                "score": 95 if primary["architecture"] == "serverless" else 60,
                "description": "Ease of management"
            },
            "Reliability": {
                "score": 88,
                "description": "Availability and fault tolerance"
            }
        }
        
        # Adjust based on team experience
        team_exp = analysis_data["user_context"]["team_experience"]
        if team_exp in ["beginner", "junior"]:
            factors["Operational Simplicity"]["score"] += 10
        elif team_exp in ["expert"]:
            factors["Operational Simplicity"]["score"] -= 10
        
        return {
            "factors": factors,
            "overall_score": sum(f["score"] for f in factors.values()) / len(factors),
            "primary_strengths": [f for f, data in factors.items() if data["score"] > 80],
            "primary_weaknesses": [f for f, data in factors.items() if data["score"] < 70]
        }
    
    def _calculate_quantitative_metrics(self, analysis_data: Dict[str, Any],
                                       gemini_result: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate quantitative metrics from analysis"""
        
        primary = analysis_data["primary_recommendation"]
        price_comp = analysis_data["price_comparison"]
        
        # Calculate cost metrics
        primary_price = primary["price"]
        avg_alternative_price = sum(price_comp["alternative_prices"].values()) / len(price_comp["alternative_prices"])
        
        cost_savings = avg_alternative_price - primary_price
        cost_savings_percent = (cost_savings / avg_alternative_price * 100) if avg_alternative_price > 0 else 0
        
        # Calculate risk metrics
        risk_levels = {"low": 20, "medium": 50, "high": 80}
        overall_risk = gemini_result["risk_assessment"]["overall_risk"]
        risk_score = risk_levels.get(overall_risk.lower(), 50)
        
        # Calculate alignment metrics
        alignment_score = self._calculate_alignment_score(analysis_data, gemini_result)
        
        return {
            "cost_metrics": {
                "primary_monthly_usd": round(primary_price, 2),
                "average_alternative_usd": round(avg_alternative_price, 2),
                "monthly_savings_usd": round(cost_savings, 2),
                "savings_percent": round(cost_savings_percent, 1),
                "roi_months": self._estimate_roi_months(primary_price, cost_savings)
            },
            "risk_metrics": {
                "risk_score": risk_score,
                "risk_level": overall_risk,
                "risk_factors_count": len(gemini_result["risk_assessment"]["primary_risk_factors"]),
                "mitigation_strategies_count": len(gemini_result["risk_assessment"]["mitigation_strategies"])
            },
            "alignment_metrics": {
                "budget_alignment_score": self._calculate_budget_alignment(analysis_data),
                "team_experience_alignment": self._calculate_team_alignment(analysis_data),
                "time_to_market_alignment": self._calculate_timeline_alignment(analysis_data),
                "overall_alignment_score": alignment_score
            }
        }
    
    def _estimate_roi_months(self, monthly_cost: float, monthly_savings: float) -> int:
        """Estimate ROI in months (simplified)"""
        if monthly_savings <= 0:
            return 12  # No savings, longer ROI
        
        # Assume initial setup cost of 3x monthly cost
        setup_cost = monthly_cost * 3
        roi_months = setup_cost / monthly_savings
        
        return min(max(int(roi_months), 1), 24)
    
    def _calculate_alignment_score(self, analysis_data: Dict[str, Any],
                                  gemini_result: Dict[str, Any]) -> float:
        """Calculate overall alignment score"""
        
        budget_score = self._calculate_budget_alignment(analysis_data)
        team_score = self._calculate_team_alignment(analysis_data)
        timeline_score = self._calculate_timeline_alignment(analysis_data)
        
        # Weighted average
        weights = {"budget": 0.4, "team": 0.3, "timeline": 0.3}
        
        alignment_score = (
            budget_score * weights["budget"] +
            team_score * weights["team"] +
            timeline_score * weights["timeline"]
        )
        
        return round(alignment_score, 1)
    
    def _calculate_budget_alignment(self, analysis_data: Dict[str, Any]) -> float:
        """Calculate budget alignment score"""
        primary_price = analysis_data["primary_recommendation"]["price"]
        budget_sensitivity = analysis_data["user_context"]["budget_sensitivity"]
        
        # Budget thresholds based on sensitivity
        thresholds = {
            "very_low": 10000,
            "low": 5000,
            "medium": 2000,
            "high": 500,
            "very_high": 200
        }
        
        budget_limit = thresholds.get(budget_sensitivity, 2000)
        
        if primary_price <= budget_limit:
            # Within budget, higher score for lower percentage
            percentage = (primary_price / budget_limit * 100)
            score = 100 - (percentage * 0.5)  # 50% at budget limit, 100% at 0
        else:
            # Over budget, penalize based on overage
            overage_percent = ((primary_price - budget_limit) / budget_limit * 100)
            score = max(0, 100 - overage_percent * 2)  # More severe penalty
        
        return max(0, min(score, 100))
    
    def _calculate_team_alignment(self, analysis_data: Dict[str, Any]) -> float:
        """Calculate team experience alignment score"""
        architecture = analysis_data["primary_recommendation"]["architecture"]
        team_experience = analysis_data["user_context"]["team_experience"]
        
        # Architecture complexity scores (higher = more complex)
        complexity_scores = {
            "serverless": 30,
            "containers": 70,
            "virtual_machines": 50
        }
        
        # Team capability scores (higher = more capable)
        team_scores = {
            "beginner": 20,
            "junior": 40,
            "intermediate": 60,
            "senior": 80,
            "expert": 95
        }
        
        arch_complexity = complexity_scores.get(architecture, 50)
        team_capability = team_scores.get(team_experience, 50)
        
        # Calculate alignment (closer match = higher score)
        diff = abs(arch_complexity - team_capability)
        
        if diff <= 20:
            score = 90  # Good match
        elif diff <= 40:
            score = 70  # Acceptable match
        elif diff <= 60:
            score = 40  # Challenging match
        else:
            score = 20  # Poor match
        
        return score
    
    def _calculate_timeline_alignment(self, analysis_data: Dict[str, Any]) -> float:
        """Calculate time-to-market alignment score"""
        architecture = analysis_data["primary_recommendation"]["architecture"]
        time_to_market = analysis_data["user_context"]["time_to_market"]
        
        # Architecture deployment speed (lower = faster)
        deployment_speed = {
            "serverless": 20,
            "containers": 60,
            "virtual_machines": 40
        }
        
        # Timeline urgency (lower = more urgent)
        urgency_scores = {
            "immediate": 20,
            "1_week": 40,
            "1_month": 60,
            "flexible": 80
        }
        
        arch_speed = deployment_speed.get(architecture, 50)
        timeline_urgency = urgency_scores.get(time_to_market, 50)
        
        # Calculate alignment (faster architecture for urgent timeline = higher score)
        if arch_speed <= timeline_urgency:
            score = 90  # Architecture can meet timeline
        elif arch_speed <= timeline_urgency + 20:
            score = 70  # Slight mismatch
        elif arch_speed <= timeline_urgency + 40:
            score = 40  # Significant mismatch
        else:
            score = 20  # Poor alignment
        
        return score
    
    def _generate_rule_based_analysis(self, analysis_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate rule-based tradeoff analysis (fallback)"""
        logger.info("📊 Generating rule-based tradeoff analysis")
        
        primary = analysis_data["primary_recommendation"]
        workload = analysis_data["workload"]
        user_context = analysis_data["user_context"]
        
        # Generate analysis based on rules
        executive_summary = (
            f"The {primary['architecture']} architecture is recommended for {workload['type']} workload "
            f"with {workload['scale']['monthly_users']} monthly users. This recommendation balances "
            f"cost, performance, and operational complexity for a {user_context['team_experience']} team."
        )
        
        # Determine recommendation strength
        strength_factors = {
            "confidence": primary["confidence"] * 30,  # 30% weight
            "price_accuracy": analysis_data["price_comparison"]["savings_analysis"].get("potential_monthly_savings", 0) > 0,
            "team_alignment": self._calculate_team_alignment(analysis_data) / 100 * 40,  # 40% weight
            "budget_alignment": self._calculate_budget_alignment(analysis_data) / 100 * 30  # 30% weight
        }
        
        recommendation_strength = min(100, int(
            strength_factors["confidence"] +
            (30 if strength_factors["price_accuracy"] else 0) +
            strength_factors["team_alignment"] +
            strength_factors["budget_alignment"]
        ))
        
        return {
            "executive_summary": executive_summary,
            "recommendation_strength": recommendation_strength,
            "primary_advantages": [
                f"Cost-effective at ${primary['price']:.2f}/month",
                f"Appropriate for {user_context['team_experience']} team experience",
                f"Good fit for {workload['type']} workload type",
                f"Supports {workload['scale']['monthly_users']} users scale"
            ],
            "primary_risks": [
                "Standard cloud adoption risks apply",
                f"Team may need training on {primary['architecture']}",
                "Performance depends on proper configuration"
            ],
            "tradeoff_matrix": {
                "cost_comparison": self._generate_cost_comparison(analysis_data),
                "performance_implications": f"Expected performance suitable for {workload['requirements']['latency']} latency requirements",
                "scalability_differences": f"Can scale to handle {workload['scale']['estimated_rps']} RPS with proper configuration",
                "operational_complexity": f"Matches {user_context['team_experience']} team capability",
                "reliability_comparison": f"Provides {workload['requirements']['availability']} availability as required"
            },
            "decision_factors": [
                {"factor": "Cost", "importance": "high", "implication": f"${primary['price']:.2f}/month fits {user_context['budget_sensitivity']} budget sensitivity"},
                {"factor": "Team Experience", "importance": "medium", "implication": f"{primary['architecture']} appropriate for {user_context['team_experience']} team"},
                {"factor": "Time to Market", "importance": "medium", "implication": f"Supports {user_context['time_to_market']} deployment timeline"},
                {"factor": "Risk Tolerance", "importance": "low", "implication": f"Matches {user_context['risk_tolerance']} risk tolerance"}
            ],
            "risk_assessment": {
                "overall_risk": user_context["risk_tolerance"],
                "primary_risk_factors": [
                    "Cloud learning curve",
                    "Configuration complexity",
                    "Cost management"
                ],
                "mitigation_strategies": [
                    "Start with non-critical workload",
                    "Implement comprehensive monitoring",
                    "Set up budget alerts",
                    "Plan regular reviews"
                ]
            },
            "next_step_recommendations": [
                "Deploy a proof-of-concept",
                "Set up monitoring and alerts",
                "Create runbooks for common operations",
                "Schedule regular cost and performance reviews"
            ],
            "analysis_source": "rule_based",
            "llm_model": "rule_engine_v1"
        }
    
    def _calculate_tradeoff_scores(self, analysis_data: Dict[str, Any],
                                  structured_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate numerical tradeoff scores"""
        
        primary = analysis_data["primary_recommendation"]
        price_comp = analysis_data["price_comparison"]
        
        # Calculate factor scores
        factor_scores = {}
        for factor_name, factor_info in self.tradeoff_factors.items():
            score = self._calculate_factor_score(factor_name, analysis_data, structured_analysis)
            factor_scores[factor_name] = {
                "score": score,
                "weight": factor_info["weight"],
                "weighted_score": score * factor_info["weight"],
                "description": factor_info["description"],
                "preference": factor_info["preference"]
            }
        
        # Calculate overall score
        total_weighted_score = sum(f["weighted_score"] for f in factor_scores.values())
        max_possible_score = sum(f["weight"] * 100 for f in self.tradeoff_factors.values())
        overall_score_percent = (total_weighted_score / max_possible_score * 100) if max_possible_score > 0 else 0
        
        # Identify strongest factors (by weighted impact on overall score)
        sorted_by_weighted = sorted(factor_scores.items(), key=lambda x: x[1]["weighted_score"], reverse=True)
        strongest_factors = [f[0] for f in sorted_by_weighted[:2]]
        
        # Identify weakest factors (by RAW score - what actually needs improvement)
        sorted_by_raw_score = sorted(factor_scores.items(), key=lambda x: x[1]["score"], reverse=False)
        weakest_factors = [f[0] for f in sorted_by_raw_score[:2]]
        
        return {
            "factor_scores": factor_scores,
            "overall_score": round(overall_score_percent, 1),
            "strongest_factors": strongest_factors,
            "weakest_factors": weakest_factors,
            "recommendation_category": self._categorize_recommendation(overall_score_percent)
        }
    
    def _calculate_factor_score(self, factor_name: str, analysis_data: Dict[str, Any],
                               structured_analysis: Dict[str, Any]) -> float:
        """Calculate score for a specific factor"""
        
        primary = analysis_data["primary_recommendation"]
        workload = analysis_data["workload"]
        user_context = analysis_data["user_context"]
        
        if factor_name == "cost":
            # Lower cost = higher score
            primary_price = primary["price"]
            alt_prices = analysis_data["price_comparison"]["alternative_prices"]
            # Calculate average of actual alternative prices (exclude $0 for current arch)
            valid_alt_prices = [p for p in alt_prices.values() if p > 0]
            avg_alt_price = sum(valid_alt_prices) / len(valid_alt_prices) if valid_alt_prices else 0
            
            if avg_alt_price > 0 and primary_price > 0:
                # Calculate how we compare to alternatives
                # If primary is cheaper than average alternative, positive savings
                savings_percent = ((avg_alt_price - primary_price) / avg_alt_price * 100)
                # Clamp to reasonable range: if 30% cheaper -> score 80, if 30% more expensive -> score 20
                score = max(0, min(100, 50 + savings_percent))
            elif primary_price == 0:
                score = 100  # Free is best
            else:
                score = 50  # Neutral if no alternatives
                
            # Adjust for budget sensitivity
            if user_context["budget_sensitivity"] in ["high", "very_high"]:
                score *= 1.2  # Boost cost score for budget-sensitive users
            
        elif factor_name == "performance":
            # Based on latency requirements
            latency = workload["requirements"]["latency"]
            latency_scores = {
                "ultra_low": 90,
                "low": 80,
                "medium": 70,
                "high": 60
            }
            score = latency_scores.get(latency, 70)
            
            # Adjust based on architecture
            if primary["architecture"] == "virtual_machines" and latency in ["ultra_low", "low"]:
                score += 10
            elif primary["architecture"] == "serverless" and latency == "ultra_low":
                score -= 5  # Cold starts can affect ultra-low latency
            
        elif factor_name == "scalability":
            # Serverless has best scalability
            arch_scores = {
                "serverless": 95,
                "containers": 80,
                "virtual_machines": 70
            }
            score = arch_scores.get(primary["architecture"], 75)
            
            # Adjust for traffic pattern
            traffic_pattern = workload["scale"]["traffic_pattern"]
            if traffic_pattern in ["variable", "bursty", "seasonal"]:
                if primary["architecture"] == "serverless":
                    score += 5  # Serverless excels at variable traffic
            
        elif factor_name == "operational_complexity":
            # Simpler = higher score
            complexity_scores = {
                "serverless": 90,
                "virtual_machines": 60,
                "containers": 50
            }
            score = complexity_scores.get(primary["architecture"], 65)
            
            # Adjust for team experience
            team_exp = user_context["team_experience"]
            if team_exp in ["beginner", "junior"] and primary["architecture"] == "serverless":
                score += 10  # Serverless is good for beginners
            elif team_exp in ["expert"] and primary["architecture"] == "containers":
                score += 10  # Experts can handle containers
            
        elif factor_name == "reliability":
            # All architectures are reliable on GCP
            score = 85
            
            # Adjust for availability requirements
            availability = workload["requirements"]["availability"]
            if availability == "critical":
                score += 5  # GCP provides high reliability
            
        elif factor_name == "time_to_market":
            # Faster deployment = higher score
            speed_scores = {
                "serverless": 90,
                "virtual_machines": 70,
                "containers": 60
            }
            score = speed_scores.get(primary["architecture"], 70)
            
            # Adjust for timeline urgency
            timeline = user_context["time_to_market"]
            if timeline == "immediate" and primary["architecture"] == "serverless":
                score += 10  # Serverless fastest to deploy
        
        else:
            score = 70  # Default score
        
        return min(max(score, 0), 100)
    
    def _categorize_recommendation(self, score: float) -> str:
        """Categorize recommendation based on score"""
        if score >= 85:
            return "strong_recommendation"
        elif score >= 70:
            return "good_recommendation"
        elif score >= 55:
            return "moderate_recommendation"
        elif score >= 40:
            return "weak_recommendation"
        else:
            return "not_recommended"
    
    def _identify_decision_factors(self, analysis_data: Dict[str, Any],
                                  tradeoff_scores: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Identify key decision factors"""
        
        user_context = analysis_data["user_context"]
        strongest_factors = tradeoff_scores["strongest_factors"]
        
        factors = []
        
        # Always include budget if sensitive
        if user_context["budget_sensitivity"] in ["high", "very_high"]:
            factors.append({
                "factor": "Budget Constraints",
                "priority": "critical",
                "impact": "Cost was the primary driver in architecture selection",
                "evidence": f"Budget sensitivity: {user_context['budget_sensitivity']}"
            })
        
        # Include strongest tradeoff factors
        for factor_name in strongest_factors[:2]:
            factor_info = self.tradeoff_factors[factor_name]
            factors.append({
                "factor": factor_name.title(),
                "priority": "high",
                "impact": f"This recommendation excels in {factor_name}",
                "evidence": f"Score: {tradeoff_scores['factor_scores'][factor_name]['score']:.0f}/100"
            })
        
        # Include team experience if not intermediate
        team_exp = user_context["team_experience"]
        if team_exp not in ["intermediate"]:
            factors.append({
                "factor": "Team Experience",
                "priority": "medium",
                "impact": f"Architecture selected to match {team_exp} team capability",
                "evidence": f"Team level: {team_exp}"
            })
        
        # Include timeline if urgent
        if user_context["time_to_market"] == "immediate":
            factors.append({
                "factor": "Time to Market",
                "priority": "high",
                "impact": "Selected for fastest deployment capability",
                "evidence": "Timeline: Immediate"
            })
        
        return factors
    
    def _calculate_analysis_quality(self, structured_analysis: Dict[str, Any]) -> float:
        """Calculate analysis quality score"""
        quality_factors = []
        
        # Executive summary quality
        exec_summary = structured_analysis.get("executive_summary", "")
        if len(exec_summary.split()) >= 20:  # At least 20 words
            quality_factors.append(0.9)
        else:
            quality_factors.append(0.6)
        
        # Advantages count
        advantages = structured_analysis.get("primary_advantages", [])
        if len(advantages) >= 3:
            quality_factors.append(0.9)
        else:
            quality_factors.append(0.6)
        
        # Risks count
        risks = structured_analysis.get("primary_risks", [])
        if len(risks) >= 2:
            quality_factors.append(0.8)  # Having risks shows balanced analysis
        else:
            quality_factors.append(0.5)
        
        # Recommendation strength
        strength = structured_analysis.get("recommendation_strength", 50)
        quality_factors.append(strength / 100)
        
        # Analysis source bonus
        source = structured_analysis.get("analysis_source", "")
        if source == "gemini_api":
            quality_factors.append(0.95)
        else:
            quality_factors.append(0.75)
        
        # Calculate average quality
        avg_quality = sum(quality_factors) / len(quality_factors)
        
        return round(avg_quality * 100, 1)  # Convert to 0-100 scale
    
    def _enhance_analysis_result(self, structured_analysis: Dict[str, Any],
                                tradeoff_scores: Dict[str, Any],
                                decision_factors: List[Dict[str, Any]],
                                phase1_result: Dict[str, Any],
                                phase2_result: Dict[str, Any],
                                phase3_result: Dict[str, Any],
                                phase4_result: Dict[str, Any],
                                processing_time_ms: int,
                                analysis_method: str,
                                user_id: str,
                                session_id: str,
                                request_id: str) -> Dict[str, Any]:
        """Enhance analysis result with metadata"""
        
        intent_analysis = phase1_result["intent_analysis"]
        architecture_analysis = phase2_result["architecture_analysis"]
        
        # RECONCILE recommendation_strength with overall_score
        # overall_score is the mathematical result from factor analysis
        # recommendation_strength should align with it to avoid confusion
        overall_score = tradeoff_scores.get("overall_score", 50)
        raw_strength = structured_analysis.get("recommendation_strength", 50)
        recommendation_category = tradeoff_scores.get("recommendation_category", "moderate_recommendation")
        
        # Align recommendation_strength to match the category from overall_score
        # This prevents contradictions like "95 strength" with "weak_recommendation"
        if recommendation_category == "strong_recommendation":
            aligned_strength = max(85, min(100, int((overall_score + raw_strength) / 2)))
        elif recommendation_category == "good_recommendation":
            aligned_strength = max(70, min(84, int((overall_score + raw_strength) / 2)))
        elif recommendation_category == "moderate_recommendation":
            aligned_strength = max(55, min(69, int((overall_score + raw_strength) / 2)))
        elif recommendation_category == "weak_recommendation":
            aligned_strength = max(40, min(54, int((overall_score + raw_strength) / 2)))
        else:  # not_recommended
            aligned_strength = max(0, min(39, int(overall_score)))
        
        # Update structured_analysis with aligned strength
        structured_analysis["recommendation_strength"] = aligned_strength
        structured_analysis["original_strength"] = raw_strength
        structured_analysis["overall_score_alignment"] = overall_score
        
        enhanced = {
            "request_id": request_id,
            "user_id": user_id,
            "session_id": session_id,
            "phase": self.phase_name,
            "phase_version": self.phase_version,
            "timestamp": datetime.utcnow().isoformat(),
            "status": "completed",
            
            "analysis_id": f"analysis_{uuid.uuid4().hex[:8]}",
            
            "analysis_inputs": {
                "workload_type": intent_analysis["workload_type"],
                "primary_architecture": architecture_analysis["primary_architecture"],
                "recommendation_confidence": architecture_analysis["confidence"],
                "monthly_users": intent_analysis["scale"]["monthly_users"],
                "team_experience": intent_analysis["constraints"]["team_experience"],
                "budget_sensitivity": intent_analysis["constraints"]["budget_sensitivity"]
            },
            
            "qualitative_analysis": structured_analysis,
            
            "quantitative_analysis": {
                "tradeoff_scores": tradeoff_scores,
                "decision_factors": decision_factors,
                "visual_scorecard": structured_analysis.get("visual_scorecard", {}),
                "quantitative_metrics": structured_analysis.get("quantitative_metrics", {})
            },
            
            "processing_metadata": {
                "processing_time_ms": processing_time_ms,
                "analysis_method": analysis_method,
                "gemini_mode": "api" if not self.gemini.mock_mode else "mock",
                "llm_model": structured_analysis.get("llm_model", "unknown"),
                "analysis_quality_score": self._calculate_analysis_quality(structured_analysis),
                "analysis_completeness": self._calculate_analysis_completeness(structured_analysis)
            },
            
            "presentation_ready": {
                "executive_summary": structured_analysis["executive_summary"],
                "recommendation_strength": structured_analysis["recommendation_strength"],
                "key_advantages": structured_analysis["primary_advantages"][:3],
                "key_risks": structured_analysis["primary_risks"][:2],
                "top_decision_factors": decision_factors[:3],
                "next_steps": structured_analysis["next_step_recommendations"][:3]
            },
            
            "next_phase": "recommendation_presentation",
            "phase_transition": {
                "recommended": True,
                "estimated_time_seconds": 15,
                "prerequisites_met": True,
                "required_input": {
                    "analysis_summary": structured_analysis["executive_summary"],
                    "recommendation_strength": structured_analysis["recommendation_strength"],
                    "key_points": {
                        "advantages": structured_analysis["primary_advantages"],
                        "risks": structured_analysis["primary_risks"],
                        "tradeoffs": structured_analysis["tradeoff_matrix"]
                    }
                }
            }
        }
        
        return enhanced
    
    def _calculate_analysis_completeness(self, structured_analysis: Dict[str, Any]) -> float:
        """Calculate analysis completeness percentage"""
        required_sections = [
            "executive_summary", "recommendation_strength",
            "primary_advantages", "primary_risks",
            "tradeoff_matrix", "decision_factors",
            "risk_assessment", "next_step_recommendations"
        ]
        
        present_sections = 0
        for section in required_sections:
            if section in structured_analysis and structured_analysis[section]:
                if isinstance(structured_analysis[section], (list, dict)):
                    if structured_analysis[section]:  # Not empty
                        present_sections += 1
                elif structured_analysis[section]:  # Not empty string
                    present_sections += 1
        
        completeness = (present_sections / len(required_sections)) * 100
        return round(completeness, 1)
    
    def _emit_success_telemetry(self, result: Dict[str, Any], processing_time_ms: int):
        """Emit success telemetry"""
        analysis_inputs = result["analysis_inputs"]
        qualitative = result["qualitative_analysis"]
        quantitative = result["quantitative_analysis"]
        
        # Emit recommendation strength metric
        self.telemetry.submit_metric(
            name="ai.tradeoff.analysis.strength",
            value=qualitative["recommendation_strength"],
            tags=[
                f"architecture:{analysis_inputs['primary_architecture']}",
                f"workload_type:{analysis_inputs['workload_type']}",
                f"phase:{self.phase_name}",
                f"analysis_method:{result['processing_metadata']['analysis_method']}",
                f"team_experience:{analysis_inputs['team_experience']}",
                f"budget_sensitivity:{analysis_inputs['budget_sensitivity']}"
            ]
        )
        
        # Emit analysis quality metric
        self.telemetry.submit_metric(
            name="ai.tradeoff.analysis.quality",
            value=result["processing_metadata"]["analysis_quality_score"],
            tags=[
                f"architecture:{analysis_inputs['primary_architecture']}",
                f"workload_type:{analysis_inputs['workload_type']}",
                f"phase:{self.phase_name}",
                f"analysis_method:{result['processing_metadata']['analysis_method']}"
            ]
        )
        
        # Emit overall tradeoff score
        if "tradeoff_scores" in quantitative:
            self.telemetry.submit_metric(
                name="ai.tradeoff.analysis.overall_score",
                value=quantitative["tradeoff_scores"]["overall_score"],
                tags=[
                    f"architecture:{analysis_inputs['primary_architecture']}",
                    f"workload_type:{analysis_inputs['workload_type']}",
                    f"phase:{self.phase_name}",
                    f"recommendation_category:{quantitative['tradeoff_scores']['recommendation_category']}"
                ]
            )
        
        # Emit processing time metric
        self.telemetry.submit_metric(
            name="ai.tradeoff.analysis.processing.time_ms",
            value=processing_time_ms,
            tags=[
                f"workload_type:{analysis_inputs['workload_type']}",
                f"phase:{self.phase_name}",
                f"success:true",
                f"analysis_method:{result['processing_metadata']['analysis_method']}"
            ]
        )
        
        # Emit success log
        self.telemetry.submit_log(
            source="cloud-sentinel",
            message={
                "event": "tradeoff_analysis_generated",
                "analysis_id": result["analysis_id"],
                "request_id": result["request_id"],
                "user_id": result["user_id"],
                "session_id": result["session_id"],
                "workload_type": analysis_inputs["workload_type"],
                "architecture": analysis_inputs["primary_architecture"],
                "recommendation_strength": qualitative["recommendation_strength"],
                "analysis_quality": result["processing_metadata"]["analysis_quality_score"],
                "analysis_method": result["processing_metadata"]["analysis_method"],
                "processing_time_ms": processing_time_ms,
                "executive_summary_preview": qualitative["executive_summary"][:200] + "..."
            },
            tags=[
                "tradeoff_analysis", 
                "success", 
                analysis_inputs["primary_architecture"],
                f"phase:{self.phase_name}",
                f"strength:{qualitative['recommendation_strength']}"
            ]
        )
        
        # Emit success event
        self.telemetry.emit_event(
            title="Tradeoff Analysis Generated",
            text=f"Generated analysis for {analysis_inputs['workload_type']} on {analysis_inputs['primary_architecture']} with {qualitative['recommendation_strength']}/100 strength",
            tags=[
                "tradeoff_analysis",
                analysis_inputs["primary_architecture"],
                f"strength:{qualitative['recommendation_strength']}",
                f"quality:{result['processing_metadata']['analysis_quality_score']}",
                f"workload:{analysis_inputs['workload_type']}",
                f"user:{result['user_id']}",
                f"phase:{self.phase_name}"
            ],
            alert_type="success"
        )
    
    def _create_error_result(self, user_id: str, session_id: str, request_id: str,
                           phase1_result: Dict[str, Any], phase2_result: Dict[str, Any],
                           phase3_result: Dict[str, Any], phase4_result: Dict[str, Any],
                           error_message: str, processing_time_ms: int) -> Dict[str, Any]:
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
                "code": "TRADEOFF_ANALYSIS_FAILED",
                "phase_summary": {
                    "workload_type": phase1_result.get("intent_analysis", {}).get("workload_type", "unknown"),
                    "architecture": phase2_result.get("architecture_analysis", {}).get("primary_architecture", "unknown"),
                    "price": phase4_result.get("primary_price", {}).get("total_monthly_usd", "unknown")
                }
            },
            "processing_metadata": {
                "processing_time_ms": processing_time_ms,
                "analysis_method": "failed",
                "attempted_retry": False
            },
            "fallback_analysis": {
                "executive_summary": "System temporarily unavailable. Basic analysis suggests the selected architecture is appropriate based on your requirements.",
                "recommendation_strength": 60,
                "key_points": [
                    "Architecture selected matches workload type",
                    "Cost appears competitive",
                    "Consider verifying with team expertise"
                ]
            }
        }
    
    def _emit_error_telemetry(self, error_result: Dict[str, Any], error_message: str):
        """Emit error telemetry"""
        self.telemetry.submit_metric(
            name="ai.tradeoff.analysis.processing.time_ms",
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
                "event": "tradeoff_analysis_failed",
                "request_id": error_result["request_id"],
                "user_id": error_result["user_id"],
                "error": error_result["error"],
                "processing_time_ms": error_result["processing_metadata"]["processing_time_ms"]
            },
            tags=[
                "tradeoff_analysis", 
                "error", 
                error_result["error"]["code"],
                f"phase:{self.phase_name}"
            ]
        )
        
        self.telemetry.emit_event(
            title="Tradeoff Analysis Failed",
            text=f"Failed to generate tradeoff analysis: {error_message}",
            tags=[
                "tradeoff_analysis_error",
                f"error_code:{error_result['error']['code']}",
                f"user:{error_result['user_id']}",
                f"phase:{self.phase_name}"
            ],
            alert_type="error",
            priority="high"
        )
    
    def _update_statistics(self, analysis_quality: float, processing_time_ms: int):
        """Update phase statistics"""
        self.stats["avg_analysis_quality"] = (
            (self.stats["avg_analysis_quality"] * (self.stats["total_analyses"] - 1) + analysis_quality) 
            / self.stats["total_analyses"]
            if self.stats["total_analyses"] > 0 
            else analysis_quality
        )
        
        self.stats["total_processing_time_ms"] += processing_time_ms
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get phase statistics"""
        total = self.stats["total_analyses"]
        
        stats = self.stats.copy()
        
        if total > 0:
            stats["avg_processing_time_ms"] = self.stats["total_processing_time_ms"] / total
            stats["gemini_usage_percent"] = (self.stats["gemini_analyses"] / total * 100) if total > 0 else 0
        else:
            stats["avg_processing_time_ms"] = 0.0
            stats["gemini_usage_percent"] = 0.0
        
        stats["phase_name"] = self.phase_name
        stats["phase_version"] = self.phase_version
        stats["tradeoff_factors"] = len(self.tradeoff_factors)
        stats["gemini_status"] = self.gemini.get_status()
        stats["telemetry_status"] = self.telemetry.get_status()
        
        return stats
    
    def reset_statistics(self):
        """Reset phase statistics"""
        self.stats = {
            "total_analyses": 0,
            "gemini_analyses": 0,
            "rule_based_analyses": 0,
            "total_processing_time_ms": 0,
            "avg_analysis_quality": 0.0
        }
        logger.info("📊 Phase 5 statistics reset")
    
    def get_status(self) -> Dict[str, Any]:
        """Get complete phase status"""
        return {
            "phase": self.phase_name,
            "version": self.phase_version,
            "initialized": True,
            "gemini_available": not self.gemini.mock_mode,
            "telemetry_available": self.telemetry.config.mode != TelemetryMode.DISABLED,
            "tradeoff_factors_configured": len(self.tradeoff_factors),
            "statistics": self.get_statistics()
        }