from core.rag import RAGEngine
import os
from dotenv import load_dotenv

load_dotenv()

def verify():
    print("VERIFYING RAG SYSTEM CONNECTIVITY...")
    rag = RAGEngine()
    
    test_queries = [
        "vocabulary",
        "grammar",
        "phrases"
    ]
    
    for q in test_queries:
        print(f"\n--- Testing Query: '{q}' ---")
        try:
            # Our query method signature: query(self, query_text, category=None)
            results = rag.query(q, category=q if q != "phrases" else None)
            if not results:
                print("No results found.")
                continue
                
            print(f"Found {len(results)} relevant documents.")
            for i, doc in enumerate(results):
                content_preview = doc.page_content[:150].replace('\n', ' ')
                category = doc.metadata.get('category', 'unknown')
                print(f"  [{i+1}] ({category}): {content_preview}...")
        except Exception as e:
            print(f"Error during query: {e}")

if __name__ == "__main__":
    verify()
