
import api from './axios'

export const listingsAPI = {
  search: (params = {}) =>
    api.get('/api/listings/', { params }),

  detail: (id) =>
    api.get(`/api/listings/${id}/`),

  create: (formData) =>
    api.post('/api/listings/create/', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    }),

  priceCheck: (params) =>
    api.get('/api/listings/price-check/', { params }),

  scamCheck: (id) =>
    api.get(`/api/listings/scam-check/${id}/`),

  nearby: (params) =>
    api.get('/api/listings/nearby/', { params }),

  toggleSave: (id) =>
    api.post(`/listing/${id}/save/`),

  submitReview: (id, data) =>
    api.post(`/listing/${id}/review/`, data),

  marketData: (params) =>
    api.get('/analytics/api/market-data/', { params }),
}