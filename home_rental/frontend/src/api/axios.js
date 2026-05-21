import axios from 'axios'

// In production use Render URL, in dev use localhost
const BASE_URL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000'

const api = axios.create({
  baseURL:         BASE_URL,
  withCredentials: true,
  headers: {
    'Content-Type': 'application/json',
    'Accept':       'application/json',
  },
})

function getCookie(name) {
  const value = `; ${document.cookie}`
  const parts = value.split(`; ${name}=`)
  if (parts.length === 2) return parts.pop().split(';').shift()
  return null
}

let csrfFetched = false

async function ensureCSRF() {
  if (csrfFetched) return
  try {
    await axios.get(`${BASE_URL}/api/csrf/`, { withCredentials: true })
    csrfFetched = true
  } catch {
    csrfFetched = true
  }
}

api.interceptors.request.use(async (config) => {
  const method = config.method?.toLowerCase()
  if (['post', 'put', 'patch', 'delete'].includes(method)) {
    await ensureCSRF()
    const token = getCookie('csrftoken')
    if (token) config.headers['X-CSRFToken'] = token
  }
  return config
})

api.interceptors.response.use(
  response => response,
  async error => {
    if (error.response?.status === 403) {
      csrfFetched = false
      await ensureCSRF()
    }
    return Promise.reject(error)
  }
)

export default api