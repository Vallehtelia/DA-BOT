"""
GPT-OSS-20B Agent implementation for the AI agent platform.
Implements reasoning levels and proper LLM integration.
"""

import json
import logging
import time
from typing import Dict, Any, Optional, List
from pathlib import Path

from transformers import pipeline
import torch

from tools.agents.base_agent import BaseAgent

class GPTOSS20BAgent(BaseAgent):
    """GPT-OSS-20B agent with reasoning level support."""
    
    def __init__(self, agent_name: str, config_path: str = "config", reasoning_level: str = "medium"):
        super().__init__(agent_name, config_path)
        
        # Reasoning level: low, medium, high
        self.reasoning_level = reasoning_level
        
        # Initialize LLM
        self.llm = self._initialize_llm()
        
        self.logger.info(f"Initialized {agent_name} agent with reasoning level: {reasoning_level}")
    
    def _initialize_llm(self):
        """Initialize the LLM model using the shared ModelManager."""
        try:
            from tools.models import ModelManager
            
            self.logger.info("Getting GPT-OSS-20B model from ModelManager")
            
            # Get the model from the singleton manager
            model_manager = ModelManager()
            pipe = model_manager.get_gpt_oss_20b()
            
            if pipe is None:
                self.logger.error("Failed to get GPT-OSS-20B model from ModelManager")
                return None
            
            self.logger.info("GPT-OSS-20B model obtained successfully")
            return pipe
            
        except Exception as e:
            self.logger.error(f"Failed to initialize LLM: {e}")
            self.logger.warning("Agent will run in fallback mode without LLM")
            return None
    
    def _call_llm(self, prompt: str) -> Optional[str]:
        """Call the GPT-OSS-20B model."""
        return self._call_llm_with_tokens(prompt, max_new_tokens=512)
    
    def _call_llm_with_tokens(self, prompt: str, max_new_tokens: int = 512) -> Optional[str]:
        """Call the GPT-OSS-20B model with custom token limit."""
        if self.llm is None:
            return None
        
        try:
            # Format the prompt with reasoning level and system prompt
            formatted_prompt = self._format_prompt_with_reasoning(prompt)
            
            self.logger.debug(f"Calling LLM with reasoning level: {self.reasoning_level}, max_tokens: {max_new_tokens}")
            
            # Generate response using the pipeline with string prompt
            outputs = self.llm(
                formatted_prompt,   # pass a single string
                max_new_tokens=max_new_tokens,
                temperature=0.2,  # Lower temperature for planning reliability
                do_sample=True,
            )
            
            # Extract the generated text safely
            out0 = outputs[0]
            gt = out0.get("generated_text", "")
            response = gt if isinstance(gt, str) else str(gt)
            
            self.logger.debug(f"LLM response received: {len(response)} characters")
            return response
            
        except Exception as e:
            self.logger.error(f"LLM call failed: {e}")
            return None
    
    def _format_prompt_with_reasoning(self, prompt: str) -> str:
        """Format prompt with reasoning level specification."""
        reasoning_instruction = self._get_reasoning_instruction()
        
        formatted_prompt = f"""System: {self.system_prompt}

{reasoning_instruction}

User: {prompt}

IMPORTANT: Reply **only** with a single JSON object (no prose, no markdown). Put the final JSON immediately after the token `assistantfinal` on the same line. Keys must be double-quoted. Include a boolean `success` field.

Assistant:"""
        
        return formatted_prompt
    
    def _get_reasoning_instruction(self) -> str:
        """Get reasoning level instruction based on current level."""
        reasoning_instructions = {
            "low": "Reasoning: low - Provide fast, concise responses for general dialogue.",
            "medium": "Reasoning: medium - Provide balanced speed and detail with moderate analysis.",
            "high": "Reasoning: high - Provide deep, detailed analysis with thorough reasoning and step-by-step thinking."
        }
        
        return reasoning_instructions.get(self.reasoning_level, reasoning_instructions["medium"])
    
    def set_reasoning_level(self, level: str):
        """Set the reasoning level for this agent."""
        if level in ["low", "medium", "high"]:
            self.reasoning_level = level
            self.logger.info(f"Reasoning level set to: {level}")
        else:
            self.logger.warning(f"Invalid reasoning level: {level}. Using 'medium'")
            self.reasoning_level = "medium"
    
    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process input data and return response."""
        try:
            # Log the action
            self._log_action("process", input_data, {})
            
            # Create the prompt from input data
            prompt = self._create_prompt_from_input(input_data)
            
            # Get LLM response
            llm_response = self._call_llm(prompt)
            
            if llm_response is None:
                return self._create_error_response("LLM call failed", "error")
            
            # Extract JSON response
            if isinstance(llm_response, str):
                json_response = self._extract_text_from_llm_response(llm_response)
            elif isinstance(llm_response, dict) and "content" in llm_response:
                # Handle Hugging Face pipeline response format
                content = llm_response["content"]
                json_response = self._extract_text_from_llm_response(content)
            else:
                # If response is already a dict, validate it directly
                json_response = str(llm_response)
            
            # Parse JSON and add defaults BEFORE validation
            try:
                import json

                # Get default action from input data
                action_default = input_data.get("action", "unknown")

                if isinstance(json_response, dict):
                    parsed_response = json_response  # already a dict
                else:
                    parsed_response = json.loads(json_response)

                # Add defaults BEFORE validation
                parsed_response.setdefault("role", self.agent_name)
                parsed_response.setdefault("success", False)
                parsed_response.setdefault("action", action_default)

                validated_response = self._validate_json_response(parsed_response)

            except json.JSONDecodeError:
                fixed_response = self._attempt_json_fix(json_response)
                if fixed_response:
                    # Get default action from input data
                    action_default = input_data.get("action", "unknown")
                    
                    fixed_response.setdefault("role", self.agent_name)
                    fixed_response.setdefault("success", False)
                    fixed_response.setdefault("action", action_default)
                    validated_response = self._validate_json_response(fixed_response)
                else:
                    return self._create_error_response("Invalid JSON response from LLM", "error")
            
            if validated_response is None:
                return self._create_error_response("Response validation failed", "error")
            
            # Debug mode: print sanitized prompts and raw responses
            if self._is_debug_mode():
                try:
                    from tools.utils.redact import safe_redact
                except Exception:
                    def safe_redact(x): 
                        return str(x) if x is not None else ""
                self.logger.info("=== DEBUG MODE ===")
                sp = safe_redact(prompt)
                self.logger.info(f"Sanitized prompt (length: {len(sp)}): {sp[:200]}...")
                self.logger.info(f"Raw LLM response: {safe_redact(llm_response)}")
                self.logger.info(f"Extracted JSON: {safe_redact(json_response)}")
                self.logger.info(f"Validated response: {safe_redact(validated_response)}")
                self.logger.info("==================")
            
            # Process memory if present in response
            if hasattr(self, 'memory') and self.memory:
                self.memory.process_agent_response_for_memory(
                    self.agent_name, 
                    "process", 
                    validated_response
                )
            
            # Log successful response
            self._log_action("process", input_data, validated_response)
            
            return validated_response
            
        except Exception as e:
            self.logger.error(f"Error processing input: {e}")
            return self._create_error_response(f"Processing error: {e}", "error")
    
    def _create_prompt_from_input(self, input_data: Dict[str, Any]) -> str:
        """Create a prompt from input data with rich context."""
        # Convert input data to a structured prompt
        prompt_parts = []
        
        # Add goal context
        if "goal" in input_data:
            prompt_parts.append(f"GOAL: {input_data['goal']}")
        
        # Add step context
        if "step_description" in input_data:
            step_num = input_data.get("step_number", "?")
            prompt_parts.append(f"STEP {step_num}: {input_data['step_description']}")
        
        # Add action context
        if "action" in input_data:
            prompt_parts.append(f"ACTION REQUIRED: {input_data['action']}")
        
        # Add execution history context
        if "execution_history" in input_data and input_data["execution_history"]:
            prompt_parts.append("RECENT EXECUTION HISTORY:")
            for i, step in enumerate(input_data["execution_history"][-3:], 1):
                step_desc = step.get("step_description", "Unknown step")
                step_status = step.get("operation_result", {}).get("status", "unknown")
                prompt_parts.append(f"  {i}. {step_desc} → {step_status}")
        
        # Add perception result context
        if "perception_result" in input_data:
            prompt_parts.append("PERCEPTION RESULT:")
            perception = input_data["perception_result"]
            if isinstance(perception, dict):
                for key, value in perception.items():
                    if key != "elements":  # Skip long element lists
                        prompt_parts.append(f"  {key}: {value}")
        
        # Add action plan context
        if "action_plan" in input_data:
            prompt_parts.append("ACTION PLAN:")
            action_plan = input_data["action_plan"]
            if isinstance(action_plan, dict):
                for key, value in action_plan.items():
                    prompt_parts.append(f"  {key}: {value}")
        
        # Add memory context
        if "memory_context" in input_data:
            memory_context = input_data["memory_context"]
            if memory_context.get("recent_important_memory"):
                prompt_parts.append("RELEVANT MEMORY:")
                for entry in memory_context["recent_important_memory"][:3]:
                    prompt_parts.append(f"  • {entry['description']} (Priority: {entry['priority']})")
        
        # Add general context
        if "context" in input_data:
            prompt_parts.append(f"CONTEXT: {input_data['context']}")
        
        # Add the base prompt
        if prompt_parts:
            prompt = "\n\n".join(prompt_parts)
        else:
            prompt = str(input_data)
        
        # Ensure JSON format is requested
        prompt = self._ensure_json_format(prompt)
        
        return prompt
    
    def _extract_first_json_block(self, text: str) -> Optional[str]:
        """Extract the first balanced JSON block from text."""
        if not isinstance(text, str):
            return None
        start = text.find('{')
        if start == -1:
            return None
        depth = 0
        for i in range(start, len(text)):
            c = text[i]
            if c == '{':
                depth += 1
            elif c == '}':
                depth -= 1
                if depth == 0:
                    return text[start:i+1]
        return None

    def _attempt_json_fix(self, response: str) -> Optional[Dict[str, Any]]:
        """Attempt to fix common JSON formatting issues using balanced-brace extraction."""
        try:
            # First try balanced-brace extraction
            block = self._extract_first_json_block(response)
            if block:
                import json
                return json.loads(block)
            
            # Fallback: fenced code blocks
            if "```json" in response:
                start = response.find("```json") + 7
                end = response.find("```", start)
                if end != -1:
                    return json.loads(response[start:end].strip())
            
            # Fallback: code blocks without language
            if "```" in response:
                start = response.find("```") + 3
                end = response.find("```", start)
                if end != -1:
                    json_str = response[start:end].strip()
                    if json_str.startswith("{") and json_str.endswith("}"):
                        return json.loads(json_str)
            
            # Fallback: after assistantfinal token
            if "assistantfinal" in response:
                start = response.find("assistantfinal") + len("assistantfinal")
                json_str = response[start:].strip()
                if json_str.startswith("{") and json_str.endswith("}"):
                    return json.loads(json_str)
            
            return None
            
        except Exception as e:
            self.logger.debug(f"JSON fix attempt failed: {e}")
            return None
    
    def get_agent_info(self) -> Dict[str, Any]:
        """Get information about this agent."""
        info = super().get_agent_info()
        info.update({
            "llm_model": "GPT-OSS-20B",
            "reasoning_level": self.reasoning_level,
            "llm_available": self.llm is not None
        })
        return info
    
    def _get_capabilities(self) -> List[str]:
        """Get list of agent capabilities."""
        capabilities = super()._get_capabilities()
        capabilities.extend([
            "llm_integration",
            "reasoning_levels",
            "json_validation",
            "prompt_formatting"
        ])
        return capabilities
    
    def _is_debug_mode(self) -> bool:
        """Check if debug mode is enabled."""
        try:
            from pathlib import Path
            import json
            mode_file = Path("config/mode.json")
            if mode_file.exists():
                with open(mode_file, 'r') as f:
                    mode_config = json.load(f)
                return mode_config.get("debug_mode", False)
        except Exception:
            pass
        return False
