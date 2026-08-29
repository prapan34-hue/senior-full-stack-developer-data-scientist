const BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

async function request(path, options) {
  const response = await fetch(`${BASE_URL}${path}`, { headers: { 'Content-Type': 'application/json' }, ...options })
  if (!response.ok) { const body = await response.json().catch(() => ({})); throw new Error(body.detail || 'ไม่สามารถเชื่อมต่อระบบได้') }
  return response.json()
}

export const api = {
  config: () => request('/api/config'),
  dashboard: () => request('/api/dashboard'),
  createObservation: (data) => request('/api/observations', { method: 'POST', body: JSON.stringify(data) }),
  predict: (data) => request('/api/predict', { method: 'POST', body: JSON.stringify(data) }),
}
