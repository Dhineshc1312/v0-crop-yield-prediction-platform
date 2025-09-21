"use client"

import { useState, useEffect, createContext, useContext } from "react"
import { useRouter } from "next/navigation"

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

export function useAuthState() {
  const [farmer, setFarmer] = useState<Farmer | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const router = useRouter()

  // Load farmer from localStorage on mount
  useEffect(() => {
    const loadFarmer = () => {
      try {
        const farmerId = localStorage.getItem("farmer_id")
        const farmerProfile = localStorage.getItem("farmer_profile")
        
        if (farmerId && farmerProfile) {
          const profile = JSON.parse(farmerProfile)
          setFarmer(profile)
        }
      } catch (error) {
        console.error("Error loading farmer from localStorage:", error)
        // Clear invalid data
        localStorage.removeItem("farmer_id")
        localStorage.removeItem("farmer_profile")
      } finally {
        setIsLoading(false)
      }
    }

    loadFarmer()
  }, [])

  const login = async (phone: string) => {
    setIsLoading(true)
    try {
      const response = await fetch("/api/auth/login", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ phone }),
      })

      const data = await response.json()

      if (!response.ok) {
        throw new Error(data.error || "Login failed")
      }

      // Store farmer data
      localStorage.setItem("farmer_id", data.farmer.id.toString())
      localStorage.setItem("farmer_profile", JSON.stringify(data.farmer))
      setFarmer(data.farmer)

    } catch (error) {
      console.error("Login error:", error)
      throw error
    } finally {
      setIsLoading(false)
    }
  }

  const register = async (name: string, phone: string, preferred_lang: string = "en") => {
    setIsLoading(true)
    try {
      const response = await fetch("/api/auth/register", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ name, phone, preferred_lang }),
      })

      const data = await response.json()

      if (!response.ok) {
        throw new Error(data.error || "Registration failed")
      }

      // Store farmer data
      localStorage.setItem("farmer_id", data.farmer.id.toString())
      localStorage.setItem("farmer_profile", JSON.stringify(data.farmer))
      setFarmer(data.farmer)

    } catch (error) {
      console.error("Registration error:", error)
      throw error
    } finally {
      setIsLoading(false)
    }
  }

  const logout = async () => {
    setIsLoading(true)
    try {
      // Call logout API
      await fetch("/api/auth/logout", {
        method: "POST",
      })

      // Clear local storage
      localStorage.removeItem("farmer_id")
      localStorage.removeItem("farmer_profile")
      
      // Clear state
      setFarmer(null)
      
      // Redirect to login
      router.push("/login")

    } catch (error) {
      console.error("Logout error:", error)
      // Even if API call fails, clear local data
      localStorage.removeItem("farmer_id")
      localStorage.removeItem("farmer_profile")
      setFarmer(null)
      router.push("/login")
    } finally {
      setIsLoading(false)
    }
  }

  const updateFarmer = (farmerData: Partial<Farmer>) => {
    if (farmer) {
      const updatedFarmer = { ...farmer, ...farmerData }
      setFarmer(updatedFarmer)
      localStorage.setItem("farmer_profile", JSON.stringify(updatedFarmer))
    }
  }

  return {
    farmer,
    isLoading,
    login,
    register,
    logout,
    updateFarmer,
  }
}