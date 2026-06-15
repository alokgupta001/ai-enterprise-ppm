"use client";

import { useEffect, useState, use } from "react";
import { useRouter } from "next/navigation";
import { fetchAssessmentQuestions, submitResponses } from "@/lib/api";
import { ChevronLeft, ChevronRight, CheckCircle2, Sparkles } from "lucide-react";

export default function QuestionsPage({ params }: { params: Promise<{ id: string }> }) {
  const router = useRouter();
  const { id: assessmentId } = use(params);

  const [questions, setQuestions] = useState<any[]>([]);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [answers, setAnswers] = useState<Record<string, { score: number; text: string }>>({});
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);

  // Current Card input state cache
  const [score, setScore] = useState(0);
  const [text, setText] = useState("");

  useEffect(() => {
    fetchAssessmentQuestions(assessmentId)
      .then((data) => {
        setQuestions(data);
        // Initialize answers dictionary
        const initialAnswers: Record<string, { score: number; text: string }> = {};
        data.forEach((q: any) => {
          initialAnswers[q.id] = { score: 0, text: "" };
        });
        setAnswers(initialAnswers);
      })
      .catch((err) => {
        console.error("Failed to fetch assessment questions", err);
      })
      .finally(() => {
        setLoading(false);
      });
  }, [assessmentId]);

  // Sync inputs on slide index change
  useEffect(() => {
    if (questions.length > 0 && questions[currentIndex]) {
      const saved = answers[questions[currentIndex].id];
      if (saved) {
        setScore(saved.score);
        setText(saved.text);
      }
    }
  }, [currentIndex, questions, answers]);

  const saveCurrentAnswer = () => {
    if (questions.length === 0) return;
    const qId = questions[currentIndex].id;
    setAnswers((prev) => ({
      ...prev,
      [qId]: { score, text }
    }));
  };

  const handleNext = () => {
    saveCurrentAnswer();
    if (currentIndex < questions.length - 1) {
      setCurrentIndex((prev) => prev + 1);
    }
  };

  const handlePrev = () => {
    saveCurrentAnswer();
    if (currentIndex > 0) {
      setCurrentIndex((prev) => prev - 1);
    }
  };

  const handleSubmit = async () => {
    saveCurrentAnswer();
    setSubmitting(true);
    try {
      const payloadResponses = Object.entries(answers).map(([qId, val]) => ({
        question_id: qId,
        score: val.score,
        text_response: val.text
      }));
      await submitResponses(assessmentId, payloadResponses);
      router.push(`/assessments/${assessmentId}/results`);
    } catch (err) {
      console.error("Submission failed", err);
      alert("Error submitting answers. Please try again.");
    } finally {
      setSubmitting(false);
    }
  };

  if (loading) {
    return (
      <div className="flex-1 flex items-center justify-center p-8">
        <div className="flex flex-col items-center gap-3">
          <div className="h-8 w-8 border-4 border-indigo-500 border-t-transparent rounded-full animate-spin"></div>
          <p className="text-zinc-400 text-sm">Loading questionnaire...</p>
        </div>
      </div>
    );
  }

  if (questions.length === 0) {
    return (
      <div className="flex-1 flex items-center justify-center p-8 text-zinc-400 text-sm">
        No questions found for this maturity framework.
      </div>
    );
  }

  const currentQ = questions[currentIndex];
  const progressPercent = Math.round(((currentIndex + 1) / questions.length) * 100);

  const getScoreColor = (val: number) => {
    if (val <= 2) return "text-red-400";
    if (val === 3) return "text-zinc-400";
    if (val === 4) return "text-indigo-400";
    return "text-emerald-400";
  };

  const scoreLabels: Record<number, string> = {
    1: "Ad-hoc / Manual",
    2: "Inconsistent",
    3: "Standardized / Defined",
    4: "Measured / Managed",
    5: "Optimizing / Continuous"
  };

  return (
    <div className="p-8 max-w-3xl mx-auto space-y-6 select-none flex flex-col justify-center min-h-[80vh]">
      {/* Progress Bar Header */}
      <div className="space-y-3">
        <div className="flex justify-between items-end">
          <div>
            <span className="text-xs font-bold text-indigo-400 uppercase tracking-widest">{currentQ.category_name}</span>
            <h2 className="text-xl font-bold text-white mt-1">
              Assessment Flow
            </h2>
          </div>
          <span className="text-sm font-semibold text-zinc-500">
            {currentIndex + 1} of {questions.length} Questions
          </span>
        </div>
        <div className="w-full bg-zinc-900 border border-zinc-800 rounded-full h-2.5 overflow-hidden">
          <div 
            className="bg-indigo-600 h-full rounded-full transition-all duration-300"
            style={{ width: `${progressPercent}%` }}
          ></div>
        </div>
      </div>

      {/* Question Card */}
      <div className="bg-zinc-900/40 border border-zinc-800 p-8 rounded-2xl shadow-xl space-y-6 relative overflow-hidden backdrop-blur-md">
        <div className="absolute top-0 right-0 p-3 bg-zinc-950/20 text-zinc-500 text-xs font-mono rounded-bl-xl border-l border-b border-zinc-800/40">
          Q-{currentIndex + 1}
        </div>

        <div className="space-y-2">
          <p className="text-lg font-bold text-white pr-12 leading-snug">
            {currentQ.question_text}
          </p>
        </div>

        {/* Numeric Slider Input */}
        <div className="space-y-4 pt-4 border-t border-zinc-800/60">
          <div className="flex justify-between items-center">
            <span className="text-xs font-semibold text-zinc-400 uppercase tracking-wider">Self Assessment Score</span>
            <span className={`text-sm font-bold ${getScoreColor(score)}`}>
              {score} - {scoreLabels[score]}
            </span>
          </div>

          <div className="flex items-center gap-4">
            <span className="text-xs text-zinc-600">1</span>
            <input 
              type="range" 
              min={1} 
              max={5} 
              value={score} 
              onChange={(e) => setScore(Number(e.target.value))}
              className="flex-1 accent-indigo-500 h-1 bg-zinc-800 rounded-lg cursor-pointer"
            />
            <span className="text-xs text-zinc-600">5</span>
          </div>
        </div>

        {/* Qualitative Text Input */}
        <div className="space-y-2 pt-2">
          <div className="flex justify-between items-center">
            <label className="text-xs font-semibold text-zinc-400 uppercase tracking-wider flex items-center gap-1.5">
              Qualitative Context
              <Sparkles className="h-3.5 w-3.5 text-indigo-400" />
            </label>
            <span className="text-[10px] text-zinc-500 font-semibold">AI Evaluator enabled</span>
          </div>
          <textarea
            value={text}
            onChange={(e) => setText(e.target.value)}
            placeholder="Describe your current processes, tools, and execution quality for this area..."
            className="w-full min-h-[140px] bg-zinc-950/60 border border-zinc-800 text-zinc-200 text-sm rounded-xl p-4 focus:outline-none focus:border-indigo-500 transition-colors resize-none leading-relaxed"
          ></textarea>
        </div>
      </div>

      {/* Slide Deck Actions */}
      <div className="flex justify-between items-center">
        <button
          onClick={handlePrev}
          disabled={currentIndex === 0}
          className="flex items-center gap-2 bg-zinc-900 border border-zinc-800 text-zinc-300 px-5 py-2.5 rounded-xl text-sm font-medium hover:bg-zinc-800 disabled:opacity-30 disabled:pointer-events-none transition-colors cursor-pointer"
        >
          <ChevronLeft className="h-4 w-4" />
          Previous
        </button>

        {currentIndex === questions.length - 1 ? (
          <button
            onClick={handleSubmit}
            disabled={submitting}
            className="flex items-center gap-2 bg-indigo-600 text-white px-6 py-2.5 rounded-xl text-sm font-bold hover:bg-indigo-500 active:bg-indigo-700 disabled:opacity-50 transition-colors cursor-pointer shadow-lg shadow-indigo-600/20"
          >
            <CheckCircle2 className="h-4 w-4" />
            {submitting ? "Analyzing results..." : "Submit & Score"}
          </button>
        ) : (
          <button
            onClick={handleNext}
            className="flex items-center gap-2 bg-indigo-600 text-white px-6 py-2.5 rounded-xl text-sm font-bold hover:bg-indigo-500 active:bg-indigo-700 transition-colors cursor-pointer shadow-lg shadow-indigo-600/20"
          >
            Next
            <ChevronRight className="h-4 w-4" />
          </button>
        )}
      </div>
    </div>
  );
}
