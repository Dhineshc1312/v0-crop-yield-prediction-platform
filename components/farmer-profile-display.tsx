"use client"

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { User, MapPin, Phone, Calendar, Sprout, Edit, Globe } from "lucide-react"
import { useTranslation } from "@/hooks/use-translation"

interface FarmerProfile {
  id: number
  name: string
  phone: string
  location_lat: number | null
  location_lon: number | null
  preferred_lang: string
  created_at: string
  farms: {
    id: number
    name: string
    crop_type: string
    sowing_date: string
    area_ha: number
  }[]
}

interface FarmerProfileDisplayProps {
  profile: FarmerProfile
  onEdit: () => void
}

export function FarmerProfileDisplay({ profile, onEdit }: FarmerProfileDisplayProps) {
  const { translate } = useTranslation()

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString("en-IN", {
      year: "numeric",
      month: "long",
      day: "numeric",
    })
  }

  const getTotalArea = () => {
    return profile.farms.reduce((total, farm) => total + farm.area_ha, 0)
  }

  return (
    <div className="w-full max-w-4xl mx-auto space-y-6">
      {/* Profile Header */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="h-12 w-12 rounded-full bg-primary/10 flex items-center justify-center">
                <User className="h-6 w-6 text-primary" />
              </div>
              <div>
                <CardTitle className="text-2xl">{profile.name}</CardTitle>
                <CardDescription className="flex items-center gap-4 mt-1">
                  <span className="flex items-center gap-1">
                    <Phone className="h-4 w-4" />
                    {profile.phone}
                  </span>
                  <span className="flex items-center gap-1">
                    <Globe className="h-4 w-4" />
                    {profile.preferred_lang === "or" ? "ଓଡ଼ିଆ" : "English"}
                  </span>
                </CardDescription>
              </div>
            </div>
            <Button onClick={onEdit} variant="outline" className="flex items-center gap-2 bg-transparent">
              <Edit className="h-4 w-4" />
              {translate("Edit Profile", "ପ୍ରୋଫାଇଲ୍ ଏଡିଟ୍ କରନ୍ତୁ")}
            </Button>
          </div>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="flex items-center gap-2 text-sm text-muted-foreground">
              <MapPin className="h-4 w-4" />
              {profile.location_lat && profile.location_lon ? (
                <span>
                  {translate("Location:", "ଅବସ୍ଥାନ:")} {profile.location_lat.toFixed(4)},{" "}
                  {profile.location_lon.toFixed(4)}
                </span>
              ) : (
                <span>{translate("Location not set", "ଅବସ୍ଥାନ ସେଟ୍ ହୋଇନାହିଁ")}</span>
              )}
            </div>
            <div className="flex items-center gap-2 text-sm text-muted-foreground">
              <Calendar className="h-4 w-4" />
              {translate("Member since", "ସଦସ୍ୟ ହେବା ତାରିଖ")} {formatDate(profile.created_at)}
            </div>
            <div className="flex items-center gap-2 text-sm text-muted-foreground">
              <Sprout className="h-4 w-4" />
              {translate("Total Area:", "ମୋଟ କ୍ଷେତ୍ର:")} {getTotalArea().toFixed(1)} {translate("hectares", "ହେକ୍ଟର")}
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Farms Section */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Sprout className="h-5 w-5" />
            {translate("My Farms", "ମୋର ଚାଷ")} ({profile.farms.length})
          </CardTitle>
          <CardDescription>
            {translate("Manage your farm details and crop information", "ଆପଣଙ୍କ ଚାଷ ବିବରଣୀ ଏବଂ ଫସଲ ସୂଚନା ପରିଚାଳନା କରନ୍ତୁ")}
          </CardDescription>
        </CardHeader>
        <CardContent>
          {profile.farms.length === 0 ? (
            <div className="text-center py-8 text-muted-foreground">
              <Sprout className="h-12 w-12 mx-auto mb-4 opacity-50" />
              <p>{translate("No farms added yet", "ଏପର୍ଯ୍ୟନ୍ତ କୌଣସି ଚାଷ ଯୋଗ କରାଯାଇନାହିଁ")}</p>
              <Button onClick={onEdit} variant="outline" className="mt-4 bg-transparent">
                {translate("Add Your First Farm", "ଆପଣଙ୍କର ପ୍ରଥମ ଚାଷ ଯୋଗ କରନ୍ତୁ")}
              </Button>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {profile.farms.map((farm, index) => (
                <Card key={farm.id} className="p-4">
                  <div className="space-y-3">
                    <div className="flex items-center justify-between">
                      <h4 className="font-semibold">{farm.name || `${translate("Farm", "ଚାଷ")} ${index + 1}`}</h4>
                      <Badge variant="secondary" className="capitalize">
                        {translate(farm.crop_type, farm.crop_type)}
                      </Badge>
                    </div>

                    <div className="space-y-2 text-sm text-muted-foreground">
                      <div className="flex items-center gap-2">
                        <Calendar className="h-4 w-4" />
                        <span>
                          {translate("Sown on", "ବୁଣିବା ତାରିଖ")} {formatDate(farm.sowing_date)}
                        </span>
                      </div>
                      <div className="flex items-center gap-2">
                        <Sprout className="h-4 w-4" />
                        <span>
                          {farm.area_ha} {translate("hectares", "ହେକ୍ଟର")}
                        </span>
                      </div>
                    </div>
                  </div>
                </Card>
              ))}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  )
}
