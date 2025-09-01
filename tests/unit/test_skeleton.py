#!/usr/bin/env python3
"""
Test script for the basic AI agent platform skeleton.
Demonstrates the core functionality without actual agents.
"""

import logging
import sys
from pathlib import Path

# Add the project root to the path
sys.path.insert(0, str(Path(__file__).parent))

from core import Overseer, Memory, FailsafeSystem

def setup_logging():
    """Setup logging for the test."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

def test_basic_skeleton():
    """Test the basic skeleton functionality."""
    print("=" * 60)
    print("Testing Basic AI Agent Platform Skeleton")
    print("=" * 60)
    
    # Test 1: Memory System
    print("\n1. Testing Memory System...")
    memory = Memory()
    
    # Add a test goal
    goal_id = memory.add_goal("Test goal: Navigate to a website and click a button")
    print(f"   ✓ Added goal: {goal_id}")
    
    # Create a test plan
    plan_steps = [
        "Take screenshot of current window",
        "Analyze UI elements and identify target button",
        "Move mouse to button coordinates",
        "Click the button",
        "Verify action was successful"
    ]
    plan_id = memory.create_plan(goal_id, plan_steps)
    print(f"   ✓ Created plan: {plan_id}")
    
    # Test 2: Failsafe System
    print("\n2. Testing Failsafe System...")
    failsafes = FailsafeSystem()
    
    # Check initial status
    status = failsafes.get_status_summary()
    print(f"   ✓ Failsafe status: {status['killswitch_active']}")
    print(f"   ✓ Can proceed: {failsafes.can_proceed()}")
    
    # Test 3: Overseer (without agents)
    print("\n3. Testing Overseer...")
    overseer = Overseer()
    
    # Check overseer status
    overseer_status = overseer.get_status()
    print(f"   ✓ Overseer initialized: {overseer_status['registered_agents']}")
    
    # Test 4: Control Scripts
    print("\n4. Testing Control Scripts...")
    
    # Test stop script
    import subprocess
    try:
        result = subprocess.run(['./bin/stop'], capture_output=True, text=True)
        print(f"   ✓ Stop script executed: {result.stdout.strip()}")
    except Exception as e:
        print(f"   ⚠ Stop script test: {e}")
    
    # Test pause script
    try:
        result = subprocess.run(['./bin/pause'], capture_output=True, text=True)
        print(f"   ✓ Pause script executed: {result.stdout.strip()}")
    except Exception as e:
        print(f"   ⚠ Pause script test: {e}")
    
    # Test dryrun script
    try:
        result = subprocess.run(['./bin/dryrun', 'on'], capture_output=True, text=True)
        print(f"   ✓ Dryrun script executed: {result.stdout.strip()}")
    except Exception as e:
        print(f"   ⚠ Dryrun script test: {e}")
    
    # Test 5: File Structure
    print("\n5. Testing File Structure...")
    
    required_files = [
        "config/policies.yml",
        "config/mode.json",
        "config/agent_prompts.yml",
        "core/memory.py",
        "core/failsafes.py",
        "core/base_agent.py",
        "core/overseer.py"
    ]
    
    for file_path in required_files:
        if Path(file_path).exists():
            print(f"   ✓ {file_path}")
        else:
            print(f"   ✗ {file_path} (missing)")
    
    print("\n" + "=" * 60)
    print("Basic Skeleton Test Complete!")
    print("=" * 60)
    
    # Show current system status
    print("\nCurrent System Status:")
    print(f"  - Goal: {memory.get_goal(goal_id).description if memory.get_goal(goal_id) else 'None'}")
    print(f"  - Plan: {len(plan_steps)} steps created")
    print(f"  - Failsafe: {'Active' if not failsafes.can_proceed() else 'Ready'}")
    print(f"  - Overseer: {len(overseer_status['registered_agents'])} agents registered")
    
    # Cleanup
    print("\nCleaning up...")
    try:
        # Remove control files
        for control_file in ['control/killswitch.on', 'control/pause.on']:
            if Path(control_file).exists():
                Path(control_file).unlink()
                print(f"   ✓ Removed {control_file}")
    except Exception as e:
        print(f"   ⚠ Cleanup warning: {e}")
    
    print("\nTest completed successfully!")

if __name__ == "__main__":
    setup_logging()
    test_basic_skeleton()
