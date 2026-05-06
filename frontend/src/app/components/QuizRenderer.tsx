'use client';

import { useState } from 'react';

type Question = {
  question: string;
  A: string;
  B: string;
  C: string;
  D: string;
  answer: string;
};

type QuizData = {
  questions: Question[];
};

export default function QuizRenderer({ data, onComplete }: { data: QuizData, onComplete?: (score: number, total: number) => void }) {
  const [currentIdx, setCurrentIdx] = useState(0);
  const [score, setScore] = useState(0);
  const [answered, setAnswered] = useState(false);
  const [selectedAns, setSelectedAns] = useState<string | null>(null);
  const [finished, setFinished] = useState(false);

  const handleSelect = (choice: string) => {
    if (answered) return;
    
    setAnswered(true);
    setSelectedAns(choice);
    const correctAns = data.questions[currentIdx].answer;
    if (choice === correctAns) {
      setScore(prev => prev + 1);
    }
  };

  const handleNext = () => {
    if (currentIdx < data.questions.length - 1) {
      setCurrentIdx(prev => prev + 1);
      setAnswered(false);
      setSelectedAns(null);
    } else {
      setFinished(true);
      if (onComplete) onComplete(score, data.questions.length);
    }
  };

  const resetQuiz = () => {
    setCurrentIdx(0);
    setScore(0);
    setAnswered(false);
    setSelectedAns(null);
    setFinished(false);
  };

  if (finished) {
    return (
      <div className="mt-4 p-8 bg-white rounded-2xl shadow-xl border border-gray-200 text-center animate-in fade-in duration-500">
        <h3 className="text-2xl font-bold mb-4 text-gray-800">🏁 Quiz Results</h3>
        <div className="text-5xl font-black text-[#f5576c] mb-6">
          {score} / {data.questions.length}
        </div>
        <p className="text-xl text-gray-600 mb-8">
          ({((score / data.questions.length) * 100).toFixed(1)}%)
        </p>
        
        <div className="bg-blue-50 p-4 rounded-xl border border-blue-100 mb-8 text-blue-700 font-medium">
          📧 Results have been emailed to your progress report! 🚀
        </div>

        <button
          onClick={resetQuiz}
          className="w-full py-4 rounded-xl bg-gray-800 text-white font-bold hover:bg-gray-700 transition-all shadow-lg"
        >
          🔄 Restart Quiz
        </button>
      </div>
    );
  }

  const q = data.questions[currentIdx];
  const correctAns = q.answer;

  return (
    <div className="mt-4 p-8 bg-white rounded-2xl shadow-xl border border-gray-200 animate-in slide-in-from-bottom-4 duration-300">
      <div className="flex justify-between items-center mb-6">
        <h3 className="text-lg font-bold text-gray-400">📝 Question {currentIdx + 1} of {data.questions.length}</h3>
        <div className="w-1/3 bg-gray-100 h-2 rounded-full overflow-hidden">
          <div 
            className="bg-[#f5576c] h-full transition-all duration-500" 
            style={{ width: `${((currentIdx + 1) / data.questions.length) * 100}%` }}
          ></div>
        </div>
      </div>
      
      <h4 className="text-xl font-bold mb-8 text-gray-800 leading-relaxed">
        {q.question}
      </h4>

      <div className="space-y-3 mb-8">
        {['A', 'B', 'C', 'D'].map((choice) => {
          const choiceText = (q as any)[choice];
          const isSelected = selectedAns === choice;
          const isCorrect = correctAns === choice;
          
          let btnStyle = "border-gray-200 hover:border-[#f5576c] hover:bg-pink-50";
          let icon = choice;
          let iconStyle = "border-gray-300 text-gray-500";

          if (answered) {
            if (isCorrect) {
              btnStyle = "bg-green-50 border-green-500 text-green-800 shadow-sm";
              icon = "✓";
              iconStyle = "bg-green-500 border-green-500 text-white";
            } else if (isSelected) {
              btnStyle = "bg-red-50 border-red-500 text-red-800 shadow-sm";
              icon = "✗";
              iconStyle = "bg-red-500 border-red-500 text-white";
            } else {
              btnStyle = "opacity-50 border-gray-100 cursor-default";
            }
          } else if (isSelected) {
            btnStyle = "bg-[#f5576c] border-[#f5576c] text-white shadow-lg";
            iconStyle = "bg-white border-white text-[#f5576c]";
          }

          return (
            <button
              key={choice}
              onClick={() => handleSelect(choice)}
              className={`w-full p-4 rounded-xl border-2 transition-all text-left flex items-center font-medium ${btnStyle}`}
            >
              <span className={`w-8 h-8 flex items-center justify-center rounded-full border-2 mr-4 font-bold text-sm transition-all ${iconStyle}`}>
                {icon}
              </span>
              {choiceText}
            </button>
          );
        })}
      </div>

      {answered && (
        <button
          onClick={handleNext}
          className="w-full py-4 rounded-xl bg-[#f5576c] text-white font-bold hover:opacity-90 transition-all shadow-xl shadow-[#f5576c]/30 animate-in fade-in slide-in-from-bottom-2 duration-300"
        >
          {currentIdx === data.questions.length - 1 ? "Finish Quiz 🏁" : "Next Question ➡️"}
        </button>
      )}
    </div>
  );
}
