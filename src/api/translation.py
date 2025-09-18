"""
Translation service for bilingual support (English ↔ Odia).
Uses Gemini API for translation with caching for common terms.
"""

import json
import os
from typing import Dict, Optional, Any
import logging
import asyncio
import aiohttp
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class TranslationService:
    """Translation service for English ↔ Odia translation"""
    
    def __init__(self, gemini_api_key: Optional[str] = None):
        self.gemini_api_key = gemini_api_key
        self.cache = {}
        self.cache_file = 'translation_cache.json'
        self.load_cache()
        self.load_static_translations()
    
    def load_cache(self):
        """Load translation cache from file"""
        try:
            if os.path.exists(self.cache_file):
                with open(self.cache_file, 'r', encoding='utf-8') as f:
                    self.cache = json.load(f)
                logger.info(f"Loaded {len(self.cache)} cached translations")
        except Exception as e:
            logger.warning(f"Failed to load translation cache: {e}")
            self.cache = {}
    
    def save_cache(self):
        """Save translation cache to file"""
        try:
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(self.cache, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"Failed to save translation cache: {e}")
    
    def load_static_translations(self):
        """Load static translations for common agricultural terms"""
        static_translations = {
            # English to Odia
            'en_to_or': {
                # Basic terms
                'yield': 'ଅମଳ',
                'crop': 'ଫସଲ',
                'rice': 'ଚାଉଳ',
                'wheat': 'ଗହମ',
                'irrigation': 'ଜଳସେଚନ',
                'fertilizer': 'ସାର',
                'soil': 'ମାଟି',
                'weather': 'ପାଗ',
                'rainfall': 'ବର୍ଷା',
                'temperature': 'ତାପମାତ୍ରା',
                'humidity': 'ଆର୍ଦ୍ରତା',
                
                # Advisory terms
                'recommended': 'ସୁପାରିଶ',
                'apply': 'ପ୍ରୟୋଗ କରନ୍ତୁ',
                'monitor': 'ନଜର ରଖନ୍ତୁ',
                'increase': 'ବୃଦ୍ଧି କରନ୍ତୁ',
                'decrease': 'କମ କରନ୍ତୁ',
                'maintain': 'ବଜାୟ ରଖନ୍ତୁ',
                
                # Units
                'tons per hectare': 'ଟନ୍ ପ୍ରତି ହେକ୍ଟର',
                'kg per hectare': 'କିଲୋଗ୍ରାମ ପ୍ରତି ହେକ୍ଟର',
                'millimeters': 'ମିଲିମିଟର',
                'degrees celsius': 'ଡିଗ୍ରୀ ସେଲସିୟସ',
                
                # Common phrases
                'high confidence': 'ଉଚ୍ଚ ବିଶ୍ୱାସ',
                'medium confidence': 'ମଧ୍ୟମ ବିଶ୍ୱାସ',
                'low confidence': 'କମ ବିଶ୍ୱାସ',
                'highly recommended': 'ଅତ୍ୟଧିକ ସୁପାରିଶ',
                'consider this option': 'ଏହି ବିକଳ୍ପକୁ ବିଚାର କରନ୍ତୁ',
            },
            
            # Odia to English
            'or_to_en': {
                'ଅମଳ': 'yield',
                'ଫସଲ': 'crop',
                'ଚାଉଳ': 'rice',
                'ଗହମ': 'wheat',
                'ଜଳସେଚନ': 'irrigation',
                'ସାର': 'fertilizer',
                'ମାଟି': 'soil',
                'ପାଗ': 'weather',
                'ବର୍ଷା': 'rainfall',
                'ତାପମାତ୍ରା': 'temperature',
                'ଆର୍ଦ୍ରତା': 'humidity',
            }
        }
        
        # Add static translations to cache
        for direction, translations in static_translations.items():
            for source, target in translations.items():
                cache_key = f"{direction}:{source.lower()}"
                self.cache[cache_key] = {
                    'translation': target,
                    'timestamp': datetime.now().isoformat(),
                    'source': 'static'
                }
    
    async def translate(self, text: str, source_lang: str = 'en', 
                       target_lang: str = 'or') -> str:
        """Translate text between languages"""
        if not text or not text.strip():
            return text
        
        # Check cache first
        cache_key = f"{source_lang}_to_{target_lang}:{text.lower()}"
        if cache_key in self.cache:
            cached_result = self.cache[cache_key]
            # Check if cache entry is not too old (30 days)
            cache_time = datetime.fromisoformat(cached_result['timestamp'])
            if datetime.now() - cache_time < timedelta(days=30):
                logger.debug(f"Using cached translation for: {text[:50]}...")
                return cached_result['translation']
        
        # Try API translation
        if self.gemini_api_key:
            try:
                translated_text = await self.translate_with_gemini(
                    text, source_lang, target_lang
                )
                
                # Cache the result
                self.cache[cache_key] = {
                    'translation': translated_text,
                    'timestamp': datetime.now().isoformat(),
                    'source': 'gemini'
                }
                
                # Save cache periodically
                if len(self.cache) % 10 == 0:
                    self.save_cache()
                
                return translated_text
                
            except Exception as e:
                logger.error(f"Gemini translation failed: {e}")
        
        # Fallback: try word-by-word translation for key terms
        return self.fallback_translation(text, source_lang, target_lang)
    
    async def translate_with_gemini(self, text: str, source_lang: str, 
                                  target_lang: str) -> str:
        """Translate using Gemini API"""
        # Language mapping
        lang_map = {
            'en': 'English',
            'or': 'Odia'
        }
        
        source_language = lang_map.get(source_lang, 'English')
        target_language = lang_map.get(target_lang, 'Odia')
        
        prompt = f"""
        Translate the following agricultural text from {source_language} to {target_language}.
        Keep technical terms accurate and use appropriate agricultural terminology.
        
        Text to translate: "{text}"
        
        Provide only the translation, no explanations.
        """
        
        # Gemini API call (simplified - you would use the actual Gemini client)
        async with aiohttp.ClientSession() as session:
            headers = {
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {self.gemini_api_key}'
            }
            
            # This is a placeholder - replace with actual Gemini API endpoint
            url = "https://generativelanguage.googleapis.com/v1/models/gemini-pro:generateContent"
            
            payload = {
                "contents": [{
                    "parts": [{
                        "text": prompt
                    }]
                }]
            }
            
            try:
                async with session.post(url, headers=headers, json=payload) as response:
                    if response.status == 200:
                        result = await response.json()
                        # Extract translation from response
                        translated_text = result.get('candidates', [{}])[0].get('content', {}).get('parts', [{}])[0].get('text', text)
                        return translated_text.strip()
                    else:
                        logger.error(f"Gemini API error: {response.status}")
                        raise Exception(f"API error: {response.status}")
                        
            except Exception as e:
                logger.error(f"Gemini API request failed: {e}")
                raise
    
    def fallback_translation(self, text: str, source_lang: str, 
                           target_lang: str) -> str:
        """Fallback translation using cached terms"""
        direction = f"{source_lang}_to_{target_lang}"
        
        # Simple word replacement for key terms
        translated_text = text
        
        for cache_key, cache_value in self.cache.items():
            if cache_key.startswith(f"{direction}:"):
                source_term = cache_key.split(':', 1)[1]
                target_term = cache_value['translation']
                
                # Case-insensitive replacement
                import re
                pattern = re.compile(re.escape(source_term), re.IGNORECASE)
                translated_text = pattern.sub(target_term, translated_text)
        
        return translated_text
    
    async def translate_advisory(self, advisory_result: Dict[str, Any], 
                               target_language: str) -> Dict[str, Any]:
        """Translate advisory recommendations"""
        if target_language == 'en':
            return advisory_result  # Already in English
        
        try:
            translated_advisory = {}
            
            for key, value in advisory_result['advisory'].items():
                if isinstance(value, str):
                    translated_value = await self.translate(value, 'en', target_language)
                    translated_advisory[key] = translated_value
                else:
                    translated_advisory[key] = value
            
            # Update the result
            advisory_result['advisory'] = translated_advisory
            
            # Translate disclaimer if present
            if 'disclaimer' in advisory_result['advisory']:
                advisory_result['advisory']['disclaimer'] = await self.translate(
                    advisory_result['advisory']['disclaimer'], 'en', target_language
                )
            
            return advisory_result
            
        except Exception as e:
            logger.error(f"Advisory translation failed: {e}")
            return advisory_result  # Return original if translation fails
    
    def get_supported_languages(self) -> List[str]:
        """Get list of supported languages"""
        return ['en', 'or']
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get translation cache statistics"""
        total_entries = len(self.cache)
        static_entries = sum(1 for v in self.cache.values() if v.get('source') == 'static')
        api_entries = total_entries - static_entries
        
        return {
            'total_cached_translations': total_entries,
            'static_translations': static_entries,
            'api_translations': api_entries,
            'cache_file': self.cache_file
        }
    
    def clear_cache(self):
        """Clear translation cache"""
        self.cache = {}
        if os.path.exists(self.cache_file):
            os.remove(self.cache_file)
        self.load_static_translations()  # Reload static translations
        logger.info("Translation cache cleared")
