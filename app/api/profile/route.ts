import { type NextRequest, NextResponse } from "next/server"

// Mock database for demo purposes
// In production, this would connect to your actual database
const mockProfiles: any[] = []

export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url)
    const userId = searchParams.get("userId")

    if (userId) {
      const profile = mockProfiles.find((p) => p.id === Number.parseInt(userId))
      if (!profile) {
        return NextResponse.json({ error: "Profile not found" }, { status: 404 })
      }
      return NextResponse.json(profile)
    }

    // Return all profiles (for admin purposes)
    return NextResponse.json(mockProfiles)
  } catch (error) {
    console.error("Error fetching profile:", error)
    return NextResponse.json({ error: "Failed to fetch profile" }, { status: 500 })
  }
}

export async function POST(request: NextRequest) {
  try {
    const body = await request.json()
    console.log("[v0] Creating profile with data:", body)

    // Validate required fields
    if (!body.name || !body.phone) {
      return NextResponse.json({ error: "Name and phone are required" }, { status: 400 })
    }

    // Create new profile
    const newProfile = {
      id: Date.now(),
      name: body.name,
      phone: body.phone,
      location_lat: body.location_lat || null,
      location_lon: body.location_lon || null,
      preferred_lang: body.preferred_lang || "en",
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
      farms: body.farms || [],
    }

    // Add farms with IDs
    newProfile.farms = newProfile.farms.map((farm: any, index: number) => ({
      id: Date.now() + index,
      name: farm.name || `Farm ${index + 1}`,
      crop_type: farm.crop_type,
      sowing_date: farm.sowing_date,
      area_ha: farm.area_ha,
      created_at: new Date().toISOString(),
    }))

    mockProfiles.push(newProfile)
    console.log("[v0] Profile created successfully:", newProfile.id)

    return NextResponse.json(newProfile, { status: 201 })
  } catch (error) {
    console.error("Error creating profile:", error)
    return NextResponse.json({ error: "Failed to create profile" }, { status: 500 })
  }
}

export async function PUT(request: NextRequest) {
  try {
    const body = await request.json()
    const { id, ...updateData } = body

    console.log("[v0] Updating profile:", id, updateData)

    if (!id) {
      return NextResponse.json({ error: "Profile ID is required" }, { status: 400 })
    }

    const profileIndex = mockProfiles.findIndex((p) => p.id === id)
    if (profileIndex === -1) {
      return NextResponse.json({ error: "Profile not found" }, { status: 404 })
    }

    // Update profile
    const updatedProfile = {
      ...mockProfiles[profileIndex],
      ...updateData,
      updated_at: new Date().toISOString(),
    }

    // Update farms with proper IDs
    if (updateData.farms) {
      updatedProfile.farms = updateData.farms.map((farm: any, index: number) => ({
        id: farm.id || Date.now() + index,
        name: farm.name || `Farm ${index + 1}`,
        crop_type: farm.crop_type,
        sowing_date: farm.sowing_date,
        area_ha: farm.area_ha,
        created_at: farm.created_at || new Date().toISOString(),
      }))
    }

    mockProfiles[profileIndex] = updatedProfile
    console.log("[v0] Profile updated successfully")

    return NextResponse.json(updatedProfile)
  } catch (error) {
    console.error("Error updating profile:", error)
    return NextResponse.json({ error: "Failed to update profile" }, { status: 500 })
  }
}

export async function DELETE(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url)
    const userId = searchParams.get("userId")

    if (!userId) {
      return NextResponse.json({ error: "User ID is required" }, { status: 400 })
    }

    const profileIndex = mockProfiles.findIndex((p) => p.id === Number.parseInt(userId))
    if (profileIndex === -1) {
      return NextResponse.json({ error: "Profile not found" }, { status: 404 })
    }

    mockProfiles.splice(profileIndex, 1)
    console.log("[v0] Profile deleted successfully")

    return NextResponse.json({ message: "Profile deleted successfully" })
  } catch (error) {
    console.error("Error deleting profile:", error)
    return NextResponse.json({ error: "Failed to delete profile" }, { status: 500 })
  }
}
