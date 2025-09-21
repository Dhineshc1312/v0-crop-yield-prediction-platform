"use client"

import { useState, useEffect } from "react"

// Translation dictionary
const translations = {
  en: {
    // App Title and Basic
    "AI Crop Yield Predictor": "AI Crop Yield Predictor",
    "Smart farming advisory for Odisha": "Smart farming advisory for Odisha",
    "Predict Your Crop Yield": "Predict Your Crop Yield",
    "Get AI-powered yield predictions and personalized farming advisory in English and Odia":
      "Get AI-powered yield predictions and personalized farming advisory in English and Odia",

    // Features
    "Accurate Predictions": "Accurate Predictions",
    "ML models trained on weather, soil, and historical data":
      "ML models trained on weather, soil, and historical data",
    "Location-Based": "Location-Based",
    "GPS-enabled recommendations for your specific location": "GPS-enabled recommendations for your specific location",
    "Bilingual Support": "Bilingual Support",
    "Available in English and Odia languages": "Available in English and Odia languages",

    // Form Fields
    "Crop Information": "Crop Information",
    "Enter your farm details to get yield prediction and advisory":
      "Enter your farm details to get yield prediction and advisory",
    Location: "Location",
    "Use GPS": "Use GPS",
    Latitude: "Latitude",
    Longitude: "Longitude",
    State: "State",
    District: "District",
    "Crop Details": "Crop Details",
    "Crop Type": "Crop Type",
    Year: "Year",
    "Farm Area (hectares)": "Farm Area (hectares)",
    "Sowing Date": "Sowing Date",
    "Farm Inputs": "Farm Inputs",
    Optional: "Optional",
    "Nitrogen (kg/ha)": "Nitrogen (kg/ha)",
    "Phosphorus (kg/ha)": "Phosphorus (kg/ha)",
    "Potassium (kg/ha)": "Potassium (kg/ha)",
    "Irrigation Events": "Irrigation Events",

    // Crops
    Rice: "Rice",
    Wheat: "Wheat",
    Maize: "Maize",
    Sugarcane: "Sugarcane",

    // Actions
    "Get Prediction & Advisory": "Get Prediction & Advisory",
    "Predicting...": "Predicting...",

    // Results
    "Ready for Prediction": "Ready for Prediction",
    "Fill in the form to get your crop yield prediction and farming advisory":
      "Fill in the form to get your crop yield prediction and farming advisory",
    "Yield Prediction": "Yield Prediction",
    "AI-powered prediction based on weather, soil, and historical data":
      "AI-powered prediction based on weather, soil, and historical data",
    "High Confidence": "High Confidence",
    "Medium Confidence": "Medium Confidence",
    "Low Confidence": "Low Confidence",
    Range: "Range",
    "Confidence Score": "Confidence Score",
    "Key Factors": "Key Factors",
    "t/ha": "t/ha",

    // Advisory
    Irrigation: "Irrigation",
    Fertilizer: "Fertilizer",
    "Pest Control": "Pest Control",
    General: "General",
    "No irrigation advisory available": "No irrigation advisory available",
    "No fertilizer advisory available": "No fertilizer advisory available",
    "No pest advisory available": "No pest advisory available",
    "No general advisory available": "No general advisory available",
    "Important Note": "Important Note",
    "Model Version": "Model Version",
    Generated: "Generated",

    // How It Works
    "How It Works": "How It Works",
    "Our AI system combines multiple data sources for accurate predictions":
      "Our AI system combines multiple data sources for accurate predictions",
    "Location Data": "Location Data",
    "GPS coordinates and district information": "GPS coordinates and district information",
    "Weather & Soil": "Weather & Soil",
    "Real-time weather and soil data from APIs": "Real-time weather and soil data from APIs",
    "AI Analysis": "AI Analysis",
    "Machine learning models process all data": "Machine learning models process all data",
    Advisory: "Advisory",
    "Personalized recommendations in your language": "Personalized recommendations in your language",

    // Footer
    "Empowering farmers with AI-driven insights for better crop yields and sustainable farming practices.":
      "Empowering farmers with AI-driven insights for better crop yields and sustainable farming practices.",
    Features: "Features",
    "Yield Prediction": "Yield Prediction",
    "Weather Integration": "Weather Integration",
    "Soil Analysis": "Soil Analysis",
    Support: "Support",
    Documentation: "Documentation",
    "API Reference": "API Reference",
    "Contact Support": "Contact Support",
    Feedback: "Feedback",
    "Built for Smart India Hackathon 2024.": "Built for Smart India Hackathon 2024.",

    // Profile Navigation
    "My Profile": "My Profile",
    "Welcome": "Welcome",
    "Login": "Login",
    "Logout": "Logout",
    "Create Account": "Create Account",
    "Farmer Login": "Farmer Login",
    "Create your farmer account to get started": "Create your farmer account to get started",
    "Enter your phone number to access your account": "Enter your phone number to access your account",
    "Creating Account...": "Creating Account...",
    "Logging in...": "Logging in...",
    "Already have an account? Login": "Already have an account? Login",
    "Don't have an account? Register": "Don't have an account? Register",
    "Continue as Guest": "Continue as Guest",

    // Profile Form
    "Farmer Profile": "Farmer Profile",
    "Create or update your farmer profile and farm details": "Create or update your farmer profile and farm details",
    "Personal Information": "Personal Information",
    "Full Name": "Full Name",
    "Enter your full name": "Enter your full name",
    "Phone Number": "Phone Number",
    "Enter phone number": "Enter phone number",
    "Preferred Language": "Preferred Language",
    "Get Current Location": "Get Current Location",
    "Getting Location...": "Getting Location...",
    "Location:": "Location:",
    "Farm Details": "Farm Details",
    "Add Farm": "Add Farm",
    Farm: "Farm",
    Remove: "Remove",
    "Farm Name": "Farm Name",
    "Enter farm name": "Enter farm name",
    "Select crop": "Select crop",
    "Farm Area (Hectares)": "Farm Area (Hectares)",
    "Save Profile": "Save Profile",
    "Saving...": "Saving...",

    // Profile Display
    "Edit Profile": "Edit Profile",
    "Location not set": "Location not set",
    "Member since": "Member since",
    "Total Area:": "Total Area:",
    hectares: "hectares",
    "My Farms": "My Farms",
    "Manage your farm details and crop information": "Manage your farm details and crop information",
    "No farms added yet": "No farms added yet",
    "Add Your First Farm": "Add Your First Farm",
    "Sown on": "Sown on",

    // Crop types
    rice: "Rice",
    wheat: "Wheat",
    maize: "Maize",
    sugarcane: "Sugarcane",
    cotton: "Cotton",
    groundnut: "Groundnut",
    soybean: "Soybean",
    mustard: "Mustard",
    sesame: "Sesame",
    turmeric: "Turmeric",
    ginger: "Ginger",
    onion: "Onion",
  },
  or: {
    // App Title and Basic
    "AI Crop Yield Predictor": "AI ଫସଲ ଅମଳ ପୂର୍ବାନୁମାନ",
    "Smart farming advisory for Odisha": "ଓଡ଼ିଶା ପାଇଁ ସ୍ମାର୍ଟ କୃଷି ପରାମର୍ଶ",
    "Predict Your Crop Yield": "ଆପଣଙ୍କ ଫସଲ ଅମଳର ପୂର୍ବାନୁମାନ କରନ୍ତୁ",
    "Get AI-powered yield predictions and personalized farming advisory in English and Odia":
      "ଇଂରାଜୀ ଏବଂ ଓଡ଼ିଆରେ AI-ଚାଳିତ ଅମଳ ପୂର୍ବାନୁମାନ ଏବଂ ବ୍ୟକ୍ତିଗତ କୃଷି ପରାମର୍ଶ ପାଆନ୍ତୁ",

    // Features
    "Accurate Predictions": "ସଠିକ ପୂର୍ବାନୁମାନ",
    "ML models trained on weather, soil, and historical data": "ପାଗ, ମାଟି ଏବଂ ଐତିହାସିକ ତଥ୍ୟରେ ତାଲିମପ୍ରାପ୍ତ ML ମଡେଲ",
    "Location-Based": "ସ୍ଥାନ-ଆଧାରିତ",
    "GPS-enabled recommendations for your specific location": "ଆପଣଙ୍କ ନିର୍ଦ୍ଦିଷ୍ଟ ସ୍ଥାନ ପାଇଁ GPS-ସକ୍ଷମ ସୁପାରିଶ",
    "Bilingual Support": "ଦ୍ୱିଭାଷିକ ସହାୟତା",
    "Available in English and Odia languages": "ଇଂରାଜୀ ଏବଂ ଓଡ଼ିଆ ଭାଷାରେ ଉପଲବ୍ଧ",

    // Form Fields
    "Crop Information": "ଫସଲ ସୂଚନା",
    "Enter your farm details to get yield prediction and advisory":
      "ଅମଳ ପୂର୍ବାନୁମାନ ଏବଂ ପରାମର୍ଶ ପାଇବା ପାଇଁ ଆପଣଙ୍କ ଚାଷ ବିବରଣୀ ପ୍ରବେଶ କରନ୍ତୁ",
    Location: "ସ୍ଥାନ",
    "Use GPS": "GPS ବ୍ୟବହାର କରନ୍ତୁ",
    Latitude: "ଅକ୍ଷାଂଶ",
    Longitude: "ଦ୍ରାଘିମା",
    State: "ରାଜ୍ୟ",
    District: "ଜିଲ୍ଲା",
    "Crop Details": "ଫସଲ ବିବରଣୀ",
    "Crop Type": "ଫସଲ ପ୍ରକାର",
    Year: "ବର୍ଷ",
    "Farm Area (hectares)": "ଚାଷ କ୍ଷେତ୍ର (ହେକ୍ଟର)",
    "Sowing Date": "ବୁଣା ତାରିଖ",
    "Farm Inputs": "ଚାଷ ସାମଗ୍ରୀ",
    Optional: "ଇଚ୍ଛାଧୀନ",
    "Nitrogen (kg/ha)": "ନାଇଟ୍ରୋଜେନ (କିଗ୍ରା/ହେକ୍ଟର)",
    "Phosphorus (kg/ha)": "ଫସଫରସ (କିଗ୍ରା/ହେକ୍ଟର)",
    "Potassium (kg/ha)": "ପୋଟାସିୟମ (କିଗ୍ରା/ହେକ୍ଟର)",
    "Irrigation Events": "ଜଳସେଚନ ଘଟଣା",

    // Crops
    Rice: "ଚାଉଳ",
    Wheat: "ଗହମ",
    Maize: "ମକା",
    Sugarcane: "ଆଖୁ",

    // Actions
    "Get Prediction & Advisory": "ପୂର୍ବାନୁମାନ ଏବଂ ପରାମର୍ଶ ପାଆନ୍ତୁ",
    "Predicting...": "ପୂର୍ବାନୁମାନ କରୁଛି...",

    // Results
    "Ready for Prediction": "ପୂର୍ବାନୁମାନ ପାଇଁ ପ୍ରସ୍ତୁତ",
    "Fill in the form to get your crop yield prediction and farming advisory":
      "ଆପଣଙ୍କ ଫସଲ ଅମଳ ପୂର୍ବାନୁମାନ ଏବଂ କୃଷି ପରାମର୍ଶ ପାଇବା ପାଇଁ ଫର୍ମ ପୂରଣ କରନ୍ତୁ",
    "Yield Prediction": "ଅମଳ ପୂର୍ବାନୁମାନ",
    "AI-powered prediction based on weather, soil, and historical data": "ପାଗ, ମାଟି ଏବଂ ଐତିହାସିକ ତଥ୍ୟ ଉପରେ ଆଧାରିତ AI-ଚାଳିତ ପୂର୍ବାନୁମାନ",
    "High Confidence": "ଉଚ୍ଚ ବିଶ୍ୱାସ",
    "Medium Confidence": "ମଧ୍ୟମ ବିଶ୍ୱାସ",
    "Low Confidence": "କମ ବିଶ୍ୱାସ",
    Range: "ପରିସର",
    "Confidence Score": "ବିଶ୍ୱାସ ସ୍କୋର",
    "Key Factors": "ମୁଖ୍ୟ କାରକ",
    "t/ha": "ଟନ/ହେକ୍ଟର",

    // Advisory
    Irrigation: "ଜଳସେଚନ",
    Fertilizer: "ସାର",
    "Pest Control": "କୀଟ ନିୟନ୍ତ୍ରଣ",
    General: "ସାଧାରଣ",
    "No irrigation advisory available": "କୌଣସି ଜଳସେଚନ ପରାମର୍ଶ ଉପଲବ୍ଧ ନାହିଁ",
    "No fertilizer advisory available": "କୌଣସି ସାର ପରାମର୍ଶ ଉପଲବ୍ଧ ନାହିଁ",
    "No pest advisory available": "କୌଣସି କୀଟ ପରାମର୍ଶ ଉପଲବ୍ଧ ନାହିଁ",
    "No general advisory available": "କୌଣସି ସାଧାରଣ ପରାମର୍ଶ ଉପଲବ୍ଧ ନାହିଁ",
    "Important Note": "ଗୁରୁତ୍ୱପୂର୍ଣ୍ଣ ଟିପ୍ପଣୀ",
    "Model Version": "ମଡେଲ ସଂସ୍କରଣ",
    Generated: "ସୃଷ୍ଟି",

    // How It Works
    "How It Works": "ଏହା କିପରି କାମ କରେ",
    "Our AI system combines multiple data sources for accurate predictions":
      "ଆମର AI ସିଷ୍ଟମ ସଠିକ ପୂର୍ବାନୁମାନ ପାଇଁ ଏକାଧିକ ତଥ୍ୟ ଉତ୍ସକୁ ମିଶାଏ",
    "Location Data": "ସ୍ଥାନ ତଥ୍ୟ",
    "GPS coordinates and district information": "GPS ସଂଯୋଜନା ଏବଂ ଜିଲ୍ଲା ସୂଚନା",
    "Weather & Soil": "ପାଗ ଏବଂ ମାଟି",
    "Real-time weather and soil data from APIs": "APIs ରୁ ରିଅଲ-ଟାଇମ ପାଗ ଏବଂ ମାଟି ତଥ୍ୟ",
    "AI Analysis": "AI ବିଶ୍ଳେଷଣ",
    "Machine learning models process all data": "ମେସିନ ଲର୍ନିଂ ମଡେଲ ସମସ୍ତ ତଥ୍ୟ ପ୍ରକ୍ରିୟାକରଣ କରେ",
    Advisory: "ପରାମର୍ଶ",
    "Personalized recommendations in your language": "ଆପଣଙ୍କ ଭାଷାରେ ବ୍ୟକ୍ତିଗତ ସୁପାରିଶ",

    // Footer
    "Empowering farmers with AI-driven insights for better crop yields and sustainable farming practices.":
      "ଉନ୍ନତ ଫସଲ ଅମଳ ଏବଂ ସ୍ଥାୟୀ କୃଷି ଅଭ୍ୟାସ ପାଇଁ AI-ଚାଳିତ ଅନ୍ତର୍ଦୃଷ୍ଟି ସହିତ କୃଷକମାନଙ୍କୁ ସଶକ୍ତ କରିବା।",
    Features: "ବିଶେଷତା",
    "Yield Prediction": "ଅମଳ ପୂର୍ବାନୁମାନ",
    "Weather Integration": "ପାଗ ଏକୀକରଣ",
    "Soil Analysis": "ମାଟି ବିଶ୍ଳେଷଣ",
    Support: "ସହାୟତା",
    Documentation: "ଡକ୍ୟୁମେଣ୍ଟେସନ",
    "API Reference": "API ରେଫରେନ୍ସ",
    "Contact Support": "ସହାୟତା ଯୋଗାଯୋଗ",
    Feedback: "ମତାମତ",
    "Built for Smart India Hackathon 2024.": "ସ୍ମାର୍ଟ ଇଣ୍ଡିଆ ହ୍ୟାକାଥନ 2024 ପାଇଁ ନିର୍ମିତ।",

    // Profile Navigation
    "My Profile": "ମୋର ପ୍ରୋଫାଇଲ୍",
    "Welcome": "ସ୍ୱାଗତ",
    "Login": "ଲଗଇନ୍",
    "Logout": "ଲଗଆଉଟ୍",

    // Profile Form
    "Farmer Profile": "କୃଷକ ପ୍ରୋଫାଇଲ୍",
    "Create or update your farmer profile and farm details": "ଆପଣଙ୍କ କୃଷକ ପ୍ରୋଫାଇଲ୍ ଏବଂ ଚାଷ ବିବରଣୀ ସୃଷ୍ଟି କିମ୍ବା ଅପଡେଟ୍ କରନ୍ତୁ",
    "Personal Information": "ବ୍ୟକ୍ତିଗତ ସୂଚନା",
    "Full Name": "ପୂର୍ଣ୍ଣ ନାମ",
    "Enter your full name": "ଆପଣଙ୍କ ପୂର୍ଣ୍ଣ ନାମ ଲେଖନ୍ତୁ",
    "Phone Number": "ଫୋନ୍ ନମ୍ବର",
    "Enter phone number": "ଫୋନ୍ ନମ୍ବର ଲେଖନ୍ତୁ",
    "Preferred Language": "ପସନ୍ଦର ଭାଷା",
    "Get Current Location": "ବର୍ତ୍ତମାନ ଅବସ୍ଥାନ ପାଆନ୍ତୁ",
    "Getting Location...": "ଅବସ୍ଥାନ ପାଇବା...",
    "Location:": "ଅବସ୍ଥାନ:",
    "Farm Details": "ଚାଷ ବିବରଣୀ",
    "Add Farm": "ଚାଷ ଯୋଗ କରନ୍ତୁ",
    Farm: "ଚାଷ",
    Remove: "ହଟାନ୍ତୁ",
    "Farm Name": "ଚାଷ ନାମ",
    "Enter farm name": "ଚାଷ ନାମ ଲେଖନ୍ତୁ",
    "Select crop": "ଫସଲ ବାଛନ୍ତୁ",
    "Farm Area (Hectares)": "ଚାଷ କ୍ଷେତ୍ର (ହେକ୍ଟର)",
    "Save Profile": "ପ୍ରୋଫାଇଲ୍ ସେଭ୍ କରନ୍ତୁ",
    "Saving...": "ସେଭ୍ କରୁଛି...",

    // Profile Display
    "Edit Profile": "ପ୍ରୋଫାଇଲ୍ ଏଡିଟ୍ କରନ୍ତୁ",
    "Location not set": "ଅବସ୍ଥାନ ସେଟ୍ ହୋଇନାହିଁ",
    "Member since": "ସଦସ୍ୟ ହେବା ତାରିଖ",
    "Total Area:": "ମୋଟ କ୍ଷେତ୍ର:",
    hectares: "ହେକ୍ଟର",
    "My Farms": "ମୋର ଚାଷ",
    "Manage your farm details and crop information": "ଆପଣଙ୍କ ଚାଷ ବିବରଣୀ ଏବଂ ଫସଲ ସୂଚନା ପରିଚାଳନା କରନ୍ତୁ",
    "No farms added yet": "ଏପର୍ଯ୍ୟନ୍ତ କୌଣସି ଚାଷ ଯୋଗ କରାଯାଇନାହିଁ",
    "Add Your First Farm": "ଆପଣଙ୍କର ପ୍ରଥମ ଚାଷ ଯୋଗ କରନ୍ତୁ",
    "Sown on": "ବୁଣିବା ତାରିଖ",

    // Crop types
    rice: "ଚାଉଳ",
    wheat: "ଗହମ",
    maize: "ମକା",
    sugarcane: "ଆଖୁ",
    cotton: "କପା",
    groundnut: "ମୂଙ୍ଗଫଳି",
    soybean: "ସୋୟାବିନ",
    mustard: "ସରିଷା",
    sesame: "ତିଳ",
    turmeric: "ହଳଦୀ",
    ginger: "ଆଦା",
    onion: "ପିଆଜ",
  },
}

export function useTranslation() {
  const [language, setLanguage] = useState<"en" | "or">("en")

  // Load language preference from localStorage
  useEffect(() => {
    const savedLanguage = localStorage.getItem("language") as "en" | "or"
    if (savedLanguage && (savedLanguage === "en" || savedLanguage === "or")) {
      setLanguage(savedLanguage)
    }
  }, [])

  // Save language preference to localStorage
  useEffect(() => {
    localStorage.setItem("language", language)
  }, [language])

  const t = (key: string): string => {
    return translations[language][key] || key
  }

  const translate = (englishText: string, odiaText: string): string => {
    return language === "or" ? odiaText : englishText
  }

  return {
    language,
    setLanguage,
    t,
    translate,
  }
}
