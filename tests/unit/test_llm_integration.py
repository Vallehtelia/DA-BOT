#!/usr/bin/env python3
"""
Test script for LLM integration with the AI agent platform.
Tests the GPT-OSS-20B agents with reasoning levels.
"""

import logging
import sys
from pathlib import Path

# Add the project root to the path
sys.path.insert(0, str(Path(__file__).parent))

from agents import GPTOSS20BAgent, OverseerAgent, PerceptionAgent, OperatorAgent

def setup_logging():
    """Setup logging for the test."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

def test_gpt_oss_agent():
    """Test the base GPT-OSS-20B agent."""
    print("=" * 60)
    print("Testing GPT-OSS-20B Base Agent")
    print("=" * 60)
    
    try:
        # Test with different reasoning levels
        for reasoning_level in ["low", "medium", "high"]:
            print(f"\n--- Testing with reasoning level: {reasoning_level} ---")
            
            agent = GPTOSS20BAgent("test_agent", reasoning_level=reasoning_level)
            
            # Test basic processing
            test_input = {
                "action": "test",
                "context": "This is a test input to verify LLM integration works."
            }
            
            print(f"Input: {test_input}")
            print("Calling LLM...")
            
            response = agent.process(test_input)
            
            if response and response.get("success"):
                print(f"✅ Success! Response: {response}")
                print(f"   Role: {response.get('role', 'N/A')}")
                print(f"   Action: {response.get('action', 'N/A')}")
                print(f"   Reasoning Level: {agent.reasoning_level}")
            else:
                print(f"❌ Failed! Response: {response}")
            
            print(f"Agent Info: {agent.get_agent_info()}")
            
    except Exception as e:
        print(f"❌ Error testing GPT-OSS-20B agent: {e}")
        return False
    
    return True

def test_overseer_agent():
    """Test the overseer agent."""
    print("\n" + "=" * 60)
    print("Testing Overseer Agent")
    print("=" * 60)
    
    try:
        agent = OverseerAgent(reasoning_level="high")
        
        # Test planning
        print("\n--- Testing Planning ---")
        plan_input = {
            "action": "plan",
            "goal": "Create a new file on the desktop called 'test.txt'",
            "context": "Plan the steps needed to create a file on the desktop"
        }
        
        print(f"Input: {plan_input}")
        response = agent.process(plan_input)
        
        if response and response.get("success"):
            print(f"✅ Planning successful!")
            print(f"   Plan: {response.get('plan', [])}")
            print(f"   Plan Quality: {response.get('plan_quality', 'N/A')}")
        else:
            print(f"❌ Planning failed: {response}")
        
        # Test coordination
        print("\n--- Testing Coordination ---")
        coord_input = {
            "action": "coordinate",
            "step_description": "Step 1: Analyze current desktop environment",
            "perception_result": {"status": "success", "elements": []},
            "context": "Coordinate the next action based on perception"
        }
        
        print(f"Input: {coord_input}")
        response = agent.process(coord_input)
        
        if response and response.get("success"):
            print(f"✅ Coordination successful!")
            print(f"   Next Agent: {response.get('next_agent', 'N/A')}")
            print(f"   Action: {response.get('action', 'N/A')}")
        else:
            print(f"❌ Coordination failed: {response}")
        
        print(f"Agent Info: {agent.get_agent_info()}")
        
    except Exception as e:
        print(f"❌ Error testing Overseer agent: {e}")
        return False
    
    return True

def test_perception_agent():
    """Test the perception agent."""
    print("\n" + "=" * 60)
    print("Testing Perception Agent")
    print("=" * 60)
    
    try:
        agent = PerceptionAgent(reasoning_level="medium")
        
        # Test screenshot analysis
        print("\n--- Testing Screenshot Analysis ---")
        analysis_input = {
            "action": "analyze",
            "screenshot_info": {"window": "desktop", "timestamp": "now"},
            "context": "Analyze the current desktop environment"
        }
        
        print(f"Input: {analysis_input}")
        response = agent.process(analysis_input)
        
        if response and response.get("success"):
            print(f"✅ Analysis successful!")
            print(f"   UI Elements: {len(response.get('ui_elements', []))}")
            print(f"   Confidence: {response.get('confidence', 'N/A')}")
        else:
            print(f"❌ Analysis failed: {response}")
        
        # Test UI element identification
        print("\n--- Testing UI Element Identification ---")
        identify_input = {
            "action": "identify",
            "target_description": "Submit button",
            "current_context": {"window": "form", "elements": []},
            "context": "Identify the submit button in the current context"
        }
        
        print(f"Input: {identify_input}")
        response = agent.process(identify_input)
        
        if response and response.get("success"):
            print(f"✅ Identification successful!")
            print(f"   UI Elements: {response.get('ui_elements', [])}")
            print(f"   Confidence: {response.get('confidence', 'N/A')}")
        else:
            print(f"❌ Identification failed: {response}")
        
        print(f"Agent Info: {agent.get_agent_info()}")
        
    except Exception as e:
        print(f"❌ Error testing Perception agent: {e}")
        return False
    
    return True

def test_operator_agent():
    """Test the operator agent."""
    print("\n" + "=" * 60)
    print("Testing Operator Agent")
    print("=" * 60)
    
    try:
        agent = OperatorAgent(reasoning_level="medium")
        
        # Test mouse movement
        print("\n--- Testing Mouse Movement ---")
        move_input = {
            "action": "move_mouse",
            "coordinates": {"x": 500, "y": 300},
            "context": "Move mouse to coordinates (500, 300)"
        }
        
        print(f"Input: {move_input}")
        response = agent.process(move_input)
        
        if response and response.get("success"):
            print(f"✅ Mouse movement successful!")
            print(f"   Status: {response.get('status', 'N/A')}")
            print(f"   Action Executed: {response.get('action_executed', 'N/A')}")
        else:
            print(f"❌ Mouse movement failed: {response}")
        
        # Test clicking
        print("\n--- Testing Click ---")
        click_input = {
            "action": "click",
            "coordinates": {"x": 500, "y": 300},
            "click_type": "left",
            "context": "Click at coordinates (500, 300)"
        }
        
        print(f"Input: {click_input}")
        response = agent.process(click_input)
        
        if response and response.get("success"):
            print(f"✅ Click successful!")
            print(f"   Status: {response.get('status', 'N/A')}")
            print(f"   Click Type: {response.get('click_type', 'N/A')}")
        else:
            print(f"❌ Click failed: {response}")
        
        # Test typing
        print("\n--- Testing Typing ---")
        type_input = {
            "action": "type",
            "text": "Hello World",
            "coordinates": {"x": 200, "y": 200},
            "context": "Type 'Hello World' at coordinates (200, 200)"
        }
        
        print(f"Input: {type_input}")
        response = agent.process(type_input)
        
        if response and response.get("success"):
            print(f"✅ Typing successful!")
            print(f"   Status: {response.get('status', 'N/A')}")
            print(f"   Text Typed: {response.get('text_typed', 'N/A')}")
        else:
            print(f"❌ Typing failed: {response}")
        
        print(f"Agent Info: {agent.get_agent_info()}")
        print(f"Execution Stats: {agent.get_execution_stats()}")
        
    except Exception as e:
        print(f"❌ Error testing Operator agent: {e}")
        return False
    
    return True

def main():
    """Main test function."""
    setup_logging()
    
    print("🧪 Testing LLM Integration with GPT-OSS-20B Agents")
    print("=" * 60)
    
    # Test each agent type
    tests = [
        ("GPT-OSS-20B Base Agent", test_gpt_oss_agent),
        ("Overseer Agent", test_overseer_agent),
        ("Perception Agent", test_perception_agent),
        ("Operator Agent", test_operator_agent)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            print(f"\n🚀 Starting {test_name} test...")
            success = test_func()
            results.append((test_name, success))
        except Exception as e:
            print(f"❌ {test_name} test crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    for test_name, success in results:
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"{test_name}: {status}")
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! LLM integration is working.")
    else:
        print("⚠️  Some tests failed. Check the output above for details.")
    
    return passed == total

if __name__ == "__main__":
    main()
