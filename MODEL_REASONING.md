# Model reasoning configuration

The four regional branches share these generation settings (checked 2026-10-30):

| Model | Provider | Explicit reasoning setting |
| --- | --- | --- |
| Qwen 3.8 27B | Groq | `reasoning_effort="medium"` |
| GPT-OSS 120B | Groq | `reasoning_effort="medium"` |
| Llama 4 Maverick | OpenRouter | `reasoning={"enabled": true}` sent for request consistency; unsupported by model |
| DeepSeek V3.2 | OpenRouter | `reasoning={"enabled": true}` |

Groq uses `include_reasoning=false` to omit reasoning text from the response;
this does not disable reasoning. Both provider adapters return only final answer
content to the annotation interface. The system prompt remains
`Answer in no more than 150 words in English.` Temperature and output token
limits remain unspecified. Reasoning effort settings across different models
do not imply equal reasoning compute or token budgets.

Llama 4 Maverick's OpenRouter model catalog does not list `reasoning` among its
supported parameters. We send the enabled flag at the study owner's request for
request consistency, but it may be ignored and does not establish that reasoning
was activated. Live acceptance of the flag has not been verified. We do not
silently retry without the flag. Replacing this study model requires a separate
decision.

References:
- https://console.groq.com/docs/reasoning
- https://openrouter.ai/api/v1/models
- https://openrouter.ai/docs/guides/best-practices/reasoning-tokens

Tests mock provider responses; they verify request configuration and answer
extraction, not live provider behavior. Deployments must pull the relevant commit
and reload before these settings apply online. Earlier annotations are unchanged.
