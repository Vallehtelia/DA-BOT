"""
Overseer Agent implementation for the AI agent platform.
Handles planning, coordination, and high-level decision making.
"""

from typing import Dict, Any, List, Optional
from tools.agents.gpt_oss_agent import GPTOSS20BAgent

class OverseerAgent(GPTOSS20BAgent):
    """Overseer agent for planning and coordination."""
    
    CAPABILITIES = {
        "perception": {
            "actions": ["analyze", "identify"],
            "notes": "Analyze screenshots; find icons/text; return coordinates."
        },
        "operator": {
            "actions": ["move_mouse", "click", "type", "scroll", "navigate"],
            "notes": "Perform UI interactions with coordinates/text."
        },
        "overseer": {
            "actions": ["plan", "coordinate", "evaluate", "complete"],
            "notes": "Plan/route/evaluate."
        },
        # future:
        "critic": {"actions": ["evaluate"], "notes": "Assess step success"},
        "router": {"actions": ["validate","block","allow","circuit_breaker"], "notes": "Safety checks"}
    }
    
    def __init__(self, config_path: str = "config", reasoning_level: str = "high"):
        super().__init__("overseer", config_path, reasoning_level)
        
        # Overseer-specific capabilities
        self.planning_history = []
        self.coordination_state = {}
    
    def _canonicalize_overseer_response(self, data: dict) -> dict:
        """Canonicalize overseer response to standard format."""
        if not isinstance(data, dict): 
            return {"role": self.agent_name, "success": False, "action": "plan", "plan": []}
        
        # Map synonyms
        if not data.get("plan") and isinstance(data.get("steps"), list):
            data["plan"] = data.pop("steps")
        
        for st in data.get("plan", []):
            if "next_agent" not in st and "agent" in st:
                st["next_agent"] = str(st.pop("agent")).lower()
        
        # Set defaults
        data.setdefault("role", "overseer")
        data.setdefault("action", "plan")
        data.setdefault("success", False)
        if not isinstance(data.get("plan"), list):
            data["plan"] = []
        
        return data
    
    def _enforce_capabilities_and_preconditions(self, steps: list) -> list:
        """Enforce agent capabilities and insert missing preconditions."""
        out = []
        
        def needs_coords(s):
            act = s.get("action", "")
            return s.get("next_agent") == "operator" and act in {"move_mouse","click","scroll"}
        
        for s in steps:
            # Normalize action based on agent
            ag = s.get("next_agent", "perception")
            act = s.get("action") or ("analyze" if ag=="perception" else ("navigate" if ag=="operator" else "plan"))
            allowed = set(self.CAPABILITIES.get(ag, {}).get("actions", []))
            
            if act not in allowed:
                # Coerce to a safe default
                act = "analyze" if ag=="perception" else ("navigate" if ag=="operator" else "plan")
            s["action"] = act
            
            # Insert precondition for coordinates
            if needs_coords(s) and not s.get("coordinates"):
                out.append({
                    "id": None,
                    "description": "Identify target UI element and return coordinates required by next operator action",
                    "next_agent": "perception",
                    "action": "identify",
                    "success_criteria": "Coordinates provided",
                    "priority": "high"
                })
            
            out.append(s)
        
        # Renumber ids
        for i, st in enumerate(out, 1):
            st["id"] = i
        
        return out
    
    def _validate_plan_with_critic(self, goal: str, plan_steps: List[Any]) -> Optional[Dict[str, Any]]:
        """Validate plan with CriticAgent if available."""
        try:
            # Check if we have access to a critic agent
            # This would typically be injected by the Overseer
            if hasattr(self, 'critic_agent') and self.critic_agent:
                critic_input = {
                    "action": "evaluate",
                    "goal": goal,
                    "plan": plan_steps
                }
                return self.critic_agent.process(critic_input)
            else:
                # Fallback validation
                return self._fallback_plan_validation(plan_steps)
        except Exception as e:
            self.logger.error(f"Error validating plan with critic: {e}")
            return None
    
    def _improve_plan_with_critic(self, goal: str, plan_steps: List[Any], critic_validation: Dict[str, Any]) -> Optional[List[Any]]:
        """Improve plan based on critic feedback."""
        try:
            if hasattr(self, 'critic_agent') and self.critic_agent:
                critic_input = {
                    "action": "improve",
                    "goal": goal,
                    "plan": plan_steps,
                    "issues": critic_validation.get("issues_found", [])
                }
                improvement_response = self.critic_agent.process(critic_input)
                
                if improvement_response and improvement_response.get("success"):
                    # Apply improvements based on recommendations
                    improved_steps = self._apply_improvements(plan_steps, improvement_response.get("recommendations", []))
                    return improved_steps
            
            return None
        except Exception as e:
            self.logger.error(f"Error improving plan with critic: {e}")
            return None
    
    def _fallback_plan_validation(self, plan_steps: List[Any]) -> Dict[str, Any]:
        """Fallback plan validation when critic is not available."""
        issues = []
        recommendations = []
        
        # Basic validation
        if not plan_steps:
            issues.append("Plan is empty")
            recommendations.append("Create a plan with at least one step")
        else:
            # Check for basic structure
            for i, step in enumerate(plan_steps):
                if isinstance(step, dict):
                    if not step.get("description"):
                        issues.append(f"Step {i+1} missing description")
                    if not step.get("next_agent"):
                        issues.append(f"Step {i+1} missing next_agent")
                    if not step.get("action"):
                        issues.append(f"Step {i+1} missing action")
                else:
                    issues.append(f"Step {i+1} is not a structured object")
        
        # Calculate quality score
        plan_quality = max(0.0, 1.0 - (len(issues) * 0.2))
        
        return {
            "role": "critic",
            "action": "evaluate",
            "reasoning_level": "high",
            "plan_quality": plan_quality,
            "issues_found": issues,
            "recommendations": recommendations,
            "overall_score": plan_quality,
            "success": True
        }
    
    def _apply_improvements(self, plan_steps: List[Any], recommendations: List[str]) -> List[Any]:
        """Apply critic recommendations to improve the plan."""
        improved_steps = []
        
        for i, step in enumerate(plan_steps):
            if isinstance(step, dict):
                improved_step = step.copy()
                
                # Apply common improvements
                for rec in recommendations:
                    if "description" in rec.lower() and not improved_step.get("description"):
                        improved_step["description"] = f"Step {i+1}: {improved_step.get('action', 'unknown')}"
                    elif "next_agent" in rec.lower() and not improved_step.get("next_agent"):
                        improved_step["next_agent"] = "perception"  # Default
                    elif "action" in rec.lower() and not improved_step.get("action"):
                        improved_step["action"] = "analyze"  # Default
                
                improved_steps.append(improved_step)
            else:
                # Convert string steps to structured objects
                improved_steps.append({
                    "id": i + 1,
                    "description": str(step),
                    "next_agent": "perception",
                    "action": "analyze",
                    "success_criteria": "Step completed",
                    "priority": "medium"
                })
        
        return improved_steps
    
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
        """Create a detailed plan for achieving a goal with approval loop."""
        try:
            goal = input_data.get("goal", "Unknown goal")
            max_iterations = 3
            approval_threshold = 0.8
            iteration = 0
            consecutive_failures = 0
            
            self.logger.info(f"Starting plan creation with approval loop for goal: {goal}")
            
            while iteration < max_iterations:
                iteration += 1
                self.logger.info(f"Plan creation iteration {iteration}/{max_iterations}")
                
                # Create planning prompt
                planning_prompt = {
                    "action": "plan",
                    "goal": goal,
                    "context": "Create a detailed plan to achieve this goal. Break it down into specific, actionable steps that can be executed by perception and operator agents."
                }
                
                # Get LLM response with higher token limit for planning
                response = self._call_llm_with_planning_tokens(planning_prompt)
                
                # Canonicalize response
                response = self._canonicalize_overseer_response(response)
                
                plan_steps = response.get("plan", [])
                if not plan_steps:
                    self.logger.warning(f"Iteration {iteration}: Planner returned no steps")
                    consecutive_failures += 1
                    continue
                
                # Clean plan steps
                plan_steps = self._clean_plan_steps(plan_steps)
                
                # Enforce capabilities and insert preconditions
                plan_steps = self._enforce_capabilities_and_preconditions(plan_steps)
                
                # Update response with processed steps
                response["plan"] = plan_steps
                response["plan_quality"] = self._assess_plan_quality(plan_steps)
                
                # Validate plan with CriticAgent if available
                critic_validation = self._validate_plan_with_critic(goal, plan_steps)
                if critic_validation:
                    response["critic_validation"] = critic_validation
                    overall_score = critic_validation.get("overall_score", 0.0)
                    
                    self.logger.info(f"Iteration {iteration}: Critic score {overall_score:.2f} (threshold: {approval_threshold})")
                    
                    # Check if plan is approved
                    if overall_score >= approval_threshold:
                        self.logger.info(f"Plan approved by critic with score {overall_score:.2f}")
                        response["plan_approved"] = True
                        response["approval_iterations"] = iteration
                        consecutive_failures = 0  # Reset failure counter
                        break
                    
                    # If not approved, try to improve the plan
                    if critic_validation.get("issues_found"):
                        self.logger.info(f"Iteration {iteration}: Critic found {len(critic_validation['issues_found'])} issues, attempting to improve plan")
                        improved_plan = self._improve_plan_with_critic(goal, plan_steps, critic_validation)
                        if improved_plan:
                            response["plan"] = improved_plan
                            response["plan_improved"] = True
                            # Continue to next iteration to re-validate improved plan
                        else:
                            self.logger.warning(f"Iteration {iteration}: Failed to improve plan based on critic feedback")
                            consecutive_failures += 1
                    else:
                        consecutive_failures += 1
                else:
                    self.logger.warning(f"Iteration {iteration}: No critic validation available")
                    consecutive_failures += 1
                
                # Check for consecutive failures
                if consecutive_failures >= 3:
                    self.logger.error(f"Hit 3 consecutive failures in plan creation")
                    if self._is_debug_mode():
                        self.logger.error("Debug mode: Exiting program due to planning failures")
                        import sys
                        sys.exit(1)
                    else:
                        self.logger.warning("Non-debug mode: Starting fresh planning attempt")
                        # Reset and start over
                        iteration = 0
                        consecutive_failures = 0
                        continue
            
            # Final validation and response preparation
            if iteration >= max_iterations:
                self.logger.warning(f"Plan creation completed after {max_iterations} iterations without approval")
                response["plan_approved"] = False
                response["approval_iterations"] = iteration
            else:
                response["success"] = True
            
            # Store planning history
            self.planning_history.append({
                "goal": goal,
                "plan": response.get("plan", []),
                "critic_validation": response.get("critic_validation"),
                "approval_iterations": response.get("approval_iterations", iteration),
                "plan_approved": response.get("plan_approved", False),
                "timestamp": self._get_timestamp()
            })
            
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
            # print("- " * 100)
            # print(f"LLM response on planning: {llm_response}")
            # print("- " * 100)
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
