#!/usr/bin/env python3
"""Debug script to test triage generation."""

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from llm.triage_agent import generate_triage_note

def test_triage_generation():
    """Test triage note generation."""
    print("Testing triage note generation...")
    
    try:
        patient_query = "fever and headache"
        answers = {"headache_location": "severe throbbing pain in temples"}
        
        print(f"Patient query: {patient_query}")
        print(f"Answers: {answers}")
        
        note, enriched_text = generate_triage_note(patient_query, answers, top_k=4)
        
        print("✅ Triage note generated successfully!")
        print(f"Patient query: {note.patient_query}")
        print(f"Followups asked: {note.followups_asked}")
        print(f"Possible conditions: {len(note.possible_conditions)}")
        print(f"Severity: {note.severity_flags.severity}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_triage_generation()
