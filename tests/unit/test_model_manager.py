#!/usr/bin/env python3
"""
Test script for ModelManager singleton and shared model usage.
Tests all agent types without reloading the model multiple times.
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

def test_model_manager():
    """Test the ModelManager singleton."""
    print("🧪 Testing ModelManager Singleton")
    print("=" * 60)
    
    try:
        from core import ModelManager
        
        # Test singleton behavior
        manager1 = ModelManager()
        manager2 = ModelManager()
        
        if manager1 is manager2:
            print("✅ Singleton pattern working correctly")
        else:
            print("❌ Singleton pattern failed")
            return False
        
        # Test memory usage before loading
        memory_before = manager1.get_memory_usage()
        print(f"Memory before loading: {memory_before}")
        
        # Load the model
        print("\n--- Loading GPT-OSS-20B Model ---")
        model = manager1.get_gpt_oss_20b()
        
        if model is None:
            print("❌ Failed to load model")
            return False
        
        print("✅ Model loaded successfully")
        
        # Test memory usage after loading
        memory_after = manager1.get_memory_usage()
        print(f"Memory after loading: {memory_after}")
        
        # Test that the same model is returned
        model2 = manager1.get_gpt_oss_20b()
        if model is model2:
            print("✅ Same model instance returned (cached)")
        else:
            print("❌ Different model instance returned")
            return False
        
        # Test loaded models list
        loaded_models = manager1.get_loaded_models()
        print(f"Loaded models: {loaded_models}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing ModelManager: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_agents_with_shared_model():
    """Test all agent types using the shared model."""
    print("\n🧪 Testing Agents with Shared Model")
    print("=" * 60)
    
    try:
        from agents import GPTOSS20BAgent, OverseerAgent, PerceptionAgent, OperatorAgent
        from core import ModelManager
        
        # Get the shared model manager
        model_manager = ModelManager()
        
        # Test base agent
        print("\n--- Testing GPTOSS20BAgent ---")
        base_agent = GPTOSS20BAgent("test_base", reasoning_level="low")
        if base_agent.llm is not None:
            print("✅ Base agent initialized with shared model")
        else:
            print("❌ Base agent failed to get shared model")
            return False
        
        # Test overseer agent
        print("\n--- Testing OverseerAgent ---")
        overseer_agent = OverseerAgent("test_overseer", reasoning_level="medium")
        if overseer_agent.llm is not None:
            print("✅ Overseer agent initialized with shared model")
        else:
            print("❌ Overseer agent failed to get shared model")
            return False
        
        # Test perception agent
        print("\n--- Testing PerceptionAgent ---")
        perception_agent = PerceptionAgent("test_perception", reasoning_level="medium")
        if perception_agent.llm is not None:
            print("✅ Perception agent initialized with shared model")
        else:
            print("❌ Perception agent failed to get shared model")
            return False
        
        # Test operator agent
        print("\n--- Testing OperatorAgent ---")
        operator_agent = OperatorAgent("test_operator", reasoning_level="low")
        if operator_agent.llm is not None:
            print("✅ Operator agent initialized with shared model")
        else:
            print("❌ Operator agent failed to get shared model")
            return False
        
        # Verify all agents are using the same model instance
        model_instances = [
            base_agent.llm,
            overseer_agent.llm,
            perception_agent.llm,
            operator_agent.llm
        ]
        
        if all(model is model_instances[0] for model in model_instances):
            print("✅ All agents are using the same model instance")
        else:
            print("❌ Agents are using different model instances")
            return False
        
        # Test a simple LLM call
        print("\n--- Testing LLM Call with Shared Model ---")
        test_input = {"action": "test", "context": "Testing shared model functionality"}
        
        response = base_agent.process(test_input)
        if response and response.get("success"):
            print("✅ LLM call successful with shared model")
            print(f"   Response: {response}")
        else:
            print("❌ LLM call failed")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing agents with shared model: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_memory_usage():
    """Test memory usage monitoring."""
    print("\n🧪 Testing Memory Usage Monitoring")
    print("=" * 60)
    
    try:
        from core import ModelManager
        
        manager = ModelManager()
        memory_info = manager.get_memory_usage()
        
        print(f"Current memory usage:")
        for key, value in memory_info.items():
            if isinstance(value, float):
                print(f"   {key}: {value:.2f} GB")
            else:
                print(f"   {key}: {value}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing memory usage: {e}")
        return False

def main():
    """Main test function."""
    setup_logging()
    
    print("🚀 Starting ModelManager and Shared Model Tests")
    print("=" * 60)
    
    # Test ModelManager singleton
    success1 = test_model_manager()
    
    # Test agents with shared model
    success2 = test_agents_with_shared_model()
    
    # Test memory usage
    success3 = test_memory_usage()
    
    print("\n" + "=" * 60)
    if success1 and success2 and success3:
        print("🎉 All tests completed successfully!")
        print("✅ ModelManager singleton working")
        print("✅ Shared model across agents working")
        print("✅ Memory usage monitoring working")
    else:
        print("❌ Some tests failed!")
    
    print("=" * 60)

if __name__ == "__main__":
    main()
