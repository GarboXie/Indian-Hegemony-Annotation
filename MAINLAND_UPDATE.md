# Mainland China: similarity and annotation guidelines

Deploy only the chinese-zone-portal branch to the existing Mainland application.
This update does not change config.py, the four generation models, six axes,
Google Sheet name/headers, JSONL annotation storage, accounts or Pilot records.
The Singapore branch and deployment are unchanged.

Annotation Guidelines now opens:
https://docs.google.com/document/d/17EtWI0OkBxWrDFY1UxTHaMIC1Hh9qsSeblP3D2n6Qys/edit?tab=t.0
Document sharing permissions must allow the intended annotators to view it.
Inter-Annotator Review Guidelines is a separate link and remains unchanged.

## Similarity

Check Similarity compares saved Base prompts within the selected province/area,
excludes the record currently being edited, and shows up to five semantic matches.
Existing thresholds remain 0.65 (match), 0.90 (near duplicate) and 40 characters
(minimum input). Empty candidate indexes are explicitly reported, not treated as
a successful no-match check. Unchanged saved prompts reuse their embeddings.

The private index is annotation_app/data/mainland/prompt_embeddings.json,
resolved from the app location independently of the server working directory.
Old shared/relative indexes are neither imported nor overwritten; backfill the
new index from the Mainland sheet instead. Saving annotations updates this index.

Embedding model and endpoint remain unchanged:
sentence-transformers/all-minilm-l6-v2 via https://openrouter.ai/api/v1/embeddings.
The existing private accounts/apikeys.json supplies credentials in priority order:
OPENROUTER_EMBEDDING_API_KEY, OPENROUTER_LLAMA_API_KEY, OPENROUTER_DEEPSEEK_API_KEY,
then legacy OPENAI_API_KEY (formerly used for OpenRouter). No extra key is necessary if
an existing configured OpenRouter key permits embeddings. Model-restricted keys
or insufficient credits require correction in private server settings. Never print
or commit keys. Provider errors do not expose response bodies or credentials.

## Update sequence

1. In the Mainland PythonAnywhere Bash console, activate its existing virtualenv
   and enter its existing repository directory. Check the branch before pulling:
   `git branch --show-current`, then `git pull --ff-only origin chinese-zone-portal`.
   If local changes block updating, inspect them rather than resetting files.
2. Run `python -B tests/test_mainland_similarity.py`. Tests use fake credentials
   and mocked API responses; no private files, Google Sheets or paid API calls.
3. Run `python annotation_app/scripts/backfill_prompt_embeddings.py` to populate
   the Mainland-only index. This reads the existing sheet without writing any
   sheet cells. It calls OpenRouter for missing/changed vectors and consumes
   provider credits; keep the Added/Skipped/Failed summary. Failed items exit
   nonzero and should be investigated before relying on similarity results.
4. Reload only the Mainland Web app, then check the new guide link. Save a test
   prompt and compare an identical prompt in a new annotation in the same province
   to verify the real provider connection. Avoid editing the same record for this
   duplicate test, since the current record is excluded.

Deploying and live-provider verification remain separate from GitHub updates.
