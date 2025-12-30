"""
Gemini API client for LLM interactions
"""
import os
import google.generativeai as genai
from typing import Optional
import time


class GeminiClient:
    """Client for interacting with Gemini API"""

    def __init__(self, api_key: Optional[str] = None, model: str = "gemini-1.5-flash"):
        """
        Initialize Gemini client

        Args:
            api_key: Gemini API key (if None, uses GEMINI_API_KEY env var)
            model: Model name to use
        """
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY not found in environment variables")

        genai.configure(api_key=self.api_key)
        self.model_name = model
        self.model = genai.GenerativeModel(model)

    def generate(self, prompt: str, temperature: float = 0.7, max_retries: int = 3) -> str:
        """
        Generate text using Gemini

        Args:
            prompt: Input prompt
            temperature: Sampling temperature (0.0 to 1.0)
            max_retries: Maximum retry attempts on failure

        Returns:
            Generated text
        """
        generation_config = genai.types.GenerationConfig(
            temperature=temperature,
            max_output_tokens=2048,
        )

        for attempt in range(max_retries):
            try:
                response = self.model.generate_content(
                    prompt,
                    generation_config=generation_config
                )
                return response.text
            except Exception as e:
                if attempt < max_retries - 1:
                    wait_time = 2 ** attempt  # Exponential backoff
                    print(f"Error: {e}. Retrying in {wait_time}s...")
                    time.sleep(wait_time)
                else:
                    raise Exception(f"Failed after {max_retries} attempts: {e}")

    def generate_with_system_prompt(self, system_prompt: str, user_prompt: str,
                                    temperature: float = 0.7) -> str:
        """
        Generate with both system and user prompts

        Args:
            system_prompt: System/role instructions
            user_prompt: User's actual prompt
            temperature: Sampling temperature

        Returns:
            Generated text
        """
        combined_prompt = f"{system_prompt}\n\n{user_prompt}"
        return self.generate(combined_prompt, temperature)
