# ConfigMaster HPS - Project Context

## What was done (2026-03-16)
Adapted the entire AI agent to match supervisor's specs (ParamCorrectif.docx.pdf + Questions.docx.pdf):
- **52 exact questions** in supervisor's order
- **DB types** matched exactly (CHAR, VARCHAR2, NUMBER sizes)
- All pushed to `master`

## Modified files (all in `nv-ai-agent-hps/agents/`)
- `schema_validator.py` — regex patterns match DB types (BIN 6-11, BANK_CODE CHAR(6), PLASTIC_TYPE {STD,EMB,VIR})
- `validation_agent.py` — CUSTOM_QUESTIONS for 52 questions, updated MENU_FIELDS
- `brain.py` — QUESTION_ORDER (54 paths), 6 GROUPS, enforced ordering
- `conversation_agent.py` — field normalization (printed→STD, embossed→EMB, virtual→VIR)
- `bank_pipeline.py` — payload mappings (RENEWAL_MAP, billing_evt 1/2/3, billing_period M/A/T/S)
- `api.py` — hardened list_goals with try/except for corrupted entries

## Active Bug
Past configurations not showing in sidebar ("No configurations yet") even though API returns goals.
Possible causes: frontend API URL/port mismatch, CORS, or goals/index.json format mismatch.

## How to start services
1. **Frontend**: `cd Frontend/ConfigMasterHPS-main && npm start` (port 3000)
2. **Backend**: `cd SIT/ConfigMaster-Backend && mvn spring-boot:run` (port 8080)
3. **FastAPI**: `cd nv-ai-agent-hps && python api.py` (port 8000)

## Repo
GitHub: anasxxx/config-master | Branch: master
