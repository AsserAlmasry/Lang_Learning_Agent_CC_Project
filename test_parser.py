import json
import re
import ast

def test_parse(content):
    json_match = re.search(r'(\{.*\}|\[.*\])', content, re.DOTALL)
    if not json_match:
        print("No JSON match")
        return

    json_str = json_match.group(1)
    
    try:
        # Stage 1: Standard JSON
        raw_data = json.loads(json_str)
        print("Stage 1 SUCCESS")
        return raw_data
    except json.JSONDecodeError as e1:
        print(f"Stage 1 failed: {e1}")
        try:
            # Stage 2: Clean trailing commas
            json_str_clean = re.sub(r',\s*([\]}])', r'\1', json_str)
            # Clean unescaped newlines within strings
            json_str_clean = re.sub(r'(?<!\\)\n', ' ', json_str_clean)
            raw_data = json.loads(json_str_clean)
            print("Stage 2 SUCCESS")
            return raw_data
        except json.JSONDecodeError as e2:
            print(f"Stage 2 failed: {e2}")
            try:
                # Stage 3: Python AST evaluation
                raw_data = ast.literal_eval(json_str)
                print("Stage 3 SUCCESS")
                return raw_data
            except Exception as e3:
                print(f"Stage 3 failed: {e3}")
                return None

# The exact problematic payload:
content = """```json
{
    "questions": [
        {
            "question": "What does it mean to 'consider' something?",
            "A": "To think about something quickly",
            "B": "To think about something carefully",
            "C": "To ignore something",
            "D": "To forget something",
            "answer": "B"
        },
        {
            "question": "What is a 'challenge' in everyday language?",
            "A": "An easy task",
            "B": "A difficult task",
            "C": "A funny task",
            "D": "A boring task",
            "answer": "B"
        }
    ]
}
```"""

print("Running test...")
res = test_parse(content)
print(f"Result: {bool(res)}")
if res:
    print(res["questions"][0]["question"])
