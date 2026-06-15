"use client";

import { useEffect, useState, use } from "react";
import { useRouter } from "next/navigation";
import { fetchResults } from "@/lib/api";
import { 
  RadarChart, 
  Radar, 
  PolarGrid, 
  PolarAngleAxis, 
  PolarRadiusAxis,
  ResponsiveContainer,
  Tooltip
} from "recharts";
import { 
  Award, 
  ArrowLeft, 
  Printer, 
  Building,
  Calendar,
  Sparkles,
  CheckCircle,
  AlertTriangle
} from "lucide-react";

export default function ResultsPage({ params }: { params: Promise<{ id: string }> }) {
  const router = useRouter();
  const { id: assessmentId } = use(params);

  const [results, setResults] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchResults(assessmentId)
      .then((data) => {
        setResults(data);
      })
      .catch((err) => {
        console.error("Failed to load results", err);
      })
      .finally(() => {
        setLoading(false);
      });
  }, [assessmentId]);

  if (loading) {
    return (
      <div className="flex-1 flex items-center justify-center p-8">
        <div className="flex flex-col items-center gap-3">
          <div className="h-8 w-8 border-4 border-indigo-500 border-t-transparent rounded-full animate-spin"></div>
          <p className="text-zinc-400 text-sm">Evaluating scores...</p>
        </div>
      </div>
    );
  }

  if (!results || !results.scores) {
    return (
      <div className="flex-1 flex items-center justify-center p-8 text-zinc-400 text-sm">
        Assessment results could not be loaded.
      </div>
    );
  }

  const radarData = results.scores.map((s: any) => ({
    subject: s.category_name,
    score: s.score,
    fullMark: 5,
  }));

  const getMaturityColor = (level: string) => {
    switch (level) {
      case "Initial": return "from-red-500/10 to-red-600/5 text-red-400 border-red-500/20";
      case "Developing": return "from-amber-500/10 to-amber-600/5 text-amber-400 border-amber-500/20";
      case "Defined": return "from-indigo-500/10 to-indigo-600/5 text-indigo-400 border-indigo-500/20";
      case "Managed": return "from-blue-500/10 to-blue-600/5 text-blue-400 border-blue-500/20";
      case "Optimizing": return "from-emerald-500/10 to-emerald-600/5 text-emerald-400 border-emerald-500/20";
      default: return "from-zinc-500/10 to-zinc-600/5 text-zinc-400 border-zinc-500/20";
    }
  };

  const parseAiSummary = (summaryText: string) => {
    if (!summaryText) return [];
    
    // Check if contains pipe syntax
    if (summaryText.includes(" | ")) {
      const parts = summaryText.split(" | ");
      return parts.map(p => {
        const strMatch = p.match(/Strength:\s*(.*?)(?=\.\s*Gap:|$)/i);
        const gapMatch = p.match(/Gap:\s*(.*?)(?=\.\s*Recommendation:|$)/i);
        const recMatch = p.match(/Recommendation:\s*(.*?)$/i);
        return {
          strength: strMatch ? strMatch[1] : "",
          gap: gapMatch ? gapMatch[1] : "",
          rec: recMatch ? recMatch[1] : ""
        };
      });
    }

    // Single statement format fallback
    const strMatch = summaryText.match(/Strength(s)?:\s*(.*?)(?=\.\s*Gap(s)?:|$)/i);
    const gapMatch = summaryText.match(/Gap(s)?:\s*(.*?)(?=\.\s*Rec(ommendation)?:|$)/i);
    const recMatch = summaryText.match(/Rec(ommendation)?:\s*(.*?)$/i);
    return [{
      strength: strMatch ? strMatch[2] : "",
      gap: gapMatch ? gapMatch[2] : "",
      rec: recMatch ? recMatch[2] : ""
    }];
  };

  return (
    <div className="p-8 max-w-6xl mx-auto space-y-8 select-none print:bg-white print:text-black">
      {/* Header controls */}
      <div className="flex justify-between items-center print:hidden">
        <button
          onClick={() => router.push("/assessments")}
          className="flex items-center gap-2 text-zinc-400 hover:text-white text-sm font-medium transition-colors cursor-pointer"
        >
          <ArrowLeft className="h-4 w-4" />
          Maturity Hub
        </button>
        <button
          onClick={() => window.print()}
          className="flex items-center gap-2 bg-zinc-900 border border-zinc-800 text-zinc-300 px-4 py-2 rounded-xl text-sm font-medium hover:bg-zinc-800 transition-colors cursor-pointer"
        >
          <Printer className="h-4 w-4" />
          Export Report
        </button>
      </div>

      {/* Hero Score Badge */}
      <div className={`p-8 border rounded-2xl bg-gradient-to-r ${getMaturityColor(results.overall_level)} flex flex-col md:flex-row items-center justify-between gap-8`}>
        <div className="space-y-3 text-center md:text-left">
          <div className="flex items-center justify-center md:justify-start gap-2.5">
            <Award className="h-6 w-6 shrink-0" />
            <span className="text-xs font-bold uppercase tracking-widest">Global Maturity Rating</span>
          </div>
          <h2 className="text-4xl font-extrabold tracking-tight">
            Maturity Level: {results.overall_level}
          </h2>
          <p className="text-sm opacity-80 max-w-xl">
            Organization demonstrates standard processes across portfolio and delivery metrics. Below is the breakdown.
          </p>
        </div>
        
        {/* Overall Score */}
        <div className="flex flex-col items-center justify-center shrink-0 border border-current/25 bg-zinc-950/40 p-6 rounded-2xl min-w-[150px]">
          <span className="text-xs font-bold uppercase opacity-60 tracking-wider">Maturity Score</span>
          <span className="text-5xl font-black mt-1">{results.overall_score}</span>
          <span className="text-[10px] font-bold opacity-60 tracking-widest mt-1">OUT OF 5.0</span>
        </div>
      </div>

      {/* Grid Dashboard */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        
        {/* Recharts Radar Chart */}
        <div className="bg-zinc-900/40 border border-zinc-800 p-6 rounded-2xl flex flex-col justify-between backdrop-blur min-h-[400px]">
          <h3 className="text-sm font-semibold text-zinc-400 uppercase tracking-wider mb-4">Maturity Distribution</h3>
          
          <div className="flex-1 flex items-center justify-center">
            <ResponsiveContainer width="100%" height={320}>
              <RadarChart cx="50%" cy="50%" outerRadius="70%" data={radarData}>
                <PolarGrid stroke="#27272a" />
                <PolarAngleAxis dataKey="subject" tick={{ fill: "#a1a1aa", fontSize: 10 }} />
                <PolarRadiusAxis angle={30} domain={[0, 5]} tick={{ fill: "#52525b" }} />
                <Radar 
                  name="Maturity Score" 
                  dataKey="score" 
                  stroke="#4f46e5" 
                  fill="#4f46e5" 
                  fillOpacity={0.35} 
                />
                <Tooltip 
                  contentStyle={{ backgroundColor: "#09090b", borderColor: "#27272a", borderRadius: "10px" }}
                  itemStyle={{ color: "#fff" }}
                />
              </RadarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Categories Scores List */}
        <div className="bg-zinc-900/40 border border-zinc-800 p-6 rounded-2xl space-y-4 backdrop-blur overflow-y-auto max-h-[420px]">
          <h3 className="text-sm font-semibold text-zinc-400 uppercase tracking-wider">Category Performance</h3>
          
          <div className="space-y-3">
            {results.scores.map((s: any) => (
              <div key={s.category_id} className="p-4 bg-zinc-950/40 border border-zinc-800/60 rounded-xl flex items-center justify-between gap-4">
                <div>
                  <h4 className="font-semibold text-white text-sm">{s.category_name}</h4>
                  <span className="text-[10px] text-zinc-500 uppercase font-semibold">{s.level} Level</span>
                </div>
                <div className="text-right shrink-0">
                  <span className="text-lg font-black text-indigo-400">{s.score}</span>
                  <span className="text-xs text-zinc-600">/5</span>
                </div>
              </div>
            ))}
          </div>
        </div>

      </div>

      {/* AI Recommendations Panel */}
      <div className="bg-zinc-900/40 border border-zinc-800 p-8 rounded-2xl space-y-6 backdrop-blur">
        <div className="flex items-center gap-2 border-b border-zinc-800 pb-4">
          <Sparkles className="h-5 w-5 text-indigo-400 animate-pulse" />
          <h3 className="text-base font-bold text-white">AI-Generated PMO Action Plan</h3>
        </div>

        <div className="space-y-6">
          {results.scores.map((s: any) => {
            const evals = parseAiSummary(s.ai_summary);
            return (
              <div key={s.category_id} className="space-y-3">
                <h4 className="text-sm font-bold text-zinc-300 border-l-2 border-indigo-500 pl-3">
                  {s.category_name} (Level: {s.level})
                </h4>
                
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4 pl-3">
                  {evals.map((ev, i) => (
                    <div key={i} className="p-4 bg-zinc-950/60 border border-zinc-800/40 rounded-xl space-y-2 text-xs">
                      {ev.strength && (
                        <div className="space-y-1">
                          <span className="text-[10px] font-bold text-emerald-500 uppercase tracking-wider flex items-center gap-1">
                            <CheckCircle className="h-3 w-3" /> Strength
                          </span>
                          <p className="text-zinc-300 leading-relaxed">{ev.strength}</p>
                        </div>
                      )}
                      {ev.gap && (
                        <div className="space-y-1 pt-2 border-t border-zinc-900">
                          <span className="text-[10px] font-bold text-amber-500 uppercase tracking-wider flex items-center gap-1">
                            <AlertTriangle className="h-3 w-3" /> Deficit/Gap
                          </span>
                          <p className="text-zinc-300 leading-relaxed">{ev.gap}</p>
                        </div>
                      )}
                      {ev.rec && (
                        <div className="space-y-1 pt-2 border-t border-zinc-900 bg-indigo-950/10 p-2 rounded">
                          <span className="text-[10px] font-bold text-indigo-400 uppercase tracking-wider flex items-center gap-1">
                            Recommendation
                          </span>
                          <p className="text-indigo-200 leading-relaxed">{ev.rec}</p>
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
