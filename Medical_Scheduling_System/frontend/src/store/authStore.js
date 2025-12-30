import { create } from 'zustand'
import { persist, createJSONStorage } from 'zustand/middleware'

export const useAuthStore = create(
  persist(
    (set) => ({
      // State
      user: null,
      token: null,
      isAuthenticated: false,
      loading: false,

      // Patient info (persisted)
      patientId: null,
      phoneNumber: null,

      // Actions
      setLoading: (loading) => set({ loading }),

      setPatientInfo: ({ patientId, phoneNumber }) =>
        set({
          patientId,
          phoneNumber,
        }),

      login: (userData, authToken) => {
        set({
          user: userData,
          token: authToken,
          isAuthenticated: true,
          loading: false,
        })
      },

      logout: () => {
        set({
          user: null,
          token: null,
          isAuthenticated: false,
          loading: false,
          patientId: null,
          phoneNumber: null,
        })
      },

      updateUser: (userData) => {
        set((state) => ({
          user: { ...(state.user || {}), ...userData },
        }))
      },
    }),
    {
      name: 'auth-storage',
      storage: acreateJSONStorage(() => localStorage),
    }
  )
)
