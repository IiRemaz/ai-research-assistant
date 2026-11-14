
import os

from dotenv import load_dotenv
from google import genai
from google.genai import types


load_dotenv()


MODEL_NAME = os.getenv(
    "GEMINI_MODEL",
    "gemini-3.1-flash-lite"
)

REQUEST_TIMEOUT = 15000


_client = None


def get_client():
    global _client

    if _client is None:
        api_key = os.getenv("GEMINI_API_KEY")

        if not api_key:
            raise ValueError(
                "GEMINI_API_KEY is missing. "
                "Add it to your .env file."
            )

        _client = genai.Client(
            api_key=api_key,
            http_options=types.HttpOptions(
                timeout=REQUEST_TIMEOUT
            )
        )

    return _client


def generate_content(prompt: str):

    if not prompt or not prompt.strip():
        raise ValueError("Prompt cannot be empty.")

    client = get_client()

    try:
        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=prompt
        )

    except Exception as error:
        raise RuntimeError(
            f"Gemini API request failed: {error}"
        ) from error

    if response is None or not response.text:
        raise RuntimeError(
            "Gemini returned an empty response."
        )

    return response
