
from prefect import task, flow, get_run_logger
from prefect.schedules import Cron
from ai_research_assistant.models.paper import Paper

from ai_research_assistant.rag.indexing import index_paper, get_index_path

from ai_research_assistant.collectors.arxiv_client import (
    fetch_papers,
    parse_feed,
    parse_paper,
    validate_papers,
    ns
)

from ai_research_assistant.database import SessionLocal
from ai_research_assistant.storage.paper_repository import save_new_papers


@task(retries=2, retry_delay_seconds=5)
def fetch_task():
    return fetch_papers()


@task
def parse_task(fetched_xml):
    parsed_xml = parse_feed(fetched_xml)

    entries = parsed_xml.findall(
        "atom:entry",
        namespaces=ns
    )

    parsed_papers = [
        parse_paper(entry, ns)
        for entry in entries
    ]

    return parsed_papers, len(entries)


@task
def validate_task(parsed_papers):
    return validate_papers(parsed_papers)



@task
def save_task(validated_papers):
    with SessionLocal() as session:
        try:
            # 1. Get arXiv IDs from validated papers
            arxiv_ids = [
                paper_data["arxiv_id"]
                for paper_data in validated_papers.values()
            ]

            # 2. Identify papers that already exist
            existing_ids = {
                row[0]
                for row in (
                    session.query(Paper.id)
                    .filter(Paper.arxiv_id.in_(arxiv_ids))
                    .all()
                )
            }

            # 3. Save new papers
            saved_count = save_new_papers(
                session=session,
                papers=validated_papers
            )

            session.commit()

            # 4. Retrieve IDs of all papers in this batch
            saved_paper_ids = [
                row[0]
                for row in (
                    session.query(Paper.id)
                    .filter(Paper.arxiv_id.in_(arxiv_ids))
                    .all()
                )
            ]

            # 5. Index newly inserted papers and recover missing indexes
            new_paper_ids = [
                paper_id
                for paper_id in saved_paper_ids
                if paper_id not in existing_ids or not get_index_path(paper_id).is_file()
            ]

            # 6. Index each new paper
            for paper_id in new_paper_ids:
                index_paper(
                    session=session,
                    paper_id=paper_id
                )

            return saved_count

        except Exception:
            session.rollback()
            raise


@flow(name="AI Research Assistant Pipeline")
def research_pipeline():
    logger = get_run_logger()

    fetched_xml = fetch_task()

    parsed_papers, fetched_count = parse_task(fetched_xml)

    validated_papers = validate_task(parsed_papers)

    saved_count = save_task(validated_papers)

    logger.info(f"Fetched papers: {fetched_count}")
    logger.info(f"Valid unique papers: {len(validated_papers)}")
    logger.info(f"New papers saved to database: {saved_count}")
    logger.info("Pipeline completed successfully.")


if __name__ == "__main__":
    research_pipeline.serve(
        name="ai-research-assistant-weekly",
        schedules=[
            Cron(
                "0 21 * * SAT",
                timezone="Asia/Riyadh"
            )
        ]
    )
