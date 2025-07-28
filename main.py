import os
import json
import fitz 
import uuid
import re
import unicodedata
from datetime import datetime
import numpy as np
import spacy
from spacy.lang.en.stop_words import STOP_WORDS
import argparse

def clean_text(text):
    if not text:
        return ""
    text = unicodedata.normalize('NFKC', text)
    replacements = {
        '\ufb00': 'ff', '\ufb01': 'fi', '\ufb02': 'fl', '\ufb03': 'ffi', '\ufb04': 'ffl',
        '\u2022': '•', '\u00e9': 'é', '\u00e8': 'è', '\u00e0': 'à', '\u00e7': 'ç', '\u00f4': 'ô', '\u00fb': 'û'
    }
    for code, rep in replacements.items():
        text = text.replace(code, rep)
    return re.sub(r'\s+', ' ', re.sub(r'[\x00-\x1F\x7F-\x9F]', ' ', text)).strip()

def load_spacy_model(name="en_core_web_md"):
    try:
        return spacy.load(name)
    except Exception as e:
        print(f"spaCy model load failed: {e}")
        exit(1)

nlp = load_spacy_model()

def extract_chunks(pdf_path, window=2):
    try:
        doc = fitz.open(pdf_path)
        pages = []
        for i in range(len(doc) - window + 1):
            text = " ".join(doc[j].get_text().strip() for j in range(i, i + window))
            if text:
                pages.append({'page': i + 1, 'text': clean_text(text)})
        return pages
    except Exception as e:
        print(f"Failed to extract chunks from {pdf_path}: {e}")
        return []

def compute_keyword_score(text, prompt):
    words = [w for w in prompt.lower().split() if w not in STOP_WORDS and len(w) > 2]
    return min(sum(1 for w in words if w in text.lower()) * 0.03, 0.15)

def compute_intent_score(text):
    doc = nlp(text)
    return min(sum(1 for t in doc if t.pos_ == "VERB" and t.tag_ in ["VB", "VBP"]) * 0.02, 0.1)

def get_vector(text):
    doc = nlp(text)
    return doc.vector if doc.has_vector else np.zeros((nlp.vocab.vectors_length,), dtype=np.float32)

def cosine_similarity(v1, v2):
    dot, norm1, norm2 = np.dot(v1, v2), np.linalg.norm(v1), np.linalg.norm(v2)
    return dot / (norm1 * norm2) if norm1 and norm2 else 0.0

def hybrid_score(prompt, text, sim):
    return sim * 0.8 + compute_keyword_score(text, prompt) * 0.1 + compute_intent_score(text) * 0.1

def clean_title(text):
    snippet = clean_text(text)
    return (snippet[:60].strip() + "...") if len(snippet) > 60 else snippet

def process_documents(folder, persona, job, top_k=5, per_doc_top=2):
    prompt = f"Persona: {persona}. Job to be done: {job}"
    prompt_vec = get_vector(prompt)
    pdfs = [f for f in os.listdir(folder) if f.endswith(".pdf")]
    if not pdfs:
        print("No PDFs found in 'documents' folder.")
        return

    all_chunks = []
    for pdf in pdfs:
        try:
            path = os.path.join(folder, pdf)
            chunks = extract_chunks(path)
            for c in chunks:
                c.update({'document': pdf, 'text': clean_text(c['text']), 'type': 'text'})
            all_chunks.extend(chunks)
        except Exception as e:
            print(f"Skipped {pdf}: {e}")

    if not all_chunks:
        print("No content extracted.")
        return

    for c in all_chunks:
        vec = get_vector(c['text'])
        sim = cosine_similarity(prompt_vec, vec)
        c['score'] = hybrid_score(prompt, c['text'], sim)

    doc_groups = {}
    for c in all_chunks:
        doc_groups.setdefault(c['document'], []).append(c)

    top_chunks = []
    for doc, chunks in doc_groups.items():
        top_chunks.extend(sorted(chunks, key=lambda x: x['score'], reverse=True)[:per_doc_top])

    global_top = sorted(top_chunks, key=lambda x: x['score'], reverse=True)[:top_k]
    sections, subsections = [], []
    for i, c in enumerate(global_top):
        sections.append({"document": c['document'], "section_title": clean_title(c['text']), "importance_rank": i + 1, "page_number": c['page']})
        subsections.append({"document": c['document'], "refined_text": c['text'], "page_number": c['page']})

    result = {
        "metadata": {
            "input_documents": pdfs,
            "persona": persona,
            "job_to_be_done": job,
            "processing_timestamp": datetime.now().isoformat()
        },
        "extracted_sections": sections,
        "subsection_analysis": subsections
    }

    output_file = f"output/output_{uuid.uuid4().hex[:6]}.json"
    try:
        with open(output_file, "w", encoding='utf-8') as f:
            json.dump(result, f, indent=4, ensure_ascii=False)
        print(f"\nOutput saved to: {output_file}")
    except Exception as e:
        print(f"Failed to write output: {e}")

# In your __main__ section:
if __name__ == "__main__":
    os.makedirs("documents", exist_ok=True)
    os.makedirs("output", exist_ok=True)
    
    persona = os.environ.get("PERSONA")
    job = os.environ.get("JOB")
    
    if not persona or not job:
        print("ERROR: Both PERSONA and JOB environment variables must be set")
        exit(1)
    
    process_documents(folder="documents", persona=persona, job=job)  
