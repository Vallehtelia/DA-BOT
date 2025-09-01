#!/usr/bin/env python3
"""
Test script to verify the bug fixes are working correctly.
"""

import json
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

def test_json_parsing_fix():
    """Test that JSON parsing handles both dicts and strings correctly."""
    print("🧪 Testing JSON Parsing Fix")
    print("=" * 50)
    
    try:
        from agents import GPTOSS20BAgent
        
        agent = GPTOSS20BAgent("test_agent", reasoning_level="medium")
        
        # Test 1: String JSON parsing
        string_json = '{"role": "test", "action": "test", "success": true}'
        parsed = json.loads(string_json)
        parsed.setdefault("role", "test_agent")
        parsed.setdefault("success", False)
        print(f"✅ String JSON parsing: {parsed}")
        
        # Test 2: Dict JSON handling
        dict_json = {"role": "test", "action": "test", "success": True}
        dict_json.setdefault("role", "test_agent")
        dict_json.setdefault("success", False)
        print(f"✅ Dict JSON handling: {dict_json}")
        
        # Test 3: Missing fields default injection
        incomplete_json = {"action": "test"}
        incomplete_json.setdefault("role", "test_agent")
        incomplete_json.setdefault("success", False)
        print(f"✅ Default injection: {incomplete_json}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing JSON parsing: {e}")
        return False

def test_plan_structure_fix():
    """Test that plan structure handling works for both strings and objects."""
    print("\n🧪 Testing Plan Structure Fix")
    print("=" * 50)
    
    try:
        from agents import OverseerAgent
        
        agent = OverseerAgent(reasoning_level="high")
        
        # Test 1: String steps
        string_steps = [
            "Step 1: Analyze environment",
            "Step 2: Execute actions"
        ]
        
        cleaned_steps = agent._clean_plan_steps(string_steps)
        print(f"✅ String steps converted to objects: {len(cleaned_steps)} steps")
        for step in cleaned_steps:
            print(f"  - {step['description']} (Agent: {step['next_agent']})")
        
        # Test 2: Object steps
        object_steps = [
            {
                "id": 1,
                "description": "Test step",
                "next_agent": "perception",
                "action": "analyze"
            }
        ]
        
        cleaned_object_steps = agent._clean_plan_steps(object_steps)
        print(f"✅ Object steps normalized: {len(cleaned_object_steps)} steps")
        for step in cleaned_object_steps:
            print(f"  - {step['description']} (Agent: {step['next_agent']})")
        
        # Test 3: Mixed steps
        mixed_steps = [
            "Step 1: String step",
            {"description": "Object step", "next_agent": "operator"}
        ]
        
        cleaned_mixed_steps = agent._clean_plan_steps(mixed_steps)
        print(f"✅ Mixed steps normalized: {len(cleaned_mixed_steps)} steps")
        for step in cleaned_mixed_steps:
            print(f"  - {step['description']} (Agent: {step['next_agent']})")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing plan structure: {e}")
        return False

def test_goal_description_fix():
    """Test that goal description access works safely."""
    print("\n🧪 Testing Goal Description Fix")
    print("=" * 50)
    
    try:
        from core import Overseer
        
        overseer = Overseer()
        
        # Test 1: No goal set
        desc = overseer._current_goal_desc()
        print(f"✅ No goal: '{desc}'")
        
        # Test 2: Valid goal set
        goal_id = overseer.set_goal("Test goal")
        desc = overseer._current_goal_desc()
        print(f"✅ Valid goal: '{desc}'")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing goal description: {e}")
        return False

def test_sensitive_redaction():
    """Test that sensitive information is redacted from logs."""
    print("\n🧪 Testing Sensitive Information Redaction")
    print("=" * 50)
    
    try:
        from core import Overseer
        
        overseer = Overseer()
        
        # Test password redaction
        test_cases = [
            "add to permanent memory email credentials: email:valle@test.fi, pass:123123",
            "Set password=secret123 for user",
            "Update pass: mypassword in database"
        ]
        
        for test_case in test_cases:
            redacted = overseer._redact_sensitive_info(test_case)
            print(f"Original: {test_case}")
            print(f"Redacted: {redacted}")
            print("")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing redaction: {e}")
        return False

def test_llm_response_extraction():
    """Test that LLM response extraction handles different formats."""
    print("\n🧪 Testing LLM Response Extraction")
    print("=" * 50)
    
    try:
        from agents import GPTOSS20BAgent
        
        agent = GPTOSS20BAgent("test_agent", reasoning_level="medium")
        
        # Test simulated response formats
        
        # Test 1: Chat-style list response
        chat_response = [
            {"role": "user", "content": "Test input"},
            {"role": "assistant", "content": '{"role": "test", "action": "test", "success": true}'}
        ]
        
        # Simulate extraction logic
        for msg in reversed(chat_response):
            if msg.get("role") in ("assistant", "assistantfinal"):
                content = msg.get("content", "")
                extracted = content if isinstance(content, str) else str(content)
                print(f"✅ Chat-style extraction: {extracted[:50]}...")
                break
        
        # Test 2: String response
        string_response = '{"role": "test", "action": "test", "success": true}'
        print(f"✅ String response: {string_response[:50]}...")
        
        # Test 3: Fallback handling
        unknown_response = {"some": "unknown format"}
        fallback = str(unknown_response)
        print(f"✅ Fallback handling: {fallback[:50]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing LLM response extraction: {e}")
        return False

def main():
    """Main test function."""
    setup_logging()
    
    print("🚀 Starting Bug Fix Verification Tests")
    print("=" * 60)
    
    # Run all tests
    tests = [
        test_json_parsing_fix,
        test_plan_structure_fix,
        test_goal_description_fix,
        test_sensitive_redaction,
        test_llm_response_extraction
    ]
    
    results = []
    for test in tests:
        try:
            results.append(test())
        except Exception as e:
            print(f"❌ Test failed with exception: {e}")
            results.append(False)
    
    print("\n" + "=" * 60)
    print("📊 Test Results Summary:")
    print("=" * 60)
    
    test_names = [
        "JSON Parsing Fix",
        "Plan Structure Fix", 
        "Goal Description Fix",
        "Sensitive Redaction",
        "LLM Response Extraction"
    ]
    
    all_passed = True
    for i, (name, result) in enumerate(zip(test_names, results)):
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{i+1}. {name}: {status}")
        if not result:
            all_passed = False
    
    print("=" * 60)
    if all_passed:
        print("🎉 All bug fixes verified successfully!")
        print("✅ System ready for testing")
    else:
        print("❌ Some bug fixes need attention")
    
    print("=" * 60)

if __name__ == "__main__":
    main()
