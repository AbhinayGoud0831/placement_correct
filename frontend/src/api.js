import axios from "axios";

const API_BASE = process.env.REACT_APP_API_BASE || "http://localhost:8000";

const api = axios.create({ baseURL: API_BASE });

api.interceptors.request.use((config) => {
  const token = localStorage.getItem("access_token");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export const register = (data) => api.post("/api/auth/register", data);

export const login = (email, password) => {
  const form = new URLSearchParams();
  form.append("username", email);
  form.append("password", password);
  return api.post("/api/auth/login", form, {
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
  });
};

export const getMe = () => api.get("/api/auth/me");

export const uploadResume = (file) => {
  const form = new FormData();
  form.append("file", file);
  return api.post("/api/resumes/upload", form, {
    headers: { "Content-Type": "multipart/form-data" },
  });
};

export const listResumes = () => api.get("/api/resumes");

export const createJob = (data) => api.post("/api/jobs", data);
export const listJobs = () => api.get("/api/jobs");

export const runAnalysis = (resumeId, jobId) =>
  api.post("/api/analyses", { resume_id: resumeId, job_id: jobId });

export const listAnalyses = () => api.get("/api/analyses");
export const getAnalysis = (id) => api.get(`/api/analyses/${id}`);

export default api;
