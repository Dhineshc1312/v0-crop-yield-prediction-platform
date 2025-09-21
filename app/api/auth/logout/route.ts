import { type NextRequest, NextResponse } from "next/server"

export async function POST(request: NextRequest) {
  try {
    console.log("[v0] Logout request received")

    // In a real application, you would:
    // 1. Invalidate the session token
    // 2. Clear server-side session data
    // 3. Update last logout time in database

    return NextResponse.json({
      success: true,
      message: "Logged out successfully",
    })
  } catch (error) {
    console.error("Logout error:", error)
    return NextResponse.json(
      { error: "Logout failed", details: error instanceof Error ? error.message : "Unknown error" },
      { status: 500 }
    )
  }
}