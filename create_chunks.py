#!/usr/bin/env python3
"""Simple script to create chunks from sections."""

import json
import os
from rag.chunkers import MedicalTextChunker
from rag.schemas import Section, Chunk, ChunkMeta

def main():
    print("Loading sections...")
    sections = []
    with open('data/interim/sections.jsonl', 'r') as f:
        for i, line in enumerate(f):
            if i % 500 == 0:
                print(f"Loaded {i} sections...")
            try:
                section_data = json.loads(line.strip())
                section = Section(**section_data)
                sections.append(section)
            except Exception as e:
                print(f"Error loading section {i}: {e}")
                continue

    print(f"Total sections loaded: {len(sections)}")

    print("Creating chunker...")
    chunker = MedicalTextChunker(target_tokens=400, overlap_sentences=2)

    print("Creating chunks...")
    all_chunks = []
    
    for i, section in enumerate(sections):
        if i % 100 == 0:
            print(f"Processing section {i}/{len(sections)}...")
        
        try:
            chunks = chunker.chunk_sections([section])
            all_chunks.extend(chunks)
        except Exception as e:
            print(f"Error processing section {i}: {e}")
            continue

    print(f"Created {len(all_chunks)} chunks")

    print("Saving chunks...")
    os.makedirs('data/processed', exist_ok=True)
    
    with open('data/processed/chunks.jsonl', 'w') as f:
        for i, chunk in enumerate(all_chunks):
            if i % 1000 == 0:
                print(f"Saved {i} chunks...")
            f.write(json.dumps(chunk.model_dump(), ensure_ascii=False) + '\n')

    print("Chunks saved successfully!")
    print(f"Total chunks: {len(all_chunks)}")
    
    # Calculate average tokens
    total_tokens = sum(chunk.metadata.token_count for chunk in all_chunks)
    avg_tokens = total_tokens / len(all_chunks) if all_chunks else 0
    print(f"Average tokens per chunk: {avg_tokens:.1f}")

if __name__ == "__main__":
    main()
