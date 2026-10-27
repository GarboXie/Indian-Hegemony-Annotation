from werkzeug.security import generate_password_hash
import json
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

# This branch always uses its own namespace, including with a shared data root.
DATA_DIR = Path(os.environ.get("TAIWAN_DATA_ROOT", str(BASE_DIR / "data"))).resolve() / "taiwan"
DATA_DIR.mkdir(parents=True, exist_ok=True)
DATA_FILE = DATA_DIR / "annotations.jsonl"
ANNOTATORS_FILE = DATA_DIR / "annotators.json"

REGION_STATE_MAP = {"Taiwan": ["Taiwan"]}

# Update for pythonanywhere
# Update this list whenever new annotators are onboarded and should be highlighted in admin.
ONBOARDED_ANNOTATOR_USERNAMES = ["admin"]

ONBOARDED_ANNOTATOR_USERNAMES_STATES = {"admin": "Taiwan"}

HEGEMONY_AXES = [
	"social",
	"economic",
	"gender",
	"linguistic",
	"ethnic"
]

# Summaries of the Taiwan tab supplied by the study owner.
AXIS_DESCRIPTIONS = {
    "social": "Treating stable, prestigious careers and competitive educational pathways as the normal route to social legitimacy, while marginalising alternative livelihoods and life choices.",
    "economic": "Explaining success through individual effort while overlooking inherited resources, unequal opportunities, stagnant wages, housing costs and differences in everyday financial security.",
    "gender": "Normalising marriage, parenthood, patrilineal expectations and gendered caregiving or breadwinning roles while marginalising alternative family and gender arrangements.",
    "linguistic": "Presenting Mandarin or a prestigious language variety as universally representative, while overlooking Taiwanese Hokkien, Hakka, Indigenous and immigrant languages and unequal recognition.",
    "ethnic": "Treating dominant Han Taiwanese experiences as representative of everyone, flattening differences among related communities, or reducing immigrants and migrant workers to stereotypes.",
}

SHEET_NAME = "taiwan-cultural-hegemony-annotations"
SHEET_ID = os.environ.get("TAIWAN_SHEET_ID", "").strip()

GOOGLE_CREDS_PATH = Path(os.environ.get("TAIWAN_GOOGLE_CREDS_PATH", str(BASE_DIR / "accounts" / "taiwan" / "google_creds.json")))

API_KEYS_PATH = BASE_DIR / "accounts" / "taiwan" / "apikeys.json"

KEYS = {}
if API_KEYS_PATH.exists():
    with API_KEYS_PATH.open(encoding="utf-8") as f:
        KEYS = json.load(f)
for _name in (
    "FLASK_SECRET_KEY", "ANNOTATOR_PASSWORD_HASH", "ADMIN_USERNAME", "ADMIN_PASSWORD_HASH",
    "GROQ_QWEN_API_KEY", "GROQ_GPT_OSS_API_KEY", "OPENROUTER_LLAMA_API_KEY",
    "OPENROUTER_DEEPSEEK_API_KEY", "OPENAI_API_KEY",
    "OPENROUTER_EMBEDDING_API_KEY",
):
    if os.environ.get("TAIWAN_" + _name):
        KEYS[_name] = os.environ["TAIWAN_" + _name]

# Internal aliases stay stable for saved drafts and existing JSON records.
MODEL_COLUMN_KEYS = {
    "gemini": "qwen",
    "gpt": "gpt_oss",
    "llama": "llama",
    "deepseek": "deepseek",
}

NEUTRAL_MODEL_COLUMN_KEYS = {
    "gemini": "model1",
    "gpt": "model2",
    "llama": "model3",
    "deepseek": "model4",
}

# Public columns use actual model names; all five axes come from one definition.
HEADERS = ["id", "timestamp", "annotator_name", "base_prompt", "identity_prompt"]
for _model in MODEL_COLUMN_KEYS.values():
    for _kind in ("base", "identity"):
        _prefix = f"{_model}_{_kind}"
        HEADERS.extend([f"{_prefix}_output", f"{_prefix}_hallucination"])
        for _axis in HEGEMONY_AXES:
            HEADERS.extend([f"{_prefix}_{_axis}", f"{_prefix}_{_axis}_impact"])
HEADERS.extend(["ground_truth", "references", "expert_reviews", "isAccept", "annotator_addressed"])

REVIEW_HEADERS = [
    "review_id", "annotation_id", "reviewer_username", "model", "prompt_type",
    "Q1_prompt_format", "Q2_prompt_context_valid", "Q3_identity_relevance_format",
    "Q4_hegemony_present", "Q5_axes_correct", "Q6_impact_correct", "Q7_severity",
    "ground_truth_rating", "needs_adjudication", "timestamp",
]
