import api from './axios'

export const roommateAPI = {
  getMyProfile: () =>
    api.get('/api/roommate/profile/me/'),

  saveProfile: (data) =>
    api.post('/api/roommate/profile/me/', data),

  getMatches: () =>
    api.get('/api/roommate/matches/'),

  compareUser: (userId) =>
    api.get(`/api/roommate/compare/${userId}/`),

  getAllProfiles: (params) =>
    api.get('/api/roommate/profiles/', { params }),

  getUserProfile: (userId) =>
    api.get(`/api/roommate/profile/${userId}/`),

  // Connect request
  sendConnectRequest: (userId) =>
    api.post(`/roommate/connect/${userId}/`),

  // Get all requests (received + sent)
  getRequests: () =>
    api.get('/roommate/requests/'),

  // Respond to a request
  respondToRequest: (matchId, action) =>
    api.post(`/roommate/respond/${matchId}/`, { action }),

  toggleLooking: () =>
    api.post('/roommate/toggle-looking/'),

  getCityStats: () =>
    api.get('/api/roommate/city-stats/'),
}