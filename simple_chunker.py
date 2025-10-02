#!/usr/bin/env python3
"""Simple, robust chunking for medical text."""

import re
import json
import os
from typing import List
from transformers import AutoTokenizer
from rag.schemas import Chunk, ChunkMeta, Section

class SimpleChunker:
    """Simple chunker that works reliably."""
    
    def __init__(self, target_tokens: int = 300):
        self.target_tokens = target_tokens
        self.tokenizer = AutoTokenizer.from_pretrained("BAAI/bge-small-en-v1.5")
    
    def count_tokens(self, text: str) -> int:
        """Count tokens safely."""
        try:
            tokens = self.tokenizer.encode(text, truncation=True, max_length=512)
            return len(tokens)
        except:
            # Fallback: rough estimation
            return len(text.split()) * 1.3
    
    def split_text(self, text: str) -> List[str]:
        """Split text into sentences."""
        sentences = re.split(r'(?<=[.!?])\s+', text)
        return [s.strip() for s in sentences if s.strip()]
    
    def create_chunks(self, sections: List[Section]) -> List[Chunk]:
        """Create chunks from sections."""
        all_chunks = []
        chunk_counter = 0
        
        for section in sections:
            if not section.content.strip():
                continue
                
            sentences = self.split_text(section.content)
            current_chunk = []
            current_tokens = 0
            
            for sentence in sentences:
                sentence_tokens = self.count_tokens(sentence)
                
                # If single sentence is too long, truncate it
                if sentence_tokens > self.target_tokens:
                    sentence = self.truncate_text(sentence, self.target_tokens)
                    sentence_tokens = self.target_tokens
                
                # If adding this sentence exceeds target, create chunk
                if current_tokens + sentence_tokens > self.target_tokens and current_chunk:
                    chunk_counter += 1
                    chunk = self.create_chunk_from_sentences(
                        current_chunk, section, chunk_counter
                    )
                    all_chunks.append(chunk)
                    current_chunk = [sentence]
                    current_tokens = sentence_tokens
                else:
                    current_chunk.append(sentence)
                    current_tokens += sentence_tokens
            
            # Add remaining sentences as final chunk
            if current_chunk:
                chunk_counter += 1
                chunk = self.create_chunk_from_sentences(
                    current_chunk, section, chunk_counter
                )
                all_chunks.append(chunk)
        
        return all_chunks
    
    def truncate_text(self, text: str, max_tokens: int) -> str:
        """Truncate text to fit token limit."""
        try:
            tokens = self.tokenizer.encode(text, truncation=True, max_length=max_tokens)
            return self.tokenizer.decode(tokens, skip_special_tokens=True)
        except:
            # Fallback: character-based truncation
            return text[:max_tokens * 4]
    
    def create_chunk_from_sentences(self, sentences: List[str], section: Section, chunk_id: int) -> Chunk:
        """Create a chunk from sentences."""
        text = ' '.join(sentences)
        tokens = self.count_tokens(text)
        
        chunk_id_str = f"chunk_{chunk_id:06d}"
        
        metadata = ChunkMeta(
            id=chunk_id_str,
            chapter=section.chapter,
            section=section.title,
            page_start=section.page_start,
            page_end=section.page_end,
            token_count=tokens
        )
        
        return Chunk(
            id=chunk_id_str,
            text=text,
            metadata=metadata
        )

def main():
    print("Loading sections...")
    sections = []
    with open('data/interim/sections.jsonl', 'r') as f:
        for i, line in enumerate(f):
            if i % 1000 == 0:
                print(f"Loaded {i} sections...")
            try:
                section_data = json.loads(line.strip())
                section = Section(**section_data)
                sections.append(section)
            except Exception as e:
                print(f"Error loading section {i}: {e}")
                continue

    print(f"Total sections loaded: {len(sections)}")

    print("Creating chunks...")
    chunker = SimpleChunker(target_tokens=300)
    chunks = chunker.create_chunks(sections)
    
    print(f"Created {len(chunks)} chunks")

    print("Saving chunks...")
    os.makedirs('data/processed', exist_ok=True)
    
    with open('data/processed/chunks.jsonl', 'w') as f:
        for i, chunk in enumerate(chunks):
            if i % 1000 == 0:
                print(f"Saved {i} chunks...")
            f.write(json.dumps(chunk.model_dump(), ensure_ascii=False) + '\n')

    print("Chunks saved successfully!")
    print(f"Total chunks: {len(chunks)}")
    
    # Calculate stats
    total_tokens = sum(chunk.metadata.token_count for chunk in chunks)
    avg_tokens = total_tokens / len(chunks) if chunks else 0
    print(f"Average tokens per chunk: {avg_tokens:.1f}")

if __name__ == "__main__":
    main()
