import os
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

if not GEMINI_API_KEY:
    print(
        "[WARNING] GEMINI_API_KEY is not set. "
        "Set it in your environment or .env file if needed."
    )

import google.generativeai as genai

if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

DEFAULT_MODEL_NAME = "gemini-2.5-flash-lite"

def get_gemini_model(model_name: str = None):
    """
    Returns a configured Gemini model instance.

    Model priority:
    1) Explicit argument if provided
    2) DEFAULT_MODEL_NAME
    """
    if model_name is None:
        model_name = DEFAULT_MODEL_NAME
    return genai.GenerativeModel(model_name)
