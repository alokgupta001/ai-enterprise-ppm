import axios from "axios";

const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000";

const api = axios.create({
  baseURL: API_BASE_URL,
});

// Request Interceptor to attach JWT token
api.interceptors.request.use((config) => {
  if (typeof window !== "undefined") {
    // Note: For production, tokens should be stored in httpOnly cookies
    // and set by the backend during authentication
    const token = localStorage.getItem("token");
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
  }
  return config;
}, (error) => {
  return Promise.reject(error);
});

// Authentication APIs
export const registerUser = async (payload: any) => {
  const response = await api.post("/api/auth/register", payload);
  return response.data;
};

export const loginUser = async (payload: any) => {
  const response = await api.post("/api/auth/login", payload);
  return response.data;
};

export const fetchCurrentUser = async () => {
  const response = await api.get("/api/auth/me");
  return response.data;
};

// Organization APIs
export const fetchOrganizations = async () => {
  const response = await api.get("/api/org/");
  return response.data;
};

// Assessment APIs
export const fetchFrameworks = async () => {
  const response = await api.get("/api/assessments/frameworks");
  return response.data;
};

export const startAssessment = async (payload: any) => {
  const response = await api.post("/api/assessments/start", payload);
  return response.data;
};

export const fetchAssessmentQuestions = async (assessmentId: string) => {
  const response = await api.get(`/api/assessments/${assessmentId}/questions`);
  return response.data;
};

export const submitResponses = async (assessmentId: string, responses: any[]) => {
  const response = await api.post(`/api/assessments/${assessmentId}/submit`, { responses });
  return response.data;
};

export const fetchResults = async (assessmentId: string) => {
  const response = await api.get(`/api/assessments/${assessmentId}/results`);
  return response.data;
};

// Projects & Portfolio APIs (Module 2)
export const fetchProjects = async (orgId?: string) => {
  const url = orgId ? `/api/projects/?org_id=${orgId}` : "/api/projects/";
  const response = await api.get(url);
  return response.data;
};

export const fetchProjectSummary = async (projectId: string) => {
  const response = await api.get(`/api/projects/${projectId}/summary`);
  return response.data;
};

// Conversational AI Assistant APIs (Module 2)
export const sendAssistantMessage = async (payload: any) => {
  const response = await api.post("/api/assistant/chat", payload);
  return response.data;
};

export const fetchRecommendations = async (orgId: string) => {
  const response = await api.get(`/api/assistant/recommendations?org_id=${orgId}`);
  return response.data;
};

export const fetchRootCauseAnalysis = async (projectId: string) => {
  const response = await api.post(`/api/assistant/projects/${projectId}/root-cause`);
  return response.data;
};

export const getStreamingChatUrl = () => {
  return `${API_BASE_URL}/api/assistant/chat/stream`;
};

export default api;
