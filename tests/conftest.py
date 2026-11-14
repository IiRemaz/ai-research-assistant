"""Isolated test environment: no network, GPU, Gemini key, or Prefect server."""
import sys
import types
from pathlib import Path
from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

# Keep optional heavy integrations out of isolated API tests. The real API and
# repositories are imported and exercised; external boundaries are mocked.
for module_name, attributes in {
    "ai_research_assistant.run_pipeline": {"research_pipeline": lambda: None},
    "ai_research_assistant.rag.indexing": {
        "get_index_path": lambda paper_id: ROOT / "data" / "vector_indexes" / f"paper_{paper_id}.index",
        "index_paper": lambda session, paper_id: None,
    },
    "ai_research_assistant.rag.retrieval": {"retrieve_relevant_chunks": lambda **kwargs: []},
    "ai_research_assistant.rag.prompt_builder": {"build_chat_prompt": lambda *args: "prompt"},
    "ai_research_assistant.model_client": {"generate_content": lambda prompt: types.SimpleNamespace(text="Mock answer")},
    "ai_research_assistant.pdf_extractor": {
        "download_pdf": lambda url: b"pdf", "extract_text": lambda data: "paper text"},
}.items():
    mod = types.ModuleType(module_name)
    for name, value in attributes.items():
        setattr(mod, name, value)
    sys.modules[module_name] = mod

from ai_research_assistant.database import Base, get_db  # noqa: E402
from ai_research_assistant.models.paper import Paper  # noqa: E402
from ai_research_assistant.models.summary import Summary  # noqa: E402
from ai_research_assistant.models.paper_chunk import PaperChunk  # noqa: E402
from ai_research_assistant.models.conversation import Conversation  # noqa: E402
from ai_research_assistant.models.message import Message  # noqa: E402
from ai_research_assistant.models.saved_paper import SavedPaper  # noqa: E402
from ai_research_assistant.api.main import app  # noqa: E402


@pytest.fixture
def session():
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine, expire_on_commit=False)
    with Session() as db:
        yield db
    engine.dispose()


@pytest.fixture
def client(session):
    def override_db():
        yield session
    app.dependency_overrides[get_db] = override_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def paper(session):
    item = Paper(arxiv_id="2611.12345", title="Research Test Paper", pdf_link="https://arxiv.org/pdf/2611.12345", full_text="Test content")
    session.add(item)
    session.commit()
    return item
