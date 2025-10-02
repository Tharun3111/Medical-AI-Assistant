#!/usr/bin/env python3
"""Simple API for testing the system."""

import os
import sys
sys.path.append('.')

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import json

from rag.retriever import create_retriever
from rag.schemas import RetrievalHit

# Create FastAPI app
app = FastAPI(
    title="Doctor Bot API",
    description="RAG-based clinical screening application",
    version="0.1.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global retriever
retriever = None

class RetrieveRequest(BaseModel):
    query: str
    top_k: Optional[int] = 8

class RetrieveResponse(BaseModel):
    query: str
    hits: List[dict]
    total_hits: int

@app.on_event("startup")
async def startup_event():
    """Initialize the retriever on startup."""
    global retriever
    try:
        print("Loading retriever...")
        retriever = create_retriever(
            index_path="data/processed/faiss.index",
            mapping_path="data/processed/mapping.json"
        )
        print("Retriever loaded successfully!")
    except Exception as e:
        print(f"Error loading retriever: {e}")
        raise

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "version": "0.1.0",
        "retriever_loaded": retriever is not None
    }

@app.post("/retrieve", response_model=RetrieveResponse)
async def retrieve_documents(request: RetrieveRequest):
    """Retrieve relevant documents for a query."""
    if retriever is None:
        raise HTTPException(status_code=500, detail="Retriever not loaded")
    
    try:
        # Retrieve documents
        hits = retriever.retrieve(
            query=request.query,
            top_k=request.top_k,
            use_reranker=False
        )
        
        # Convert hits to dict format
        hits_dict = []
        for hit in hits:
            hits_dict.append({
                "chunk_id": hit.chunk_id,
                "score": hit.score,
                "text": hit.text[:200] + "..." if len(hit.text) > 200 else hit.text,
                "metadata": {
                    "section": hit.metadata.section,
                    "page_start": hit.metadata.page_start,
                    "page_end": hit.metadata.page_end
                }
            })
        
        return RetrieveResponse(
            query=request.query,
            hits=hits_dict,
            total_hits=len(hits_dict)
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error during retrieval: {str(e)}")

@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Doctor Bot API",
        "version": "0.1.0",
        "docs": "/docs",
        "health": "/health"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
