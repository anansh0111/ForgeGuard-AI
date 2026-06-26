import axios from 'axios'

const BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

const client = axios.create({
  baseURL: BASE_URL,
  timeout: 15000,
  headers: { 'Content-Type': 'application/json' },
})

// ── Machines ──────────────────────────────────────────────────────────────────
export const getMachines = () => client.get('/machines/').then(r => r.data)
export const getMachineStats = () => client.get('/machines/stats').then(r => r.data)

// ── Predictions ───────────────────────────────────────────────────────────────
export const getPredictions = (params = {}) =>
  client.get('/predictions/', { params }).then(r => r.data)

export const runPredict = (payload) =>
  client.post('/predict', payload).then(r => r.data)

// ── Recommendations ───────────────────────────────────────────────────────────
export const getRecommendations = (params = {}) =>
  client.get('/recommendations/', { params }).then(r => r.data)

export const runRecommend = (payload) =>
  client.post('/recommend', payload).then(r => r.data)

// ── Health ────────────────────────────────────────────────────────────────────
export const getHealth = () => client.get('/health').then(r => r.data)

export default client
