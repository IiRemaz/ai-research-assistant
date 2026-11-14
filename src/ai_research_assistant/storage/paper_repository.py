
from datetime import date, datetime, time, timedelta, timezone
from zoneinfo import ZoneInfo

from sqlalchemy.orm import Session

from ai_research_assistant.database import utc_now
from ai_research_assistant.models.paper import Paper
from ai_research_assistant.models.summary import Summary
from ai_research_assistant.model_client import generate_content
from ai_research_assistant.pdf_extractor import download_pdf, extract_text


MODEL_NAME = "gemini-3.1-flash-lite"

RIYADH_TIMEZONE = ZoneInfo("Asia/Riyadh")


def save_new_papers(
    session: Session,
    papers: dict
) -> int:

    saved_count = 0

    for paper_data in papers.values():
        existing_paper = (
            session.query(Paper)
            .filter_by(arxiv_id=paper_data["arxiv_id"])
            .first()
        )

        if existing_paper:
            continue

        new_paper = Paper(
            arxiv_id=paper_data["arxiv_id"],
            title=paper_data["title"],
            published=paper_data["published"],
            pdf_link=paper_data["pdf_link"],
            received_at=utc_now()
        )

        session.add(new_paper)
        saved_count += 1

    session.flush()

    return saved_count


def get_all_papers(session: Session) -> list[Paper]:

    return (
        session.query(Paper)
        .order_by(Paper.published.desc())
        .all()
    )


def get_papers_by_received_date(
    session: Session,
    selected_date: date
) -> list[Paper]:

    start_local = datetime.combine(
        selected_date,
        time.min,
        tzinfo=RIYADH_TIMEZONE
    )

    next_day_local = start_local + timedelta(days=1)

    start_utc = (
        start_local
        .astimezone(timezone.utc)
        .replace(tzinfo=None)
    )

    next_day_utc = (
        next_day_local
        .astimezone(timezone.utc)
        .replace(tzinfo=None)
    )

    return (
        session.query(Paper)
        .filter(
            Paper.received_at >= start_utc,
            Paper.received_at < next_day_utc
        )
        .all()
    )


def get_saved_summary(
    session: Session,
    paper_id: int,
    language: str
) -> str | None:

    summary = (
        session.query(Summary)
        .filter_by(
            paper_id=paper_id,
            language=language
        )
        .first()
    )

    return summary.content if summary else None


def save_summary(
    session: Session,
    paper_id: int,
    content: str,
    language: str,
    model_name: str
) -> Summary:

    if not content or not content.strip():
        raise ValueError("Summary content cannot be empty.")

    summary = Summary(
        paper_id=paper_id,
        content=content,
        language=language,
        model_name=model_name
    )

    session.add(summary)
    session.flush()
    session.commit()


    return summary


def get_paper_by_id(
    session: Session,
    paper_id: int
) -> Paper | None:

    return (
        session.query(Paper)
        .filter_by(id=paper_id)
        .first()
    )


def get_or_create_summary(
    session: Session,
    paper_id: int,
    language: str
) -> str:

    saved_summary = get_saved_summary(
        session=session,
        paper_id=paper_id,
        language=language
    )

    if saved_summary:
        return saved_summary

    paper_text = get_or_extract_paper_text(
        session=session,
        paper_id=paper_id
    )

    new_summary_content = generate_summary(
        paper_text=paper_text,
        language=language
    )

    save_summary(
        session=session,
        paper_id=paper_id,
        content=new_summary_content,
        language=language,
        model_name=MODEL_NAME
    )

    return new_summary_content


def generate_summary(
    paper_text: str,
    language: str
) -> str:

    if not paper_text or not paper_text.strip():
        raise ValueError("Paper text cannot be empty.")

    prompt = f"""
    Summarize the following research paper in {language}.

    Include:
    - Research problem
    - Proposed method
    - Main findings
    - Limitations

    Paper:
    {paper_text}
    """

    response = generate_content(prompt)

    if response is None or not response.text:
        raise RuntimeError("The model returned an empty summary.")

    return response.text


def get_or_extract_paper_text(
    session: Session,
    paper_id: int
) -> str:

    paper = get_paper_by_id(
        session=session,
        paper_id=paper_id
    )

    if paper is None:
        raise ValueError(
            f"Paper with ID {paper_id} was not found."
        )

    if paper.full_text and paper.full_text.strip():
        return paper.full_text

    if not paper.pdf_link:
        raise ValueError(
            f"Paper with ID {paper_id} has no PDF link."
        )

    pdf_file = download_pdf(paper.pdf_link)

    paper_text = extract_text(pdf_file)

    if not paper_text or not paper_text.strip():
        raise ValueError(
            "Could not extract text from the PDF."
        )

    paper.full_text = paper_text

    session.flush()

    return paper_text
