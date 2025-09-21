import { type NextRequest, NextResponse } from "next/server"

// Mock database for demo purposes
// In production, this would connect to your actual database
const mockFarmers: any[] = []

export async function POST(request: NextRequest) {
  try {
    const body = await request.json()
    console.log("[v0] Login request:", body)

    const { phone } = body

    if (!phone) {
      return NextResponse.json({ error: "Phone number is required" }, { status: 400 })
    }

    // Find farmer by phone number
    const farmer = mockFarmers.find((f) => f.phone === phone)

    if (!farmer) {
      return NextResponse.json({ error: "Farmer not found. Please register first." }, { status: 404 })
    }

    // Update last login
    farmer.last_login = new Date().toISOString()

    console.log("[v0] Login successful for farmer:", farmer.id)

    return NextResponse.json({
      success: true,
      farmer: {
        id: farmer.id,
        name: farmer.name,
        phone: farmer.phone,
        preferred_lang: farmer.preferred_lang,
        location_lat: farmer.location_lat,
        location_lon: farmer.location_lon,
        farms: farmer.farms || [],
        last_login: farmer.last_login,
      },
    })
  } catch (error) {
    console.error("Login error:", error)
    return NextResponse.json(
      { error: "Login failed", details: error instanceof Error ? error.message : "Unknown error" },
      { status: 500 }
    )
  }
}