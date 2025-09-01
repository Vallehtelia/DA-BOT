"""
Overseer Agent implementation for the AI agent platform.
Handles planning, coordination, and high-level decision making.
"""

from typing import Dict, Any, List
from tools.agents.gpt_oss_agent import GPTOSS20BAgent

class OverseerAgent(GPTOSS20BAgent):
    """Overseer agent for planning and coordination."""
    
    def __init__(self, config_path: str = "config", reasoning_level: str = "high"):
        super().__init__("overseer", config_path, reasoning_level)
        
        # Overseer-specific capabilities
        self.planning_history = []
        self.coordination_state = {}
    
    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process overseer-specific tasks."""
        action = input_data.get("action", "unknown")
        
        if action == "plan":
            return self._create_plan(input_data)
        elif action == "coordinate":
            return self._coordinate_action(input_data)
        elif action == "evaluate":
            return self._evaluate_progress(input_data)
        elif action == "complete":
            return self._assess_completion(input_data)
        else:
            return super().process(input_data)
    
    def _create_plan(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a detailed plan for achieving a goal."""
        try:
            goal = input_data.get("goal", "Unknown goal")
            
            # Create planning prompt
            planning_prompt = {
                "action": "plan",
                "goal": goal,
                "context": "Create a detailed plan to achieve this goal. Break it down into specific, actionable steps that can be executed by perception and operator agents."
            }
            
            # Get LLM response with higher token limit for planning
            response = self._call_llm_with_planning_tokens(planning_prompt)
            
            if response:
                plan_steps = response.get("plan", [])
                if plan_steps:
                    # Validate and clean plan steps
                    cleaned_steps = self._clean_plan_steps(plan_steps)
                    
                    # Update response with cleaned steps
                    response["plan"] = cleaned_steps
                    response["plan_quality"] = self._assess_plan_quality(cleaned_steps)
                    
                    # Store planning history
                    self.planning_history.append({
                        "goal": goal,
                        "plan": cleaned_steps,
                        "timestamp": self._get_timestamp()
                    })
                    
                    # Mark as successful if we have a plan
                    response["success"] = True
                else:
                    self.logger.warning(f"Planner returned no steps; using fallback. Raw response: {response}")
            else:
                self.logger.warning("Planner returned no response; using fallback.")
            
            return response
            
        except Exception as e:
            self.logger.error(f"Error creating plan: {e}")
            return self._create_error_response(f"Plan creation failed: {e}", "plan")
    
    def _call_llm_with_planning_tokens(self, prompt: str) -> Dict[str, Any]:
        """Call LLM with higher token limit for planning tasks."""
        try:
            # Create the prompt from input data
            formatted_prompt = self._create_prompt_from_input(prompt)
            
            # Get LLM response with higher token limit for planning
            llm_response = self._call_llm_with_tokens(formatted_prompt, max_new_tokens=1024)
            
            if llm_response is None:
                return self._create_error_response("LLM call failed", "error")
            
            # Extract JSON response
            if isinstance(llm_response, str):
                json_response = self._extract_text_from_llm_response(llm_response)
            elif isinstance(llm_response, dict) and "content" in llm_response:
                content = llm_response["content"]
                json_response = self._extract_text_from_llm_response(content)
            else:
                json_response = str(llm_response)
            
            # Parse JSON and add defaults BEFORE validation
            try:
                import json

                if isinstance(json_response, dict):
                    parsed_response = json_response  # already a dict
                else:
                    parsed_response = json.loads(json_response)

                # Add defaults BEFORE validation
                parsed_response.setdefault("role", self.agent_name)
                parsed_response.setdefault("success", False)
                parsed_response.setdefault("action", "plan")

                validated_response = self._validate_json_response(parsed_response)

            except json.JSONDecodeError:
                fixed_response = self._attempt_json_fix(json_response)
                if fixed_response:
                    fixed_response.setdefault("role", self.agent_name)
                    fixed_response.setdefault("success", False)
                    fixed_response.setdefault("action", "plan")
                    validated_response = self._validate_json_response(fixed_response)
                else:
                    return self._create_error_response("Invalid JSON response from LLM", "error")
            
            if validated_response is None:
                return self._create_error_response("Response validation failed", "error")
            
            # Treat "has plan" as success and ensure required fields
            if isinstance(validated_response, dict):
                plan = validated_response.get("plan", [])
                if isinstance(plan, list) and len(plan) > 0:
                    validated_response["success"] = True
                validated_response.setdefault("role", self.agent_name)
                validated_response.setdefault("action", "plan")
            
            return validated_response
            
        except Exception as e:
            self.logger.error(f"Error in planning LLM call: {e}")
            return self._create_error_response(f"Planning LLM call failed: {e}", "error")
    
    def _coordinate_action(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Coordinate between perception and operation phases."""
        try:
            step_description = input_data.get("step_description", "")
            perception_result = input_data.get("perception_result", {})
            
            # Create coordination prompt
            coordination_prompt = {
                "action": "coordinate",
                "step_description": step_description,
                "perception_result": perception_result,
                "context": "Based on the perception result, decide what action should be taken next. Consider the current step and what needs to be accomplished."
            }
            
            # Get LLM response
            response = super().process(coordination_prompt)
            
            if response and response.get("success"):
                # Update coordination state
                self.coordination_state.update({
                    "current_step": step_description,
                    "last_perception": perception_result,
                    "last_coordination": response
                })
            
            return response
            
        except Exception as e:
            self.logger.error(f"Error coordinating action: {e}")
            return self._create_error_response(f"Coordination failed: {e}", "coordinate")
    
    def _evaluate_progress(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate progress towards the goal."""
        try:
            current_step = input_data.get("step_description", "")
            operation_result = input_data.get("operation_result", {})
            
            # Create evaluation prompt
            evaluation_prompt = {
                "action": "evaluate",
                "step_description": current_step,
                "operation_result": operation_result,
                "context": "Evaluate if this step was executed successfully and what progress was made towards the overall goal."
            }
            
            # Get LLM response
            response = super().process(evaluation_prompt)
            
            if response and response.get("success"):
                # Assess step success
                step_success = self._assess_step_success(operation_result)
                response["step_success"] = step_success
                response["progress_assessment"] = self._assess_overall_progress()
            
            return response
            
        except Exception as e:
            self.logger.error(f"Error evaluating progress: {e}")
            return self._create_error_response(f"Progress evaluation failed: {e}", "evaluate")
    
    def _assess_completion(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Assess if the goal has been completed."""
        try:
            goal = input_data.get("goal", "")
            execution_history = input_data.get("execution_history", [])
            
            # Create completion assessment prompt
            completion_prompt = {
                "action": "complete",
                "goal": goal,
                "execution_history": execution_history,
                "context": "Assess if the goal has been fully completed based on the execution history and current state."
            }
            
            # Get LLM response
            response = super().process(completion_prompt)
            
            if response and response.get("success"):
                # Determine completion status
                completion_status = self._determine_completion_status(execution_history)
                response["completion_status"] = completion_status
                response["completion_confidence"] = self._calculate_completion_confidence(execution_history)
            
            return response
            
        except Exception as e:
            self.logger.error(f"Error assessing completion: {e}")
            return self._create_error_response(f"Completion assessment failed: {e}", "complete")
    
    def _clean_plan_steps(self, steps: List[Any]) -> List[Dict[str, Any]]:
        """Clean and validate plan steps, converting to structured format."""
        cleaned_steps = []
        
        for i, step in enumerate(steps, 1):
            if isinstance(step, str) and step.strip():
                # Convert string step to structured format
                cleaned_step = {
                    "id": i,
                    "description": step.strip(),
                    "next_agent": "perception",  # Default agent
                    "action": "analyze",  # Default action
                    "success_criteria": "Step completed successfully",
                    "priority": "medium"
                }
                cleaned_steps.append(cleaned_step)
            elif isinstance(step, dict):
                next_agent = step.get("next_agent") or step.get("agent") or "perception"
                next_agent = str(next_agent).lower()
                if next_agent not in ("perception", "operator", "overseer"):
                    next_agent = "perception"

                action = step.get("action")
                if not action:
                    action = "analyze" if next_agent == "perception" else ("navigate" if next_agent == "operator" else "plan")

                # Normalize operator actions to supported set
                if next_agent == "operator":
                    allowed_ops = {"move_mouse","click","type","scroll","navigate"}
                    if action not in allowed_ops:
                        action = "navigate"

                cleaned_step = {
                    "id": step.get("id", i),
                    "description": step.get("description", f"Step {i}"),
                    "next_agent": next_agent,
                    "action": action,
                    "success_criteria": step.get("success_criteria", "Step completed successfully"),
                    "priority": step.get("priority", "medium")
                }
                cleaned_steps.append(cleaned_step)
        
        # Ensure we have at least some steps
        if not cleaned_steps:
            cleaned_steps = [
                {
                    "id": 1,
                    "description": "Analyze current environment and identify requirements",
                    "next_agent": "perception",
                    "action": "analyze",
                    "success_criteria": "List required capabilities identified",
                    "priority": "high"
                },
                {
                    "id": 2,
                    "description": "Plan specific actions needed",
                    "next_agent": "overseer",
                    "action": "plan",
                    "success_criteria": "Action plan created",
                    "priority": "high"
                },
                {
                    "id": 3,
                    "description": "Execute planned actions",
                    "next_agent": "operator",
                    "action": "execute",
                    "success_criteria": "Actions executed successfully",
                    "priority": "high"
                },
                {
                    "id": 4,
                    "description": "Verify results and assess completion",
                    "next_agent": "overseer",
                    "action": "evaluate",
                    "success_criteria": "Goal completion verified",
                    "priority": "high"
                }
            ]
        
        return cleaned_steps
    
    def _assess_plan_quality(self, steps: List[Any]) -> float:
        """Assess plan quality (0..1) for list of strings or dicts."""
        if not steps:
            return 0.0

        # Normalize to text
        texts = []
        for s in steps:
            if isinstance(s, dict):
                texts.append(str(s.get("description", "")))
            else:
                texts.append(str(s))

        quality = 0.0
        # Step count (detail)
        if len(texts) >= 3:
            quality += 0.3
        elif len(texts) >= 1:
            quality += 0.1

        # Specificity
        keywords = ["click", "type", "move", "analyze", "verify", "check", "open", "run", "read", "report"]
        specific = sum(1 for t in texts if any(k in t.lower() for k in keywords))
        quality += min(0.4, specific * 0.1)

        # Ordering / multi-step
        if len(texts) > 1:
            quality += 0.2

        return min(1.0, quality)
    
    def _assess_step_success(self, operation_result: Dict[str, Any]) -> bool:
        """Assess if a step was executed successfully."""
        if not operation_result:
            return False
        
        # Check for success indicators
        status = operation_result.get("status", "")
        success = operation_result.get("success", False)
        
        if isinstance(success, bool):
            return success
        
        if isinstance(status, str):
            return status.lower() in ["success", "completed", "done", "ok"]
        
        return False
    
    def _assess_overall_progress(self) -> str:
        """Assess overall progress towards the goal."""
        if not self.coordination_state:
            return "unknown"
        
        # Simple progress assessment based on coordination state
        if "last_coordination" in self.coordination_state:
            return "in_progress"
        
        return "starting"
    
    def _determine_completion_status(self, execution_history: List[Dict[str, Any]]) -> str:
        """Determine if the goal has been completed."""
        if not execution_history:
            return "unknown"
        
        # Check if all steps were successful
        successful_steps = sum(1 for step in execution_history if step.get("success", False))
        total_steps = len(execution_history)
        
        if total_steps == 0:
            return "unknown"
        
        completion_ratio = successful_steps / total_steps
        
        if completion_ratio >= 0.8:
            return "complete"
        elif completion_ratio >= 0.5:
            return "mostly_complete"
        else:
            return "incomplete"
    
    def _calculate_completion_confidence(self, execution_history: List[Dict[str, Any]]) -> float:
        """Calculate confidence in completion assessment (0.0 to 1.0)."""
        if not execution_history:
            return 0.0
        
        # Simple confidence calculation based on execution history
        confidence = 0.5  # Base confidence
        
        # Increase confidence with more execution history
        if len(execution_history) >= 3:
            confidence += 0.3
        elif len(execution_history) >= 1:
            confidence += 0.1
        
        # Increase confidence with successful steps
        successful_steps = sum(1 for step in execution_history if step.get("success", False))
        total_steps = len(execution_history)
        
        if total_steps > 0:
            success_ratio = successful_steps / total_steps
            confidence += success_ratio * 0.2
        
        return min(1.0, confidence)
    
    def get_agent_info(self) -> Dict[str, Any]:
        """Get overseer-specific agent information."""
        info = super().get_agent_info()
        info.update({
            "planning_history_count": len(self.planning_history),
            "coordination_state": self.coordination_state,
            "specialization": "planning_and_coordination"
        })
        return info
