import api from './axios'

export const chatAPI = {
  getRooms: () =>
    api.get('/chat/api/rooms/'),

  getMessages: (roomId, since = '') =>
    api.get(`/chat/${roomId}/messages/`, {
      params: since ? { since } : {},
    }),

  startChat: (listingId) =>
    api.post(`/chat/start/${listingId}/`),

  markRead: (roomId) =>
    api.post(`/chat/${roomId}/mark-read/`),

  closeChat: (roomId) =>
    api.post(`/chat/${roomId}/close/`),
}