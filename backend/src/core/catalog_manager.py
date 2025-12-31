"""
GCP Machine Type Catalog Manager
Comprehensive catalog of GCP machine types with specs and cost scores
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum

class MachineFamily(Enum):
    GENERAL_PURPOSE = "general_purpose"
    COMPUTE_OPTIMIZED = "compute_optimized"
    MEMORY_OPTIMIZED = "memory_optimized"
    ACCELERATOR_OPTIMIZED = "accelerator_optimized"
    STORAGE_OPTIMIZED = "storage_optimized"
    SHARED_CORE = "shared_core"

class MachineSize(Enum):
    MICRO = "micro"
    SMALL = "small"
    MEDIUM = "medium"
    LARGE = "large"
    XLARGE = "xlarge"
    XLARGE_2 = "2xlarge"
    XLARGE_4 = "4xlarge"
    XLARGE_8 = "8xlarge"

@dataclass
class MachineSpec:
    type: str  # e.g., "n2-standard-4"
    family: MachineFamily
    size: MachineSize
    cpu: int  # vCPUs
    ram: int  # GB
    cost_score: int  # 1-100, lower is cheaper
    architectures: List[str]  # Compatible architectures
    recommended_for: List[str]  # Recommended workload types
    description: str
    generation: str  # "n2", "e2", "n2d", "t2d", etc.
    sustained_use_discount: bool = True
    spot_available: bool = True
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": self.type,
            "family": self.family.value,
            "size": self.size.value,
            "cpu": self.cpu,
            "ram": self.ram,
            "cost_score": self.cost_score,
            "architectures": self.architectures,
            "recommended_for": self.recommended_for,
            "description": self.description,
            "generation": self.generation
        }

class GCPCatalog:
    """Comprehensive GCP machine type catalog"""
    
    def __init__(self):
        self.machines = self._build_catalog()
        self.architecture_mapping = self._build_architecture_mapping()
        
    def _build_catalog(self) -> Dict[str, MachineSpec]:
        """Build comprehensive GCP machine catalog"""
        machines = {}
        
        # ========== GENERAL PURPOSE ==========
        # E2 series (Cost-effective)
        machines["e2-micro"] = MachineSpec(
            type="e2-micro",
            family=MachineFamily.GENERAL_PURPOSE,
            size=MachineSize.MICRO,
            cpu=2,
            ram=1,
            cost_score=10,
            architectures=["containers", "virtual_machines"],
            recommended_for=["web_app", "api_backend", "development"],
            description="Cost-effective small instances",
            generation="e2"
        )
        
        machines["e2-small"] = MachineSpec(
            type="e2-small",
            family=MachineFamily.GENERAL_PURPOSE,
            size=MachineSize.SMALL,
            cpu=2,
            ram=2,
            cost_score=15,
            architectures=["containers", "virtual_machines"],
            recommended_for=["web_app", "api_backend"],
            description="Cost-effective small instances",
            generation="e2"
        )
        
        machines["e2-medium"] = MachineSpec(
            type="e2-medium",
            family=MachineFamily.GENERAL_PURPOSE,
            size=MachineSize.MEDIUM,
            cpu=2,
            ram=4,
            cost_score=20,
            architectures=["containers", "virtual_machines"],
            recommended_for=["web_app", "api_backend", "mobile_backend"],
            description="Cost-effective general purpose",
            generation="e2"
        )
        
        # N2 series (Balanced)
        machines["n2-standard-2"] = MachineSpec(
            type="n2-standard-2",
            family=MachineFamily.GENERAL_PURPOSE,
            size=MachineSize.SMALL,
            cpu=2,
            ram=8,
            cost_score=30,
            architectures=["containers", "virtual_machines"],
            recommended_for=["api_backend", "web_app", "mobile_backend"],
            description="Balanced compute and memory",
            generation="n2"
        )
        
        machines["n2-standard-4"] = MachineSpec(
            type="n2-standard-4",
            family=MachineFamily.GENERAL_PURPOSE,
            size=MachineSize.MEDIUM,
            cpu=4,
            ram=16,
            cost_score=50,
            architectures=["containers", "virtual_machines"],
            recommended_for=["api_backend", "web_app", "data_processing"],
            description="Ideal for most general workloads",
            generation="n2"
        )
        
        machines["n2-standard-8"] = MachineSpec(
            type="n2-standard-8",
            family=MachineFamily.GENERAL_PURPOSE,
            size=MachineSize.LARGE,
            cpu=8,
            ram=32,
            cost_score=80,
            architectures=["containers", "virtual_machines"],
            recommended_for=["api_backend", "web_app", "batch_processing"],
            description="High performance general purpose",
            generation="n2"
        )
        
        machines["n2-standard-16"] = MachineSpec(
            type="n2-standard-16",
            family=MachineFamily.GENERAL_PURPOSE,
            size=MachineSize.XLARGE,
            cpu=16,
            ram=64,
            cost_score=120,
            architectures=["containers", "virtual_machines"],
            recommended_for=["data_processing", "ml_inference", "realtime_streaming"],
            description="High performance for demanding workloads",
            generation="n2"
        )
        
        # ========== COMPUTE OPTIMIZED ==========
        machines["c2-standard-4"] = MachineSpec(
            type="c2-standard-4",
            family=MachineFamily.COMPUTE_OPTIMIZED,
            size=MachineSize.MEDIUM,
            cpu=4,
            ram=16,
            cost_score=70,
            architectures=["containers", "virtual_machines"],
            recommended_for=["ml_inference", "gaming_server", "realtime_streaming"],
            description="Compute optimized with high CPU performance",
            generation="c2"
        )
        
        machines["c2-standard-8"] = MachineSpec(
            type="c2-standard-8",
            family=MachineFamily.COMPUTE_OPTIMIZED,
            size=MachineSize.LARGE,
            cpu=8,
            ram=32,
            cost_score=110,
            architectures=["containers", "virtual_machines"],
            recommended_for=["ml_inference", "gaming_server", "batch_processing"],
            description="High performance compute optimized",
            generation="c2"
        )
        
        machines["c2d-standard-8"] = MachineSpec(
            type="c2d-standard-8",
            family=MachineFamily.COMPUTE_OPTIMIZED,
            size=MachineSize.LARGE,
            cpu=8,
            ram=32,
            cost_score=105,
            architectures=["containers", "virtual_machines"],
            recommended_for=["ml_inference", "data_processing"],
            description="AMD-based compute optimized",
            generation="c2d"
        )
        
        # ========== MEMORY OPTIMIZED ==========
        machines["n2-highmem-4"] = MachineSpec(
            type="n2-highmem-4",
            family=MachineFamily.MEMORY_OPTIMIZED,
            size=MachineSize.MEDIUM,
            cpu=4,
            ram=32,
            cost_score=75,
            architectures=["containers", "virtual_machines"],
            recommended_for=["data_processing", "in_memory_cache", "analytics"],
            description="Memory optimized for data-intensive workloads",
            generation="n2"
        )
        
        machines["n2-highmem-8"] = MachineSpec(
            type="n2-highmem-8",
            family=MachineFamily.MEMORY_OPTIMIZED,
            size=MachineSize.LARGE,
            cpu=8,
            ram=64,
            cost_score=115,
            architectures=["containers", "virtual_machines"],
            recommended_for=["data_processing", "in_memory_cache"],
            description="High memory for large datasets",
            generation="n2"
        )
        
        machines["m2-ultramem-8"] = MachineSpec(
            type="m2-ultramem-8",
            family=MachineFamily.MEMORY_OPTIMIZED,
            size=MachineSize.LARGE,
            cpu=8,
            ram=128,
            cost_score=150,
            architectures=["virtual_machines"],
            recommended_for=["data_processing", "analytics", "large_datasets"],
            description="Ultra memory for extremely large datasets",
            generation="m2"
        )
        
        # ========== ACCELERATOR OPTIMIZED ==========
        machines["a2-highgpu-1g"] = MachineSpec(
            type="a2-highgpu-1g",
            family=MachineFamily.ACCELERATOR_OPTIMIZED,
            size=MachineSize.LARGE,
            cpu=12,
            ram=85,
            cost_score=200,
            architectures=["virtual_machines"],
            recommended_for=["ml_inference", "deep_learning", "gpu_compute"],
            description="GPU optimized with NVIDIA Tesla A100",
            generation="a2"
        )
        
        machines["g2-standard-4"] = MachineSpec(
            type="g2-standard-4",
            family=MachineFamily.ACCELERATOR_OPTIMIZED,
            size=MachineSize.MEDIUM,
            cpu=4,
            ram=16,
            cost_score=180,
            architectures=["virtual_machines"],
            recommended_for=["ml_inference", "gaming_server", "rendering"],
            description="GPU optimized with NVIDIA L4",
            generation="g2"
        )
        
        # ========== STORAGE OPTIMIZED ==========
        machines["n2-highcpu-4"] = MachineSpec(
            type="n2-highcpu-4",
            family=MachineFamily.STORAGE_OPTIMIZED,
            size=MachineSize.MEDIUM,
            cpu=4,
            ram=4,
            cost_score=45,
            architectures=["containers", "virtual_machines"],
            recommended_for=["batch_processing", "web_app", "api_backend"],
            description="High CPU to memory ratio for compute-intensive",
            generation="n2"
        )
        
        return machines
    
    def _build_architecture_mapping(self) -> Dict[str, List[str]]:
        """Build mapping from architecture to compatible machine types"""
        mapping = {
            "serverless": [
                "Cloud Run Default",
                "Cloud Functions Default"
            ],
            "containers": [
                "e2-micro", "e2-small", "e2-medium",
                "n2-standard-2", "n2-standard-4", "n2-standard-8",
                "c2-standard-4", "c2-standard-8",
                "n2-highmem-4", "n2-highmem-8"
            ],
            "virtual_machines": list(self.machines.keys())  # All machines
        }
        return mapping
    
    def get_by_type(self, machine_type: str) -> Optional[MachineSpec]:
        """Get machine spec by type"""
        return self.machines.get(machine_type)
    
    def find_matching_machines(self, 
                              architecture: str,
                              min_cpu: int = 1,
                              max_cpu: int = 64,
                              min_ram: int = 1,
                              max_ram: int = 512,
                              max_cost_score: int = 100) -> List[MachineSpec]:
        """Find machines matching criteria"""
        compatible_types = self.architecture_mapping.get(architecture, [])
        
        matching = []
        for machine_type in compatible_types:
            if machine_type in self.machines:
                spec = self.machines[machine_type]
                if (min_cpu <= spec.cpu <= max_cpu and
                    min_ram <= spec.ram <= max_ram and
                    spec.cost_score <= max_cost_score):
                    matching.append(spec)
        
        return sorted(matching, key=lambda x: x.cost_score)
    
    def recommend_for_workload(self, 
                              workload_type: str,
                              architecture: str,
                              monthly_users: int,
                              estimated_rps: int) -> List[MachineSpec]:
        """Recommend machines based on workload characteristics"""
        
        # Calculate required resources based on workload
        if monthly_users < 1000:
            # Development/Testing
            cpu_range = (1, 2)
            ram_range = (1, 4)
            max_cost = 20
        elif monthly_users < 10000:
            # Small scale
            cpu_range = (2, 4)
            ram_range = (2, 8)
            max_cost = 40
        elif monthly_users < 100000:
            # Medium scale
            cpu_range = (4, 8)
            ram_range = (8, 16)
            max_cost = 70
        elif monthly_users < 1000000:
            # Large scale
            cpu_range = (8, 16)
            ram_range = (16, 32)
            max_cost = 120
        else:
            # Enterprise scale
            cpu_range = (16, 32)
            ram_range = (32, 64)
            max_cost = 200
        
        # Adjust for workload type
        if workload_type in ["ml_inference", "gaming_server", "realtime_streaming"]:
            cpu_range = (cpu_range[0] + 2, cpu_range[1] + 4)
            max_cost += 30
        
        if workload_type in ["data_processing", "analytics"]:
            ram_range = (ram_range[0] * 2, ram_range[1] * 2)
        
        # Adjust for RPS
        if estimated_rps > 100:
            cpu_range = (cpu_range[0] + 1, cpu_range[1] + 2)
        if estimated_rps > 500:
            cpu_range = (cpu_range[0] + 2, cpu_range[1] + 4)
        
        # Find matching machines
        matching = self.find_matching_machines(
            architecture=architecture,
            min_cpu=cpu_range[0],
            max_cpu=cpu_range[1],
            min_ram=ram_range[0],
            max_ram=ram_range[1],
            max_cost_score=max_cost
        )
        
        # Filter by workload recommendations
        filtered = [
            machine for machine in matching 
            if workload_type in machine.recommended_for
        ]
        
        return filtered[:5] if filtered else matching[:5]  # Return top 5 recommendations
    
    def get_machine_families(self) -> List[str]:
        """Get all machine families"""
        return [family.value for family in MachineFamily]
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get catalog statistics"""
        total_machines = len(self.machines)
        
        families = {}
        for spec in self.machines.values():
            family = spec.family.value
            families[family] = families.get(family, 0) + 1
        
        return {
            "total_machines": total_machines,
            "families_distribution": families,
            "cpu_range": {
                "min": min(spec.cpu for spec in self.machines.values()),
                "max": max(spec.cpu for spec in self.machines.values()),
                "avg": sum(spec.cpu for spec in self.machines.values()) / total_machines
            },
            "ram_range": {
                "min": min(spec.ram for spec in self.machines.values()),
                "max": max(spec.ram for spec in self.machines.values()),
                "avg": sum(spec.ram for spec in self.machines.values()) / total_machines
            },
            "cost_score_range": {
                "min": min(spec.cost_score for spec in self.machines.values()),
                "max": max(spec.cost_score for spec in self.machines.values()),
                "avg": sum(spec.cost_score for spec in self.machines.values()) / total_machines
            }
        }
