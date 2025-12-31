"""
Google Cloud Billing API Client
Production-grade with caching, fallback, and comprehensive pricing
"""

import os
import json
import logging
import time
import random
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
from pathlib import Path

import requests
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

logger = logging.getLogger(__name__)

@dataclass
class PriceComponent:
    """Individual price component"""
    service: str
    sku: str
    description: str
    usage_unit: str
    pricing_unit: str
    price_per_unit: float
    estimated_usage: float
    estimated_cost: float
    region: str

@dataclass
class PriceEstimate:
    """Complete price estimate"""
    total_monthly_usd: float
    components: List[PriceComponent]
    region: str
    architecture: str
    machine_type: Optional[str] = None
    timestamp: datetime = None
    confidence: float = 1.0
    cache_hit: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "total_monthly_usd": round(self.total_monthly_usd, 2),
            "region": self.region,
            "architecture": self.architecture,
            "machine_type": self.machine_type,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "confidence": self.confidence,
            "cache_hit": self.cache_hit,
            "components": [
                {
                    "service": c.service,
                    "description": c.description,
                    "usage_unit": c.usage_unit,
                    "pricing_unit": c.pricing_unit,
                    "price_per_unit": c.price_per_unit,
                    "estimated_usage": c.estimated_usage,
                    "estimated_cost": round(c.estimated_cost, 2),
                    "region": c.region
                }
                for c in self.components
            ]
        }

class GCPPricingClient:
    """Production GCP Pricing Client with Billing API integration"""
    
    def __init__(self, credentials_path: Optional[str] = None, use_cache: bool = True):
        self.service = None
        self.credentials = None
        self.use_cache = use_cache
        self.cache = {}
        self.cache_file = Path(__file__).parent.parent / ".pricing_cache.json"
        self.mock_mode = False
        
        # Load credentials
        if credentials_path:
            self._load_credentials_from_file(credentials_path)
        else:
            self._load_credentials_from_env()
        
        # Initialize service
        self._initialize_service()
        
        # Load cache
        if use_cache:
            self._load_cache()
        
        # Region mapping
        self.regions = {
            "us-east": ["us-east1", "us-east4"],
            "us-west": ["us-west1", "us-west2", "us-west3", "us-west4"],
            "europe": ["europe-west1", "europe-west2", "europe-west3", "europe-west4"],
            "asia": ["asia-east1", "asia-east2", "asia-northeast1", "asia-southeast1"],
            "australia": ["australia-southeast1"],
            "india": ["asia-south1", "asia-south2"],
            "global": ["us-central1"]  # Default
        }
        
        # Service SKU mapping (simplified - real API would have exact SKUs)
        self.service_skus = {
            "compute": {
                "serverless": {
                    "Cloud Run": "Cloud Run CPU Allocation",
                    "Cloud Functions": "Cloud Functions Invocation"
                },
                "containers": {
                    "GKE Standard": "GKE Standard Cluster Management",
                    "GKE Autopilot": "GKE Autopilot vCPU"
                },
                "virtual_machines": {
                    "n2-standard": "N2 Custom Instance Core",
                    "e2-standard": "E2 Instance Core",
                    "c2-standard": "C2 Instance Core"
                }
            },
            "database": {
                "Cloud SQL": {
                    "PostgreSQL": "Cloud SQL for PostgreSQL: db-standard",
                    "MySQL": "Cloud SQL for MySQL: db-standard"
                },
                "Firestore": {
                    "Native Mode": "Firestore Stored Data"
                }
            },
            "storage": {
                "Cloud Storage": {
                    "Standard": "Cloud Storage Standard Storage US",
                    "Nearline": "Cloud Storage Nearline Storage US"
                },
                "Persistent Disk": {
                    "SSD": "Persistent Disk SSD backed",
                    "Standard": "Persistent Disk Standard"
                }
            },
            "networking": {
                "Load Balancing": {
                    "HTTP(S)": "Load Balancing HTTPS Load Balancer"
                },
                "CDN": {
                    "Cloud CDN": "Cloud CDN Egress from North America"
                },
                "VPC": {
                    "Egress": "Network Egress Internet"
                }
            },
            "ai_ml": {
                "Vertex AI": {
                    "Prediction": "Vertex AI Online Prediction"
                },
                "Vision AI": {
                    "Object Detection": "Cloud Vision API Object Detection"
                }
            }
        }
        
        # Default prices (fallback when API unavailable)
        self.default_prices = self._load_default_prices()
        
        logger.info(f"✅ GCP Pricing Client initialized. Mock mode: {self.mock_mode}")
        logger.info(f"📊 Available regions: {len(self.regions)}")
    
    def _load_credentials_from_env(self):
        """Load credentials from environment"""
        try:
            # Try to read service account JSON directly from .env file
            env_file = Path(__file__).parent.parent.parent / ".env"
            if env_file.exists():
                # Read the entire .env file to extract JSON
                with open(env_file, 'r') as f:
                    content = f.read()
                
                # Extract JSON between GOOGLE_SERVICE_ACCOUNT_JSON={ and }
                import re
                pattern = r'GOOGLE_SERVICE_ACCOUNT_JSON=(\{[^}]*\}(?:\s*\})*)'
                match = re.search(pattern, content, re.DOTALL)
                
                if match:
                    json_str = match.group(1)
                    # Clean up the JSON string
                    json_str = json_str.strip()
                    
                    try:
                        sa_info = json.loads(json_str)
                        self.credentials = service_account.Credentials.from_service_account_info(
                            sa_info,
                            scopes=["https://www.googleapis.com/auth/cloud-platform"]
                        )
                        logger.info("✅ Loaded service account from .env file")
                        logger.info(f"📧 Service account: {sa_info.get('client_email', 'unknown')}")
                        return
                    except json.JSONDecodeError as je:
                        logger.warning(f"⚠️  Failed to parse JSON from .env: {je}")
            
            # Fallback: Try service account JSON from environment variable
            sa_json = os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON")
            if sa_json:
                try:
                    self.credentials = service_account.Credentials.from_service_account_info(
                        json.loads(sa_json),
                        scopes=["https://www.googleapis.com/auth/cloud-platform"]
                    )
                    logger.info("✅ Loaded service account from environment variable")
                    return
                except json.JSONDecodeError:
                    logger.warning("⚠️  GOOGLE_SERVICE_ACCOUNT_JSON env var is not valid JSON")
            
            # Try credentials file path
            creds_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
            if creds_path and Path(creds_path).exists():
                self.credentials = service_account.Credentials.from_service_account_file(
                    creds_path,
                    scopes=["https://www.googleapis.com/auth/cloud-platform"]
                )
                logger.info(f"✅ Loaded service account from file: {creds_path}")
                return
            
            # No credentials found
            logger.warning("⚠️  No credentials found in .env, environment, or file path")
            logger.info("💡 To use real GCP Billing API, provide credentials in .env file")
            self.credentials = None
            self.mock_mode = True
            
        except Exception as e:
            logger.error(f"❌ Failed to load credentials: {e}")
            self.credentials = None
            self.mock_mode = True
    
    def _load_credentials_from_file(self, path: str):
        """Load credentials from file"""
        try:
            self.credentials = service_account.Credentials.from_service_account_file(
                path,
                scopes=["https://www.googleapis.com/auth/cloud-platform"]
            )
            logger.info(f"✅ Loaded service account from file: {path}")
        except Exception as e:
            logger.error(f"❌ Failed to load credentials from file: {e}")
            self.mock_mode = True
    
    def _initialize_service(self):
        """Initialize Cloud Billing API service"""
        if not self.credentials:
            logger.warning("⚠️  No credentials available, using mock mode")
            self.mock_mode = True
            return
        
        try:
            self.service = build(
                'cloudbilling',
                'v1',
                credentials=self.credentials,
                cache_discovery=False
            )
            logger.info("✅ Cloud Billing API service initialized")
        except Exception as e:
            logger.error(f"❌ Failed to initialize Cloud Billing API: {e}")
            self.mock_mode = True
    
    def _load_default_prices(self) -> Dict[str, Any]:
        """Load default prices for fallback"""
        return {
            "compute": {
                "serverless": {
                    "Cloud Run": {"price_per_unit": 0.0000240, "unit": "vCPU-second"},
                    "Cloud Functions": {"price_per_unit": 0.0000025, "unit": "GHz-second"}
                },
                "containers": {
                    "GKE Standard": {"price_per_unit": 0.10, "unit": "cluster-hour"},
                    "GKE Autopilot": {"price_per_unit": 0.00003125, "unit": "vCPU-second"}
                },
                "virtual_machines": {
                    "n2-standard-4": {"price_per_unit": 0.1931, "unit": "hour"},
                    "e2-standard-4": {"price_per_unit": 0.134012, "unit": "hour"},
                    "c2-standard-4": {"price_per_unit": 0.2088, "unit": "hour"},
                    "n2-highmem-8": {"price_per_unit": 0.4288, "unit": "hour"},
                    "a2-highgpu-1g": {"price_per_unit": 3.6739, "unit": "hour"}
                }
            },
            "database": {
                "Cloud SQL": {
                    "PostgreSQL db-standard-1": {"price_per_unit": 0.085, "unit": "hour"},
                    "MySQL db-standard-1": {"price_per_unit": 0.085, "unit": "hour"}
                },
                "Firestore": {
                    "Storage": {"price_per_unit": 0.18, "unit": "GB-month"},
                    "Operations": {"price_per_unit": 0.06, "unit": "100k operations"}
                }
            },
            "storage": {
                "Cloud Storage": {
                    "Standard": {"price_per_unit": 0.02, "unit": "GB-month"},
                    "Nearline": {"price_per_unit": 0.01, "unit": "GB-month"}
                },
                "Persistent Disk": {
                    "SSD": {"price_per_unit": 0.17, "unit": "GB-month"},
                    "Standard": {"price_per_unit": 0.04, "unit": "GB-month"}
                }
            },
            "networking": {
                "Load Balancing": {
                    "HTTP(S)": {"price_per_unit": 0.025, "unit": "hour"}
                },
                "CDN": {
                    "Egress": {"price_per_unit": 0.08, "unit": "GB"}
                },
                "VPC": {
                    "Egress": {"price_per_unit": 0.12, "unit": "GB"}
                }
            }
        }
    
    def _load_cache(self):
        """Load pricing cache from file"""
        try:
            if self.cache_file.exists():
                with open(self.cache_file, 'r') as f:
                    self.cache = json.load(f)
                logger.info(f"📁 Loaded pricing cache: {len(self.cache)} entries")
        except Exception as e:
            logger.error(f"Failed to load cache: {e}")
            self.cache = {}
    
    def _save_cache(self):
        """Save pricing cache to file"""
        try:
            with open(self.cache_file, 'w') as f:
                json.dump(self.cache, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save cache: {e}")
    
    def _get_cache_key(self, service: str, sku: str, region: str) -> str:
        """Generate cache key"""
        return f"{service}:{sku}:{region}"
    
    # GCP Service IDs (required for Billing API)
    # These are the official service IDs from GCP Billing Catalog
    # To find: gcloud services list --available | grep billing
    # Or: https://cloud.google.com/billing/v1/how-tos/catalog-api
    GCP_SERVICE_IDS = {
        "Compute Engine": "6F81-5844-456A",
        "Cloud Run": "152E-C115-5142",
        "Cloud Functions": "29E7-DA93-CA13",
        "Cloud SQL": "9662-B51E-5089",
        "Cloud Storage": "95FF-2EF5-5EA1",
        "Cloud Pub/Sub": "A1E8-BE35-7EBC",
        "BigQuery": "24E6-581D-38E5",
        "Kubernetes Engine": "CCD8-9BF1-090E",
        "Cloud Load Balancing": "152E-C115-5142",  # Part of Compute Engine networking
        "Networking": "6F81-5844-456A",  # Network egress is under Compute Engine
        "Cloud CDN": "6F81-5844-456A",  # CDN is under Compute Engine
        "Memorystore": "E69E-8A3F-0E51",
        "Firestore": "D95E-A6A5-1929",
        "App Engine": "F17B-412E-CB64",
        "Cloud Logging": "5490-F7B7-8DF6",
        "Cloud Monitoring": "58CD-E7C3-72CA",
        "Persistent Disk": "6F81-5844-456A",  # Disks are under Compute Engine
    }
    
    def _get_from_cache(self, cache_key: str) -> Optional[Dict[str, Any]]:
        """Get price from cache"""
        if not self.use_cache:
            return None
        
        if cache_key in self.cache:
            entry = self.cache[cache_key]
            # Check if cache is still valid (1 day TTL)
            cache_time = datetime.fromisoformat(entry["timestamp"])
            if datetime.now() - cache_time < timedelta(days=1):
                return entry
        return None
    
    def _add_to_cache(self, cache_key: str, price_data: Dict[str, Any]):
        """Add price to cache"""
        if not self.use_cache:
            return
        
        self.cache[cache_key] = {
            **price_data,
            "timestamp": datetime.now().isoformat()
        }
        
        # Save cache periodically (every 10 additions)
        if len(self.cache) % 10 == 0:
            self._save_cache()
    
    def get_price_from_api(self, service: str, sku: str, region: str) -> Optional[Dict[str, Any]]:
        """
        Get price from Cloud Billing API
        
        Args:
            service: Service name (e.g., "Compute Engine") or service ID (e.g., "6F81-5844-456A")
            sku: SKU description to search for
            region: Region code (e.g., "us-central1")
            
        Returns:
            Price data or None if not found
        """
        if self.mock_mode or not self.service:
            logger.debug(f"Mock mode or no service, skipping API call for {service}:{sku}")
            return None
        
        cache_key = self._get_cache_key(service, sku, region)
        cached = self._get_from_cache(cache_key)
        if cached:
            logger.debug(f"Cache hit for {cache_key}")
            return cached
        
        try:
            # Resolve service name to service ID if needed
            service_id = self.GCP_SERVICE_IDS.get(service, service)
            service_name = f"services/{service_id}"
            
            logger.info(f"🔍 Querying GCP Billing API: {service} ({service_id}) for SKU: {sku}")
            
            # Get SKUs for the service (without 'view' parameter - not supported)
            all_skus = []
            next_page_token = None
            max_pages = 5  # Limit pagination to avoid long waits
            
            for page in range(max_pages):
                request_params = {
                    "parent": service_name,
                    "currencyCode": "USD",
                }
                if next_page_token:
                    request_params["pageToken"] = next_page_token
                
                skus_request = self.service.services().skus().list(**request_params)
                response = skus_request.execute()
                
                all_skus.extend(response.get('skus', []))
                next_page_token = response.get('nextPageToken')
                
                if not next_page_token:
                    break
            
            logger.info(f"📊 Retrieved {len(all_skus)} SKUs from API")
            
            # Find matching SKU with region filtering
            sku_lower = sku.lower()
            region_lower = region.lower()
            
            best_match = None
            best_match_score = 0
            
            for sku_item in all_skus:
                description = sku_item.get('description', '').lower()
                # serviceRegions is a list of strings like ["us-central1", "us-east1"]
                raw_regions = sku_item.get('serviceRegions', [])
                sku_regions = [r.lower() if isinstance(r, str) else r.get('region', '').lower() for r in raw_regions]
                
                # Skip if region doesn't match (unless global)
                region_matches = (
                    'global' in sku_regions or 
                    region_lower in sku_regions or
                    any(region_lower in r for r in sku_regions) or
                    not sku_regions  # No region restriction
                )
                
                if not region_matches:
                    continue
                
                # Score the match
                score = 0
                if sku_lower in description:
                    score += 10
                for word in sku_lower.split():
                    if word in description:
                        score += 1
                
                if score > best_match_score:
                    best_match_score = score
                    best_match = sku_item
            
            if best_match and best_match_score > 0:
                # Extract pricing info
                pricing_info = best_match.get('pricingInfo', [{}])[0]
                pricing_expression = pricing_info.get('pricingExpression', {})
                
                # Get tiered rates
                tiers = pricing_expression.get('tieredRates', [{}])
                if tiers:
                    unit_price = tiers[0].get('unitPrice', {})
                    
                    # Calculate price per unit
                    units = float(unit_price.get('units', 0))
                    nanos = float(unit_price.get('nanos', 0)) / 1e9
                    price_per_unit = units + nanos
                    
                    price_data = {
                        "service": service,
                        "sku": sku,
                        "sku_id": best_match.get('skuId'),
                        "description": best_match.get('description'),
                        "category": best_match.get('category', {}).get('resourceFamily'),
                        "region": region,
                        "price_per_unit": price_per_unit,
                        "currency": unit_price.get('currencyCode', 'USD'),
                        "unit": pricing_expression.get('usageUnit', ''),
                        "display_quantity": pricing_expression.get('displayQuantity', 1),
                        "match_score": best_match_score,
                        "source": "api",
                        "timestamp": datetime.now().isoformat()
                    }
                    
                    # Cache the result
                    self._add_to_cache(cache_key, price_data)
                    
                    logger.info(f"✅ API price found: {sku} = ${price_per_unit:.6f}/{pricing_expression.get('usageUnit', 'unit')}")
                    return price_data
            
            logger.warning(f"⚠️ SKU not found in API response: {service}:{sku} (region: {region})")
            return None
            
        except HttpError as e:
            logger.error(f"❌ HTTP error getting price: {e}")
            return None
        except Exception as e:
            logger.error(f"❌ Error getting price from API: {e}")
            import traceback
            logger.debug(traceback.format_exc())
            return None
    
    def estimate_compute_cost(self, architecture: str, machine_type: Optional[str] = None,
                             cpu: int = 4, ram: int = 16, region: str = "us-central1",
                             estimated_rps: int = 100, monthly_users: int = 10000) -> List[PriceComponent]:
        """Estimate compute costs based on architecture"""
        components = []
        
        # Calculate usage based on architecture
        if architecture == "serverless":
            # Cloud Run pricing (CPU allocation + requests)
            cpu_seconds_per_month = cpu * 720 * estimated_rps * 0.1  # Simplified
            
            components.append(PriceComponent(
                service="Cloud Run",
                sku="CPU Allocation",
                description="Cloud Run vCPU Allocation",
                usage_unit="vCPU-second",
                pricing_unit="vCPU-second",
                price_per_unit=0.0000240,
                estimated_usage=cpu_seconds_per_month,
                estimated_cost=cpu_seconds_per_month * 0.0000240,
                region=region
            ))
            
            components.append(PriceComponent(
                service="Cloud Run",
                sku="Request",
                description="Cloud Run Requests",
                usage_unit="request",
                pricing_unit="million requests",
                price_per_unit=0.40,
                estimated_usage=estimated_rps * 2592000 / 1000000,  # Monthly requests in millions
                estimated_cost=(estimated_rps * 2592000 / 1000000) * 0.40,
                region=region
            ))
            
        elif architecture == "containers":
            # GKE pricing
            if machine_type and machine_type in self.default_prices["compute"]["virtual_machines"]:
                price_info = self.default_prices["compute"]["virtual_machines"][machine_type]
                
                components.append(PriceComponent(
                    service="GKE",
                    sku="Node",
                    description=f"GKE Node: {machine_type}",
                    usage_unit="hour",
                    pricing_unit="hour",
                    price_per_unit=price_info["price_per_unit"],
                    estimated_usage=720,  # 24*30 hours
                    estimated_cost=price_info["price_per_unit"] * 720,
                    region=region
                ))
                
                # Cluster management fee
                components.append(PriceComponent(
                    service="GKE",
                    sku="Management",
                    description="GKE Cluster Management",
                    usage_unit="cluster",
                    pricing_unit="hour",
                    price_per_unit=0.10,
                    estimated_usage=720,
                    estimated_cost=0.10 * 720,
                    region=region
                ))
            else:
                # Estimate based on CPU/RAM
                hourly_rate = (cpu * 0.02) + (ram * 0.005)
                
                components.append(PriceComponent(
                    service="GKE",
                    sku="Custom",
                    description=f"GKE Custom: {cpu}vCPU, {ram}GB RAM",
                    usage_unit="hour",
                    pricing_unit="hour",
                    price_per_unit=hourly_rate,
                    estimated_usage=720,
                    estimated_cost=hourly_rate * 720,
                    region=region
                ))
                
        elif architecture == "virtual_machines":
            # Compute Engine pricing
            if machine_type and machine_type in self.default_prices["compute"]["virtual_machines"]:
                price_info = self.default_prices["compute"]["virtual_machines"][machine_type]
                
                components.append(PriceComponent(
                    service="Compute Engine",
                    sku=machine_type,
                    description=f"Compute Engine: {machine_type}",
                    usage_unit="hour",
                    pricing_unit="hour",
                    price_per_unit=price_info["price_per_unit"],
                    estimated_usage=720,
                    estimated_cost=price_info["price_per_unit"] * 720,
                    region=region
                ))
            else:
                # Estimate based on CPU/RAM
                hourly_rate = (cpu * 0.018) + (ram * 0.0045)
                
                components.append(PriceComponent(
                    service="Compute Engine",
                    sku="Custom",
                    description=f"Compute Engine Custom: {cpu}vCPU, {ram}GB RAM",
                    usage_unit="hour",
                    pricing_unit="hour",
                    price_per_unit=hourly_rate,
                    estimated_usage=720,
                    estimated_cost=hourly_rate * 720,
                    region=region
                ))
        
        return components
    
    def estimate_database_cost(self, workload_type: str, monthly_users: int,
                              region: str = "us-central1") -> List[PriceComponent]:
        """Estimate database costs based on workload"""
        components = []
        
        # Database size estimation
        if workload_type in ["api_backend", "web_app", "mobile_backend"]:
            # Relational database
            estimated_storage_gb = max(10, monthly_users * 0.001)  # 1KB per user
            
            components.append(PriceComponent(
                service="Cloud SQL",
                sku="PostgreSQL db-standard-1",
                description="Cloud SQL PostgreSQL (db-standard-1)",
                usage_unit="hour",
                pricing_unit="hour",
                price_per_unit=0.085,
                estimated_usage=720,
                estimated_cost=0.085 * 720,
                region=region
            ))
            
            components.append(PriceComponent(
                service="Cloud SQL",
                sku="Storage",
                description="Cloud SQL Storage",
                usage_unit="GB",
                pricing_unit="GB-month",
                price_per_unit=0.17,
                estimated_usage=estimated_storage_gb,
                estimated_cost=0.17 * estimated_storage_gb,
                region=region
            ))
            
        elif workload_type in ["data_processing", "ml_inference"]:
            # Firestore for flexible schema
            estimated_storage_gb = max(50, monthly_users * 0.01)
            estimated_operations = monthly_users * 100
            
            components.append(PriceComponent(
                service="Firestore",
                sku="Storage",
                description="Firestore Storage",
                usage_unit="GB",
                pricing_unit="GB-month",
                price_per_unit=0.18,
                estimated_usage=estimated_storage_gb,
                estimated_cost=0.18 * estimated_storage_gb,
                region=region
            ))
            
            components.append(PriceComponent(
                service="Firestore",
                sku="Operations",
                description="Firestore Operations",
                usage_unit="100k operations",
                pricing_unit="100k operations",
                price_per_unit=0.06,
                estimated_usage=estimated_operations / 100000,
                estimated_cost=(estimated_operations / 100000) * 0.06,
                region=region
            ))
        
        return components
    
    def estimate_storage_cost(self, workload_type: str, monthly_users: int,
                             region: str = "us-central1") -> List[PriceComponent]:
        """Estimate storage costs"""
        components = []
        
        # Object storage
        estimated_storage_gb = max(20, monthly_users * 0.005)
        
        components.append(PriceComponent(
            service="Cloud Storage",
            sku="Standard",
            description="Cloud Storage Standard",
            usage_unit="GB",
            pricing_unit="GB-month",
            price_per_unit=0.02,
            estimated_usage=estimated_storage_gb,
            estimated_cost=0.02 * estimated_storage_gb,
            region=region
        ))
        
        # Persistent Disk for VMs/containers
        if workload_type not in ["serverless"]:
            estimated_disk_gb = max(100, monthly_users * 0.01)
            
            components.append(PriceComponent(
                service="Persistent Disk",
                sku="SSD",
                description="Persistent Disk SSD",
                usage_unit="GB",
                pricing_unit="GB-month",
                price_per_unit=0.17,
                estimated_usage=estimated_disk_gb,
                estimated_cost=0.17 * estimated_disk_gb,
                region=region
            ))
        
        return components
    
    def estimate_networking_cost(self, workload_type: str, monthly_users: int,
                                region: str = "us-central1") -> List[PriceComponent]:
        """Estimate networking costs"""
        components = []
        
        # Egress traffic estimation
        estimated_egress_gb = monthly_users * 0.5  # 500MB per user
        
        components.append(PriceComponent(
            service="Network",
            sku="Egress",
            description="Network Egress to Internet",
            usage_unit="GB",
            pricing_unit="GB",
            price_per_unit=0.12,
            estimated_usage=estimated_egress_gb,
            estimated_cost=0.12 * estimated_egress_gb,
            region=region
        ))
        
        # Load balancer if needed
        if workload_type not in ["serverless"]:
            components.append(PriceComponent(
                service="Load Balancing",
                sku="HTTP(S)",
                description="HTTP(S) Load Balancer",
                usage_unit="hour",
                pricing_unit="hour",
                price_per_unit=0.025,
                estimated_usage=720,
                estimated_cost=0.025 * 720,
                region=region
            ))
        
        return components
    
    def estimate_additional_services(self, workload_type: str, monthly_users: int,
                                    region: str = "us-central1") -> List[PriceComponent]:
        """Estimate additional service costs"""
        components = []
        
        if workload_type == "ml_inference":
            # Vertex AI prediction
            estimated_predictions = monthly_users * 10
            
            components.append(PriceComponent(
                service="Vertex AI",
                sku="Prediction",
                description="Vertex AI Online Prediction",
                usage_unit="hour",
                pricing_unit="hour",
                price_per_unit=3.15,
                estimated_usage=720,
                estimated_cost=3.15 * 720,
                region=region
            ))
            
            components.append(PriceComponent(
                service="Vertex AI",
                sku="Node",
                description="Vertex AI Prediction Node",
                usage_unit="node",
                pricing_unit="hour",
                price_per_unit=1.1025,
                estimated_usage=720,
                estimated_cost=1.1025 * 720,
                region=region
            ))
        
        elif workload_type == "realtime_streaming":
            # Pub/Sub
            estimated_messages = monthly_users * 1000
            
            components.append(PriceComponent(
                service="Pub/Sub",
                sku="Message",
                description="Pub/Sub Messages",
                usage_unit="GB",
                pricing_unit="GB",
                price_per_unit=0.40,
                estimated_usage=estimated_messages * 0.001,  # Assume 1KB per message
                estimated_cost=estimated_messages * 0.001 * 0.40,
                region=region
            ))
        
        return components
    
    def calculate_total_cost(self, architecture: str, machine_type: Optional[str],
                            workload_type: str, region: str, cpu: int, ram: int,
                            estimated_rps: int, monthly_users: int) -> PriceEstimate:
        """
        Calculate total monthly cost
        
        Args:
            architecture: serverless/containers/virtual_machines
            machine_type: Specific machine type if available
            workload_type: Type of workload
            region: Target region
            cpu: Number of vCPUs
            ram: RAM in GB
            estimated_rps: Estimated requests per second
            monthly_users: Estimated monthly users
            
        Returns:
            Complete price estimate
        """
        start_time = time.time()
        
        # Get region code
        region_code = self._get_region_code(region)
        
        # Calculate all cost components
        all_components = []
        
        # Compute costs
        compute_components = self.estimate_compute_cost(
            architecture=architecture,
            machine_type=machine_type,
            cpu=cpu,
            ram=ram,
            region=region_code,
            estimated_rps=estimated_rps,
            monthly_users=monthly_users
        )
        all_components.extend(compute_components)
        
        # Database costs
        db_components = self.estimate_database_cost(
            workload_type=workload_type,
            monthly_users=monthly_users,
            region=region_code
        )
        all_components.extend(db_components)
        
        # Storage costs
        storage_components = self.estimate_storage_cost(
            workload_type=workload_type,
            monthly_users=monthly_users,
            region=region_code
        )
        all_components.extend(storage_components)
        
        # Networking costs
        network_components = self.estimate_networking_cost(
            workload_type=workload_type,
            monthly_users=monthly_users,
            region=region_code
        )
        all_components.extend(network_components)
        
        # Additional services
        additional_components = self.estimate_additional_services(
            workload_type=workload_type,
            monthly_users=monthly_users,
            region=region_code
        )
        all_components.extend(additional_components)
        
        # Calculate total
        total_cost = sum(comp.estimated_cost for comp in all_components)
        
        # Calculate confidence based on data sources
        confidence = 0.95 if not self.mock_mode else 0.85
        
        processing_time_ms = int((time.time() - start_time) * 1000)
        
        logger.info(f"💰 Total cost calculated: ${total_cost:.2f}/month (confidence: {confidence:.1%})")
        logger.info(f"⏱️  Calculation time: {processing_time_ms}ms")
        
        return PriceEstimate(
            total_monthly_usd=total_cost,
            components=all_components,
            region=region_code,
            architecture=architecture,
            machine_type=machine_type,
            timestamp=datetime.now(),
            confidence=confidence,
            cache_hit=False
        )
    
    def _get_region_code(self, region_name: str) -> str:
        """Convert region name to GCP region code"""
        for region_group, codes in self.regions.items():
            if region_name.lower() in region_group.lower():
                return codes[0]  # Return first region in group
        
        # Default to us-central1
        return "us-central1"
    
    def calculate_alternative_prices(self, primary_estimate: PriceEstimate,
                                   alternative_architectures: List[str]) -> Dict[str, float]:
        """Calculate prices for alternative architectures"""
        alternative_prices = {}
        
        for alt_arch in alternative_architectures:
            if alt_arch == primary_estimate.architecture:
                continue
            
            # Simplified alternative calculation (30% adjustment)
            if alt_arch == "serverless":
                multiplier = 0.7  # Serverless is often cheaper
            elif alt_arch == "containers":
                multiplier = 1.1  # Containers slightly more expensive
            else:  # virtual_machines
                multiplier = 1.2  # VMs most expensive
            
            alternative_price = primary_estimate.total_monthly_usd * multiplier
            alternative_prices[alt_arch] = round(alternative_price, 2)
            
            logger.debug(f"Alternative {alt_arch}: ${alternative_price:.2f}/month")
        
        return alternative_prices
    
    def get_status(self) -> Dict[str, Any]:
        """Get client status"""
        return {
            "initialized": True,
            "mock_mode": self.mock_mode,
            "api_available": not self.mock_mode,
            "cache_enabled": self.use_cache,
            "cache_entries": len(self.cache),
            "regions_available": len(self.regions),
            "default_prices_loaded": len(self.default_prices) > 0
        }