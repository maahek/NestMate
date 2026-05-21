import api from './axios'

export const authAPI = {
  // Get CSRF token first
  getCSRF: () =>
    api.get('/api/csrf/'),

  login: (email, password) =>
    api.post('/accounts/login/', { email, password }),

  register: (data) =>
    api.post('/accounts/register/', data),

  logout: () =>
    api.post('/accounts/logout/'),

  getProfile: () =>
    api.get('/accounts/profile/'),

  updateProfile: (formData) =>
    api.post('/accounts/profile/', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    }),

  uploadVerification: (formData) =>
    api.post('/accounts/verify/', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    }),

  changePassword: (data) =>
    api.post('/accounts/change-password/', data),

  getPublicProfile: (userId) =>
    api.get(`/accounts/profile/${userId}/`),
}