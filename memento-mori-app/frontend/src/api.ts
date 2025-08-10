import axios from 'axios'

const backend = import.meta.env.VITE_BACKEND_URL || '' // e.g. https://your-backend.onrender.com

// If no backend provided, use the public API directly (must allow CORS)
export const api = axios.create({
  baseURL: backend || 'https://api.mentemori.icu',
  timeout: 30000,
})

export function wsUrl(path: string) {
  // derive ws url from backend (preferred) or same-origin
  if (backend) {
    return backend.replace(/^http/, 'ws') + path
  }
  // fallback: relative ws
  const loc = window.location
  const proto = loc.protocol === 'https:' ? 'wss:' : 'ws:'
  return `${proto}//${loc.host}${path}`
}

export async function getWorlds() { return (await api.get('/worlds')).data }
export async function getWgroups() { return (await api.get('/wgroups')).data }
export async function getPlayerRanking(worldId: number) {
  return (await api.get(`/${worldId}/player_ranking/latest`)).data
}
export async function getLocalGvg(worldId: number) {
  return (await api.get(`/${worldId}/localgvg/latest`)).data
}

import axios from 'axios'

const backend = import.meta.env.VITE_BACKEND_URL || '' // e.g. https://your-backend.onrender.com

// If no backend provided, use the public API directly (must allow CORS)
export const api = axios.create({
  baseURL: backend || 'https://api.mentemori.icu',
  timeout: 30000,
})

export async function getWorlds() { return (await api.get('/worlds')).data }
export async function getWgroups() { return (await api.get('/wgroups')).data }
export async function getPlayerRanking(worldId: number) {
  return (await api.get(`/${worldId}/player_ranking/latest`)).data
}
export async function getLocalGvg(worldId: number) {
  return (await api.get(`/${worldId}/localgvg/latest`)).data
}

import axios from 'axios'

const backend = import.meta.env.VITE_BACKEND_URL || '' // e.g. https://your-backend.onrender.com

// If no backend provided, use the public API directly (must allow CORS)
export const api = axios.create({
  baseURL: backend || 'https://api.mentemori.icu',
  timeout: 30000,
})

export async function getWorlds() { return (await api.get('/worlds')).data }
export async function getWgroups() { return (await api.get('/wgroups')).data }
export async function getPlayerRanking(worldId: number) {
  return (await api.get(`/${worldId}/player_ranking/latest`)).data
}