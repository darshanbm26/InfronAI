"""
Production-grade Gemini client with MULTI-KEY support
Uses multiple API keys with intelligent rotation on quota exhaustion
"""

import os
import json
import logging
import re
import time
import random
from typing import Dict, Any, Optional, List
from pathlib import Path

# Load .env file
try:
    from dotenv import load_dotenv
    env_file = Path(__file__).parent.parent.parent / ".env"
    if env_file.exists():
        load_dotenv(env_file)
except ImportError:
    pass

import google.genai as genai

logger = logging.getLogger(__name__)

class GeminiClient:
    """Production Gemini client with multi-key support and rotation"""
    
    # Class-level state shared across all instances
    _shared_key_index = 0  # Track last working key across all instances
    _shared_key_failures = {}  # Track failures across all instances
    _shared_clients = {}  # Share initialized clients
    _api_keys_loaded = []  # Shared list of API keys
    _all_keys_exhausted = False  # Global flag: true if ALL keys tried and exhausted
    
    def __init__(self):
        # Load all API keys (only once for the first instance)
        if not GeminiClient._api_keys_loaded:
            GeminiClient._api_keys_loaded = self._load_api_keys()
            GeminiClient._shared_key_failures = {name: 0 for name, _ in GeminiClient._api_keys_loaded}
            self._initialize_all_clients()
        
        # Use shared state
        self.api_keys = GeminiClient._api_keys_loaded
        self.clients = GeminiClient._shared_clients
        self.key_failures = GeminiClient._shared_key_failures
        
        self.model_name = os.getenv("GEMINI_MODEL", "gemini-2.5-flash-lite")
        self.max_tokens = int(os.getenv("GEMINI_MAX_TOKENS", "8192"))
        self.temperature = float(os.getenv("GEMINI_TEMPERATURE", "0.2"))
        self.mock_mode = False
        
        # Log initialization with current working key
        current_key = self._get_current_key_name()
        logger.info(f"🔑 Using shared key pool: {len(self.api_keys)} keys, starting with {current_key}")
    
    def _load_api_keys(self) -> List[str]:
        """Load all available API keys from environment"""
        keys = []
        
        # Primary key
        primary = os.getenv("GEMINI_API_KEY")
        if primary:
            keys.append(("PRIMARY", primary))
            logger.debug(f"✅ Loaded PRIMARY API key: {primary[:20]}...")
        
        # Backup keys 1-3
        for i in range(1, 4):
            backup = os.getenv(f"GEMINI_API_KEY_{i}")
            if backup:
                keys.append((f"BACKUP_{i}", backup))
                logger.debug(f"✅ Loaded BACKUP_{i} API key: {backup[:20]}...")
        
        if not keys:
            logger.error("❌ NO API KEYS FOUND IN ENVIRONMENT!")
            
        return keys
    
    def _initialize_all_clients(self) -> None:
        """Initialize genai.Client for each API key (shared across instances)"""
        for name, api_key in GeminiClient._api_keys_loaded:
            try:
                client = genai.Client(api_key=api_key)
                GeminiClient._shared_clients[name] = client
                logger.info(f"✅ Initialized shared client: {name}")
            except Exception as e:
                logger.error(f"❌ Failed to initialize {name}: {e}")
                GeminiClient._shared_clients[name] = None
    
    def _get_current_key_name(self) -> str:
        """Get name of current key from shared state"""
        if GeminiClient._shared_key_index < len(self.api_keys):
            return self.api_keys[GeminiClient._shared_key_index][0]
        return "UNKNOWN"
    
    def _rotate_to_next_key(self) -> bool:
        """Rotate to next available API key (updates shared state)"""
        original_index = GeminiClient._shared_key_index
        original_key = self._get_key_name_at(original_index)
        
        # If only 1 key, no rotation possible
        if len(self.api_keys) == 1:
            logger.error("⚠️  Only 1 API key available - cannot rotate!")
            return False
        
        # Try next keys
        for i in range(len(self.api_keys) - 1):  # -1 because we don't want to try the same key
            GeminiClient._shared_key_index = (GeminiClient._shared_key_index + 1) % len(self.api_keys)
            key_name = self._get_current_key_name()
            
            if self.clients.get(key_name) is not None and key_name != original_key:
                logger.warning(f"🔄 KEY ROTATION (SHARED): {original_key} → {key_name}")
                return True
        
        # All keys exhausted - no more keys available
        logger.error("⚠️  ALL API KEYS EXHAUSTED! No more keys to try...")
        return False
    
    def _get_key_name_at(self, index: int) -> str:
        """Get key name at specific index"""
        if 0 <= index < len(self.api_keys):
            return self.api_keys[index][0]
        return "UNKNOWN"
    
    def _get_current_client(self) -> Optional[Any]:
        """Get current active client"""
        key_name = self._get_current_key_name()
        return self.clients.get(key_name)
    
    def call_with_retry(self, prompt: str, max_retries: int = 3) -> Optional[Any]:
        """Call Gemini with key rotation on quota exhaustion"""
        # Fast-fail if all keys already exhausted globally
        if GeminiClient._all_keys_exhausted:
            logger.warning("⚡ All keys already exhausted globally - skipping Gemini calls")
            raise Exception("All API keys quota exhausted (global state)")
        
        last_error = None
        
        for attempt in range(max_retries):
            # Check global exhaustion flag at start of each attempt
            if GeminiClient._all_keys_exhausted:
                logger.warning("⚡ All keys exhausted globally - skipping retry")
                raise Exception("All API keys quota exhausted (global state)")
            
            client = self._get_current_client()
            
            if client is None:
                logger.error(f"❌ No valid client available for {self._get_current_key_name()}")
                self._rotate_to_next_key()
                continue
            
            try:
                key_name = self._get_current_key_name()
                logger.debug(f"📤 Attempt {attempt + 1}/{max_retries} with key: {key_name}")
                
                response = client.models.generate_content(
                    model=self.model_name,
                    contents=prompt,
                    config={
                        "temperature": self.temperature,
                        "max_output_tokens": self.max_tokens,
                        "top_p": 0.95,
                        "top_k": 40
                    }
                )
                
                # Success - reset failure count
                self.key_failures[key_name] = 0
                logger.info(f"✅ Success with {key_name}")
                return response
                
            except Exception as e:
                error_str = str(e)
                last_error = e
                self.key_failures[key_name] = self.key_failures.get(key_name, 0) + 1
                
                # Check if quota exhausted (429)
                if "429" in error_str or "RESOURCE_EXHAUSTED" in error_str:
                    logger.warning(f"⚠️  Quota exhausted on {key_name} (attempt {attempt + 1})")
                    
                    # Rotate to next key immediately
                    if not self._rotate_to_next_key():
                        logger.error("❌ No more keys available - marking all keys as globally exhausted")
                        GeminiClient._all_keys_exhausted = True
                        raise Exception("All API keys quota exhausted")
                    
                    # Exponential backoff before retry
                    wait_time = (2 ** attempt) + random.uniform(0, 1)
                    logger.info(f"⏳ Waiting {wait_time:.1f}s before next key...")
                    time.sleep(wait_time)
                
                else:
                    # Non-quota error
                    logger.error(f"❌ API error on {key_name}: {error_str[:100]}")
                    raise e
        
        # All retries exhausted
        logger.error(f"❌ Failed after {max_retries} retries with all keys")
        raise last_error if last_error else Exception("All retries failed")
    
    def parse_intent(self, user_input: str) -> Dict[str, Any]:
        """Parse user infrastructure intent with multi-key support"""
        start_time = time.time()
        
        # Try real Gemini with key rotation
        try:
            result = self._parse_with_gemini(user_input)
            processing_time_ms = int((time.time() - start_time) * 1000)
            result["processing_time_ms"] = processing_time_ms
            result["active_key"] = self._get_current_key_name()
            return result
        except Exception as e:
            logger.error(f"❌ All keys exhausted or failed: {e}")
            # Fall back to enhanced mock
            logger.info("📋 Falling back to enhanced mock parsing")
            result = self._enhanced_mock_parse(user_input)
            processing_time_ms = int((time.time() - start_time) * 1000)
            result["processing_time_ms"] = processing_time_ms
            result["active_key"] = "MOCK_FALLBACK"
            return result
    
    def _parse_with_gemini(self, user_input: str) -> Dict[str, Any]:
        """Parse intent using real Gemini API with key rotation"""
        prompt = self._create_intent_parsing_prompt(user_input)
        
        try:
            # Call Gemini with retry logic and key rotation
            response = self.call_with_retry(prompt)
            
            if not response:
                raise ValueError("Failed to get response after retries")
            
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
                elif hasattr(candidate, 'content') and hasattr(candidate.content, 'text'):
                    response_text = candidate.content.text
            
            if not response_text:
                logger.warning("Empty response text from Gemini")
                raise ValueError(f"Could not extract text from Gemini response")
            
            # Extract JSON from response
            json_text = self._extract_json_from_response(response_text)
            
            if not json_text:
                logger.warning(f"Could not extract JSON from: {response_text[:200]}...")
                raise ValueError("Could not extract valid JSON from response")
            
            result = json.loads(json_text)
            
            # Validate structure
            self._validate_intent_structure(result)
            
            # Add metadata
            result["parsing_source"] = "gemini_api"
            result["llm_model"] = self.model_name
            result["active_key"] = self._get_current_key_name()
            
            logger.info(f"✅ Intent parsed via REAL Gemini with {self._get_current_key_name()}: "
                       f"{result['workload_type']} (confidence: {result.get('parsing_confidence', 'N/A')})")
            
            return result
            
        except json.JSONDecodeError as e:
            logger.error(f"JSON parsing error: {e}")
            return self._enhanced_mock_parse(user_input)
        except Exception as e:
            logger.error(f"Gemini API error in parsing: {e}")
            raise  # Re-raise to let caller handle
    
    def _create_intent_parsing_prompt(self, user_input: str) -> str:
        """Create optimized prompt for intent parsing"""
        return f"""You are an expert cloud infrastructure architect at Google. Parse this user request into structured JSON.

USER REQUEST: "{user_input}"

Return ONLY a valid JSON object with these exact fields:
- workload_type (must be one of: api_backend, web_app, data_processing, ml_inference, batch_processing, realtime_streaming, mobile_backend, gaming_server)
- scale (object with: monthly_users [number], estimated_rps [number], traffic_pattern [string: steady/variable/bursty/seasonal])
- requirements (object with: latency [string: ultra_low/low/medium/high], availability [string: critical/high/medium/low], geography [string], compliance [array of strings: gdpr/hipaa/pci/soc2])
- constraints (object with: budget_sensitivity [string: very_low/low/medium/high], team_experience [string: beginner/junior/intermediate/senior/expert], time_to_market [string: immediate/1_week/1_month/flexible])
- parsing_confidence (number between 0.0 and 1.0 with 2 decimal places)

Example response format:
{{
    "workload_type": "api_backend",
    "scale": {{
        "monthly_users": 50000,
        "estimated_rps": 150,
        "traffic_pattern": "variable"
    }},
    "requirements": {{
        "latency": "low",
        "availability": "high",
        "geography": "india",
        "compliance": ["gdpr"]
    }},
    "constraints": {{
        "budget_sensitivity": "medium",
        "team_experience": "intermediate",
        "time_to_market": "1_week"
    }},
    "parsing_confidence": 0.94
}}

CRITICAL INSTRUCTIONS:
1. Return ONLY the JSON object, no markdown, no code blocks, no explanations
2. Estimate realistic numbers based on the user request
3. If geography not specified, use "global"
4. If compliance not mentioned, use empty array []
5. parsing_confidence should reflect your certainty

JSON OUTPUT:"""
    
    def _extract_json_from_response(self, text: str) -> Optional[str]:
        """Extract JSON from Gemini response with multiple fallbacks"""
        # Remove markdown code blocks
        text = re.sub(r'```json\s*', '', text)
        text = re.sub(r'```\s*', '', text)
        
        # Try to find JSON pattern
        patterns = [
            r'(\{.*\})',
            r'(\[.*\])',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.DOTALL)
            if match:
                json_str = match.group(1)
                try:
                    json.loads(json_str)
                    return json_str
                except json.JSONDecodeError:
                    continue
        
        return None
    
    def _validate_intent_structure(self, data: Dict[str, Any]) -> None:
        """Validate the parsed intent structure"""
        required_fields = [
            "workload_type", "scale", "requirements", 
            "constraints", "parsing_confidence"
        ]
        
        for field in required_fields:
            if field not in data:
                raise ValueError(f"Missing required field: {field}")
        
        valid_workloads = [
            "api_backend", "web_app", "data_processing", 
            "ml_inference", "batch_processing", "realtime_streaming",
            "mobile_backend", "gaming_server"
        ]
        
        if data["workload_type"] not in valid_workloads:
            raise ValueError(f"Invalid workload_type: {data['workload_type']}")
        
        confidence = data["parsing_confidence"]
        if not isinstance(confidence, (int, float)) or not 0.0 <= confidence <= 1.0:
            raise ValueError(f"Invalid parsing_confidence: {confidence}")
    
    def _enhanced_mock_parse(self, user_input: str) -> Dict[str, Any]:
        """Enhanced mock parsing with realistic heuristics"""
        from datetime import datetime
        
        logger.info(f"🔧 Enhanced mock parsing: {user_input[:80]}...")
        
        input_lower = user_input.lower()
        
        # Workload detection
        workload_keywords = {
            "api_backend": ["api", "rest", "endpoint", "backend", "service", "microservice"],
            "web_app": ["web", "website", "frontend", "app", "portal", "dashboard"],
            "data_processing": ["data", "process", "etl", "pipeline", "batch", "analytics"],
            "ml_inference": ["ml", "ai", "model", "learning", "inference", "prediction"],
            "realtime_streaming": ["stream", "realtime", "live", "websocket", "socket"],
            "mobile_backend": ["mobile", "app backend", "ios", "android"],
            "gaming_server": ["game", "gaming", "multiplayer", "real-time"],
        }
        
        detected_workload = "api_backend"
        for workload, keywords in workload_keywords.items():
            if any(keyword in input_lower for keyword in keywords):
                detected_workload = workload
                break
        
        # Scale detection
        numbers = re.findall(r'\d+[,.]?\d*[kKmM]?', user_input)
        monthly_users = 10000
        
        if numbers:
            try:
                num_str = numbers[0].lower()
                if 'k' in num_str:
                    monthly_users = int(float(num_str.replace('k', '')) * 1000)
                elif 'm' in num_str:
                    monthly_users = int(float(num_str.replace('m', '')) * 1000000)
                else:
                    monthly_users = int(float(num_str))
            except:
                monthly_users = random.choice([1000, 5000, 10000, 50000, 100000])
        
        # RPS calculation
        if monthly_users < 1000:
            estimated_rps = random.randint(1, 10)
        elif monthly_users < 10000:
            estimated_rps = random.randint(10, 50)
        elif monthly_users < 100000:
            estimated_rps = random.randint(50, 200)
        else:
            estimated_rps = random.randint(200, 1000)
        
        # Traffic pattern
        if any(word in input_lower for word in ["steady", "consistent", "constant"]):
            traffic_pattern = "steady"
        elif any(word in input_lower for word in ["burst", "spike", "peak", "seasonal"]):
            traffic_pattern = "bursty"
        elif any(word in input_lower for word in ["variable", "varying"]):
            traffic_pattern = "variable"
        else:
            traffic_pattern = random.choice(["steady", "variable", "bursty"])
        
        # Geography
        regions = {
            "india": ["india", "mumbai", "delhi", "bangalore", "chennai"],
            "us-east": ["us east", "virginia", "us-east"],
            "us-west": ["us west", "oregon", "california", "us-west"],
            "europe": ["europe", "frankfurt", "london", "paris"],
            "asia": ["asia", "singapore", "tokyo"],
            "australia": ["australia", "sydney"],
        }
        
        geography = "global"
        for region, keywords in regions.items():
            if any(keyword in input_lower for keyword in keywords):
                geography = region
                break
        
        # Requirements
        latency = "medium"
        if "low latency" in input_lower or "fast" in input_lower:
            latency = "low"
        elif "ultra low" in input_lower or "real-time" in input_lower:
            latency = "ultra_low"
        
        availability = "high"
        if "high availability" in input_lower or "99.9" in input_lower:
            availability = "critical"
        
        compliance = []
        if any(word in input_lower for word in ["gdpr", "europe"]):
            compliance.append("gdpr")
        if any(word in input_lower for word in ["hipaa", "health"]):
            compliance.append("hipaa")
        if any(word in input_lower for word in ["pci", "payment"]):
            compliance.append("pci")
        
        # Constraints
        budget_sensitivity = "medium"
        if "budget" in input_lower and any(word in input_lower for word in ["tight", "low", "cost"]):
            budget_sensitivity = "high"
        
        team_experience = "intermediate"
        if any(word in input_lower for word in ["junior", "beginner", "new"]):
            team_experience = "junior"
        elif any(word in input_lower for word in ["senior", "expert"]):
            team_experience = "senior"
        
        time_to_market = "1_month"
        if any(word in input_lower for word in ["urgent", "immediate", "asap"]):
            time_to_market = "immediate"
        elif any(word in input_lower for word in ["week", "soon"]):
            time_to_market = "1_week"
        
        # Confidence
        word_count = len(user_input.split())
        if word_count < 10:
            confidence = round(random.uniform(0.6, 0.75), 2)
        elif word_count < 30:
            confidence = round(random.uniform(0.75, 0.85), 2)
        else:
            confidence = round(random.uniform(0.85, 0.95), 2)
        
        return {
            "workload_type": detected_workload,
            "scale": {
                "monthly_users": monthly_users,
                "estimated_rps": estimated_rps,
                "traffic_pattern": traffic_pattern
            },
            "requirements": {
                "latency": latency,
                "availability": availability,
                "geography": geography,
                "compliance": compliance
            },
            "constraints": {
                "budget_sensitivity": budget_sensitivity,
                "team_experience": team_experience,
                "time_to_market": time_to_market
            },
            "parsing_confidence": confidence,
            "parsing_source": "enhanced_mock",
            "llm_model": "mock_heuristic_v1",
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def get_status(self) -> Dict[str, Any]:
        """Get detailed client status with all keys"""
        key_status = {}
        for name, _ in self.api_keys:
            key_status[name] = {
                "initialized": self.clients.get(name) is not None,
                "failures": self.key_failures.get(name, 0),
                "is_current": (name == self._get_current_key_name())
            }
        
        return {
            "current_key": self._get_current_key_name(),
            "total_keys": len(self.api_keys),
            "keys": key_status,
            "model_name": self.model_name,
            "mock_mode": self.mock_mode,
            "max_tokens": self.max_tokens,
            "temperature": self.temperature
        }
    
    def get_key_rotation_info(self) -> Dict[str, Any]:
        """Get key rotation status"""
        return {
            "current_key": self._get_current_key_name(),
            "current_index": self.current_key_index,
            "total_keys": len(self.api_keys),
            "key_failures": dict(self.key_failures),
            "keys": [name for name, _ in self.api_keys]
        }
