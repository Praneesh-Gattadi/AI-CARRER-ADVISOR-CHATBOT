# ================== gemini_service.py ==================
from google import genai
from google.genai import types
from loguru import logger

class GeminiService:
    def __init__(self, api_key: str):
        self.api_key = api_key
        # Initialize Google GenAI client using the official SDK
        self.client = genai.Client(api_key=self.api_key)
        logger.info("✅ Official Google GenAI SDK client initialized")

    def generate_response(self, messages: list, system_instruction: str) -> str:
        """
        Generates a non-streaming response from the official Gemini API with robust fallbacks.
        
        Args:
            messages: List of structured message dicts: [{"role": "user"/"model", "content": "..."}]
            system_instruction: The core prompt guardrails.
            
        Returns:
            The text response from the model.
        """
        logger.info(f"📤 Sending request to Gemini API | messages_count={len(messages)}")

        models_to_try = [
            "gemini-1.5-flash",       # Stable production model with extremely high free-tier quota limits
            "gemini-2.5-flash",       # Primary 2.5 flash
            "gemini-3.1-flash-lite",  # First fallback: next-gen lightweight responsive model
            "gemini-2.0-flash"        # Second fallback: 2.0 series model
        ]

        # Convert dictionary messages to Google GenAI Content types
        contents = []
        for msg in messages:
            role = "user" if msg["role"] == "user" else "model"
            contents.append(
                types.Content(
                    role=role,
                    parts=[types.Part.from_text(text=msg["content"])]
                )
            )

        config = types.GenerateContentConfig(
            system_instruction=system_instruction,
            tools=[{"google_search": {}}]
        )

        last_error = ""

        for model_id in models_to_try:
            try:
                logger.info(f"🔄 Attempting model: {model_id}")
                response = self.client.models.generate_content(
                    model=model_id,
                    contents=contents,
                    config=config
                )
                
                if response.text:
                    logger.info(f"✅ Response received successfully from {model_id}")
                    return response.text

            except Exception as e:
                last_error = str(e)
                logger.warning(f"⚠️ Model {model_id} failed: {last_error}. Trying fallback...")
                if "API_KEY_INVALID" in last_error or "401" in last_error:
                    return "🔑 **Invalid API Key** — Your Google Gemini API key was rejected. Check your .env file."
                continue

        return f"🚨 **All Gemini Models Offline:** The Gemini API endpoints are currently experiencing issues. Last error:\n```\n{last_error}\n```"

    def generate_response_stream(self, messages: list, system_instruction: str):
        """
        Generates a streaming typewriter-like response from the official Gemini API with robust fallbacks.
        
        Args:
            messages: List of structured message dicts: [{"role": "user"/"model", "content": "..."}]
            system_instruction: The core prompt guardrails.
            
        Yields:
            Text chunks as they arrive from the model.
        """
        logger.info(f"📤 Sending streaming request to Gemini API | messages_count={len(messages)}")

        models_to_try = [
            "gemini-1.5-flash",       # Stable production model with high free tier limits
            "gemini-2.5-flash",       # Primary 2.5 flash
            "gemini-3.1-flash-lite",  # First fallback
            "gemini-2.0-flash"        # Second fallback
        ]

        # Convert dictionary messages to Google GenAI Content types
        contents = []
        for msg in messages:
            role = "user" if msg["role"] == "user" else "model"
            contents.append(
                types.Content(
                    role=role,
                    parts=[types.Part.from_text(text=msg["content"])]
                )
            )

        config = types.GenerateContentConfig(
            system_instruction=system_instruction,
            tools=[{"google_search": {}}]
        )

        last_error = ""

        for model_id in models_to_try:
            try:
                logger.info(f"🔄 Attempting streaming with model: {model_id}")
                response_stream = self.client.models.generate_content_stream(
                    model=model_id,
                    contents=contents,
                    config=config
                )
                
                for chunk in response_stream:
                    if chunk.text:
                        yield chunk.text
                
                logger.info(f"✅ Streaming response finished successfully from {model_id}")
                return # Exit on successful stream completion

            except Exception as e:
                last_error = str(e)
                logger.warning(f"⚠️ Model {model_id} failed in stream: {last_error}. Trying fallback...")
                if "API_KEY_INVALID" in last_error or "401" in last_error:
                    yield "🔑 **Invalid API Key** — Your Google Gemini API key was rejected. Check your .env file."
                    return
                continue

        # If all models in the fallback loop fail
        yield f"🚨 **All Gemini Models Offline:** The Gemini API endpoints are currently experiencing issues. Last error:\n```\n{last_error}\n```"