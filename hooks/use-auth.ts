"use client"

import { useState, useEffect, createContext, useContext } from "react"

interface AuthState {
  isLoggedIn: boolean
  farmerName: string | null
  farmerPhone: string | null
}

interface AuthContextType extends AuthState {
  login: (name: string, phone: string) => void
  logout: () => void
  checkAuthStatus: () => void
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

export function useAuth() {
  const [authState, setAuthState] = useState<AuthState>({
    isLoggedIn: false,
    farmerName: null,
    farmerPhone: null
  })

  const checkAuthStatus = () => {
    if (typeof window !== 'undefined') {
      const isLoggedIn = localStorage.getItem("farmer_logged_in") === "true"
      const farmerName = localStorage.getItem("farmer_name")
      const farmerPhone = localStorage.getItem("farmer_phone")

      setAuthState({
        isLoggedIn,
        farmerName,
        farmerPhone
      })
    }
  }

  const login = (name: string, phone: string) => {
    localStorage.setItem("farmer_logged_in", "true")
    localStorage.setItem("farmer_name", name)
    localStorage.setItem("farmer_phone", phone)
    
    setAuthState({
      isLoggedIn: true,
      farmerName: name,
      farmerPhone: phone
    })
  }

  const logout = () => {
    localStorage.removeItem("farmer_logged_in")
    localStorage.removeItem("farmer_name")
    localStorage.removeItem("farmer_phone")
    localStorage.removeItem("farmer_profile") // Clear profile data too
    
    setAuthState({
      isLoggedIn: false,
      farmerName: null,
      farmerPhone: null
    })
  }

  useEffect(() => {
    checkAuthStatus()
  }, [])

  return {
    ...authState,
    login,
    logout,
    checkAuthStatus
  }
}

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const auth = useAuth()
  
  return (
    <AuthContext.Provider value={auth}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuthContext() {
  const context = useContext(AuthContext)
  if (context === undefined) {
    throw new Error('useAuthContext must be used within an AuthProvider')
  }
  return context
}