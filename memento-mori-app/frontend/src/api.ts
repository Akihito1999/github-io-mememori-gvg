import axios from 'axios'

const backend = import.meta.env.VITE_BACKEND_URL || '' // e.g. https://your-backend.onrender.com

export const api = axios.create({
  baseURL: backend || 'https://api.mentemori.icu',
  timeout: 30000,
})

// WebSocket(GvG)の接続先を返す（backendがあれば /ws/gvg、無ければ本家に直）
export function wsUrlGvg() {
  return backend
    ? backend.replace(/^http/, 'ws') + '/ws/gvg'
    : 'wss://api.mentemori.icu/gvg'
}

export async function getWorlds() {
  return (await api.get('/worlds')).data
}
export async function getWgroups() {
  return (await api.get('/wgroups')).data
}
export async function getPlayerRanking(worldId: number) {
  return (await api.get(`/${worldId}/player_ranking/latest`)).data
}
export async function getLocalGvg(worldId: number) {
  return (await api.get(`/${worldId}/localgvg/latest`)).data
}
