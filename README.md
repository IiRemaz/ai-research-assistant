# AI Research Assistant — integrated version

This version preserves the original Python/RAG backend and React UI and adds connected saved papers, summaries, chat, indexing and background updates.

## Setup (Windows PowerShell)

From the project root, activate your existing Python environment and install the original project dependencies (`pip install -e .` if your original `pyproject.toml` is present). This delivery includes the source and frontend but **does not include your secret `.env`, virtual environment, or the original populated SQLite database**.

Set `GEMINI_API_KEY` in a private `.env` in the project root. Optionally set `GEMINI_MODEL`.

Initialize the database:

```powershell
python -m ai_research_assistant.init_db
```

Start backend:

```powershell
python -m uvicorn ai_research_assistant.api.main:app --reload
```

Start frontend in another terminal:

```powershell
cd frontend
npm install
npm run dev
```

Open http://localhost:5173. API docs: http://127.0.0.1:8000/docs.

To use a different API host, create `frontend/.env.local` containing `VITE_API_BASE_URL=http://127.0.0.1:8000`.

## Notes

- The delivered archive intentionally excludes node_modules, Python bytecode, credentials, Git history, and large datasets.
- To retain your **51 existing papers**, copy your existing `data/research.db` into this project's `data/` folder before starting the backend. Back it up first.
- The new `saved_papers` table is created on API startup; existing tables are not dropped.
- Chat requires a FAISS index for each paper. The chat page provides an **Index this paper** action if missing. This may take time and download PDFs/models.
- `Update Papers` runs the Prefect pipeline in a FastAPI background task, with polling for completion. For production, use a dedicated worker/queue instead.
- Saved papers are global to this local installation (no authentication).
- Full PDF summaries can exceed model context limits; production deployment should implement chunked/hierarchical summarization.
- Only source-level checks/build checks are performed here; end-to-end network/Gemini operations require local credentials and runtime.

## Automated tests

Backend unit and API integration tests run without API keys, network, or a GPU:

```powershell
python -m pip install -e ".[dev]"
python -m pytest -q tests
python -m pytest --cov=ai_research_assistant --cov-report=term-missing tests
```

Browser UI end-to-end scenarios use Playwright with mocked HTTP responses. They exercise the real React UI and browser navigation but **do not** verify a live Gemini/arXiv service:

```powershell
cd frontend
npm install
npx playwright install chromium
npm run test:e2e
```

To validate the real deployed stack, start FastAPI and Vite, configure `.env` with your own Gemini key, and manually check collection, PDF extraction, embedding downloads, FAISS indexing, summarization, and chat. These require external resources and are not covered by the offline test suite. Use a fresh database; do not copy the previous `data/research.db`.
