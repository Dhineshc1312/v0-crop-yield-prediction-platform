import { type NextRequest, NextResponse } from "next/server"

// Mock database for demo purposes
// In production, this would connect to your actual database
const mockFarmers: any[] = []

export async function POST(request: NextRequest) {
  try {
    const body = await request.json()
    console.log("[v0] Registration request:", body)

    const { name, phone, preferred_lang } = body

    if (!name || !phone) {
      return NextResponse.json({ error: "Name and phone number are required" }, { status: 400 })
    }

    // Check if farmer already exists
    const existingFarmer = mockFarmers.find((f) => f.phone === phone)
    if (existingFarmer) {
      return NextResponse.json({ error: "Phone number already registered" }, { status: 409 })
    }

    // Create new farmer
    const newFarmer = {
      id: Date.now(),
      name: name.trim(),
      phone: phone.trim(),
      preferred_lang: preferred_lang || "en",
      location_lat: null,
      location_lon: null,
      farms: [],
      created_at: new Date().toISOString(),
      last_login: new Date().toISOString(),
    }

    mockFarmers.push(newFarmer)
    console.log("[v0] Farmer registered successfully:", newFarmer.id)

    return NextResponse.json({
      success: true,
      farmer: newFarmer,
    }, { status: 201 })
  } catch (error) {
    console.error("Registration error:", error)
    return NextResponse.json(
      { error: "Registration failed", details: error instanceof Error ? error.message : "Unknown error" },
      { status: 500 }
    )
  }
}