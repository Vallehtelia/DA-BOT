"""
Critic Agent implementation for the AI agent platform.
Handles plan validation, quality assessment, and improvement suggestions.
"""

from typing import Dict, Any, List
from tools.agents.gpt_oss_agent import GPTOSS20BAgent

class CriticAgent(GPTOSS20BAgent):
    """Critic agent for plan validation and quality assessment."""
    
    def __init__(self, config_path: str = "config", reasoning_level: str = "high"):
        super().__init__("critic", config_path, reasoning_level)
        
        # Critic-specific capabilities
        self.validation_history = []
        self.quality_metrics = {}
    
    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process critic-specific tasks."""
        action = input_data.get("action", "unknown")
        
        if action == "evaluate":
            return self._evaluate_plan(input_data)
        elif action == "feedback":
            return self._provide_feedback(input_data)
        elif action == "improve":
            return self._suggest_improvements(input_data)
        else:
            return super().process(input_data)
    
    def _evaluate_plan(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate plan quality and completeness."""
        try:
            plan = input_data.get("plan", [])
            goal = input_data.get("goal", "Unknown goal")
            
            # Create evaluation prompt
            evaluation_prompt = {
                "action": "evaluate",
                "goal": goal,
                "plan": plan,
                "context": "Evaluate the plan quality, completeness, and feasibility. Check for missing preconditions, unclear steps, and capability mismatches."
            }
            
            # Get LLM response
            response = self._call_llm_with_planning_tokens(evaluation_prompt)
            
            if response:
                # Validate response structure
                validated_response = self._validate_critic_response(response)
                
                if validated_response:
                    # Store validation history
                    self.validation_history.append({
                        "goal": goal,
                        "plan": plan,
                        "evaluation": validated_response,
                        "timestamp": self._get_timestamp()
                    })
                    
                    return validated_response
            
            # Fallback evaluation
            return self._create_fallback_evaluation(plan, goal)
            
        except Exception as e:
            self.logger.error(f"Error evaluating plan: {e}")
            return self._create_error_response(f"Plan evaluation failed: {e}", "evaluate")
    
    def _provide_feedback(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Provide detailed feedback on plan issues."""
        try:
            plan = input_data.get("plan", [])
            issues = input_data.get("issues", [])
            
            # Create feedback prompt
            feedback_prompt = {
                "action": "feedback",
                "plan": plan,
                "issues": issues,
                "context": "Provide detailed feedback on the identified issues and suggest specific improvements."
            }
            
            # Get LLM response
            response = self._call_llm_with_planning_tokens(feedback_prompt)
            
            if response:
                validated_response = self._validate_critic_response(response)
                if validated_response:
                    return validated_response
            
            # Fallback feedback
            return self._create_fallback_feedback(plan, issues)
            
        except Exception as e:
            self.logger.error(f"Error providing feedback: {e}")
            return self._create_error_response(f"Feedback generation failed: {e}", "feedback")
    
    def _suggest_improvements(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Suggest specific improvements to the plan."""
        try:
            plan = input_data.get("plan", [])
            goal = input_data.get("goal", "Unknown goal")
            
            # Create improvement prompt
            improvement_prompt = {
                "action": "improve",
                "goal": goal,
                "plan": plan,
                "context": "Suggest specific improvements to make the plan more robust, complete, and executable."
            }
            
            # Get LLM response
            response = self._call_llm_with_planning_tokens(improvement_prompt)
            
            if response:
                validated_response = self._validate_critic_response(response)
                if validated_response:
                    return validated_response
            
            # Fallback improvements
            return self._create_fallback_improvements(plan, goal)
            
        except Exception as e:
            self.logger.error(f"Error suggesting improvements: {e}")
            return self._create_error_response(f"Improvement suggestions failed: {e}", "improve")
    
    def _validate_critic_response(self, response: Dict[str, Any]) -> Dict[str, Any]:
        """Validate critic response structure."""
        if not isinstance(response, dict):
            return None
        
        # Ensure required fields
        response.setdefault("role", "critic")
        response.setdefault("action", "evaluate")
        response.setdefault("success", False)
        response.setdefault("reasoning_level", "high")
        response.setdefault("plan_quality", 0.0)
        response.setdefault("issues_found", [])
        response.setdefault("recommendations", [])
        response.setdefault("overall_score", 0.0)
        
        # Validate types
        if not isinstance(response.get("plan_quality"), (int, float)):
            response["plan_quality"] = 0.0
        if not isinstance(response.get("issues_found"), list):
            response["issues_found"] = []
        if not isinstance(response.get("recommendations"), list):
            response["recommendations"] = []
        if not isinstance(response.get("overall_score"), (int, float)):
            response["overall_score"] = 0.0
        
        return response
    
    def _create_fallback_evaluation(self, plan: List[Any], goal: str) -> Dict[str, Any]:
        """Create fallback evaluation when LLM fails."""
        issues = []
        recommendations = []
        
        # Basic validation
        if not plan:
            issues.append("Plan is empty")
            recommendations.append("Create a plan with at least one step")
        else:
            # Check for basic structure
            for i, step in enumerate(plan):
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
        overall_score = plan_quality
        
        return {
            "role": "critic",
            "action": "evaluate",
            "reasoning_level": "high",
            "plan_quality": plan_quality,
            "issues_found": issues,
            "recommendations": recommendations,
            "overall_score": overall_score,
            "success": True
        }
    
    def _create_fallback_feedback(self, plan: List[Any], issues: List[str]) -> Dict[str, Any]:
        """Create fallback feedback when LLM fails."""
        recommendations = []
        
        for issue in issues:
            if "missing description" in issue:
                recommendations.append("Add clear, actionable descriptions to all steps")
            elif "missing next_agent" in issue:
                recommendations.append("Specify which agent should execute each step")
            elif "missing action" in issue:
                recommendations.append("Define specific actions for each step")
            elif "not a structured object" in issue:
                recommendations.append("Convert string steps to structured objects with required fields")
        
        return {
            "role": "critic",
            "action": "feedback",
            "reasoning_level": "high",
            "plan_quality": 0.5,
            "issues_found": issues,
            "recommendations": recommendations,
            "overall_score": 0.5,
            "success": True
        }
    
    def _create_fallback_improvements(self, plan: List[Any], goal: str) -> Dict[str, Any]:
        """Create fallback improvements when LLM fails."""
        recommendations = [
            "Ensure each step has a clear description",
            "Specify the correct agent for each step",
            "Include success criteria for each step",
            "Add coordinate identification steps before operator actions",
            "Break down complex steps into smaller micro-steps"
        ]
        
        return {
            "role": "critic",
            "action": "improve",
            "reasoning_level": "high",
            "plan_quality": 0.6,
            "issues_found": ["Generic plan structure issues"],
            "recommendations": recommendations,
            "overall_score": 0.6,
            "success": True
        }
    
    def _call_llm_with_planning_tokens(self, prompt: str) -> Dict[str, Any]:
        """Call LLM with higher token limit for planning tasks."""
        try:
            # Create the prompt from input data
            if isinstance(prompt, dict):
                formatted_prompt = self._create_prompt_from_input(prompt)
            else:
                formatted_prompt = prompt
            
            # Ensure JSON format is requested
            formatted_prompt = self._ensure_json_format(formatted_prompt)
            
            # Call LLM with higher token limit
            llm_response = self._call_llm_with_tokens(formatted_prompt, max_new_tokens=1024)
            
            if llm_response is None:
                return None
            
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
                    parsed_response = json_response
                else:
                    parsed_response = json.loads(json_response)
                
                # Add defaults BEFORE validation
                parsed_response.setdefault("role", self.agent_name)
                parsed_response.setdefault("success", False)
                parsed_response.setdefault("action", "evaluate")
                
                validated_response = self._validate_json_response(parsed_response)
                
            except json.JSONDecodeError:
                fixed_response = self._attempt_json_fix(json_response)
                if fixed_response:
                    fixed_response.setdefault("role", self.agent_name)
                    fixed_response.setdefault("success", False)
                    fixed_response.setdefault("action", "evaluate")
                    validated_response = self._validate_json_response(fixed_response)
                else:
                    return None
            
            return validated_response
            
        except Exception as e:
            self.logger.error(f"Error in planning LLM call: {e}")
            return None
    
    def _get_timestamp(self) -> str:
        """Get current timestamp."""
        import time
        return time.strftime("%Y-%m-%d %H:%M:%S")
    
    def get_agent_info(self) -> Dict[str, Any]:
        """Get information about this agent."""
        info = super().get_agent_info()
        info.update({
            "validation_history_count": len(self.validation_history),
            "quality_metrics": self.quality_metrics
        })
        return info
