import { NextRequest, NextResponse } from "next/server"
import { farmerDb } from "@/lib/database"

export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url)
    const farmerId = searchParams.get("farmerId")

    if (!farmerId) {
      return NextResponse.json({ error: "Farmer ID is required" }, { status: 400 })
    }

    const farmer = await farmerDb.getFarmerById(parseInt(farmerId))
    if (!farmer) {
      return NextResponse.json({ error: "Farmer not found" }, { status: 404 })
    }

    const farms = await farmerDb.getFarmerFarms(farmer.id)

    return NextResponse.json({
      ...farmer,
      farms
    })
  } catch (error) {
    console.error("Error fetching profile:", error)
    return NextResponse.json({ 
      error: "Failed to fetch profile",
      details: error instanceof Error ? error.message : "Database error"
    }, { status: 500 })
  }
}

export async function POST(request: NextRequest) {
  try {
    const body = await request.json()
    console.log("[Profile] Creating profile with data:", body)

    const { name, phone, email, location_lat, location_lon, preferred_lang, farms } = body

    if (!name || !phone) {
      return NextResponse.json({ error: "Name and phone are required" }, { status: 400 })
    }

    // Check if farmer already exists
    const existingFarmer = await farmerDb.getFarmerByPhone(phone)
    if (existingFarmer) {
      return NextResponse.json({ error: "Phone number already registered" }, { status: 409 })
    }

    // Create farmer
    const newFarmer = await farmerDb.createFarmer({
      name,
      phone,
      email,
      location_lat,
      location_lon,
      preferred_lang
    })

    // Create farms if provided
    const createdFarms = []
    if (farms && farms.length > 0) {
      for (const farm of farms) {
        if (farm.crop_type && farm.sowing_date && farm.area_ha) {
          const createdFarm = await farmerDb.createFarm({
            farmer_id: newFarmer.id,
            name: farm.name || `Farm ${createdFarms.length + 1}`,
            crop_type: farm.crop_type,
            sowing_date: farm.sowing_date,
            area_ha: farm.area_ha
          })
          createdFarms.push(createdFarm)
        }
      }
    }

    console.log("[Profile] Profile created successfully:", newFarmer.id)

    return NextResponse.json({
      ...newFarmer,
      farms: createdFarms
    }, { status: 201 })
  } catch (error) {
    console.error("Error creating profile:", error)
    return NextResponse.json({ 
      error: "Failed to create profile",
      details: error instanceof Error ? error.message : "Database error"
    }, { status: 500 })
  }
}

export async function PUT(request: NextRequest) {
  try {
    const body = await request.json()
    const { id, farms, ...farmerUpdates } = body

    console.log("[Profile] Updating profile:", id, farmerUpdates)

    if (!id) {
      return NextResponse.json({ error: "Farmer ID is required" }, { status: 400 })
    }

    // Update farmer
    const updatedFarmer = await farmerDb.updateFarmer(id, farmerUpdates)

    // Handle farms updates
    let updatedFarms = []
    if (farms) {
      // Get existing farms
      const existingFarms = await farmerDb.getFarmerFarms(id)
      
      // Update or create farms
      for (const farm of farms) {
        if (farm.id) {
          // Update existing farm
          const updatedFarm = await farmerDb.updateFarm(farm.id, {
            name: farm.name,
            crop_type: farm.crop_type,
            sowing_date: farm.sowing_date,
            area_ha: farm.area_ha
          })
          updatedFarms.push(updatedFarm)
        } else if (farm.crop_type && farm.sowing_date && farm.area_ha) {
          // Create new farm
          const newFarm = await farmerDb.createFarm({
            farmer_id: id,
            name: farm.name || `Farm ${updatedFarms.length + 1}`,
            crop_type: farm.crop_type,
            sowing_date: farm.sowing_date,
            area_ha: farm.area_ha
          })
          updatedFarms.push(newFarm)
        }
      }

      // Delete farms that are no longer in the list
      const farmIdsToKeep = farms.filter(f => f.id).map(f => f.id)
      for (const existingFarm of existingFarms) {
        if (!farmIdsToKeep.includes(existingFarm.id)) {
          await farmerDb.deleteFarm(existingFarm.id)
        }
      }
    } else {
      updatedFarms = await farmerDb.getFarmerFarms(id)
    }

    console.log("[Profile] Profile updated successfully")

    return NextResponse.json({
      ...updatedFarmer,
      farms: updatedFarms
    })
  } catch (error) {
    console.error("Error updating profile:", error)
    return NextResponse.json({ 
      error: "Failed to update profile",
      details: error instanceof Error ? error.message : "Database error"
    }, { status: 500 })
  }
}