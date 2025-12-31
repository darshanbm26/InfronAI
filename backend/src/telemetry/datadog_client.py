"""
Production-grade Datadog telemetry client
Works with or without API keys
"""

import os
import logging
import json
from datetime import datetime
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from enum import Enum

from .metrics_registry import get_metric_definitions, validate_metric_name

logger = logging.getLogger(__name__)

class TelemetryMode(Enum):
    DATADOG = "datadog"
    CONSOLE = "console"
    FILE = "file"
    DISABLED = "disabled"

@dataclass
class TelemetryConfig:
    mode: TelemetryMode = TelemetryMode.CONSOLE
    datadog_api_key: Optional[str] = None
    datadog_app_key: Optional[str] = None
    datadog_site: str = "datadoghq.com"
    log_file: str = "telemetry.log"
    enable_metrics: bool = True
    enable_logs: bool = True
    enable_events: bool = True

class TelemetryClient:
    """Unified telemetry client with multiple backends"""
    
    def __init__(self, config: Optional[TelemetryConfig] = None):
        self.config = config or self._load_config_from_env()
        self.metrics_buffer = []
        self.events_buffer = []
        self.metric_definitions = get_metric_definitions()
        
        self._initialize_client()
        
        logger.info(f"📡 Telemetry initialized in {self.config.mode.value} mode")
    
    def _load_config_from_env(self) -> TelemetryConfig:
        """Load configuration from environment variables"""
        dd_api_key = os.getenv("DD_API_KEY")
        dd_app_key = os.getenv("DD_APP_KEY")
        
        mode = TelemetryMode.CONSOLE
        if dd_api_key and dd_app_key:
            mode = TelemetryMode.DATADOG
        elif os.getenv("TELEMETRY_MODE") == "file":
            mode = TelemetryMode.FILE
        elif os.getenv("TELEMETRY_DISABLED", "false").lower() == "true":
            mode = TelemetryMode.DISABLED
        
        return TelemetryConfig(
            mode=mode,
            datadog_api_key=dd_api_key,
            datadog_app_key=dd_app_key,
            datadog_site=os.getenv("DD_SITE", "datadoghq.com"),
            log_file=os.getenv("TELEMETRY_LOG_FILE", "telemetry.log"),
            enable_metrics=os.getenv("TELEMETRY_ENABLE_METRICS", "true").lower() == "true",
            enable_logs=os.getenv("TELEMETRY_ENABLE_LOGS", "true").lower() == "true",
            enable_events=os.getenv("TELEMETRY_ENABLE_EVENTS", "true").lower() == "true"
        )
    
    def _initialize_client(self):
        """Initialize the appropriate telemetry backend"""
        if self.config.mode == TelemetryMode.DATADOG:
            self._init_datadog()
        elif self.config.mode == TelemetryMode.FILE:
            self._init_file_logging()
        elif self.config.mode == TelemetryMode.DISABLED:
            logger.info("📡 Telemetry disabled")
    
    def _init_datadog(self):
        """Initialize Datadog API client"""
        try:
            from datadog_api_client import ApiClient, Configuration
            from datadog_api_client.v1.api.metrics_api import MetricsApi
            from datadog_api_client.v1.api.events_api import EventsApi
            from datadog_api_client.v2.api.logs_api import LogsApi
            
            self.configuration = Configuration()
            self.configuration.api_key["apiKeyAuth"] = self.config.datadog_api_key
            self.configuration.api_key["appKeyAuth"] = self.config.datadog_app_key
            self.configuration.server_variables["site"] = self.config.datadog_site
            
            self.api_client = ApiClient(self.configuration)
            self.metrics_api = MetricsApi(self.api_client)
            self.events_api = EventsApi(self.api_client)
            self.logs_api = LogsApi(self.api_client)
            
            logger.info(f"✅ Datadog telemetry enabled for site: {self.config.datadog_site}")
            
        except ImportError:
            logger.error("datadog-api-client not installed. Falling back to console mode.")
            self.config.mode = TelemetryMode.CONSOLE
        except Exception as e:
            logger.error(f"Failed to initialize Datadog: {e}")
            self.config.mode = TelemetryMode.CONSOLE
    
    def _init_file_logging(self):
        """Initialize file-based telemetry"""
        try:
            # Ensure log directory exists
            log_dir = os.path.dirname(self.config.log_file)
            if log_dir and not os.path.exists(log_dir):
                os.makedirs(log_dir)
            
            logger.info(f"📁 File telemetry enabled: {self.config.log_file}")
        except Exception as e:
            logger.error(f"Failed to initialize file logging: {e}")
            self.config.mode = TelemetryMode.CONSOLE
    
    def submit_metric(self, name: str, value: float, tags: Optional[List[str]] = None, 
                     timestamp: Optional[datetime] = None):
        """
        Submit a metric with validation
        
        Args:
            name: Metric name (must be in registry)
            value: Metric value
            tags: Optional tags
            timestamp: Optional timestamp
        """
        if not self.config.enable_metrics:
            return
        
        # Validate metric name
        if not validate_metric_name(name):
            logger.warning(f"Unknown metric name: {name}")
        
        tags = tags or []
        timestamp = timestamp or datetime.now()
        
        metric_entry = {
            "name": name,
            "value": value,
            "tags": tags,
            "timestamp": timestamp.isoformat(),
            "type": "gauge"
        }
        
        # Add to buffer
        self.metrics_buffer.append(metric_entry)
        
        # Process based on mode
        if self.config.mode == TelemetryMode.DATADOG:
            self._submit_metric_to_datadog(metric_entry)
        elif self.config.mode == TelemetryMode.CONSOLE:
            self._log_metric_to_console(metric_entry)
        elif self.config.mode == TelemetryMode.FILE:
            self._write_metric_to_file(metric_entry)
    
    def _submit_metric_to_datadog(self, metric: Dict[str, Any]):
        """Submit metric to Datadog"""
        try:
            from datadog_api_client.v1.model.metrics_payload import MetricsPayload
            from datadog_api_client.v1.model.series import Series
            from datadog_api_client.v1.model.point import Point
            import time
            from datetime import datetime
            
            # Convert ISO timestamp string to Unix timestamp
            timestamp_str = metric["timestamp"]
            if isinstance(timestamp_str, str):
                # Parse ISO format timestamp and convert to Unix timestamp
                dt = datetime.fromisoformat(timestamp_str)
                unix_timestamp = int(dt.timestamp())
            else:
                unix_timestamp = int(time.time())
            
            # Create Point with [timestamp, value] format
            point = Point([unix_timestamp, metric["value"]])
            
            series = Series(
                metric=metric["name"],
                points=[point],
                tags=metric["tags"],
                type=metric.get("type", "gauge")
            )
            
            body = MetricsPayload(series=[series])
            self.metrics_api.submit_metrics(body=body)
            
        except Exception as e:
            logger.error(f"Failed to submit metric to Datadog: {e}")
    
    def _log_metric_to_console(self, metric: Dict[str, Any]):
        """Log metric to console"""
        tags_str = f" tags={metric['tags']}" if metric['tags'] else ""
        print(f"📈 METRIC: {metric['name']}={metric['value']}{tags_str}")
    
    def _write_metric_to_file(self, metric: Dict[str, Any]):
        """Write metric to file"""
        try:
            with open(self.config.log_file, 'a') as f:
                f.write(json.dumps(metric) + '\n')
        except Exception as e:
            logger.error(f"Failed to write metric to file: {e}")
    
    def submit_log(self, source: str, message: Dict[str, Any], 
                  tags: Optional[List[str]] = None, level: str = "info"):
        """
        Submit a structured log
        
        Args:
            source: Source of the log
            message: Structured log message
            tags: Optional tags
            level: Log level (info, warning, error, debug)
        """
        if not self.config.enable_logs:
            return
        
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "source": source,
            "level": level,
            "message": message,
            "tags": tags or []
        }
        
        # Process based on mode
        if self.config.mode == TelemetryMode.DATADOG:
            self._submit_log_to_datadog(log_entry)
        elif self.config.mode == TelemetryMode.CONSOLE:
            self._log_to_console(log_entry)
        elif self.config.mode == TelemetryMode.FILE:
            self._write_log_to_file(log_entry)
    
    def _submit_log_to_datadog(self, log: Dict[str, Any]):
        """Submit log to Datadog"""
        try:
            from datadog_api_client.v2.model.http_log import HTTPLog
            from datadog_api_client.v2.model.http_log_item import HTTPLogItem
            
            log_item = HTTPLogItem(
                message=json.dumps(log["message"]),
                ddsource=log["source"],
                ddtags=",".join(log["tags"]) if log["tags"] else "",
                hostname="cloud-sentinel-backend",
                service="infrastructure-advisor",
                status=log["level"].upper()
            )
            
            body = HTTPLog([log_item])
            self.logs_api.submit_log(body=body)
            
        except Exception as e:
            logger.error(f"Failed to submit log to Datadog: {e}")
    
    def _log_to_console(self, log: Dict[str, Any]):
        """Log to console"""
        level = log["level"].upper()
        event = log["message"].get("event", "unknown")
        
        # Color codes for different levels
        colors = {
            "INFO": "\033[94m",      # Blue
            "WARNING": "\033[93m",   # Yellow
            "ERROR": "\033[91m",     # Red
            "DEBUG": "\033[90m",     # Gray
        }
        
        color = colors.get(level, "\033[0m")
        reset = "\033[0m"
        
        print(f"{color}[{level}] {event}{reset}: {json.dumps(log['message'], indent=2)}")
    
    def _write_log_to_file(self, log: Dict[str, Any]):
        """Write log to file"""
        try:
            with open(self.config.log_file, 'a') as f:
                f.write(json.dumps(log) + '\n')
        except Exception as e:
            logger.error(f"Failed to write log to file: {e}")
    
    def emit_event(self, title: str, text: str, tags: Optional[List[str]] = None,
                  alert_type: str = "info", priority: str = "normal"):
        """
        Emit a business event
        
        Args:
            title: Event title
            text: Event description
            tags: Optional tags
            alert_type: info, success, warning, error
            priority: low, normal, high
        """
        if not self.config.enable_events:
            return
        
        event_entry = {
            "timestamp": datetime.now().isoformat(),
            "title": title,
            "text": text,
            "tags": tags or [],
            "alert_type": alert_type,
            "priority": priority
        }
        
        self.events_buffer.append(event_entry)
        
        if self.config.mode == TelemetryMode.DATADOG:
            self._emit_event_to_datadog(event_entry)
        elif self.config.mode == TelemetryMode.CONSOLE:
            self._log_event_to_console(event_entry)
        elif self.config.mode == TelemetryMode.FILE:
            self._write_event_to_file(event_entry)
    
    def _emit_event_to_datadog(self, event: Dict[str, Any]):
        """Emit event to Datadog"""
        try:
            from datadog_api_client.v1.model.event_create_request import EventCreateRequest
            
            body = EventCreateRequest(
                title=event["title"],
                text=event["text"],
                tags=event["tags"],
                alert_type=event["alert_type"],
                priority=event["priority"]
            )
            
            self.events_api.create_event(body=body)
            
        except Exception as e:
            logger.error(f"Failed to emit event to Datadog: {e}")
    
    def _log_event_to_console(self, event: Dict[str, Any]):
        """Log event to console"""
        alert_colors = {
            "info": "\033[94m",
            "success": "\033[92m",
            "warning": "\033[93m",
            "error": "\033[91m"
        }
        
        color = alert_colors.get(event["alert_type"], "\033[0m")
        reset = "\033[0m"
        
        print(f"{color}🔔 EVENT: {event['title']}{reset}")
        print(f"   {event['text']}")
        if event["tags"]:
            print(f"   Tags: {event['tags']}")
    
    def _write_event_to_file(self, event: Dict[str, Any]):
        """Write event to file"""
        try:
            with open(self.config.log_file, 'a') as f:
                f.write(json.dumps(event) + '\n')
        except Exception as e:
            logger.error(f"Failed to write event to file: {e}")
    
    def flush_buffers(self):
        """Flush all buffered telemetry data"""
        if self.config.mode == TelemetryMode.FILE:
            try:
                all_data = {
                    "metrics": self.metrics_buffer,
                    "events": self.events_buffer,
                    "timestamp": datetime.now().isoformat()
                }
                
                with open(self.config.log_file, 'w') as f:
                    json.dump(all_data, f, indent=2)
                
                logger.info(f"💾 Flushed telemetry buffers to {self.config.log_file}")
                self.metrics_buffer.clear()
                self.events_buffer.clear()
                
            except Exception as e:
                logger.error(f"Failed to flush buffers: {e}")
    
    def get_status(self) -> Dict[str, Any]:
        """Get telemetry client status"""
        return {
            "mode": self.config.mode.value,
            "enabled": self.config.mode != TelemetryMode.DISABLED,
            "metrics_enabled": self.config.enable_metrics,
            "logs_enabled": self.config.enable_logs,
            "events_enabled": self.config.enable_events,
            "buffered_metrics": len(self.metrics_buffer),
            "buffered_events": len(self.events_buffer),
            "datadog_configured": bool(self.config.datadog_api_key and self.config.datadog_app_key)
        }