"use client"

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Progress } from "@/components/ui/progress"
import { TrendingUp, Droplets, AlertTriangle, CheckCircle, Info } from "lucide-react"
import { useTranslation } from "@/hooks/use-translation"

interface PredictionResultsProps {
  prediction: any
  language: string
}

export function PredictionResults({ prediction, language }: PredictionResultsProps) {
  const { t } = useTranslation()

  console.log("[v0] Prediction data received in component:", prediction)

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

  const predictionData = prediction.prediction || prediction
  const advisoryData = prediction.advisory || {}

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
            <Badge className={getConfidenceColor(predictionData.confidence_score)}>
              {getConfidenceLabel(predictionData.confidence_score)}
            </Badge>
          </CardTitle>
          <CardDescription>{t("AI-powered prediction based on weather, soil, and historical data")}</CardDescription>
        </CardHeader>
        <CardContent className="pt-6">
          <div className="text-center mb-6">
            <div className="text-4xl font-bold text-green-600 mb-2">
              {formatYield(predictionData.yield_tons_per_ha || predictionData.predicted_yield_t_ha || 0)}
            </div>
            {predictionData.predicted_yield_range_t_ha && (
              <div className="text-sm text-gray-600">
                {t("Range")}: {formatYield(predictionData.predicted_yield_range_t_ha[0])} -{" "}
                {formatYield(predictionData.predicted_yield_range_t_ha[1])}
              </div>
            )}
          </div>

          <div className="space-y-4">
            <div>
              <div className="flex justify-between text-sm mb-2">
                <span>{t("Confidence Score")}</span>
                <span>{(predictionData.confidence_score * 100).toFixed(1)}%</span>
              </div>
              <Progress value={predictionData.confidence_score * 100} className="h-2" />
            </div>

            {predictionData.risk_factors && predictionData.risk_factors.length > 0 && (
              <div>
                <h4 className="font-semibold mb-3 flex items-center gap-2">
                  <Info className="h-4 w-4" />
                  {t("Risk Factors")}
                </h4>
                <div className="space-y-2">
                  {predictionData.risk_factors.map((factor: string, index: number) => (
                    <div key={index} className="flex items-center text-sm">
                      <Badge variant="outline" className="text-xs capitalize">
                        {factor.replace(/_/g, " ")}
                      </Badge>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        </CardContent>
      </Card>

      {/* Advisory Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {advisoryData.recommendations && advisoryData.recommendations.length > 0 && (
          <Card className="md:col-span-2">
            <CardHeader className="pb-3">
              <CardTitle className="text-lg flex items-center gap-2">
                <CheckCircle className="h-5 w-5 text-green-600" />
                {t("Recommendations")}
              </CardTitle>
            </CardHeader>
            <CardContent>
              <ul className="space-y-2">
                {advisoryData.recommendations.map((rec: string, index: number) => (
                  <li key={index} className="text-sm text-gray-700 flex items-start gap-2">
                    <span className="text-green-600 mt-1">•</span>
                    {rec}
                  </li>
                ))}
              </ul>
            </CardContent>
          </Card>
        )}

        {/* Irrigation Schedule */}
        {advisoryData.irrigation_schedule && advisoryData.irrigation_schedule.length > 0 && (
          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="text-lg flex items-center gap-2">
                <Droplets className="h-5 w-5 text-blue-600" />
                {t("Irrigation Schedule")}
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {advisoryData.irrigation_schedule.map((schedule: any, index: number) => (
                  <div key={index} className="text-sm">
                    <div className="font-medium capitalize">{schedule.stage}</div>
                    <div className="text-gray-600">
                      Day {schedule.days_after_sowing} • {schedule.water_depth_cm}cm depth
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        )}

        {/* Weather Impact */}
        {advisoryData.weather_impact && (
          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="text-lg flex items-center gap-2">
                <AlertTriangle className="h-5 w-5 text-yellow-600" />
                {t("Weather Impact")}
              </CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-gray-700 leading-relaxed">{advisoryData.weather_impact}</p>
            </CardContent>
          </Card>
        )}
      </div>

      {/* Expected Harvest Date */}
      {predictionData.expected_harvest_date && (
        <Card className="bg-blue-50 border-blue-200">
          <CardContent className="pt-4">
            <div className="flex items-center justify-center gap-2">
              <span className="font-semibold text-blue-800">{t("Expected Harvest Date")}:</span>
              <span className="text-blue-700">
                {new Date(predictionData.expected_harvest_date).toLocaleDateString()}
              </span>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Model Information */}
      <Card className="bg-gray-50">
        <CardContent className="pt-4">
          <div className="flex justify-between items-center text-sm text-gray-600">
            <span>
              {t("Model Version")}: {prediction.model_version || "v1.0"}
            </span>
            <span>
              {t("Generated")}: {new Date().toLocaleString()}
            </span>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
