import openai
from groq import Groq
from utils.config import Config
from utils.email_helper import send_feedback_email

class BaseTool:
    def __init__(self):
        # Primary LLM is now Groq
        self.groq_client = Groq(api_key=Config.GROQ_API_KEY) if Config.GROQ_API_KEY else None
        
        # Fallback/Secondary is OpenRouter
        self.openrouter_client = openai.OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=Config.OPENROUTER_API_KEY,
        )
        
        # Keep OpenAI client just in case (optional)
        self.openai_client = openai.OpenAI(api_key=Config.OPENAI_API_KEY) if Config.OPENAI_API_KEY else None

    def _get_completion(self, prompt, messages=None, fast=True):
        """Helper to route to Groq primarily, OpenRouter secondarily."""
        if messages is None:
            messages = [{"role": "user", "content": prompt}]
            
        model = Config.GROQ_FAST_MODEL if fast else Config.GROQ_MODEL
            
        if self.groq_client:
            try:
                # Force valid JSON if requested
                kwargs = {
                    "model": model,
                    "messages": messages,
                    "max_tokens": 4000
                }
                if prompt and "json object" in prompt.lower():
                    kwargs["response_format"] = {"type": "json_object"}
                    
                response = self.groq_client.chat.completions.create(**kwargs)
                return response.choices[0].message.content
            except Exception as e:
                import streamlit as st
                st.error(f"Groq API Error: {e}")
                print(f"Groq error: {e}, falling back to OpenRouter")
        
        # OpenRouter fallback
        response = self.openrouter_client.chat.completions.create(
            model="meta-llama/llama-3.2-3b-instruct:free",
            messages=messages,
            max_tokens=4000
        )
        return response.choices[0].message.content

class EnhancedGrammarTool(BaseTool):
    def run(self, query, context=""):
        prompt = f"English Teacher Mode: Explain the following grammar point.\nContext from Knowledge Base: {context}\nUser Query: {query}"
        return self._get_completion(prompt)

class EnhancedVocabularyTool(BaseTool):
    def run(self, query, context=""):
        prompt = f"English Teacher Mode: Explain this word or vocabulary point.\nContext from Knowledge Base: {context}\nUser Query: {query}"
        return self._get_completion(prompt)

class EnhancedTranslationTool(BaseTool):
    def run(self, query, context=""):
        prompt = f"Translator Mode: Translate this and explain the nuances.\nContext: {context}\nText: {query}"
        return self._get_completion(prompt)

class EnhancedQuizTool(BaseTool):
    def run(self, query, context=""):
        import re
        # Find requested number up to 10 (e.g. "10-question", "7 questions")
        match = re.search(r'\b(10|[1-9])\b\s*-?\s*q', query, re.IGNORECASE)
        if not match:
            # Fallback to any number 1-10
            match = re.search(r'\b(10|[1-9])\b', query)
            
        num_q = match.group(1) if match else "5"
        
        system_prompt = (
            f"You are a professional English Quiz Master. Generate an interactive multiple-choice quiz focusing on the USER'S REQUESTED TOPIC: '{query}'.\n"
            f"Use the provided context to guide the difficulty level and style, but ensure the questions are primarily about the specific topic the user asked for.\n"
            f"If the context doesn't have enough information on the topic, use your general knowledge of English teaching to create high-quality questions.\n"
            f"CRITICAL: You MUST generate EXACTLY {num_q} questions. Do not generate more. Do not generate fewer.\n"
            f"CRITICAL: Output MUST be a perfectly valid JSON object with a 'questions' key. "
            f"All keys and all string values MUST be enclosed in double quotes.\n\n"
            f"Use this exact JSON format template:\n"
            f"{{\n"
            f"  \"questions\": [\n"
            f"    {{\n"
            f"      \"question\": \"Question text here?\",\n"
            f"      \"A\": \"Option A text\",\n"
            f"      \"B\": \"Option B text\",\n"
            f"      \"C\": \"Option C text\",\n"
            f"      \"D\": \"Option D text\",\n"
            f"      \"answer\": \"B\"\n"
            f"    }}\n"
            f"  ]\n"
            f"}}\n"
            f"For 'answer', provide ONLY the exact single uppercase letter (A, B, C, or D) of the correct option."
        )
        prompt = f"{system_prompt}\n\nContext for reference: {context}"
        # Use the powerful 70B model (fast=False) to ensure it obeys the exact question count
        return self._get_completion(prompt, fast=False)

class EnhancedConversationTool(BaseTool):
    def run(self, query, history=[], practice_mode=False):
        # Use big model for reformatting, fast model for chat
        is_reformat = "reformat" in query.lower() or "ocr" in query.lower()
        
        if practice_mode:
            system_prompt = (
                "You are an English Conversation Practice Partner. RULES:\n"
                "1. Stay in character for the scenario described in the first message.\n"
                "2. Respond naturally as the character would (barista, interviewer, receptionist, etc.).\n"
                "3. Keep your replies SHORT and conversational (2-4 sentences max).\n"
                "4. If the user makes a grammar or vocabulary mistake, BRIEFLY note it at the end of your response "
                "in this format: [Tip: 'incorrect phrase' -> 'correct phrase']\n"
                "5. Ask a follow-up question to keep the conversation going.\n"
                "6. Do NOT break character. Do NOT explain you are an AI.\n"
                "7. Use simple, clear English appropriate for language learners."
            )
        else:
            system_prompt = (
                "You are a professional English tutor and Academic Assistant. "
                "Your goal is to help users learn English while also assisting with their academic tasks. "
                "If a user provides fragmented text (like an OCR transcript), your task is to intelligently reconstruct it "
                "into a clean, professional, and structured document using Markdown (tables, bold headings, lists). "
                "Correct any obvious OCR typos while maintaining the original meaning. "
                "Always be encouraging and professional."
            )
        
        messages = [{"role": "system", "content": system_prompt}]
        messages.extend(history)
        messages.append({"role": "user", "content": query})
        return self._get_completion(None, messages=messages, fast=not is_reformat)

