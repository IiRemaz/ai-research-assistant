"""Unit tests: repository constraints and business rules without network calls."""
import pytest
from ai_research_assistant.storage.paper_repository import save_new_papers, get_or_create_summary
from ai_research_assistant.storage.conversation_repository import create_conversation, save_message, get_conversation_messages
from ai_research_assistant.storage.paper_chunk_repository import save_chunks, get_chunks_by_paper
from ai_research_assistant.models.paper import Paper


def test_save_new_papers_deduplicates(session):
    payload = {'p': {'arxiv_id': '2611.99999', 'title': 'New', 'published': None, 'pdf_link': None}}
    assert save_new_papers(session, payload) == 1
    session.commit()
    assert save_new_papers(session, payload) == 0
    assert session.query(Paper).count() == 1


def test_create_conversation_requires_paper(session):
    with pytest.raises(ValueError, match='not found'):
        create_conversation(session, 1234)


def test_message_validation_and_order(session, paper):
    conv = create_conversation(session, paper.id)
    with pytest.raises(ValueError, match='Role'):
        save_message(session, conv.id, 'system', 'bad')
    with pytest.raises(ValueError, match='empty'):
        save_message(session, conv.id, 'user', '  ')
    save_message(session, conv.id, 'user', 'Question')
    save_message(session, conv.id, 'assistant', 'Answer')
    assert [m.content for m in get_conversation_messages(session, conv.id)] == ['Question', 'Answer']


def test_chunks_replace_previous_and_reject_empty(session, paper):
    assert save_chunks(session, paper.id, ['one', 'two']) == 2
    assert save_chunks(session, paper.id, ['new']) == 1
    assert [c.content for c in get_chunks_by_paper(session, paper.id)] == ['new']
    with pytest.raises(ValueError, match='empty'):
        save_chunks(session, paper.id, [''])


def test_summary_reuse_without_model_call(session, paper):
    from ai_research_assistant.models.summary import Summary
    session.add(Summary(paper_id=paper.id, content='cached', language='English', model_name='mock'))
    session.commit()
    assert get_or_create_summary(session, paper.id, 'English') == 'cached'
