import { NextRequest, NextResponse } from "next/server"
import { farmerDb } from "@/lib/database"

export async function POST(request: NextRequest) {
  try {
    const body = await request.json()
    console.log("[Auth] Registration request:", { 
      name: body.name, 
      phone: body.phone,
      preferred_lang: body.preferred_lang 
    })

    const { name, phone, email, preferred_lang, location_lat, location_lon } = body

    if (!name || !phone) {
      return NextResponse.json({ 
        error: "Name and phone number are required" 
      }, { status: 400 })
    }

    // Check if farmer already exists
    const existingFarmer = await farmerDb.getFarmerByPhone(phone)
    if (existingFarmer) {
      return NextResponse.json({ 
        error: "Phone number already registered" 
      }, { status: 409 })
    }

    // Create new farmer
    const newFarmer = await farmerDb.createFarmer({
      name: name.trim(),
      phone: phone.trim(),
      email: email?.trim(),
      location_lat,
      location_lon,
      preferred_lang: preferred_lang || "en"
    })

    console.log("[Auth] Farmer registered successfully:", newFarmer.id)

    return NextResponse.json({
      success: true,
      farmer: {
        ...newFarmer,
        farms: []
      },
    }, { status: 201 })
  } catch (error) {
    console.error("Registration error:", error)
    return NextResponse.json(
      { 
        error: "Registration failed", 
        details: error instanceof Error ? error.message : "Database connection error" 
      },
      { status: 500 }
    )
  }
}