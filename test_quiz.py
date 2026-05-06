import sys
import os
from dotenv import load_dotenv

# Load env before importing core to ensure API keys are set
load_dotenv()

from core.tools import EnhancedQuizTool
from core.agent import EnhancedLanguageLearningAgent
import json

agent = EnhancedLanguageLearningAgent()
query = "give me a 10-quaetion quiz on simple A1 vocab"

print("Running Quiz generation test...")
result = agent.tools['quiz'].run(query, context="Context about decide, explain, consider, compare, describe.")

print("Raw Output Length:", len(result))
try:
    data = json.loads(result)
    questions = data.get("questions", [])
    print("Number of questions generated:", len(questions))
except Exception as e:
    print("Failed to parse JSON:", e)
    print("Raw Output:", result)
