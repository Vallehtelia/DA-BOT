"""
Core failsafe system for the AI agent platform.
Handles killswitch, pause, budget monitoring, and safety checks.
"""

import os
import signal
import time
import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional, Callable
from dataclasses import dataclass
import threading

@dataclass
class BudgetLimits:
    """Budget limits for the system."""
    max_run_seconds: int = 1200
    max_steps: int = 200
    max_screenshots: int = 300
    max_requests: int = 100
    
    def __post_init__(self):
        """Filter out non-budget fields that might be passed from policies."""
        # Only keep the fields that are actually budget-related
        budget_fields = ['max_run_seconds', 'max_steps', 'max_screenshots', 'max_requests']
        for field in list(self.__dict__.keys()):
            if field not in budget_fields:
                delattr(self, field)

@dataclass
class SafetyStatus:
    """Current safety status of the system."""
    killswitch_active: bool = False
    pause_active: bool = False
    budget_exceeded: bool = False
    circuit_breakers: Dict[str, str] = None  # tool_name -> status
    loop_detection: Dict[str, int] = None    # action_signature -> count

class FailsafeSystem:
    """Core failsafe system for the AI agent platform."""
    
    def __init__(self, config_path: str = "config", control_path: str = "control"):
        self.config_path = Path(config_path)
        self.control_path = Path(control_path)
        self.control_path.mkdir(exist_ok=True)
        
        # Load configuration
        self.policies = self._load_policies()
        
        # Extract only budget-related policies
        budget_policies = {}
        policies_data = self.policies.get("policies", {})
        budget_fields = ['max_run_seconds', 'max_steps', 'max_screenshots', 'max_requests']
        for field in budget_fields:
            if field in policies_data:
                budget_policies[field] = policies_data[field]
        
        self.budget_limits = BudgetLimits(**budget_policies)
        
        # Initialize safety status
        self.safety_status = SafetyStatus(
            circuit_breakers={},
            loop_detection={}
        )
        
        # Runtime tracking
        self.start_time = time.time()
        self.step_count = 0
        self.screenshot_count = 0
        self.request_count = 0
        
        # Setup logging
        self.logger = logging.getLogger(__name__)
        
        # Dev override for safety features
        self.dev_disable_safety = bool(int(os.getenv("DISABLE_KILLSWITCH", "0")))
        if self.dev_disable_safety:
            self.logger.warning("DEV MODE: Safety features disabled via DISABLE_KILLSWITCH=1")
        
        # Setup signal handlers
        self._setup_signal_handlers()
        
        # Start watchdog thread
        self.watchdog_thread = threading.Thread(target=self._watchdog_loop, daemon=True)
        self.watchdog_thread.start()
        
        self.logger.info("Failsafe system initialized")
    
    def _load_policies(self) -> Dict[str, Any]:
        """Load policies from config file."""
        policies_file = self.config_path / "policies.yml"
        if policies_file.exists():
            try:
                import yaml
                with open(policies_file, 'r') as f:
                    return yaml.safe_load(f)
            except Exception as e:
                self.logger.warning(f"Failed to load policies: {e}")
        
        # Return default policies
        return {
            "policies": {
                "max_run_seconds": 1200,
                "max_steps": 200,
                "max_screenshots": 300,
                "max_requests": 100
            }
        }
    
    def _setup_signal_handlers(self):
        """Setup signal handlers for graceful shutdown."""
        def signal_handler(signum, frame):
            self.logger.info(f"Received signal {signum}, activating killswitch")
            self.activate_killswitch()
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
    
    def _watchdog_loop(self):
        """Watchdog thread that monitors system health."""
        while True:
            try:
                # Check control files
                self._check_control_files()
                
                # Check budgets
                self._check_budgets()
                
                # Update heartbeat
                self._update_heartbeat()
                
                time.sleep(2)  # Check every 2 seconds
                
            except Exception as e:
                self.logger.error(f"Watchdog error: {e}")
                time.sleep(5)
    
    def _check_control_files(self):
        """Check for control files and update safety status."""
        # Check killswitch
        killswitch_file = self.control_path / "killswitch.on"
        if killswitch_file.exists():
            if not self.safety_status.killswitch_active:
                self.safety_status.killswitch_active = True
                self.logger.critical("KILLSWITCH ACTIVATED via control file")
        
        # Check pause
        pause_file = self.control_path / "pause.on"
        if pause_file.exists():
            if not self.safety_status.pause_active:
                self.safety_status.pause_active = True
                self.logger.warning("System PAUSED via control file")
        else:
            if self.safety_status.pause_active:
                self.safety_status.pause_active = False
                self.logger.info("System RESUMED - pause file removed")
    
    def _check_budgets(self):
        """Check if any budget limits have been exceeded."""
        current_time = time.time()
        run_time = current_time - self.start_time
        
        # Check run time
        if run_time > self.budget_limits.max_run_seconds:
            if not self.safety_status.budget_exceeded:
                self.safety_status.budget_exceeded = True
                self.logger.critical(f"Budget exceeded: {run_time}s > {self.budget_limits.max_run_seconds}s")
        
        # Check step count
        if self.step_count > self.budget_limits.max_steps:
            if not self.safety_status.budget_exceeded:
                self.safety_status.budget_exceeded = True
                self.logger.critical(f"Step budget exceeded: {self.step_count} > {self.budget_limits.max_steps}")
        
        # Check screenshot count
        if self.screenshot_count > self.budget_limits.max_screenshots:
            if not self.safety_status.budget_exceeded:
                self.safety_status.budget_exceeded = True
                self.logger.critical(f"Screenshot budget exceeded: {self.screenshot_count} > {self.budget_limits.max_screenshots}")
    
    def _update_heartbeat(self):
        """Update the heartbeat file."""
        heartbeat_file = self.control_path / "heartbeat.json"
        heartbeat_data = {
            "timestamp": time.time(),
            "step_count": self.step_count,
            "run_time": time.time() - self.start_time,
            "safety_status": {
                "killswitch_active": self.safety_status.killswitch_active,
                "pause_active": self.safety_status.pause_active,
                "budget_exceeded": self.safety_status.budget_exceeded
            }
        }
        
        try:
            with open(heartbeat_file, 'w') as f:
                json.dump(heartbeat_data, f, indent=2)
        except Exception as e:
            self.logger.error(f"Failed to update heartbeat: {e}")
    
    def activate_killswitch(self):
        """Activate the killswitch."""
        self.safety_status.killswitch_active = True
        killswitch_file = self.control_path / "killswitch.on"
        try:
            killswitch_file.touch()
            self.logger.critical("KILLSWITCH ACTIVATED")
        except Exception as e:
            self.logger.error(f"Failed to create killswitch file: {e}")
    
    def deactivate_killswitch(self):
        """Deactivate the killswitch."""
        self.safety_status.killswitch_active = False
        killswitch_file = self.control_path / "killswitch.on"
        try:
            if killswitch_file.exists():
                killswitch_file.unlink()
                self.logger.info("Killswitch deactivated")
        except Exception as e:
            self.logger.error(f"Failed to remove killswitch file: {e}")
    
    def pause_system(self):
        """Pause the system."""
        self.safety_status.pause_active = True
        pause_file = self.control_path / "pause.on"
        try:
            pause_file.touch()
            self.logger.warning("System PAUSED")
        except Exception as e:
            self.logger.error(f"Failed to create pause file: {e}")
    
    def resume_system(self):
        """Resume the system."""
        self.safety_status.pause_active = False
        pause_file = self.control_path / "pause.on"
        try:
            if pause_file.exists():
                pause_file.unlink()
                self.logger.info("System RESUMED")
        except Exception as e:
            self.logger.error(f"Failed to remove pause file: {e}")
    
    def can_proceed(self) -> bool:
        """Check if the system can proceed with operations."""
        if self.dev_disable_safety:
            return True
        
        if self.safety_status.killswitch_active:
            self.logger.critical("Cannot proceed: KILLSWITCH ACTIVE")
            return False
        
        if self.safety_status.pause_active:
            self.logger.warning("Cannot proceed: System PAUSED")
            return False
        
        if self.safety_status.budget_exceeded:
            self.logger.critical("Cannot proceed: Budget exceeded")
            return False
        
        return True
    
    def increment_step(self):
        """Increment the step counter."""
        self.step_count += 1
    
    def increment_screenshot(self):
        """Increment the screenshot counter."""
        self.screenshot_count += 1
    
    def increment_request(self):
        """Increment the request counter."""
        self.request_count += 1
    
    def check_circuit_breaker(self, tool_name: str) -> bool:
        """Check if a circuit breaker is open for a tool."""
        status = self.safety_status.circuit_breakers.get(tool_name, "closed")
        return status == "closed"
    
    def open_circuit_breaker(self, tool_name: str, reason: str = "Unknown"):
        """Open a circuit breaker for a tool."""
        self.safety_status.circuit_breakers[tool_name] = "open"
        self.logger.warning(f"Circuit breaker opened for {tool_name}: {reason}")
    
    def close_circuit_breaker(self, tool_name: str):
        """Close a circuit breaker for a tool."""
        self.safety_status.circuit_breakers[tool_name] = "closed"
        self.logger.info(f"Circuit breaker closed for {tool_name}")
    
    def check_loop_detection(self, action_signature: str, max_repeats: int = 3) -> bool:
        """Check for repeated actions to detect loops."""
        count = self.safety_status.loop_detection.get(action_signature, 0)
        if count >= max_repeats:
            self.logger.warning(f"Loop detected for {action_signature}: {count} repeats")
            return False
        return True
    
    def record_action(self, action_signature: str):
        """Record an action for loop detection."""
        current_count = self.safety_status.loop_detection.get(action_signature, 0)
        self.safety_status.loop_detection[action_signature] = current_count + 1
    
    def get_status_summary(self) -> Dict[str, Any]:
        """Get a summary of the current safety status."""
        return {
            "killswitch_active": self.safety_status.killswitch_active,
            "pause_active": self.safety_status.pause_active,
            "budget_exceeded": self.safety_status.budget_exceeded,
            "run_time": time.time() - self.start_time,
            "step_count": self.step_count,
            "screenshot_count": self.screenshot_count,
            "request_count": self.request_count,
            "circuit_breakers": self.safety_status.circuit_breakers.copy(),
            "loop_detection": self.safety_status.loop_detection.copy()
        }
