export const BASE_URL = (import.meta.env.VITE_API_URL || 'http://localhost:8000').replace(/\/$/, '')
export const WS_URL = BASE_URL.replace(/^http/, 'ws') + '/ws'

function errorMessage(detail) {
  if (typeof detail === 'string') return detail
  if (Array.isArray(detail)) return detail.map(item => item?.msg || String(item)).join(', ')
  return detail?.message || 'ไม่สามารถเชื่อมต่อระบบได้'
}

async function request(path, options) {
  const controller = new AbortController()
  const timeout = setTimeout(() => controller.abort(), 15000)
  let response
  try {
    response = await fetch(`${BASE_URL}${path}`, {
      ...options,
      headers: { 'Content-Type': 'application/json', ...options?.headers },
      signal: controller.signal,
    })
  } catch (error) {
    if (error.name === 'AbortError') throw new Error('การบันทึกใช้เวลานานเกินไป กรุณาตรวจสอบว่า backend ยังทำงานอยู่')
    throw new Error('ไม่สามารถเชื่อมต่อระบบได้ กรุณาตรวจสอบ backend')
  } finally {
    clearTimeout(timeout)
  }
  if (!response.ok) { const body = await response.json().catch(() => ({})); throw new Error(errorMessage(body.detail)) }
  return response.json()
}

export const api = {
  config: () => request('/api/config'),
  dashboard: () => request('/api/dashboard'),
  createObservation: (data) => request('/api/observations', { method: 'POST', body: JSON.stringify(data) }),
  resetObservations: (adminToken) => request('/api/observations', { method: 'DELETE', headers: { 'X-Admin-Token': adminToken } }),
  predict: (data) => request('/api/predict', { method: 'POST', body: JSON.stringify(data) }),
}
