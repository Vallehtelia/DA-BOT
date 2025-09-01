"""
Perception Agent implementation for the AI agent platform.
Handles screenshot analysis and UI element identification.
"""

from typing import Dict, Any, List, Tuple
from tools.agents.gpt_oss_agent import GPTOSS20BAgent

class PerceptionAgent(GPTOSS20BAgent):
    """Perception agent for analyzing screenshots and identifying UI elements."""
    
    def __init__(self, config_path: str = "config", reasoning_level: str = "medium"):
        super().__init__("perception", config_path, reasoning_level)
        
        # Perception-specific capabilities
        self.analysis_history = []
        self.ui_element_patterns = {}
    
    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process perception-specific tasks."""
        action = input_data.get("action", "unknown")
        
        if action == "analyze":
            return self._analyze_screenshot(input_data)
        elif action == "identify":
            return self._identify_ui_elements(input_data)
        elif action == "coordinate":
            return self._provide_coordinates(input_data)
        else:
            return super().process(input_data)
    
    def _analyze_screenshot(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze a screenshot and provide insights."""
        try:
            # For now, we'll simulate screenshot analysis
            # In the future, this will take actual screenshots
            screenshot_info = input_data.get("screenshot_info", {})
            
            # If there's no screenshot data, return success with default continue
            if not screenshot_info:
                return self._create_success_response(
                    "analyze",
                    ui_elements=[],
                    recommended_action="continue",
                    confidence=0.5,
                    reasoning="No visual input; defaulting to continue."
                )
            
            # Create analysis prompt
            analysis_prompt = {
                "action": "analyze",
                "screenshot_info": screenshot_info,
                "context": "Analyze the current visual environment and identify what can be seen, what actions might be possible, and what the current state appears to be."
            }
            
            # Get LLM response
            response = super().process(analysis_prompt)
            
            if response and response.get("success"):
                # Simulate UI element detection
                simulated_elements = self._simulate_ui_elements(screenshot_info)
                response["ui_elements"] = simulated_elements
                response["confidence"] = 0.85  # Simulated confidence
                
                # Store analysis history
                self.analysis_history.append({
                    "screenshot_info": screenshot_info,
                    "analysis_result": response,
                    "timestamp": self._get_timestamp()
                })
            
            return response
            
        except Exception as e:
            self.logger.error(f"Error analyzing screenshot: {e}")
            return self._create_error_response(f"Screenshot analysis failed: {e}", "analyze")
    
    def _identify_ui_elements(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Identify specific UI elements in the current environment."""
        try:
            target_description = input_data.get("target_description", "")
            current_context = input_data.get("current_context", {})
            
            # Create identification prompt
            identification_prompt = {
                "action": "identify",
                "target_description": target_description,
                "current_context": current_context,
                "context": "Identify the specific UI element described in the target. Provide coordinates, element type, and recommended action."
            }
            
            # Get LLM response
            response = super().process(identification_prompt)
            
            if response and response.get("success"):
                # Enhance response with UI element details
                ui_elements = response.get("ui_elements", [])
                enhanced_elements = self._enhance_ui_elements(ui_elements, target_description)
                response["ui_elements"] = enhanced_elements
                
                # Calculate confidence based on element specificity
                response["confidence"] = self._calculate_identification_confidence(enhanced_elements)
            
            return response
            
        except Exception as e:
            self.logger.error(f"Error identifying UI elements: {e}")
            return self._create_error_response(f"UI element identification failed: {e}", "identify")
    
    def _provide_coordinates(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Provide coordinates for UI elements and actions."""
        try:
            action_needed = input_data.get("action_needed", "")
            current_state = input_data.get("current_state", {})
            
            # Create coordinate prompt
            coordinate_prompt = {
                "action": "coordinate",
                "action_needed": action_needed,
                "current_state": current_state,
                "context": "Based on the current state and required action, provide specific coordinates and action details for the operator to execute."
            }
            
            # Get LLM response
            response = super().process(coordinate_prompt)
            
            if response and response.get("success"):
                # Validate and enhance coordinates
                validated_coordinates = self._validate_coordinates(response)
                response["validated_coordinates"] = validated_coordinates
                
                # Add action recommendations
                response["action_recommendations"] = self._generate_action_recommendations(action_needed, validated_coordinates)
            
            return response
            
        except Exception as e:
            self.logger.error(f"Error providing coordinates: {e}")
            return self._create_error_response(f"Coordinate provision failed: {e}", "coordinate")
    
    def _simulate_ui_elements(self, screenshot_info: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Simulate UI element detection (placeholder for real implementation)."""
        # This is a placeholder - in real implementation, this would use computer vision
        simulated_elements = [
            {
                "type": "button",
                "text": "Submit",
                "coordinates": {"x": 500, "y": 300},
                "action": "click",
                "confidence": 0.95
            },
            {
                "type": "input",
                "text": "Enter text here",
                "coordinates": {"x": 200, "y": 200},
                "action": "type",
                "confidence": 0.90
            },
            {
                "type": "text",
                "text": "Welcome to the application",
                "coordinates": {"x": 100, "y": 50},
                "action": "read",
                "confidence": 0.98
            }
        ]
        
        return simulated_elements
    
    def _enhance_ui_elements(self, ui_elements: List[Dict[str, Any]], target_description: str) -> List[Dict[str, Any]]:
        """Enhance UI elements with additional context and validation."""
        enhanced_elements = []
        
        for element in ui_elements:
            enhanced_element = element.copy()
            
            # Add relevance score based on target description
            relevance_score = self._calculate_relevance_score(element, target_description)
            enhanced_element["relevance_score"] = relevance_score
            
            # Add action priority
            enhanced_element["action_priority"] = self._calculate_action_priority(element)
            
            # Validate coordinates
            if "coordinates" in element:
                enhanced_element["coordinates_valid"] = self._validate_coordinate_range(element["coordinates"])
            
            enhanced_elements.append(enhanced_element)
        
        # Sort by relevance and priority
        enhanced_elements.sort(key=lambda x: (x.get("relevance_score", 0), x.get("action_priority", 0)), reverse=True)
        
        return enhanced_elements
    
    def _calculate_relevance_score(self, element: Dict[str, Any], target_description: str) -> float:
        """Calculate how relevant an element is to the target description."""
        if not target_description or not element:
            return 0.0
        
        target_lower = target_description.lower()
        element_text = element.get("text", "").lower()
        element_type = element.get("type", "").lower()
        
        score = 0.0
        
        # Text similarity
        if element_text in target_lower or target_lower in element_text:
            score += 0.6
        
        # Type relevance
        if "button" in target_lower and element_type == "button":
            score += 0.3
        elif "input" in target_lower and element_type == "input":
            score += 0.3
        elif "text" in target_lower and element_type == "text":
            score += 0.2
        
        # Action relevance
        action = element.get("action", "")
        if "click" in target_lower and action == "click":
            score += 0.2
        elif "type" in target_lower and action == "type":
            score += 0.2
        
        return min(1.0, score)
    
    def _calculate_action_priority(self, element: Dict[str, Any]) -> int:
        """Calculate action priority for an element."""
        priority = 1  # Base priority
        
        # Higher priority for interactive elements
        if element.get("type") == "button":
            priority += 3
        elif element.get("type") == "input":
            priority += 2
        elif element.get("type") == "link":
            priority += 2
        
        # Higher priority for clickable actions
        if element.get("action") == "click":
            priority += 2
        elif element.get("action") == "type":
            priority += 1
        
        return priority
    
    def _validate_coordinate_range(self, coordinates: Dict[str, Any]) -> bool:
        """Validate that coordinates are within reasonable screen bounds."""
        x = coordinates.get("x", 0)
        y = coordinates.get("y", 0)
        
        # Assume reasonable screen bounds (adjust as needed)
        max_x = 1920
        max_y = 1080
        
        return 0 <= x <= max_x and 0 <= y <= max_y
    
    def _validate_coordinates(self, response: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and clean coordinates from the response."""
        validated = {}
        
        # Extract coordinates from response
        ui_elements = response.get("ui_elements", [])
        valid_elements = []
        
        for element in ui_elements:
            if "coordinates" in element and self._validate_coordinate_range(element["coordinates"]):
                valid_elements.append(element)
        
        validated["ui_elements"] = valid_elements
        validated["total_elements"] = len(valid_elements)
        validated["validation_status"] = "passed" if valid_elements else "failed"
        
        return validated
    
    def _generate_action_recommendations(self, action_needed: str, validated_coordinates: Dict[str, Any]) -> List[str]:
        """Generate action recommendations based on validated coordinates."""
        recommendations = []
        
        ui_elements = validated_coordinates.get("ui_elements", [])
        
        for element in ui_elements:
            element_type = element.get("type", "")
            element_action = element.get("action", "")
            
            if element_type == "button" and element_action == "click":
                recommendations.append(f"Click the '{element.get('text', 'button')}' at coordinates ({element['coordinates']['x']}, {element['coordinates']['y']})")
            elif element_type == "input" and element_action == "type":
                recommendations.append(f"Type into the '{element.get('text', 'input field')}' at coordinates ({element['coordinates']['x']}, {element['coordinates']['y']})")
            elif element_type == "text":
                recommendations.append(f"Read the text '{element.get('text', '')}' at coordinates ({element['coordinates']['x']}, {element['coordinates']['y']})")
        
        return recommendations
    
    def _calculate_identification_confidence(self, ui_elements: List[Dict[str, Any]]) -> float:
        """Calculate confidence in UI element identification."""
        if not ui_elements:
            return 0.0
        
        # Calculate average confidence across all elements
        total_confidence = sum(element.get("confidence", 0.5) for element in ui_elements)
        avg_confidence = total_confidence / len(ui_elements)
        
        # Boost confidence if we have multiple elements
        if len(ui_elements) > 1:
            avg_confidence = min(1.0, avg_confidence + 0.1)
        
        return avg_confidence
    
    def get_agent_info(self) -> Dict[str, Any]:
        """Get perception-specific agent information."""
        info = super().get_agent_info()
        info.update({
            "analysis_history_count": len(self.analysis_history),
            "ui_element_patterns_count": len(self.ui_element_patterns),
            "specialization": "visual_analysis_and_ui_identification"
        })
        return info
