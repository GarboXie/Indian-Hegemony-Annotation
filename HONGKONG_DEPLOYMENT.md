# Hong Kong portal deployment

Use only the hongkong-zone-portal branch in a separate checkout and web application.
No subzones: the study location is fixed to Hong Kong. Do not repoint the Mainland,
Singapore, Taiwan or India applications to this branch, and do not copy their annotation
files, account lists, draft directories, databases or embedding indexes.

## Study configuration

Five axes, in this order: social, economic, gender, linguistic, ethnic.
Source and Annotation Guidelines (Hong Kong Tab 1):
https://docs.google.com/document/d/12NAq50EGfsqa4CFQ0wyQ4Q47NRfAp6H1-qw0mYvQXN8/edit?tab=t.0

The four generation models and their blinded webpage labels are inherited from
the tested Singapore portal: Qwen (Model 1), GPT-OSS (Model 2), Llama Maverick
(Model 3), DeepSeek (Model 4). Full backend identifiers remain in JSON records.
Sheets/CSV prefixes are qwen, gpt_oss, llama, deepseek. Base and Identity remain
separate. There are 106 annotation columns and 15 legacy review-export columns,
without region/state. Internal location fields are fixed compatibility values.
Peer IAA review uses a dedicated Hong Kong SQLite database. Assignment lists start
empty until Hong Kong annotators are onboarded. No previous campaign data is loaded.

## Private configuration

All local runtime files live under annotation_app/data/hongkong/, including
annotations.jsonl, annotators.json, drafts/, notes/, iaa_reviews.db,
prompt_embeddings.json and persisted review assignments. Optional HONGKONG_DATA_ROOT
changes the parent directory but always uses its hongkong/ namespace. The cookie
name is hongkong_portal_session. Use a new session secret and new login/invite values.

Private files (ignored by Git):

- annotation_app/accounts/hongkong/apikeys.json
- annotation_app/accounts/hongkong/google_creds.json

From the Hong Kong virtualenv, run the interactive credential helper:

```bash
python annotation_app/scripts/setup_hongkong_credentials.py
```

It asks for an admin password, signup invitation code and four API keys without
echoing values. Existing populated settings are preserved. It creates a fresh
session secret. Do not run it through a heredoc, paste keys into chat or commit them.
Only this Hong Kong private JSON file is loaded; other portals' credentials are not.

Each key can alternatively be supplied with a HONGKONG_ environment prefix, e.g.
HONGKONG_FLASK_SECRET_KEY, HONGKONG_ADMIN_USERNAME, HONGKONG_ADMIN_PASSWORD_HASH,
HONGKONG_ANNOTATOR_PASSWORD_HASH, HONGKONG_GROQ_QWEN_API_KEY,
HONGKONG_GROQ_GPT_OSS_API_KEY, HONGKONG_OPENROUTER_LLAMA_API_KEY,
HONGKONG_OPENROUTER_DEEPSEEK_API_KEY. Environment values override the private file.
HONGKONG_GOOGLE_CREDS_PATH optionally selects a private service-account file.

## Dedicated Google Sheet

Create a new spreadsheet titled hongkong-cultural-hegemony-annotations. Share it as
editor with the chosen service-account email and set HONGKONG_SHEET_ID to its ID.
Never supply an existing Singapore, Mainland, India or Pilot spreadsheet ID.
The app opens the exact ID and validates its title. Initialize the new worksheets:

```bash
export HONGKONG_SHEET_ID="NEW_HONGKONG_SPREADSHEET_ID"
python annotation_app/scripts/initialize_hongkong_sheet.py
```

The helper preflights all existing target sheets, creates testing/testing2/testreview
if absent, and initializes only empty sheets. It rejects unexpected headers or
data instead of migrating another campaign's schema. Expected counts: 106/106/15.

## PythonAnywhere

Create a separate account/app for Hong Kong. Install annotation_app/requirements.txt
in its own virtualenv, set the Web Virtualenv field to its exact absolute path
(account directory names are case sensitive), and configure the new WSGI file:

```python
import os
import sys
project = "/home/YOUR_HONGKONG_USERNAME/Indian-Hegemony-Annotation"
sys.path.insert(0, project + "/annotation_app")
os.environ["HONGKONG_SHEET_ID"] = "NEW_HONGKONG_SPREADSHEET_ID"
os.environ.pop("LOCAL_DEMO", None)
from app import app as application
```

Replace both placeholders with actual Hong Kong values. Do not edit another portal's
WSGI file. Reload only the new Hong Kong Web app after configuration succeeds.

## Similarity and verification

Check Similarity searches saved Hong Kong Base prompts, excluding the current record.
It requires at least 40 characters, shows five matches at threshold 0.65, and flags
near duplicates at 0.90. It uses OpenRouter embeddings with an existing current
OpenRouter model key; optional HONGKONG_OPENROUTER_EMBEDDING_API_KEY takes precedence.
No new chat model or lexical algorithm is substituted. Empty indexes are explicit.
For existing Hong Kong records, run scripts/backfill_prompt_embeddings.py from
annotation_app/ (or use its full relative path from the repository root). It calls
the provider and writes only the private Hong Kong index; provider charges may apply.

Local checks, with mocked API responses and temporary credentials:

```bash
python -B tests/test_hongkong_schema.py
python -B tests/test_prompt_similarity.py
python -B tests/test_hongkong.py
```

Before launch, verify real API generation, service-account permissions, signup,
all eight Base/Identity outputs, five axes, draft saving, confirmation, expert
review, CSV export, guide access and a same-prompt similarity match in a new record.
Local mocked checks do not establish real provider access or online deployment.
