
from openai import OpenAI
import requests
from config import KEYS

SYSTEM_PROMPT = "Answer in no more than 150 words in English."

GROQ_BASE_URL = "https://api.groq.com/openai/v1"
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"


def _generate_groq(prompt: str, model: str, key_name: str) -> str:
    client = OpenAI(
        api_key=KEYS[key_name],
        base_url=GROQ_BASE_URL
    )

    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt}
        ],
        timeout=90
    )

    choice = response.choices[0]
    print(f"{model} FINISH REASON:", choice.finish_reason)

    return choice.message.content or ""


def _generate_openrouter(
    prompt: str,
    model: str,
    key_name: str,
    reasoning: bool = False
) -> str:
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt}
        ]
    }

    if reasoning:
        payload["reasoning"] = {"enabled": True}

    response = requests.post(
        OPENROUTER_URL,
        headers={
            "Authorization": f"Bearer {KEYS[key_name]}",
            "Content-Type": "application/json"
        },
        json=payload,
        timeout=90
    )

    response.raise_for_status()
    result = response.json()
    choice = result["choices"][0]

    print(f"{model} FINISH REASON:", choice.get("finish_reason"))

    return choice["message"].get("content") or ""


def generate_qwen_output(prompt: str) -> str:
    return _generate_groq(
        prompt,
        "qwen/qwen3.8-27b",
        "GROQ_QWEN_API_KEY"
    )


def generate_gpt_oss_output(prompt: str) -> str:
    return _generate_groq(
        prompt,
        "openai/gpt-oss-120b",
        "GROQ_GPT_OSS_API_KEY"
    )


def generate_llama_output(prompt: str) -> str:
    return _generate_openrouter(
        prompt,
        "meta-llama/llama-4-maverick",
        "OPENROUTER_LLAMA_API_KEY"
    )


def generate_deepseek_output(prompt: str) -> str:
    return _generate_openrouter(
        prompt,
        "deepseek/deepseek-v3.2",
        "OPENROUTER_DEEPSEEK_API_KEY",
        reasoning=True
    )
