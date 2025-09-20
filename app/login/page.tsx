"use client"

import { useState } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Separator } from "@/components/ui/separator"
import { User, Phone, ArrowLeft, Sprout, Eye, EyeOff } from "lucide-react"
import { useTranslation } from "@/hooks/use-translation"
import Link from "next/link"
import { useRouter } from "next/navigation"

export default function LoginPage() {
  const { t, language } = useTranslation()
  const router = useRouter()
  const [isLoading, setIsLoading] = useState(false)
  const [showPassword, setShowPassword] = useState(false)
  const [isSignUp, setIsSignUp] = useState(false)
  const [formData, setFormData] = useState({
    name: "",
    phone: "",
    password: "",
    confirmPassword: ""
  })

  const handleInputChange = (field: string, value: string) => {
    setFormData(prev => ({ ...prev, [field]: value }))
  }

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault()
    setIsLoading(true)

    try {
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 1000))

      // For demo purposes, accept any phone/password combination
      if (formData.phone && formData.password) {
        // Store login state
        localStorage.setItem("farmer_logged_in", "true")
        localStorage.setItem("farmer_phone", formData.phone)
        localStorage.setItem("farmer_name", formData.name || "Farmer")

        // Redirect to home page
        router.push("/")
      } else {
        alert(t("Please enter phone number and password"))
      }
    } catch (error) {
      console.error("Login error:", error)
      alert(t("Login failed. Please try again."))
    } finally {
      setIsLoading(false)
    }
  }

  const handleSignUp = async (e: React.FormEvent) => {
    e.preventDefault()
    setIsLoading(true)

    try {
      // Validate passwords match
      if (formData.password !== formData.confirmPassword) {
        alert(t("Passwords do not match"))
        setIsLoading(false)
        return
      }

      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 1000))

      // For demo purposes, accept any valid input
      if (formData.name && formData.phone && formData.password) {
        // Store login state
        localStorage.setItem("farmer_logged_in", "true")
        localStorage.setItem("farmer_phone", formData.phone)
        localStorage.setItem("farmer_name", formData.name)

        // Redirect to home page
        router.push("/")
      } else {
        alert(t("Please fill in all required fields"))
      }
    } catch (error) {
      console.error("Sign up error:", error)
      alert(t("Sign up failed. Please try again."))
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-green-50 to-blue-50 flex items-center justify-center p-4">
      <div className="w-full max-w-md">
        {/* Header */}
        <div className="text-center mb-8">
          <Link href="/">
            <Button variant="ghost" className="mb-4">
              <ArrowLeft className="h-4 w-4 mr-2" />
              {t("Back to Home")}
            </Button>
          </Link>
          
          <div className="flex items-center justify-center gap-3 mb-4">
            <div className="bg-gradient-to-br from-primary to-primary/80 p-3 rounded-xl shadow-lg">
              <Sprout className="h-8 w-8 text-primary-foreground" />
            </div>
            <div>
              <h1 className="text-2xl font-bold text-foreground">{t("AI Crop Yield Predictor")}</h1>
            </div>
          </div>
        </div>

        {/* Login/Signup Card */}
        <Card className="shadow-xl">
          <CardHeader className="text-center">
            <CardTitle className="flex items-center justify-center gap-2 text-xl">
              <User className="h-5 w-5" />
              {isSignUp ? t("Create Farmer Account") : t("Farmer Login")}
            </CardTitle>
            <CardDescription>
              {isSignUp 
                ? t("Join our platform to get personalized crop yield predictions")
                : t("Sign in to access your personalized farming dashboard")
              }
            </CardDescription>
          </CardHeader>
          
          <CardContent>
            <form onSubmit={isSignUp ? handleSignUp : handleLogin} className="space-y-4">
              {/* Name field (only for signup) */}
              {isSignUp && (
                <div className="space-y-2">
                  <Label htmlFor="name">{t("Full Name")} *</Label>
                  <Input
                    id="name"
                    type="text"
                    value={formData.name}
                    onChange={(e) => handleInputChange("name", e.target.value)}
                    placeholder={t("Enter your full name")}
                    required={isSignUp}
                  />
                </div>
              )}

              {/* Phone field */}
              <div className="space-y-2">
                <Label htmlFor="phone">{t("Phone Number")} *</Label>
                <div className="relative">
                  <Phone className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                  <Input
                    id="phone"
                    type="tel"
                    value={formData.phone}
                    onChange={(e) => handleInputChange("phone", e.target.value)}
                    placeholder="+91-9876543210"
                    className="pl-10"
                    required
                  />
                </div>
              </div>

              {/* Password field */}
              <div className="space-y-2">
                <Label htmlFor="password">{t("Password")} *</Label>
                <div className="relative">
                  <Input
                    id="password"
                    type={showPassword ? "text" : "password"}
                    value={formData.password}
                    onChange={(e) => handleInputChange("password", e.target.value)}
                    placeholder={t("Enter your password")}
                    required
                  />
                  <Button
                    type="button"
                    variant="ghost"
                    size="sm"
                    className="absolute right-0 top-0 h-full px-3 py-2 hover:bg-transparent"
                    onClick={() => setShowPassword(!showPassword)}
                  >
                    {showPassword ? (
                      <EyeOff className="h-4 w-4 text-muted-foreground" />
                    ) : (
                      <Eye className="h-4 w-4 text-muted-foreground" />
                    )}
                  </Button>
                </div>
              </div>

              {/* Confirm Password field (only for signup) */}
              {isSignUp && (
                <div className="space-y-2">
                  <Label htmlFor="confirmPassword">{t("Confirm Password")} *</Label>
                  <Input
                    id="confirmPassword"
                    type="password"
                    value={formData.confirmPassword}
                    onChange={(e) => handleInputChange("confirmPassword", e.target.value)}
                    placeholder={t("Confirm your password")}
                    required={isSignUp}
                  />
                </div>
              )}

              {/* Submit Button */}
              <Button type="submit" className="w-full" disabled={isLoading}>
                {isLoading ? (
                  <>
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                    {isSignUp ? t("Creating Account...") : t("Signing In...")}
                  </>
                ) : (
                  <>
                    <User className="h-4 w-4 mr-2" />
                    {isSignUp ? t("Create Account") : t("Sign In")}
                  </>
                )}
              </Button>
            </form>

            <Separator className="my-6" />

            {/* Toggle between login and signup */}
            <div className="text-center">
              <p className="text-sm text-muted-foreground mb-2">
                {isSignUp 
                  ? t("Already have an account?")
                  : t("Don't have an account?")
                }
              </p>
              <Button
                type="button"
                variant="outline"
                onClick={() => {
                  setIsSignUp(!isSignUp)
                  setFormData({ name: "", phone: "", password: "", confirmPassword: "" })
                }}
                className="w-full"
              >
                {isSignUp ? t("Sign In Instead") : t("Create New Account")}
              </Button>
            </div>

            {/* Demo credentials */}
            <div className="mt-6 p-3 bg-muted rounded-lg">
              <p className="text-xs text-muted-foreground text-center">
                {t("Demo: Use any phone number and password to login")}
              </p>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}