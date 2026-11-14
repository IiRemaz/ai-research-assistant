from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from threading import Lock
from ai_research_assistant.models.saved_paper import SavedPaper
from ai_research_assistant.models.paper import Paper
from ai_research_assistant.models.summary import Summary
from ai_research_assistant.rag.indexing import get_index_path, index_paper

from ai_research_assistant.database import get_db
from ai_research_assistant.run_pipeline import research_pipeline
from ai_research_assistant.storage.paper_repository import (
    get_all_papers,
    get_paper_by_id,
    get_or_create_summary,
)

from ai_research_assistant.api.schemas.paper import PaperResponse
from ai_research_assistant.api.schemas.summary import (
    SummaryRequest,
    SummaryResponse,
)


router = APIRouter(
    prefix="/papers",
    tags=["Papers"]
)


@router.get("/", response_model=list[PaperResponse])
def list_papers(db: Session = Depends(get_db)):

    papers = get_all_papers(session=db)

    return papers


# Only one update can run at a time in this local, single-worker application.
_update_lock = Lock()
_update_state = {"running": False, "error": None}


def _run_update():
    try:
        research_pipeline()
    except Exception as exc:
        _update_state["error"] = str(exc)
    finally:
        _update_state["running"] = False
        _update_lock.release()


@router.post("/update", status_code=202)
def update_papers(background_tasks: BackgroundTasks):
    if not _update_lock.acquire(blocking=False):
        raise HTTPException(409, "An update is already running.")
    _update_state.update(running=True, error=None)
    background_tasks.add_task(_run_update)
    return {"running": True}


@router.get("/update/status")
def get_update_status():
    return dict(_update_state)


@router.get("/saved", response_model=list[PaperResponse])
def saved_papers(db: Session = Depends(get_db)):
    return (db.query(Paper).join(SavedPaper, SavedPaper.paper_id == Paper.id)
            .order_by(SavedPaper.created_at.desc()).all())


@router.put("/{paper_id}/saved")
def save_paper(paper_id: int, db: Session = Depends(get_db)):
    if db.get(Paper, paper_id) is None:
        raise HTTPException(404, "Paper not found.")
    if db.query(SavedPaper).filter_by(paper_id=paper_id).first() is None:
        db.add(SavedPaper(paper_id=paper_id))
        try:
            db.commit()
        except IntegrityError:
            db.rollback()
    return {"saved": True}


@router.delete("/{paper_id}/saved")
def unsave_paper(paper_id: int, db: Session = Depends(get_db)):
    if db.get(Paper, paper_id) is None:
        raise HTTPException(404, "Paper not found.")
    db.query(SavedPaper).filter_by(paper_id=paper_id).delete()
    db.commit()
    return {"saved": False}


@router.get("/summaries")
def list_summaries(db: Session = Depends(get_db)):
    rows = (db.query(Summary, Paper.title).join(Paper, Paper.id == Summary.paper_id)
            .order_by(Summary.id.desc()).all())
    return [{"id": summary.id, "paper_id": summary.paper_id,
             "title": title, "content": summary.content,
             "language": summary.language, "model_name": summary.model_name}
            for summary, title in rows]


@router.get("/{paper_id}/index-status")
def paper_index_status(paper_id: int, db: Session = Depends(get_db)):
    if db.get(Paper, paper_id) is None:
        raise HTTPException(404, "Paper not found.")
    return {"indexed": get_index_path(paper_id).is_file()}


@router.post("/{paper_id}/index")
def index_selected_paper(paper_id: int, db: Session = Depends(get_db)):
    if db.get(Paper, paper_id) is None:
        raise HTTPException(404, "Paper not found.")
    try:
        index_paper(session=db, paper_id=paper_id)
    except ValueError as exc:
        db.rollback()
        raise HTTPException(400, str(exc)) from exc
    except Exception as exc:
        db.rollback()
        raise HTTPException(503, "Indexing failed; check server logs.") from exc
    return {"indexed": True}


@router.get("/{paper_id}", response_model=PaperResponse)
def get_paper(
    paper_id: int,
    db: Session = Depends(get_db)
):
    paper = get_paper_by_id(
        session=db,
        paper_id=paper_id
    )

    if paper is None:
        raise HTTPException(
            status_code=404,
            detail="Paper not found."
        )

    return paper


@router.post(
    "/{paper_id}/summarize",
    response_model=SummaryResponse
)
def summarize_paper(
    paper_id: int,
    request: SummaryRequest,
    db: Session = Depends(get_db)
):
    paper = get_paper_by_id(
        session=db,
        paper_id=paper_id
    )

    if paper is None:
        raise HTTPException(
            status_code=404,
            detail="Paper not found."
        )

    try:
        content = get_or_create_summary(
            session=db,
            paper_id=paper_id,
            language=request.language
        )

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error)
        )

    except RuntimeError:
        raise HTTPException(
            status_code=503,
            detail=(
                "The summarization service is temporarily "
                "unavailable. Please try again later."
            )
        )

    return SummaryResponse(
        paper_id=paper_id,
        content=content,
        language=request.language
    )