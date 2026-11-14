from sqlalchemy import Column, Integer, ForeignKey, DateTime, UniqueConstraint
from ai_research_assistant.database import Base, utc_now

class SavedPaper(Base):
    __tablename__ = "saved_papers"
    id = Column(Integer, primary_key=True)
    paper_id = Column(Integer, ForeignKey("papers.id", ondelete="CASCADE"), nullable=False)
    created_at = Column(DateTime, default=utc_now, nullable=False)
    __table_args__ = (UniqueConstraint("paper_id", name="uq_saved_paper"),)
