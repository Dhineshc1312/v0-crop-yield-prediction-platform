import { NextRequest, NextResponse } from "next/server"
import { farmerDb } from "@/lib/database"

export async function POST(request: NextRequest) {
  try {
    const body = await request.json()
    console.log("[Auth] Login request:", { phone: body.phone })

    const { phone } = body

    if (!phone) {
      return NextResponse.json({ error: "Phone number is required" }, { status: 400 })
    }

    // Find farmer by phone number
    const farmer = await farmerDb.getFarmerByPhone(phone)

    if (!farmer) {
      return NextResponse.json({ 
        error: "Farmer not found. Please register first." 
      }, { status: 404 })
    }

    // Get farmer's farms
    const farms = await farmerDb.getFarmerFarms(farmer.id)

    console.log("[Auth] Login successful for farmer:", farmer.id)

    return NextResponse.json({
      success: true,
      farmer: {
        ...farmer,
        farms
      },
    })
  } catch (error) {
    console.error("Login error:", error)
    return NextResponse.json(
      { 
        error: "Login failed", 
        details: error instanceof Error ? error.message : "Database connection error" 
      },
      { status: 500 }
    )
  }
}