"""End-to-end test: vocabulary quiz must use vocabulary context, not general knowledge."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from dotenv import load_dotenv
load_dotenv()

from core.agent import EnhancedLanguageLearningAgent

agent = EnhancedLanguageLearningAgent()

print("=" * 60)
print("END-TO-END TEST: Vocabulary Quiz Routing")
print("=" * 60)

# Test 1: Vocabulary quiz should pull from vocabulary category
result = agent.process_query("give me a five question quiz on simple vocabulary in English", intent_override="quiz")

print(f"\nIntent: {result['intent']}")
print(f"Confidence: {result['confidence']}")
print(f"\nRetrieved Context (first 500 chars):")
ctx = result['retrieved_context'][:500]
# Safe print for Windows
safe_ctx = ctx.encode('ascii', errors='replace').decode('ascii')
print(safe_ctx)

print(f"\n--- Does context contain vocabulary data? ---")
has_vocab = any(w in ctx.lower() for w in ['word:', 'definition:', 'example:'])
has_grammar = 'tenses' in ctx.lower() or 'conditionals' in ctx.lower()

if has_vocab and not has_grammar:
    print("PASS: Quiz context is VOCABULARY (correct!)")
elif has_vocab:
    print("PARTIAL: Context has vocabulary but also grammar")
else:
    print("FAIL: Context is NOT vocabulary")

print(f"\nResponse (first 300 chars):")
safe_resp = result['response'][:300].encode('ascii', errors='replace').decode('ascii')
print(safe_resp)
print("=" * 60)
