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
            from tools.critic import CriticAgent
            
            # Create agents with appropriate reasoning levels
            overseer_agent = OverseerAgent(reasoning_level="high")
            perception_agent = PerceptionAgent(reasoning_level="medium")
            operator_agent = OperatorAgent(reasoning_level="medium")
            critic_agent = CriticAgent(reasoning_level="high")
            
            # Register agents
            self.register_agent(overseer_agent)
            self.register_agent(perception_agent)
            self.register_agent(operator_agent)
            self.register_agent(critic_agent)
            
            # Inject critic agent into overseer for plan validation
            overseer_agent.critic_agent = critic_agent
            
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
    
    def _execute_step(self, step_index: int, step: Any) -> bool:
        """Execute a single step using agent-specific dispatch."""
        try:
            # Normalize step format
            if isinstance(step, dict):
                desc = step.get("description", f"Step {step_index+1}")
                agent = step.get("next_agent", "perception")
                action = step.get("action", "analyze")
            else:
                desc = str(step)
                agent, action = "perception", "analyze"

            self.logger.info(f"Dispatching step {step_index+1} → agent={agent} action={action}")

            # Include recent history + memory context
            common = {
                "goal": self._current_goal_desc(),
                "step_description": desc,
                "step_number": len(self.execution_history) + 1,
                "execution_history": self.execution_history[-10:],
                "memory_context": self.memory.get_memory_context_for_agent(agent, action, desc),
            }

            if agent not in self.agents:
                self.logger.warning(f"No agent registered for {agent}")
                return False

            payload = {"action": action, **common}
            # Pass through coordinates/text if present
            if isinstance(step, dict):
                for k in ("coordinates","text","target","hints"):
                    if k in step: 
                        payload[k] = step[k]

            result = self.agents[agent].process(payload)
            success = bool(result and result.get("success"))

            # Record step execution
            self.execution_history.append({
                "step_index": step_index,
                "step_description": desc,
                "step_agent": agent,
                "step_action": action,
                "operation_result": result,
                "timestamp": time.time()
            })
            
            return success
            
        except Exception as e:
            self.logger.error(f"Error executing step {step_index}: {e}")
            return False
    

    

    
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
