"""
Main Overseer class for the AI agent platform.
Coordinates all agents and manages the main execution loop.
"""

import json
import logging
import time
from typing import Dict, Any, List, Optional
from pathlib import Path

from tools.memory import Memory
from tools.safety import FailsafeSystem
from tools.agents import BaseAgent

# Import real agent implementations - will be imported dynamically to avoid circular imports

class Overseer:
    """Main overseer that coordinates all agents and manages execution."""
    
    def __init__(self, config_path: str = "config"):
        self.config_path = Path(config_path)
        self.logger = logging.getLogger("overseer")
        
        # Initialize core systems
        self.memory = Memory()
        self.failsafes = FailsafeSystem()
        
        # Initialize agents (will be populated later)
        self.agents: Dict[str, BaseAgent] = {}
        
        # Initialize and register real agents
        self._initialize_agents()
        
        # Current execution state
        self.current_goal: Optional[str] = None
        self.current_plan: Optional[str] = None
        self.execution_history: List[Dict[str, Any]] = []
        
        # Load configuration
        self.mode_config = self._load_mode_config()
        
        self.logger.info("Overseer initialized")
    
    def _current_goal_desc(self) -> str:
        """Safely get the current goal description."""
        try:
            if not self.current_goal:
                return "Unknown goal"
            goal = self.memory.get_goal(self.current_goal)
            return goal.description if goal else "Unknown goal"
        except Exception:
            return "Unknown goal"
    
    def _redact_sensitive_info(self, text: str) -> str:
        """Redact sensitive information from logs."""
        import re
        # Redact password patterns
        text = re.sub(r'(pass(?:word)?[:=]\s*)([^\s,]+)', r'\1[REDACTED]', text, flags=re.IGNORECASE)
        # Redact email password patterns
        text = re.sub(r'(pass:\s*)([^\s,]+)', r'\1[REDACTED]', text, flags=re.IGNORECASE)
        return text
    
    def _initialize_agents(self):
        """Initialize and register all agents."""
        try:
            # Import agents dynamically to avoid circular imports
            from tools.overseer import OverseerAgent
            from tools.perception import PerceptionAgent
            from tools.operator import OperatorAgent
            
            # Create agents with appropriate reasoning levels
            overseer_agent = OverseerAgent(reasoning_level="high")
            perception_agent = PerceptionAgent(reasoning_level="medium")
            operator_agent = OperatorAgent(reasoning_level="medium")
            
            # Register agents
            self.register_agent(overseer_agent)
            self.register_agent(perception_agent)
            self.register_agent(operator_agent)
            
            self.logger.info(f"Initialized {len(self.agents)} agents: {list(self.agents.keys())}")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize agents: {e}")
            self.logger.warning("Overseer will run with limited functionality")
    
    def _load_mode_config(self) -> Dict[str, Any]:
        """Load mode configuration."""
        mode_file = self.config_path / "mode.json"
        if mode_file.exists():
            try:
                with open(mode_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                self.logger.warning(f"Failed to load mode config: {e}")
        
        return {"dry_run": True, "verbosity": "low"}
    
    def register_agent(self, agent: BaseAgent):
        """Register an agent with the overseer."""
        self.agents[agent.agent_name] = agent
        self.logger.info(f"Registered agent: {agent.agent_name}")
    
    def set_goal(self, goal_description: str, priority: int = 1) -> str:
        """Set a new goal for the system."""
        goal_id = self.memory.add_goal(goal_description, priority)
        self.current_goal = goal_id
        redacted_description = self._redact_sensitive_info(goal_description)
        self.logger.info(f"Set new goal: {goal_id} - {redacted_description}")
        return goal_id
    
    def create_plan(self, goal_id: str) -> str:
        """Create a plan for achieving the goal."""
        if not self.current_goal:
            raise ValueError("No goal set")
        
        # Get the goal details
        goal = self.memory.get_goal(goal_id)
        if not goal:
            raise ValueError(f"Goal {goal_id} not found")
        
        # Create initial plan using overseer agent
        if "overseer" in self.agents:
            overseer_agent = self.agents["overseer"]
            
            # Create rich planning prompt with full context
            planning_prompt = {
                "action": "plan",
                "goal": goal.description,
                "step_description": "Create a plan to achieve this goal",
                "step_number": 0,
                            "execution_history": self.execution_history[-10:],  # Last 10 steps for better context
            "memory_context": self.memory.get_memory_context_for_agent("overseer", "plan", goal.description),
                "context": (
                "Create a detailed plan to achieve this goal. Break it down into specific, actionable steps that can be executed by perception and operator agents. "
                "Respond ONLY with strict JSON per your system schema. "
                "Return a non-empty 'plan' array with 4–8 steps. Each step must include: description, next_agent ('perception'|'operator'|'overseer'), action, success_criteria, priority."
            )
            }
            
            # Get plan from overseer
            response = overseer_agent.process(planning_prompt)
            
            if response and response.get("success"):
                # Extract plan from response
                plan_steps = response.get("plan", [])
                if not plan_steps:
                    # Fallback: create a simple plan
                    plan_steps = [
                        "Step 1: Analyze current environment and identify requirements",
                        "Step 2: Gather detailed requirements and create action plan",
                        "Step 3: Execute the planned actions",
                        "Step 4: Validate results and complete the goal"
                    ]
                
                # Clean and structure the plan steps
                if hasattr(self.agents.get("overseer"), "_clean_plan_steps"):
                    plan_steps = self.agents["overseer"]._clean_plan_steps(plan_steps)
                
                plan_id = self.memory.create_plan(goal_id, plan_steps)
                self.current_plan = plan_id
                
                self.logger.info(f"Created plan: {plan_id} with {len(plan_steps)} steps")
                return plan_id
            else:
                # Fallback: create a simple plan
                plan_steps = [
                    "Step 1: Analyze current environment and identify requirements",
                    "Step 2: Gather detailed requirements and create action plan",
                    "Step 3: Execute the planned actions",
                    "Step 4: Validate results and complete the goal"
                ]
                
                # Clean and structure the plan steps
                if hasattr(self.agents.get("overseer"), "_clean_plan_steps"):
                    plan_steps = self.agents["overseer"]._clean_plan_steps(plan_steps)
                
                plan_id = self.memory.create_plan(goal_id, plan_steps)
                self.current_plan = plan_id
                self.logger.warning("Created fallback plan due to overseer agent failure")
                return plan_id
        else:
            # Fallback: create a simple plan
            plan_steps = [
                "Step 1: Analyze current environment and identify requirements",
                "Step 2: Gather detailed requirements and create action plan",
                "Step 3: Execute the planned actions",
                "Step 4: Validate results and complete the goal"
            ]
            
            # Clean and structure the plan steps
            if hasattr(self.agents.get("overseer"), "_clean_plan_steps"):
                plan_steps = self.agents["overseer"]._clean_plan_steps(plan_steps)
            
            plan_id = self.memory.create_plan(goal_id, plan_steps)
            self.current_plan = plan_id
            return plan_id
    

    def execute_plan(self) -> bool:
        """Execute the current plan."""
        if not self.current_plan:
            raise ValueError("No plan set")
        
        plan = self.memory.get_plan(self.current_plan)
        if not plan:
            raise ValueError(f"Plan {self.current_plan} not found")
        
        self.logger.info(f"Executing plan: {plan.id} with {len(plan.steps)} steps")
        
        # Update plan status
        self.memory.update_plan_step(plan.id, 0, "executing")
        
        # Execute each step
        for step_index, step_description in enumerate(plan.steps):
            # Check failsafes before proceeding
            if not self.failsafes.can_proceed():
                self.logger.critical("Cannot proceed due to failsafe activation")
                return False
            
            # Increment step counter
            self.failsafes.increment_step()
            
            self.logger.info(f"Executing step {step_index + 1}: {step_description}")
            
            # Execute the step
            step_success = self._execute_step(step_index, step_description)
            
            if not step_success:
                self.logger.error(f"Step {step_index + 1} failed")
                self.memory.update_plan_step(plan.id, step_index, "failed")
                return False
            
            # Update plan progress
            self.memory.update_plan_step(plan.id, step_index + 1)
            
            # Checkpoint after each step
            self.memory.checkpoint()
            
            # Small delay between steps
            time.sleep(0.1)
        
        # Mark plan as complete
        self.memory.update_plan_step(plan.id, len(plan.steps), "complete")
        self.logger.info("Plan execution completed successfully")
        return True
    
    def _execute_step(self, step_index: int, step_description: Any) -> bool:
        """Execute a single step."""
        try:
            # Handle both string and object step formats
            if isinstance(step_description, dict):
                step_desc = step_description.get("description", f"Step {step_index + 1}")
                step_agent = step_description.get("next_agent", "perception")
                step_action = step_description.get("action", "analyze")
            else:
                step_desc = str(step_description)
                step_agent = "perception"
                step_action = "analyze"
            
            # Phase 1: Perception - analyze current state
            perception_result = self._execute_perception_step(step_desc)
            if not perception_result:
                return False
            
            # Phase 2: Planning - decide what action to take
            action_plan = self._execute_planning_step(step_desc, perception_result)
            if not action_plan:
                return False
            
            # Phase 3: Operation - execute the action
            operation_result = self._execute_operation_step(action_plan)
            if not operation_result:
                return False
            
            # Phase 4: Validation - check if step was successful
            validation_result = self._execute_validation_step(step_desc, operation_result)
            
            # Record step execution
            self.execution_history.append({
                "step_index": step_index,
                "step_description": step_desc,
                "step_agent": step_agent,
                "step_action": step_action,
                "perception_result": perception_result,
                "action_plan": action_plan,
                "operation_result": operation_result,
                "validation_result": validation_result,
                "timestamp": time.time()
            })
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error executing step {step_index}: {e}")
            return False
    
    def _execute_perception_step(self, step_description: str) -> Optional[Dict[str, Any]]:
        """Execute perception step to analyze current state."""
        if "perception" not in self.agents:
            self.logger.warning("No perception agent available")
            return {"status": "no_agent", "elements": []}
        
        perception_agent = self.agents["perception"]
        
        # Create rich perception prompt with full context
        perception_prompt = {
            "action": "analyze",
            "goal": self._current_goal_desc(),
            "step_description": step_description,
            "step_number": len(self.execution_history) + 1,
            "execution_history": self.execution_history[-3:],  # Last 3 steps
            "memory_context": self.memory.get_memory_context_for_agent("perception", "analyze", step_description),
            "context": f"Goal: {self._current_goal_desc()}. Step {len(self.execution_history) + 1}: {step_description}. Analyze the current environment and identify what needs to be done."
        }
        
        # Process with perception agent
        response = perception_agent.process(perception_prompt)
        return response if response and response.get("success") else {
            "status": "success",
            "elements": [],
            "recommended_action": "continue"
        }
    
    def _execute_planning_step(self, step_description: str, perception_result: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Execute planning step to decide what action to take."""
        if "overseer" not in self.agents:
            self.logger.warning("No overseer agent available")
            return {"action": "continue", "reasoning": "no agent available"}
        
        overseer_agent = self.agents["overseer"]
        
        # Create rich planning prompt with full context
        planning_prompt = {
            "action": "coordinate",
            "goal": self._current_goal_desc(),
            "step_description": step_description,
            "step_number": len(self.execution_history) + 1,
            "perception_result": perception_result,
            "execution_history": self.execution_history[-10:],  # Last 10 steps for better context
            "memory_context": self.memory.get_memory_context_for_agent("overseer", "plan", step_description),
            "context": (
                f"Goal: {self._current_goal_desc()}. Step {len(self.execution_history) + 1}: {step_description}. "
                "Based on perception result, decide what action to take next. "
                "Return JSON with an operator-executable \"action\" set to one of "
                "[\"move_mouse\",\"click\",\"type\",\"scroll\",\"navigate\"]. "
                "If coordinates or text are required, include them."
            )
        }
        
        response = overseer_agent.process(planning_prompt)
        return response if response and response.get("success") else None
    
    def _execute_operation_step(self, action_plan: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Execute operation step to perform the planned action."""
        if "operator" not in self.agents:
            self.logger.warning("No operator agent available")
            return {"status": "no_agent", "action": "continue"}
        
        operator_agent = self.agents["operator"]
        
        # Coerce unsupported actions before calling Operator
        op_action = action_plan.get("action", "navigate")
        allowed = {"move_mouse", "click", "type", "scroll", "navigate"}
        if op_action not in allowed:
            op_action = action_plan.get("operator_action", "navigate")
            action_plan["action"] = op_action
        
        # Create rich operation prompt with full context
        operation_prompt = {
            "action": op_action,
            "goal": self._current_goal_desc(),
            "action_plan": action_plan,
            "step_number": len(self.execution_history) + 1,
            "execution_history": self.execution_history[-10:],  # Last 10 steps for better context
            "memory_context": self.memory.get_memory_context_for_agent("operator", "execute", action_plan.get("action", "unknown")),
            "context": f"Goal: {self._current_goal_desc()}. Execute the planned action: {op_action}."
        }
        
        # Execute the action
        response = operator_agent.process(operation_prompt)
        return response if response and response.get("success") else None
    
    def _execute_validation_step(self, step_description: str, operation_result: Dict[str, Any]) -> Dict[str, Any]:
        """Execute validation step to check if the step was successful."""
        if "critic" not in self.agents:
            return {"status": "no_agent", "evaluation": "pass"}
        
        critic_agent = self.agents["critic"]
        
        # Evaluate the step execution
        validation_prompt = {
            "action": "evaluate",
            "step_description": step_description,
            "operation_result": operation_result,
            "context": "Evaluate if the step was executed successfully"
        }
        
        response = critic_agent.process(validation_prompt)
        return response if response and response.get("success") else {"status": "error", "evaluation": "unknown"}
    
    def run(self, goal_description: str) -> bool:
        """Main run method - set goal, create plan, and execute."""
        try:
            redacted_description = self._redact_sensitive_info(goal_description)
            self.logger.info(f"Starting execution with goal: {redacted_description}")
            
            # Set the goal
            goal_id = self.set_goal(goal_description)
            
            # Create a plan
            plan_id = self.create_plan(goal_id)
            
            # Execute the plan
            success = self.execute_plan()
            
            if success:
                self.memory.update_goal_status(goal_id, "complete")
                self.logger.info("Goal completed successfully")
            else:
                self.memory.update_goal_status(goal_id, "failed")
                self.logger.error("Goal failed")
            
            return success
            
        except Exception as e:
            self.logger.error(f"Error during execution: {e}")
            if self.current_goal:
                self.memory.update_goal_status(self.current_goal, "failed")
            return False
    
    def get_status(self) -> Dict[str, Any]:
        """Get current system status."""
        return {
            "current_goal": self.current_goal,
            "current_plan": self.current_plan,
            "failsafe_status": self.failsafes.get_status_summary(),
            "registered_agents": list(self.agents.keys()),
            "execution_history_length": len(self.execution_history),
            "mode_config": self.mode_config
        }
    
    def shutdown(self):
        """Shutdown the overseer gracefully."""
        self.logger.info("Shutting down overseer...")
        
        # Create final checkpoint
        self.memory.checkpoint()
        
        # Clean up old checkpoints
        self.memory.cleanup_old_checkpoints()
        
        self.logger.info("Overseer shutdown complete")
