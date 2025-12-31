"""
Phase 4: Real Pricing Calculation
Production-grade implementation with GCP Billing API integration
"""

import time
import logging
import json
from datetime import datetime
from typing import Dict, Any, Optional, List
import uuid
import random

from ..core.gemini_client import GeminiClient
from ..core.gcp_pricing_client import GCPPricingClient, PriceEstimate
from ..telemetry.datadog_client import TelemetryClient, TelemetryConfig, TelemetryMode

logger = logging.getLogger(__name__)

class PricingCalculationPhase:
    """Complete Phase 4: Real Pricing Calculation"""
    
    def __init__(self, telemetry_config: Optional[TelemetryConfig] = None):
        self.phase_name = "pricing_calculation"
        self.phase_version = "1.0.0"
        
        # Initialize clients
        self.gemini = GeminiClient()
        self.telemetry = TelemetryClient(telemetry_config)
        self.pricing_client = GCPPricingClient()
        
        # Accuracy tracking
        self.accuracy_stats = {
            "total_calculations": 0,
            "api_calculations": 0,
            "fallback_calculations": 0,
            "total_processing_time_ms": 0,
            "estimated_accuracy_sum": 0.0
        }
        
        # Region cost multipliers (simplified)
        self.region_multipliers = {
            "us-east": 1.0,
            "us-west": 1.05,
            "europe": 1.15,
            "asia": 1.10,
            "australia": 1.25,
            "india": 1.08,
            "global": 1.0
        }
        
        logger.info(f"✅ Phase 4 initialized: {self.phase_name} v{self.phase_version}")
        logger.info(f"💰 Pricing client status: {self.pricing_client.get_status()}")
    
    async def process(self, phase1_result: Dict[str, Any], 
                     phase2_result: Dict[str, Any],
                     phase3_result: Dict[str, Any],
                     user_id: Optional[str] = None,
                     session_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Calculate real pricing using GCP Billing API
        
        Args:
            phase1_result: Complete output from Phase 1
            phase2_result: Complete output from Phase 2
            phase3_result: Complete output from Phase 3
            user_id: User identifier
            session_id: Session identifier
            
        Returns:
            Dict containing pricing calculation with full context
        """
        start_time = time.time()
        
        # Validate inputs
        self._validate_inputs(phase1_result, phase2_result, phase3_result)
        
        self.accuracy_stats["total_calculations"] += 1
        
        # Extract data from previous phases
        intent_analysis = phase1_result["intent_analysis"]
        architecture_analysis = phase2_result["architecture_analysis"]
        specification_analysis = phase3_result["specification_analysis"]
        configuration = phase3_result["configuration"]
        
        workload_type = intent_analysis["workload_type"]
        scale = intent_analysis["scale"]
        requirements = intent_analysis["requirements"]
        architecture = architecture_analysis["primary_architecture"]
        machine_type = specification_analysis.get("exact_type")
        
        # Use IDs from previous phases
        request_id = phase1_result.get("request_id", f"req_{int(time.time())}_{uuid.uuid4().hex[:6]}")
        user_id = user_id or phase1_result.get("user_id", f"user_{uuid.uuid4().hex[:8]}")
        session_id = session_id or phase1_result.get("session_id", f"session_{uuid.uuid4().hex[:8]}")
        
        try:
            logger.info(f"💰 Pricing calculation - Architecture: {architecture}, Machine: {machine_type}")
            
            # Step 1: Calculate primary price
            calculation_method = "gcp_api"
            try:
                primary_estimate = self.pricing_client.calculate_total_cost(
                    architecture=architecture,
                    machine_type=machine_type,
                    workload_type=workload_type,
                    region=requirements["geography"],
                    cpu=specification_analysis.get("cpu", 4),
                    ram=specification_analysis.get("ram", 8),
                    estimated_rps=scale["estimated_rps"],
                    monthly_users=scale["monthly_users"]
                )
                
                if self.pricing_client.mock_mode:
                    calculation_method = "mock_fallback"
                    self.accuracy_stats["fallback_calculations"] += 1
                else:
                    self.accuracy_stats["api_calculations"] += 1
                    
            except Exception as e:
                logger.warning(f"Primary price calculation failed, using fallback: {e}")
                primary_estimate = self._calculate_fallback_price(
                    architecture, machine_type, workload_type, scale, specification_analysis
                )
                calculation_method = "error_fallback"
                self.accuracy_stats["fallback_calculations"] += 1
            
            # Step 2: Calculate alternative prices
            alternative_architectures = ["serverless", "containers", "virtual_machines"]
            alternative_prices = self.pricing_client.calculate_alternative_prices(
                primary_estimate, alternative_architectures
            )
            
            # Step 3: Calculate accuracy estimate
            accuracy_estimate = self._estimate_pricing_accuracy(
                calculation_method, primary_estimate, architecture
            )
            
            # Step 4: Calculate processing time
            processing_time_ms = int((time.time() - start_time) * 1000)
            
            # Step 5: Calculate savings potential
            savings_analysis = self._analyze_savings_potential(
                primary_estimate, alternative_prices, architecture_analysis
            )
            
            # Step 6: Enhance result with metadata
            enhanced_result = self._enhance_pricing_result(
                primary_estimate,
                alternative_prices,
                accuracy_estimate,
                savings_analysis,
                phase1_result,
                phase2_result,
                phase3_result,
                processing_time_ms,
                calculation_method,
                user_id,
                session_id,
                request_id
            )
            
            # Step 7: Update statistics
            self._update_statistics(accuracy_estimate, processing_time_ms)
            
            # Step 8: Emit telemetry
            self._emit_success_telemetry(enhanced_result, processing_time_ms)
            
            logger.info(f"✅ Price calculated: ${primary_estimate.total_monthly_usd:.2f}/month")
            logger.info(f"   Accuracy: {accuracy_estimate*100:.1f}%")
            logger.info(f"   Method: {calculation_method}")
            logger.info(f"   Time: {processing_time_ms}ms")
            
            return enhanced_result
            
        except Exception as e:
            # Handle failures gracefully
            processing_time_ms = int((time.time() - start_time) * 1000)
            
            error_result = self._create_error_result(
                user_id, session_id, request_id, 
                phase1_result, phase2_result, phase3_result, str(e), processing_time_ms
            )
            
            self._emit_error_telemetry(error_result, str(e))
            
            logger.error(f"❌ Pricing calculation failed: {e}")
            raise
    
    def _validate_inputs(self, phase1_result: Dict[str, Any], 
                        phase2_result: Dict[str, Any], 
                        phase3_result: Dict[str, Any]):
        """Validate all input phases"""
        if not phase1_result or "intent_analysis" not in phase1_result:
            raise ValueError("Invalid Phase 1 result. Missing intent_analysis")
        
        if not phase2_result or "architecture_analysis" not in phase2_result:
            raise ValueError("Invalid Phase 2 result. Missing architecture_analysis")
        
        if not phase3_result or "specification_analysis" not in phase3_result:
            raise ValueError("Invalid Phase 3 result. Missing specification_analysis")
        
        # Validate required fields
        intent_analysis = phase1_result["intent_analysis"]
        required_fields = ["workload_type", "scale", "requirements"]
        for field in required_fields:
            if field not in intent_analysis:
                raise ValueError(f"Missing required field in intent_analysis: {field}")
    
    def _calculate_fallback_price(self, architecture: str, machine_type: Optional[str],
                                 workload_type: str, scale: Dict[str, Any],
                                 specification_analysis: Dict[str, Any]) -> PriceEstimate:
        """Calculate fallback price when API is unavailable"""
        logger.info("📊 Using fallback pricing calculation")
        
        # Base price based on architecture
        base_prices = {
            "serverless": 200,
            "containers": 300,
            "virtual_machines": 250
        }
        
        base_price = base_prices.get(architecture, 250)
        
        # Adjust for machine type
        machine_adjustment = 1.0
        if machine_type:
            if "highmem" in machine_type.lower():
                machine_adjustment *= 1.5
            if "highcpu" in machine_type.lower():
                machine_adjustment *= 1.3
            if "standard" in machine_type.lower():
                machine_adjustment *= 1.0
        
        # Adjust for scale
        monthly_users = scale["monthly_users"]
        if monthly_users < 1000:
            scale_factor = 0.3
        elif monthly_users < 10000:
            scale_factor = 0.6
        elif monthly_users < 100000:
            scale_factor = 1.0
        elif monthly_users < 1000000:
            scale_factor = 2.0
        else:
            scale_factor = 4.0
        
        # Adjust for workload type
        workload_multipliers = {
            "api_backend": 1.0,
            "web_app": 1.2,
            "data_processing": 1.8,
            "ml_inference": 3.0,
            "batch_processing": 1.5,
            "realtime_streaming": 2.0,
            "mobile_backend": 1.1,
            "gaming_server": 2.5
        }
        
        workload_factor = workload_multipliers.get(workload_type, 1.0)
        
        # Calculate total
        total_price = base_price * machine_adjustment * scale_factor * workload_factor
        
        # Create mock components
        from ..core.gcp_pricing_client import PriceComponent
        
        components = [
            PriceComponent(
                service="Compute",
                sku="Fallback",
                description=f"Fallback {architecture} compute",
                usage_unit="month",
                pricing_unit="month",
                price_per_unit=total_price * 0.6,
                estimated_usage=1,
                estimated_cost=total_price * 0.6,
                region="global"
            ),
            PriceComponent(
                service="Database",
                sku="Fallback",
                description="Fallback database",
                usage_unit="month",
                pricing_unit="month",
                price_per_unit=total_price * 0.2,
                estimated_usage=1,
                estimated_cost=total_price * 0.2,
                region="global"
            ),
            PriceComponent(
                service="Storage",
                sku="Fallback",
                description="Fallback storage",
                usage_unit="month",
                pricing_unit="month",
                price_per_unit=total_price * 0.1,
                estimated_usage=1,
                estimated_cost=total_price * 0.1,
                region="global"
            ),
            PriceComponent(
                service="Networking",
                sku="Fallback",
                description="Fallback networking",
                usage_unit="month",
                pricing_unit="month",
                price_per_unit=total_price * 0.1,
                estimated_usage=1,
                estimated_cost=total_price * 0.1,
                region="global"
            )
        ]
        
        return PriceEstimate(
            total_monthly_usd=total_price,
            components=components,
            region="global",
            architecture=architecture,
            machine_type=machine_type,
            timestamp=datetime.now(),
            confidence=0.7,  # Lower confidence for fallback
            cache_hit=False
        )
    
    def _estimate_pricing_accuracy(self, calculation_method: str,
                                  price_estimate: PriceEstimate,
                                  architecture: str) -> float:
        """Estimate pricing accuracy based on calculation method"""
        base_accuracy = price_estimate.confidence
        
        # Adjust based on calculation method
        method_accuracy = {
            "gcp_api": 0.95,
            "mock_fallback": 0.85,
            "error_fallback": 0.75
        }
        
        method_acc = method_accuracy.get(calculation_method, 0.8)
        
        # Adjust based on architecture
        architecture_accuracy = {
            "serverless": 0.90,  # Serverless pricing is predictable
            "containers": 0.85,
            "virtual_machines": 0.95  # VM pricing is most accurate
        }
        
        arch_acc = architecture_accuracy.get(architecture, 0.85)
        
        # Combined accuracy
        accuracy = (base_accuracy + method_acc + arch_acc) / 3
        
        return min(max(accuracy, 0.5), 0.99)
    
    def _analyze_savings_potential(self, primary_estimate: PriceEstimate,
                                  alternative_prices: Dict[str, float],
                                  architecture_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze savings potential vs alternatives"""
        primary_price = primary_estimate.total_monthly_usd
        primary_arch = primary_estimate.architecture
        
        savings = {}
        best_alternative = None
        best_savings = 0
        
        for alt_arch, alt_price in alternative_prices.items():
            if alt_arch == primary_arch:
                continue
            
            saving_amount = primary_price - alt_price
            saving_percent = (saving_amount / primary_price * 100) if primary_price > 0 else 0
            
            savings[alt_arch] = {
                "price": alt_price,
                "savings_amount": round(saving_amount, 2),
                "savings_percent": round(saving_percent, 1)
            }
            
            if saving_amount > best_savings:
                best_savings = saving_amount
                best_alternative = alt_arch
        
        # Calculate waste potential
        waste_potential = self._calculate_waste_potential(primary_estimate)
        
        # Identify optimization opportunities
        optimizations = self._identify_pricing_optimizations(
            primary_estimate, architecture_analysis
        )
        
        return {
            "alternative_prices": savings,
            "best_alternative": best_alternative,
            "potential_monthly_savings": round(best_savings, 2) if best_alternative else 0,
            "waste_potential_percent": waste_potential,
            "optimization_opportunities": optimizations,
            "commitment_discount_eligible": self._check_commitment_eligibility(primary_estimate),
            "spot_instance_savings": self._calculate_spot_savings(primary_estimate)
        }
    
    def _calculate_waste_potential(self, price_estimate: PriceEstimate) -> float:
        """Calculate potential waste percentage"""
        # Analyze components for over-provisioning
        total_cost = price_estimate.total_monthly_usd
        
        # Check for components that might be over-provisioned
        waste_factors = []
        
        for component in price_estimate.components:
            # High fixed costs with low utilization potential
            if component.usage_unit == "hour" and component.price_per_unit > 0.1:
                waste_factors.append(0.2)  # 20% potential waste
            elif "Storage" in component.description and component.estimated_usage > 100:
                waste_factors.append(0.3)  # 30% potential waste
        
        if waste_factors:
            avg_waste = sum(waste_factors) / len(waste_factors)
        else:
            avg_waste = 0.1  # Default 10% waste
        
        return round(avg_waste * 100, 1)
    
    def _identify_pricing_optimizations(self, price_estimate: PriceEstimate,
                                       architecture_analysis: Dict[str, Any]) -> List[str]:
        """Identify pricing optimization opportunities"""
        optimizations = []
        
        # Commitment discounts
        if price_estimate.total_monthly_usd > 500:
            optimizations.append("Consider committed use discounts (up to 57% savings for 1-year commitment)")
        
        # Spot/Preemptible instances
        if architecture_analysis["primary_architecture"] in ["containers", "virtual_machines"]:
            optimizations.append("Preemptible VMs available for 60-91% cost savings on fault-tolerant workloads")
        
        # Sustained use discounts
        if not self.pricing_client.mock_mode:
            optimizations.append("Automatic sustained use discounts apply after 25% monthly usage")
        
        # Right-sizing opportunities
        compute_components = [c for c in price_estimate.components if "Compute" in c.service or "GKE" in c.service]
        if compute_components:
            total_compute = sum(c.estimated_cost for c in compute_components)
            if total_compute > price_estimate.total_monthly_usd * 0.7:
                optimizations.append("Compute represents >70% of cost - consider right-sizing instances")
        
        # Storage tier optimization
        storage_components = [c for c in price_estimate.components if "Storage" in c.service]
        for storage in storage_components:
            if storage.estimated_usage > 1000 and "Standard" in storage.description:
                optimizations.append(f"Consider Nearline/Coldline storage for {storage.description} (up to 70% savings)")
        
        if not optimizations:
            optimizations.append("Configuration appears cost-optimized for current requirements")
        
        return optimizations
    
    def _check_commitment_eligibility(self, price_estimate: PriceEstimate) -> Dict[str, Any]:
        """Check commitment discount eligibility"""
        eligible = price_estimate.total_monthly_usd > 300
        
        if eligible:
            return {
                "eligible": True,
                "minimum_commitment_usd": 300,
                "potential_savings_percent": {
                    "1_year": 37,
                    "3_year": 55
                },
                "recommendation": "Commit to 1-year for 37% savings or 3-year for 55% savings"
            }
        else:
            return {
                "eligible": False,
                "reason": "Monthly spend below commitment threshold",
                "minimum_required": 300
            }
    
    def _calculate_spot_savings(self, price_estimate: PriceEstimate) -> Dict[str, Any]:
        """Calculate spot instance savings potential"""
        if price_estimate.architecture not in ["containers", "virtual_machines"]:
            return {"available": False, "reason": "Spot instances only available for VMs and containers"}
        
        compute_components = [c for c in price_estimate.components if "Compute" in c.service]
        total_compute = sum(c.estimated_cost for c in compute_components)
        
        return {
            "available": True,
            "potential_savings_percent": 70,
            "estimated_monthly_savings": round(total_compute * 0.7, 2),
            "recommended_for": ["batch_processing", "data_processing", "ml_training"],
            "risks": ["Preemption with 30-second warning", "Not suitable for stateful workloads"]
        }
    
    def _enhance_pricing_result(self, primary_estimate: PriceEstimate,
                               alternative_prices: Dict[str, float],
                               accuracy_estimate: float,
                               savings_analysis: Dict[str, Any],
                               phase1_result: Dict[str, Any],
                               phase2_result: Dict[str, Any],
                               phase3_result: Dict[str, Any],
                               processing_time_ms: int,
                               calculation_method: str,
                               user_id: str,
                               session_id: str,
                               request_id: str) -> Dict[str, Any]:
        """Enhance pricing result with metadata"""
        
        intent_analysis = phase1_result["intent_analysis"]
        architecture_analysis = phase2_result["architecture_analysis"]
        specification_analysis = phase3_result["specification_analysis"]
        
        enhanced = {
            "request_id": request_id,
            "user_id": user_id,
            "session_id": session_id,
            "phase": self.phase_name,
            "phase_version": self.phase_version,
            "timestamp": datetime.utcnow().isoformat(),
            "status": "completed",
            
            "pricing_inputs": {
                "workload_type": intent_analysis["workload_type"],
                "architecture": architecture_analysis["primary_architecture"],
                "machine_type": specification_analysis.get("exact_type", "unknown"),
                "region": intent_analysis["requirements"]["geography"],
                "monthly_users": intent_analysis["scale"]["monthly_users"],
                "estimated_rps": intent_analysis["scale"]["estimated_rps"]
            },
            
            "primary_price": {
                "total_monthly_usd": round(primary_estimate.total_monthly_usd, 2),
                "confidence": primary_estimate.confidence,
                "calculation_method": calculation_method,
                "components": primary_estimate.to_dict()["components"],
                "region": primary_estimate.region,
                "timestamp": primary_estimate.timestamp.isoformat() if primary_estimate.timestamp else None
            },
            
            "alternative_prices": alternative_prices,
            
            "pricing_accuracy": {
                "estimated_accuracy": round(accuracy_estimate, 3),
                "calculation_method": calculation_method,
                "confidence_factors": {
                    "api_availability": not self.pricing_client.mock_mode,
                    "architecture_complexity": "low" if architecture_analysis["primary_architecture"] == "serverless" else "medium",
                    "data_freshness": "recent" if calculation_method == "gcp_api" else "estimated"
                }
            },
            
            "savings_analysis": savings_analysis,
            
            "processing_metadata": {
                "processing_time_ms": processing_time_ms,
                "calculation_method": calculation_method,
                "pricing_api_available": not self.pricing_client.mock_mode,
                "cache_used": primary_estimate.cache_hit,
                "components_calculated": len(primary_estimate.components)
            },
            
            "business_impact": {
                "affordability_tier": self._determine_affordability_tier(primary_estimate.total_monthly_usd),
                "roi_estimate_months": self._estimate_roi(primary_estimate, intent_analysis),
                "budget_alignment": self._assess_budget_alignment(
                    primary_estimate.total_monthly_usd,
                    intent_analysis["constraints"]["budget_sensitivity"]
                )
            },
            
            "next_phase": "tradeoff_analysis",
            "phase_transition": {
                "recommended": True,
                "estimated_time_seconds": 15,
                "prerequisites_met": True,
                "required_input": {
                    "primary_price": primary_estimate.total_monthly_usd,
                    "alternative_prices": alternative_prices,
                    "architecture": architecture_analysis["primary_architecture"]
                }
            }
        }
        
        return enhanced
    
    def _determine_affordability_tier(self, monthly_price: float) -> str:
        """Determine affordability tier"""
        if monthly_price < 100:
            return "very_low"
        elif monthly_price < 500:
            return "low"
        elif monthly_price < 2000:
            return "medium"
        elif monthly_price < 10000:
            return "high"
        else:
            return "enterprise"
    
    def _estimate_roi(self, price_estimate: PriceEstimate, intent_analysis: Dict[str, Any]) -> int:
        """Estimate ROI in months"""
        monthly_cost = price_estimate.total_monthly_usd
        
        # Very simplified ROI calculation
        if monthly_cost < 500:
            return 1  # 1 month ROI for small projects
        elif monthly_cost < 2000:
            return 3  # 3 months ROI for medium projects
        elif monthly_cost < 10000:
            return 6  # 6 months ROI for large projects
        else:
            return 12  # 12 months ROI for enterprise
    
    def _assess_budget_alignment(self, monthly_price: float, budget_sensitivity: str) -> Dict[str, Any]:
        """Assess alignment with budget sensitivity"""
        budget_tiers = {
            "very_low": 10000,
            "low": 5000,
            "medium": 2000,
            "high": 500
        }
        
        budget_limit = budget_tiers.get(budget_sensitivity, 2000)
        
        within_budget = monthly_price <= budget_limit
        percentage_of_budget = (monthly_price / budget_limit * 100) if budget_limit > 0 else 100
        
        return {
            "within_budget": within_budget,
            "budget_limit_usd": budget_limit,
            "percentage_of_budget": round(percentage_of_budget, 1),
            "budget_sensitivity": budget_sensitivity,
            "recommendation": "Within budget" if within_budget else f"Exceeds budget by {round(percentage_of_budget - 100, 1)}%"
        }
    
    def _emit_success_telemetry(self, result: Dict[str, Any], processing_time_ms: int):
        """Emit success telemetry"""
        pricing_inputs = result["pricing_inputs"]
        primary_price = result["primary_price"]
        
        # Emit price metric
        self.telemetry.submit_metric(
            name="pricing.calculation.total",
            value=primary_price["total_monthly_usd"],
            tags=[
                f"architecture:{pricing_inputs['architecture']}",
                f"workload_type:{pricing_inputs['workload_type']}",
                f"phase:{self.phase_name}",
                f"calculation_method:{primary_price['calculation_method']}",
                f"region:{pricing_inputs['region']}",
                f"affordability_tier:{result['business_impact']['affordability_tier']}"
            ]
        )
        
        # Emit accuracy metric
        self.telemetry.submit_metric(
            name="pricing.calculation.accuracy",
            value=result["pricing_accuracy"]["estimated_accuracy"],
            tags=[
                f"architecture:{pricing_inputs['architecture']}",
                f"workload_type:{pricing_inputs['workload_type']}",
                f"phase:{self.phase_name}",
                f"calculation_method:{primary_price['calculation_method']}",
                f"api_available:{not self.pricing_client.mock_mode}"
            ]
        )
        
        # Emit processing time metric
        self.telemetry.submit_metric(
            name="pricing.calculation.processing.time_ms",
            value=processing_time_ms,
            tags=[
                f"workload_type:{pricing_inputs['workload_type']}",
                f"phase:{self.phase_name}",
                f"success:true",
                f"calculation_method:{primary_price['calculation_method']}"
            ]
        )
        
        # Emit savings potential metric
        best_savings = result["savings_analysis"]["potential_monthly_savings"]
        if best_savings > 0:
            self.telemetry.submit_metric(
                name="pricing.savings.potential",
                value=best_savings,
                tags=[
                    f"architecture:{pricing_inputs['architecture']}",
                    f"workload_type:{pricing_inputs['workload_type']}",
                    f"phase:{self.phase_name}"
                ]
            )
        
        # Emit success log
        self.telemetry.submit_log(
            source="cloud-sentinel",
            message={
                "event": "pricing_calculated",
                "request_id": result["request_id"],
                "user_id": result["user_id"],
                "session_id": result["session_id"],
                "workload_type": pricing_inputs["workload_type"],
                "architecture": pricing_inputs["architecture"],
                "total_monthly_usd": primary_price["total_monthly_usd"],
                "accuracy": result["pricing_accuracy"]["estimated_accuracy"],
                "calculation_method": primary_price["calculation_method"],
                "processing_time_ms": processing_time_ms,
                "api_used": not self.pricing_client.mock_mode,
                "components_count": len(primary_price["components"]),
                "within_budget": result["business_impact"]["budget_alignment"]["within_budget"]
            },
            tags=[
                "pricing_calculation", 
                "success", 
                pricing_inputs["architecture"],
                f"phase:{self.phase_name}",
                f"budget:{result['business_impact']['budget_alignment']['within_budget']}"
            ]
        )
        
        # Emit success event
        self.telemetry.emit_event(
            title="Pricing Calculated",
            text=f"Calculated ${primary_price['total_monthly_usd']:.2f}/month for {pricing_inputs['workload_type']} on {pricing_inputs['architecture']} with {result['pricing_accuracy']['estimated_accuracy']*100:.1f}% accuracy",
            tags=[
                "pricing_calculated",
                pricing_inputs["architecture"],
                f"price:{primary_price['total_monthly_usd']}",
                f"accuracy:{result['pricing_accuracy']['estimated_accuracy']:.2f}",
                f"workload:{pricing_inputs['workload_type']}",
                f"user:{result['user_id']}",
                f"phase:{self.phase_name}"
            ],
            alert_type="success"
        )
    
    def _create_error_result(self, user_id: str, session_id: str, request_id: str,
                           phase1_result: Dict[str, Any], phase2_result: Dict[str, Any],
                           phase3_result: Dict[str, Any], error_message: str, 
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
                "code": "PRICING_CALCULATION_FAILED",
                "phase_summary": {
                    "workload_type": phase1_result.get("intent_analysis", {}).get("workload_type", "unknown"),
                    "architecture": phase2_result.get("architecture_analysis", {}).get("primary_architecture", "unknown"),
                    "machine_type": phase3_result.get("specification_analysis", {}).get("exact_type", "unknown")
                }
            },
            "processing_metadata": {
                "processing_time_ms": processing_time_ms,
                "calculation_method": "failed",
                "attempted_retry": False
            },
            "fallback_suggestion": {
                "estimated_price_usd": 500,
                "estimated_accuracy": 0.5,
                "recommendation": "System temporarily unavailable. Using estimated pricing based on similar workloads."
            }
        }
    
    def _emit_error_telemetry(self, error_result: Dict[str, Any], error_message: str):
        """Emit error telemetry"""
        self.telemetry.submit_metric(
            name="pricing.calculation.processing.time_ms",
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
                "event": "pricing_calculation_failed",
                "request_id": error_result["request_id"],
                "user_id": error_result["user_id"],
                "error": error_result["error"],
                "processing_time_ms": error_result["processing_metadata"]["processing_time_ms"]
            },
            tags=[
                "pricing_calculation", 
                "error", 
                error_result["error"]["code"],
                f"phase:{self.phase_name}"
            ]
        )
        
        self.telemetry.emit_event(
            title="Pricing Calculation Failed",
            text=f"Failed to calculate pricing: {error_message}",
            tags=[
                "pricing_error",
                f"error_code:{error_result['error']['code']}",
                f"user:{error_result['user_id']}",
                f"phase:{self.phase_name}"
            ],
            alert_type="error",
            priority="high"
        )
    
    def _update_statistics(self, accuracy_estimate: float, processing_time_ms: int):
        """Update phase statistics"""
        self.accuracy_stats["estimated_accuracy_sum"] += accuracy_estimate
        self.accuracy_stats["total_processing_time_ms"] += processing_time_ms
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get phase statistics"""
        total = self.accuracy_stats["total_calculations"]
        
        stats = self.accuracy_stats.copy()
        
        if total > 0:
            stats["avg_accuracy"] = self.accuracy_stats["estimated_accuracy_sum"] / total
            stats["avg_processing_time_ms"] = self.accuracy_stats["total_processing_time_ms"] / total
            stats["api_usage_percent"] = (self.accuracy_stats["api_calculations"] / total * 100) if total > 0 else 0
        else:
            stats["avg_accuracy"] = 0.0
            stats["avg_processing_time_ms"] = 0.0
            stats["api_usage_percent"] = 0.0
        
        stats["phase_name"] = self.phase_name
        stats["phase_version"] = self.phase_version
        stats["pricing_client_status"] = self.pricing_client.get_status()
        stats["gemini_status"] = self.gemini.get_status()
        stats["telemetry_status"] = self.telemetry.get_status()
        
        return stats
    
    def reset_statistics(self):
        """Reset phase statistics"""
        self.accuracy_stats = {
            "total_calculations": 0,
            "api_calculations": 0,
            "fallback_calculations": 0,
            "total_processing_time_ms": 0,
            "estimated_accuracy_sum": 0.0
        }
        logger.info("📊 Phase 4 statistics reset")
    
    def get_status(self) -> Dict[str, Any]:
        """Get complete phase status"""
        return {
            "phase": self.phase_name,
            "version": self.phase_version,
            "initialized": True,
            "pricing_api_available": not self.pricing_client.mock_mode,
            "telemetry_available": self.telemetry.config.mode != TelemetryMode.DISABLED,
            "statistics": self.get_statistics()
        }