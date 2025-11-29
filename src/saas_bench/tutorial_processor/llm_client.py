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
            model="grok-4-1-fast-reasoning",
            messages=messages,
        )

        return response.choices[0].message.content or ""

    def structured_output(
        self, prompt: str, system: str, response_model: Type[BaseModel]
    ) -> BaseModel:
        """Get structured output using OpenAI SDK's structured outputs feature."""
        import json

        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        # Try beta structured outputs API first
        try:
            if hasattr(self.client, "beta") and hasattr(self.client.beta, "chat"):
                response = self.client.beta.chat.completions.parse(
                    model="grok-4-1-fast-reasoning",
                    messages=messages,
                    response_format=response_model,
                )
                return response.choices[0].message.parsed
        except (AttributeError, Exception):
            pass

        # Fallback: Use JSON mode and parse manually
        # Add instruction to return JSON matching the schema
        schema = response_model.model_json_schema()
        json_prompt = f"""{prompt}

Please respond with a valid JSON object that matches this schema:
{json.dumps(schema, indent=2)}

Return ONLY the JSON object, no additional text or markdown formatting."""

        messages_with_json = []
        if system:
            messages_with_json.append({"role": "system", "content": system})
        messages_with_json.append({"role": "user", "content": json_prompt})

        response = self.client.chat.completions.create(
            model="grok-3",
            messages=messages_with_json,
            response_format={"type": "json_object"},
        )

        content = response.choices[0].message.content or "{}"

        # Clean up content if it's wrapped in markdown code blocks
        if content.strip().startswith("```"):
            # Extract JSON from markdown code blocks
            lines = content.strip().split("\n")
            content = "\n".join(lines[1:-1]) if len(lines) > 2 else content

        # Parse JSON and create Pydantic model
        json_data = json.loads(content)
        return response_model(**json_data)
