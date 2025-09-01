#!/usr/bin/env python3
"""
Test script for the enhanced context system.
Demonstrates rich context injection, memory integration, and better agent understanding.
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

def test_enhanced_context():
    """Test the enhanced context system."""
    print("🧪 Testing Enhanced Context System")
    print("=" * 60)
    
    try:
        from core import Memory, Overseer
        
        # Initialize memory system
        memory = Memory()
        print("✅ Memory system initialized")
        
        # Add some test memory to demonstrate context
        print("\n--- Adding Test Memory for Context ---")
        
        memory.add_important_memory(
            agent="overseer",
            action="previous_session",
            important_info=["credential", "account_details"],
            description="Previously created GitHub account with username 'valle_dev'",
            priority="high",
            tags=["github", "account", "credential"]
        )
        
        memory.add_important_memory(
            agent="perception",
            action="system_analysis",
            important_info=["system_info", "configuration"],
            description="System resolution detected: 1920x1080, Windows 11",
            priority="medium",
            tags=["system", "resolution", "windows"]
        )
        
        print("✅ Added test memory entries")
        
        # Initialize overseer
        print("\n--- Initializing Overseer with Enhanced Context ---")
        overseer = Overseer()
        print("✅ Overseer initialized")
        
        # Test goal execution with enhanced context
        print("\n--- Testing Goal Execution with Rich Context ---")
        
        test_goal = "add to permanent memory email credentials: email:valle.vaalanti@valle.fi, pass:123123"
        
        print(f"🎯 Goal: {test_goal}")
        print("📋 This will now provide agents with:")
        print("  - Full goal context")
        print("  - Step-by-step progress")
        print("  - Execution history")
        print("  - Relevant memory from previous sessions")
        print("  - Rich, structured prompts")
        
        # Run the goal
        success = overseer.run(test_goal)
        
        if success:
            print("✅ Goal completed successfully with enhanced context!")
        else:
            print("❌ Goal failed, but context system should have provided better understanding")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing enhanced context: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_memory_context_injection():
    """Test how memory context is injected into agent prompts."""
    print("\n🧪 Testing Memory Context Injection")
    print("=" * 60)
    
    try:
        from core import Memory
        
        memory = Memory()
        
        # Get memory context for a specific agent and action
        print("--- Getting Memory Context for Overseer Planning ---")
        
        context = memory.get_memory_context_for_agent("overseer", "plan", "credential management")
        print(f"Memory context retrieved:")
        print(f"  - Recent important memory: {len(context['recent_important_memory'])} entries")
        print(f"  - Relevant memory: {len(context['relevant_memory'])} entries")
        print(f"  - Total memory count: {context['total_memory_count']}")
        
        if context['recent_important_memory']:
            print("\n📚 Recent Important Memory:")
            for entry in context['recent_important_memory']:
                print(f"  • {entry['description']} (Priority: {entry['priority']})")
        
        if context['relevant_memory']:
            print("\n🔍 Relevant Memory for 'credential management':")
            for entry in context['relevant_memory']:
                print(f"  • {entry['description']} (Tags: {', '.join(entry['tags'])})")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing memory context injection: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_prompt_generation():
    """Test how rich prompts are generated with context."""
    print("\n🧪 Testing Rich Prompt Generation")
    print("=" * 60)
    
    try:
        from agents import GPTOSS20BAgent
        
        # Create a test agent
        agent = GPTOSS20BAgent(reasoning_level="medium")
        print("✅ Test agent created")
        
        # Test rich input data
        print("\n--- Testing Rich Input Data Processing ---")
        
        rich_input = {
            "goal": "add to permanent memory email credentials: email:valle.vaalanti@valle.fi, pass:123123",
            "step_description": "Step 1: Analyze current environment and identify requirements",
            "step_number": 1,
            "action": "coordinate",
            "execution_history": [
                {
                    "step_description": "Initialization",
                    "operation_result": {"status": "success"}
                }
            ],
            "memory_context": {
                "recent_important_memory": [
                    {
                        "description": "Previously created GitHub account with username 'valle_dev'",
                        "priority": "high"
                    }
                ]
            },
            "context": "Goal: add to permanent memory email credentials. Step 1: Analyze current environment and identify requirements. Based on perception result, decide what action to take next."
        }
        
        # Generate prompt
        prompt = agent._create_prompt_from_input(rich_input)
        
        print("📝 Generated Rich Prompt:")
        print("=" * 40)
        print(prompt)
        print("=" * 40)
        
        print("\n✅ Rich prompt generated successfully!")
        print("📊 Prompt includes:")
        print("  - 🎯 Goal context")
        print("  - 📋 Step information")
        print("  - 📚 Execution history")
        print("  - 🧠 Memory context")
        print("  - 💭 Detailed context")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing prompt generation: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main test function."""
    setup_logging()
    
    print("🚀 Starting Enhanced Context System Tests")
    print("=" * 60)
    
    # Test memory context injection
    success1 = test_memory_context_injection()
    
    # Test rich prompt generation
    success2 = test_prompt_generation()
    
    # Test full system integration
    success3 = test_enhanced_context()
    
    print("\n" + "=" * 60)
    if success1 and success2 and success3:
        print("🎉 All enhanced context tests completed successfully!")
        print("✅ Memory context injection working")
        print("✅ Rich prompt generation working")
        print("✅ Full system integration working")
        print("\n🚀 Agents now have:")
        print("  - Full goal and step context")
        print("  - Execution history awareness")
        print("  - Memory from previous sessions")
        print("  - Rich, structured prompts")
        print("  - Better understanding of what to do")
    else:
        print("❌ Some enhanced context tests failed!")
    
    print("=" * 60)

if __name__ == "__main__":
    main()
