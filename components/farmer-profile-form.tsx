"use client"

import type React from "react"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Separator } from "@/components/ui/separator"
import { MapPin, User, Calendar, Sprout } from "lucide-react"
import { useGeolocation } from "@/hooks/use-geolocation"
import { useTranslation } from "@/hooks/use-translation"

interface FarmerProfileData {
  name: string
  phone: string
  location_lat: number | null
  location_lon: number | null
  preferred_lang: string
  farms: {
    name: string
    crop_type: string
    sowing_date: string
    area_ha: number
  }[]
}

interface FarmerProfileFormProps {
  onSubmit: (data: FarmerProfileData) => void
  initialData?: Partial<FarmerProfileData>
  isLoading?: boolean
}

const CROP_TYPES = [
  "rice",
  "wheat",
  "maize",
  "sugarcane",
  "cotton",
  "groundnut",
  "soybean",
  "mustard",
  "sesame",
  "turmeric",
  "ginger",
  "onion",
]

export function FarmerProfileForm({ onSubmit, initialData, isLoading }: FarmerProfileFormProps) {
  const { location, getCurrentLocation, isLoading: locationLoading } = useGeolocation()
  const { translate, language, setLanguage } = useTranslation()

  const [formData, setFormData] = useState<FarmerProfileData>({
    name: initialData?.name || "",
    phone: initialData?.phone || "",
    location_lat: initialData?.location_lat || location?.latitude || null,
    location_lon: initialData?.location_lon || location?.longitude || null,
    preferred_lang: initialData?.preferred_lang || language,
    farms: initialData?.farms || [
      {
        name: "",
        crop_type: "",
        sowing_date: "",
        area_ha: 0,
      },
    ],
  })

  const handleInputChange = (field: keyof FarmerProfileData, value: any) => {
    setFormData((prev) => ({ ...prev, [field]: value }))
  }

  const handleFarmChange = (index: number, field: string, value: any) => {
    const updatedFarms = [...formData.farms]
    updatedFarms[index] = { ...updatedFarms[index], [field]: value }
    setFormData((prev) => ({ ...prev, farms: updatedFarms }))
  }

  const addFarm = () => {
    setFormData((prev) => ({
      ...prev,
      farms: [...prev.farms, { name: "", crop_type: "", sowing_date: "", area_ha: 0 }],
    }))
  }

  const removeFarm = (index: number) => {
    if (formData.farms.length > 1) {
      setFormData((prev) => ({
        ...prev,
        farms: prev.farms.filter((_, i) => i !== index),
      }))
    }
  }

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    onSubmit(formData)
  }

  const handleGetLocation = async () => {
    const loc = await getCurrentLocation()
    if (loc) {
      setFormData((prev) => ({
        ...prev,
        location_lat: loc.latitude,
        location_lon: loc.longitude,
      }))
    }
  }

  return (
    <Card className="w-full max-w-4xl mx-auto">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <User className="h-5 w-5" />
          {translate("Farmer Profile", "କୃଷକ ପ୍ରୋଫାଇଲ୍")}
        </CardTitle>
        <CardDescription>
          {translate(
            "Create or update your farmer profile and farm details",
            "ଆପଣଙ୍କ କୃଷକ ପ୍ରୋଫାଇଲ୍ ଏବଂ ଚାଷ ବିବରଣୀ ସୃଷ୍ଟି କିମ୍ବା ଅପଡେଟ୍ କରନ୍ତୁ",
          )}
        </CardDescription>
      </CardHeader>
      <CardContent>
        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Personal Information */}
          <div className="space-y-4">
            <h3 className="text-lg font-semibold flex items-center gap-2">
              <User className="h-4 w-4" />
              {translate("Personal Information", "ବ୍ୟକ୍ତିଗତ ସୂଚନା")}
            </h3>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="name">{translate("Full Name", "ପୂର୍ଣ୍ଣ ନାମ")} *</Label>
                <Input
                  id="name"
                  value={formData.name}
                  onChange={(e) => handleInputChange("name", e.target.value)}
                  placeholder={translate("Enter your full name", "ଆପଣଙ୍କ ପୂର୍ଣ୍ଣ ନାମ ଲେଖନ୍ତୁ")}
                  required
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="phone">{translate("Phone Number", "ଫୋନ୍ ନମ୍ବର")} *</Label>
                <Input
                  id="phone"
                  type="tel"
                  value={formData.phone}
                  onChange={(e) => handleInputChange("phone", e.target.value)}
                  placeholder={translate("Enter phone number", "ଫୋନ୍ ନମ୍ବର ଲେଖନ୍ତୁ")}
                  required
                />
              </div>
            </div>

            <div className="space-y-2">
              <Label htmlFor="language">{translate("Preferred Language", "ପସନ୍ଦର ଭାଷା")}</Label>
              <Select
                value={formData.preferred_lang}
                onValueChange={(value) => {
                  handleInputChange("preferred_lang", value)
                  setLanguage(value as "en" | "or")
                }}
              >
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="en">English</SelectItem>
                  <SelectItem value="or">ଓଡ଼ିଆ (Odia)</SelectItem>
                </SelectContent>
              </Select>
            </div>

            {/* Location */}
            <div className="space-y-2">
              <Label className="flex items-center gap-2">
                <MapPin className="h-4 w-4" />
                {translate("Location", "ଅବସ୍ଥାନ")}
              </Label>
              <div className="flex gap-2">
                <Button
                  type="button"
                  variant="outline"
                  onClick={handleGetLocation}
                  disabled={locationLoading}
                  className="flex items-center gap-2 bg-transparent"
                >
                  <MapPin className="h-4 w-4" />
                  {locationLoading
                    ? translate("Getting Location...", "ଅବସ୍ଥାନ ପାଇବା...")
                    : translate("Get Current Location", "ବର୍ତ୍ତମାନ ଅବସ୍ଥାନ ପାଆନ୍ତୁ")}
                </Button>
                {formData.location_lat && formData.location_lon && (
                  <div className="flex items-center text-sm text-muted-foreground">
                    {translate("Location:", "ଅବସ୍ଥାନ:")} {formData.location_lat.toFixed(4)},{" "}
                    {formData.location_lon.toFixed(4)}
                  </div>
                )}
              </div>
            </div>
          </div>

          <Separator />

          {/* Farm Information */}
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <h3 className="text-lg font-semibold flex items-center gap-2">
                <Sprout className="h-4 w-4" />
                {translate("Farm Details", "ଚାଷ ବିବରଣୀ")}
              </h3>
              <Button type="button" variant="outline" onClick={addFarm}>
                {translate("Add Farm", "ଚାଷ ଯୋଗ କରନ୍ତୁ")}
              </Button>
            </div>

            {formData.farms.map((farm, index) => (
              <Card key={index} className="p-4">
                <div className="flex items-center justify-between mb-4">
                  <h4 className="font-medium">
                    {translate("Farm", "ଚାଷ")} {index + 1}
                  </h4>
                  {formData.farms.length > 1 && (
                    <Button
                      type="button"
                      variant="ghost"
                      size="sm"
                      onClick={() => removeFarm(index)}
                      className="text-red-600 hover:text-red-700"
                    >
                      {translate("Remove", "ହଟାନ୍ତୁ")}
                    </Button>
                  )}
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor={`farm-name-${index}`}>{translate("Farm Name", "ଚାଷ ନାମ")}</Label>
                    <Input
                      id={`farm-name-${index}`}
                      value={farm.name}
                      onChange={(e) => handleFarmChange(index, "name", e.target.value)}
                      placeholder={translate("Enter farm name", "ଚାଷ ନାମ ଲେଖନ୍ତୁ")}
                    />
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor={`crop-type-${index}`}>{translate("Crop Type", "ଫସଲ ପ୍ରକାର")} *</Label>
                    <Select
                      value={farm.crop_type}
                      onValueChange={(value) => handleFarmChange(index, "crop_type", value)}
                    >
                      <SelectTrigger>
                        <SelectValue placeholder={translate("Select crop", "ଫସଲ ବାଛନ୍ତୁ")} />
                      </SelectTrigger>
                      <SelectContent>
                        {CROP_TYPES.map((crop) => (
                          <SelectItem key={crop} value={crop}>
                            {translate(crop, crop)}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor={`sowing-date-${index}`} className="flex items-center gap-2">
                      <Calendar className="h-4 w-4" />
                      {translate("Sowing Date", "ବୁଣିବା ତାରିଖ")} *
                    </Label>
                    <Input
                      id={`sowing-date-${index}`}
                      type="date"
                      value={farm.sowing_date}
                      onChange={(e) => handleFarmChange(index, "sowing_date", e.target.value)}
                      required
                    />
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor={`area-${index}`}>{translate("Farm Area (Hectares)", "ଚାଷ କ୍ଷେତ୍ର (ହେକ୍ଟର)")} *</Label>
                    <Input
                      id={`area-${index}`}
                      type="number"
                      step="0.1"
                      min="0"
                      value={farm.area_ha}
                      onChange={(e) => handleFarmChange(index, "area_ha", Number.parseFloat(e.target.value) || 0)}
                      placeholder="0.0"
                      required
                    />
                  </div>
                </div>
              </Card>
            ))}
          </div>

          <div className="flex justify-end gap-4">
            <Button type="submit" disabled={isLoading} className="min-w-32">
              {isLoading ? translate("Saving...", "ସେଭ୍ କରୁଛି...") : translate("Save Profile", "ପ୍ରୋଫାଇଲ୍ ସେଭ୍ କରନ୍ତୁ")}
            </Button>
          </div>
        </form>
      </CardContent>
    </Card>
  )
}
