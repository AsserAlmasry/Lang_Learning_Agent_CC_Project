"""
Full dataset re-ingestion script.
Rebuilds ChromaDB with grammar, vocabulary, AND phrases - matching the original notebook.
"""
import os, sys, shutil, json, time

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.rag import RAGEngine
from dotenv import load_dotenv
load_dotenv()

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
DB_PATH = os.path.join(DATA_DIR, "chroma_db")

def rebuild():
    print("=" * 60)
    print("FULL DATASET RE-INGESTION")
    print("=" * 60)

    # Step 1: Wipe old database
    if os.path.exists(DB_PATH):
        shutil.rmtree(DB_PATH)
        print("[1/4] Old database wiped.")
    time.sleep(1)

    # Step 2: Initialize fresh RAG engine
    rag = RAGEngine(persist_directory=DB_PATH)
    print("[2/4] Fresh RAG engine initialized.")

    # Step 3: Ingest all three datasets
    datasets = {
        "grammar": os.path.join(DATA_DIR, "grammar_kb.json"),
        "vocabulary": os.path.join(DATA_DIR, "vocabulary_kb.json"),
        "phrases": os.path.join(DATA_DIR, "phrases_kb.json"),
    }

    for category, path in datasets.items():
        if not os.path.exists(path):
            print(f"  [SKIP] {path} not found!")
            continue
        success, msg = rag.ingest_json_data(path, category)
        print(f"  [DONE] {msg}")

    print("[3/4] All datasets ingested.")

    # Step 4: Verification
    print("\n[4/4] VERIFICATION:")
    tests = {
        "grammar": "Present Simple",
        "vocabulary": "abandon",
        "phrases": "Good morning",
    }
    all_pass = True
    for cat, query in tests.items():
        results = rag.query(query, category=cat, k=1)
        if results:
            snippet = results[0].page_content[:100].replace('\n', ' ')
            print(f"  [{cat.upper()}] PASS -> {snippet}...")
        else:
            print(f"  [{cat.upper()}] FAIL -> No results for '{query}'")
            all_pass = False

    print("\n" + "=" * 60)
    if all_pass:
        print("SUCCESS: All 3 datasets ingested and verified.")
    else:
        print("WARNING: Some datasets failed verification.")
    print("=" * 60)

if __name__ == "__main__":
    rebuild()
