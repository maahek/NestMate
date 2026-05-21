import api from './axios'

export const agreementsAPI = {
  getAll: () =>
    api.get('/agreements/'),

  getDetail: (id) =>
    api.get(`/agreements/${id}/`),

  create: (listingId, data) =>
    api.post(`/agreements/create/${listingId}/`, data),

  sign: (id, role) =>
    api.post(`/agreements/${id}/sign/`, { role }),

  download: (id) =>
    api.get(`/agreements/${id}/download/`, {
      responseType: 'blob',
    }),

  regenerate: (id) =>
    api.post(`/agreements/${id}/regenerate/`),

  delete: (id) =>
    api.post(`/agreements/${id}/delete/`),

  getStatus: (id) =>
    api.get(`/agreements/${id}/status/`),
}