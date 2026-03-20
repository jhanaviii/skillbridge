const BASE = '/api';

async function request(path, options = {}) {
  const res = await fetch(`${BASE}${path}`, {
    headers: { 'Content-Type': 'application/json', ...options.headers },
    ...options,
  });
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new Error(body.detail || `API error ${res.status}`);
  }
  return res.json();
}

export function fetchProfiles() {
  return request('/profiles');
}

export function fetchProfile(profileId) {
  return request(`/profiles/${profileId}`);
}

export function createProfile(data) {
  return request('/profiles', {
    method: 'POST',
    body: JSON.stringify(data),
  });
}

export function updateProfile(profileId, updates) {
  return request(`/profiles/${profileId}`, {
    method: 'PATCH',
    body: JSON.stringify(updates),
  });
}

export function fetchJobs(params = {}) {
  const qs = new URLSearchParams();
  if (params.role) qs.set('role', params.role);
  if (params.seniority) qs.set('seniority', params.seniority);
  const q = qs.toString();
  return request(`/jobs${q ? '?' + q : ''}`);
}

export function fetchJob(jobId) {
  return request(`/jobs/${jobId}`);
}

export function analyzeGap(profileId, jobId) {
  return request('/analyze', {
    method: 'POST',
    body: JSON.stringify({ profile_id: profileId, job_id: jobId }),
  });
}

export function generateRoadmap(profileId, jobId) {
  return request('/roadmap', {
    method: 'POST',
    body: JSON.stringify({ profile_id: profileId, job_id: jobId }),
  });
}

export function getInterviewPrep(profileId, jobId) {
  return request('/interview-prep', {
    method: 'POST',
    body: JSON.stringify({ profile_id: profileId, job_id: jobId }),
  });
}

export function fetchHealth() {
  return request('/health');
}
