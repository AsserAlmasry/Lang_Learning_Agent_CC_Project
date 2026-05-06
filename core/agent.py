from core.classifier import EnhancedIntentClassifier
from core.rag import RAGEngine
from core.tools import (
    EnhancedGrammarTool, 
    EnhancedVocabularyTool, 
    EnhancedTranslationTool, 
    EnhancedQuizTool, 
    EnhancedConversationTool
)

class EnhancedLanguageLearningAgent:
    def __init__(self):
        self.classifier = EnhancedIntentClassifier()
        self.rag = RAGEngine()
        self.tools = {
            'grammar': EnhancedGrammarTool(),
            'vocabulary': EnhancedVocabularyTool(),
            'translation': EnhancedTranslationTool(),
            'quiz': EnhancedQuizTool(),
            'conversation': EnhancedConversationTool()
        }
        self.session_history = []

    def process_query(self, query, intent_override=None):
        if intent_override:
            intent = intent_override
            confidence = 1.0
        else:
            intent, confidence = self.classifier.classify(query)
        
        # Retrieval
        retrieval_category = intent if intent in ['grammar', 'vocabulary'] else None
        
        # Override retrieval category for quizzes based on query content
        if intent == 'quiz':
            q_lower = query.lower()
            if any(w in q_lower for w in ['vocab', 'word', 'definition', 'meaning']):
                retrieval_category = 'vocabulary'
            elif any(w in q_lower for w in ['phrase', 'expression', 'translation']):
                retrieval_category = 'phrases'
            else:
                retrieval_category = 'grammar'
        
        # Retrieve more docs for quizzes so the LLM has rich context
        # We need at least 50 to guarantee enough unique content for a 10-question quiz without overlaps
        k = 50 if intent == 'quiz' else 3
        retrieved_docs = self.rag.query(query, category=retrieval_category, k=k)
        context = "\n".join([doc.page_content for doc in retrieved_docs])
        
        # Tool Execution
        if intent == 'conversation':
            response = self.tools[intent].run(query, history=self.session_history[-5:], practice_mode=(intent_override == 'conversation'))
        else:
            response = self.tools[intent].run(query, context=context)
            
        # Log to history
        self.session_history.append({"role": "user", "content": query})
        self.session_history.append({"role": "assistant", "content": response})
        
        return {
            "intent": intent,
            "confidence": confidence,
            "response": response,
            "retrieved_context": context
        }
