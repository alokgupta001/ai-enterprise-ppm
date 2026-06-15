"use client";

import { useEffect, useState, useRef } from "react";
import { useRouter } from "next/navigation";
import { 
  fetchCurrentUser, 
  sendAssistantMessage, 
  fetchRecommendations,
  getStreamingChatUrl 
} from "@/lib/api";
import { 
  Bot, 
  Send, 
  MessageSquare, 
  Plus, 
  Loader2, 
  User, 
  Sparkles,
  ArrowRight,
  TrendingUp,
  AlertTriangle,
  Users
} from "lucide-react";
import axios from "axios";

interface Conversation {
  id: string;
  title: string;
  created_at: string;
}

interface Message {
  id?: string;
  role: "user" | "assistant";
  content: string;
  agent_used?: string;
  created_at?: string;
}

export default function AssistantPage() {
  const router = useRouter();
  const [currentUser, setCurrentUser] = useState<any>(null);
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [activeConvId, setActiveConvId] = useState<string | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputValue, setInputValue] = useState("");
  
  // Loading & Streaming states
  const [loadingProfile, setLoadingProfile] = useState(true);
  const [loadingConversations, setLoadingConversations] = useState(false);
  const [loadingMessages, setLoadingMessages] = useState(false);
  const [isSending, setIsSending] = useState(false);
  const [streamedContent, setStreamedContent] = useState("");
  const [activeAgent, setActiveAgent] = useState<string | null>(null);

  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Suggested starters
  const starters = [
    {
      title: "Risks & Diagnostic",
      text: "Why is ERP Modernization at risk?",
      icon: AlertTriangle,
      color: "text-amber-400 bg-amber-500/10 border-amber-500/25"
    },
    {
      title: "Delayed Timeline",
      text: "Why is Data Migration Platform delayed?",
      icon: TrendingUp,
      color: "text-rose-400 bg-rose-500/10 border-rose-500/25"
    },
    {
      title: "Database Query",
      text: "List all projects with budget greater than 200000",
      icon: Sparkles,
      color: "text-indigo-400 bg-indigo-500/10 border-indigo-500/25"
    },
    {
      title: "Resource & Staffing",
      text: "Show resource allocation across all active projects",
      icon: Users,
      color: "text-emerald-400 bg-emerald-500/10 border-emerald-500/25"
    }
  ];

  // 1. Fetch current user on mount
  useEffect(() => {
    fetchCurrentUser()
      .then((data) => {
        setCurrentUser(data);
        setLoadingProfile(false);
      })
      .catch(() => {
        router.push("/login");
      });
  }, [router]);

  // 2. Fetch conversations when user is loaded
  useEffect(() => {
    if (currentUser) {
      loadConversations();
    }
  }, [currentUser]);

  // 3. Load messages when active conversation changes
  useEffect(() => {
    if (activeConvId) {
      loadMessages(activeConvId);
    } else {
      setMessages([]);
    }
  }, [activeConvId]);

  // 4. Auto scroll to bottom
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, streamedContent]);

  const loadConversations = async () => {
    if (!currentUser) return;
    setLoadingConversations(true);
    try {
      const response = await axios.get(`http://localhost:8000/api/assistant/conversations?org_id=${currentUser.organization_id}`, {
        headers: { Authorization: `Bearer ${localStorage.getItem("token")}` }
      });
      setConversations(response.data);
    } catch (err) {
      console.error("Failed to load conversations", err);
    } finally {
      setLoadingConversations(false);
    }
  };

  const loadMessages = async (convId: string) => {
    setLoadingMessages(true);
    try {
      const response = await axios.get(`http://localhost:8000/api/assistant/conversations/${convId}/messages`, {
        headers: { Authorization: `Bearer ${localStorage.getItem("token")}` }
      });
      setMessages(response.data);
    } catch (err) {
      console.error("Failed to load messages", err);
    } finally {
      setLoadingMessages(false);
    }
  };

  const handleStartNewChat = () => {
    setActiveConvId(null);
    setMessages([]);
    setStreamedContent("");
    setActiveAgent(null);
  };

  const handleSendMessage = async (text: string) => {
    if (!text.trim() || !currentUser || isSending) return;

    // Add user message locally
    const userMsg: Message = { role: "user", content: text };
    setMessages(prev => [...prev, userMsg]);
    setInputValue("");
    setIsSending(true);
    setStreamedContent("");
    setActiveAgent(null);

    const token = localStorage.getItem("token");
    const abortController = new AbortController();
    const timeoutId = setTimeout(() => abortController.abort(), 30000); // 30 second timeout
    
    try {
      // Use ReadableStream for Server-Sent Events (SSE)
      const response = await fetch("http://localhost:8000/api/assistant/chat/stream", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Authorization": `Bearer ${token}`
        },
        body: JSON.stringify({
          org_id: currentUser.organization_id,
          conversation_id: activeConvId || undefined,
          message: text
        }),
        signal: abortController.signal
      });

      if (!response.ok) {
        throw new Error("API call failed");
      }

      const reader = response.body?.getReader();
      const decoder = new TextDecoder();
      let buffer = "";

      if (reader) {
        while (true) {
          const { done, value } = await reader.read();
          if (done) break;

          buffer += decoder.decode(value, { stream: true });
          const lines = buffer.split("\n");
          // Save the last line if it's incomplete
          buffer = lines.pop() || "";

          for (const line of lines) {
            const trimmedLine = line.trim();
            if (trimmedLine.startsWith("data: ")) {
              const rawJson = trimmedLine.slice(6).trim();
              try {
                const parsed = JSON.parse(rawJson);
                if (parsed.type === "meta") {
                  setActiveAgent(parsed.agent);
                } else if (parsed.type === "token") {
                  setStreamedContent(prev => prev + parsed.content);
                } else if (parsed.type === "done") {
                  const newConvId = parsed.conversation_id;
                  
                  // Wrap up message
                  const aiMsg: Message = {
                    role: "assistant",
                    content: parsed.content || "", // we will assign full streamedContent later
                    agent_used: parsed.agent
                  };

                  // If it was a new conversation, refresh conversations list and select it
                  if (!activeConvId && newConvId) {
                    setActiveConvId(newConvId);
                    loadConversations();
                  } else {
                    // Just reload messages to make sure DB state matches
                    loadMessages(activeConvId || newConvId);
                  }
                }
              } catch (e) {
                // Ignore parse errors on ping/partial frames
              }
            }
          }
        }
      }
    } catch (err: any) {
      console.error(err);
      if (err.name === 'AbortError') {
        setMessages(prev => [
          ...prev,
          { role: "assistant", content: "Request timeout. The assistant took too long to respond. Please try again." }
        ]);
      } else {
        // Fallback to non-streaming endpoint if fetch stream fails
        try {
          const data = await sendAssistantMessage({
            org_id: currentUser.organization_id,
            conversation_id: activeConvId || undefined,
            message: text
          });

          if (!activeConvId && data.conversation_id) {
            setActiveConvId(data.conversation_id);
            loadConversations();
          } else {
            loadMessages(activeConvId || data.conversation_id);
          }
        } catch (fbErr: any) {
          setMessages(prev => [
            ...prev,
            { role: "assistant", content: "Error communicating with assistant. Please try again." }
          ]);
        }
      }
    } finally {
      clearTimeout(timeoutId);
      setIsSending(false);
      setStreamedContent("");
    }
  };

  const parseInlineMarkdown = (text: string) => {
    const boldRegex = /\*\*(.*?)\*\*/g;
    const parts = [];
    let lastIndex = 0;
    let match;
    
    while ((match = boldRegex.exec(text)) !== null) {
      const prevText = text.substring(lastIndex, match.index);
      if (prevText) parts.push(prevText);
      parts.push(<strong key={match.index} className="font-semibold text-white">{match[1]}</strong>);
      lastIndex = boldRegex.lastIndex;
    }
    
    const remainingText = text.substring(lastIndex);
    if (remainingText) parts.push(remainingText);
    
    return parts.length > 0 ? parts : text;
  };

  const renderMessageContent = (content: string) => {
    if (content.includes("|") && content.includes("---")) {
      const blocks = [];
      let currentTable: string[] = [];
      const lines = content.split("\n");
      
      for (let i = 0; i < lines.length; i++) {
        const line = lines[i].trim();
        if (line.startsWith("|") && line.endsWith("|")) {
          currentTable.push(line);
        } else {
          if (currentTable.length > 0) {
            blocks.push({ type: "table", data: currentTable });
            currentTable = [];
          }
          if (line) {
            blocks.push({ type: "text", data: line });
          }
        }
      }
      if (currentTable.length > 0) {
        blocks.push({ type: "table", data: currentTable });
      }
      
      return (
        <div className="space-y-3">
          {blocks.map((block, index) => {
            if (block.type === "table") {
              const tableLines = block.data as string[];
              const headers = tableLines[0].split("|").map(s => s.trim()).filter(Boolean);
              // Line 1 is the separator: e.g. |---|---|
              const rows = tableLines.slice(2).map(line => line.split("|").map(s => s.trim()).filter(Boolean));
              
              return (
                <div key={index} className="overflow-x-auto my-3 rounded-xl border border-zinc-800 shadow-lg max-w-full">
                  <table className="min-w-full divide-y divide-zinc-800 text-sm">
                    <thead className="bg-zinc-950 text-zinc-300 font-semibold uppercase tracking-wider text-xs">
                      <tr>
                        {headers.map((h, idx) => (
                          <th key={idx} className="px-4 py-2.5 text-left">{h}</th>
                        ))}
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-zinc-800 bg-zinc-900/40">
                      {rows.map((row, rIdx) => (
                        <tr key={rIdx} className="hover:bg-indigo-950/10 transition-colors">
                          {row.map((cell, cIdx) => (
                            <td key={cIdx} className="px-4 py-2.5 text-zinc-300 font-light">{cell}</td>
                          ))}
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              );
            }
            
            return <p key={index} className="text-sm leading-relaxed text-zinc-300">{parseInlineMarkdown(block.data as string)}</p>;
          })}
        </div>
      );
    }

    return (
      <div className="space-y-1.5 text-sm leading-relaxed text-zinc-300">
        {content.split("\n").map((line, idx) => {
          const trimmed = line.trim();
          if (trimmed.startsWith("###")) {
            return <h3 key={idx} className="text-base font-bold text-white mt-4 mb-2">{trimmed.replace("###", "").trim()}</h3>;
          }
          if (trimmed.startsWith("####")) {
            return <h4 key={idx} className="text-sm font-semibold text-white mt-3 mb-1.5">{trimmed.replace("####", "").trim()}</h4>;
          }
          if (trimmed.startsWith("- ")) {
            return <li key={idx} className="ml-4 list-disc text-zinc-300 my-0.5">{parseInlineMarkdown(trimmed.replace("- ", ""))}</li>;
          }
          if (trimmed.startsWith("*") && trimmed.endsWith("*")) {
            return <p key={idx} className="italic text-zinc-400 text-xs my-1">{trimmed.replace(/\*/g, "")}</p>;
          }
          return line ? <p key={idx}>{parseInlineMarkdown(line)}</p> : <div key={idx} className="h-1"></div>;
        })}
      </div>
    );
  };

  if (loadingProfile) {
    return (
      <div className="flex-1 flex flex-col items-center justify-center bg-zinc-950 text-white">
        <Loader2 className="h-10 w-10 animate-spin text-indigo-500 mb-4" />
        <p className="text-zinc-400 text-sm">Synchronizing assistant workspace...</p>
      </div>
    );
  }

  return (
    <div className="flex-1 flex bg-zinc-950 relative overflow-hidden h-full">
      {/* Subtle background glow */}
      <div className="absolute top-1/4 right-1/4 w-80 h-80 bg-indigo-600/5 rounded-full blur-3xl pointer-events-none"></div>

      {/* Internal Sidebar: Past Discussions */}
      <div className="w-72 border-r border-zinc-800 bg-zinc-900/30 flex flex-col z-10 shrink-0">
        <div className="p-4 border-b border-zinc-800 flex items-center justify-between">
          <span className="text-xs font-bold uppercase tracking-wider text-zinc-400">Conversations</span>
          <button 
            onClick={handleStartNewChat}
            className="p-1.5 rounded-lg border border-zinc-800 hover:bg-zinc-800 hover:text-white transition-colors cursor-pointer text-zinc-400 flex items-center gap-1.5 text-xs"
          >
            <Plus className="h-4.5 w-4.5" />
            New
          </button>
        </div>

        {/* List of past conversations */}
        <div className="flex-1 overflow-y-auto p-3 space-y-1">
          {loadingConversations ? (
            <div className="flex flex-col items-center py-8 text-zinc-500 gap-2">
              <Loader2 className="h-5 w-5 animate-spin text-zinc-600" />
              <span className="text-xs">Loading history...</span>
            </div>
          ) : conversations.length === 0 ? (
            <div className="text-center py-12 text-zinc-500 text-xs px-4">
              No recent discussions. Start one below!
            </div>
          ) : (
            conversations.map((conv) => {
              const isActive = activeConvId === conv.id;
              return (
                <button
                  key={conv.id}
                  onClick={() => setActiveConvId(conv.id)}
                  className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-left text-sm transition-all duration-150 cursor-pointer ${
                    isActive 
                      ? "bg-zinc-800 text-white border border-zinc-700 shadow-md font-medium" 
                      : "text-zinc-400 hover:bg-zinc-900 hover:text-zinc-200"
                  }`}
                >
                  <MessageSquare className={`h-4 w-4 shrink-0 ${isActive ? "text-indigo-400" : "text-zinc-500"}`} />
                  <span className="truncate flex-1">{conv.title}</span>
                </button>
              );
            })
          )}
        </div>
      </div>

      {/* Main Chat Interface */}
      <div className="flex-1 flex flex-col justify-between relative z-10 h-full">
        {/* Chat Header */}
        <div className="h-16 border-b border-zinc-800 px-6 flex items-center justify-between bg-zinc-950/80 backdrop-blur-md">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-indigo-600/10 rounded-lg text-indigo-400 border border-indigo-500/20">
              <Bot className="h-5 w-5" />
            </div>
            <div>
              <h2 className="text-sm font-semibold text-white tracking-tight">PMO Intelligence Center</h2>
              <p className="text-xs text-zinc-400">Specialist Agents: Risk, Resources & Timelines</p>
            </div>
          </div>
          {activeAgent && (
            <div className="px-2.5 py-1 bg-indigo-600/10 border border-indigo-500/30 text-indigo-400 rounded-full text-xs font-medium flex items-center gap-1.5 animate-pulse">
              <Sparkles className="h-3 w-3" />
              Active: {activeAgent}
            </div>
          )}
        </div>

        {/* Scrollable messages area */}
        <div className="flex-1 overflow-y-auto px-6 py-6 space-y-6">
          {messages.length === 0 && !isSending ? (
            /* Blank Starter Template */
            <div className="max-w-2xl mx-auto flex flex-col justify-center items-center h-full py-16 text-center">
              <div className="p-4 bg-indigo-600/10 border border-indigo-500/20 rounded-2xl text-indigo-400 mb-6 shadow-xl shadow-indigo-600/5">
                <Bot className="h-10 w-10 animate-bounce" />
              </div>
              <h3 className="text-2xl font-bold text-white tracking-tight">AI PMO Advisor</h3>
              <p className="text-zinc-400 text-sm max-w-sm mt-2 mb-10 leading-relaxed">
                Query project timelines, resources, and risks. Ask diagnostics on delays, or generate SQL matrices instantly.
              </p>

              {/* Suggestions Grid */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 w-full">
                {starters.map((s, idx) => {
                  const Icon = s.icon;
                  return (
                    <button
                      key={idx}
                      onClick={() => {
                        setInputValue(s.text);
                        handleSendMessage(s.text);
                      }}
                      className="p-4 bg-zinc-900/40 border border-zinc-800 rounded-xl text-left hover:border-indigo-500/40 hover:bg-zinc-900/70 transition-all duration-200 group cursor-pointer"
                    >
                      <div className="flex items-center gap-2 mb-2">
                        <div className={`p-1.5 rounded-lg border ${s.color}`}>
                          <Icon className="h-4 w-4" />
                        </div>
                        <span className="text-xs font-semibold text-zinc-300">{s.title}</span>
                      </div>
                      <p className="text-sm text-zinc-400 group-hover:text-zinc-200 line-clamp-2 leading-snug">
                        {s.text}
                      </p>
                    </button>
                  );
                })}
              </div>
            </div>
          ) : (
            /* Active Message List */
            <div className="max-w-3xl mx-auto space-y-6">
              {messages.map((msg, idx) => {
                const isUser = msg.role === "user";
                return (
                  <div key={idx} className={`flex items-start gap-4 ${isUser ? "justify-end" : "justify-start"}`}>
                    {!isUser && (
                      <div className="p-2 bg-zinc-900 border border-zinc-800 rounded-xl text-indigo-400 shadow-md">
                        <Bot className="h-5 w-5" />
                      </div>
                    )}
                    <div className={`max-w-[85%] rounded-2xl px-5 py-4 shadow-xl ${
                      isUser 
                        ? "bg-indigo-600/90 text-white rounded-tr-none font-light" 
                        : "bg-zinc-900/60 backdrop-blur-md border border-zinc-800 rounded-tl-none"
                    }`}>
                      {isUser ? (
                        <p className="text-sm font-light leading-relaxed">{msg.content}</p>
                      ) : (
                        <div>
                          {renderMessageContent(msg.content)}
                          {msg.agent_used && (
                            <div className="mt-3.5 pt-2 border-t border-zinc-800/60 flex items-center gap-1.5 text-zinc-500 text-[10px] uppercase font-bold tracking-wider">
                              <Sparkles className="h-3 w-3 text-indigo-400" />
                              Agent: {msg.agent_used}
                            </div>
                          )}
                        </div>
                      )}
                    </div>
                  </div>
                );
              })}

              {/* Streaming placeholder message */}
              {isSending && (streamedContent || activeAgent) && (
                <div className="flex items-start gap-4 justify-start">
                  <div className="p-2 bg-zinc-900 border border-zinc-800 rounded-xl text-indigo-400">
                    <Bot className="h-5 w-5" />
                  </div>
                  <div className="max-w-[85%] bg-zinc-900/60 backdrop-blur-md border border-zinc-800 rounded-2xl rounded-tl-none px-5 py-4 shadow-xl">
                    {streamedContent ? (
                      <div>
                        {renderMessageContent(streamedContent)}
                        <span className="inline-block w-1.5 h-4 ml-1 bg-indigo-500 animate-pulse"></span>
                      </div>
                    ) : (
                      <div className="flex items-center gap-2 text-zinc-400 text-sm">
                        <Loader2 className="h-4 w-4 animate-spin text-indigo-500" />
                        <span>Formulating response metrics...</span>
                      </div>
                    )}
                  </div>
                </div>
              )}
              <div ref={messagesEndRef} />
            </div>
          )}
        </div>

        {/* Input Bar */}
        <div className="p-4 border-t border-zinc-800 bg-zinc-950/80 backdrop-blur-md">
          <form 
            onSubmit={(e) => {
              e.preventDefault();
              handleSendMessage(inputValue);
            }} 
            className="max-w-3xl mx-auto flex items-center gap-3 relative"
          >
            <input
              type="text"
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              placeholder="Ask about project risks, velocity bottlenecks, or custom database selects..."
              disabled={isSending}
              className="flex-1 bg-zinc-900/60 border border-zinc-800 rounded-2xl pl-4 pr-12 py-3.5 text-sm text-white focus:outline-none focus:border-indigo-500/70 placeholder-zinc-500 transition-colors shadow-inner"
            />
            <button
              type="submit"
              disabled={!inputValue.trim() || isSending}
              className="absolute right-2.5 p-2 bg-indigo-600 rounded-xl hover:bg-indigo-500 disabled:opacity-30 transition-colors text-white cursor-pointer shadow-lg shadow-indigo-600/10"
            >
              {isSending ? (
                <Loader2 className="h-4 w-4 animate-spin" />
              ) : (
                <Send className="h-4 w-4" />
              )}
            </button>
          </form>
          <div className="text-center text-[10px] text-zinc-500 mt-2 tracking-wide font-light uppercase">
            Data secured under organization role-based access policy.
          </div>
        </div>
      </div>
    </div>
  );
}
