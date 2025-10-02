#!/usr/bin/env python3
"""Test script to verify the system works."""

import os
import sys
sys.path.append('.')

def test_imports():
    """Test that all modules can be imported."""
    print("Testing imports...")
    try:
        from rag.schemas import Chunk, ChunkMeta, RetrievalHit
        from rag.retriever import create_retriever
        from llm.providers import create_llm_manager
        from llm.followup_agent import FollowupAgent
        from llm.triage_agent import TriageAgent
        print("✅ All imports successful")
        return True
    except Exception as e:
        print(f"❌ Import error: {e}")
        return False

def test_retriever():
    """Test the retriever."""
    print("\nTesting retriever...")
    try:
        from rag.retriever import create_retriever
        
        retriever = create_retriever(
            index_path="data/processed/faiss.index",
            mapping_path="data/processed/mapping.json"
        )
        
        # Test retrieval
        hits = retriever.retrieve("chest pain", top_k=3)
        print(f"✅ Retrieved {len(hits)} hits")
        for hit in hits:
            print(f"  - {hit.chunk_id}: {hit.score:.3f}")
        return True
    except Exception as e:
        print(f"❌ Retriever error: {e}")
        return False

def test_llm_manager():
    """Test LLM manager."""
    print("\nTesting LLM manager...")
    try:
        from llm.providers import create_llm_manager
        
        # Check if API key is set
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            print("⚠️  GEMINI_API_KEY not set, skipping LLM test")
            return True
        
        llm_manager = create_llm_manager(
            gemini_api_key=api_key,
            use_ollama_fallback=False
        )
        
        # Test simple generation
        response = llm_manager.generate_response("Hello, how are you?")
        print(f"✅ LLM response: {response[:50]}...")
        return True
    except Exception as e:
        print(f"❌ LLM error: {e}")
        return False

def test_agents():
    """Test the agents."""
    print("\nTesting agents...")
    try:
        from rag.retriever import create_retriever
        from llm.providers import create_llm_manager
        from llm.followup_agent import FollowupAgent
        from llm.triage_agent import TriageAgent
        
        # Check if API key is set
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            print("⚠️  GEMINI_API_KEY not set, skipping agent test")
            return True
        
        # Create retriever
        retriever = create_retriever(
            index_path="data/processed/faiss.index",
            mapping_path="data/processed/mapping.json"
        )
        
        # Create LLM manager
        llm_manager = create_llm_manager(
            gemini_api_key=api_key,
            use_ollama_fallback=False
        )
        
        # Test followup agent
        followup_agent = FollowupAgent(llm_manager)
        questions = followup_agent.generate_followups("chest pain")
        print(f"✅ Followup questions: {len(questions)}")
        
        # Test triage agent
        hits = retriever.retrieve("chest pain", top_k=3)
        triage_agent = TriageAgent(llm_manager)
        triage_note = triage_agent.generate_triage_note("chest pain", hits)
        print(f"✅ Triage note generated: {triage_note.urgency}")
        
        return True
    except Exception as e:
        print(f"❌ Agent error: {e}")
        return False

def main():
    """Run all tests."""
    print("🏥 Doctor Bot System Test")
    print("=" * 40)
    
    tests = [
        test_imports,
        test_retriever,
        test_llm_manager,
        test_agents
    ]
    
    passed = 0
    for test in tests:
        if test():
            passed += 1
    
    print(f"\n📊 Results: {passed}/{len(tests)} tests passed")
    
    if passed == len(tests):
        print("🎉 All tests passed! System is ready.")
    else:
        print("⚠️  Some tests failed. Check the errors above.")

if __name__ == "__main__":
    main()
