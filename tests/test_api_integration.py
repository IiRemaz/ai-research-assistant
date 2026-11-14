"""Integration tests run real FastAPI routes and SQLAlchemy against disposable SQLite."""
from unittest.mock import patch
from ai_research_assistant.models.summary import Summary
from ai_research_assistant.models.saved_paper import SavedPaper
from ai_research_assistant.models.message import Message


def test_health_and_empty_library(client):
    assert client.get('/').status_code == 200
    assert client.get('/papers/').json() == []
    assert client.get('/papers/saved').json() == []
    assert client.get('/papers/summaries').json() == []


def test_paper_listing_and_not_found(client, paper):
    data = client.get('/papers/').json()
    assert len(data) == 1 and data[0]['id'] == paper.id
    assert client.get(f'/papers/{paper.id}').json()['title'] == paper.title
    assert client.get('/papers/99999').status_code == 404


def test_save_unsave_idempotency(client, session, paper):
    url = f'/papers/{paper.id}/saved'
    assert client.put(url).json() == {'saved': True}
    assert client.put(url).json() == {'saved': True}
    assert session.query(SavedPaper).count() == 1
    assert [p['id'] for p in client.get('/papers/saved').json()] == [paper.id]
    assert client.delete(url).json() == {'saved': False}
    assert client.delete(url).json() == {'saved': False}
    assert client.get('/papers/saved').json() == []
    assert client.put('/papers/99999/saved').status_code == 404


def test_summary_generation_caching_and_listing(client, session, paper):
    with patch('ai_research_assistant.storage.paper_repository.generate_content') as model:
        model.return_value.text = 'Summary generated'
        url = f'/papers/{paper.id}/summarize'
        first = client.post(url, json={'language': 'Arabic'})
        second = client.post(url, json={'language': 'Arabic'})
        assert first.status_code == second.status_code == 200
        assert first.json()['content'] == second.json()['content'] == 'Summary generated'
        assert model.call_count == 1
    assert session.query(Summary).count() == 1
    assert client.get('/papers/summaries').json()[0]['title'] == paper.title
    assert client.post(url, json={'language': 'French'}).status_code == 422
    assert client.post('/papers/99999/summarize', json={'language': 'Arabic'}).status_code == 404


def test_conversation_create_list_and_history(client, paper):
    response = client.post('/conversations/', json={'paper_id': paper.id})
    assert response.status_code == 200
    cid = response.json()['id']
    assert client.get(f'/conversations/paper/{paper.id}').json()[0]['id'] == cid
    assert client.get(f'/conversations/{cid}/messages').json() == []
    assert client.get('/conversations/99999/messages').status_code == 404
    assert client.post('/conversations/', json={'paper_id': 99999}).status_code == 404


def test_chat_roundtrip_persists_messages_and_sources(client, session, paper):
    cid = client.post('/conversations/', json={'paper_id': paper.id}).json()['id']
    chunks = [{'chunk_index': 0, 'content': 'Evidence', 'score': 0.9}]
    with patch('ai_research_assistant.services.chat_service.retrieve_relevant_chunks', return_value=chunks), \
         patch('ai_research_assistant.services.chat_service.generate_content') as model:
        model.return_value.text = 'Answer [Chunk 0]'
        response = client.post(f'/conversations/{cid}/messages', json={'paper_id': paper.id, 'question': 'What is new?'})
    assert response.status_code == 200, response.text
    assert response.json()['sources'] == chunks
    assert response.json()['answer'] == 'Answer [Chunk 0]'
    assert [m['role'] for m in client.get(f'/conversations/{cid}/messages').json()] == ['user', 'assistant']
    assert session.query(Message).count() == 2


def test_chat_validation_and_missing_index(client, paper):
    cid = client.post('/conversations/', json={'paper_id': paper.id}).json()['id']
    assert client.post(f'/conversations/{cid}/messages', json={'paper_id': paper.id, 'question': '   '}).status_code == 400
    with patch('ai_research_assistant.services.chat_service.retrieve_relevant_chunks', side_effect=FileNotFoundError):
        response = client.post(f'/conversations/{cid}/messages', json={'paper_id': paper.id, 'question': 'Explain'})
    assert response.status_code == 409


def test_index_status_and_manual_index(client, paper):
    assert client.get(f'/papers/{paper.id}/index-status').json() == {'indexed': False}
    with patch('ai_research_assistant.api.routers.papers.index_paper') as index:
        assert client.post(f'/papers/{paper.id}/index').json() == {'indexed': True}
        index.assert_called_once()
    assert client.post('/papers/99999/index').status_code == 404


def test_update_status_and_trigger(client):
    with patch('ai_research_assistant.api.routers.papers.research_pipeline') as pipeline:
        response = client.post('/papers/update')
        assert response.status_code == 202
        pipeline.assert_called_once()
    status = client.get('/papers/update/status').json()
    assert status == {'running': False, 'error': None}
