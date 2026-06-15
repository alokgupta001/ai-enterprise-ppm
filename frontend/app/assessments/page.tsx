"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { fetchFrameworks, startAssessment, fetchCurrentUser } from "@/lib/api";
import { ClipboardCheck, ArrowRight, Activity, Cpu, Sparkles } from "lucide-react";

export default function AssessmentsPage() {
  const router = useRouter();
  const [frameworks, setFrameworks] = useState<any[]>([]);
  const [currentUser, setCurrentUser] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [starting, setStarting] = useState<string | null>(null);

  useEffect(() => {
    const loadData = async () => {
      try {
        const user = await fetchCurrentUser();
        setCurrentUser(user);
        const fws = await fetchFrameworks();
        setFrameworks(fws);
      } catch (err) {
        console.error("Failed to load assessments page data", err);
      } finally {
        setLoading(false);
      }
    };
    loadData();
  }, []);

  const handleStart = async (frameworkId: string) => {
    if (!currentUser) return;
    setStarting(frameworkId);
    try {
      const result = await startAssessment({
        org_id: currentUser.organization_id,
        framework_id: frameworkId,
      });
      router.push(`/assessments/${result.id}/questions`);
    } catch (err) {
      console.error("Failed to start assessment", err);
      alert("Error starting the assessment. Please try again.");
    } finally {
      setStarting(null);
    }
  };

  if (loading) {
    return (
      <div className="flex-1 flex items-center justify-center p-8">
        <div className="flex flex-col items-center gap-3">
          <div className="h-8 w-8 border-4 border-indigo-500 border-t-transparent rounded-full animate-spin"></div>
          <p className="text-zinc-400 text-sm">Loading frameworks...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="p-8 max-w-5xl mx-auto space-y-8 select-none">
      {/* Welcome banner */}
      <div className="p-8 rounded-2xl bg-zinc-900 border border-zinc-800 flex flex-col md:flex-row items-start md:items-center justify-between gap-6 relative overflow-hidden">
        <div className="absolute top-0 right-0 w-80 h-80 bg-indigo-600/5 rounded-full blur-3xl pointer-events-none"></div>
        
        <div className="space-y-2 relative z-10">
          <h2 className="text-2xl font-bold text-white tracking-tight">Enterprise Maturity Hub</h2>
          <p className="text-zinc-400 max-w-xl text-sm leading-relaxed">
            Run an in-depth PMO execution diagnostics to analyze process strengths and compile AI-powered recommendations.
          </p>
        </div>
        <div className="flex items-center gap-4 shrink-0">
          <div className="text-right">
            <p className="text-xs text-zinc-500 uppercase tracking-wider font-semibold">Account Level</p>
            <p className="text-sm font-bold text-indigo-400">{currentUser?.role}</p>
          </div>
          <div className="h-10 w-10 bg-indigo-600/10 text-indigo-400 rounded-lg flex items-center justify-center font-bold">
            <ClipboardCheck className="h-5 w-5" />
          </div>
        </div>
      </div>

      {/* Framework Cards */}
      <div className="space-y-4">
        <h3 className="text-sm font-semibold text-zinc-400 uppercase tracking-wider px-1">Available Frameworks</h3>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {frameworks.map((fw) => (
            <div 
              key={fw.id} 
              className="bg-zinc-900/40 backdrop-blur border border-zinc-800/80 p-6 rounded-2xl flex flex-col justify-between hover:border-zinc-700 hover:shadow-xl transition-all duration-300 group"
            >
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <span className="text-xs font-semibold px-2.5 py-1 bg-zinc-800 text-zinc-300 rounded-full border border-zinc-700">
                    Version {fw.version}
                  </span>
                  <div className="flex gap-2">
                    <Activity className="h-4 w-4 text-emerald-500" />
                    <Cpu className="h-4 w-4 text-violet-500" />
                  </div>
                </div>

                <div className="space-y-2">
                  <h4 className="text-lg font-bold text-white group-hover:text-indigo-400 transition-colors">
                    {fw.name}
                  </h4>
                  <p className="text-zinc-400 text-sm leading-relaxed">
                    {fw.description}
                  </p>
                </div>
              </div>

              <button
                onClick={() => handleStart(fw.id)}
                disabled={starting !== null}
                className="mt-6 w-full flex items-center justify-center gap-2 bg-indigo-600 text-white py-2.5 rounded-xl font-semibold text-sm hover:bg-indigo-500 active:bg-indigo-700 disabled:opacity-50 transition-all cursor-pointer group-hover:shadow-lg group-hover:shadow-indigo-600/10"
              >
                {starting === fw.id ? (
                  "Starting assessment..."
                ) : (
                  <>
                    Begin Evaluation
                    <ArrowRight className="h-4 w-4 group-hover:translate-x-1 transition-transform" />
                  </>
                )}
              </button>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
