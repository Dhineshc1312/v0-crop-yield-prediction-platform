"use client"

import { useState } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Separator } from "@/components/ui/separator"
import { Button } from "@/components/ui/button"
import { MapPin, Sprout, TrendingUp, Globe, User, Leaf, Sun, Droplets, Smartphone, Brain, Target } from "lucide-react"
import { PredictionForm } from "@/components/prediction-form"
import { PredictionResults } from "@/components/prediction-results"
import { LanguageToggle } from "@/components/language-toggle"
import { useTranslation } from "@/hooks/use-translation"
import { useGeolocation } from "@/hooks/use-geolocation"
import { useAuth } from "@/components/auth-provider"
import Link from "next/link"

export default function HomePage() {
  const { t, language, setLanguage } = useTranslation()
  const { location, loading: locationLoading, error: locationError, getCurrentLocation } = useGeolocation()
  const { farmer, logout } = useAuth()
  const [prediction, setPrediction] = useState(null)
  const [isLoading, setIsLoading] = useState(false)

  const handlePredictionSubmit = async (formData: any) => {
    setIsLoading(true)
    console.log("[v0] Starting prediction request with data:", formData)

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

      console.log("[v0] API response status:", response.status)

      if (!response.ok) {
        const errorData = await response.json()
        console.error("[v0] API error response:", errorData)
        throw new Error(errorData.details || "Prediction failed")
      }

      const result = await response.json()
      console.log("[v0] Prediction result received:", result)
      setPrediction(result)
    } catch (error) {
      console.error("Prediction error:", error)
      alert(`Prediction failed: ${error instanceof Error ? error.message : "Unknown error"}`)
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-background">
      <header className="bg-card/80 backdrop-blur-md shadow-sm border-b border-border/50 sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-20">
            <div className="flex items-center gap-4">
              <div className="bg-gradient-to-br from-primary to-primary/80 p-3 rounded-xl shadow-lg">
                <Sprout className="h-7 w-7 text-primary-foreground" />
              </div>
              <div>
                <h1 className="text-2xl font-bold text-foreground">{t("AI Crop Yield Predictor")}</h1>
                <p className="text-sm text-muted-foreground font-medium">{t("Smart farming advisory for Odisha")}</p>
              </div>
            </div>
            <div className="flex items-center gap-4">
              {farmer ? (
                <div className="flex items-center gap-2">
                  <span className="text-sm text-muted-foreground">
                    {t("Welcome")}, {farmer.name}
                  </span>
                  <Link href="/profile">
                    <Button
                      variant="outline"
                      className="flex items-center gap-2 border-primary/30 hover:bg-primary/10 bg-card/50 backdrop-blur-sm font-medium"
                    >
                      <User className="h-4 w-4" />
                      {t("My Profile")}
                    </Button>
                  </Link>
                  <Button
                    variant="ghost"
                    onClick={logout}
                    className="text-sm text-muted-foreground hover:text-foreground"
                  >
                    {t("Logout")}
                  </Button>
                </div>
              ) : (
                <Link href="/login">
                  <Button
                    variant="outline"
                    className="flex items-center gap-2 border-primary/30 hover:bg-primary/10 bg-card/50 backdrop-blur-sm font-medium"
                  >
                    <User className="h-4 w-4" />
                    {t("Login")}
                  </Button>
                </Link>
              )}
              <div className="language-switcher">
                <LanguageToggle language={language} onLanguageChange={setLanguage} />
              </div>
            </div>
          </div>
        </div>
      </header>

      <section className="relative overflow-hidden">
        <div className="hero-gradient">
          <div className="agricultural-pattern">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20">
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
                <div className="text-center lg:text-left">
                  <h2 className="text-5xl lg:text-6xl font-bold text-white mb-6 text-balance">
                    {t("Predict Your Crop Yield")}
                  </h2>
                  <p className="text-xl text-white/90 mb-8 text-pretty max-w-2xl">
                    {t("Get AI-powered yield predictions and personalized farming advisory in English and Odia")}
                  </p>
                  <Button
                    size="lg"
                    className="cta-button text-lg px-8 py-4 font-semibold"
                    onClick={() => document.getElementById("prediction-form")?.scrollIntoView({ behavior: "smooth" })}
                  >
                    <Target className="h-5 w-5 mr-2" />
                    {t("Get Prediction")}
                  </Button>
                </div>
                <div className="relative">
                  <div className="relative bg-white/10 backdrop-blur-sm rounded-3xl p-8 border border-white/20">
                    <img
                      src="/indian-farmer-using-smartphone-in-green-rice-field.jpg"
                      alt="Farmer using AI technology in field"
                      className="w-full h-auto rounded-2xl shadow-2xl"
                    />
                    <div className="absolute -top-4 -right-4 bg-accent p-3 rounded-full shadow-lg icon-glow">
                      <Smartphone className="h-6 w-6 text-accent-foreground" />
                    </div>
                    <div className="absolute -bottom-4 -left-4 bg-secondary p-3 rounded-full shadow-lg icon-glow">
                      <Brain className="h-6 w-6 text-secondary-foreground" />
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
        <section className="mb-20">
          <div className="text-center mb-12">
            <h3 className="text-3xl font-bold text-foreground mb-4">{t("Why Choose Our Platform?")}</h3>
            <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
              {t("Advanced AI technology meets traditional farming wisdom")}
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            <Card className="feature-card group">
              <CardContent className="pt-8 pb-8 text-center">
                <div className="bg-gradient-to-br from-primary/20 to-primary/10 rounded-2xl p-6 w-20 h-20 mx-auto mb-6 flex items-center justify-center group-hover:scale-110 transition-transform duration-300">
                  <TrendingUp className="h-10 w-10 text-primary" />
                </div>
                <h3 className="font-bold text-xl mb-3 text-card-foreground">{t("Accurate Predictions")}</h3>
                <p className="text-muted-foreground leading-relaxed">
                  {t("ML models trained on weather, soil, and historical data")}
                </p>
              </CardContent>
            </Card>

            <Card className="feature-card group">
              <CardContent className="pt-8 pb-8 text-center">
                <div className="bg-gradient-to-br from-secondary/20 to-secondary/10 rounded-2xl p-6 w-20 h-20 mx-auto mb-6 flex items-center justify-center group-hover:scale-110 transition-transform duration-300">
                  <MapPin className="h-10 w-10 text-secondary" />
                </div>
                <h3 className="font-bold text-xl mb-3 text-card-foreground">{t("Location-Based")}</h3>
                <p className="text-muted-foreground leading-relaxed">
                  {t("GPS-enabled recommendations for your specific location")}
                </p>
              </CardContent>
            </Card>

            <Card className="feature-card group">
              <CardContent className="pt-8 pb-8 text-center">
                <div className="bg-gradient-to-br from-accent/20 to-accent/10 rounded-2xl p-6 w-20 h-20 mx-auto mb-6 flex items-center justify-center group-hover:scale-110 transition-transform duration-300">
                  <Globe className="h-10 w-10 text-accent" />
                </div>
                <h3 className="font-bold text-xl mb-3 text-card-foreground">{t("Bilingual Support")}</h3>
                <p className="text-muted-foreground leading-relaxed">{t("Available in English and Odia languages")}</p>
              </CardContent>
            </Card>
          </div>
        </section>

        <section id="prediction-form" className="mb-20">
          <div className="grid grid-cols-1 xl:grid-cols-2 gap-8">
            {/* Prediction Form */}
            <div>
              <Card className="feature-card shadow-xl">
                <CardHeader className="bg-gradient-to-r from-primary/5 to-primary/10 rounded-t-xl">
                  <CardTitle className="flex items-center gap-3 text-xl">
                    <Sprout className="h-6 w-6 text-primary" />
                    {t("Crop Information")}
                  </CardTitle>
                  <CardDescription className="text-base">
                    {t("Enter your farm details to get yield prediction and advisory")}
                  </CardDescription>
                </CardHeader>
                <CardContent className="pt-6">
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
                <Card className="feature-card h-full flex items-center justify-center shadow-xl">
                  <CardContent className="text-center py-16">
                    <div className="bg-gradient-to-br from-muted/50 to-muted/30 rounded-2xl p-8 w-32 h-32 mx-auto mb-6 flex items-center justify-center">
                      <Leaf className="h-16 w-16 text-primary" />
                    </div>
                    <h3 className="text-xl font-bold text-card-foreground mb-3">{t("Ready for Prediction")}</h3>
                    <p className="text-muted-foreground text-base leading-relaxed max-w-sm mx-auto">
                      {t("Fill in the form to get your crop yield prediction and farming advisory")}
                    </p>
                  </CardContent>
                </Card>
              )}
            </div>
          </div>
        </section>

        <section className="mb-20">
          <Card className="feature-card shadow-xl">
            <CardHeader className="text-center pb-8">
              <CardTitle className="text-3xl font-bold">{t("How It Works")}</CardTitle>
              <CardDescription className="text-lg mt-2">
                {t("Our AI system combines multiple data sources for accurate predictions")}
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
                <div className="text-center group">
                  <div className="bg-gradient-to-br from-primary/20 to-primary/10 rounded-2xl p-5 w-18 h-18 mx-auto mb-4 flex items-center justify-center group-hover:scale-110 transition-transform duration-300">
                    <MapPin className="h-9 w-9 text-primary" />
                  </div>
                  <h4 className="font-bold text-lg mb-2 text-card-foreground">{t("Location Data")}</h4>
                  <p className="text-sm text-muted-foreground leading-relaxed">
                    {t("GPS coordinates and district information")}
                  </p>
                </div>

                <div className="text-center group">
                  <div className="bg-gradient-to-br from-secondary/20 to-secondary/10 rounded-2xl p-5 w-18 h-18 mx-auto mb-4 flex items-center justify-center group-hover:scale-110 transition-transform duration-300">
                    <Sun className="h-9 w-9 text-secondary" />
                  </div>
                  <h4 className="font-bold text-lg mb-2 text-card-foreground">{t("Weather & Soil")}</h4>
                  <p className="text-sm text-muted-foreground leading-relaxed">
                    {t("Real-time weather and soil data from APIs")}
                  </p>
                </div>

                <div className="text-center group">
                  <div className="bg-gradient-to-br from-accent/20 to-accent/10 rounded-2xl p-5 w-18 h-18 mx-auto mb-4 flex items-center justify-center group-hover:scale-110 transition-transform duration-300">
                    <TrendingUp className="h-9 w-9 text-accent" />
                  </div>
                  <h4 className="font-bold text-lg mb-2 text-card-foreground">{t("AI Analysis")}</h4>
                  <p className="text-sm text-muted-foreground leading-relaxed">
                    {t("Machine learning models process all data")}
                  </p>
                </div>

                <div className="text-center group">
                  <div className="bg-gradient-to-br from-chart-2/20 to-chart-2/10 rounded-2xl p-5 w-18 h-18 mx-auto mb-4 flex items-center justify-center group-hover:scale-110 transition-transform duration-300">
                    <Droplets className="h-9 w-9 text-chart-2" />
                  </div>
                  <h4 className="font-bold text-lg mb-2 text-card-foreground">{t("Advisory")}</h4>
                  <p className="text-sm text-muted-foreground leading-relaxed">
                    {t("Personalized recommendations in your language")}
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>
        </section>
      </main>

      <footer className="bg-gradient-to-r from-card to-card/80 border-t border-border/50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-12">
            <div>
              <div className="flex items-center gap-4 mb-6">
                <div className="bg-gradient-to-br from-primary to-primary/80 p-3 rounded-xl shadow-lg">
                  <Sprout className="h-7 w-7 text-primary-foreground" />
                </div>
                <span className="text-2xl font-bold text-foreground">AI Harvesters</span>
              </div>
              <p className="text-muted-foreground leading-relaxed">
                {t(
                  "Empowering farmers with AI-driven insights for better crop yields and sustainable farming practices.",
                )}
              </p>
            </div>

            <div>
              <h3 className="text-xl font-bold mb-6 text-foreground">{t("Features")}</h3>
              <ul className="space-y-3 text-muted-foreground">
                <li className="flex items-center gap-2">
                  <div className="w-2 h-2 bg-primary rounded-full"></div>
                  {t("Yield Prediction")}
                </li>
                <li className="flex items-center gap-2">
                  <div className="w-2 h-2 bg-primary rounded-full"></div>
                  {t("Weather Integration")}
                </li>
                <li className="flex items-center gap-2">
                  <div className="w-2 h-2 bg-primary rounded-full"></div>
                  {t("Soil Analysis")}
                </li>
                <li className="flex items-center gap-2">
                  <div className="w-2 h-2 bg-primary rounded-full"></div>
                  {t("Bilingual Support")}
                </li>
              </ul>
            </div>

            <div>
              <h3 className="text-xl font-bold mb-6 text-foreground">{t("Support")}</h3>
              <ul className="space-y-3 text-muted-foreground">
                <li className="flex items-center gap-2">
                  <div className="w-2 h-2 bg-secondary rounded-full"></div>
                  {t("Documentation")}
                </li>
                <li className="flex items-center gap-2">
                  <div className="w-2 h-2 bg-secondary rounded-full"></div>
                  {t("API Reference")}
                </li>
                <li className="flex items-center gap-2">
                  <div className="w-2 h-2 bg-secondary rounded-full"></div>
                  {t("Contact Support")}
                </li>
                <li className="flex items-center gap-2">
                  <div className="w-2 h-2 bg-secondary rounded-full"></div>
                  {t("Feedback")}
                </li>
              </ul>
            </div>
          </div>

          <Separator className="my-12 bg-border/50" />

          <div className="text-center text-muted-foreground">
            <p className="text-lg">&copy; AI Harvesters. {t("Built for Smart India Hackathon 2025.")}</p>
          </div>
        </div>
      </footer>
    </div>
  )
}