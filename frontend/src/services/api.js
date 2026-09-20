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

  const contentType =
    response.headers.get('content-type') || ''

  const data = contentType.includes(
    'application/json',
  )
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

export function getAvailableJobs() {
  return request('/jobs/available', {
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
  return Boolean(
    localStorage.getItem('access_token'),
  )
}

export function getJob(jobId) {
  return request(`/jobs/${jobId}`, {
    method: 'GET',
  })
}

export function getAssignment(assignmentId) {
  return request(`/assignments/${assignmentId}`, {
    method: 'GET',
  })
}

export function getMyJobInterests() {
  return request('/job-interests/mine', {
    method: 'GET',
  })
}

export function createJobInterest(jobId) {
  return request('/job-interests/', {
    method: 'POST',
    body: JSON.stringify({
      job_id: jobId,
    }),
  })
}

export function withdrawJobInterest(interestId) {
  return request(
    `/job-interests/${interestId}/withdraw`,
    {
      method: 'PATCH',
    },
  )
}

export function getJobInterests(jobId) {
  return request(`/jobs/${jobId}/interests`, {
    method: 'GET',
  })
}

export function createAssignment(jobId, workerId) {
  return request('/assignments/', {
    method: 'POST',
    body: JSON.stringify({
      job_id: jobId,
      worker_id: workerId,
    }),
  })
}

export function getMyAssignments() {
  return request('/assignments/mine', {
    method: 'GET',
  })
}

export function acceptAssignment(assignmentId) {
  return request(
    `/assignments/${assignmentId}/accept`,
    {
      method: 'PATCH',
    },
  )
}

export function rejectAssignment(assignmentId) {
  return request(
    `/assignments/${assignmentId}/reject`,
    {
      method: 'PATCH',
    },
  )
}

export function getMyWorks() {
  return request('/works/mine', {
    method: 'GET',
  })
}

export function createWork(
  assignmentId,
  description = null,
) {
  return request('/works/', {
    method: 'POST',
    body: JSON.stringify({
      assignment_id: assignmentId,
      description,
    }),
  })
}

export function getWork(workId) {
  return request(`/works/${workId}`, {
    method: 'GET',
  })
}

export function getWorkByAssignment(assignmentId) {
  return request(
    `/works/assignment/${assignmentId}`,
    {
      method: 'GET',
    },
  )
}

export function updateWork(
  workId,
  description,
) {
  return request(`/works/${workId}`, {
    method: 'PUT',
    body: JSON.stringify({
      description,
    }),
  })
}

export function updateWorkStatus(
  workId,
  status,
) {
  return request(`/works/${workId}/status`, {
    method: 'PATCH',
    body: JSON.stringify({
      status,
    }),
  })
}

export function getEvidenceForWork(workId) {
  return request(`/evidence/work/${workId}`, {
    method: 'GET',
  })
}

export function createEvidence(
  workId,
  evidenceType,
  url,
  description = null,
) {
  return request('/evidence/', {
    method: 'POST',
    body: JSON.stringify({
      work_id: workId,
      evidence_type: evidenceType,
      url,
      description,
    }),
  })
}

export function getWorkByJob(jobId) {
  return request(`/works/job/${jobId}`, {
    method: 'GET',
  })
}

export function getConfirmationForWork(workId) {
  return request(`/confirmations/work/${workId}`, {
    method: 'GET',
  })
}

export function createConfirmation(
  workId,
  comment = null,
) {
  return request('/confirmations/', {
    method: 'POST',
    body: JSON.stringify({
      work_id: workId,
      comment,
    }),
  })
}

export function getPaymentForWork(workId) {
  return request(`/payments/work/${workId}`, {
    method: 'GET',
  })
}

export function createPayment(
  workId,
  transactionReference = null,
) {
  return request('/payments/', {
    method: 'POST',
    body: JSON.stringify({
      work_id: workId,
      transaction_reference: transactionReference,
    }),
  })
}

export function markPaymentAsPaid(paymentId) {
  return request(
    `/payments/${paymentId}/paid`,
    {
      method: 'PATCH',
    },
  )
}

export function getReputationForWork(workId) {
  return request(`/reputations/work/${workId}`, {
    method: 'GET',
  })
}

export function createReputation(
  workId,
  rating,
  comment = null,
) {
  return request('/reputations/', {
    method: 'POST',
    body: JSON.stringify({
      work_id: workId,
      rating,
      comment,
    }),
  })
}