#!/usr/bin/env python3
"""
MAIN.PY - Professional Production Application
Core System: Data Processing Engine
Version: 1.0.0

Features:
- Modular architecture with separation of concerns
- Comprehensive logging and monitoring
- Robust error handling and retry mechanisms
- Configuration management
- Performance metrics and health checks
- CLI interface with argument parsing
- Type hints and full documentation

Author: Senior Software Architect
Created: 2024
"""

import logging
import argparse
import sys
import time
import json
from pathlib import Path
from typing import Optional, List, Dict, Any, Tuple, Callable
from dataclasses import dataclass, asdict
from enum import Enum, auto
from datetime import datetime
import signal
import threading

# Third-party imports would be listed in requirements.txt
# import requests
# import numpy as np
# from sqlalchemy import create_engine

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class AppStatus(Enum):
    """Application status enumeration"""
    INITIALIZING = auto()
    RUNNING = auto()
    PAUSED = auto()
    STOPPING = auto()
    TERMINATED = auto()

@dataclass
class AppConfig:
    """Application configuration dataclass"""
    debug: bool = False
    max_retries: int = 3
    timeout: int = 30
    data_file: Path = Path("data/output.json")
    log_level: str = "INFO"
    enable_metrics: bool = True
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert config to dictionary for serialization"""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AppConfig':
        """Create config from dictionary"""
        return cls(**data)

class PerformanceMetrics:
    """Track and report application performance metrics"""
    
    def __init__(self):
        self.start_time: Optional[float] = None
        self.end_time: Optional[float] = None
        self.items_processed: int = 0
        self.errors_count: int = 0
        self.retry_count: int = 0
    
    def start_timer(self) -> None:
        """Start performance timer"""
        self.start_time = time.time()
    
    def stop_timer(self) -> None:
        """Stop performance timer"""
        self.end_time = time.time()
    
    def get_elapsed_time(self) -> float:
        """Get elapsed time in seconds"""
        if self.start_time is None:
            return 0.0
        end = self.end_time if self.end_time else time.time()
        return end - self.start_time
    
    def increment_processed(self, count: int = 1) -> None:
        """Increment processed items count"""
        self.items_processed += count
    
    def increment_errors(self, count: int = 1) -> None:
        """Increment error count"""
        self.errors_count += count
    
    def increment_retries(self, count: int = 1) -> None:
        """Increment retry count"""
        self.retry_count += count
    
    def get_summary(self) -> Dict[str, Any]:
        """Get metrics summary"""
        return {
            "elapsed_time_seconds": round(self.get_elapsed_time(), 2),
            "items_processed": self.items_processed,
            "errors_count": self.errors_count,
            "retry_count": self.retry_count,
            "items_per_second": round(self.items_processed / self.get_elapsed_time(), 2) if self.get_elapsed_time() > 0 else 0
        }

class DataProcessor:
    """Main data processing class with business logic"""
    
    def __init__(self, config: AppConfig, metrics: PerformanceMetrics):
        self.config = config
        self.metrics = metrics
        self.processed_count = 0
        logger.info("DataProcessor initialized with config: %s", config)
    
    def process_data(self, input_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Process input data with error handling and validation"""
        if not input_data:
            logger.warning("Empty input data received")
            return []
        
        processed_data = []
        
        for index, item in enumerate(input_data):
            try:
                logger.debug("Processing item %d: %s", index, item.get('id', 'unknown'))
                processed_item = self._process_single_item(item)
                processed_data.append(processed_item)
                self.processed_count += 1
                self.metrics.increment_processed()
                
            except Exception as e:
                logger.error("Failed to process item %s: %s", item, e)
                self.metrics.increment_errors()
                if self.config.debug:
                    logger.exception("Detailed error traceback:")
        
        logger.info("Processed %d items successfully", self.processed_count)
        return processed_data
    
    def _process_single_item(self, item: Dict[str, Any]) -> Dict[str, Any]:
        """Process a single data item - core business logic"""
        # Validate required fields
        if 'id' not in item:
            raise ValueError("Item missing required 'id' field")
        
        # Create a copy to avoid modifying the original
        processed_item = item.copy()
        
        # Add processing metadata
        processed_item['processed_at'] = datetime.utcnow().isoformat()
        processed_item['processing_version'] = '1.0.0'
        
        # Example transformations
        if 'name' in processed_item and isinstance(processed_item['name'], str):
            processed_item['name_upper'] = processed_item['name'].upper()
            processed_item['name_length'] = len(processed_item['name'])
        
        if 'value' in processed_item and isinstance(processed_item['value'], (int, float)):
            processed_item['value_doubled'] = processed_item['value'] * 2
        
        return processed_item
    
    def save_results(self, data: List[Dict[str, Any]], output_path: Path) -> bool:
        """Save processed data to file with retry logic"""
        max_attempts = self.config.max_retries + 1  # +1 for the initial attempt
        
        for attempt in range(max_attempts):
            try:
                output_path.parent.mkdir(parents=True, exist_ok=True)
                
                # Save as JSON with pretty formatting
                with open(output_path, 'w', encoding='utf-8') as f:
                    json.dump({
                        "metadata": {
                            "processed_at": datetime.utcnow().isoformat(),
                            "items_count": len(data),
                            "processing_time_seconds": round(self.metrics.get_elapsed_time(), 2)
                        },
                        "data": data
                    }, f, indent=2, ensure_ascii=False)
                
                logger.info("Results saved to %s", output_path)
                return True
                
            except Exception as e:
                self.metrics.increment_errors()
                self.metrics.increment_retries()
                
                if attempt < max_attempts - 1:
                    wait_time = 2 ** attempt  # Exponential backoff
                    logger.warning("Save attempt %d failed, retrying in %d seconds: %s", 
                                  attempt + 1, wait_time, e)
                    time.sleep(wait_time)
                else:
                    logger.error("All %d save attempts failed: %s", max_attempts, e)
                    return False

class HealthMonitor:
    """Monitor application health and provide status updates"""
    
    def __init__(self):
        self.status = AppStatus.INITIALIZING
        self.last_check = time.time()
        self.health_checks = {}
    
    def update_status(self, new_status: AppStatus) -> None:
        """Update application status"""
        self.status = new_status
        logger.info("Application status changed to: %s", new_status.name)
    
    def register_health_check(self, name: str, check_func: Callable[[], bool]) -> None:
        """Register a health check function"""
        self.health_checks[name] = check_func
    
    def perform_health_check(self) -> Dict[str, bool]:
        """Perform all registered health checks"""
        results = {}
        for name, check_func in self.health_checks.items():
            try:
                results[name] = check_func()
            except Exception as e:
                logger.error("Health check %s failed: %s", name, e)
                results[name] = False
        return results

class Application:
    """Main application class coordinating all components"""
    
    def __init__(self, config: AppConfig):
        self.config = config
        self.metrics = PerformanceMetrics()
        self.health_monitor = HealthMonitor()
        self.processor = DataProcessor(config, self.metrics)
        self.shutdown_event = threading.Event()
        
        # Register signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        
        logger.info("Application initialized")
    
    def _signal_handler(self, signum, frame) -> None:
        """Handle shutdown signals gracefully"""
        logger.info("Received signal %d, initiating shutdown", signum)
        self.shutdown_event.set()
    
    def run(self) -> int:
        """Main application entry point - returns exit code"""
        exit_code = 0
        self.metrics.start_timer()
        self.health_monitor.update_status(AppStatus.RUNNING)
        
        try:
            logger.info("Starting application execution")
            
            # Load data
            sample_data = self._load_sample_data()
            logger.info("Loaded %d items for processing", len(sample_data))
            
            # Process data
            processed_data = self.processor.process_data(sample_data)
            
            # Check if shutdown was requested
            if self.shutdown_event.is_set():
                logger.warning("Shutdown requested during processing")
                return 130
            
            # Save results
            success = self.processor.save_results(processed_data, self.config.data_file)
            
            if not success:
                logger.error("Failed to save results")
                exit_code = 1
            
            # Log performance metrics
            self.metrics.stop_timer()
            if self.config.enable_metrics:
                self._log_performance_metrics()
            
            self.health_monitor.update_status(AppStatus.TERMINATED)
            logger.info("Application completed with exit code: %d", exit_code)
            
        except KeyboardInterrupt:
            logger.info("Application interrupted by user")
            exit_code = 130
        except Exception as e:
            logger.critical("Unhandled application error: %s", e)
            logger.exception("Critical error details:")
            exit_code = 1
        finally:
            self.health_monitor.update_status(AppStatus.TERMINATED)
        
        return exit_code
    
    def _load_sample_data(self) -> List[Dict[str, Any]]:
        """Load sample data for demonstration"""
        return [
            {"id": 1, "name": "Alice", "value": 100, "category": "A"},
            {"id": 2, "name": "Bob", "value": 200, "category": "B"},
            {"id": 3, "name": "Charlie", "value": 300, "category": "A"},
            {"id": 4, "name": "Diana", "value": 400, "category": "C"},
            {"id": 5, "name": "Evan", "value": 500, "category": "B"},
            {"id": 6, "name": "Fiona", "value": 600, "category": "A"},
            {"id": 7, "name": "George", "value": 700, "category": "C"},
            {"id": 8, "name": "Hannah", "value": 800, "category": "B"},
            {"id": 9, "name": "Ian", "value": 900, "category": "A"},
            {"id": 10, "name": "Jessica", "value": 1000, "category": "C"}
        ]
    
    def _log_performance_metrics(self) -> None:
        """Log performance metrics summary"""
        metrics = self.metrics.get_summary()
        logger.info("Performance Metrics:")
        for key, value in metrics.items():
            logger.info("  %s: %s", key, value)

def parse_arguments() -> argparse.Namespace:
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description="Professional Data Processing Application",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    
    parser.add_argument(
        '--debug', '-d',
        action='store_true',
        help='Enable debug mode with verbose logging'
    )
    
    parser.add_argument(
        '--output', '-o',
        type=Path,
        default=Path("data/output.json"),
        help='Output file path'
    )
    
    parser.add_argument(
        '--max-retries',
        type=int,
        default=3,
        help='Maximum number of retry attempts for operations'
    )
    
    parser.add_argument(
        '--timeout',
        type=int,
        default=30,
        help='Operation timeout in seconds'
    )
    
    parser.add_argument(
        '--log-level',
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
        default='INFO',
        help='Set the logging level'
    )
    
    parser.add_argument(
        '--disable-metrics',
        action='store_true',
        help='Disable performance metrics collection'
    )
    
    return parser.parse_args()

def setup_logging(log_level: str) -> None:
    """Setup logging with specified level"""
    level = getattr(logging, log_level.upper(), logging.INFO)
    logging.getLogger().setLevel(level)
    
    # Update existing handlers
    for handler in logging.getLogger().handlers:
        handler.setLevel(level)

def main() -> int:
    """
    Main function - application entry point
    Returns: Exit code (0 for success, non-zero for errors)
    """
    # Parse command line arguments
    args = parse_arguments()
    
    # Initialize configuration
    config = AppConfig(
        debug=args.debug,
        max_retries=args.max_retries,
        timeout=args.timeout,
        data_file=args.output,
        log_level=args.log_level,
        enable_metrics=not args.disable_metrics
    )
    
    # Setup logging
    setup_logging(config.log_level)
    
    if config.debug:
        logger.debug("Debug mode enabled")
        logger.debug("Configuration: %s", config.to_dict())
    
    # Create and run application
    app = Application(config)
    exit_code = app.run()
    
    return exit_code

if __name__ == "__main__":
    # Professional error handling and clean exit
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        logger.info("Application terminated by user")
        sys.exit(130)
    except Exception as e:
        logger.critical("Fatal error during application startup: %s", e)
        sys.exit(1)

