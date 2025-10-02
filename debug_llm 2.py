#!/usr/bin/env python3
"""Debug script to test LLM response generation."""

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from llm.providers import get_llm_client
from llm.outputs_schemas import TriageNote

def test_llm_response():
    """Test LLM response generation."""
    print("Testing LLM response generation...")
    
    try:
        client = get_llm_client()
        print("✅ LLM client created")
        
        # Test simple response
        response = client.generate_response("Hello, please respond with 'OK'")
        print(f"Simple response: {response}")
        
        # Test structured response
        print("\nTesting structured response...")
        structured = client.generate_structured(
            system_prompt="You are a test assistant. Return a JSON object with 'test': 'success'",
            input_vars={},
            output_schema=dict
        )
        print(f"Structured response: {structured}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_llm_response()
