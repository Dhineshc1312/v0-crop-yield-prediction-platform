"use client"

import type React from "react"

import { useState, useEffect } from "react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Separator } from "@/components/ui/separator"
import { MapPin, Loader2, Calendar, Droplets, Zap } from "lucide-react"
import { useTranslation } from "@/hooks/use-translation"

interface PredictionFormProps {
  onSubmit: (data: any) => void
  isLoading: boolean
  currentLocation?: { latitude: number; longitude: number } | null
  onGetLocation: () => void
  locationLoading: boolean
  language: string
}

export function PredictionForm({
  onSubmit,
  isLoading,
  currentLocation,
  onGetLocation,
  locationLoading,
  language,
}: PredictionFormProps) {
  const { t } = useTranslation()
  const [formData, setFormData] = useState({
    latitude: "",
    longitude: "",
    state: "Odisha",
    district: "Kendrapara",
    crop: "rice",
    year: new Date().getFullYear().toString(),
    area_ha: "",
    sowing_date: "",
    fertilizer_N_kg: "",
    fertilizer_P_kg: "",
    fertilizer_K_kg: "",
    irrigation_events: "",
    use_satellite: false,
  })

  // Update form when location is available
  useEffect(() => {
    if (currentLocation) {
      setFormData((prev) => ({
        ...prev,
        latitude: currentLocation.latitude.toString(),
        longitude: currentLocation.longitude.toString(),
      }))
    }
  }, [currentLocation])

  const handleInputChange = (field: string, value: string | boolean) => {
    setFormData((prev) => ({
      ...prev,
      [field]: value,
    }))
  }

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()

    // Prepare data for API
    const apiData = {
      latitude: Number.parseFloat(formData.latitude),
      longitude: Number.parseFloat(formData.longitude),
      state: formData.state,
      district: formData.district,
      crop: formData.crop,
      year: Number.parseInt(formData.year),
      farmer_inputs: {
        area_ha: formData.area_ha ? Number.parseFloat(formData.area_ha) : undefined,
        sowing_date: formData.sowing_date || undefined,
        fertilizer_N_kg: formData.fertilizer_N_kg ? Number.parseFloat(formData.fertilizer_N_kg) : undefined,
        fertilizer_P_kg: formData.fertilizer_P_kg ? Number.parseFloat(formData.fertilizer_P_kg) : undefined,
        fertilizer_K_kg: formData.fertilizer_K_kg ? Number.parseFloat(formData.fertilizer_K_kg) : undefined,
        irrigation_events: formData.irrigation_events ? Number.parseInt(formData.irrigation_events) : undefined,
      },
      use_satellite: formData.use_satellite,
      language: language,
    }

    onSubmit(apiData)
  }

  const isFormValid = formData.latitude && formData.longitude && formData.district && formData.crop && formData.year

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      {/* Location Section */}
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <h3 className="text-lg font-semibold flex items-center gap-2">
            <MapPin className="h-5 w-5 text-blue-600" />
            {t("Location")}
          </h3>
          <Button type="button" variant="outline" size="sm" onClick={onGetLocation} disabled={locationLoading}>
            {locationLoading ? <Loader2 className="h-4 w-4 animate-spin mr-2" /> : <MapPin className="h-4 w-4 mr-2" />}
            {t("Use GPS")}
          </Button>
        </div>

        <div className="grid grid-cols-2 gap-4">
          <div>
            <Label htmlFor="latitude">{t("Latitude")}</Label>
            <Input
              id="latitude"
              type="number"
              step="any"
              placeholder="20.508973"
              value={formData.latitude}
              onChange={(e) => handleInputChange("latitude", e.target.value)}
              required
            />
          </div>
          <div>
            <Label htmlFor="longitude">{t("Longitude")}</Label>
            <Input
              id="longitude"
              type="number"
              step="any"
              placeholder="86.418039"
              value={formData.longitude}
              onChange={(e) => handleInputChange("longitude", e.target.value)}
              required
            />
          </div>
        </div>

        <div className="grid grid-cols-2 gap-4">
          <div>
            <Label htmlFor="state">{t("State")}</Label>
            <Select value={formData.state} onValueChange={(value) => handleInputChange("state", value)}>
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="Odisha">Odisha</SelectItem>
                <SelectItem value="West Bengal">West Bengal</SelectItem>
                <SelectItem value="Bihar">Bihar</SelectItem>
                <SelectItem value="Jharkhand">Jharkhand</SelectItem>
              </SelectContent>
            </Select>
          </div>
          <div>
            <Label htmlFor="district">{t("District")}</Label>
            <Select value={formData.district} onValueChange={(value) => handleInputChange("district", value)}>
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="Kendrapara">Kendrapara</SelectItem>
                <SelectItem value="Cuttack">Cuttack</SelectItem>
                <SelectItem value="Puri">Puri</SelectItem>
                <SelectItem value="Khordha">Khordha</SelectItem>
                <SelectItem value="Balasore">Balasore</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </div>
      </div>

      <Separator />

      {/* Crop Information */}
      <div className="space-y-4">
        <h3 className="text-lg font-semibold flex items-center gap-2">
          <Calendar className="h-5 w-5 text-green-600" />
          {t("Crop Details")}
        </h3>

        <div className="grid grid-cols-2 gap-4">
          <div>
            <Label htmlFor="crop">{t("Crop Type")}</Label>
            <Select value={formData.crop} onValueChange={(value) => handleInputChange("crop", value)}>
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="rice">{t("Rice")}</SelectItem>
                <SelectItem value="wheat">{t("Wheat")}</SelectItem>
                <SelectItem value="maize">{t("Maize")}</SelectItem>
                <SelectItem value="sugarcane">{t("Sugarcane")}</SelectItem>
              </SelectContent>
            </Select>
          </div>
          <div>
            <Label htmlFor="year">{t("Year")}</Label>
            <Select value={formData.year} onValueChange={(value) => handleInputChange("year", value)}>
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="2024">2024</SelectItem>
                <SelectItem value="2025">2025</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </div>

        <div className="grid grid-cols-2 gap-4">
          <div>
            <Label htmlFor="area_ha">{t("Farm Area (hectares)")}</Label>
            <Input
              id="area_ha"
              type="number"
              step="0.1"
              placeholder="1.5"
              value={formData.area_ha}
              onChange={(e) => handleInputChange("area_ha", e.target.value)}
            />
          </div>
          <div>
            <Label htmlFor="sowing_date">{t("Sowing Date")}</Label>
            <Input
              id="sowing_date"
              type="date"
              value={formData.sowing_date}
              onChange={(e) => handleInputChange("sowing_date", e.target.value)}
            />
          </div>
        </div>
      </div>

      <Separator />

      {/* Optional Inputs */}
      <div className="space-y-4">
        <h3 className="text-lg font-semibold flex items-center gap-2">
          <Zap className="h-5 w-5 text-purple-600" />
          {t("Farm Inputs")} <span className="text-sm font-normal text-gray-500">({t("Optional")})</span>
        </h3>

        <div className="grid grid-cols-3 gap-4">
          <div>
            <Label htmlFor="fertilizer_N_kg">{t("Nitrogen (kg/ha)")}</Label>
            <Input
              id="fertilizer_N_kg"
              type="number"
              placeholder="120"
              value={formData.fertilizer_N_kg}
              onChange={(e) => handleInputChange("fertilizer_N_kg", e.target.value)}
            />
          </div>
          <div>
            <Label htmlFor="fertilizer_P_kg">{t("Phosphorus (kg/ha)")}</Label>
            <Input
              id="fertilizer_P_kg"
              type="number"
              placeholder="60"
              value={formData.fertilizer_P_kg}
              onChange={(e) => handleInputChange("fertilizer_P_kg", e.target.value)}
            />
          </div>
          <div>
            <Label htmlFor="fertilizer_K_kg">{t("Potassium (kg/ha)")}</Label>
            <Input
              id="fertilizer_K_kg"
              type="number"
              placeholder="40"
              value={formData.fertilizer_K_kg}
              onChange={(e) => handleInputChange("fertilizer_K_kg", e.target.value)}
            />
          </div>
        </div>

        <div>
          <Label htmlFor="irrigation_events">{t("Irrigation Events")}</Label>
          <Input
            id="irrigation_events"
            type="number"
            placeholder="8"
            value={formData.irrigation_events}
            onChange={(e) => handleInputChange("irrigation_events", e.target.value)}
          />
        </div>
      </div>

      <Button type="submit" className="w-full" disabled={!isFormValid || isLoading} size="lg">
        {isLoading ? (
          <>
            <Loader2 className="h-5 w-5 animate-spin mr-2" />
            {t("Predicting...")}
          </>
        ) : (
          <>
            <Droplets className="h-5 w-5 mr-2" />
            {t("Get Prediction & Advisory")}
          </>
        )}
      </Button>
    </form>
  )
}
