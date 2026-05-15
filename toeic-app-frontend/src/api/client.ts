import axios from 'axios'
import type { AxiosInstance } from 'axios'

export const backendOrigin = import.meta.env.VITE_BACKEND_ORIGIN || `${window.location.protocol}//${window.location.hostname}:8000`

export function resolveBackendAssetUrl(url?: string): string {
  if (!url) return ''
  if (/^https?:\/\//i.test(url)) return url
  return new URL(url, backendOrigin).toString()
}

const apiClient: AxiosInstance = axios.create({
  baseURL: '/api/v1',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json'
  }
})

apiClient.interceptors.response.use(
  response => response,
  error => {
    console.error('API Error:', error)
    return Promise.reject(error)
  }
)

export default apiClient
