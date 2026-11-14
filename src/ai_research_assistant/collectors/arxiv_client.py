
import re
import xml.etree.ElementTree as ET

from datetime import datetime, timezone
from urllib.parse import urlparse

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from ai_research_assistant.config.categories import ARXIV_CATEGORIES


ARXIV_API_URL = "https://export.arxiv.org/api/query"

ARXIV_USER_AGENT = "AIResearchAssistant/1.0"

ns = {
    "atom": "http://www.w3.org/2005/Atom"
}


def create_http_session() -> requests.Session:
    retry_strategy = Retry(
        total=3,
        connect=3,
        read=3,
        status=3,
        backoff_factor=2,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=frozenset(["GET"]),
        respect_retry_after_header=True
    )

    adapter = HTTPAdapter(
        max_retries=retry_strategy
    )

    http_session = requests.Session()

    http_session.mount("https://", adapter)

    http_session.headers.update({
        "User-Agent": ARXIV_USER_AGENT
    })

    return http_session


def build_category_query() -> str:
    if not ARXIV_CATEGORIES:
        raise ValueError("No arXiv categories configured.")

    parts = [
        f"cat:{category}"
        for category in ARXIV_CATEGORIES
    ]

    return " OR ".join(parts)


def fetch_papers() -> str:
    query = build_category_query()

    params = {
        "search_query": query,
        "start": 0,
        "max_results": 10,
        "sortBy": "submittedDate",
        "sortOrder": "descending",
    }

    with create_http_session() as http_session:
        response = http_session.get(
            ARXIV_API_URL,
            params=params,
            timeout=(10, 30)
        )

        response.raise_for_status()

        if not response.text.strip():
            raise ValueError("arXiv returned an empty response.")

        return response.text


def parse_feed(xml_text: str):
    if not xml_text or not xml_text.strip():
        raise ValueError("XML response cannot be empty.")

    try:
        return ET.fromstring(xml_text)

    except ET.ParseError as error:
        raise ValueError(
            "Could not parse the arXiv XML response."
        ) from error


def clean_text(text: str) -> str:
    if not text:
        return ""

    return re.sub(r"\s+", " ", text).strip()


def is_valid_arxiv_pdf_url(url: str) -> bool:
    if not url:
        return False

    parsed_url = urlparse(url)

    return (
        parsed_url.scheme == "https"
        and parsed_url.hostname == "arxiv.org"
    )


def parse_paper(entry, ns):
    title = clean_text(
        entry.findtext(
            "atom:title",
            namespaces=ns
        )
    )

    raw_id = entry.findtext(
        "atom:id",
        namespaces=ns
    )

    published_text = entry.findtext(
        "atom:published",
        namespaces=ns
    )

    arxiv_id = None

    if raw_id and "/abs/" in raw_id:
        arxiv_id = (
            raw_id.split("/abs/")[-1]
            .split("v")[0]
        )

    published = None

    if published_text:
        try:
            parsed_date = datetime.fromisoformat(
                published_text.replace("Z", "+00:00")
            )

            if parsed_date.tzinfo is None:
                parsed_date = parsed_date.replace(
                    tzinfo=timezone.utc
                )

            published = (
                parsed_date
                .astimezone(timezone.utc)
                .replace(tzinfo=None)
            )

        except ValueError:
            published = None

    pdf_element = entry.find(
        "atom:link[@type='application/pdf']",
        namespaces=ns
    )

    pdf_link = (
        pdf_element.get("href")
        if pdf_element is not None
        else None
    )

    if not pdf_link:
        alternate_element = entry.find(
            "atom:link[@rel='alternate']",
            namespaces=ns
        )

        if alternate_element is not None:
            href = alternate_element.get("href")

            if href and "/abs/" in href:
                pdf_link = (
                    href.replace("/abs/", "/pdf/")
                    + ".pdf"
                )

    if not is_valid_arxiv_pdf_url(pdf_link):
        pdf_link = None

    return {
        "title": title,
        "arxiv_id": arxiv_id,
        "published": published,
        "pdf_link": pdf_link,
    }


def validate_papers(papers: list[dict]) -> dict:
    valid_papers = {}

    required_fields = [
        "title",
        "arxiv_id",
        "published",
        "pdf_link",
    ]

    for paper in papers:
        if not all(
            paper.get(field)
            for field in required_fields
        ):
            continue

        if paper["arxiv_id"] in valid_papers:
            continue

        valid_papers[paper["arxiv_id"]] = paper

    return valid_papers


if __name__ == "__main__":
    xml_text = fetch_papers()

    xml_root = parse_feed(xml_text)

    stored_papers = []

    for entry in xml_root.findall(
        "atom:entry",
        namespaces=ns
    ):
        paper = parse_paper(entry, ns)
        stored_papers.append(paper)

    valid_papers = validate_papers(stored_papers)

    print(f"Fetched {len(stored_papers)} papers.")
    print(f"Valid unique papers: {len(valid_papers)}")

    for paper in valid_papers.values():
        print(
            f"- [{paper['arxiv_id']}] {paper['title']}"
        )
