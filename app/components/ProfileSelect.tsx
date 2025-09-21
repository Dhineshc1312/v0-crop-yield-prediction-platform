"use client"

import React, { useState, useEffect } from "react"

// Type definitions
interface FarmerProfile {
  id: number
  name: string
  phone: string
  password?: string
  location_lat: number | null
  location_lon: number | null
  preferred_lang: string
}

// Utility: Async geolocation
const getLocation = (): Promise<GeolocationCoordinates> =>
  new Promise((resolve, reject) => {
    if (!navigator.geolocation) reject("Geolocation not supported")
    else
      navigator.geolocation.getCurrentPosition(
        (pos) => resolve(pos.coords),
        (err) => reject(err.message)
      )
  })

// ------------------- CreateProfileForm -------------------
interface CreateProfileFormProps {
  onCreated: () => void
}

export const CreateProfileForm: React.FC<CreateProfileFormProps> = ({ onCreated }) => {
  const [form, setForm] = useState<FarmerProfile>({
    id: 0,
    name: "",
    phone: "",
    password: "",
    location_lat: null,
    location_lon: null,
    preferred_lang: "en",
  })
  const [error, setError] = useState<string>("")
  const [loading, setLoading] = useState<boolean>(false)

  // Get geolocation on mount
  useEffect(() => {
    getLocation()
      .then((coords) =>
        setForm((f) => ({
          ...f,
          location_lat: coords.latitude,
          location_lon: coords.longitude,
        }))
      )
      .catch(() => {}) // silently fail if user denies location
  }, [])

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value } = e.target
    setForm((prev) => ({
      ...prev,
      [name]: value,
    }))
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError("")
    setLoading(true)

    try {
      const res = await fetch("/api/profiles", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(form),
      })
      const data = await res.json()
      if (!res.ok) throw new Error(data.error || "Failed to create profile")

      onCreated()
      setForm({
        id: 0,
        name: "",
        phone: "",
        password: "",
        location_lat: null,
        location_lon: null,
        preferred_lang: "en",
      })
    } catch (err: any) {
      console.error(err)
      setError(err.message || "Failed to create profile")
    } finally {
      setLoading(false)
    }
  }

  return (
    <form onSubmit={handleSubmit} className="bg-white p-6 rounded-lg shadow-md w-full max-w-md mx-auto mt-6">
      <h2 className="text-xl font-semibold mb-4">Create New Profile</h2>

      {error && <p className="text-red-500 mb-2">{error}</p>}

      <input
        required
        name="name"
        placeholder="Name"
        value={form.name}
        onChange={handleChange}
        className="w-full mb-3 p-2 border rounded"
      />
      <input
        required
        name="phone"
        placeholder="Phone"
        value={form.phone}
        onChange={handleChange}
        className="w-full mb-3 p-2 border rounded"
      />
      <input
        required
        type="password"
        name="password"
        placeholder="Password"
        value={form.password}
        onChange={handleChange}
        className="w-full mb-3 p-2 border rounded"
      />
      <input
        name="location_lat"
        placeholder="Latitude"
        value={form.location_lat ?? ""}
        onChange={handleChange}
        className="w-full mb-3 p-2 border rounded"
      />
      <input
        name="location_lon"
        placeholder="Longitude"
        value={form.location_lon ?? ""}
        onChange={handleChange}
        className="w-full mb-3 p-2 border rounded"
      />
      <select
        name="preferred_lang"
        value={form.preferred_lang}
        onChange={handleChange}
        className="w-full mb-4 p-2 border rounded"
      >
        <option value="en">English</option>
        <option value="ta">Tamil</option>
      </select>

      <button
        type="submit"
        disabled={loading}
        className="w-full bg-green-600 text-white p-2 rounded hover:bg-green-700 disabled:bg-green-300"
      >
        {loading ? "Saving..." : "Create Profile"}
      </button>
    </form>
  )
}

// ------------------- ProfileSelect -------------------
const ProfileSelect: React.FC = () => {
  const [profiles, setProfiles] = useState<FarmerProfile[]>([])
  const [selectedId, setSelectedId] = useState<number | null>(null)
  const [error, setError] = useState<string>("")
  const [loading, setLoading] = useState<boolean>(false)

  const loadProfiles = async () => {
    setLoading(true)
    setError("")
    try {
      const res = await fetch("/api/profiles")
      const data = await res.json()
      setProfiles(data)
      if (data.length > 0 && !selectedId) setSelectedId(data[0].id)
    } catch (err) {
      console.error(err)
      setError("Failed to load profiles")
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadProfiles()
  }, [])

  const selectedProfile = profiles.find((p) => p.id === selectedId) || null

  return (
    <div className="p-6 max-w-3xl mx-auto">
      <h1 className="text-2xl font-bold mb-4">Select Profile</h1>

      {error && <p className="text-red-500 mb-2">{error}</p>}

      {loading ? (
        <p>Loading profiles...</p>
      ) : profiles.length === 0 ? (
        <p>No profiles found. Please create one.</p>
      ) : (
        <div className="flex flex-wrap gap-2 mb-4">
          {profiles.map((p) => (
            <button
              key={p.id}
              onClick={() => setSelectedId(p.id)}
              className={`px-4 py-2 rounded border ${
                selectedId === p.id ? "bg-green-600 text-white" : "bg-white text-black"
              }`}
            >
              {p.name} ({p.phone})
            </button>
          ))}
        </div>
      )}

      {selectedProfile && (
        <div className="bg-white p-4 rounded shadow mb-4">
          <h2 className="font-semibold">Selected Profile</h2>
          <p>Name: {selectedProfile.name}</p>
          <p>Phone: {selectedProfile.phone}</p>
          <p>
            Location:{" "}
            {selectedProfile.location_lat && selectedProfile.location_lon
              ? `${selectedProfile.location_lat.toFixed(6)}, ${selectedProfile.location_lon.toFixed(6)}`
              : "N/A"}
          </p>
          <p>Language: {selectedProfile.preferred_lang.toUpperCase()}</p>
        </div>
      )}

      <CreateProfileForm
        onCreated={() => {
          loadProfiles()
          setSelectedId(null)
        }}
      />
    </div>
  )
}

export default ProfileSelect
