#!/usr/bin/env python3
"""
Simple test script for LLM integration - tests one agent at a time.
"""

import logging
import sys
from pathlib import Path

# Add the project root to the path
sys.path.insert(0, str(Path(__file__).parent))

def setup_logging():
    """Setup logging for the test."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

def test_single_agent():
    """Test a single agent to avoid model reloading issues."""
    print("🧪 Testing Single GPT-OSS-20B Agent")
    print("=" * 60)
    
    try:
        from agents import GPTOSS20BAgent
        
        print("Creating agent with high reasoning level...")
        agent = GPTOSS20BAgent("test_agent", reasoning_level="high")
        
        print(f"Agent created successfully!")
        print(f"   Model: {agent.get_agent_info().get('llm_model', 'N/A')}")
        print(f"   Reasoning Level: {agent.reasoning_level}")
        print(f"   LLM Available: {agent.get_agent_info().get('llm_available', False)}")
        
        # Test basic processing
        print("\n--- Testing LLM Call ---")
        test_input = {
            "action": "test",
            "context": "This is a test to verify the LLM integration works correctly."
        }
        
        print(f"Input: {test_input}")
        print("Calling LLM (this may take a moment)...")
        
        response = agent.process(test_input)
        
        if response and response.get("success"):
            print(f"✅ Success! Response received:")
            print(f"   Role: {response.get('role', 'N/A')}")
            print(f"   Action: {response.get('action', 'N/A')}")
            print(f"   Success: {response.get('success', 'N/A')}")
            
            # Show the full response for debugging
            print(f"\nFull Response:")
            import json
            print(json.dumps(response, indent=2))
            
        else:
            print(f"❌ Failed! Response: {response}")
            if response:
                print(f"   Error: {response.get('error', 'Unknown error')}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main test function."""
    setup_logging()
    
    print("🚀 Starting Simple LLM Integration Test")
    print("=" * 60)
    
    success = test_single_agent()
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 Test completed successfully!")
        print("✅ LLM integration is working!")
    else:
        print("❌ Test failed!")
    
    print("=" * 60)

if __name__ == "__main__":
    main()
