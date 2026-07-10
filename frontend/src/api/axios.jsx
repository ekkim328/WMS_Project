import axios from "axios";

const defaultBaseURL = import.meta.env.DEV ? "http://127.0.0.1:8081" : "";

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL ?? defaultBaseURL,
  withCredentials: true,
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem("access_token");

  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }

  return config;
});

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem("access_token");
    }

    return Promise.reject(error);
  },
);

export default api;
