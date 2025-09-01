"""
Base agent class for the AI agent platform.
Provides common functionality for all agents.
"""

import json
import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List, Union
from pathlib import Path
import yaml

class BaseAgent(ABC):
    """Base class for all agents in the platform."""
    
    def __init__(self, agent_name: str, config_path: str = "config"):
        self.agent_name = agent_name
        self.config_path = Path(config_path)
        self.logger = logging.getLogger(f"agent.{agent_name}")
        
        # Load agent prompts
        self.prompts = self._load_prompts()
        self.system_prompt = self.prompts.get(agent_name, {}).get("system_prompt", "")
        
        # Initialize LLM (to be implemented by subclasses)
        self.llm = None
        
        self.logger.info(f"Initialized {agent_name} agent")
    
    def _load_prompts(self) -> Dict[str, Any]:
        """Load agent prompts from configuration file."""
        prompts_file = self.config_path / "agent_prompts.yml"
        if prompts_file.exists():
            try:
                with open(prompts_file, 'r') as f:
                    return yaml.safe_load(f)
            except Exception as e:
                self.logger.warning(f"Failed to load prompts: {e}")
        
        return {}
    
    @abstractmethod
    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process input data and return response. Must be implemented by subclasses."""
        pass
    
    def _validate_json_response(self, response) -> Optional[Dict[str, Any]]:
        """Validate and parse JSON response; accepts str or dict."""
        try:
            import json
            if isinstance(response, str):
                parsed = json.loads(response)
            elif isinstance(response, dict):
                parsed = response
            else:
                self.logger.error(f"Invalid response type for JSON validation: {type(response)}")
                return None

            if "role" not in parsed:
                self.logger.error("Response missing 'role' field")
                return None
            if "action" not in parsed:
                self.logger.error("Response missing 'action' field")
                return None

            return parsed
        except Exception as e:
            self.logger.error(f"Invalid JSON response: {e}")
            self.logger.error(f"Raw response: {response}")
            return None
    
    def _create_error_response(self, error_message: str, action: str = "error") -> Dict[str, Any]:
        """Create a standardized error response."""
        return {
            "role": self.agent_name,
            "action": action,
            "error": error_message,
            "success": False,
            "timestamp": self._get_timestamp()
        }
    
    def _create_success_response(self, action: str, **kwargs) -> Dict[str, Any]:
        """Create a standardized success response."""
        response = {
            "role": self.agent_name,
            "action": action,
            "success": True,
            "timestamp": self._get_timestamp()
        }
        response.update(kwargs)
        return response
    
    def _get_timestamp(self) -> float:
        """Get current timestamp."""
        import time
        return time.time()
    
    def _log_action(self, action: str, input_data: Dict[str, Any], output_data: Dict[str, Any]):
        """Log agent action for debugging and audit."""
        self.logger.info(f"Action: {action}")
        self.logger.debug(f"Input: {input_data}")
        self.logger.debug(f"Output: {output_data}")
    
    def _extract_text_from_llm_response(self, response: str) -> str:
        """Return the last valid JSON object from an LLM response, or the stripped response if none found."""
        import re, json

        def _scan_last_valid_json_obj(text: str) -> str | None:
            in_str = False
            esc = False
            brace = 0
            start = None
            last_valid = None

            for i, ch in enumerate(text):
                if esc:
                    esc = False
                    continue
                if ch == '\\':
                    esc = in_str
                    continue
                if ch == '"':
                    in_str = not in_str
                    continue
                if in_str:
                    continue

                if ch == '{':
                    if brace == 0:
                        start = i
                    brace += 1
                elif ch == '}':
                    if brace > 0:
                        brace -= 1
                        if brace == 0 and start is not None:
                            candidate = text[start:i+1].strip()
                            try:
                                json.loads(candidate)
                                last_valid = candidate  # keep scanning to prefer the last one
                            except Exception:
                                pass
            return last_valid

        # Prefer the segment after 'assistantfinal' if present
        segment = response
        if "assistantfinal" in response:
            segment = response.split("assistantfinal", 1)[1]
            # Remove any leading whitespace or newlines
            segment = segment.lstrip()

        # Try code blocks (prefer the last one), then the chosen segment, then the full response
        code_blocks = re.findall(r"```(?:json)?\s*([\s\S]*?)\s*```", segment, flags=re.IGNORECASE)
        search_order = []
        if code_blocks:
            search_order.append(code_blocks[-1])
        search_order.append(segment)
        if segment is not response:
            search_order.append(response)

        for text in search_order:
            found = _scan_last_valid_json_obj(text)
            if found:
                return found

        return response.strip()
    
    def _ensure_json_format(self, prompt: Union[str, dict]) -> str:
        """Ensure the prompt requests JSON format."""
        if not isinstance(prompt, str):
            try:
                prompt = json.dumps(prompt, ensure_ascii=False)
            except Exception:
                prompt = str(prompt)
        low = prompt.lower()
        if ("valid json only" not in low) and ("respond with valid json" not in low):
            prompt += "\n\nIMPORTANT: You must respond with valid JSON only. Do not include any other text, markdown, or formatting. Your response must start with { and end with }."
        return prompt
    
    def _add_context_to_prompt(self, base_prompt: str, context: Dict[str, Any]) -> str:
        """Add context information to a prompt."""
        if not context:
            return base_prompt
        
        context_str = "\n\nContext:\n"
        for key, value in context.items():
            if isinstance(value, dict):
                context_str += f"{key}: {json.dumps(value, indent=2)}\n"
            else:
                context_str += f"{key}: {value}\n"
        
        return base_prompt + context_str
    
    def _add_memory_context_to_prompt(self, base_prompt: str, memory_context: Dict[str, Any] = None) -> str:
        """Add memory context to a prompt if available."""
        if not memory_context:
            return base_prompt
        
        memory_str = "\n\nRelevant Memory:\n"
        
        # Add recent important memory
        if memory_context.get("recent_important_memory"):
            memory_str += "Recent Important Information:\n"
            for entry in memory_context["recent_important_memory"]:
                memory_str += f"- {entry['description']} (Priority: {entry['priority']})\n"
        
        # Add relevant memory for current task
        if memory_context.get("relevant_memory"):
            memory_str += "\nRelevant Information for Current Task:\n"
            for entry in memory_context["relevant_memory"]:
                memory_str += f"- {entry['description']} (Tags: {', '.join(entry['tags'])})\n"
        
        return base_prompt + memory_str
    
    def _retry_llm_call(self, prompt: str, max_retries: int = 3) -> Optional[str]:
        """Retry LLM call with exponential backoff."""
        import time
        
        for attempt in range(max_retries):
            try:
                if self.llm is None:
                    raise Exception("LLM not initialized")
                
                # This will be implemented by subclasses
                response = self._call_llm(prompt)
                if response:
                    return response
                    
            except Exception as e:
                self.logger.warning(f"LLM call attempt {attempt + 1} failed: {e}")
                if attempt < max_retries - 1:
                    wait_time = 2 ** attempt
                    self.logger.info(f"Waiting {wait_time}s before retry...")
                    time.sleep(wait_time)
        
        self.logger.error(f"All {max_retries} LLM call attempts failed")
        return None
    
    def _call_llm(self, prompt: str) -> Optional[str]:
        """Call the LLM. Must be implemented by subclasses."""
        raise NotImplementedError("Subclasses must implement _call_llm")
    
    def get_agent_info(self) -> Dict[str, Any]:
        """Get information about this agent."""
        return {
            "name": self.agent_name,
            "type": self.__class__.__name__,
            "system_prompt": self.system_prompt[:100] + "..." if len(self.system_prompt) > 100 else self.system_prompt,
            "capabilities": self._get_capabilities()
        }
    
    def _get_capabilities(self) -> List[str]:
        """Get list of agent capabilities. Can be overridden by subclasses."""
        return ["process", "validate_json", "error_handling"]
    

