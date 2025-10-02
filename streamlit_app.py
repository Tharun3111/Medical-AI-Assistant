#!/usr/bin/env python3
"""
Streamlit UI for Doctor Bot with LLM-as-Judge Implementation
"""

import streamlit as st
import requests
import json
import time
from typing import Dict, List, Optional
import pandas as pd

# Configure page
st.set_page_config(
    page_title="Doctor Bot - LLM-as-Judge Demo",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# API Configuration
API_BASE_URL = "http://127.0.0.1:8000"

def call_api(endpoint: str, data: Dict) -> Optional[Dict]:
    """Call the API endpoint and return response."""
    try:
        response = requests.post(f"{API_BASE_URL}{endpoint}", json=data, timeout=30)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"API Error: {e}")
        return None

def display_qa_issues(issues: List[Dict]) -> None:
    """Display QA issues in a formatted way."""
    if not issues:
        st.success("✅ No quality issues found!")
        return
    
    st.subheader("🔍 Quality Assessment Issues")
    
    for i, issue in enumerate(issues, 1):
        check_type = issue.get('check', 'unknown')
        status = issue.get('status', 'unknown')
        details = issue.get('details', 'No details provided')
        score = issue.get('score', 0.0)
        offending_fields = issue.get('offending_fields', [])
        
        # Color coding based on status
        if status == "pass":
            color = "green"
            icon = "✅"
        elif status == "warn":
            color = "orange"
            icon = "⚠️"
        else:  # fail
            color = "red"
            icon = "❌"
        
        with st.expander(f"{icon} {check_type.title()} Check ({status.upper()}) - Score: {score:.2f}"):
            st.write(f"**Details:** {details}")
            if offending_fields:
                st.write(f"**Offending Fields:** {', '.join(offending_fields)}")

def display_triage_note(note: Dict) -> None:
    """Display triage note in a formatted way."""
    st.subheader("📋 Triage Note")
    
    # Patient Query
    st.write(f"**Patient Query:** {note.get('patient_query', 'N/A')}")
    
    # Followups Asked
    followups = note.get('followups_asked', [])
    if followups:
        st.write(f"**Follow-ups Asked:** {', '.join(followups)}")
    
    # Possible Conditions
    conditions = note.get('possible_conditions', [])
    if conditions:
        st.subheader("🔬 Possible Conditions")
        for i, condition in enumerate(conditions, 1):
            with st.expander(f"Condition {i}: {condition.get('name', 'Unknown')}"):
                st.write(f"**Rationale:** {condition.get('rationale', 'N/A')}")
                st.write(f"**Source:** {condition.get('source', 'N/A')}")
                support_chunks = condition.get('support_chunk_ids', [])
                if support_chunks:
                    st.write(f"**Supporting Chunks:** {', '.join(support_chunks)}")
    
    # Severity Flags
    severity_flags = note.get('severity_flags', {})
    if severity_flags:
        st.subheader("🚨 Severity Assessment")
        col1, col2 = st.columns(2)
        with col1:
            severity = severity_flags.get('severity', 'unknown')
            if severity == "emergent":
                st.error(f"**Severity:** {severity.upper()}")
            elif severity == "urgent":
                st.warning(f"**Severity:** {severity.upper()}")
            else:
                st.info(f"**Severity:** {severity.upper()}")
        
        with col2:
            st.write(f"**Source:** {severity_flags.get('source', 'N/A')}")
        
        red_flags = severity_flags.get('red_flags', [])
        if red_flags:
            st.write("**Red Flags:**")
            for flag in red_flags:
                st.write(f"• {flag}")
        
        emergency_action = severity_flags.get('emergency_action')
        if emergency_action:
            st.error(f"**Emergency Action:** {emergency_action}")
    
    # Test Recommendations
    tests = note.get('tests_to_discuss', [])
    if tests:
        st.subheader("🧪 Recommended Tests")
        for i, test in enumerate(tests, 1):
            with st.expander(f"Test {i}: {test.get('name', 'Unknown')}"):
                st.write(f"**Why:** {test.get('why', 'N/A')}")
                st.write(f"**Timing:** {test.get('timing', 'N/A')}")
                st.write(f"**Source:** {test.get('source', 'N/A')}")
                support_chunks = test.get('support_chunk_ids', [])
                if support_chunks:
                    st.write(f"**Supporting Chunks:** {', '.join(support_chunks)}")
    
    # Disease Course
    disease_course = note.get('disease_course', {})
    if disease_course:
        st.subheader("📈 Expected Disease Course")
        st.write(f"**Baseline Summary:** {disease_course.get('baseline_summary', 'N/A')}")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.write(f"**30 Days:** {disease_course.get('day_30', 'N/A')}")
        with col2:
            st.write(f"**60 Days:** {disease_course.get('day_60', 'N/A')}")
        with col3:
            st.write(f"**90 Days:** {disease_course.get('day_90', 'N/A')}")
        
        st.write(f"**Source:** {disease_course.get('source', 'N/A')}")
    
    # Lifestyle Plan
    lifestyle = note.get('lifestyle_plan', {})
    if lifestyle:
        st.subheader("🏃‍♂️ Lifestyle Recommendations")
        col1, col2 = st.columns(2)
        with col1:
            st.write(f"**Diet:** {lifestyle.get('diet', 'N/A')}")
            st.write(f"**Activity:** {lifestyle.get('activity', 'N/A')}")
            st.write(f"**Sleep:** {lifestyle.get('sleep', 'N/A')}")
        with col2:
            st.write(f"**Hydration:** {lifestyle.get('hydration', 'N/A')}")
            st.write(f"**Home Remedies:** {lifestyle.get('home_remedies', 'N/A')}")
        
        st.write(f"**Source:** {lifestyle.get('source', 'N/A')}")
    
    # Follow-up Schedule
    followup_schedule = note.get('followup_schedule', '')
    if followup_schedule:
        st.subheader("📅 Follow-up Schedule")
        st.write(followup_schedule)
    
    # Disclaimers
    disclaimers = note.get('disclaimers', '')
    if disclaimers:
        st.subheader("⚠️ Important Disclaimers")
        st.warning(disclaimers)

def main():
    """Main Streamlit application."""
    st.title("🏥 Doctor Bot - LLM-as-Judge Demo")
    st.markdown("**AI-powered clinical triage with quality assurance**")
    
    # Sidebar for configuration
    with st.sidebar:
        st.header("⚙️ Configuration")
        api_url = st.text_input("API URL", value=API_BASE_URL, help="Base URL for the Doctor Bot API")
        top_k = st.slider("Top K Retrieval", min_value=4, max_value=16, value=8, help="Number of top retrieval results")
        
        st.header("📊 System Status")
        # Check API health
        try:
            health_response = requests.get(f"{api_url}/health", timeout=5)
            if health_response.status_code == 200:
                st.success("✅ API Online")
            else:
                st.error("❌ API Error")
        except:
            st.error("❌ API Offline")
            st.info("Please start the API with: `uvicorn api.main:app --reload`")
    
    # Main content area
    tab1, tab2, tab3 = st.tabs(["🔍 Triage Process", "📊 Judge Analysis", "📚 About"])
    
    with tab1:
        st.header("Clinical Triage Process")
        st.markdown("This demo shows the two-step triage process with LLM-as-Judge quality assurance.")
        
        # Step 1: Initial Query
        st.subheader("Step 1: Patient Symptoms")
        patient_query = st.text_area(
            "Describe the patient's symptoms:",
            value="fever 3 days, chills, cough, poor appetite",
            height=100,
            help="Enter the patient's initial symptom description"
        )
        
        if st.button("🚀 Start Triage Process", type="primary"):
            if not patient_query.strip():
                st.error("Please enter patient symptoms.")
                return
            
            # Call API for initial triage (should return followup questions)
            with st.spinner("Analyzing symptoms and generating follow-up questions..."):
                response = call_api("/triage", {
                    "query": patient_query,
                    "top_k": top_k
                })
            
            if response:
                if response.get("next_action") == "ask_followups":
                    st.success("✅ Follow-up questions generated!")
                    
                    # Display follow-up questions
                    questions = response.get("followup_questions", [])
                    if questions:
                        st.subheader("❓ Follow-up Questions")
                        st.markdown("Please answer these questions to help with the triage assessment:")
                        
                        # Store questions in session state
                        st.session_state.questions = questions
                        st.session_state.patient_query = patient_query
                        
                        # Create form for answers
                        with st.form("followup_answers"):
                            st.markdown("**Please provide answers to the following questions:**")
                            answers = {}
                            
                            for i, question in enumerate(questions):
                                answer = st.text_input(
                                    f"Q{i+1}: {question.get('text', '')}",
                                    key=f"answer_{i}",
                                    help=f"Question ID: {question.get('id', 'unknown')}"
                                )
                                if answer:
                                    answers[question.get('text', f'Q{i+1}')] = answer
                            
                            submitted = st.form_submit_button("📋 Generate Triage Note", type="primary")
                            
                            if submitted and answers:
                                # Call API with answers
                                with st.spinner("Generating triage note and running quality assessment..."):
                                    triage_response = call_api("/triage", {
                                        "query": patient_query,
                                        "followup_answers": answers,
                                        "top_k": top_k
                                    })
                                
                                if triage_response:
                                    if triage_response.get("next_action") == "return_triage":
                                        st.success("✅ Triage note generated and quality assessed!")
                                        
                                        # Store results in session state
                                        st.session_state.triage_note = triage_response.get("triage_note")
                                        st.session_state.judge_verdict = triage_response.get("judge_verdict")
                                        
                                        # Display results
                                        display_triage_note(st.session_state.triage_note)
                                        
                                        # Show judge verdict
                                        verdict = st.session_state.judge_verdict
                                        if verdict:
                                            st.subheader("⚖️ Quality Assessment Results")
                                            
                                            decision = verdict.get("decision", "unknown")
                                            overall_score = verdict.get("overall_score", 0.0)
                                            
                                            if decision == "approve":
                                                st.success(f"✅ **APPROVED** - Overall Score: {overall_score:.2f}")
                                            elif decision == "revise":
                                                st.warning(f"⚠️ **REVISED** - Overall Score: {overall_score:.2f}")
                                                st.info("The triage note has been automatically revised based on quality assessment.")
                                            else:  # reject
                                                st.error(f"❌ **REJECTED** - Overall Score: {overall_score:.2f}")
                                            
                                            # Display issues
                                            issues = verdict.get("issues", [])
                                            display_qa_issues(issues)
                                            
                                            # Show if note was revised
                                            revised_note = verdict.get("revised_note")
                                            if revised_note and decision == "revise":
                                                st.subheader("📝 Revised Triage Note")
                                                st.info("The following is the judge-revised version of the triage note:")
                                                display_triage_note(revised_note)
                    else:
                        st.warning("No follow-up questions were generated.")
                else:
                    st.error("Unexpected response from API.")
            else:
                st.error("Failed to communicate with API.")
    
    with tab2:
        st.header("Judge Analysis Details")
        
        if "judge_verdict" in st.session_state and st.session_state.judge_verdict:
            verdict = st.session_state.judge_verdict
            
            # Overall assessment
            st.subheader("📊 Overall Assessment")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                decision = verdict.get("decision", "unknown")
                if decision == "approve":
                    st.metric("Decision", "✅ APPROVED", delta=None)
                elif decision == "revise":
                    st.metric("Decision", "⚠️ REVISED", delta=None)
                else:
                    st.metric("Decision", "❌ REJECTED", delta=None)
            
            with col2:
                overall_score = verdict.get("overall_score", 0.0)
                st.metric("Overall Score", f"{overall_score:.2f}", delta=None)
            
            with col3:
                issues_count = len(verdict.get("issues", []))
                st.metric("Issues Found", issues_count, delta=None)
            
            # Detailed breakdown
            issues = verdict.get("issues", [])
            if issues:
                st.subheader("🔍 Detailed Quality Checks")
                
                # Create a DataFrame for better visualization
                df_data = []
                for issue in issues:
                    df_data.append({
                        "Check Type": issue.get("check", "unknown").title(),
                        "Status": issue.get("status", "unknown").upper(),
                        "Score": f"{issue.get('score', 0.0):.2f}",
                        "Details": issue.get("details", "N/A"),
                        "Offending Fields": ", ".join(issue.get("offending_fields", []))
                    })
                
                df = pd.DataFrame(df_data)
                st.dataframe(df, use_container_width=True)
                
                # Show individual issues
                display_qa_issues(issues)
            else:
                st.success("✅ No quality issues found in the triage note!")
        else:
            st.info("Please complete the triage process first to see judge analysis details.")
    
    with tab3:
        st.header("About LLM-as-Judge Implementation")
        
        st.markdown("""
        ### 🎯 What is LLM-as-Judge?
        
        The LLM-as-Judge system is a quality assurance layer that evaluates AI-generated triage notes for:
        
        - **🔗 Grounding**: Every clinical claim must be supported by retrieved passages
        - **🔄 Consistency**: No internal contradictions; severity flags align with evidence
        - **🛡️ Safety**: Appropriate red-flags and disclaimers; no definitive diagnosis language
        - **📋 Completeness**: All required fields present; unsupported claims marked as "insufficient evidence"
        - **📝 Format**: Output validates against the TriageNote schema
        
        ### 🔄 Two-Step Process
        
        1. **Initial Assessment**: Generate follow-up questions based on patient symptoms
        2. **Triage Generation**: Create comprehensive triage note with judge evaluation
        
        ### ⚖️ Judge Decisions
        
        - **✅ APPROVE**: Note meets all quality standards
        - **⚠️ REVISE**: Note has issues but can be corrected automatically
        - **❌ REJECT**: Note has critical issues requiring manual review
        
        ### 🏗️ Technical Stack
        
        - **Primary LLM**: Google Gemini 1.5 Flash
        - **Fallback LLM**: Ollama Llama 3.1 8B
        - **Embeddings**: BAAI/bge-small-en-v1.5
        - **Vector DB**: FAISS
        - **API**: FastAPI
        - **UI**: Streamlit
        
        ### 🔒 Privacy & Safety
        
        - HIPAA-aware logging (minimal data retention)
        - No sensitive data exposure in logs
        - All clinical claims must be grounded in source material
        - Educational language only (no diagnostic claims)
        """)
        
        st.subheader("🚀 Getting Started")
        st.markdown("""
        1. Set your `GEMINI_API_KEY` environment variable
        2. Start the API: `uvicorn api.main:app --reload`
        3. Run this Streamlit app: `streamlit run streamlit_app.py`
        4. Enter patient symptoms and follow the two-step process
        """)

if __name__ == "__main__":
    main()
