export const useAuthStore = create(
  persist(
    (set, get) => ({
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

      // Getters
      getUser: () => get().user,
      getToken: () => get().token,
      getPatientId: () => get().patientId,
      getPhoneNumber: () => get().phoneNumber,
    }),
    {
      name: 'auth-storage',
      storage: createJSONStorage(() => localStorage),
    }
  )
)