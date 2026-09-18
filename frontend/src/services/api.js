const API_BASE_URL = 'http://localhost:8000'

async function request(path, options = {}) {
  const token = localStorage.getItem('access_token')

  const headers = {
    'Content-Type': 'application/json',
    ...(options.headers || {}),
  }

  if (token) {
    headers.Authorization = `Bearer ${token}`
  }

  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...options,
    headers,
  })

  const contentType = response.headers.get('content-type') || ''

  const data = contentType.includes('application/json')
    ? await response.json()
    : await response.text()

  if (response.status === 401) {
    localStorage.removeItem('access_token')
  }

  if (!response.ok) {
    const message =
      typeof data === 'object' &&
      data !== null &&
      'detail' in data
        ? typeof data.detail === 'string'
          ? data.detail
          : 'Request failed'
        : typeof data === 'string' && data
          ? data
          : 'Request failed'

    throw new Error(message)
  }

  return data
}

export function loginUser(credentials) {
  return request('/auth/login', {
    method: 'POST',
    body: JSON.stringify(credentials),
  })
}

export function registerUser(userData) {
  return request('/auth/register', {
    method: 'POST',
    body: JSON.stringify(userData),
  })
}

export function getCurrentUser() {
  return request('/users/me', {
    method: 'GET',
  })
}

export function getMyJobs() {
  return request('/jobs/mine', {
    method: 'GET',
  })
}

export function createJob(jobData) {
  return request('/jobs/', {
    method: 'POST',
    body: JSON.stringify(jobData),
  })
}

export function logoutUser() {
  localStorage.removeItem('access_token')
}

export function isAuthenticated() {
  return Boolean(localStorage.getItem('access_token'))
}