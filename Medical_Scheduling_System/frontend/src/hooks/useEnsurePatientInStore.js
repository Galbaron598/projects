import { useCallback, useRef } from 'react'
import { useAuthStore } from '../store/authStore'
import { patientsAPI } from '../services/api'

export default function useEnsurePatientInStore() {
  const userPhoneNumber = useAuthStore((s) => s.user?.phoneNumber)
  const setPatientInfo = useAuthStore((s) => s.setPatientInfo)

  // ✅ prevents double "create patient" in React 18 StrictMode/dev
  const ensurePromiseRef = useRef(null)

  const ensurePatientInStore = useCallback(async () => {
    if (ensurePromiseRef.current) return ensurePromiseRef.current

    ensurePromiseRef.current = (async () => {
      const phone = String(userPhoneNumber || '').replace(/\D/g, '').trim()
      if (!phone) throw new Error('Missing user phoneNumber (from auth)')

      const existsRes = await patientsAPI.exists(phone)
      const exists = Boolean(existsRes?.data?.exists)
      const existingId = existsRes?.data?.id

      if (exists && existingId) {
        const id = Number(existingId)
        setPatientInfo({ patientId: id, phoneNumber: phone })
        return id
      }

      const createdRes = await patientsAPI.create(phone)
      const created = createdRes?.data

      if (!created?.id) throw new Error('Patient created but missing id from server response')

      const newId = Number(created.id)
      setPatientInfo({
        patientId: newId,
        phoneNumber: created.phone_number || phone,
      })
      return newId
    })()

    try {
      return await ensurePromiseRef.current
    } finally {
      ensurePromiseRef.current = null
    }
  }, [setPatientInfo, userPhoneNumber])

  return ensurePatientInStore
}
