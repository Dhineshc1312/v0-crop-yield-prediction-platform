"use client"

import { createContext, useContext } from "react"
import { useAuthState } from "@/hooks/use-auth"

interface Farmer {
  id: number
  name: string
  phone: string
  preferred_lang: string
  location_lat: number | null
  location_lon: number | null
  farms: any[]
  last_login?: string
}

interface AuthContextType {
  farmer: Farmer | null
  isLoading: boolean
  login: (phone: string) => Promise<void>
  register: (name: string, phone: string, preferred_lang?: string) => Promise<void>
  logout: () => Promise<void>
  updateFarmer: (farmerData: Partial<Farmer>) => void
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

export function useAuth() {
  const context = useContext(AuthContext)
  if (context === undefined) {
    throw new Error("useAuth must be used within an AuthProvider")
  }
  return context
}

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const auth = useAuthState()

  return (
    <AuthContext.Provider value={auth}>
      {children}
    </AuthContext.Provider>
  )
}