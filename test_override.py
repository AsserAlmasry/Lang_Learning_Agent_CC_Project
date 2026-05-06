import sys
import os

# Add the current directory to sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

# Mocking environment variables
os.environ["OPENAI_API_KEY"] = "mock_key"
os.environ["OPENROUTER_API_KEY"] = "mock_key"
os.environ["SENDER_EMAIL"] = "mock@example.com"
os.environ["SENDER_PASSWORD"] = "mock_pass"

try:
    from core.agent import EnhancedLanguageLearningAgent
    from unittest.mock import MagicMock
    import core.rag
    import core.tools
    
    core.rag.RAGEngine = MagicMock()
    core.tools.EnhancedGrammarTool = MagicMock()
    core.tools.EnhancedVocabularyTool = MagicMock()
    core.tools.EnhancedTranslationTool = MagicMock()
    core.tools.EnhancedQuizTool = MagicMock()
    core.tools.EnhancedConversationTool = MagicMock()
    
    agent = EnhancedLanguageLearningAgent()
    print("OK: Agent initialized")
    
    # Test with intent_override
    print("Testing with intent_override...")
    agent.classifier.classify = MagicMock(return_value=("grammar", 0.9))
    agent.rag.query = MagicMock(return_value=[])
    agent.tools['grammar'].run = MagicMock(return_value="Mocked response")
    
    result = agent.process_query("hello", intent_override="grammar")
    print(f"OK: Result: {result['intent']}")
    
except Exception as e:
    print(f"FAIL: {e}")
    import traceback
    traceback.print_exc()
