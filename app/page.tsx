"use client"

import { useState } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Separator } from "@/components/ui/separator"
import { MapPin, Sprout, TrendingUp, Globe } from "lucide-react"
import { PredictionForm } from "@/components/prediction-form"
import { PredictionResults } from "@/components/prediction-results"
import { LanguageToggle } from "@/components/language-toggle"
import { useTranslation } from "@/hooks/use-translation"
import { useGeolocation } from "@/hooks/use-geolocation"

export default function HomePage() {
  const { t, language, setLanguage } = useTranslation()
  const { location, loading: locationLoading, error: locationError, getCurrentLocation } = useGeolocation()
  const [prediction, setPrediction] = useState(null)
  const [isLoading, setIsLoading] = useState(false)

  const handlePredictionSubmit = async (formData: any) => {
    setIsLoading(true)
    try {
      const response = await fetch("/api/predict", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          ...formData,
          language: language,
        }),
      })

      if (!response.ok) {
        throw new Error("Prediction failed")
      }

      const result = await response.json()
      setPrediction(result)
    } catch (error) {
      console.error("Prediction error:", error)
      // Handle error appropriately
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-green-50 to-blue-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center gap-3">
              <div className="bg-green-600 p-2 rounded-lg">
                <Sprout className="h-6 w-6 text-white" />
              </div>
              <div>
                <h1 className="text-xl font-bold text-gray-900">{t("AI Crop Yield Predictor")}</h1>
                <p className="text-sm text-gray-600">{t("Smart farming advisory for Odisha")}</p>
              </div>
            </div>
            <LanguageToggle language={language} onLanguageChange={setLanguage} />
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Hero Section */}
        <div className="text-center mb-12">
          <h2 className="text-4xl font-bold text-gray-900 mb-4">{t("Predict Your Crop Yield")}</h2>
          <p className="text-xl text-gray-600 max-w-3xl mx-auto mb-8">
            {t("Get AI-powered yield predictions and personalized farming advisory in English and Odia")}
          </p>

          {/* Key Features */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
            <Card className="text-center">
              <CardContent className="pt-6">
                <TrendingUp className="h-12 w-12 text-green-600 mx-auto mb-4" />
                <h3 className="font-semibold text-lg mb-2">{t("Accurate Predictions")}</h3>
                <p className="text-gray-600 text-sm">{t("ML models trained on weather, soil, and historical data")}</p>
              </CardContent>
            </Card>

            <Card className="text-center">
              <CardContent className="pt-6">
                <MapPin className="h-12 w-12 text-blue-600 mx-auto mb-4" />
                <h3 className="font-semibold text-lg mb-2">{t("Location-Based")}</h3>
                <p className="text-gray-600 text-sm">{t("GPS-enabled recommendations for your specific location")}</p>
              </CardContent>
            </Card>

            <Card className="text-center">
              <CardContent className="pt-6">
                <Globe className="h-12 w-12 text-purple-600 mx-auto mb-4" />
                <h3 className="font-semibold text-lg mb-2">{t("Bilingual Support")}</h3>
                <p className="text-gray-600 text-sm">{t("Available in English and Odia languages")}</p>
              </CardContent>
            </Card>
          </div>
        </div>

        {/* Main Content */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Prediction Form */}
          <div>
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Sprout className="h-5 w-5 text-green-600" />
                  {t("Crop Information")}
                </CardTitle>
                <CardDescription>{t("Enter your farm details to get yield prediction and advisory")}</CardDescription>
              </CardHeader>
              <CardContent>
                <PredictionForm
                  onSubmit={handlePredictionSubmit}
                  isLoading={isLoading}
                  currentLocation={location}
                  onGetLocation={getCurrentLocation}
                  locationLoading={locationLoading}
                  language={language}
                />
              </CardContent>
            </Card>
          </div>

          {/* Results */}
          <div>
            {prediction ? (
              <PredictionResults prediction={prediction} language={language} />
            ) : (
              <Card className="h-full flex items-center justify-center">
                <CardContent className="text-center py-12">
                  <div className="bg-gray-100 rounded-full p-6 w-24 h-24 mx-auto mb-4 flex items-center justify-center">
                    <TrendingUp className="h-12 w-12 text-gray-400" />
                  </div>
                  <h3 className="text-lg font-semibold text-gray-900 mb-2">{t("Ready for Prediction")}</h3>
                  <p className="text-gray-600">
                    {t("Fill in the form to get your crop yield prediction and farming advisory")}
                  </p>
                </CardContent>
              </Card>
            )}
          </div>
        </div>

        {/* Additional Information */}
        <div className="mt-16">
          <Card>
            <CardHeader>
              <CardTitle>{t("How It Works")}</CardTitle>
              <CardDescription>
                {t("Our AI system combines multiple data sources for accurate predictions")}
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
                <div className="text-center">
                  <div className="bg-blue-100 rounded-full p-4 w-16 h-16 mx-auto mb-4 flex items-center justify-center">
                    <span className="text-2xl font-bold text-blue-600">1</span>
                  </div>
                  <h4 className="font-semibold mb-2">{t("Location Data")}</h4>
                  <p className="text-sm text-gray-600">{t("GPS coordinates and district information")}</p>
                </div>

                <div className="text-center">
                  <div className="bg-green-100 rounded-full p-4 w-16 h-16 mx-auto mb-4 flex items-center justify-center">
                    <span className="text-2xl font-bold text-green-600">2</span>
                  </div>
                  <h4 className="font-semibold mb-2">{t("Weather & Soil")}</h4>
                  <p className="text-sm text-gray-600">{t("Real-time weather and soil data from APIs")}</p>
                </div>

                <div className="text-center">
                  <div className="bg-purple-100 rounded-full p-4 w-16 h-16 mx-auto mb-4 flex items-center justify-center">
                    <span className="text-2xl font-bold text-purple-600">3</span>
                  </div>
                  <h4 className="font-semibold mb-2">{t("AI Analysis")}</h4>
                  <p className="text-sm text-gray-600">{t("Machine learning models process all data")}</p>
                </div>

                <div className="text-center">
                  <div className="bg-orange-100 rounded-full p-4 w-16 h-16 mx-auto mb-4 flex items-center justify-center">
                    <span className="text-2xl font-bold text-orange-600">4</span>
                  </div>
                  <h4 className="font-semibold mb-2">{t("Advisory")}</h4>
                  <p className="text-sm text-gray-600">{t("Personalized recommendations in your language")}</p>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      </main>

      {/* Footer */}
      <footer className="bg-gray-900 text-white mt-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            <div>
              <div className="flex items-center gap-3 mb-4">
                <div className="bg-green-600 p-2 rounded-lg">
                  <Sprout className="h-6 w-6 text-white" />
                </div>
                <span className="text-xl font-bold">AI Harvesters</span>
              </div>
              <p className="text-gray-400">
                {t(
                  "Empowering farmers with AI-driven insights for better crop yields and sustainable farming practices.",
                )}
              </p>
            </div>

            <div>
              <h3 className="text-lg font-semibold mb-4">{t("Features")}</h3>
              <ul className="space-y-2 text-gray-400">
                <li>{t("Yield Prediction")}</li>
                <li>{t("Weather Integration")}</li>
                <li>{t("Soil Analysis")}</li>
                <li>{t("Bilingual Support")}</li>
              </ul>
            </div>

            <div>
              <h3 className="text-lg font-semibold mb-4">{t("Support")}</h3>
              <ul className="space-y-2 text-gray-400">
                <li>{t("Documentation")}</li>
                <li>{t("API Reference")}</li>
                <li>{t("Contact Support")}</li>
                <li>{t("Feedback")}</li>
              </ul>
            </div>
          </div>

          <Separator className="my-8 bg-gray-800" />

          <div className="text-center text-gray-400">
            <p>&copy; 2024 AI Harvesters. {t("Built for Smart India Hackathon 2024.")}</p>
          </div>
        </div>
      </footer>
    </div>
  )
}
