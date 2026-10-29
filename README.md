# Hong Kong Cultural Hegemony Annotation Portal

Independent Hong Kong portal based on the Taiwan portal workflow. Use the
`hongkong-zone-portal` branch with a dedicated deployment, credentials and Sheet.

- Five axes: social, economic, gender, linguistic, ethnic.
- No subzones or region/state columns in Sheets and CSV exports.
- Four LLMs, blinded Model 1–4 presentation and separate Base/Identity outputs.
- Draft saving, confirmation, expert review, IAA storage and Check Similarity.
- Hong Kong-only account, data, draft, review, notes and similarity storage.
- 106 annotation columns; model prefixes: qwen, gpt_oss, llama, deepseek.

[Hong Kong axes and guidelines](https://docs.google.com/document/d/12NAq50EGfsqa4CFQ0wyQ4Q47NRfAp6H1-qw0mYvQXN8/edit?tab=t.0)

See [HONGKONG_DEPLOYMENT.md](HONGKONG_DEPLOYMENT.md) for setup and verification. Existing
Mainland, Singapore, Taiwan, India and Pilot deployments/data are not migrated into Hong Kong.
Never commit or share API keys, service-account JSON files or login credentials.
