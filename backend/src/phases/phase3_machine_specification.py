"""
Phase 3: Machine Specification Sommelier
Production-grade implementation with full telemetry
"""

import time
import logging
import json
from datetime import datetime
from typing import Dict, Any, Optional, List
import uuid
import random

from ..core.gemini_client import GeminiClient
from ..core.catalog_manager import GCPCatalog, MachineSpec, MachineFamily, MachineSize
from ..telemetry.datadog_client import TelemetryClient, TelemetryConfig, TelemetryMode

logger = logging.getLogger(__name__)

class MachineSpecificationPhase:
    """Complete Phase 3: Machine Specification"""
    
    def __init__(self, telemetry_config: Optional[TelemetryConfig] = None):
        self.phase_name = "machine_specification"
        self.phase_version = "1.0.0"
        
        # Initialize clients
        self.gemini = GeminiClient()
        self.telemetry = TelemetryClient(telemetry_config)
        self.catalog = GCPCatalog()
        
        # Size mapping
        self.size_mapping = {
            "micro": MachineSize.MICRO,
            "small": MachineSize.SMALL,
            "medium": MachineSize.MEDIUM,
            "large": MachineSize.LARGE,
            "xlarge": MachineSize.XLARGE,
            "2xlarge": MachineSize.XLARGE_2,
            "4xlarge": MachineSize.XLARGE_4,
            "8xlarge": MachineSize.XLARGE_8
        }
        
        # Family mapping
        self.family_mapping = {
            "general_purpose": MachineFamily.GENERAL_PURPOSE,
            "compute_optimized": MachineFamily.COMPUTE_OPTIMIZED,
            "memory_optimized": MachineFamily.MEMORY_OPTIMIZED,
            "accelerator_optimized": MachineFamily.ACCELERATOR_OPTIMIZED,
            "storage_optimized": MachineFamily.STORAGE_OPTIMIZED,
            "shared_core": MachineFamily.SHARED_CORE
        }
        
        # Statistics
        self.stats = {
            "total_requests": 0,
            "gemini_selections": 0,
            "catalog_selections": 0,
            "rule_fallback_selections": 0,
            "total_processing_time_ms": 0,
            "avg_confidence": 0.0
        }
        
        logger.info(f"✅ Phase 3 initialized: {self.phase_name} v{self.phase_version}")
        logger.info(f"📊 Catalog loaded: {len(self.catalog.machines)} machine types")
    
    async def process(self, phase1_result: Dict[str, Any], 
                     phase2_result: Dict[str, Any],
                     user_id: Optional[str] = None,
                     session_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Select optimal machine specification
        
        Args:
            phase1_result: Complete output from Phase 1
            phase2_result: Complete output from Phase 2
            user_id: User identifier
            session_id: Session identifier
            
        Returns:
            Dict containing machine specification with full context
        """
        start_time = time.time()
        
        # Validate inputs
        if not phase1_result or "intent_analysis" not in phase1_result:
            raise ValueError("Invalid Phase 1 result. Missing intent_analysis")
        
        if not phase2_result or "architecture_analysis" not in phase2_result:
            raise ValueError("Invalid Phase 2 result. Missing architecture_analysis")
        
        self.stats["total_requests"] += 1
        
        # Extract data from previous phases
        intent_analysis = phase1_result["intent_analysis"]
        business_context = phase1_result.get("business_context", {})
        architecture_analysis = phase2_result["architecture_analysis"]
        
        workload_type = intent_analysis["workload_type"]
        scale = intent_analysis["scale"]
        architecture = architecture_analysis["primary_architecture"]
        
        # Use IDs from previous phases
        request_id = phase1_result.get("request_id", f"req_{int(time.time())}_{uuid.uuid4().hex[:6]}")
        user_id = user_id or phase1_result.get("user_id", f"user_{uuid.uuid4().hex[:8]}")
        session_id = session_id or phase1_result.get("session_id", f"session_{uuid.uuid4().hex[:8]}")
        
        try:
            logger.info(f"⚙️  Machine specification - Architecture: {architecture}, Workload: {workload_type}")
            
            # Step 1: Select machine family and size
            selection_method = "gemini_api"
            try:
                # Try Gemini first
                spec_result = await self._select_with_gemini(
                    intent_analysis, architecture_analysis, user_id, session_id
                )
                self.stats["gemini_selections"] += 1
            except Exception as e:
                logger.warning(f"Gemini specification failed, using catalog-based: {e}")
                # Fallback to catalog-based selection
                spec_result = self._select_with_catalog(
                    intent_analysis, architecture_analysis
                )
                selection_method = "catalog_fallback"
                self.stats["catalog_selections"] += 1
            
            # Step 2: Lookup exact machine in catalog
            if selection_method == "gemini_api":
                catalog_match = self._find_catalog_match(
                    spec_result["machine_family"],
                    spec_result["machine_size"],
                    architecture
                )
                
                if catalog_match:
                    spec_result["exact_type"] = catalog_match.type
                    spec_result["cpu"] = catalog_match.cpu
                    spec_result["ram"] = catalog_match.ram
                    spec_result["catalog_match"] = "exact"
                    spec_result["catalog_spec"] = catalog_match.to_dict()
                else:
                    # Find closest match
                    closest = self._find_closest_match(
                        spec_result["machine_family"],
                        spec_result["machine_size"],
                        architecture,
                        workload_type
                    )
                    spec_result["exact_type"] = closest.type
                    spec_result["cpu"] = closest.cpu
                    spec_result["ram"] = closest.ram
                    spec_result["catalog_match"] = "closest"
                    spec_result["catalog_spec"] = closest.to_dict()
            
            # Step 3: Calculate optimal configuration
            configuration = self._calculate_optimal_config(
                spec_result, intent_analysis, architecture_analysis
            )
            
            # Step 4: Calculate processing time
            processing_time_ms = int((time.time() - start_time) * 1000)
            
            # Step 5: Enhance result with metadata
            enhanced_result = self._enhance_specification_result(
                spec_result,
                configuration,
                phase1_result,
                phase2_result,
                processing_time_ms,
                selection_method,
                user_id,
                session_id,
                request_id
            )
            
            # Step 6: Update statistics
            self._update_statistics(spec_result, processing_time_ms)
            
            # Step 7: Emit telemetry
            self._emit_success_telemetry(enhanced_result, processing_time_ms)
            
            logger.info(f"✅ Machine specified: {spec_result.get('exact_type', 'unknown')}")
            logger.info(f"   CPU: {spec_result.get('cpu', 'N/A')}, RAM: {spec_result.get('ram', 'N/A')}GB")
            logger.info(f"   Confidence: {spec_result.get('confidence', 'N/A')}")
            logger.info(f"   Method: {selection_method}")
            logger.info(f"   Time: {processing_time_ms}ms")
            
            return enhanced_result
            
        except Exception as e:
            # Handle failures gracefully
            processing_time_ms = int((time.time() - start_time) * 1000)
            
            error_result = self._create_error_result(
                user_id, session_id, request_id, 
                phase1_result, phase2_result, str(e), processing_time_ms
            )
            
            self._emit_error_telemetry(error_result, str(e))
            
            logger.error(f"❌ Machine specification failed: {e}")
            raise
    
    async def _select_with_gemini(self, intent_analysis: Dict[str, Any],
                                 architecture_analysis: Dict[str, Any],
                                 user_id: str, session_id: str) -> Dict[str, Any]:
        """Select machine specification using Gemini API"""
        workload_type = intent_analysis["workload_type"]
        scale = intent_analysis["scale"]
        requirements = intent_analysis["requirements"]
        constraints = intent_analysis["constraints"]
        architecture = architecture_analysis["primary_architecture"]
        
        prompt = self._create_specification_prompt(
            workload_type, scale, requirements, constraints, architecture
        )
        
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
                raise ValueError("Could not extract JSON from response")
            
            json_text = match.group(1)
            result = json.loads(json_text)
            
            # Validate result
            self._validate_specification_result(result, architecture)
            
            # Add metadata
            result["selection_method"] = "gemini_api"
            result["llm_model"] = self.gemini.model_name
            result["active_key"] = self.gemini._get_current_key_name()
            
            return result
            
        except Exception as e:
            logger.error(f"Gemini specification error: {e}")
            raise
    
    def _create_specification_prompt(self, workload_type: str, scale: Dict[str, Any],
                                    requirements: Dict[str, Any], constraints: Dict[str, Any],
                                    architecture: str) -> str:
        """Create prompt for Gemini machine specification"""
        
        # Get machine families for reference
        families = self.catalog.get_machine_families()
        
        return f"""You are an expert cloud infrastructure architect at Google. Select the optimal machine specification.

WORKLOAD TYPE: {workload_type}
ARCHITECTURE: {architecture}

SCALE:
- Monthly Users: {scale.get('monthly_users', 10000)}
- Estimated RPS: {scale.get('estimated_rps', 50)}
- Traffic Pattern: {scale.get('traffic_pattern', 'variable')}

REQUIREMENTS:
- Latency: {requirements.get('latency', 'medium')}
- Availability: {requirements.get('availability', 'high')}
- Geography: {requirements.get('geography', 'global')}

CONSTRAINTS:
- Budget Sensitivity: {constraints.get('budget_sensitivity', 'medium')}
- Team Experience: {constraints.get('team_experience', 'intermediate')}
- Time to Market: {constraints.get('time_to_market', '1_week')}

Available Machine Families:
1. GENERAL_PURPOSE: Balanced CPU/Memory (e2-, n2- series)
2. COMPUTE_OPTIMIZED: High CPU performance (c2-, c2d- series)
3. MEMORY_OPTIMIZED: High memory capacity (n2-highmem-, m2- series)
4. ACCELERATOR_OPTIMIZED: GPU/TPU optimized (a2-, g2- series)
5. STORAGE_OPTIMIZED: High CPU to memory ratio (n2-highcpu- series)
6. SHARED_CORE: Cost-effective for dev/test (e2-micro, e2-small)

Machine Sizes: micro, small, medium, large, xlarge, 2xlarge, 4xlarge, 8xlarge

Return ONLY a valid JSON object with these exact fields:
- machine_family (must be one of: {', '.join(families)})
- machine_size (must be one of: micro, small, medium, large, xlarge, 2xlarge, 4xlarge, 8xlarge)
- confidence (number between 0.0 and 1.0 with 2 decimal places)
- reasoning (string explaining your choice)
- estimated_cpu_range (object with: min, max, recommended)
- estimated_ram_gb_range (object with: min, max, recommended)

Example:
{{
    "machine_family": "general_purpose",
    "machine_size": "medium",
    "confidence": 0.88,
    "reasoning": "General purpose provides balanced CPU/Memory for API workload with 50k monthly users. Medium size handles estimated 150 RPS with room for growth.",
    "estimated_cpu_range": {{
        "min": 2,
        "max": 4,
        "recommended": 4
    }},
    "estimated_ram_gb_range": {{
        "min": 4,
        "max": 16,
        "recommended": 8
    }}
}}

CRITICAL INSTRUCTIONS:
1. Return ONLY the JSON object, no markdown, no code blocks
2. Consider architecture constraints: {architecture} may limit machine options
3. Adjust for budget sensitivity: {constraints.get('budget_sensitivity')}
4. Consider team experience: {constraints.get('team_experience')} team
5. For {workload_type} workload with {scale.get('monthly_users')} users
6. Confidence should reflect certainty based on available information

JSON OUTPUT:"""
    
    def _validate_specification_result(self, result: Dict[str, Any], architecture: str) -> None:
        """Validate machine specification result"""
        required_fields = [
            "machine_family", "machine_size", "confidence", 
            "reasoning", "estimated_cpu_range", "estimated_ram_gb_range"
        ]
        
        for field in required_fields:
            if field not in result:
                raise ValueError(f"Missing required field: {field}")
        
        if result["machine_family"] not in self.catalog.get_machine_families():
            raise ValueError(f"Invalid machine_family: {result['machine_family']}")
        
        if result["machine_size"] not in self.size_mapping:
            raise ValueError(f"Invalid machine_size: {result['machine_size']}")
        
        confidence = result["confidence"]
        if not isinstance(confidence, (int, float)) or not 0.0 <= confidence <= 1.0:
            raise ValueError(f"Invalid confidence: {confidence}")
        
        # Validate CPU range
        cpu_range = result["estimated_cpu_range"]
        if not all(k in cpu_range for k in ["min", "max", "recommended"]):
            raise ValueError("Invalid estimated_cpu_range structure")
        
        # Validate RAM range
        ram_range = result["estimated_ram_gb_range"]
        if not all(k in ram_range for k in ["min", "max", "recommended"]):
            raise ValueError("Invalid estimated_ram_gb_range structure")
    
    def _select_with_catalog(self, intent_analysis: Dict[str, Any],
                            architecture_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Catalog-based machine specification selection"""
        workload_type = intent_analysis["workload_type"]
        scale = intent_analysis["scale"]
        requirements = intent_analysis["requirements"]
        constraints = intent_analysis["constraints"]
        architecture = architecture_analysis["primary_architecture"]
        
        # Get recommendations from catalog
        recommendations = self.catalog.recommend_for_workload(
            workload_type=workload_type,
            architecture=architecture,
            monthly_users=scale["monthly_users"],
            estimated_rps=scale["estimated_rps"]
        )
        
        if not recommendations:
            # Fallback to rule-based selection
            return self._select_with_rules(intent_analysis, architecture_analysis)
        
        # Pick the best recommendation (lowest cost score)
        best_spec = recommendations[0]
        
        # Determine family and size
        machine_family = best_spec.family.value
        machine_size = best_spec.size.value
        
        # Calculate confidence based on match quality
        confidence = self._calculate_catalog_confidence(
            best_spec, workload_type, scale, requirements
        )
        
        return {
            "machine_family": machine_family,
            "machine_size": machine_size,
            "exact_type": best_spec.type,  # Include exact machine type
            "cpu": best_spec.cpu,           # Include CPU count
            "ram": best_spec.ram,           # Include RAM
            "confidence": round(confidence, 2),
            "reasoning": f"Catalog-based selection: {best_spec.type} recommended for {workload_type} workload with {scale['monthly_users']} monthly users. {best_spec.description}",
            "estimated_cpu_range": {
                "min": max(1, best_spec.cpu - 2),
                "max": best_spec.cpu + 2,
                "recommended": best_spec.cpu
            },
            "estimated_ram_gb_range": {
                "min": max(1, best_spec.ram - 4),
                "max": best_spec.ram + 8,
                "recommended": best_spec.ram
            },
            "selection_method": "catalog_based",
            "llm_model": "catalog_engine_v1",
            "catalog_recommendation": best_spec.to_dict()
        }
    
    def _select_with_rules(self, intent_analysis: Dict[str, Any],
                          architecture_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Rule-based machine specification selection (final fallback)"""
        workload_type = intent_analysis["workload_type"]
        scale = intent_analysis["scale"]
        requirements = intent_analysis["requirements"]
        constraints = intent_analysis["constraints"]
        architecture = architecture_analysis["primary_architecture"]
        
        monthly_users = scale["monthly_users"]
        estimated_rps = scale.get("estimated_rps", 100)
        
        # Determine machine family based on workload
        family_rules = {
            "api_backend": "general_purpose",
            "web_app": "general_purpose",
            "data_processing": "memory_optimized",
            "ml_inference": "compute_optimized",
            "batch_processing": "storage_optimized",
            "realtime_streaming": "compute_optimized",
            "mobile_backend": "general_purpose",
            "gaming_server": "accelerator_optimized"
        }
        
        machine_family = family_rules.get(workload_type, "general_purpose")
        
        # Determine machine size based on scale AND RPS requirements
        # Use the more demanding of users or RPS to size properly
        rps_based_size = self._size_from_rps(estimated_rps, workload_type)
        user_based_size = self._size_from_users(monthly_users)
        
        # Pick larger of the two
        size_order = ["micro", "small", "medium", "large", "xlarge", "2xlarge", "4xlarge", "8xlarge"]
        rps_idx = size_order.index(rps_based_size) if rps_based_size in size_order else 2
        user_idx = size_order.index(user_based_size) if user_based_size in size_order else 2
        machine_size = size_order[max(rps_idx, user_idx)]
        
        # Adjust for requirements
        if requirements.get("latency") in ["ultra_low", "low"]:
            machine_size = self._upgrade_size(machine_size)
        
        if requirements.get("availability") == "critical":
            machine_size = self._upgrade_size(machine_size)
        
        # Adjust for budget
        if constraints.get("budget_sensitivity") == "high":
            machine_size = self._downgrade_size(machine_size)
            if machine_family != "shared_core":
                machine_family = "general_purpose"
        
        # Map family + size to actual GCP machine type
        machine_type_mapping = {
            ("general_purpose", "micro"): {"type": "e2-micro", "cpu": 2, "ram": 1},
            ("general_purpose", "small"): {"type": "n2-standard-2", "cpu": 2, "ram": 8},
            ("general_purpose", "medium"): {"type": "n2-standard-4", "cpu": 4, "ram": 16},
            ("general_purpose", "large"): {"type": "n2-standard-8", "cpu": 8, "ram": 32},
            ("general_purpose", "xlarge"): {"type": "n2-standard-16", "cpu": 16, "ram": 64},
            ("general_purpose", "2xlarge"): {"type": "n2-standard-32", "cpu": 32, "ram": 128},
            ("compute_optimized", "micro"): {"type": "c2-standard-4", "cpu": 4, "ram": 16},
            ("compute_optimized", "small"): {"type": "c2-standard-4", "cpu": 4, "ram": 16},
            ("compute_optimized", "medium"): {"type": "c2-standard-8", "cpu": 8, "ram": 32},
            ("compute_optimized", "large"): {"type": "c2-standard-16", "cpu": 16, "ram": 64},
            ("compute_optimized", "xlarge"): {"type": "c2-standard-30", "cpu": 30, "ram": 120},
            ("memory_optimized", "micro"): {"type": "n2-highmem-2", "cpu": 2, "ram": 16},
            ("memory_optimized", "small"): {"type": "n2-highmem-4", "cpu": 4, "ram": 32},
            ("memory_optimized", "medium"): {"type": "n2-highmem-8", "cpu": 8, "ram": 64},
            ("memory_optimized", "large"): {"type": "n2-highmem-16", "cpu": 16, "ram": 128},
            ("memory_optimized", "xlarge"): {"type": "n2-highmem-32", "cpu": 32, "ram": 256},
            ("accelerator_optimized", "medium"): {"type": "a2-highgpu-1g", "cpu": 12, "ram": 85},
            ("accelerator_optimized", "large"): {"type": "a2-highgpu-2g", "cpu": 24, "ram": 170},
            ("storage_optimized", "medium"): {"type": "n2-standard-4", "cpu": 4, "ram": 16},
            ("storage_optimized", "large"): {"type": "n2-standard-8", "cpu": 8, "ram": 32},
        }
        
        # Get machine specs or use defaults
        key = (machine_family, machine_size)
        if key in machine_type_mapping:
            spec = machine_type_mapping[key]
        else:
            # Fallback to general purpose medium
            spec = machine_type_mapping.get(("general_purpose", machine_size), 
                                           {"type": "n2-standard-4", "cpu": 4, "ram": 16})
        
        base_cpu = spec["cpu"]
        base_ram = spec["ram"]
        exact_type = spec["type"]
        
        # Adjust for workload type
        if workload_type in ["data_processing", "ml_inference"]:
            base_ram = base_ram * 2
        
        if workload_type in ["ml_inference", "gaming_server"]:
            base_cpu = base_cpu + 2
        
        confidence = 0.7  # Lower confidence for rule-based
        
        return {
            "machine_family": machine_family,
            "machine_size": machine_size,
            "exact_type": exact_type,
            "cpu": base_cpu,
            "ram": base_ram,
            "confidence": round(confidence, 2),
            "reasoning": f"Rule-based selection: {exact_type} ({machine_family} {machine_size}) for {workload_type} with {monthly_users} users, {estimated_rps} RPS. Budget sensitivity: {constraints.get('budget_sensitivity')}, Team experience: {constraints.get('team_experience')}.",
            "estimated_cpu_range": {
                "min": max(1, base_cpu - 2),
                "max": base_cpu + 4,
                "recommended": base_cpu
            },
            "estimated_ram_gb_range": {
                "min": max(1, base_ram - 4),
                "max": base_ram + 8,
                "recommended": base_ram
            },
            "selection_method": "rule_based",
            "llm_model": "rule_engine_v1"
        }
    
    def _size_from_rps(self, rps: int, workload_type: str) -> str:
        """Determine machine size based on RPS requirements"""
        # RPS capacity per CPU varies by workload type
        rps_per_cpu = {
            "api_backend": 50,
            "web_app": 30,
            "data_processing": 10,
            "ml_inference": 5,
            "batch_processing": 20,
            "realtime_streaming": 40,
            "mobile_backend": 40,
            "gaming_server": 20
        }
        
        base_rps = rps_per_cpu.get(workload_type, 25)
        cpus_needed = max(1, rps // base_rps)
        
        # Map CPU count to size
        if cpus_needed <= 2:
            return "small"
        elif cpus_needed <= 4:
            return "medium"
        elif cpus_needed <= 8:
            return "large"
        elif cpus_needed <= 16:
            return "xlarge"
        elif cpus_needed <= 32:
            return "2xlarge"
        elif cpus_needed <= 64:
            return "4xlarge"
        else:
            return "8xlarge"
    
    def _size_from_users(self, monthly_users: int) -> str:
        """Determine machine size based on monthly users"""
        if monthly_users < 1000:
            return "micro"
        elif monthly_users < 10000:
            return "small"
        elif monthly_users < 100000:
            return "medium"
        elif monthly_users < 1000000:
            return "large"
        else:
            return "xlarge"
    
    def _upgrade_size(self, current_size: str) -> str:
        """Upgrade machine size"""
        sizes = list(self.size_mapping.keys())
        current_index = sizes.index(current_size) if current_size in sizes else 2
        return sizes[min(current_index + 1, len(sizes) - 1)]
    
    def _downgrade_size(self, current_size: str) -> str:
        """Downgrade machine size"""
        sizes = list(self.size_mapping.keys())
        current_index = sizes.index(current_size) if current_size in sizes else 2
        return sizes[max(current_index - 1, 0)]
    
    def _find_catalog_match(self, machine_family: str, machine_size: str,
                           architecture: str) -> Optional[MachineSpec]:
        """Find exact match in catalog"""
        compatible_types = self.catalog.architecture_mapping.get(architecture, [])
        
        for machine_type in compatible_types:
            spec = self.catalog.get_by_type(machine_type)
            if (spec and 
                spec.family.value == machine_family and 
                spec.size.value == machine_size):
                return spec
        
        return None
    
    def _find_closest_match(self, machine_family: str, machine_size: str,
                           architecture: str, workload_type: str) -> MachineSpec:
        """Find closest match in catalog"""
        # Get all compatible machines
        compatible_types = self.catalog.architecture_mapping.get(architecture, [])
        
        # Filter by family first
        family_machines = []
        for machine_type in compatible_types:
            spec = self.catalog.get_by_type(machine_type)
            if spec and spec.family.value == machine_family:
                family_machines.append(spec)
        
        if not family_machines:
            # Fallback to any compatible machine
            for machine_type in compatible_types:
                spec = self.catalog.get_by_type(machine_type)
                if spec:
                    family_machines.append(spec)
        
        if not family_machines:
            # Ultimate fallback: default machine
            return self.catalog.get_by_type("n2-standard-4")
        
        # Sort by size closeness
        target_size_order = list(self.size_mapping.keys())
        try:
            target_index = target_size_order.index(machine_size)
        except ValueError:
            target_index = 2  # medium as default
        
        # Find closest size
        closest = min(
            family_machines,
            key=lambda x: abs(target_size_order.index(x.size.value) - target_index)
        )
        
        return closest
    
    def _calculate_catalog_confidence(self, spec: MachineSpec, 
                                     workload_type: str, scale: Dict[str, Any],
                                     requirements: Dict[str, Any]) -> float:
        """Calculate confidence score for catalog selection"""
        confidence = 0.8  # Base confidence
        
        # Adjust based on workload recommendation
        if workload_type in spec.recommended_for:
            confidence += 0.1
        else:
            confidence -= 0.1
        
        # Adjust based on scale match
        monthly_users = scale["monthly_users"]
        if monthly_users < 1000 and spec.size.value == "micro":
            confidence += 0.05
        elif monthly_users < 10000 and spec.size.value == "small":
            confidence += 0.05
        elif monthly_users < 100000 and spec.size.value == "medium":
            confidence += 0.05
        elif monthly_users < 1000000 and spec.size.value in ["large", "xlarge"]:
            confidence += 0.05
        
        # Adjust for latency requirements
        if requirements.get("latency") in ["ultra_low", "low"]:
            if spec.family.value in ["compute_optimized", "general_purpose"]:
                confidence += 0.05
        
        return min(max(confidence, 0.3), 0.95)
    
    def _calculate_optimal_config(self, spec_result: Dict[str, Any],
                                 intent_analysis: Dict[str, Any],
                                 architecture_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate optimal configuration based on spec"""
        workload_type = intent_analysis["workload_type"]
        scale = intent_analysis["scale"]
        architecture = architecture_analysis["primary_architecture"]
        
        cpu = spec_result.get("cpu", 4)
        ram = spec_result.get("ram", 8)
        
        # Base configuration
        config = {
            "machine_type": spec_result.get("exact_type", "unknown"),
            "cpu": cpu,
            "ram_gb": ram,
            "architecture": architecture,
            "scaling_strategy": "automatic",
            "availability": "regional" if intent_analysis["requirements"]["availability"] == "critical" else "zonal"
        }
        
        # Add architecture-specific configurations
        if architecture == "serverless":
            config.update({
                "min_instances": 0,
                "max_instances": 10,
                "concurrency": 80,
                "cpu_allocation": "default",
                "memory_allocation": f"{ram}Gi"
            })
        elif architecture == "containers":
            config.update({
                "min_replicas": 2,
                "max_replicas": 10,
                "auto_scaling": {
                    "cpu_utilization": 70,
                    "requests_per_replica": 100
                },
                "resource_requests": {
                    "cpu": f"{cpu * 1000}m",
                    "memory": f"{ram}Gi"
                },
                "resource_limits": {
                    "cpu": f"{cpu * 1000}m",
                    "memory": f"{ram}Gi"
                }
            })
        elif architecture == "virtual_machines":
            config.update({
                "instance_count": 2,
                "auto_healing": True,
                "auto_scaling": {
                    "min_replicas": 2,
                    "max_replicas": 10,
                    "cpu_utilization": 70
                },
                "disk_size_gb": 100,
                "disk_type": "pd-ssd"
            })
        
        # Adjust for workload type
        if workload_type == "data_processing":
            config["disk_size_gb"] = 500
            config["disk_type"] = "pd-standard"
        
        if workload_type == "ml_inference":
            config["accelerator"] = {
                "type": "nvidia-tesla-t4",
                "count": 1
            }
        
        return config
    
    def _enhance_specification_result(self, spec_result: Dict[str, Any],
                                     configuration: Dict[str, Any],
                                     phase1_result: Dict[str, Any],
                                     phase2_result: Dict[str, Any],
                                     processing_time_ms: int,
                                     selection_method: str,
                                     user_id: str,
                                     session_id: str,
                                     request_id: str) -> Dict[str, Any]:
        """Enhance specification result with metadata"""
        
        intent_analysis = phase1_result["intent_analysis"]
        business_context = phase1_result.get("business_context", {})
        architecture_analysis = phase2_result["architecture_analysis"]
        
        enhanced = {
            "request_id": request_id,
            "user_id": user_id,
            "session_id": session_id,
            "phase": self.phase_name,
            "phase_version": self.phase_version,
            "timestamp": datetime.utcnow().isoformat(),
            "status": "completed",
            
            "phase_inputs": {
                "workload_type": intent_analysis["workload_type"],
                "architecture": architecture_analysis["primary_architecture"],
                "scale_tier": business_context.get("scale_tier", "unknown"),
                "monthly_users": intent_analysis["scale"]["monthly_users"]
            },
            
            "specification_analysis": spec_result,
            
            "configuration": configuration,
            
            "processing_metadata": {
                "processing_time_ms": processing_time_ms,
                "selection_method": selection_method,
                "gemini_mode": "api" if not self.gemini.mock_mode else "mock",
                "llm_model": spec_result.get("llm_model", "unknown"),
                "catalog_match": spec_result.get("catalog_match", "none"),
                "active_key": spec_result.get("active_key", "unknown")
            },
            
            "performance_assessment": {
                "estimated_rps_capacity": self._estimate_rps_capacity(
                    spec_result.get("cpu", 4),
                    spec_result.get("ram", 8),
                    intent_analysis["workload_type"],
                    configuration  # Pass config to include replica count
                ),
                "estimated_concurrent_users": self._estimate_concurrent_users(
                    spec_result.get("cpu", 4),
                    intent_analysis["workload_type"],
                    configuration  # Pass config to include replica count
                ),
                "performance_score": self._calculate_performance_score(
                    spec_result, intent_analysis
                ),
                "bottleneck_analysis": self._analyze_bottlenecks(
                    spec_result, intent_analysis
                )
            },
            
            "cost_estimation_preview": {
                "relative_cost_tier": self._estimate_cost_tier(spec_result),
                "optimization_opportunities": self._identify_optimizations(
                    spec_result, intent_analysis, architecture_analysis
                ),
                "waste_potential_percent": self._estimate_waste_potential(
                    spec_result, intent_analysis["scale"]
                )
            },
            
            "next_phase": "pricing_calculation",
            "phase_transition": {
                "recommended": True,
                "estimated_time_seconds": 15,
                "prerequisites_met": True,
                "required_input": {
                    "architecture": architecture_analysis["primary_architecture"],
                    "machine_type": spec_result.get("exact_type", "unknown"),
                    "configuration": configuration
                }
            }
        }
        
        return enhanced
    
    def _estimate_rps_capacity(self, cpu: int, ram: int, workload_type: str, 
                               configuration: Dict[str, Any] = None) -> Dict[str, Any]:
        """Estimate RPS capacity based on machine specs and replica count"""
        base_rps_per_cpu = {
            "api_backend": 50,
            "web_app": 30,
            "data_processing": 10,
            "ml_inference": 5,
            "batch_processing": 20,
            "realtime_streaming": 40,
            "mobile_backend": 40,
            "gaming_server": 20
        }
        
        base = base_rps_per_cpu.get(workload_type, 25)
        estimated_per_instance = cpu * base
        
        # Get replica/instance count from configuration
        replica_count = 1
        if configuration:
            architecture = configuration.get("architecture", "")
            if architecture == "serverless":
                # Serverless scales automatically, use max_instances as estimate
                replica_count = configuration.get("max_instances", 10)
            elif architecture == "containers":
                # Use average of min/max replicas
                min_rep = configuration.get("min_replicas", 2)
                max_rep = configuration.get("max_replicas", 10)
                replica_count = (min_rep + max_rep) // 2
            elif architecture == "virtual_machines":
                # Use instance count or average of auto-scaling range
                auto_scaling = configuration.get("auto_scaling", {})
                if auto_scaling:
                    min_rep = auto_scaling.get("min_replicas", 2)
                    max_rep = auto_scaling.get("max_replicas", 10)
                    replica_count = (min_rep + max_rep) // 2
                else:
                    replica_count = configuration.get("instance_count", 2)
        
        # Total capacity scales with replicas
        total_estimated = estimated_per_instance * replica_count
        
        return {
            "per_instance": estimated_per_instance,
            "conservative": int(total_estimated * 0.7),
            "optimal": total_estimated,
            "maximum": int(total_estimated * 1.3),
            "saturation_point": int(total_estimated * 1.5),
            "replica_count": replica_count
        }
    
    def _estimate_concurrent_users(self, cpu: int, workload_type: str,
                                   configuration: Dict[str, Any] = None) -> Dict[str, Any]:
        """Estimate concurrent user capacity including replicas"""
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
        
        base = users_per_cpu.get(workload_type, 300)
        estimated_per_instance = cpu * base
        
        # Get replica count
        replica_count = 1
        if configuration:
            architecture = configuration.get("architecture", "")
            if architecture == "serverless":
                replica_count = configuration.get("max_instances", 10)
            elif architecture == "containers":
                replica_count = (configuration.get("min_replicas", 2) + configuration.get("max_replicas", 10)) // 2
            elif architecture == "virtual_machines":
                auto_scaling = configuration.get("auto_scaling", {})
                if auto_scaling:
                    replica_count = (auto_scaling.get("min_replicas", 2) + auto_scaling.get("max_replicas", 10)) // 2
                else:
                    replica_count = configuration.get("instance_count", 2)
        
        total_estimated = estimated_per_instance * replica_count
        
        return {
            "per_instance": estimated_per_instance,
            "concurrent_users": total_estimated,
            "sessions_per_second": int(total_estimated * 0.1),
            "peak_capacity": int(total_estimated * 1.5),
            "replica_count": replica_count
        }
    
    def _calculate_performance_score(self, spec_result: Dict[str, Any],
                                   intent_analysis: Dict[str, Any]) -> float:
        """Calculate performance score (0-100)"""
        score = 70  # Base score
        
        # CPU score
        recommended_cpu = spec_result.get("estimated_cpu_range", {}).get("recommended", 4)
        actual_cpu = spec_result.get("cpu", 4)
        
        if actual_cpu >= recommended_cpu:
            score += 10
        elif actual_cpu >= recommended_cpu * 0.7:
            score += 5
        else:
            score -= 10
        
        # RAM score
        recommended_ram = spec_result.get("estimated_ram_gb_range", {}).get("recommended", 8)
        actual_ram = spec_result.get("ram", 8)
        
        if actual_ram >= recommended_ram:
            score += 10
        elif actual_ram >= recommended_ram * 0.7:
            score += 5
        else:
            score -= 10
        
        # Workload match score
        workload_type = intent_analysis["workload_type"]
        if spec_result.get("catalog_spec", {}).get("recommended_for"):
            if workload_type in spec_result["catalog_spec"]["recommended_for"]:
                score += 10
        
        return min(max(score, 0), 100)
    
    def _analyze_bottlenecks(self, spec_result: Dict[str, Any],
                            intent_analysis: Dict[str, Any]) -> List[str]:
        """Analyze potential bottlenecks"""
        bottlenecks = []
        
        cpu = spec_result.get("cpu", 4)
        ram = spec_result.get("ram", 8)
        workload_type = intent_analysis["workload_type"]
        estimated_rps = intent_analysis["scale"].get("estimated_rps", 50)
        
        # Estimate capacity
        capacity = self._estimate_rps_capacity(cpu, ram, workload_type)
        
        if estimated_rps > capacity["optimal"]:
            bottlenecks.append(f"Estimated RPS ({estimated_rps}) exceeds optimal capacity ({capacity['optimal']})")
        
        if workload_type in ["data_processing", "ml_inference"] and ram < 16:
            bottlenecks.append(f"Insufficient RAM ({ram}GB) for {workload_type} workload")
        
        if workload_type in ["realtime_streaming", "gaming_server"] and cpu < 4:
            bottlenecks.append(f"Insufficient CPU ({cpu} cores) for real-time workload")
        
        if not bottlenecks:
            bottlenecks.append("No significant bottlenecks identified")
        
        return bottlenecks
    
    def _estimate_cost_tier(self, spec_result: Dict[str, Any]) -> str:
        """Estimate relative cost tier"""
        cost_score = spec_result.get("catalog_spec", {}).get("cost_score", 50)
        
        if cost_score < 20:
            return "very_low"
        elif cost_score < 40:
            return "low"
        elif cost_score < 70:
            return "medium"
        elif cost_score < 100:
            return "high"
        else:
            return "very_high"
    
    def _identify_optimizations(self, spec_result: Dict[str, Any],
                               intent_analysis: Dict[str, Any],
                               architecture_analysis: Dict[str, Any]) -> List[str]:
        """Identify optimization opportunities"""
        optimizations = []
        
        # Check for over-provisioning
        monthly_users = intent_analysis["scale"]["monthly_users"]
        cpu = spec_result.get("cpu", 4)
        
        if monthly_users < 1000 and cpu > 2:
            optimizations.append(f"Consider downgrading from {cpu} cores to 2 cores for development workload")
        
        if monthly_users < 10000 and cpu > 4:
            optimizations.append(f"Consider downgrading from {cpu} cores to 4 cores for small scale")
        
        # Check architecture optimizations
        architecture = architecture_analysis["primary_architecture"]
        if architecture == "virtual_machines" and intent_analysis["workload_type"] == "api_backend":
            optimizations.append("Consider serverless architecture for better cost efficiency with variable traffic")
        
        # Check for commitment discounts
        if spec_result.get("catalog_spec", {}).get("sustained_use_discount", True):
            optimizations.append("Eligible for sustained use discounts (30% savings)")
        
        if spec_result.get("catalog_spec", {}).get("spot_available", True):
            optimizations.append("Consider spot instances for 60-90% cost savings on fault-tolerant workloads")
        
        if not optimizations:
            optimizations.append("Configuration appears optimal for current requirements")
        
        return optimizations
    
    def _estimate_waste_potential(self, spec_result: Dict[str, Any],
                                 scale: Dict[str, Any]) -> float:
        """Estimate potential waste percentage"""
        monthly_users = scale["monthly_users"]
        cpu = spec_result.get("cpu", 4)
        
        # Estimate utilization based on scale
        if monthly_users < 1000:
            estimated_utilization = 0.2  # 20%
        elif monthly_users < 10000:
            estimated_utilization = 0.4  # 40%
        elif monthly_users < 100000:
            estimated_utilization = 0.6  # 60%
        elif monthly_users < 1000000:
            estimated_utilization = 0.8  # 80%
        else:
            estimated_utilization = 0.9  # 90%
        
        waste = (1 - estimated_utilization) * 100
        return round(waste, 1)
    
    def _emit_success_telemetry(self, result: Dict[str, Any], processing_time_ms: int):
        """Emit success telemetry"""
        spec_analysis = result["specification_analysis"]
        phase_inputs = result["phase_inputs"]
        configuration = result["configuration"]
        
        # Emit machine type metric
        if "exact_type" in spec_analysis:
            self.telemetry.submit_metric(
                name="ai.machine.specification.type",
                value=1.0,
                tags=[
                    f"machine_type:{spec_analysis['exact_type']}",
                    f"architecture:{phase_inputs['architecture']}",
                    f"workload_type:{phase_inputs['workload_type']}",
                    f"phase:{self.phase_name}",
                    f"selection_method:{spec_analysis.get('selection_method', 'unknown')}",
                    f"catalog_match:{spec_analysis.get('catalog_match', 'none')}"
                ]
            )
        
        # Emit CPU/RAM metrics
        if "cpu" in spec_analysis and "ram" in spec_analysis:
            self.telemetry.submit_metric(
                name="ai.machine.specification.cpu",
                value=spec_analysis["cpu"],
                tags=[
                    f"machine_family:{spec_analysis['machine_family']}",
                    f"workload_type:{phase_inputs['workload_type']}",
                    f"phase:{self.phase_name}"
                ]
            )
            
            self.telemetry.submit_metric(
                name="ai.machine.specification.ram",
                value=spec_analysis["ram"],
                tags=[
                    f"machine_family:{spec_analysis['machine_family']}",
                    f"workload_type:{phase_inputs['workload_type']}",
                    f"phase:{self.phase_name}"
                ]
            )
        
        # Emit confidence metric
        self.telemetry.submit_metric(
            name="ai.machine.specification.confidence",
            value=spec_analysis["confidence"],
            tags=[
                f"machine_family:{spec_analysis['machine_family']}",
                f"workload_type:{phase_inputs['workload_type']}",
                f"phase:{self.phase_name}",
                f"selection_method:{spec_analysis.get('selection_method', 'unknown')}"
            ]
        )
        
        # Emit processing time metric
        self.telemetry.submit_metric(
            name="ai.machine.specification.processing.time_ms",
            value=processing_time_ms,
            tags=[
                f"workload_type:{phase_inputs['workload_type']}",
                f"phase:{self.phase_name}",
                f"success:true"
            ]
        )
        
        # Emit success log
        self.telemetry.submit_log(
            source="cloud-sentinel",
            message={
                "event": "machine_specified",
                "request_id": result["request_id"],
                "user_id": result["user_id"],
                "session_id": result["session_id"],
                "workload_type": phase_inputs["workload_type"],
                "architecture": phase_inputs["architecture"],
                "machine_type": spec_analysis.get("exact_type", "unknown"),
                "cpu": spec_analysis.get("cpu", "unknown"),
                "ram_gb": spec_analysis.get("ram", "unknown"),
                "confidence": spec_analysis["confidence"],
                "selection_method": spec_analysis.get("selection_method", "unknown"),
                "processing_time_ms": processing_time_ms,
                "configuration_summary": {
                    "scaling_strategy": configuration.get("scaling_strategy"),
                    "availability": configuration.get("availability")
                }
            },
            tags=[
                "machine_specification", 
                "success", 
                phase_inputs["architecture"],
                spec_analysis.get("machine_family", "unknown"),
                f"phase:{self.phase_name}"
            ]
        )
        
        # Emit success event
        machine_type = spec_analysis.get("exact_type", f"{spec_analysis['machine_family']}_{spec_analysis['machine_size']}")
        self.telemetry.emit_event(
            title="Machine Specification Selected",
            text=f"Selected {machine_type} for {phase_inputs['workload_type']} on {phase_inputs['architecture']} with {spec_analysis['confidence']*100:.1f}% confidence",
            tags=[
                "machine_specified",
                spec_analysis["machine_family"],
                f"machine_type:{machine_type}",
                f"confidence:{spec_analysis['confidence']:.2f}",
                f"workload:{phase_inputs['workload_type']}",
                f"architecture:{phase_inputs['architecture']}",
                f"user:{result['user_id']}",
                f"phase:{self.phase_name}"
            ],
            alert_type="success"
        )
    
    def _create_error_result(self, user_id: str, session_id: str, request_id: str,
                           phase1_result: Dict[str, Any], phase2_result: Dict[str, Any],
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
                "code": "MACHINE_SPECIFICATION_FAILED",
                "phase_summary": {
                    "workload_type": phase1_result.get("intent_analysis", {}).get("workload_type", "unknown"),
                    "architecture": phase2_result.get("architecture_analysis", {}).get("primary_architecture", "unknown")
                }
            },
            "processing_metadata": {
                "processing_time_ms": processing_time_ms,
                "selection_method": "failed",
                "attempted_retry": False
            },
            "fallback_suggestion": {
                "suggested_machine": "n2-standard-4",
                "estimated_confidence": 0.5,
                "recommendation": "System temporarily unavailable. Using default n2-standard-4 machine type."
            }
        }
    
    def _emit_error_telemetry(self, error_result: Dict[str, Any], error_message: str):
        """Emit error telemetry"""
        self.telemetry.submit_metric(
            name="ai.machine.specification.processing.time_ms",
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
                "event": "machine_specification_failed",
                "request_id": error_result["request_id"],
                "user_id": error_result["user_id"],
                "error": error_result["error"],
                "processing_time_ms": error_result["processing_metadata"]["processing_time_ms"]
            },
            tags=[
                "machine_specification", 
                "error", 
                error_result["error"]["code"],
                f"phase:{self.phase_name}"
            ]
        )
        
        self.telemetry.emit_event(
            title="Machine Specification Failed",
            text=f"Failed to specify machine: {error_message}",
            tags=[
                "machine_specification_error",
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
            total_success = (self.stats["gemini_selections"] + 
                           self.stats["catalog_selections"] + 
                           self.stats["rule_fallback_selections"])
            
            if total_success > 0:
                self.stats["avg_confidence"] = ((current_avg * (total_success - 1)) + confidence) / total_success
            else:
                self.stats["avg_confidence"] = confidence
        
        self.stats["total_processing_time_ms"] += processing_time_ms
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get phase statistics"""
        total = self.stats["total_requests"]
        successful = (self.stats["gemini_selections"] + 
                     self.stats["catalog_selections"] + 
                     self.stats["rule_fallback_selections"])
        
        stats = self.stats.copy()
        
        if total > 0:
            stats["success_rate"] = successful / total if total > 0 else 0.0
            stats["avg_processing_time_ms"] = self.stats["total_processing_time_ms"] / total
            stats["gemini_success_rate"] = self.stats["gemini_selections"] / total
            stats["catalog_success_rate"] = self.stats["catalog_selections"] / total
        else:
            stats["success_rate"] = 0.0
            stats["avg_processing_time_ms"] = 0.0
            stats["gemini_success_rate"] = 0.0
            stats["catalog_success_rate"] = 0.0
        
        stats["phase_name"] = self.phase_name
        stats["phase_version"] = self.phase_version
        stats["catalog_statistics"] = self.catalog.get_statistics()
        stats["gemini_status"] = self.gemini.get_status()
        stats["telemetry_status"] = self.telemetry.get_status()
        
        return stats
    
    def reset_statistics(self):
        """Reset phase statistics"""
        self.stats = {
            "total_requests": 0,
            "gemini_selections": 0,
            "catalog_selections": 0,
            "rule_fallback_selections": 0,
            "total_processing_time_ms": 0,
            "avg_confidence": 0.0
        }
        logger.info("📊 Phase 3 statistics reset")
    
    def get_status(self) -> Dict[str, Any]:
        """Get complete phase status"""
        return {
            "phase": self.phase_name,
            "version": self.phase_version,
            "initialized": True,
            "gemini_available": not self.gemini.mock_mode,
            "telemetry_available": self.telemetry.config.mode != TelemetryMode.DISABLED,
            "catalog_available": True,
            "catalog_machines": len(self.catalog.machines),
            "statistics": self.get_statistics()
        }