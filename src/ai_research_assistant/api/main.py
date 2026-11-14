
from fastapi import FastAPI
from contextlib import asynccontextmanager
from ai_research_assistant.database import Base, engine
from ai_research_assistant.models.saved_paper import SavedPaper
from fastapi.middleware.cors import CORSMiddleware
from ai_research_assistant.api.routers import papers, chat


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create new optional feature tables without modifying existing tables.
    Base.metadata.create_all(bind=engine, tables=[SavedPaper.__table__])
    yield

app = FastAPI(
    lifespan=lifespan,
    title="AI Research Assistant",
    description="An API for collecting, analyzing, and querying AI research papers.",
    version="1.0.0"
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {
        "message": "AI Research Assistant API is running"
    }


app.include_router(papers.router)
app.include_router(chat.router)
