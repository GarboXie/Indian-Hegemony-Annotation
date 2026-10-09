import json
from google import genai
from google.genai import types
from config import KEYS
from openai import OpenAI
import requests

# _gemini_client = genai.Client(api_key=KEYS["GEMINI_API_KEY"])
_gpt_client = OpenAI(api_key=KEYS["GPT_API_KEY"])
_deepseek_client =  OpenAI(api_key=KEYS["DEEPSEEK_API_KEY"], base_url="https://api.deepseek.com")

# def generate_gemini_output(prompt: str) -> str:
#     """
#     Gemini Output Generator
#     """
#     response = _gemini_client.models.generate_content(
#         model="gemini-3-flash-preview",
#         contents=[prompt],
#         config=types.GenerateContentConfig(
#             system_instruction="Answer in no more than 150 words in English.",
#             temperature=0.8
#         )
#     )
#     return response.text

# def generate_gemini_output(prompt: str) -> str:
#     """
#     Gemini Output Generator
#     """
#     _model = genai.GenerativeModel(
#     model_name="gemini-3-flash-preview",
#     system_instruction="Answer in no more than 150 words in English."
#     )
#     response = _model.generate_content(
#         prompt,
#         generation_config={
#             "temperature": 0.8
#         }
#     )

#     return response.text

_groq_client = OpenAI(api_key = KEYS["GROQ_API_KEY"], base_url = "https://api.groq.com/openai/v1")

def generate_gemini_output(prompt: str) -> str:
    """
    Generate Gemini response through OpenRouter.
    """
    response = requests.post(
        url="https://openrouter.ai/api/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {KEYS['OPENROUTER_API_KEY']}",
            "Content-Type": "application/json",
        },
        json={
            "model": "google/gemini-3-flash-preview",
            "messages": [
                {
                    "role": "system",
                    "content": "Answer in no more than 150 words in English."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": 0.8,
            "max_tokens": 1000
        },
        timeout=90
    )

    response.raise_for_status()
    result = response.json()

    choice = result["choices"][0]
    print("GEMINI FINISH REASON:", choice.get("finish_reason"))

    return choice["message"].get("content") or ""

def generate_gpt_output(prompt: str) -> str:
    """
    Generate GPT-5.2 response through OpenRouter.
    """
    response = requests.post(
        url="https://openrouter.ai/api/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {KEYS['OPENROUTER_API_KEY']}",
            "Content-Type": "application/json",
        },
        json={
            "model": "openai/gpt-5.2",
            "messages": [
                {
                    "role": "system",
                    "content": "Answer in no more than 150 words in English."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": 0.8,
            "max_tokens": 1000
        },
        timeout=90
    )

    response.raise_for_status()
    result = response.json()

    choice = result["choices"][0]
    print("GPT FINISH REASON:", choice.get("finish_reason"))

    return choice["message"].get("content") or ""

def generate_deepseek_output(prompt: str) -> str:
    """
    Generate DeepSeek V3.2 response through OpenRouter.
    """
    response = requests.post(
        url="https://openrouter.ai/api/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {KEYS['OPENROUTER_API_KEY']}",
            "Content-Type": "application/json",
        },
        json={
            "model": "deepseek/deepseek-v3.2",
            "messages": [
                {
                    "role": "system",
                    "content": "Answer in no more than 150 words in English."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": 0.8,
            "max_tokens": 1000,
            "reasoning": {"enabled": True}
        },
        timeout=90
    )

    response.raise_for_status()
    result = response.json()

    choice = result["choices"][0]
    print("DEEPSEEK FINISH REASON:", choice.get("finish_reason"))

    return choice["message"].get("content") or ""


def generate_llama_output(prompt: str) -> str:
    """
    Generate GPT-OSS-120B response through OpenRouter.
    """
    response = requests.post(
        url="https://openrouter.ai/api/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {KEYS['OPENROUTER_API_KEY']}",
            "Content-Type": "application/json",
        },
        json={
            "model": "openai/gpt-oss-120b",
            "messages": [
                {
                    "role": "system",
                    "content": "Answer in no more than 150 words in English."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": 0.8,
            "max_tokens": 1000
        },
        timeout=90
    )

    response.raise_for_status()
    result = response.json()

    choice = result["choices"][0]

    print("GPT-OSS FINISH REASON:", choice.get("finish_reason"))

    return choice["message"].get("content") or ""