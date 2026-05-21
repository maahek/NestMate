import { create } from 'zustand'
import { listingsAPI } from '../api/listings'

const useListingStore = create((set, get) => ({
  listings:  [],
  listing:   null,
  total:     0,
  page:      1,
  loading:   false,
  error:     null,
  filters:   {},

  setFilters: (filters) => {
    set({ filters, page: 1 })
    get().searchListings(filters)
  },

  searchListings: async (params = {}) => {
    set({ loading: true, error: null })
    try {
      const res = await listingsAPI.search({ ...params, page: get().page })
      set({
        listings: res.data.listings || [],
        total:    res.data.total    || 0,
        loading:  false,
      })
    } catch {
      set({ error: 'Failed to load listings', loading: false })
    }
  },

  fetchListing: async (id) => {
    set({ loading: true, error: null, listing: null })
    try {
      const res = await listingsAPI.detail(id)
      set({ listing: res.data, loading: false })
    } catch {
      set({ error: 'Listing not found', loading: false })
    }
  },

  setPage: (page) => {
    set({ page })
    get().searchListings(get().filters)
  },

  clearListing: () => set({ listing: null }),
}))

export default useListingStore