"use client";

import { useState, useEffect } from "react";
import { FarmerProfileForm } from "@/components/farmer-profile-form";
import { FarmerProfileDisplay } from "@/components/farmer-profile-display";
import { Button } from "@/components/ui/button";
import { ArrowLeft, LogOut } from "lucide-react";
import Link from "next/link";

interface Farm {
  id: number;
  name: string;
  crop_type: string;
  sowing_date: string;
  area_ha: number;
}

interface FarmerProfile {
  id: number;
  name: string;
  phone: string;
  location_lat: number | null;
  location_lon: number | null;
  preferred_lang: string;
  created_at: string;
  farms: Farm[];
}

export default function ProfilePage() {
  const [profiles, setProfiles] = useState<FarmerProfile[]>([]);
  const [profile, setProfile] = useState<FarmerProfile | null>(null);
  const [isEditing, setIsEditing] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [isInitialLoading, setIsInitialLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadProfiles();
  }, []);

  const loadProfiles = async () => {
    try {
      setError(null);
      setIsInitialLoading(true);
      const response = await fetch("/api/profiles");
      if (!response.ok) throw new Error("Failed to fetch profiles");
      const data: FarmerProfile[] = await response.json();

      setProfiles(data);

      if (data.length > 0) {
        setProfile(data[0]); // default to first profile
        setIsEditing(false);
      } else {
        setProfile(null);
        setIsEditing(true);
      }
    } catch (err) {
      console.error("Error loading profiles:", err);
      setError(err instanceof Error ? err.message : "Unknown error");
      setProfile(null);
      setIsEditing(true);
    } finally {
      setIsInitialLoading(false);
    }
  };

  const handleSaveProfile = async (formData: Partial<FarmerProfile>) => {
    setIsLoading(true);
    setError(null);
    try {
      const response = await fetch("/api/profiles", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(formData),
      });

      if (!response.ok) {
        let errorMsg = "Failed to save profile";
        try {
          const errorData = await response.json();
          errorMsg = errorData.error || errorMsg;
        } catch {
          // JSON parsing error fallback
        }
        throw new Error(errorMsg);
      }

      const savedProfile: FarmerProfile = await response.json();

      setProfiles((prev) =>
        prev.some((p) => p.id === savedProfile.id)
          ? prev.map((p) => (p.id === savedProfile.id ? savedProfile : p))
          : [...prev, savedProfile]
      );
      setProfile(savedProfile);
      setIsEditing(false);
    } catch (err) {
      console.error("Error saving profile:", err);
      setError(err instanceof Error ? err.message : "Unknown error");
    } finally {
      setIsLoading(false);
    }
  };

  const handleLogout = () => {
    setProfile(null);
    setIsEditing(profiles.length === 0);
    // Optional: Clear profiles or implement actual logout logic here
    alert(
      profiles.length === 0
        ? "No profiles available. Please create a new one."
        : "Logged out. Please select another profile or create a new one."
    );
  };

  if (isInitialLoading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-green-50 to-blue-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-green-600 mx-auto mb-4"></div>
          <p className="text-muted-foreground">Loading profiles...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-green-50 to-blue-50">
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <div className="mb-8 flex justify-between items-center">
          <Link href="/">
            <Button variant="ghost" className="mb-4">
              <ArrowLeft className="h-4 w-4 mr-2" />
              Back to Home
            </Button>
          </Link>

          {profile && (
            <Button variant="destructive" onClick={handleLogout}>
              <LogOut className="h-4 w-4 mr-2" />
              Logout
            </Button>
          )}
        </div>

        {/* Error Message */}
        {error && (
          <div className="mb-4 text-red-600 font-semibold" role="alert">
            {error}
          </div>
        )}

        {/* Profile Selector */}
        {profiles.length > 0 && !isEditing && (
          <div className="mb-6">
            <h2 className="text-lg font-semibold mb-2">Select Account</h2>
            <div className="flex gap-2 flex-wrap">
              {profiles.map((p) => (
                <Button
                  key={p.id}
                  variant={profile?.id === p.id ? "default" : "outline"}
                  onClick={() => {
                    setProfile(p);
                    setError(null);
                  }}
                  disabled={isLoading}
                >
                  {p.name} ({p.phone})
                </Button>
              ))}
            </div>
          </div>
        )}

        {/* Content */}
        {isEditing ? (
          <FarmerProfileForm
            onSubmit={handleSaveProfile}
            initialData={profile || undefined}
            isLoading={isLoading}
          />
        ) : profile ? (
          <FarmerProfileDisplay
            profile={profile}
            onEdit={() => {
              setIsEditing(true);
              setError(null);
            }}
          />
        ) : (
          <p className="text-muted-foreground">No profile selected</p>
        )}
      </div>
    </div>
  );
}
