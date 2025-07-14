// Vite Environment Configuration
export const config = {
  apiBaseUrl: import.meta.env.VITE_API_BASE_URL || "http://localhost:8000",
  appTitle: import.meta.env.VITE_APP_TITLE || "CV Agent",
  appVersion: import.meta.env.VITE_APP_VERSION || "1.0.0",
  isDev: import.meta.env.DEV,
  isProd: import.meta.env.PROD,
  mode: import.meta.env.MODE,
};

// API endpoints configuration
export const API_ENDPOINTS = {
  upload: `${config.apiBaseUrl}/upload`,
  ask: `${config.apiBaseUrl}/ask`,
  health: `${config.apiBaseUrl}/health`,
  graphInfo: `${config.apiBaseUrl}/graph-info`,
  graphImage: `${config.apiBaseUrl}/graph-image`,
  graphMermaid: `${config.apiBaseUrl}/graph-mermaid`,
  examples: `${config.apiBaseUrl}/examples`,
};

export default config;
