"use client"

import { Button } from "@/components/ui/button"
import { Globe } from "lucide-react"

interface LanguageToggleProps {
  language: string
  onLanguageChange: (language: string) => void
}

export function LanguageToggle({ language, onLanguageChange }: LanguageToggleProps) {
  return (
    <div className="flex items-center gap-2">
      <Globe className="h-4 w-4 text-gray-600" />
      <div className="flex bg-gray-100 rounded-lg p-1">
        <Button
          variant={language === "en" ? "default" : "ghost"}
          size="sm"
          onClick={() => onLanguageChange("en")}
          className="text-xs px-3 py-1"
        >
          English
        </Button>
        <Button
          variant={language === "or" ? "default" : "ghost"}
          size="sm"
          onClick={() => onLanguageChange("or")}
          className="text-xs px-3 py-1"
        >
          ଓଡ଼ିଆ
        </Button>
      </div>
    </div>
  )
}
