"use client"

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Progress } from "@/components/ui/progress"
import { TrendingUp, Droplets, Zap, Bug, AlertTriangle, CheckCircle, Info } from "lucide-react"
import { useTranslation } from "@/hooks/use-translation"

interface PredictionResultsProps {
  prediction: any
  language: string
}

export function PredictionResults({ prediction, language }: PredictionResultsProps) {
  const { t } = useTranslation()

  const getConfidenceColor = (confidence: number) => {
    if (confidence >= 0.8) return "text-green-600 bg-green-50"
    if (confidence >= 0.6) return "text-yellow-600 bg-yellow-50"
    return "text-red-600 bg-red-50"
  }

  const getConfidenceLabel = (confidence: number) => {
    if (confidence >= 0.8) return t("High Confidence")
    if (confidence >= 0.6) return t("Medium Confidence")
    return t("Low Confidence")
  }

  const formatYield = (yield_value: number) => {
    return `${yield_value.toFixed(2)} ${t("t/ha")}`
  }

  return (
    <div className="space-y-6">
      {/* Main Prediction Card */}
      <Card className="border-2 border-green-200">
        <CardHeader className="bg-green-50">
          <CardTitle className="flex items-center justify-between">
            <span className="flex items-center gap-2">
              <TrendingUp className="h-6 w-6 text-green-600" />
              {t("Yield Prediction")}
            </span>
            <Badge className={getConfidenceColor(prediction.confidence_score)}>
              {getConfidenceLabel(prediction.confidence_score)}
            </Badge>
          </CardTitle>
          <CardDescription>{t("AI-powered prediction based on weather, soil, and historical data")}</CardDescription>
        </CardHeader>
        <CardContent className="pt-6">
          <div className="text-center mb-6">
            <div className="text-4xl font-bold text-green-600 mb-2">{formatYield(prediction.predicted_yield_t_ha)}</div>
            <div className="text-sm text-gray-600">
              {t("Range")}: {formatYield(prediction.predicted_yield_range_t_ha[0])} -{" "}
              {formatYield(prediction.predicted_yield_range_t_ha[1])}
            </div>
          </div>

          <div className="space-y-4">
            <div>
              <div className="flex justify-between text-sm mb-2">
                <span>{t("Confidence Score")}</span>
                <span>{(prediction.confidence_score * 100).toFixed(1)}%</span>
              </div>
              <Progress value={prediction.confidence_score * 100} className="h-2" />
            </div>

            {/* Top Contributing Factors */}
            <div>
              <h4 className="font-semibold mb-3 flex items-center gap-2">
                <Info className="h-4 w-4" />
                {t("Key Factors")}
              </h4>
              <div className="space-y-2">
                {prediction.top_features?.slice(0, 3).map((feature: any, index: number) => (
                  <div key={index} className="flex justify-between items-center text-sm">
                    <span className="capitalize">{feature.feature.replace(/_/g, " ")}</span>
                    <div className="flex items-center gap-2">
                      <span className="text-gray-600">{feature.value}</span>
                      <Badge variant="outline" className="text-xs">
                        {(feature.importance * 100).toFixed(1)}%
                      </Badge>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Advisory Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {/* Irrigation Advisory */}
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-lg flex items-center gap-2">
              <Droplets className="h-5 w-5 text-blue-600" />
              {t("Irrigation")}
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-sm text-gray-700 leading-relaxed">
              {prediction.advisory?.irrigation || t("No irrigation advisory available")}
            </p>
          </CardContent>
        </Card>

        {/* Fertilizer Advisory */}
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-lg flex items-center gap-2">
              <Zap className="h-5 w-5 text-yellow-600" />
              {t("Fertilizer")}
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-sm text-gray-700 leading-relaxed">
              {prediction.advisory?.fertilizer || t("No fertilizer advisory available")}
            </p>
          </CardContent>
        </Card>

        {/* Pest Advisory */}
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-lg flex items-center gap-2">
              <Bug className="h-5 w-5 text-red-600" />
              {t("Pest Control")}
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-sm text-gray-700 leading-relaxed">
              {prediction.advisory?.pest || t("No pest advisory available")}
            </p>
          </CardContent>
        </Card>

        {/* General Advisory */}
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-lg flex items-center gap-2">
              <CheckCircle className="h-5 w-5 text-green-600" />
              {t("General")}
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-sm text-gray-700 leading-relaxed">
              {prediction.advisory?.general || t("No general advisory available")}
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Disclaimer */}
      {prediction.advisory?.disclaimer && (
        <Card className="border-yellow-200 bg-yellow-50">
          <CardContent className="pt-4">
            <div className="flex items-start gap-3">
              <AlertTriangle className="h-5 w-5 text-yellow-600 mt-0.5 flex-shrink-0" />
              <div>
                <h4 className="font-semibold text-yellow-800 mb-1">{t("Important Note")}</h4>
                <p className="text-sm text-yellow-700">{prediction.advisory.disclaimer}</p>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Model Information */}
      <Card className="bg-gray-50">
        <CardContent className="pt-4">
          <div className="flex justify-between items-center text-sm text-gray-600">
            <span>
              {t("Model Version")}: {prediction.model_version}
            </span>
            <span>
              {t("Generated")}: {new Date(prediction.timestamp).toLocaleString()}
            </span>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
