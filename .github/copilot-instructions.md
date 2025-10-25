<!--
Project-specific instructions for AI coding agents. Keep this file concise (20-50 lines).
Update by hand if runtime / env changes (e.g., LIVEKIT keys, chroma DB path).
-->
# Copilot instructions — healthcare_ai_backend

Goal: Help contributors be immediately productive by summarizing the architecture, critical workflows, and project-specific patterns.

1) Big picture
- This repository runs LiveKit-based conversational agents (see `src/agent.py`) and a small FastAPI app that launches agent workers (`src/main.py`).
- Audio/text flow: LiveKit session → STT (configured in `entrypoint`) → agent LLM (tools declared in `src/agent.py`) → tool calls (e.g., `ChromaService.query`) → TTS / response back to LiveKit.
- Vector DB / knowledge: `src/chroma/chroma_service.py` uses `chromadb.PersistentClient(path="./chroma_db")` and a collection named `health_issues`. Data is loaded from Excel via `src/chroma/generate_excel.py` and `ChromaService.excel_to_collection`.

2) How to run locally (discoverable from repo)
- Python requirement: >=3.13 (see `pyproject.toml`).
- Environment: create `.env.local` with LIVEKIT keys (README shows an example). The agent code reads `.env.local` via `dotenv.load_dotenv(".env.local")`.
- Recommended start points:
  - Run the agent CLI as shown in the README: `uv sync` then `uv run src/agent.py dev` (the repo references a `uv` command wrapper in docs).
  - Alternatively run the web API that starts background agent workers: `uvicorn src.main:app --reload` (this launches the FastAPI app, which starts the agent workers via the `lifespan` manager).

3) Key files and roles (quick map)
- `src/agent.py` — primary agent definitions, tool implementations (`@agents.function_tool`) and the `entrypoint` worker function.
- `src/main.py` — FastAPI app that launches workers programmatically (useful for local web testing and health checks).
- `src/chroma/chroma_service.py` — encapsulates chromadb client, collection creation, `excel_to_collection`, and `query` (returns list of dicts with keys `id`, `health_issue`, `symptoms`, `advice`, `distance`).
- `src/chroma/generate_excel.py` — example generator for `healthcare_data.xlsx` used to seed the DB.
- `pyproject.toml` — dependency list (chromadb, fastapi, livekit-agents, uvicorn, pandas, openpyxl, etc.).

4) Project-specific conventions & patterns
- Tools are declared with `@agents.function_tool` and used by the `Agent` subclass: follow the pattern in `src/agent.py` (tool → returns dict → agent converts fields to natural language).
- Agent orchestration is asynchronous: prefer async tool implementations and use `AgentSession`/`agents.Worker` APIs as in `entrypoint` and `src/main.py`.
- Chroma DB path is relative (`./chroma_db`) — ensure working directory is project root when running agents, or adjust to an absolute path for reproducible runs.
- Excel import expects columns: `id, health_issue, symptoms, advice`. Use `src/chroma/generate_excel.py` as an example seed.

5) Integration points & external deps to be aware of
- LiveKit (LIVEKIT_API_KEY/SECRET/URL) — set in `.env.local`.
- STT/LLM/TTS choices are configured in `AgentSession` (see `stt`, `llm`, `tts` strings in `src/agent.py`). Replace as needed with supported model IDs.
- ChromaDB persists locally by default; backups or remote hosting require changing the client init.

6) Notable, discoverable issues to watch for
- `symptom_check_api` appears defined twice in `src/agent.py` — this shadowing can cause unexpected behavior; prefer the second definition (it returns a list-style result) or refactor to a single function.
- The repository relies on a CLI wrapper referenced in README (`uv`) which may come from a dev tool or project-specific CLI; if `uv` is missing, use `uvicorn` or run `src/main.py` directly.

7) Quick examples to copy-paste
- Seed DB: run the generator script then import:
  - `python src/chroma/generate_excel.py`  (creates `healthcare_data.xlsx`)
  - from project root: run a small script that calls `ChromaService.excel_to_collection("healthcare_data.xlsx")` or run `src/chroma/chroma_service.py` as __main__ (it has a usage example).
- Example query shape expected by `symptom_check_api`:
  - Input: `['fever','cough']`
  - Output: `[{'id': '1', 'health_issue': 'Covid', 'symptoms': 'fever, cough, tired', 'advice': 'isolate, drink water', 'distance': 0.12}, ...]`

If anything here is unclear or you want more detail (run commands, CI hooks, or a dev Dockerfile), tell me which areas to expand and I will iterate.
