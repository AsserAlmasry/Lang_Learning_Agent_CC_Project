import re

class EnhancedIntentClassifier:
    def __init__(self):
        # Ordered by priority for exact matches
        self.patterns = {
            'quiz': [
                r'\bquiz\b', r'\btest\b', r'\bexercise\b', 
                r'check my level', r'assess me', r'evaluate me'
            ],
            'translation': [
                r'\btranslate\b', r'how to say', r'meaning of', 
                r'what is the meaning', r'translation of'
            ],
            'grammar': [
                r'grammar rule', r'how to use', 
                r'difference between', r'tense', r'preposition'
            ],
            'vocabulary': [
                r'vocabulary', r'synonym', r'antonym',
                r'definition of', r'use .* in a sentence'
            ],
            'conversation': [
                r'talk', r'chat', r'conversation', r'speak', 
                r'discuss', r'practice', r'help me learn'
            ]
        }

    def classify(self, text):
        text = text.lower()
        print(f"[Classifier] Analyzing query: '{text}'")
        
        # Immediate return for common greetings or vague help
        greetings = ['hello', 'hi', 'hey', 'how are you', "how's it going"]
        if any(g in text for g in greetings) and len(text.split()) < 10:
             print("[Classifier] Match found: greeting -> conversation")
             return 'conversation', 1.0

        # FORCE OVERRIDE for practice/conversation
        if any(w in text for w in ['practice', 'conversation', 'chat', 'talk', 'discuss']):
            print("[Classifier] Match found: explicit conversation trigger")
            return 'conversation', 1.0

        scores = {intent: 0 for intent in self.patterns}
        for intent, patterns in self.patterns.items():
            for pattern in patterns:
                if re.search(pattern, text):
                    scores[intent] += 1
                    print(f"[Classifier] Pattern matched: {intent} ({pattern})")
            
        best_intent = max(scores, key=scores.get)
        
        if scores[best_intent] == 0:
            print("[Classifier] No pattern matched -> defaulting to conversation")
            return 'conversation', 0.5
            
        # Specific safeguard: don't translate if the user is just talking about learning
        if best_intent == 'translation' and any(w in text for w in ["learn", "skill", "practice", "study"]):
             print("[Classifier] Safeguard triggered: translation ignored due to learning context")
             return 'conversation', 0.9
            
        confidence = min(scores[best_intent] / 2.0, 1.0)
        print(f"[Classifier] Final classification: {best_intent} (confidence: {confidence})")
        return best_intent, confidence


