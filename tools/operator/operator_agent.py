"""
Operator Agent implementation for the AI agent platform.
Handles execution of actions like mouse movements, clicks, and typing.
"""

from typing import Dict, Any, List, Tuple
from tools.agents.gpt_oss_agent import GPTOSS20BAgent

class OperatorAgent(GPTOSS20BAgent):
    """Operator agent for executing actions based on perception analysis."""
    
    def __init__(self, config_path: str = "config", reasoning_level: str = "medium"):
        super().__init__("operator", config_path, reasoning_level)
        
        # Operator-specific capabilities
        self.action_history = []
        self.execution_stats = {
            "total_actions": 0,
            "successful_actions": 0,
            "failed_actions": 0
        }
    
    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process operator-specific tasks."""
        action = input_data.get("action", "unknown")
        
        if action == "move_mouse":
            return self._move_mouse(input_data)
        elif action == "click":
            return self._click_element(input_data)
        elif action == "type":
            return self._type_text(input_data)
        elif action == "scroll":
            return self._scroll_page(input_data)
        elif action == "navigate":
            return self._navigate_interface(input_data)
        else:
            return super().process(input_data)
    
    def _move_mouse(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Move mouse to specified coordinates."""
        try:
            coordinates = input_data.get("coordinates", {})
            x = coordinates.get("x", 0)
            y = coordinates.get("y", 0)
            
            # Validate coordinates
            if not self._validate_coordinates(x, y):
                return self._create_error_response("Invalid coordinates", "move_mouse")
            
            # Create move mouse prompt
            move_prompt = {
                "action": "move_mouse",
                "coordinates": {"x": x, "y": y},
                "context": "Move the mouse cursor to the specified coordinates smoothly and accurately."
            }
            
            # Get LLM response for action planning
            response = super().process(move_prompt)
            
            if response and response.get("success"):
                # Simulate mouse movement (placeholder for real implementation)
                movement_success = self._simulate_mouse_movement(x, y)
                
                response["status"] = "success" if movement_success else "failed"
                response["coordinates"] = {"x": x, "y": y}
                response["action_executed"] = "mouse_movement"
                
                # Update execution stats
                self._update_execution_stats(movement_success)
                
                # Store action history
                self._store_action_history("move_mouse", {"x": x, "y": y}, movement_success)
            
            return response
            
        except Exception as e:
            self.logger.error(f"Error moving mouse: {e}")
            return self._create_error_response(f"Mouse movement failed: {e}", "move_mouse")
    
    def _click_element(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Click on an element at specified coordinates."""
        try:
            coordinates = input_data.get("coordinates", {})
            x = coordinates.get("x", 0)
            y = coordinates.get("y", 0)
            click_type = input_data.get("click_type", "left")
            
            # Validate coordinates
            if not self._validate_coordinates(x, y):
                return self._create_error_response("Invalid coordinates", "click")
            
            # Create click prompt
            click_prompt = {
                "action": "click",
                "coordinates": {"x": x, "y": y},
                "click_type": click_type,
                "context": f"Perform a {click_type} click at the specified coordinates."
            }
            
            # Get LLM response for action planning
            response = super().process(click_prompt)
            
            if response and response.get("success"):
                # Simulate click (placeholder for real implementation)
                click_success = self._simulate_click(x, y, click_type)
                
                response["status"] = "success" if click_success else "failed"
                response["coordinates"] = {"x": x, "y": y}
                response["click_type"] = click_type
                response["action_executed"] = "click"
                
                # Update execution stats
                self._update_execution_stats(click_success)
                
                # Store action history
                self._store_action_history("click", {"x": x, "y": y, "type": click_type}, click_success)
            
            return response
            
        except Exception as e:
            self.logger.error(f"Error clicking element: {e}")
            return self._create_error_response(f"Click failed: {e}", "click")
    
    def _type_text(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Type text into an input field."""
        try:
            text = input_data.get("text", "")
            coordinates = input_data.get("coordinates", {})
            x = coordinates.get("x", 0)
            y = coordinates.get("y", 0)
            
            if not text:
                return self._create_error_response("No text provided", "type")
            
            # Validate coordinates
            if not self._validate_coordinates(x, y):
                return self._create_error_response("Invalid coordinates", "type")
            
            # Create type prompt
            type_prompt = {
                "action": "type",
                "text": text,
                "coordinates": {"x": x, "y": y},
                "context": f"Type the text '{text}' into the input field at the specified coordinates."
            }
            
            # Get LLM response for action planning
            response = super().process(type_prompt)
            
            if response and response.get("success"):
                # Simulate typing (placeholder for real implementation)
                typing_success = self._simulate_typing(text, x, y)
                
                response["status"] = "success" if typing_success else "failed"
                response["text_typed"] = text
                response["coordinates"] = {"x": x, "y": y}
                response["action_executed"] = "typing"
                
                # Update execution stats
                self._update_execution_stats(typing_success)
                
                # Store action history
                self._store_action_history("type", {"text": text, "x": x, "y": y}, typing_success)
            
            return response
            
        except Exception as e:
            self.logger.error(f"Error typing text: {e}")
            return self._create_error_response(f"Typing failed: {e}", "type")
    
    def _scroll_page(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Scroll the page in the specified direction."""
        try:
            direction = input_data.get("direction", "down")
            amount = input_data.get("amount", 100)
            
            # Create scroll prompt
            scroll_prompt = {
                "action": "scroll",
                "direction": direction,
                "amount": amount,
                "context": f"Scroll the page {direction} by {amount} pixels."
            }
            
            # Get LLM response for action planning
            response = super().process(scroll_prompt)
            
            if response and response.get("success"):
                # Simulate scrolling (placeholder for real implementation)
                scroll_success = self._simulate_scrolling(direction, amount)
                
                response["status"] = "success" if scroll_success else "failed"
                response["direction"] = direction
                response["amount"] = amount
                response["action_executed"] = "scrolling"
                
                # Update execution stats
                self._update_execution_stats(scroll_success)
                
                # Store action history
                self._store_action_history("scroll", {"direction": direction, "amount": amount}, scroll_success)
            
            return response
            
        except Exception as e:
            self.logger.error(f"Error scrolling page: {e}")
            return self._create_error_response(f"Scrolling failed: {e}", "scroll")
    
    def _navigate_interface(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Navigate through the interface based on instructions."""
        try:
            navigation_instruction = input_data.get("instruction", "")
            current_context = input_data.get("current_context", {})
            
            # Create navigation prompt
            navigation_prompt = {
                "action": "navigate",
                "instruction": navigation_instruction,
                "current_context": current_context,
                "context": f"Navigate the interface according to the instruction: {navigation_instruction}"
            }
            
            # Get LLM response for navigation planning
            response = super().process(navigation_prompt)
            
            if response and response.get("success"):
                # Simulate navigation (placeholder for real implementation)
                navigation_success = self._simulate_navigation(navigation_instruction)
                
                response["status"] = "success" if navigation_success else "failed"
                response["instruction"] = navigation_instruction
                response["action_executed"] = "navigation"
                
                # Update execution stats
                self._update_execution_stats(navigation_success)
                
                # Store action history
                self._store_action_history("navigate", {"instruction": navigation_instruction}, navigation_success)
            
            return response
            
        except Exception as e:
            self.logger.error(f"Error navigating interface: {e}")
            return self._create_error_response(f"Navigation failed: {e}", "navigate")
    
    def _validate_coordinates(self, x: int, y: int) -> bool:
        """Validate that coordinates are within reasonable screen bounds."""
        # Assume reasonable screen bounds (adjust as needed)
        max_x = 1920
        max_y = 1080
        
        return 0 <= x <= max_x and 0 <= y <= max_y
    
    def _simulate_mouse_movement(self, x: int, y: int) -> bool:
        """Simulate mouse movement (placeholder for real implementation)."""
        # This is a placeholder - in real implementation, this would use pyautogui or similar
        self.logger.info(f"Simulating mouse movement to ({x}, {y})")
        return True
    
    def _simulate_click(self, x: int, y: int, click_type: str) -> bool:
        """Simulate mouse click (placeholder for real implementation)."""
        # This is a placeholder - in real implementation, this would use pyautogui or similar
        self.logger.info(f"Simulating {click_type} click at ({x}, {y})")
        return True
    
    def _simulate_typing(self, text: str, x: int, y: int) -> bool:
        """Simulate typing text (placeholder for real implementation)."""
        # This is a placeholder - in real implementation, this would use pyautogui or similar
        self.logger.info(f"Simulating typing '{text}' at ({x}, {y})")
        return True
    
    def _simulate_scrolling(self, direction: str, amount: int) -> bool:
        """Simulate page scrolling (placeholder for real implementation)."""
        # This is a placeholder - in real implementation, this would use pyautogui or similar
        self.logger.info(f"Simulating scroll {direction} by {amount} pixels")
        return True
    
    def _simulate_navigation(self, instruction: str) -> bool:
        """Simulate interface navigation (placeholder for real implementation)."""
        # This is a placeholder - in real implementation, this would use pyautogui or similar
        self.logger.info(f"Simulating navigation: {instruction}")
        return True
    
    def _update_execution_stats(self, success: bool):
        """Update execution statistics."""
        self.execution_stats["total_actions"] += 1
        if success:
            self.execution_stats["successful_actions"] += 1
        else:
            self.execution_stats["failed_actions"] += 1
    
    def _store_action_history(self, action_type: str, action_data: Dict[str, Any], success: bool):
        """Store action in history."""
        self.action_history.append({
            "action_type": action_type,
            "action_data": action_data,
            "success": success,
            "timestamp": self._get_timestamp()
        })
        
        # Keep only last 100 actions
        if len(self.action_history) > 100:
            self.action_history = self.action_history[-100:]
    
    def get_execution_stats(self) -> Dict[str, Any]:
        """Get current execution statistics."""
        stats = self.execution_stats.copy()
        if stats["total_actions"] > 0:
            stats["success_rate"] = stats["successful_actions"] / stats["total_actions"]
        else:
            stats["success_rate"] = 0.0
        
        return stats
    
    def get_agent_info(self) -> Dict[str, Any]:
        """Get operator-specific agent information."""
        info = super().get_agent_info()
        info.update({
            "action_history_count": len(self.action_history),
            "execution_stats": self.get_execution_stats(),
            "specialization": "action_execution_and_interface_control"
        })
        return info
