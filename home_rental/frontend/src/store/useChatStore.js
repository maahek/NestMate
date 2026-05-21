import { create } from 'zustand'
import { chatAPI } from '../api/chat'

const useChatStore = create((set) => ({
  rooms:         [],
  activeRoom:    null,
  messages:      [],
  totalUnread:   0,
  loading:       false,
  roomsError:    null,
  messagesError: null,
  wsConnection:  null,

  fetchRooms: async () => {
    set({ loading: true, roomsError: null })
    try {
      const res = await chatAPI.getRooms()
      set({
        rooms:       res.data.rooms || [],
        totalUnread: res.data.total_unread || 0,
        loading:     false,
        roomsError:  null,
      })
    } catch (err) {
      set({
        loading: false,
        roomsError: err.response?.data?.error || 'Unable to load chats. Please try again.',
      })
    }
  },

  fetchMessages: async (roomId) => {
    set({ loading: true, messagesError: null })
    try {
      const res = await chatAPI.getMessages(roomId)
      set({
        messages:   res.data.messages || [],
        activeRoom: {
          id:            roomId,
          status:        res.data.room_status,
          agreed_rent:   res.data.agreed_rent,
          listing_id:    res.data.listing_id,
          listing_title: res.data.listing_title,
          listing_rent:  res.data.listing_rent,
        },
        loading:      false,
        messagesError: null,
      })
    } catch (err) {
      set({
        loading: false,
        messagesError: err.response?.data?.error || 'Unable to load messages. Please refresh.',
      })
    }
  },

  addMessage: (message) => {
    set(state => ({ messages: [...state.messages, message] }))
  },

  setWsConnection: (ws) => set({ wsConnection: ws }),

  markRoomAsRead: async (roomId) => {
    try {
      await chatAPI.markRead(roomId)
      set(state => ({
        rooms: state.rooms.map(r =>
          r.id === roomId ? { ...r, unread: 0 } : r
        ),
        totalUnread: Math.max(0, state.totalUnread - (
          state.rooms.find(r => r.id === roomId)?.unread || 0
        )),
      }))
    } catch { /* silent */ }
  },

  startChat: async (listingId) => {
    const res = await chatAPI.startChat(listingId)
    return res.data.room_id || res.data.id
  },

  clearActiveRoom: () => set({ activeRoom: null, messages: [], messagesError: null }),
}))

export default useChatStore