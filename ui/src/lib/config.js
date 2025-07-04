import { dev } from '$app/environment';

export const API_BASE_URL = dev 
  ? '/api'  // Use proxy in development
  : 'https://mushare.onrender.com/api';  // Direct URL in production

export const API_ENDPOINTS = {
  convert: `${API_BASE_URL}/v1/convert`,
  cacheStats: `${API_BASE_URL}/cache/stats`
}; 