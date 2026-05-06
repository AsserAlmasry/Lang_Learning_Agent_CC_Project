import sys
import os
from unittest.mock import MagicMock

# Add the current directory to sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

# Mocking environment variables before any imports
os.environ["OPENAI_API_KEY"] = "mock_key"
os.environ["OPENROUTER_API_KEY"] = "mock_key"
os.environ["SENDER_EMAIL"] = "mock@example.com"
os.environ["SENDER_PASSWORD"] = "mock_pass"

try:
    from core.classifier import EnhancedIntentClassifier
    from core.agent import EnhancedLanguageLearningAgent
    from utils.config import Config
    print("OK: Imports successful")
except Exception as e:
    print(f"FAIL: Import failed: {e}")
    # Show traceback for debugging
    import traceback
    traceback.print_exc()
    sys.exit(1)

def test_classifier():
    classifier = EnhancedIntentClassifier()
    test_cases = {
        "Can you explain the past tense?": "grammar",
        "What does 'stunning' mean?": "vocabulary",
        "Translate this to Arabic.": "translation",
        "I want to take a quiz.": "quiz",
        "Hello, how are you?": "conversation"
    }
    
    for text, expected in test_cases.items():
        intent, confidence = classifier.classify(text)
        if intent == expected:
            print(f"OK: Classifier: '{text}' -> {intent} (Correct)")
        else:
            print(f"FAIL: Classifier: '{text}' -> {intent} (Expected {expected})")

def test_agent_initialization():
    try:
        # We mock RAGEngine and Tools to avoid actual API calls
        import core.rag
        import core.tools
        
        core.rag.RAGEngine = MagicMock()
        core.tools.EnhancedGrammarTool = MagicMock()
        core.tools.EnhancedVocabularyTool = MagicMock()
        core.tools.EnhancedTranslationTool = MagicMock()
        core.tools.EnhancedQuizTool = MagicMock()
        core.tools.EnhancedConversationTool = MagicMock()
        
        agent = EnhancedLanguageLearningAgent()
        print("OK: Agent initialization successful (Mocked)")
        
        # Test query processing
        agent.classifier.classify = MagicMock(return_value=("grammar", 0.9))
        agent.rag.query = MagicMock(return_value=[])
        agent.tools['grammar'].run = MagicMock(return_value="Mocked grammar explanation")
        
        result = agent.process_query("Tell me about grammar")
        if result['response'] == "Mocked grammar explanation":
            print("OK: Agent query processing successful (Mocked)")
        else:
            print("FAIL: Agent query processing failed")
            
    except Exception as e:
        print(f"FAIL: Agent test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_classifier()
    test_agent_initialization()
