'use client';

import { useState, useEffect, useRef } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import QuizRenderer from './components/QuizRenderer';

// Configurable API URL: empty string forces relative URLs (e.g. /api/chat) 
// so NGINX can correctly reverse proxy the requests to the backend.
const API_URL = process.env.NEXT_PUBLIC_API_URL || '';
const API_KEY = process.env.NEXT_PUBLIC_API_KEY || '';
const AUTH_HEADERS = { 'Content-Type': 'application/json', 'X-API-Key': API_KEY };


type Message = {
  role: 'user' | 'assistant';
  content: string;
  intent?: string;
  audio?: string;
  isQuiz?: boolean;
  quizData?: any;
};

export default function Home() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [sessionId, setSessionId] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [scenario, setScenario] = useState('Free Chat');
  const [ocrResult, setOcrResult] = useState<string | null>(null);
  const [view, setView] = useState<'chat' | 'stats' | 'arch'>('chat');
  
  const [quizTopic, setQuizTopic] = useState('');
  const [quizCount, setQuizCount] = useState(5);
  const [isListening, setIsListening] = useState(false);
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);

  const messagesEndRef = useRef<HTMLDivElement>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const audioChunksRef = useRef<Blob[]>([]);


  const scenarios = {
    "Free Chat": "Have a friendly casual conversation in English about any topic the user wants.",
    "At a Cafe": "You are a barista at a coffee shop. Greet the customer and take their order naturally.",
    "Job Interview": "You are an HR interviewer for a tech company. Conduct a professional job interview.",
    "Hotel Check-in": "You are a hotel receptionist. Help the guest check in and answer questions about the hotel.",
    "Doctor Visit": "You are a doctor. Ask the patient about their symptoms and give advice.",
    "Shopping": "You are a shop assistant. Help the customer find and buy what they need.",
    "Airport": "You are an airline check-in agent. Help the passenger with their flight."
  };

  const scenarioIcons = {
    "Free Chat": "💬", "At a Cafe": "☕", "Job Interview": "💼", 
    "Hotel Check-in": "🏨", "Doctor Visit": "🏥", "Shopping": "🛍️", "Airport": "✈️"
  };

  useEffect(() => {
    setSessionId(Date.now().toString());
    setMessages([{ role: 'assistant', content: 'Hello! I am your Intelligent Language Learning Agent. How can I help you today?' }]);
  }, []);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const sendMessage = async (overrideMsg?: string, intentOverride?: string) => {
    const textToSend = overrideMsg || input;
    if (!textToSend.trim()) return;

    if (!overrideMsg) {
      setMessages((prev) => [...prev, { role: 'user', content: textToSend }]);
      setInput('');
    }
    
    setIsLoading(true);
    setView('chat');

    try {
      const res = await fetch(`${API_URL}/api/chat`, {
        method: 'POST',
        headers: AUTH_HEADERS,
        body: JSON.stringify({
          session_id: sessionId,
          message: textToSend,
          intent_override: intentOverride
        })
      });

      const data = await res.json();
      
      let isQuiz = false;
      let quizData = null;
      
      if (data.intent === 'quiz') {
        try {
          const jsonMatch = data.response.match(/(\{.*\}|\[.*\])/s);
          if (jsonMatch) {
            quizData = JSON.parse(jsonMatch[1]);
            if (quizData.questions) quizData = quizData.questions;
            isQuiz = true;
          }
        } catch (e) {
          console.error("Quiz Parse Error:", e);
        }
      }

      setMessages((prev) => [...prev, { 
        role: 'assistant', 
        content: data.response,
        intent: data.intent,
        isQuiz,
        quizData: quizData ? { questions: quizData } : null
      }]);
    } catch (error) {
      console.error(error);
      setMessages((prev) => [...prev, { role: 'assistant', content: 'Sorry, I encountered an error connecting to the server.' }]);
    } finally {
      setIsLoading(false);
    }
  };

  const startConversationPractice = () => {
    const scenarioDesc = scenarios[scenario as keyof typeof scenarios];
    const msg = `Start a conversation practice. Scenario: ${scenario}. ${scenarioDesc} Begin naturally as your character. Keep your first message short (2-3 sentences). Do NOT break character.`;
    setMessages([]);
    sendMessage(msg, 'conversation');
  };

  const handleCustomQuiz = () => {
    const topicText = quizTopic.trim() ? ` on ${quizTopic}` : "";
    const msg = `Give me a quiz${topicText} with ${quizCount} questions.`;
    setMessages((prev) => [...prev, { role: 'user', content: `[Custom Quiz Request: ${quizCount} questions${topicText}]` }]);
    sendMessage(msg, "quiz");
  };

  const handleTestMode = (mode: string, text: string) => {
    setMessages((prev) => [...prev, { role: 'assistant', content: `${mode.toUpperCase()} mode activated! ${text}`, intent: mode.toUpperCase() }]);
    setView('chat');
  };

  const clearChat = async () => {
    setMessages([{ role: 'assistant', content: 'Chat cleared. How can I help you?' }]);
    setView('chat');
    try {
      await fetch(`${API_URL}/api/session/reset`, {
        method: 'POST',
        headers: AUTH_HEADERS,
        body: JSON.stringify({ session_id: sessionId })
      });
    } catch (e) { console.error("Reset Error:", e); }
  };

  const playAudio = async (text: string) => {
    try {
      const res = await fetch(`${API_URL}/api/tts`, {
        method: 'POST',
        headers: AUTH_HEADERS,
        body: JSON.stringify({ text })
      });
      const blob = await res.blob();
      const url = URL.createObjectURL(blob);
      const audio = new Audio(url);
      audio.play();
    } catch (e) { console.error(e); }
  };

  const toggleListening = async () => {
    if (isListening) {
      if (mediaRecorderRef.current && mediaRecorderRef.current.state === "recording") {
        mediaRecorderRef.current.stop();
        setIsListening(false);
      }
      return;
    }

    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const mediaRecorder = new MediaRecorder(stream);
      mediaRecorderRef.current = mediaRecorder;
      audioChunksRef.current = [];

      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          audioChunksRef.current.push(event.data);
        }
      };

      mediaRecorder.onstop = async () => {
        const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/webm' });
        const formData = new FormData();
        formData.append('file', audioBlob, 'recording.webm');

        try {
          const response = await fetch(`${API_URL}/api/stt`, {
            method: 'POST',
            headers: { 'X-API-Key': API_KEY },
            body: formData,
          });
          const data = await response.json();
          if (data.text) {
            setInput((prev) => prev ? prev + ' ' + data.text : data.text);
          }
        } catch (err) {
          console.error("STT Fetch Error:", err);
          alert("Failed to transcribe audio. Please check your connection.");
        } finally {
          stream.getTracks().forEach(track => track.stop());
        }
      };

      mediaRecorder.start();
      setIsListening(true);
    } catch (err) {
      console.error("Microphone Access Error:", err);
      alert("Could not access microphone. Please check permissions.");
    }
  };

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    const formData = new FormData();
    formData.append('file', file);
    setIsLoading(true);
    try {
      const res = await fetch(`${API_URL}/api/ocr`, { method: 'POST', headers: { 'X-API-Key': API_KEY }, body: formData });
      const data = await res.json();
      setOcrResult(data.transcript);
    } catch (e) { console.error(e); }
    finally { setIsLoading(false); }
  };

  const handleOcrAction = (action: 'chat' | 'reformat') => {
    if (!ocrResult) return;
    const msg = action === 'chat' 
      ? `I uploaded an image with this text: '${ocrResult}'. Can you explain it?`
      : `I have an OCR transcript of an assignment: '${ocrResult}'. Please reformat this into a professional, structured document with clean Markdown tables, headings, and a summary of the results. Fix any typos from the OCR process.`;
    setMessages((prev) => [...prev, { role: 'user', content: msg }]);
    sendMessage(msg);
    setOcrResult(null);
  };

  const sendQuizEmail = async (score: number, total: number) => {
    try {
      await fetch(`${API_URL}/api/email/quiz`, {
        method: 'POST',
        headers: AUTH_HEADERS,
        body: JSON.stringify({ session_id: sessionId, score, total })
      });
    } catch (e) { console.error(e); }
  };

  const sendStatsEmail = async () => {
    setIsLoading(true);
    try {
      const res = await fetch(`${API_URL}/api/email/stats`, {
        method: 'POST',
        headers: AUTH_HEADERS,
        body: JSON.stringify({ session_id: sessionId })
      });
      if (res.ok) alert("Session report sent successfully! 🚀");
    } catch (e) { console.error(e); }
    finally { setIsLoading(false); }
  };

  return (
    <div className="flex h-screen bg-[#f8f9fa] overflow-hidden relative">
      {/* Sidebar Overlay for Mobile */}
      {isSidebarOpen && (
        <div 
          className="fixed inset-0 bg-black/50 z-40 md:hidden backdrop-blur-sm"
          onClick={() => setIsSidebarOpen(false)}
        />
      )}

      {/* Sidebar */}
      <div className={`
        fixed md:relative z-50 md:z-auto h-full bg-white border-r border-gray-200 
        overflow-y-auto shadow-sm custom-scrollbar transition-transform duration-300
        w-[280px] md:w-1/4 md:min-w-[340px] p-6
        ${isSidebarOpen ? 'translate-x-0' : '-translate-x-full md:translate-x-0'}
      `}>
        <div className="bg-green-50 text-green-800 p-3 rounded-lg border border-green-200 mb-6 font-medium flex items-center">
          <span className="mr-2">✅</span> 1781 documents loaded
        </div>

        <h3 className="text-lg font-bold mb-4 text-gray-800 flex items-center gap-2">
          <span className="text-xl">🎯</span> Available Tools
        </h3>
        <div className="grid grid-cols-2 gap-2 mb-6 text-center">
          <div className="tool-badge !m-0 !py-2 !px-1 text-xs font-bold text-white shadow-md bg-[linear-gradient(135deg,#667eea_0%,#764ba2_100%)]">1️⃣ Grammar</div>
          <div className="tool-badge !m-0 !py-2 !px-1 text-xs font-bold text-white shadow-md bg-[linear-gradient(135deg,#f093fb_0%,#f5576c_100%)]">2️⃣ Vocab</div>
          <div className="tool-badge !m-0 !py-2 !px-1 text-xs font-bold text-white shadow-md bg-[linear-gradient(135deg,#4facfe_0%,#00f2fe_100%)]">3️⃣ Translate</div>
          <div className="tool-badge !m-0 !py-2 !px-1 text-xs font-bold text-white shadow-md bg-[linear-gradient(135deg,#43e97b_0%,#38f9d7_100%)]">4️⃣ Quiz</div>
        </div>

        <hr className="my-6 border-gray-100" />
        
        <h3 className="text-lg font-bold mb-4 text-gray-800 flex items-center gap-2">
          <span className="text-xl">💡</span> Test Modes
        </h3>
        <div className="space-y-2 mb-6">
          <button className="action-btn !py-3 !text-sm" onClick={() => handleTestMode('grammar', "Try: 'Explain present perfect tense'")}>1️⃣ Test Grammar Handler</button>
          <button className="action-btn !py-3 !text-sm" onClick={() => handleTestMode('vocabulary', "Try: 'What does achieve mean?'")}>2️⃣ Test Vocabulary Handler</button>
          <button className="action-btn !py-3 !text-sm" onClick={() => handleTestMode('translation', "Try: 'Translate hello to Arabic'")}>3️⃣ Test Translation Tool</button>
          <button className="action-btn !py-3 !text-sm" onClick={() => handleTestMode('quiz', "Try: 'Give me a quiz on conditionals'")}>4️⃣ Test Interactive Quiz</button>
        </div>

        <hr className="my-6 border-gray-100" />

        <h3 className="text-lg font-bold mb-4 text-gray-800 flex items-center gap-2">
          <span className="text-xl">📝</span> Interactive Quiz Tools
        </h3>
        <div className="space-y-4">
          <div>
            <label className="block text-xs font-bold text-gray-400 uppercase mb-2">Quiz Topic</label>
            <input 
              type="text" placeholder="e.g. Present Perfect" value={quizTopic} onChange={(e) => setQuizTopic(e.target.value)}
              className="w-full p-3 border border-gray-200 rounded-xl outline-none focus:border-[#f5576c] transition-all"
            />
          </div>
          <div>
            <label className="block text-xs font-bold text-gray-400 uppercase mb-2">Number of Questions: {quizCount}</label>
            <input 
              type="range" min="1" max="10" step="1" value={quizCount} onChange={(e) => setQuizCount(parseInt(e.target.value))}
              className="w-full accent-[#f5576c]"
            />
          </div>
          <button className="action-btn !mt-2" onClick={handleCustomQuiz}>📝 Generate Custom Quiz</button>
        </div>

        <hr className="my-6 border-gray-100" />

        <h3 className="text-lg font-bold mb-4 text-gray-800 flex items-center gap-2">
          <span className="text-xl">🗣️</span> Conversation Practice
        </h3>
        <select 
          value={scenario} onChange={(e) => setScenario(e.target.value)}
          className="w-full p-3 border border-gray-300 rounded-lg mb-4 focus:ring-2 focus:ring-[#f5576c] outline-none"
        >
          {Object.keys(scenarios).map(s => <option key={s}>{s}</option>)}
        </select>
        <button className="action-btn bg-gradient-to-r from-[#fa709a] to-[#fee140]" onClick={startConversationPractice}>🎭 Start Practice</button>
        
        <div className="grid grid-cols-2 gap-2 mt-4">
          <button className="action-btn !bg-blue-500 !p-3 text-sm" onClick={() => setView('arch')}>🏗️ Architecture</button>
          <button className="action-btn !bg-indigo-500 !p-3 text-sm" onClick={() => setView('stats')}>📈 Statistics</button>
        </div>

        <button className="action-btn bg-gray-200 !text-gray-700 !shadow-none hover:bg-gray-300 mt-4" onClick={clearChat}>🗑️ Clear Chat</button>

        <hr className="my-6 border-gray-100" />
        
        <h3 className="text-lg font-bold mb-4 text-gray-800 flex items-center gap-2">
          <span className="text-xl">📷</span> Handwritten OCR
        </h3>
        <input type="file" ref={fileInputRef} onChange={handleFileUpload} className="hidden" accept="image/*" />
        <button className="w-full p-4 border-2 border-dashed border-gray-300 rounded-xl text-gray-500 hover:border-[#f5576c] hover:text-[#f5576c] transition-all" onClick={() => fileInputRef.current?.click()}>Upload handwritten image</button>
      </div>

      {/* Main Area */}
      <div className="flex-1 flex flex-col h-full overflow-hidden relative">
        {/* Header */}
        <div className="main-gradient p-4 md:p-8 text-white shadow-md flex justify-between items-center z-10">
          <div className="flex items-center gap-4">
            <button 
              onClick={() => setIsSidebarOpen(!isSidebarOpen)}
              className="p-2 bg-white/20 rounded-lg md:hidden hover:bg-white/30 transition-all"
            >
              {isSidebarOpen ? '✕' : '☰'}
            </button>
            <div>
              <h1 className="text-xl md:text-3xl font-bold mb-0 md:mb-2 leading-tight">AI Language Agent</h1>
              <p className="hidden md:block opacity-90 text-lg">Your personal AI tutor for English mastery</p>
            </div>
          </div>
          {view !== 'chat' && <button onClick={() => setView('chat')} className="bg-white/20 hover:bg-white/30 px-4 py-2 md:p-3 rounded-xl backdrop-blur-md transition-all font-bold text-sm md:text-base">🔙 Back</button>}
        </div>

        <div className="flex-1 overflow-y-auto bg-gray-50 custom-scrollbar">
          {view === 'chat' && (
            <div className="p-8 max-w-5xl mx-auto min-h-full flex flex-col">
              <div className="flex-1">
                {/* Practice Banner */}
                {scenario !== "Free Chat" && (
                  <div className="bg-gradient-to-r from-[#fa709a] to-[#fee140] p-6 rounded-2xl mb-8 text-center text-white shadow-xl animate-in slide-in-from-top duration-500">
                    <span className="text-4xl mb-2 block">{scenarioIcons[scenario as keyof typeof scenarioIcons]}</span>
                    <h2 className="text-2xl font-bold">Conversation Practice: {scenario}</h2>
                    <p className="opacity-90 mt-1">Speak naturally! The AI will correct your mistakes inline.</p>
                  </div>
                )}

                {/* OCR Result Overlay */}
                {ocrResult && (
                  <div className="mb-8 p-6 bg-white rounded-2xl shadow-xl border border-gray-200 animate-in slide-in-from-top duration-300">
                    <h3 className="text-xl font-bold mb-4 text-gray-800">📄 OCR Detection Results</h3>
                    <pre className="bg-gray-50 p-4 rounded-lg text-sm overflow-x-auto mb-6 max-h-40">{ocrResult}</pre>
                    <div className="flex gap-4">
                      <button className="flex-1 py-3 bg-gray-100 text-gray-700 rounded-xl font-bold hover:bg-gray-200 transition-all" onClick={() => handleOcrAction('chat')}>💬 Chat about Image</button>
                      <button className="flex-1 py-3 bg-[#f5576c] text-white rounded-xl font-bold hover:opacity-90 transition-all shadow-lg shadow-[#f5576c]/30" onClick={() => handleOcrAction('reformat')}>✨ Professional Reformat</button>
                    </div>
                  </div>
                )}

                {messages.map((msg, idx) => (
                  <div key={idx} className={`chat-message ${msg.role === 'user' ? 'user-message' : 'bot-message relative'}`}>
                    <div className="flex items-center justify-between mb-2">
                      <div className="flex items-center">
                        <span className="font-bold mr-2 text-lg">{msg.role === 'user' ? '👤 You' : '🤖 Agent'}</span>
                        {msg.intent && (
                          <span className="tool-badge bg-gray-100 text-gray-600 border border-gray-200 !m-0 !py-1 !px-3 text-xs uppercase">{msg.intent}</span>
                        )}
                      </div>
                      {msg.role === 'assistant' && !msg.isQuiz && (
                        <button onClick={() => playAudio(msg.content)} className="p-2 rounded-full hover:bg-gray-100 text-gray-400 hover:text-[#f5576c] transition-all">🔊</button>
                      )}
                    </div>
                    {msg.isQuiz ? <QuizRenderer data={msg.quizData} onComplete={sendQuizEmail} /> : 
                      <div className="markdown-content"><ReactMarkdown remarkPlugins={[remarkGfm]}>{msg.content}</ReactMarkdown></div>}
                  </div>
                ))}
                {isLoading && <div className="chat-message bot-message flex items-center gap-2"><div className="flex gap-1"><div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div><div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce delay-75"></div><div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce delay-150"></div></div></div>}
                <div ref={messagesEndRef} />
              </div>
              
              {/* Footer */}
              <div className="mt-12 mb-4 text-center border-t border-gray-200 pt-8 pb-4">
                <p className="text-[1.2rem] font-bold text-[#e040fb] [text-shadow:1px_1px_2px_rgba(0,0,0,0.3)] flex items-center justify-center gap-2">
                  🚀 Powered by: Asser Almasry | AI Engineer 💻 @all rights saved 📜✨
                </p>
              </div>
            </div>
          )}

          {view === 'arch' && (
            <div className="p-12 max-w-4xl mx-auto space-y-6">
              <div className="bg-white p-8 rounded-2xl shadow-lg border border-gray-200">
                <h2 className="text-3xl font-bold mb-6 text-gray-800">🏗️ Agent Architecture</h2>
                <div className="bg-blue-50 p-6 rounded-xl border-l-8 border-blue-500 mb-8">
                  <h4 className="font-bold text-blue-800 text-lg">📋 Intelligent Routing System</h4>
                  <p className="text-blue-700 mt-2"><b>PLANNER MODULE:</b> Analyzes user queries → Routes to appropriate specialized tools → Combines results → Delivers comprehensive responses</p>
                </div>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  {['Grammar Handler', 'Vocabulary Handler', 'Translation Engine', 'Quiz Generator'].map((t, i) => (
                    <div key={i} className="p-6 border border-gray-100 rounded-xl bg-gray-50">
                      <h4 className={`font-bold mb-2 ${i==0?'text-[#667eea]':i==1?'text-[#ed8936]':i==2?'text-[#4facfe]':'text-[#43e97b]'}`}>{i+1}️⃣ {t}</h4>
                      <p className="text-sm text-gray-600">Specialized module powered by Llama 3 models and domain-specific knowledge bases.</p>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}

          {view === 'stats' && (
            <div className="p-12 max-w-4xl mx-auto space-y-6">
              <div className="bg-white p-10 rounded-3xl shadow-xl border border-gray-200 text-center">
                <h2 className="text-3xl font-bold mb-8 text-gray-800">📈 Session Statistics</h2>
                <div className="grid grid-cols-3 gap-8 mb-12">
                  <div className="p-8 bg-purple-50 rounded-3xl border border-purple-100">
                    <p className="text-purple-600 font-bold text-lg mb-2">Messages</p>
                    <p className="text-4xl font-black text-purple-900">{messages.length}</p>
                  </div>
                  <div className="p-8 bg-pink-50 rounded-3xl border border-pink-100">
                    <p className="text-pink-600 font-bold text-lg mb-2">Duration</p>
                    <p className="text-4xl font-black text-pink-900">7.5 min</p>
                  </div>
                  <div className="p-8 bg-green-50 rounded-3xl border border-green-100">
                    <p className="text-green-600 font-bold text-lg mb-2">Confidence</p>
                    <p className="text-4xl font-black text-green-900">92%</p>
                  </div>
                </div>
                <button 
                  onClick={sendStatsEmail}
                  disabled={isLoading}
                  className="px-12 py-5 bg-[#f5576c] text-white rounded-2xl font-bold hover:opacity-90 shadow-2xl shadow-[#f5576c]/40 transition-all text-xl disabled:opacity-50"
                >
                  {isLoading ? 'Sending...' : '📧 Email Session Report 🚀'}
                </button>
              </div>
            </div>
          )}
        </div>

        {/* Input Area */}
        {view === 'chat' && (
          <div className="p-4 md:p-6 bg-white border-t border-gray-200 z-10">
            <form onSubmit={(e) => { e.preventDefault(); sendMessage(); }} className="flex gap-2 md:gap-4 max-w-5xl mx-auto">
              <div className="relative flex-1">
                <input type="text" value={input} onChange={(e) => setInput(e.target.value)} placeholder="Type a message..." className="chat-input-container !pr-10 md:!pr-12 h-12 md:h-14 text-sm md:text-base" />
                <button type="button" onClick={toggleListening} className={`absolute right-2 md:right-3 top-1/2 -translate-y-1/2 p-2 rounded-full transition-all ${isListening ? 'bg-red-100 text-red-500 animate-pulse' : 'hover:bg-gray-100 text-gray-400 hover:text-[#f5576c]'}`}>🎤</button>
              </div>
              <button type="submit" disabled={isLoading || !input.trim()} className="bg-gray-800 text-white px-4 md:px-10 py-3 md:py-4 rounded-xl font-bold hover:bg-gray-700 transition-all disabled:opacity-50 text-sm md:text-lg">Send</button>
            </form>
          </div>
        )}
      </div>
      
      <style jsx global>{`
        .markdown-content p { margin-bottom: 1rem; }
        .markdown-content strong { font-weight: 700; color: inherit; }
        .custom-scrollbar::-webkit-scrollbar { width: 6px; }
        .custom-scrollbar::-webkit-scrollbar-thumb { background: #e0e0e0; border-radius: 10px; }
      `}</style>
    </div>
  );
}
