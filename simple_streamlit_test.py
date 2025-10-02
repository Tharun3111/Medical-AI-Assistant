#!/usr/bin/env python3
"""
Simple Streamlit test to debug the issue
"""

import streamlit as st
import requests
import json

st.title("🏥 Doctor Bot - Simple Test")
st.markdown("Testing the basic functionality")

# Test API connection
if st.button("Test API Connection"):
    try:
        response = requests.get("http://127.0.0.1:8000/health", timeout=10)
        if response.status_code == 200:
            st.success("✅ API is working!")
            st.json(response.json())
        else:
            st.error(f"❌ API returned status {response.status_code}")
    except Exception as e:
        st.error(f"❌ API Error: {e}")

# Test triage call
if st.button("Test Triage Call"):
    try:
        response = requests.post(
            "http://127.0.0.1:8000/triage",
            json={"query": "fever and headache"},
            timeout=30
        )
        if response.status_code == 200:
            data = response.json()
            st.success("✅ Triage call successful!")
            st.write("Response keys:", list(data.keys()))
            st.write("Next action:", data.get('next_action'))
            
            if 'followup_questions' in data:
                st.write("Follow-up questions:")
                for i, q in enumerate(data['followup_questions'], 1):
                    st.write(f"{i}. {q.get('text', 'N/A')}")
        else:
            st.error(f"❌ Triage call returned status {response.status_code}")
    except Exception as e:
        st.error(f"❌ Triage Error: {e}")

# Test full triage with answers
if st.button("Test Full Triage"):
    try:
        # First call
        response1 = requests.post(
            "http://127.0.0.1:8000/triage",
            json={"query": "fever and headache"},
            timeout=30
        )
        
        if response1.status_code == 200:
            data1 = response1.json()
            st.write("Step 1 - Follow-up questions generated")
            
            # Second call with answers
            response2 = requests.post(
                "http://127.0.0.1:8000/triage",
                json={
                    "query": "fever and headache",
                    "followup_answers": {
                        "headache_location": "severe throbbing pain in temples",
                        "fever_duration": "2 days continuous"
                    }
                },
                timeout=30
            )
            
            if response2.status_code == 200:
                data2 = response2.json()
                st.success("✅ Full triage successful!")
                st.write("Response keys:", list(data2.keys()))
                st.write("Next action:", data2.get('next_action'))
                
                if 'triage_note' in data2:
                    st.write("Triage note generated!")
                    triage_note = data2['triage_note']
                    st.write("Patient query:", triage_note.get('patient_query'))
                    st.write("Possible conditions:", len(triage_note.get('possible_conditions', [])))
                
                if 'judge_verdict' in data2:
                    st.write("Judge verdict generated!")
                    verdict = data2['judge_verdict']
                    st.write("Decision:", verdict.get('decision'))
                    st.write("Overall score:", verdict.get('overall_score'))
            else:
                st.error(f"❌ Second call returned status {response2.status_code}")
        else:
            st.error(f"❌ First call returned status {response1.status_code}")
    except Exception as e:
        st.error(f"❌ Full triage error: {e}")
