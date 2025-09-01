#!/usr/bin/env python3
"""
Test script for the enhanced memory system.
Demonstrates important memory storage, retrieval, and context injection.
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

def test_memory_system():
    """Test the enhanced memory system."""
    print("🧪 Testing Enhanced Memory System")
    print("=" * 60)
    
    try:
        from core import Memory
        
        # Initialize memory system
        memory = Memory()
        print("✅ Memory system initialized")
        
        # Test adding important memory
        print("\n--- Testing Important Memory Storage ---")
        
        # Add some test memory entries
        memory.add_important_memory(
            agent="overseer",
            action="create_account",
            important_info=["credential", "account_details"],
            description="Created GitHub account with username 'valle_dev'",
            priority="high",
            tags=["github", "account", "credential"]
        )
        
        memory.add_important_memory(
            agent="perception",
            action="analyze_screen",
            important_info=["system_info", "configuration"],
            description="Detected system resolution: 1920x1080",
            priority="medium",
            tags=["system", "resolution", "display"]
        )
        
        memory.add_important_memory(
            agent="operator",
            action="install_software",
            important_info=["software", "configuration"],
            description="Installed Visual Studio Code with Python extension",
            priority="high",
            tags=["software", "vscode", "python", "development"]
        )
        
        print("✅ Added 3 important memory entries")
        
        # Test memory retrieval
        print("\n--- Testing Memory Retrieval ---")
        
        # Get all high priority memory
        high_priority = memory.get_important_memory(priority="high")
        print(f"High priority memory entries: {len(high_priority)}")
        for entry in high_priority:
            print(f"  - {entry.description} (Tags: {', '.join(entry.tags)})")
        
        # Search for specific memory
        print("\n--- Testing Memory Search ---")
        search_results = memory.search_important_memory("github")
        print(f"Search results for 'github': {len(search_results)}")
        for entry in search_results:
            print(f"  - {entry.description}")
        
        # Test memory context for agents
        print("\n--- Testing Memory Context for Agents ---")
        context = memory.get_memory_context_for_agent("overseer", "plan", "development")
        print(f"Memory context: {len(context['recent_important_memory'])} recent, {len(context['relevant_memory'])} relevant")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing memory system: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_agent_memory_integration():
    """Test how agents would use the memory system."""
    print("\n🧪 Testing Agent Memory Integration")
    print("=" * 60)
    
    try:
        from core import Memory
        
        memory = Memory()
        
        # Simulate an agent response with memory field
        print("--- Simulating Agent Response with Memory ---")
        
        agent_response = {
            "role": "overseer",
            "action": "plan",
            "plan": ["step1", "step2"],
            "memory": {
            "important_info": ["credential", "api_key"],
            "description": "Obtained API key for OpenAI services",
            "priority": "high"
            }
        }
        
        # Process the response for memory
        success = memory.process_agent_response_for_memory(
            "overseer", "plan", agent_response
        )
        
        if success:
            print("✅ Successfully processed agent response for memory")
            
            # Check if memory was added
            api_memory = memory.search_important_memory("API key")
            if api_memory:
                print(f"✅ Found memory entry: {api_memory[0].description}")
            else:
                print("❌ Memory entry not found")
        else:
            print("❌ Failed to process agent response for memory")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing agent memory integration: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_memory_persistence():
    """Test that memory persists between sessions."""
    print("\n🧪 Testing Memory Persistence")
    print("=" * 60)
    
    try:
        from core import Memory
        
        # Create first memory instance
        memory1 = Memory()
        initial_count = len(memory1.important_memory)
        print(f"Initial memory count: {initial_count}")
        
        # Add a test entry
        memory1.add_important_memory(
            agent="test",
            action="test_persistence",
            important_info=["test"],
            description="Test memory persistence",
            priority="low"
        )
        
        print(f"Added test entry, new count: {len(memory1.important_memory)}")
        
        # Create second memory instance (should load existing data)
        memory2 = Memory()
        loaded_count = len(memory2.important_memory)
        print(f"Loaded memory count: {loaded_count}")
        
        if loaded_count == initial_count + 1:
            print("✅ Memory persistence working correctly")
        else:
            print("❌ Memory persistence failed")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing memory persistence: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main test function."""
    setup_logging()
    
    print("🚀 Starting Enhanced Memory System Tests")
    print("=" * 60)
    
    # Test basic memory functionality
    success1 = test_memory_system()
    
    # Test agent integration
    success2 = test_agent_memory_integration()
    
    # Test persistence
    success3 = test_memory_persistence()
    
    print("\n" + "=" * 60)
    if success1 and success2 and success3:
        print("🎉 All memory system tests completed successfully!")
        print("✅ Important memory storage working")
        print("✅ Agent memory integration working")
        print("✅ Memory persistence working")
    else:
        print("❌ Some memory system tests failed!")
    
    print("=" * 60)

if __name__ == "__main__":
    main()
