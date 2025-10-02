#!/usr/bin/env python3
"""
Example script demonstrating the LLM-as-Judge implementation
without requiring the full Streamlit UI.
"""

import requests
import json
import time

API_BASE_URL = "http://127.0.0.1:8000"

def demo_triage_process():
    """Demonstrate the complete triage process with judge evaluation."""
    
    print("🏥 Doctor Bot LLM-as-Judge Demo")
    print("=" * 50)
    
    # Step 1: Initial query
    patient_query = "fever 3 days, chills, cough, poor appetite"
    print(f"\n📝 Patient Query: {patient_query}")
    
    # Call API for follow-up questions
    print("\n🔍 Step 1: Generating follow-up questions...")
    response = requests.post(f"{API_BASE_URL}/triage", json={
        "query": patient_query,
        "top_k": 8
    })
    
    if response.status_code != 200:
        print(f"❌ API Error: {response.status_code}")
        print(response.text)
        return
    
    data = response.json()
    
    if data.get("next_action") != "ask_followups":
        print("❌ Unexpected response")
        return
    
    questions = data.get("followup_questions", [])
    print(f"✅ Generated {len(questions)} follow-up questions:")
    
    for i, q in enumerate(questions, 1):
        print(f"  {i}. {q.get('text', 'N/A')}")
    
    # Simulate answers
    print("\n📋 Step 2: Simulating patient answers...")
    answers = {
        "How long have you been experiencing these symptoms?": "3 days",
        "What is your current temperature?": "102°F",
        "Do you have any shortness of breath?": "No",
        "Are you experiencing any chest pain?": "No",
        "Have you tried any medications?": "Tylenol, no relief"
    }
    
    print("Simulated answers:")
    for q, a in answers.items():
        print(f"  Q: {q}")
        print(f"  A: {a}")
    
    # Call API with answers
    print("\n🔬 Step 3: Generating triage note with judge evaluation...")
    triage_response = requests.post(f"{API_BASE_URL}/triage", json={
        "query": patient_query,
        "followup_answers": answers,
        "top_k": 8
    })
    
    if triage_response.status_code != 200:
        print(f"❌ API Error: {triage_response.status_code}")
        print(triage_response.text)
        return
    
    triage_data = triage_response.json()
    
    if triage_data.get("next_action") != "return_triage":
        print("❌ Unexpected response")
        return
    
    # Display results
    print("\n📊 Step 4: Results")
    print("=" * 30)
    
    # Triage note
    triage_note = triage_data.get("triage_note", {})
    print(f"\n📋 Triage Note Generated")
    print(f"Patient Query: {triage_note.get('patient_query', 'N/A')}")
    
    # Possible conditions
    conditions = triage_note.get("possible_conditions", [])
    if conditions:
        print(f"\n🔬 Possible Conditions ({len(conditions)}):")
        for i, cond in enumerate(conditions, 1):
            print(f"  {i}. {cond.get('name', 'Unknown')}")
            print(f"     Rationale: {cond.get('rationale', 'N/A')}")
            print(f"     Source: {cond.get('source', 'N/A')}")
            support_chunks = cond.get('support_chunk_ids', [])
            if support_chunks:
                print(f"     Supporting Chunks: {', '.join(support_chunks)}")
    
    # Severity assessment
    severity = triage_note.get("severity_flags", {})
    if severity:
        print(f"\n🚨 Severity Assessment:")
        print(f"  Level: {severity.get('severity', 'N/A')}")
        print(f"  Source: {severity.get('source', 'N/A')}")
        red_flags = severity.get('red_flags', [])
        if red_flags:
            print(f"  Red Flags: {', '.join(red_flags)}")
    
    # Judge verdict
    verdict = triage_data.get("judge_verdict", {})
    if verdict:
        print(f"\n⚖️ Judge Evaluation:")
        decision = verdict.get("decision", "unknown")
        overall_score = verdict.get("overall_score", 0.0)
        
        if decision == "approve":
            print(f"  ✅ DECISION: APPROVED (Score: {overall_score:.2f})")
        elif decision == "revise":
            print(f"  ⚠️ DECISION: REVISED (Score: {overall_score:.2f})")
        else:
            print(f"  ❌ DECISION: REJECTED (Score: {overall_score:.2f})")
        
        # Quality issues
        issues = verdict.get("issues", [])
        if issues:
            print(f"\n  🔍 Quality Issues Found ({len(issues)}):")
            for i, issue in enumerate(issues, 1):
                check = issue.get('check', 'unknown')
                status = issue.get('status', 'unknown')
                score = issue.get('score', 0.0)
                details = issue.get('details', 'N/A')
                print(f"    {i}. {check.upper()} - {status.upper()} (Score: {score:.2f})")
                print(f"       Details: {details}")
        else:
            print("  ✅ No quality issues found!")
    
    print(f"\n🎉 Demo completed successfully!")
    print(f"\n💡 To see the full interactive UI, run:")
    print(f"   streamlit run streamlit_app.py")

if __name__ == "__main__":
    try:
        demo_triage_process()
    except KeyboardInterrupt:
        print("\n\n👋 Demo interrupted by user")
    except Exception as e:
        print(f"\n❌ Demo failed: {e}")
        print(f"\n💡 Make sure the API is running:")
        print(f"   uvicorn api.main:app --reload")
