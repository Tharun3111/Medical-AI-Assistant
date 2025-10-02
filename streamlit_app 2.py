#!/usr/bin/env python3
"""Streamlit web interface for Doctor Bot."""

import streamlit as st
import requests
import json
import time
from typing import List, Dict, Any
import sys
import os

# Add current directory to path
sys.path.append('.')

# Configure page
st.set_page_config(
    page_title="🏥 Doctor Bot - Clinical Screening Assistant",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# API configuration
API_BASE_URL = "http://127.0.0.1:8000"

def check_server_status():
    """Check if the API server is running."""
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=5)
        return response.status_code == 200, response.json()
    except:
        return False, None

def call_api(endpoint: str, data: Dict[str, Any] = None) -> Dict[str, Any]:
    """Make API call to backend."""
    try:
        if data:
            response = requests.post(f"{API_BASE_URL}{endpoint}", json=data, timeout=30)
        else:
            response = requests.get(f"{API_BASE_URL}{endpoint}", timeout=30)
        
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"API Error: {e}")
        return None

def display_retrieval_results(results: Dict[str, Any]):
    """Display retrieval results in a nice format."""
    if not results or 'hits' not in results:
        st.warning("No results found.")
        return
    
    st.subheader(f"📚 Found {results['total_hits']} relevant medical documents")
    
    for i, hit in enumerate(results['hits'], 1):
        with st.expander(f"📄 Document {i} (Relevance: {hit['score']:.1%})", expanded=i==1):
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.write(f"**Section:** {hit['metadata']['section']}")
                st.write(f"**Pages:** {hit['metadata']['page_start']}-{hit['metadata']['page_end']}")
                st.write(f"**Chunk ID:** `{hit['chunk_id']}`")
            
            with col2:
                # Color code the relevance score
                score = hit['score']
                if score >= 0.8:
                    st.success(f"**Score: {score:.1%}**")
                elif score >= 0.6:
                    st.warning(f"**Score: {score:.1%}**")
                else:
                    st.info(f"**Score: {score:.1%}**")
            
            st.write("**Content:**")
            st.write(hit['text'])

def main():
    """Main Streamlit application."""
    st.title("🏥 Doctor Bot - Clinical Screening Assistant")
    st.markdown("**Educational tool for symptom analysis and medical literature search**")
    
    # Check server status
    server_running, health_data = check_server_status()
    
    if not server_running:
        st.error("❌ API server is not running!")
        st.markdown("""
        **To start the server, run in your terminal:**
        ```bash
        cd "/Users/tharundchowdary/Desktop/Jay Project/doctor-bot"
        python simple_api.py
        ```
        """)
        return
    
    st.success("✅ API server is running and healthy!")
    
    # Sidebar
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        # Server status
        if health_data:
            st.success(f"**Status:** {health_data.get('status', 'unknown')}")
            st.info(f"**Version:** {health_data.get('version', 'unknown')}")
            st.success(f"**Retriever:** {'Loaded' if health_data.get('retriever_loaded') else 'Not loaded'}")
        
        st.markdown("---")
        
        # Search settings
        st.subheader("🔍 Search Settings")
        top_k = st.slider("Number of documents to retrieve", 1, 10, 5)
        
        st.markdown("---")
        
        # Sample queries
        st.subheader("💡 Sample Queries")
        sample_queries = [
            "chest pain",
            "fever and cough",
            "headache and neck stiffness",
            "abdominal pain",
            "shortness of breath",
            "diabetes symptoms",
            "hypertension signs",
            "depression symptoms"
        ]
        
        for query in sample_queries:
            if st.button(f"🔍 {query}", key=f"sample_{query}"):
                st.session_state.query = query
    
    # Main interface
    tab1, tab2, tab3 = st.tabs(["🔍 Medical Search", "📊 System Info", "ℹ️ About"])
    
    with tab1:
        st.header("Medical Literature Search")
        
        # Query input
        query = st.text_area(
            "Enter your medical query:",
            value=st.session_state.get('query', ''),
            placeholder="e.g., chest pain, fever and cough, headache with neck stiffness",
            height=100,
            help="Describe symptoms, conditions, or medical questions you want to research"
        )
        
        col1, col2, col3 = st.columns([1, 1, 2])
        
        with col1:
            search_button = st.button("🔍 Search", type="primary", use_container_width=True)
        
        with col2:
            clear_button = st.button("🗑️ Clear", use_container_width=True)
        
        if clear_button:
            st.session_state.query = ""
            st.rerun()
        
        # Process search
        if search_button and query:
            with st.spinner("Searching medical literature..."):
                start_time = time.time()
                
                data = {
                    "query": query,
                    "top_k": top_k
                }
                
                results = call_api("/retrieve", data)
                
                if results:
                    processing_time = time.time() - start_time
                    
                    # Display results
                    display_retrieval_results(results)
                    
                    # Show processing time
                    st.caption(f"⏱️ Search completed in {processing_time:.2f} seconds")
                    
                    # Show query info
                    st.info(f"**Query:** {query}")
                    st.info(f"**Documents retrieved:** {results['total_hits']}")
        
        elif search_button and not query:
            st.warning("Please enter a medical query to search.")
    
    with tab2:
        st.header("System Information")
        
        # System stats
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("API Status", "🟢 Online", "Healthy")
        
        with col2:
            st.metric("Server Version", "0.1.0", "Latest")
        
        with col3:
            st.metric("Retriever", "✅ Loaded", "Ready")
        
        # Test different queries
        st.subheader("🧪 Quick Tests")
        
        test_queries = [
            "chest pain",
            "fever and cough", 
            "headache neck stiffness",
            "abdominal pain"
        ]
        
        for test_query in test_queries:
            if st.button(f"Test: {test_query}", key=f"test_{test_query}"):
                with st.spinner(f"Testing '{test_query}'..."):
                    data = {"query": test_query, "top_k": 2}
                    results = call_api("/retrieve", data)
                    
                    if results:
                        st.success(f"✅ '{test_query}' - Found {results['total_hits']} results")
                        for hit in results['hits']:
                            st.write(f"  - {hit['chunk_id']}: {hit['score']:.1%}")
                    else:
                        st.error(f"❌ '{test_query}' - Failed")
    
    with tab3:
        st.header("About Doctor Bot")
        
        st.markdown("""
        **Doctor Bot** is an educational RAG (Retrieval-Augmented Generation) application 
        designed for clinical screening and medical literature search.
        
        ### 🎯 Features
        - 📚 **Medical Literature Search**: Search through "Symptoms to Diagnosis" book
        - 🔍 **Semantic Retrieval**: Find relevant medical information using AI
        - 📊 **Relevance Scoring**: See how relevant each result is
        - 🏥 **Clinical Context**: Get section and page references
        
        ### 🔧 Technical Stack
        - **Vector Search**: FAISS with BGE embeddings
        - **API**: FastAPI + Uvicorn
        - **UI**: Streamlit
        - **Knowledge Base**: Medical literature (6,025 chunks)
        
        ### ⚠️ Important Disclaimers
        - This is an **educational tool only**
        - **Not a substitute for professional medical advice**
        - Always consult qualified healthcare providers
        - Results should not be used for actual patient care
        
        ### 📊 System Stats
        - **Total Documents**: 6,025 medical chunks
        - **Average Chunk Size**: ~103 tokens
        - **Embedding Model**: BAAI/bge-small-en-v1.5
        - **Search Method**: Cosine similarity with FAISS
        """)
        
        # System health check
        st.subheader("🔍 System Health")
        if health_data:
            st.json(health_data)
        else:
            st.error("Unable to retrieve system health information")

if __name__ == "__main__":
    main()
