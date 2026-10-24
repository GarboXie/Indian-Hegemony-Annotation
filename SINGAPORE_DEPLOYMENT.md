# Singapore portal deployment

Deploy the `singapore-zone-portal` branch in a separate checkout and web application.
Do not reload or repoint the Mainland China application. Never copy Pilot annotations,
registered accounts, review assignments, databases or drafts into this deployment.

## Persistent storage

Set `SINGAPORE_DATA_ROOT` to a dedicated persistent directory. All runtime data is
stored under its `singapore/` child: annotations.jsonl, annotators.json, drafts/,
notes/, iaa_reviews.db, prompt_embeddings.json and review assignments. The default
is annotation_app/data/singapore/. Keep it outside the public static directory.
The cookie name is singapore_portal_session; use a new session signing key.

## Private settings

Configure these in the server environment (never commit actual values):

- SINGAPORE_FLASK_SECRET_KEY (new random value)
- SINGAPORE_ANNOTATOR_PASSWORD_HASH (new signup code hash)
- SINGAPORE_ADMIN_USERNAME
- SINGAPORE_ADMIN_PASSWORD_HASH (new admin password hash)
- SINGAPORE_GROQ_QWEN_API_KEY
- SINGAPORE_GROQ_GPT_OSS_API_KEY
- SINGAPORE_OPENROUTER_LLAMA_API_KEY
- SINGAPORE_OPENROUTER_DEEPSEEK_API_KEY
- SINGAPORE_OPENAI_API_KEY (OpenRouter embeddings, if enabled)
- SINGAPORE_GOOGLE_CREDS_PATH (private service-account file)
- SINGAPORE_SHEET_ID (new dedicated spreadsheet ID)

User-supplied candidate Singapore Sheet ID:
`1kGgFGzc07sFi8HG8f2h_PeiGA_Kl9E3-czbSkUOLE8M`.
Its title, worksheets and service-account permissions still require verification.

Alternatively, application keys may be stored in the ignored private file
annotation_app/accounts/singapore/apikeys.json using the original unprefixed key
names. Environment settings override the file. No legacy accounts/apikeys.json
or legacy Google credentials are loaded.

Create a new spreadsheet titled `singapore-cultural-hegemony-annotations`, with
worksheets `testing`, `testing2` and `testreview`. Share only this new spreadsheet
with the Singapore service account as editor. The app opens by ID and validates
the title before writing. Never supply the Mainland China or Pilot sheet ID.

## Launch

Install annotation_app/requirements.txt in a separate virtual environment.
Point the new web application's WSGI configuration to annotation_app/wsgi.py
and its virtual environment to that environment. Supply private settings before
importing the WSGI application. Leave LOCAL_DEMO unset in production.

For PythonAnywhere, use a separate Web app/domain and checkout directory; do not
edit the existing Mainland app's WSGI configuration. Account, domain, persistent
directory and new Sheet ID must be chosen before final deployment.

## Verification

Run `python -B tests/test_singapore.py` locally. It uses a temporary isolated
directory, generated test credentials and mocked model responses, without external
API requests or reading private credentials. It does not verify live provider
access or Google Sheets permissions. After deployment, verify those separately
and then exercise signup, eight Base/Identity outputs, draft saving, confirmation,
admin review and CSV export in the new portal.

Peer-review assignment lists start empty until Singapore annotators are onboarded.

## Model column names

Singapore Sheets and CSV exports use neutral prefixes for blinded annotation:

| Sheet prefix | Internal alias | Backend model |
| --- | --- | --- |
| model1 | gemini | qwen/qwen3.8-27b (Groq) |
| model2 | gpt | openai/gpt-oss-120b (Groq) |
| model3 | llama | meta-llama/llama-4-maverick (OpenRouter) |
| model4 | deepseek | deepseek/deepseek-v3.2 (OpenRouter) |

Legacy aliases remain in form fields, generation routes, saved drafts and JSON
records. They do not identify the actual provider model. The change preserves
all 124 column positions. The sheet helper accepts the exact previous Singapore
header layout and relabels row 1 only; unexpected layouts are rejected. Readers
accept both old and neutral prefixes. Update server code before relabeling Sheets,
then reload the new app; never manually reorder columns. Run
`python -B tests/test_sheet_columns.py` to check migration and reading compatibility.

## Free hosting choice (checked 2026-10-24)

A separate PythonAnywhere free account is a candidate for this app: each free
account has one web app, a single worker and a monthly renewal requirement.
The published allowlist currently includes api.groq.com and openrouter.ai.
Validate real API calls from the chosen account before launch. Official sources:
https://help.pythonanywhere.com/pages/FreeAccountsFeatures/
https://www.pythonanywhere.com/whitelist/

Render Free is not a direct fit for the current local-file storage: idle sleep,
restart and redeploy discard local accounts, drafts and SQLite reviews. Using it
would require an external persistent datastore for all of those, not only Sheets.
https://render.com/docs/free
