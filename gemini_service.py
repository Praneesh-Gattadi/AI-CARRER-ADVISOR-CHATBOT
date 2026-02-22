# ================== gemini_service.py ==================
import json
import requests
from loguru import logger

class GeminiService:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.api_url = "https://openrouter.ai/api/v1/chat/completions"
        logger.info("✅ OpenRouter proxy initialized")

    def generate_response(self, prompt: str) -> str:
        logger.info(f"📤 Sending request to OpenRouter | prompt_length={len(prompt)}")

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "HTTP-Referer": "http://localhost:8501", 
            "X-Title": "AI Career Advisor Chatbot"           
        }

        # 🚀 REQUIREMENT 4.1: Proper exception handling and fallback mechanism
        # If one free model is offline (404/400), it instantly tries the next one.
        models_to_try = [
            "google/gemini-2.0-flash-thinking-exp:free", # Primary: Newest Gemini 2.0
            "google/gemma-3-27b-it:free",                # Fallback 1: Google's Open-Source Gemma 3
            "openrouter/free"                            # Fallback 2: Auto-routes to ANY available free model
        ]

        last_error = ""

        for model_id in models_to_try:
            payload = {
                "model": model_id,
                "messages": [{"role": "user", "content": prompt}]
            }

            try:
                logger.info(f"🔄 Attempting model: {model_id}")
                response = requests.post(self.api_url, headers=headers, json=payload, timeout=30)
                
                # If OpenRouter rejects the model (400) or it is offline (404), skip to the next
                if response.status_code in [400, 404]:
                    last_error = response.text
                    logger.warning(f"⚠️ Model {model_id} unavailable. Trying fallback...")
                    continue
                    
                response.raise_for_status() 
                data = response.json()

                if "choices" in data and len(data["choices"]) > 0:
                    text = data["choices"][0]["message"]["content"]
                    logger.info(f"✅ Response received successfully from {model_id}")
                    return text

            except requests.exceptions.HTTPError as e:
                last_error = e.response.text
                if "401" in str(e):
                     return "🔑 **Invalid API Key** — Your OpenRouter key was rejected. Check your .env file."
                continue
                
            except Exception as e:
                last_error = str(e)
                continue

        # If all fallbacks fail, print the very last error we got
        return f"🚨 **All Free Models Offline:** OpenRouter's free endpoints are currently down. Last error:\n```json\n{last_error}\n```"