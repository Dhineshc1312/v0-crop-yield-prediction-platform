import { NextRequest, NextResponse } from "next/server";
import { z } from "zod";
import bcrypt from "bcryptjs";

// Profile interface
interface Profile {
  id: number;
  name: string;
  phone: string;
  passwordHash: string;
  location_lat: number | null;
  location_lon: number | null;
  preferred_lang: string;
  created_at: string;
  farms: any[];
}

let profiles: Profile[] = [];

const ProfileSchema = z.object({
  name: z.string().min(1),
  phone: z.string().regex(/^\d{10,14}$/),
  password: z.string().min(6),
  location_lat: z.number().nullable().optional(),
  location_lon: z.number().nullable().optional(),
  preferred_lang: z.string().optional().default("en"),
  farms: z.array(z.any()).optional().default([]),
});
const LoginSchema = z.object({
  phone: z.string().regex(/^\d{10,14}$/),
  password: z.string().min(6),
});

function getCORSHeaders() {
  return {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Methods": "GET,POST,PUT,OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type",
  };
}

export async function OPTIONS() {
  return new NextResponse(null, { status: 204, headers: getCORSHeaders() });
}

export async function GET() {
  try {
    const profileNoHash = profiles.map(({ passwordHash, ...rest }) => rest);
    return NextResponse.json(profileNoHash, { headers: getCORSHeaders() });
  } catch {
    return NextResponse.json(
      { error: "Failed to fetch profiles" },
      { status: 500, headers: getCORSHeaders() }
    );
  }
}

export async function POST(req: NextRequest) {
  try {
    const data = await req.json();
    const result = ProfileSchema.safeParse(data);

    if (!result.success) {
      return NextResponse.json(
        { error: "Validation error", details: result.error.errors.map(e => e.message) },
        { status: 400, headers: getCORSHeaders() }
      );
    }

    if (profiles.some(p => p.phone === result.data.phone)) {
      return NextResponse.json(
        { error: "Profile with this phone already exists" },
        { status: 409, headers: getCORSHeaders() }
      );
    }

    const passwordHash = await bcrypt.hash(result.data.password, 10);
    const newProfile: Profile = {
      id: Date.now(),
      name: result.data.name,
      phone: result.data.phone,
      passwordHash,
      location_lat: result.data.location_lat ?? null,
      location_lon: result.data.location_lon ?? null,
      preferred_lang: result.data.preferred_lang ?? "en",
      created_at: new Date().toISOString(),
      farms: result.data.farms ?? [],
    };

    profiles.push(newProfile);
    const { passwordHash: _, ...profileOnly } = newProfile;
    return NextResponse.json(profileOnly, { status: 201, headers: getCORSHeaders() });
  } catch {
    return NextResponse.json(
      { error: "Failed to save profile" },
      { status: 500, headers: getCORSHeaders() }
    );
  }
}

export async function PUT(req: NextRequest) {
  try {
    const data = await req.json();
    const result = LoginSchema.safeParse(data);

    if (!result.success) {
      return NextResponse.json({ error: "Validation error" }, { status: 400 });
    }

    const profile = profiles.find(p => p.phone === result.data.phone);
    if (!profile) {
      return NextResponse.json({ error: "Profile not found" }, { status: 404 });
    }

    const valid = await bcrypt.compare(result.data.password, profile.passwordHash);
    if (!valid) {
      return NextResponse.json({ error: "Invalid password" }, { status: 401 });
    }

    const { passwordHash: _, ...profileOnly } = profile;
    return NextResponse.json(profileOnly, { headers: getCORSHeaders() });
  } catch {
    return NextResponse.json(
      { error: "Authentication failed" },
      { status: 500, headers: getCORSHeaders() }
    );
  }
}
