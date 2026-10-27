# Taiwan Cultural Hegemony Annotation Portal

Independent Taiwan portal based on the Singapore portal workflow. Use the
`taiwan-zone-portal` branch with a dedicated deployment, credentials and Sheet.

- Five axes: social, economic, gender, linguistic, ethnic.
- No subzones or region/state columns in Sheets and CSV exports.
- Four LLMs, blinded Model 1–4 presentation and separate Base/Identity outputs.
- Draft saving, confirmation, expert review, IAA storage and Check Similarity.
- Taiwan-only account, data, draft, review, notes and similarity storage.
- 106 annotation columns; model prefixes: qwen, gpt_oss, llama, deepseek.

[Taiwan axes and guidelines](https://docs.google.com/document/d/12NAq50EGfsqa4CFQ0wyQ4Q47NRfAp6H1-qw0mYvQXN8/edit?tab=t.rojo4iiwribr)

See [TAIWAN_DEPLOYMENT.md](TAIWAN_DEPLOYMENT.md) for setup and verification. Existing
Mainland, Singapore, India and Pilot deployments/data are not migrated into Taiwan.
Never commit or share API keys, service-account JSON files or login credentials.
