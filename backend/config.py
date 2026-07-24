import os
import sys
import site

# Ensure user site-packages are in sys.path
user_site = site.getusersitepackages()
if user_site not in sys.path:
    sys.path.insert(0, user_site)

from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "") or os.getenv("GOOGLE_API_KEY", "")

def get_llm(model_provider: str = "auto"):
    """
    Returns an initialized LLM based on available API keys.
    Prefers Groq (llama-3.1-8b-instant), falls back to Gemini (gemini-1.5-flash).
    """
    if (model_provider == "groq" or model_provider == "auto") and GROQ_API_KEY and GROQ_API_KEY != "your_groq_api_key_here":
        try:
            from langchain_groq import ChatGroq
            return ChatGroq(
                model_name="llama-3.1-8b-instant",
                groq_api_key=GROQ_API_KEY,
                temperature=0.2
            )
        except Exception as e:
            print(f"Warning: Could not initialize Groq 8b LLM: {e}")

    if (model_provider == "gemini" or model_provider == "auto") and GEMINI_API_KEY and GEMINI_API_KEY != "your_gemini_api_key_here":
        try:
            from langchain_google_genai import ChatGoogleGenerativeAI
            return ChatGoogleGenerativeAI(
                model="gemini-1.5-flash",
                google_api_key=GEMINI_API_KEY,
                temperature=0.2
            )
        except Exception as e:
            print(f"Warning: Could not initialize Gemini LLM: {e}")

    raise ValueError(
        "No valid API keys found! Please set GROQ_API_KEY or GEMINI_API_KEY in your .env file."
    )
