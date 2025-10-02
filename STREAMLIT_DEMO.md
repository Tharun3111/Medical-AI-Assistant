# 🏥 Doctor Bot - LLM-as-Judge Streamlit Demo

A comprehensive Streamlit interface demonstrating the LLM-as-Judge implementation for clinical triage with quality assurance.

## 🚀 Quick Start

### Option 1: Automated Startup (Recommended)
```bash
./start_demo.sh
```

This script will:
- Check for `.env` file and GEMINI_API_KEY
- Build vector index if needed
- Install Streamlit dependencies
- Start both API and Streamlit UI
- Open http://localhost:8501

### Option 2: Manual Startup

1. **Set up environment:**
   ```bash
   cp env.example .env
   # Edit .env and set your GEMINI_API_KEY
   ```

2. **Build vector index:**
   ```bash
   bash scripts/01_ingest.sh
   bash scripts/02_build_index.sh
   ```

3. **Install Streamlit dependencies:**
   ```bash
   pip install -r requirements_streamlit.txt
   ```

4. **Start API:**
   ```bash
   uvicorn api.main:app --reload
   ```

5. **Start Streamlit (in another terminal):**
   ```bash
   streamlit run streamlit_app.py
   ```

## 🎯 Features

### 📋 Two-Step Triage Process
1. **Initial Assessment**: Enter patient symptoms → Get follow-up questions
2. **Triage Generation**: Answer questions → Get judged triage note

### ⚖️ LLM-as-Judge Quality Assurance
- **Grounding Check**: All clinical claims must be supported by retrieved passages
- **Consistency Check**: No internal contradictions
- **Safety Check**: Appropriate red-flags and disclaimers
- **Completeness Check**: All required fields present
- **Format Check**: Valid TriageNote schema compliance

### 📊 Judge Analysis Dashboard
- Overall assessment score and decision
- Detailed breakdown of quality checks
- Issue tracking with specific field identification
- Automatic revision capabilities

## 🖥️ Interface Overview

### Tab 1: Triage Process
- Patient symptom input
- Follow-up question generation
- Answer collection form
- Triage note display
- Judge verdict presentation

### Tab 2: Judge Analysis
- Quality assessment metrics
- Detailed issue breakdown
- Score visualization
- Field-specific feedback

### Tab 3: About
- System explanation
- Technical stack details
- Getting started guide

## 🔧 Configuration

### API Settings (Sidebar)
- **API URL**: Base URL for Doctor Bot API (default: http://127.0.0.1:8000)
- **Top K Retrieval**: Number of retrieval results (4-16, default: 8)

### Environment Variables
- `GEMINI_API_KEY`: Required for primary LLM
- `USE_OLLAMA_FALLBACK`: Enable Ollama fallback (optional)
- `PROCESSED_DIR`: Path to processed data (default: data/processed)

## 📱 Usage Example

1. **Enter Symptoms**: "fever 3 days, chills, cough, poor appetite"
2. **Get Questions**: System generates relevant follow-up questions
3. **Answer Questions**: Provide detailed responses
4. **View Results**: See triage note with judge evaluation
5. **Analyze Quality**: Review judge assessment and any revisions

## 🎨 UI Components

### Status Indicators
- ✅ **APPROVED**: Note meets all quality standards
- ⚠️ **REVISED**: Note corrected by judge
- ❌ **REJECTED**: Note has critical issues

### Quality Checks
- **Grounding**: Claims supported by source material
- **Consistency**: No internal contradictions
- **Safety**: Appropriate warnings and disclaimers
- **Completeness**: All required fields present
- **Format**: Valid schema compliance

## 🔒 Privacy & Safety

- HIPAA-aware logging (minimal data retention)
- No sensitive data exposure in logs
- All clinical claims grounded in source material
- Educational language only (no diagnostic claims)

## 🛠️ Troubleshooting

### API Connection Issues
- Ensure API is running on http://127.0.0.1:8000
- Check GEMINI_API_KEY is set correctly
- Verify vector index is built

### Streamlit Issues
- Install dependencies: `pip install -r requirements_streamlit.txt`
- Check port 8501 is available
- Restart Streamlit if needed

### Data Issues
- Rebuild index: `bash scripts/01_ingest.sh && bash scripts/02_build_index.sh`
- Check data/processed/ directory exists
- Verify PDF is in data/raw/ directory

## 📚 API Endpoints

- `POST /triage`: Main triage endpoint with judge evaluation
- `GET /health`: Health check
- `GET /docs`: API documentation
- `POST /retrieve`: Document retrieval
- `POST /ingest`: PDF ingestion

## 🎯 Demo Scenarios

### Scenario 1: Simple Fever
- Input: "fever and headache"
- Expected: Follow-up questions about duration, severity
- Result: Routine triage with grounding checks

### Scenario 2: Complex Symptoms
- Input: "chest pain, shortness of breath, dizziness"
- Expected: Urgent triage with red-flag assessment
- Result: Judge evaluation of safety recommendations

### Scenario 3: Insufficient Information
- Input: "not feeling well"
- Expected: Comprehensive follow-up questions
- Result: Judge ensures completeness

## 🔄 Next Steps

1. **Customize Prompts**: Edit `llm/prompts/judge.txt` for specific requirements
2. **Adjust Scoring**: Modify judge evaluation criteria
3. **Add Visualizations**: Enhance charts and graphs
4. **Integrate EMR**: Connect to electronic medical records
5. **Deploy Production**: Scale for clinical use

---

**Note**: This is a demonstration system. For clinical use, ensure proper validation, testing, and regulatory compliance.
