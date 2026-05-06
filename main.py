import streamlit as st
import time
import os
import json
from core.agent import EnhancedLanguageLearningAgent
from utils.config import Config
from streamlit_mic_recorder import mic_recorder
import easyocr
from PIL import Image
import numpy as np

# Page config
st.set_page_config(
    page_title="English Language Learning Agent",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Beautiful Custom CSS (Extracted from original notebook)
st.markdown("""
<style>
.main {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    padding: 2rem;
}
.stButton>button {
    background: linear-gradient(90deg, #f093fb 0%, #f5576c 100%);
    color: white;
    border-radius: 12px;
    padding: 12px 28px;
    border: none;
    box-shadow: 0 4px 15px rgba(245, 87, 108, 0.4);
    font-weight: 600;
    transition: all 0.3s ease;
}
.stButton>button:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 20px rgba(245, 87, 108, 0.6);
}
.chat-message {
    padding: 1.5rem;
    border-radius: 15px;
    margin-bottom: 1.5rem;
    box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    animation: fadeIn 0.5s ease;
}
@keyframes fadeIn {
    from { opacity: 0; transform: translateY(10px); }
    to { opacity: 1; transform: translateY(0); }
}
.user-message {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    margin-left: 10%;
}
.bot-message {
    background: white;
    color: #333;
    border-left: 4px solid #f5576c;
    margin-right: 10%;
}
.tool-badge {
    display: inline-block;
    padding: 8px 16px;
    border-radius: 20px;
    font-size: 14px;
    margin: 5px;
    font-weight: 600;
    box-shadow: 0 2px 8px rgba(0,0,0,0.15);
    transition: all 0.3s ease;
}
.tool-badge:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(0,0,0,0.2);
}
.stTextInput>div>div>input {
    border-radius: 10px;
    border: 2px solid #e0e0e0;
    padding: 12px;
    font-size: 16px;
}
.stTextInput>div>div>input:focus {
    border-color: #f5576c;
    box-shadow: 0 0 0 0.2rem rgba(245, 87, 108, 0.25);
}
h1, h2, h3 {
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
}
</style>
""", unsafe_allow_html=True)

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "current_mode" not in st.session_state:
    st.session_state.current_mode = "free"
if "session_id" not in st.session_state:
    st.session_state.session_id = time.time()
if "practice_scenario" not in st.session_state:
    st.session_state.practice_scenario = None

def get_duration():
    return round((time.time() - st.session_state.session_id) / 60, 1)

if 'agent' not in st.session_state:
    valid, msg = Config.validate()
    if not valid:
        st.error(msg)
        st.stop()
    st.session_state.agent = EnhancedLanguageLearningAgent()

# Sidebar
with st.sidebar:
    st.markdown("""
    <div style="background-color: #d4edda; color: #155724; padding: 10px; border-radius: 5px; border: 1px solid #c3e6cb; margin-bottom: 20px;">
        ✅ 1781 documents loaded
    </div>
    """, unsafe_allow_html=True)

    st.markdown("### 🎯 Available Tools")
    st.markdown("""
    <div class="tool-badge" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white;">1️⃣ Grammar</div>
    <div class="tool-badge" style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); color: white;">2️⃣ Vocabulary</div>
    <div class="tool-badge" style="background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); color: white;">3️⃣ Translation</div>
    <div class="tool-badge" style="background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%); color: white;">4️⃣ Quiz (10Q)</div>
    <div class="tool-badge" style="background: linear-gradient(135deg, #fa709a 0%, #fee140 100%); color: white;">5️⃣ Conversation</div>
    <div class="tool-badge" style="background: linear-gradient(135deg, #30cfd0 0%, #330867 100%); color: white;">6️⃣ Email Results</div>
    """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("### 💡 Test Modes")
    
    if st.button("1️⃣ Test Grammar Handler", use_container_width=True):
        st.session_state.current_mode = "grammar"
        st.session_state.messages.append({"role": "assistant", "content": "Grammar mode activated! Try: 'Explain present perfect tense'", "intent": "GRAMMAR"})
        st.rerun()
    
    if st.button("2️⃣ Test Vocabulary Handler", use_container_width=True):
        st.session_state.current_mode = "vocabulary"
        st.session_state.messages.append({"role": "assistant", "content": "Vocabulary mode activated! Try: 'What does achieve mean?'", "intent": "VOCABULARY"})
        st.rerun()

    if st.button("3️⃣ Test Translation Tool", use_container_width=True):
        st.session_state.current_mode = "translation"
        st.session_state.messages.append({"role": "assistant", "content": "Translation mode activated! Try: 'Translate hello to Arabic'", "intent": "TRANSLATION"})
        st.rerun()

    if st.button("4️⃣ Test Interactive Quiz", use_container_width=True):
        st.session_state.current_mode = "quiz"
        st.session_state.messages.append({"role": "assistant", "content": "Quiz mode activated! Try: 'Give me a quiz on conditionals'", "intent": "QUIZ"})
        st.rerun()

    st.markdown("---")
    st.markdown("### 💬 Conversation Practice")
    scenarios = {
        "Free Chat": "Have a friendly casual conversation in English about any topic the user wants.",
        "At a Cafe": "You are a barista at a coffee shop. Greet the customer and take their order naturally.",
        "Job Interview": "You are an HR interviewer for a tech company. Conduct a professional job interview.",
        "Hotel Check-in": "You are a hotel receptionist. Help the guest check in and answer questions about the hotel.",
        "Doctor Visit": "You are a doctor. Ask the patient about their symptoms and give advice.",
        "Shopping": "You are a shop assistant. Help the customer find and buy what they need.",
        "Airport": "You are an airline check-in agent. Help the passenger with their flight."
    }
    selected_scenario = st.selectbox("Choose a scenario:", list(scenarios.keys()), key="scenario_select")
    
    if st.button("🎭 Start Practice", use_container_width=True):
        st.session_state.current_mode = "conversation"
        st.session_state.practice_scenario = selected_scenario
        st.session_state.messages = []  # Fresh conversation for the scenario
        scenario_desc = scenarios[selected_scenario]
        with st.spinner("Setting up the scenario..."):
            result = st.session_state.agent.process_query(
                f"Start a conversation practice. Scenario: {selected_scenario}. {scenario_desc} "
                f"Begin naturally as your character. Keep your first message short (2-3 sentences). Do NOT break character.",
                intent_override="conversation"
            )
            # Generate TTS for initial message
            audio_bytes = None
            try:
                from gtts import gTTS
                import io
                tts = gTTS(text=result["response"], lang='en', slow=False)
                fp = io.BytesIO()
                tts.write_to_fp(fp)
                audio_bytes = fp.getvalue()
            except Exception as e:
                st.error(f"TTS Setup Error: {e}")
                
            st.session_state.messages.append({
                "role": "assistant", 
                "content": result["response"], 
                "intent": "CONVERSATION",
                "audio": audio_bytes
            })
        st.rerun()

    st.markdown("---")
    if st.button("🔄 Free Input Mode", use_container_width=True):
        st.session_state.current_mode = "free"
        st.session_state.practice_scenario = None
        st.session_state.messages.append({"role": "assistant", "content": "Free input mode activated! The agent will automatically detect your intent.", "intent": "CONVERSATION"})
        st.rerun()

    if st.button("8️⃣ View Agent Architecture", use_container_width=True):
        st.session_state.show_arch = True
        st.session_state.show_stats = False
        
    if st.button("9️⃣ View Session Statistics", use_container_width=True):
        st.session_state.show_stats = True
        st.session_state.show_arch = False

    if st.button("🗑️ Clear Chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

    st.markdown("---")
    st.markdown("### 📷 Handwritten OCR")
    uploaded_file = st.file_uploader("Upload handwritten digits", type=["png", "jpg", "jpeg"])
    
    @st.cache_resource
    def get_ocr_reader():
        try:
            return easyocr.Reader(['en'], gpu=False) # GPU False for stability in diverse envs
        except Exception as e:
            st.error(f"OCR Initialization Error: {e}")
            return None

    if uploaded_file:
        st.image(uploaded_file, caption="Uploaded Image", use_container_width=True)
        digit_only = st.checkbox("🔢 Digit Only Mode", value=False)
        
        # We store the OCR text in session state to show it in the main area
        with st.spinner("🔍 Reading handwriting..."):
            image = Image.open(uploaded_file)
            reader = get_ocr_reader()
            if reader:
                try:
                    allowlist = '0123456789' if digit_only else None
                    # Use detailed mode to get coordinates for spatial sorting
                    ocr_results = reader.readtext(np.array(image), detail=1, paragraph=False, allowlist=allowlist)
                    
                    # Sort results: primary by Y-coordinate (top-to-bottom), secondary by X (left-to-right)
                    # We group items with similar Y (within a threshold) to handle slanted handwriting
                    ocr_results.sort(key=lambda x: x[0][0][1]) # Sort by top-left Y
                    
                    lines = []
                    current_line = []
                    last_y = -1
                    y_threshold = 20 # Group words within 20px of each other vertically
                    
                    for res in ocr_results:
                        bbox, text, prob = res
                        y = bbox[0][1]
                        if last_y == -1 or abs(y - last_y) < y_threshold:
                            current_line.append((bbox[0][0], text))
                        else:
                            # Finish previous line
                            current_line.sort(key=lambda x: x[0]) # Sort line left-to-right
                            lines.append(" ".join([t for x, t in current_line]))
                            current_line = [(bbox[0][0], text)]
                        last_y = y
                    
                    if current_line:
                        current_line.sort(key=lambda x: x[0])
                        lines.append(" ".join([t for x, t in current_line]))
                        
                    st.session_state.ocr_transcript = "\n".join(lines)
                except Exception as e:
                    st.error(f"OCR Error: {e}")
            else:
                st.error("OCR Reader could not be initialized.")
    else:
        st.session_state.ocr_transcript = None

# Main Area - OCR Interaction (If image uploaded)
if st.session_state.get("ocr_transcript"):
    with st.container():
        st.markdown("""
        <div style="background: rgba(255, 255, 255, 0.1); padding: 20px; border-radius: 15px; border: 1px solid rgba(255, 255, 255, 0.2); margin-bottom: 20px;">
            <h3 style="margin-top: 0;">📄 OCR Detection Results</h3>
        </div>
        """, unsafe_allow_html=True)
        
        with st.expander("🔍 View Raw Transcript", expanded=False):
            st.code(st.session_state.ocr_transcript)
        
        col_chat, col_reformat = st.columns(2)
        with col_chat:
            if st.button("💬 Chat about this Image", key="ocr_chat_btn", use_container_width=True, type="secondary"):
                st.session_state.messages.append({"role": "user", "content": f"I uploaded an image with this text: '{st.session_state.ocr_transcript}'. Can you explain it?"})
                st.session_state.ocr_transcript = None # Clear after action
                st.rerun()
        with col_reformat:
            if st.button("✨ Professional Reformat", key="ocr_reformat_btn", use_container_width=True, type="primary"):
                st.session_state.messages.append({"role": "user", "content": f"I have an OCR transcript of an assignment: '{st.session_state.ocr_transcript}'. Please reformat this into a professional, structured document with clean Markdown tables, headings, and a summary of the results. Fix any typos from the OCR process."})
                st.session_state.ocr_transcript = None # Clear after action
                st.rerun()

# Architecture View
if st.session_state.get("show_arch"):
    with st.container():
        st.markdown("""
        <div style="background: #f8f9fa; padding: 30px; border-radius: 15px; border: 1px solid #dee2e6; margin-bottom: 25px;">
            <h1 style="margin:0; color: #343a40;">🏗️ AGENT ARCHITECTURE</h1>
            <div style="background: #e7f3ff; padding: 15px; border-radius: 10px; margin-top: 20px; border-left: 5px solid #007bff;">
                <h4 style="margin:0; color: #0056b3;">📋 INTELLIGENT ROUTING SYSTEM</h4>
                <p style="margin: 10px 0 0 0; color: #004085;"><b>PLANNER MODULE:</b> Analyzes user queries → Routes to appropriate specialized tools → Combines results → Delivers comprehensive responses</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("### 🔧 5 SPECIALIZED TOOLS")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            <div style="background: #fdfdfd; padding: 20px; border-radius: 12px; border: 1px solid #eee; margin-bottom: 20px; box-shadow: 0 4px 6px rgba(0,0,0,0.02);">
                <h4 style="color: #007bff;">1️⃣ 📝 Grammar Handler</h4>
                <p style="background: #e6fffa; padding: 8px; border-radius: 5px; color: #2c7a7b; font-size: 0.9rem;"><b>LLM:</b> Groq Llama 3.3-70B</p>
                <p style="background: #f0fff4; padding: 8px; border-radius: 5px; color: #2f855a; font-size: 0.9rem;"><b>RAG:</b> ✓ Grammar Knowledge Base</p>
                <p style="font-size: 0.85rem; color: #718096; margin-top: 10px;">💡 Explains grammar rules, tenses, and structures with examples.</p>
            </div>
            
            <div style="background: #fdfdfd; padding: 20px; border-radius: 12px; border: 1px solid #eee; margin-bottom: 20px; box-shadow: 0 4px 6px rgba(0,0,0,0.02);">
                <h4 style="color: #667eea;">3️⃣ 🌐 Translation Engine</h4>
                <p style="background: #ebf8ff; padding: 8px; border-radius: 5px; color: #2b6cb0; font-size: 0.9rem;"><b>Engine:</b> Deep Learning Neural Translation</p>
                <p style="background: #fff5f5; padding: 8px; border-radius: 5px; color: #c53030; font-size: 0.9rem;"><b>Languages:</b> Arabic, German, French, etc.</p>
                <p style="font-size: 0.85rem; color: #718096; margin-top: 10px;">🌍 Real-time multi-language translation and context awareness.</p>
            </div>
            """, unsafe_allow_html=True)
            
        with col2:
            st.markdown("""
            <div style="background: #fdfdfd; padding: 20px; border-radius: 12px; border: 1px solid #eee; margin-bottom: 20px; box-shadow: 0 4px 6px rgba(0,0,0,0.02);">
                <h4 style="color: #ed8936;">2️⃣ 📚 Vocabulary Handler</h4>
                <p style="background: #e6fffa; padding: 8px; border-radius: 5px; color: #2c7a7b; font-size: 0.9rem;"><b>LLM:</b> Groq Llama 3.1-8B</p>
                <p style="background: #f0fff4; padding: 8px; border-radius: 5px; color: #2f855a; font-size: 0.9rem;"><b>RAG:</b> ✓ Vocabulary KB</p>
                <p style="font-size: 0.85rem; color: #718096; margin-top: 10px;">📖 Defines words with translations, synonyms, and usage examples.</p>
            </div>
            
            <div style="background: #fdfdfd; padding: 20px; border-radius: 12px; border: 1px solid #eee; margin-bottom: 20px; box-shadow: 0 4px 6px rgba(0,0,0,0.02);">
                <h4 style="color: #9f7aea;">4️⃣ 🎯 Quiz Generator</h4>
                <p style="background: #faf5ff; padding: 8px; border-radius: 5px; color: #6b46c1; font-size: 0.9rem;"><b>LLM:</b> Dynamic Context Generator</p>
                <p style="background: #fffaf0; padding: 8px; border-radius: 5px; color: #9c4221; font-size: 0.9rem;"><b>Format:</b> Interactive MCQ</p>
                <p style="font-size: 0.85rem; color: #718096; margin-top: 10px;">📝 Creates personalized assessment quizzes based on session progress.</p>
            </div>

            <div style="background: #fdfdfd; padding: 20px; border-radius: 12px; border: 1px solid #eee; margin-bottom: 20px; box-shadow: 0 4px 6px rgba(0,0,0,0.02);">
                <h4 style="color: #48bb78;">6️⃣ ✍️ Handwriting OCR</h4>
                <p style="background: #f0fff4; padding: 8px; border-radius: 5px; color: #2f855a; font-size: 0.9rem;"><b>Engine:</b> EasyOCR + Torch</p>
                <p style="background: #e6fffa; padding: 8px; border-radius: 5px; color: #2c7a7b; font-size: 0.9rem;"><b>Feature:</b> Digit-Only Mode</p>
                <p style="font-size: 0.85rem; color: #718096; margin-top: 10px;">📄 Converts handwritten notes and assignments into structured text.</p>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("""
        <div style="background: #fff5f5; padding: 20px; border-radius: 12px; border-left: 5px solid #f56565; margin-top: 10px;">
            <h4 style="margin:0; color: #c53030;">🧠 MULTI-MODEL INTELLIGENCE</h4>
            <p style="margin: 10px 0 0 0; color: #9b2c2c;">The agent dynamically switches between <b>Llama 3.3-70B</b> for complex analysis and <b>Llama 3.1-8B</b> for real-time interaction to balance speed and intelligence.</p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("---")
        if st.button("Close Architecture", use_container_width=True):
            st.session_state.show_arch = False
            st.rerun()

# Statistics View
if st.session_state.get("show_stats"):
    with st.container():
        st.markdown("""
        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 30px; border-radius: 15px; color: white; margin-bottom: 25px; box-shadow: 0 10px 20px rgba(0,0,0,0.1);">
            <h1 style="margin:0; color: white;">📊 SESSION STATISTICS</h1>
            <p style="opacity: 0.9;">Your learning journey at a glance</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Calculate stats
        assistant_msgs = [m for m in st.session_state.messages if m["role"] == "assistant"]
        total_queries = len(assistant_msgs)
        avg_confidence = sum([m.get("confidence", 0.9) for m in assistant_msgs]) / max(total_queries, 1) * 100
        
        duration = get_duration()
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("⏱️ Duration", f"{duration} min")
        with col2:
            st.metric("🎯 Queries", total_queries)
        with col3:
            st.metric("🔧 Tools", len(set([m.get("intent", "CONVERSATION") for m in assistant_msgs])))
        with col4:
            st.metric("⚡ Queries/Min", round(total_queries/duration, 1) if duration > 0 else 0)

        st.markdown("### 📈 Average Confidence Score")
        st.progress(avg_confidence / 100)
        st.write(f"**{avg_confidence:.1f}%**")

        st.markdown("### 🔧 Tool Usage Breakdown")
        from collections import Counter
        counts = Counter([m.get("intent", "CONVERSATION").upper() for m in assistant_msgs])
        
        for tool, count in counts.items():
            st.write(f"**{tool}:** {count} uses")
            st.progress(min(count / 10, 1.0)) # Scale to 10 uses max for visual

        st.markdown("---")
        col_btn1, col_btn2 = st.columns(2)
        with col_btn1:
            if st.button("📧 Email Session Report", key="email_session_stats", use_container_width=True, type="primary"):
                from utils.email_helper import send_feedback_email
                from utils.email_templates import get_premium_report_html
                import datetime
                
                timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                body = get_premium_report_html("Student", duration, total_queries, avg_confidence, counts)
                
                success, msg = send_feedback_email(f"Learning Session Summary [{timestamp}]", body)
                if success: st.success("Report emailed successfully! 🚀")
                else: st.error(msg)
        with col_btn2:
            if st.button("Close Statistics", use_container_width=True):
                st.session_state.show_stats = False
                st.rerun()

# Main UI Title
st.markdown('<h1 style="text-align: center; color: #e040fb; text-shadow: 2px 2px 4px rgba(0,0,0,0.3); font-size: 2.8rem;">🎓 English Language Learning Agent 🚀</h1>', unsafe_allow_html=True)
st.markdown('<p style="text-align: center; color: #7c4dff; font-size: 1.5rem; text-shadow: 1px 1px 2px rgba(0,0,0,0.2);">Master English with your AI Assistant! 🧠✨</p>', unsafe_allow_html=True)

# Conversation Practice Banner
if st.session_state.current_mode == "conversation" and st.session_state.practice_scenario:
    scenario = st.session_state.practice_scenario
    scenario_icons = {"Free Chat": "💬", "At a Cafe": "☕", "Job Interview": "💼", "Hotel Check-in": "🏨", "Doctor Visit": "🏥", "Shopping": "🛍️", "Airport": "✈️"}
    icon = scenario_icons.get(scenario, "💬")
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, #fa709a 0%, #fee140 100%); padding: 15px 25px; border-radius: 12px; margin-bottom: 20px; text-align: center;">
        <span style="font-size: 1.8rem;">{icon}</span>
        <span style="color: white; font-size: 1.3rem; font-weight: 700; margin-left: 10px;">Conversation Practice: {scenario}</span>
        <p style="color: rgba(255,255,255,0.9); margin: 5px 0 0 0; font-size: 0.95rem;">Speak naturally! The AI will correct your mistakes inline.</p>
    </div>
    """, unsafe_allow_html=True)

# Helper for Quiz
def render_interactive_quiz(content, msg_index):
    import json
    import re
    import ast
    
    # Robust JSON extraction
    json_match = re.search(r'(\{.*\}|\[.*\])', content, re.DOTALL)
    if not json_match:
        st.markdown(content)
        return

    try:
        # Robust JSON extraction
        json_match = re.search(r'(\{.*\}|\[.*\])', content, re.DOTALL)
        if not json_match:
            st.markdown(content)
            return

        json_str = json_match.group(1)
        # Multi-stage parsing attempt
        try:
            # Stage 1: Standard JSON
            raw_data = json.loads(json_str)
        except json.JSONDecodeError as e1:
            try:
                # Stage 2: Clean trailing commas (common LLM error)
                json_str_clean = re.sub(r',\s*([\]}])', r'\1', json_str)
                # Clean unescaped newlines within strings
                json_str_clean = re.sub(r'(?<!\\)\n', ' ', json_str_clean)
                raw_data = json.loads(json_str_clean)
            except json.JSONDecodeError as e2:
                try:
                    # Stage 3: Python AST evaluation (handles single quotes as string delimiters)
                    raw_data = ast.literal_eval(json_str)
                except Exception as e3:
                    st.error(f"Failed to parse quiz data. Error: {e1}")
                    st.code(json_str)
                    return
        
        quiz_data = raw_data if isinstance(raw_data, list) else raw_data.get("questions", [])
        
        # Normalize quiz data (Handle A, B, C, D keys)
        normalized_data = []
        for q in quiz_data:
            if "options" not in q:
                # Extract options from keys A, B, C, D
                opts = []
                for k in ["A", "B", "C", "D"]:
                    if k in q: opts.append(q[k])
                q["options"] = opts
            
            # Normalize answer (if it's "A", "B" etc., get the text)
            if "answer" in q and q["answer"] in ["A", "B", "C", "D"]:
                ans_key = q["answer"]
                q["answer"] = q.get(ans_key, q["answer"])
            elif "correct" in q and q["correct"] in ["A", "B", "C", "D"]:
                ans_key = q["correct"]
                q["correct"] = q.get(ans_key, q["correct"])
                
            normalized_data.append(q)
        
        quiz_data = normalized_data
        
        # Enforce exact requested count by checking the previous user message
        try:
            if msg_index > 0:
                user_msg = st.session_state.messages[msg_index-1]["content"]
                match = re.search(r'\b(10|[1-9])\b\s*-?\s*q', user_msg, re.IGNORECASE)
                if not match: match = re.search(r'\b(10|[1-9])\b', user_msg)
                if match:
                    req_count = int(match.group(1))
                    if len(quiz_data) > req_count:
                        quiz_data = quiz_data[:req_count]
        except Exception:
            pass
        
        if not quiz_data:
            st.warning("No questions found in the quiz data.")
            st.markdown(content)
            return

        # Initialize quiz state for this specific message
        quiz_key = f"quiz_state_{msg_index}"
        if quiz_key not in st.session_state:
            st.session_state[quiz_key] = {
                "current_idx": 0,
                "score": 0,
                "answered": False,
                "selected_ans": None,
                "finished": False
            }
        
        state = st.session_state[quiz_key]
        
        if state["finished"]:
            st.markdown(f"### 🏁 Quiz Results")
            st.success(f"## Your Score: {state['score']}/{len(quiz_data)} ({(state['score']/len(quiz_data))*100:.1f}%)")
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("📧 Email Results", key=f"email_{msg_index}", use_container_width=True):
                    from utils.email_helper import send_feedback_email
                    from utils.email_templates import get_quiz_report_html
                    import datetime
                    
                    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    percentage = (state['score'] / len(quiz_data)) * 100
                    body = get_quiz_report_html("Student", state['score'], len(quiz_data), percentage)
                    
                    success, msg = send_feedback_email(f"Interactive Quiz Results [{timestamp}]", body)
                    if success: st.success("Results sent! 🚀")
                    else: st.error(msg)
            with col2:
                if st.button("🔄 Restart Quiz", key=f"restart_{msg_index}", use_container_width=True):
                    del st.session_state[quiz_key]
                    st.rerun()
            return

        current_q = quiz_data[state["current_idx"]]
        st.markdown(f"### 📝 Question {state['current_idx'] + 1} of {len(quiz_data)}")
        st.markdown(f"#### {current_q['question']}")
        
        # Determine correct answer key (handle both 'answer' and 'correct')
        correct_answer = current_q.get('answer') or current_q.get('correct')
        
        # Render options as buttons with premium styling
        for opt in current_q['options']:
            if not state["answered"]:
                if st.button(opt, key=f"opt_{msg_index}_{state['current_idx']}_{opt}", use_container_width=True):
                    state["answered"] = True
                    state["selected_ans"] = opt
                    if opt == correct_answer:
                        state["score"] += 1
                    st.rerun()
            else:
                # Show feedback
                is_correct = (opt == correct_answer)
                is_selected = (opt == state["selected_ans"])
                
                if is_correct:
                    st.markdown(f'<div style="background-color: rgba(76, 175, 80, 0.2); padding: 10px; border-radius: 5px; border-left: 5px solid #4CAF50; margin-bottom: 10px; color: #2e7d32;">✅ <b>{opt}</b> (Correct)</div>', unsafe_allow_html=True)
                elif is_selected:
                    st.markdown(f'<div style="background-color: rgba(244, 67, 54, 0.2); padding: 10px; border-radius: 5px; border-left: 5px solid #F44336; margin-bottom: 10px; color: #c62828;">❌ <b>{opt}</b> (Incorrect)</div>', unsafe_allow_html=True)
                    st.markdown(f'<div style="background-color: rgba(33, 150, 243, 0.1); padding: 10px; border-radius: 5px; border-left: 5px solid #2196F3; color: #1565c0;">💡 <b>Correct Answer:</b> {correct_answer}</div>', unsafe_allow_html=True)
                else:
                    st.button(opt, key=f"opt_dis_{msg_index}_{state['current_idx']}_{opt}", disabled=True, use_container_width=True)

        if state["answered"]:
            st.markdown("---")
            if state["current_idx"] < len(quiz_data) - 1:
                if st.button("➡️ Next Question", key=f"next_{msg_index}", type="primary", use_container_width=True):
                    state["current_idx"] += 1
                    state["answered"] = False
                    state["selected_ans"] = None
                    st.rerun()
            else:
                if st.button("🏁 View Final Score", key=f"finish_{msg_index}", type="primary", use_container_width=True):
                    state["finished"] = True
                    st.rerun()
                    
    except Exception as e:
        st.error(f"Error parsing quiz: {e}")
        st.markdown(content)

# Chat Display
chat_container = st.container()
with chat_container:
    for idx, msg in enumerate(st.session_state.messages):
        if msg["role"] == "user":
            st.markdown(f'<div class="chat-message user-message"><strong>👤 You:</strong><br>{msg["content"]}</div>', unsafe_allow_html=True)
        else:
            intent = msg.get("intent", "CONVERSATION").upper()
            confidence = msg.get("confidence", 0.9)
            
            badge_colors = {
                'GRAMMAR': 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                'VOCABULARY': 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)',
                'TRANSLATION': 'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)',
                'CONVERSATION': 'linear-gradient(135deg, #fa709a 0%, #fee140 100%)',
                'QUIZ': 'linear-gradient(135deg, #43e97b 0%, #38f9d7 100%)'
            }
            badge_color = badge_colors.get(intent, 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)')
            
            with st.container():
                st.markdown(f"""
                <div class="chat-message bot-message">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
                        <strong>🤖 Agent</strong>
                        <div>
                            <span style="background: {badge_color}; color: white; padding: 5px 12px; border-radius: 15px; font-size: 12px; margin-right: 5px;">{intent}</span>
                            <span style="background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%); color: white; padding: 5px 12px; border-radius: 15px; font-size: 12px;">{confidence:.0%}</span>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                if intent == 'QUIZ':
                    render_interactive_quiz(msg["content"], idx)
                else:
                    st.markdown(f'<div class="bot-message" style="margin-top: -1.5rem; box-shadow: none; border-left: none;">{msg["content"]}</div>', unsafe_allow_html=True)
                    if msg.get("audio"):
                        # Autoplay only if it's the very last message in the chat
                        is_latest = (idx == len(st.session_state.messages) - 1)
                        st.audio(msg["audio"], format="audio/mp3", autoplay=is_latest)

# Input area
with st.container():
    # Voice Input (Professional direct STT)
    from streamlit_mic_recorder import speech_to_text
    
    col_voice, col_space = st.columns([1, 4])
    with col_voice:
        st.markdown("🎙️ **Voice:**")
    
    # This component returns the text directly!
    text_from_voice = speech_to_text(
        language='en',
        start_prompt="Start Speaking ⏺️",
        stop_prompt="Stop & Process ⏹️",
        just_once=True,
        key='speech_to_text'
    )
    
    if text_from_voice:
        st.session_state.voice_text = text_from_voice
        st.info(f"Detected: {text_from_voice}")

    with st.form(key='chat_form', clear_on_submit=True):
        col1, col2 = st.columns([5, 1])
        with col1:
            # Check if there is voice text to pre-fill
            default_val = st.session_state.get("voice_text", "")
            user_input = st.text_input(
                "💬 Your message:",
                value=default_val,
                placeholder="Ask anything... (e.g., 'Explain present perfect', 'Quiz on conditionals', 'Translate hello to Arabic')",
                label_visibility="collapsed"
            )
                
        with col2:
            send_button = st.form_submit_button("Send ➤", use_container_width=True)

        if (send_button and user_input):
            # Clear voice text now that it's being used
            if st.session_state.get("voice_text"):
                st.session_state.voice_text = ""
                
            st.session_state.messages.append({"role": "user", "content": user_input})
            
            with st.spinner("Processing..."):
                # Use mode override if in specific test mode
                intent_override = None
                if st.session_state.current_mode != "free":
                    intent_override = st.session_state.current_mode
                
                # Process query
                result = st.session_state.agent.process_query(user_input, intent_override=intent_override)
                
                # Generate TTS audio for conversation practice
                audio_bytes = None
                if result["intent"].upper() == "CONVERSATION":
                    try:
                        from gtts import gTTS
                        import io
                        import re
                        # Don't speak the bracketed tips
                        clean_text = re.sub(r'\[Tip:.*?\]', '', result["response"]).strip()
                        if clean_text:
                            tts = gTTS(text=clean_text, lang='en', slow=False)
                            fp = io.BytesIO()
                            tts.write_to_fp(fp)
                            audio_bytes = fp.getvalue()
                    except Exception as e:
                        st.error(f"Failed to generate AI Voice: {e}")
                
                # Store in messages
                st.session_state.messages.append({
                    "role": "assistant", 
                    "content": result["response"],
                    "intent": result["intent"],
                    "confidence": result["confidence"],
                    "audio": audio_bytes
                })
                
            st.rerun()

# Footer
st.markdown("---")
st.markdown('<p style="text-align: center; color: #e040fb; font-size: 1.2rem; text-shadow: 1px 1px 2px rgba(0,0,0,0.3);">🚀 Powered by: Asser Almasry | AI Engineer 💻 @all rights saved 📜✨</p>', unsafe_allow_html=True)
