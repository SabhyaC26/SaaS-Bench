"""LLM client wrapper for Grok API using OpenAI SDK."""

import os
from typing import Type

from dotenv import load_dotenv
from openai import OpenAI
from pydantic import BaseModel

load_dotenv()


class GrokClient:
    """Wrapper around OpenAI SDK configured for Grok endpoints."""

    def __init__(self):
        """Initialize Grok client with API key from environment."""
        api_key = os.getenv("GROK_API_KEY")
        base_url = os.getenv("GROK_BASE_URL", "https://api.x.ai/v1")

        if not api_key:
            raise ValueError("GROK_API_KEY environment variable not set")

        self.client = OpenAI(api_key=api_key, base_url=base_url)

    def chat_completion(self, prompt: str, system: str = "") -> str:
        """Basic text completion."""
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        response = self.client.chat.completions.create(
            model="grok-beta",
            messages=messages,
        )

        return response.choices[0].message.content or ""

    def structured_output(
        self, prompt: str, system: str, response_model: Type[BaseModel]
    ) -> BaseModel:
        """Get structured output using OpenAI SDK's structured outputs feature."""
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        # Use structured outputs with Pydantic model
        response = self.client.beta.chat.completions.parse(
            model="grok-beta",
            messages=messages,
            response_format=response_model,
        )

        return response.choices[0].message.parsed

