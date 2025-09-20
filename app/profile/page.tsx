"use client"

import { useState, useEffect } from "react"
import { FarmerProfileForm } from "@/components/farmer-profile-form"
import { FarmerProfileDisplay } from "@/components/farmer-profile-display"
import { Button } from "@/components/ui/button"
import { ArrowLeft } from "lucide-react"
import Link from "next/link"

interface FarmerProfile {
  id: number
  name: string
  phone: string
  location_lat: number | null
  location_lon: number | null
  preferred_lang: string
  created_at: string
  farms: {
    id: number
    name: string
    crop_type: string
    sowing_date: string
    area_ha: number
  }[]
}

export default function ProfilePage() {
  const [profile, setProfile] = useState<FarmerProfile | null>(null)
  const [isEditing, setIsEditing] = useState(false)
  const [isLoading, setIsLoading] = useState(false)
  const [isInitialLoading, setIsInitialLoading] = useState(true)

  // Load profile on component mount
  useEffect(() => {
    loadProfile()
  }, [])

  const loadProfile = async () => {
    try {
      const savedProfile = localStorage.getItem("farmer_profile")
      if (savedProfile) {
        const profileData = JSON.parse(savedProfile)
        setProfile(profileData)
        setIsEditing(false)
      } else {
        setIsEditing(true) // Show form if no profile exists
      }
    } catch (error) {
      console.error("Error loading profile:", error)
      setIsEditing(true)
    } finally {
      setIsInitialLoading(false)
    }
  }

  const handleSaveProfile = async (formData: any) => {
    setIsLoading(true)
    try {
      console.log("[v0] Saving profile data:", formData)

      const method = profile ? "PUT" : "POST"
      const body = profile ? { ...formData, id: profile.id } : formData

      const response = await fetch("/api/profile", {
        method,
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(body),
      })

      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.error || "Failed to save profile")
      }

      const savedProfile = await response.json()
      console.log("[v0] Profile saved successfully:", savedProfile)

      // Also save to localStorage for demo persistence
      localStorage.setItem("farmer_profile", JSON.stringify(savedProfile))

      setProfile(savedProfile)
      setIsEditing(false)
    } catch (error) {
      console.error("Error saving profile:", error)
      alert(`Failed to save profile: ${error instanceof Error ? error.message : "Unknown error"}`)
    } finally {
      setIsLoading(false)
    }
  }

  if (isInitialLoading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-green-50 to-blue-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-green-600 mx-auto mb-4"></div>
          <p className="text-muted-foreground">Loading profile...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-green-50 to-blue-50">
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <div className="mb-8">
          <Link href="/">
            <Button variant="ghost" className="mb-4">
              <ArrowLeft className="h-4 w-4 mr-2" />
              Back to Home
            </Button>
          </Link>
        </div>

        {/* Content */}
        {isEditing ? (
          <FarmerProfileForm onSubmit={handleSaveProfile} initialData={profile || undefined} isLoading={isLoading} />
        ) : profile ? (
          <FarmerProfileDisplay profile={profile} onEdit={() => setIsEditing(true)} />
        ) : null}
      </div>
    </div>
  )
}
