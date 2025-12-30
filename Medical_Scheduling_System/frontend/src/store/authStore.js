import { create } from 'zustand'
import { persist } from 'zustand/middleware'

const useAuthStore = create(
  persist(
    (set) => ({
      user: null,
      token: null,
      isAuthenticated: false,  // ← Start as false

      login: (user, token) => {
        set({
          user,
          token,
          isAuthenticated: true,
        })
      },

      logout: () => {
        set({
          user: null,
          token: null,
          isAuthenticated: false,
        })
      },

      updateUser: (userData) => {
        set((state) => ({
          user: { ...state.user, ...userData },
        }))
      },
    }),
    {
      name: 'auth-storage',
      
      // Check token on rehydration
      onRehydrateStorage: () => (state) => {
        if (state) {
          // Only set authenticated if token actually exists
          state.isAuthenticated = !!state.token
        }
      },
    }
  )
)

export { useAuthStore }