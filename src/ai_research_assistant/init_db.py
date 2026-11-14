
from ai_research_assistant.database import Base, engine

# Import all models so SQLAlchemy registers their tables.
from ai_research_assistant.models.paper import Paper
from ai_research_assistant.models.summary import Summary
from ai_research_assistant.models.conversation import Conversation
from ai_research_assistant.models.message import Message
from ai_research_assistant.models.paper_chunk import PaperChunk
from ai_research_assistant.models.saved_paper import SavedPaper


def initialize_database():
    Base.metadata.create_all(bind=engine)
    print("Database tables initialized successfully.")


if __name__ == "__main__":
    initialize_database()
