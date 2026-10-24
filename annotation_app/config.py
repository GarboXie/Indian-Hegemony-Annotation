from werkzeug.security import generate_password_hash
import json
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

# This branch always uses its own namespace, including with a shared data root.
DATA_DIR = Path(os.environ.get("SINGAPORE_DATA_ROOT", str(BASE_DIR / "data"))).resolve() / "singapore"
DATA_DIR.mkdir(parents=True, exist_ok=True)
DATA_FILE = DATA_DIR / "annotations.jsonl"
ANNOTATORS_FILE = DATA_DIR / "annotators.json"

REGION_STATE_MAP = {"Singapore": ["Singapore"]}

# Update for pythonanywhere
# Update this list whenever new annotators are onboarded and should be highlighted in admin.
ONBOARDED_ANNOTATOR_USERNAMES = ["admin"]

ONBOARDED_ANNOTATOR_USERNAMES_STATES = {"admin": "Singapore"}

HEGEMONY_AXES = [
	"social",
	"economic",
	"religious",
	"gender",
	"linguistic",
	"ethnic"
]

SHEET_NAME = "singapore-cultural-hegemony-annotations"
SHEET_ID = os.environ.get("SINGAPORE_SHEET_ID", "").strip()

GOOGLE_CREDS_PATH = Path(os.environ.get("SINGAPORE_GOOGLE_CREDS_PATH", str(BASE_DIR / "accounts" / "singapore" / "google_creds.json")))

API_KEYS_PATH = BASE_DIR / "accounts" / "singapore" / "apikeys.json"

KEYS = {}
if API_KEYS_PATH.exists():
    with API_KEYS_PATH.open(encoding="utf-8") as f:
        KEYS = json.load(f)
for _name in (
    "FLASK_SECRET_KEY", "ANNOTATOR_PASSWORD_HASH", "ADMIN_USERNAME", "ADMIN_PASSWORD_HASH",
    "GROQ_QWEN_API_KEY", "GROQ_GPT_OSS_API_KEY", "OPENROUTER_LLAMA_API_KEY",
    "OPENROUTER_DEEPSEEK_API_KEY", "OPENAI_API_KEY",
):
    if os.environ.get("SINGAPORE_" + _name):
        KEYS[_name] = os.environ["SINGAPORE_" + _name]

# Internal aliases stay stable for saved drafts and existing JSON records.
MODEL_COLUMN_KEYS = {
    "gemini": "qwen_3_8_27b",
    "gpt": "gpt_oss_120b",
    "llama": "llama_4_maverick",
    "deepseek": "deepseek_v3_2",
}

NEUTRAL_MODEL_COLUMN_KEYS = {
    "gemini": "model1",
    "gpt": "model2",
    "llama": "model3",
    "deepseek": "model4",
}

LEGACY_HEADERS = [
	# --- metadata ---
	"id",
	"timestamp",
	"annotator_name",
	"region",
	"state",

	# --- prompts ---
	"base_prompt",
	"identity_prompt",

	# === GEMINI BASE ===
	"gemini_base_output",
	"gemini_base_hallucination",
	"gemini_base_social",
	"gemini_base_social_impact",
	"gemini_base_economic",
	"gemini_base_economic_impact",
	"gemini_base_religious",
	"gemini_base_religious_impact",
	"gemini_base_gender",
	"gemini_base_gender_impact",
	"gemini_base_linguistic",
	"gemini_base_linguistic_impact",
	"gemini_base_ethnic",
	"gemini_base_ethnic_impact",

	# === GEMINI IDENTITY ===
	"gemini_identity_output",
	"gemini_identity_hallucination",
	"gemini_identity_social",
	"gemini_identity_social_impact",
	"gemini_identity_economic",
	"gemini_identity_economic_impact",
	"gemini_identity_religious",
	"gemini_identity_religious_impact",
	"gemini_identity_gender",
	"gemini_identity_gender_impact",
	"gemini_identity_linguistic",
	"gemini_identity_linguistic_impact",
	"gemini_identity_ethnic",
	"gemini_identity_ethnic_impact",

	# === GPT BASE ===
	"gpt_base_output",
	"gpt_base_hallucination",
	"gpt_base_social",
	"gpt_base_social_impact",
	"gpt_base_economic",
	"gpt_base_economic_impact",
	"gpt_base_religious",
	"gpt_base_religious_impact",
	"gpt_base_gender",
	"gpt_base_gender_impact",
	"gpt_base_linguistic",
	"gpt_base_linguistic_impact",
	"gpt_base_ethnic",
	"gpt_base_ethnic_impact",

	# === GPT IDENTITY ===
	"gpt_identity_output",
	"gpt_identity_hallucination",
	"gpt_identity_social",
	"gpt_identity_social_impact",
	"gpt_identity_economic",
	"gpt_identity_economic_impact",
	"gpt_identity_religious",
	"gpt_identity_religious_impact",
	"gpt_identity_gender",
	"gpt_identity_gender_impact",
	"gpt_identity_linguistic",
	"gpt_identity_linguistic_impact",
	"gpt_identity_ethnic",
	"gpt_identity_ethnic_impact",

	# === LLAMA i.e GPT-OSS-120B BASE ===
	"llama_base_output",
	"llama_base_hallucination",
	"llama_base_social",
	"llama_base_social_impact",
	"llama_base_economic",
	"llama_base_economic_impact",
	"llama_base_religious",
	"llama_base_religious_impact",
	"llama_base_gender",
	"llama_base_gender_impact",
	"llama_base_linguistic",
	"llama_base_linguistic_impact",
	"llama_base_ethnic",
	"llama_base_ethnic_impact",

	# === LLAMA i.e GPT-OSS-120B IDENTITY ===
	"llama_identity_output",
	"llama_identity_hallucination",
	"llama_identity_social",
	"llama_identity_social_impact",
	"llama_identity_economic",
	"llama_identity_economic_impact",
	"llama_identity_religious",
	"llama_identity_religious_impact",
	"llama_identity_gender",
	"llama_identity_gender_impact",
	"llama_identity_linguistic",
	"llama_identity_linguistic_impact",
	"llama_identity_ethnic",
	"llama_identity_ethnic_impact",

	# === DEEPSEEK BASE ===
	"deepseek_base_output",
	"deepseek_base_hallucination",
	"deepseek_base_social",
	"deepseek_base_social_impact",
	"deepseek_base_economic",
	"deepseek_base_economic_impact",
	"deepseek_base_religious",
	"deepseek_base_religious_impact",
	"deepseek_base_gender",
	"deepseek_base_gender_impact",
	"deepseek_base_linguistic",
	"deepseek_base_linguistic_impact",
	"deepseek_base_ethnic",
	"deepseek_base_ethnic_impact",

	# === DEEPSEEK IDENTITY ===
	"deepseek_identity_output",
	"deepseek_identity_hallucination",
	"deepseek_identity_social",
	"deepseek_identity_social_impact",
	"deepseek_identity_economic",
	"deepseek_identity_economic_impact",
	"deepseek_identity_religious",
	"deepseek_identity_religious_impact",
	"deepseek_identity_gender",
	"deepseek_identity_gender_impact",
	"deepseek_identity_linguistic",
	"deepseek_identity_linguistic_impact",
	"deepseek_identity_ethnic",
	"deepseek_identity_ethnic_impact",

	"ground_truth",

	# --- references ---
	"references",
	"expert_reviews",
	"isAccept",
	"annotator_addressed",
]

# Previous public schema, retained for explicit migration and compatibility.
NEUTRAL_HEADERS = [
    NEUTRAL_MODEL_COLUMN_KEYS.get(header.split("_", 1)[0], header.split("_", 1)[0])
    + ("_" + header.split("_", 1)[1] if "_" in header else "")
    for header in LEGACY_HEADERS
]

HEADERS = [
    MODEL_COLUMN_KEYS.get(header.split("_", 1)[0], header.split("_", 1)[0])
    + ("_" + header.split("_", 1)[1] if "_" in header else "")
    for header in LEGACY_HEADERS
    if header not in {"region", "state"}
]
