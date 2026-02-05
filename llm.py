import google.generativeai as genai
import os
from dotenv import load_dotenv
from google.api_core import exceptions as google_exceptions

load_dotenv()

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

model = genai.GenerativeModel("gemini-2.5-flash-lite")


def detect_intent(message):

    prompt = f"""
Return ONLY one word from this list:

refund
delivery
payment
cancel
other

Message: {message}
"""

    try:
        response = model.generate_content(
            prompt,
            generation_config={
                "temperature": 0,
                "max_output_tokens": 3
            }
        )

        intent = response.text.strip().lower()

        allowed = {"refund", "delivery", "payment", "cancel", "other"}

        return intent if intent in allowed else "other"

    except google_exceptions.ResourceExhausted:
        return "other"
    except Exception:
        return "other"


def chat_reply(context):

    prompt = f"""
You are a high-performance AI support agent for a food delivery platform.

STRICT RULES:
- Never ask for order ID.
- Never ask for information already provided.
- Do not apologize excessively.
- Avoid corporate phrases like "We understand your frustration".
- Be direct and human.

STYLE:
- Maximum 2–3 sentences.
- Prefer facts over empathy.
- No long paragraphs.

ESCALATION:
Only suggest creating a ticket if the issue cannot be resolved automatically.

CONTEXT:
{context}
"""

    try:
        response = model.generate_content(
            prompt,
            generation_config={
                "temperature": 0.3,
                "max_output_tokens": 120
            }
        )

        return response.text.strip()

    except google_exceptions.ResourceExhausted:
        return "AI service is temporarily busy. Please try again shortly."
    except Exception:
        return "I'm having trouble responding right now. Please try again."