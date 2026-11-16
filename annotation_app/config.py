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

SHEET_NAME = "chinese-cultural-hegemony-annotations"

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
	"native_prompt",

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
	"gemini_native_output",
	"gemini_native_hallucination",
	"gemini_native_social",
	"gemini_native_social_impact",
	"gemini_native_economic",
	"gemini_native_economic_impact",
	"gemini_native_cultural",
	"gemini_native_cultural_impact",
	"gemini_native_gender",
	"gemini_native_gender_impact",
	"gemini_native_linguistic",
	"gemini_native_linguistic_impact",
	"gemini_native_regional",
	"gemini_native_regional_impact",

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
	"gpt_native_output",
	"gpt_native_hallucination",
	"gpt_native_social",
	"gpt_native_social_impact",
	"gpt_native_economic",
	"gpt_native_economic_impact",
	"gpt_native_cultural",
	"gpt_native_cultural_impact",
	"gpt_native_gender",
	"gpt_native_gender_impact",
	"gpt_native_linguistic",
	"gpt_native_linguistic_impact",
	"gpt_native_regional",
	"gpt_native_regional_impact",

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
	"llama_native_output",
	"llama_native_hallucination",
	"llama_native_social",
	"llama_native_social_impact",
	"llama_native_economic",
	"llama_native_economic_impact",
	"llama_native_cultural",
	"llama_native_cultural_impact",
	"llama_native_gender",
	"llama_native_gender_impact",
	"llama_native_linguistic",
	"llama_native_linguistic_impact",
	"llama_native_regional",
	"llama_native_regional_impact",

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
	"deepseek_native_output",
	"deepseek_native_hallucination",
	"deepseek_native_social",
	"deepseek_native_social_impact",
	"deepseek_native_economic",
	"deepseek_native_economic_impact",
	"deepseek_native_cultural",
	"deepseek_native_cultural_impact",
	"deepseek_native_gender",
	"deepseek_native_gender_impact",
	"deepseek_native_linguistic",
	"deepseek_native_linguistic_impact",
	"deepseek_native_regional",
	"deepseek_native_regional_impact",

	"ground_truth",

	# --- references ---
	"references",
	"expert_reviews",
	"isAccept",
	"annotator_addressed",
]

# Keep earlier worksheet columns in place for historical annotations.
HEADERS.extend(["ground_truth_native", "second_prompt_type"])
