#!/usr/bin/env python3
"""
Test script to demonstrate the new approval loop functionality in OverseerAgent.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from tools.overseer.overseer_agent import OverseerAgent
from tools.critic.critic_agent import CriticAgent
import json

def test_approval_loop():
    """Test the approval loop functionality."""
    print("🧪 Testing Approval Loop Functionality")
    print("=" * 50)
    
    # Initialize agents
    print("📋 Initializing agents...")
    overseer = OverseerAgent(reasoning_level="high")
    critic = CriticAgent(reasoning_level="high")
    
    # Inject critic into overseer
    overseer.critic_agent = critic
    
    print("✅ Agents initialized successfully")
    print()
    
    # Test goal
    test_goal = "check this computer's window resolution"
    print(f"🎯 Test Goal: {test_goal}")
    print()
    
    # Create plan with approval loop
    print("🔄 Starting plan creation with approval loop...")
    input_data = {
        "action": "plan",
        "goal": test_goal
    }
    
    try:
        response = overseer.process(input_data)
        
        print("📊 Plan Creation Results:")
        print(f"  Success: {response.get('success', False)}")
        print(f"  Plan Approved: {response.get('plan_approved', False)}")
        print(f"  Approval Iterations: {response.get('approval_iterations', 0)}")
        print(f"  Plan Quality: {response.get('plan_quality', 0.0):.2f}")
        
        if response.get("critic_validation"):
            cv = response["critic_validation"]
            print(f"  Critic Overall Score: {cv.get('overall_score', 0.0):.2f}")
            print(f"  Issues Found: {len(cv.get('issues_found', []))}")
            print(f"  Recommendations: {len(cv.get('recommendations', []))}")
        
        print()
        print("📋 Generated Plan:")
        plan = response.get("plan", [])
        for i, step in enumerate(plan, 1):
            print(f"  {i}. {step.get('description', 'No description')}")
            print(f"     Agent: {step.get('next_agent', 'unknown')}")
            print(f"     Action: {step.get('action', 'unknown')}")
            print(f"     Priority: {step.get('priority', 'unknown')}")
            print()
        
        print("✅ Test completed successfully!")
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_approval_loop()
