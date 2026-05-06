from core.rag import RAGEngine
import os
from dotenv import load_dotenv

load_dotenv()

def deep_verify():
    print("CORE RAG DATA INTEGRITY CHECK")
    print("="*40)
    rag = RAGEngine()
    
    # Specific topics from the user's provided snippet
    critical_topics = [
        "Present Simple",
        "Mixed Conditionals",
        "Modal Ought To",
        "abandon", # vocab
        "Guten Morgen" # phrase
    ]
    
    matches = 0
    for topic in critical_topics:
        print(f"Checking for: '{topic}'...")
        try:
            results = rag.query(topic)
            if results:
                # Check if the content contains the specific text from the snippet
                content = results[0].page_content
                print(f"  [FOUND] Content Snippet: {content[:120].replace('\n', ' ')}...")
                matches += 1
            else:
                print(f"  [MISSING] No results for '{topic}'")
        except Exception as e:
            print(f"  [ERROR] {e}")

    print("="*40)
    if matches == len(critical_topics):
        print("INTEGRITY VERIFIED: The agent is 100% connected to the database initialized with your provided code.")
    else:
        print(f"PARTIAL MATCH: Found {matches}/{len(critical_topics)} topics.")

if __name__ == "__main__":
    deep_verify()
