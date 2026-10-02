from werkzeug.security import generate_password_hash
import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

DATA_FILE = BASE_DIR / "static" / "annotations.jsonl"

REGION_STATE_MAP = {
	"North China": [
        "Beijing",
        "Tianjin",
        "Hebei",
        "Shanxi",
        "Inner Mongolia"
    ],

    "Northeast China": [
        "Liaoning",
        "Jilin",
        "Heilongjiang"
    ],

    "Northwestern China": [
        "Shaanxi",
        "Gansu",
        "Qinghai",
        "Ningxia",
        "Xinjiang"
    ],

    "East China": [
        "Shanghai",
        "Jiangsu",
        "Zhejiang",
        "Anhui",
        "Fujian",
        "Taiwan",
        "Jiangxi",
        "Shandong"
    ],

    "South Central China": [
        "Henan",
        "Hubei",
        "Hunan",
        "Guangdong",
        "Guangxi",
        "Hainan"
    ],

    "Southwestern China": [
        "Chongqing",
        "Sichuan",
        "Guizhou",
        "Yunnan",
        "Tibet"
    ]
    
}

# Update for pythonanywhere
# Update this list whenever new annotators are onboarded and should be highlighted in admin.
ONBOARDED_ANNOTATOR_USERNAMES = [
	"admin",
	"Arnab6203",
	"nishtharajput",
	"Manasikelkar26",
	"Riddhi Vora",
	"Ajit Rana",
	"Priyanka",
	"Riddhi157",
	"tauseef",
	"Aishwarya Gadgil",
	"Ashish",
	"Manshi Patel",
	"Veera Hymavathi Sirisipalli",
	"Subham48",
	"Lila Ghimire",
	"neerav",
	"Sohail Khan",
	"Adya",
	"kameshwari04",
	"Manorath Thacker",
	"Payal",
	"hareeshreji",
	"Akhlaqur@12345",
	"binduhemant",
	"Gayathri",
	"Sylesh",
	"Som_Shikhar",
	"PallaviBeauvoir",
	"Palak_Shah",
]

ONBOARDED_ANNOTATOR_USERNAMES_STATES = {
	"admin": "Uttar Pradesh",
	"Arnab6203": "West Bengal",
	"nishtharajput": "Haryana",
	"Manasikelkar26": "Maharashtra",
	"Riddhi Vora": "Gujarat",
	"Ajit Rana": "Haryana",
	"Priyanka": "Haryana",
	"Riddhi157": "Maharashtra",
	"tauseef": "Bihar",
	"Aishwarya Gadgil": "Maharashtra",
	"Ashish": "Jammu and Kashmir",
	"Manshi Patel": "Uttar Pradesh",
	"Veera Hymavathi Sirisipalli": "Andhra Pradesh",
	"Subham48": "West Bengal",
	"Lila Ghimire": "West Bengal",
	"neerav": "Uttar Pradesh",
	"Sohail Khan": "Jammu and Kashmir",
	"Adya": "Kerala",
	"kameshwari04": "Bihar",
	"Manorath Thacker": "Gujarat",
	"Payal": "Odisha",
	"hareeshreji": "Kerala",
	"Akhlaqur@12345": "Bihar",
	"binduhemant": "Andhra Pradesh",
	"Gayathri": "Andhra Pradesh",
	"Sylesh": "Andhra Pradesh",
	"Som_Shikhar": "Odisha",
	"PallaviBeauvoir": "Odisha",
	"Palak_Shah" : "Gujarat"
}

HEGEMONY_AXES = [
	"social",
	"economic",
	"cultural",	
	"gender",
	"linguistic",
	"regional"
]

SHEET_NAME = "chinese-cultural-hegemony-pilot-annotations"

GOOGLE_CREDS_PATH = BASE_DIR / "accounts" / "google_creds.json"

API_KEYS_PATH = BASE_DIR / "accounts" / "apikeys.json"

with open(API_KEYS_PATH, "r") as f:
	KEYS = json.load(f)

# llama is actually GPT-OSS
HEADERS = [
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
	"gemini_base_cultural",
	"gemini_base_cultural_impact",
	"gemini_base_gender",
	"gemini_base_gender_impact",
	"gemini_base_linguistic",
	"gemini_base_linguistic_impact",
	"gemini_base_regional",
	"gemini_base_regional_impact",

	# === GEMINI IDENTITY ===
	"gemini_identity_output",
	"gemini_identity_hallucination",
	"gemini_identity_social",
	"gemini_identity_social_impact",
	"gemini_identity_economic",
	"gemini_identity_economic_impact",
	"gemini_identity_cultural",
	"gemini_identity_cultural_impact",
	"gemini_identity_gender",
	"gemini_identity_gender_impact",
	"gemini_identity_linguistic",
	"gemini_identity_linguistic_impact",
	"gemini_identity_regional",
	"gemini_identity_regional_impact",

	# === GPT BASE ===
	"gpt_base_output",
	"gpt_base_hallucination",
	"gpt_base_social",
	"gpt_base_social_impact",
	"gpt_base_economic",
	"gpt_base_economic_impact",
	"gpt_base_cultural",
	"gpt_base_cultural_impact",
	"gpt_base_gender",
	"gpt_base_gender_impact",
	"gpt_base_linguistic",
	"gpt_base_linguistic_impact",
	"gpt_base_regional",
	"gpt_base_regional_impact",

	# === GPT IDENTITY ===
	"gpt_identity_output",
	"gpt_identity_hallucination",
	"gpt_identity_social",
	"gpt_identity_social_impact",
	"gpt_identity_economic",
	"gpt_identity_economic_impact",
	"gpt_identity_cultural",
	"gpt_identity_cultural_impact",
	"gpt_identity_gender",
	"gpt_identity_gender_impact",
	"gpt_identity_linguistic",
	"gpt_identity_linguistic_impact",
	"gpt_identity_regional",
	"gpt_identity_regional_impact",

	# === LLAMA i.e GPT-OSS-120B BASE ===
	"llama_base_output",
	"llama_base_hallucination",
	"llama_base_social",
	"llama_base_social_impact",
	"llama_base_economic",
	"llama_base_economic_impact",
	"llama_base_cultural",
	"llama_base_cultural_impact",
	"llama_base_gender",
	"llama_base_gender_impact",
	"llama_base_linguistic",
	"llama_base_linguistic_impact",
	"llama_base_regional",
	"llama_base_regional_impact",

	# === LLAMA i.e GPT-OSS-120B IDENTITY ===
	"llama_identity_output",
	"llama_identity_hallucination",
	"llama_identity_social",
	"llama_identity_social_impact",
	"llama_identity_economic",
	"llama_identity_economic_impact",
	"llama_identity_cultural",
	"llama_identity_cultural_impact",
	"llama_identity_gender",
	"llama_identity_gender_impact",
	"llama_identity_linguistic",
	"llama_identity_linguistic_impact",
	"llama_identity_regional",
	"llama_identity_regional_impact",

	# === DEEPSEEK BASE ===
	"deepseek_base_output",
	"deepseek_base_hallucination",
	"deepseek_base_social",
	"deepseek_base_social_impact",
	"deepseek_base_economic",
	"deepseek_base_economic_impact",
	"deepseek_base_cultural",
	"deepseek_base_cultural_impact",
	"deepseek_base_gender",
	"deepseek_base_gender_impact",
	"deepseek_base_linguistic",
	"deepseek_base_linguistic_impact",
	"deepseek_base_regional",
	"deepseek_base_regional_impact",

	# === DEEPSEEK IDENTITY ===
	"deepseek_identity_output",
	"deepseek_identity_hallucination",
	"deepseek_identity_social",
	"deepseek_identity_social_impact",
	"deepseek_identity_economic",
	"deepseek_identity_economic_impact",
	"deepseek_identity_cultural",
	"deepseek_identity_cultural_impact",
	"deepseek_identity_gender",
	"deepseek_identity_gender_impact",
	"deepseek_identity_linguistic",
	"deepseek_identity_linguistic_impact",
	"deepseek_identity_regional",
	"deepseek_identity_regional_impact",

	"ground_truth",

	# --- references ---
	"references",
	"expert_reviews",
	"isAccept",
	"annotator_addressed",
]
