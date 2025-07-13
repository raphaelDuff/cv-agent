// Vite-specific utilities

/**
 * Get asset URL using Vite's import.meta.url
 * @param {string} path - Asset path relative to src/assets
 * @returns {string} - Full asset URL
 */
export const getAssetUrl = (path) => {
  return new URL(`../assets/${path}`, import.meta.url).href;
};

/**
 * Check if running in development mode
 * @returns {boolean}
 */
export const isDevelopment = () => import.meta.env.DEV;

/**
 * Check if running in production mode
 * @returns {boolean}
 */
export const isProduction = () => import.meta.env.PROD;

/**
 * Get environment variable with fallback
 * @param {string} key - Environment variable key (without VITE_ prefix)
 * @param {string} fallback - Fallback value
 * @returns {string}
 */
export const getEnvVar = (key, fallback = '') => {
  return import.meta.env[`VITE_${key}`] || fallback;
};

/**
 * Dynamic import for code splitting
 * @param {string} path - Module path
 * @returns {Promise}
 */
export const dynamicImport = (path) => {
  return import(/* @vite-ignore */ path);
};

/**
 * Log only in development mode
 * @param {...any} args - Arguments to log
 */
export const devLog = (...args) => {
  if (isDevelopment()) {
    console.log('[DEV]', ...args);
  }
};

/**
 * Error handler with better development experience
 * @param {Error} error - Error object
 * @param {string} context - Error context
 */
export const handleError = (error, context = 'Unknown') => {
  if (isDevelopment()) {
    console.error(`[${context}] Error:`, error);
  } else {
    // In production, you might want to send to an error reporting service
    console.error('An error occurred:', error.message);
  }
};