/** Browser E2E with mocked HTTP boundaries: no Gemini key or external network needed. */
import { test, expect } from '@playwright/test';

const paper = { id: 1, arxiv_id: '2611.12345', title: 'A Test Research Paper', published: '2026-11-01T00:00:00', pdf_link: 'https://arxiv.org/pdf/2611.12345', received_at: '2026-11-01T00:00:00' };

test.beforeEach(async ({ page }) => {
  let saved = false;
  let summaryGenerated = false;
  await page.route('http://127.0.0.1:8000/**', async route => {
    const url = new URL(route.request().url());
    const method = route.request().method();
    const path = url.pathname;
    const json = (body: unknown, status = 200) => route.fulfill({ status, contentType: 'application/json', body: JSON.stringify(body) });
    if (path === '/papers/' && method === 'GET') return json([paper]);
    if (path === '/papers/saved' && method === 'GET') return json(saved ? [paper] : []);
    if (path === '/papers/1/saved' && method === 'PUT') { saved = true; return json({ saved }); }
    if (path === '/papers/1/saved' && method === 'DELETE') { saved = false; return json({ saved }); }
    if (path === '/papers/summaries') return json(summaryGenerated ? [{ id: 1, paper_id: 1, title: paper.title, content: 'Structured findings', language: 'English', model_name: 'mock' }] : []);
    if (path === '/papers/1/summarize') { summaryGenerated = true; return json({ paper_id: 1, content: 'Structured findings', language: 'English' }); }
    if (path === '/papers/1/index-status') return json({ indexed: true });
    if (path === '/conversations/paper/1') return json([]);
    if (path === '/conversations/' && method === 'POST') return json({ id: 4, paper_id: 1, title: null, created_at: '2026-11-01T00:00:00', updated_at: '2026-11-01T00:00:00' });
    if (path === '/conversations/4/messages' && method === 'POST') return json({ conversation_id: 4, paper_id: 1, answer: 'Evidence-based answer', sources: [{ chunk_index: 0, content: 'Evidence', score: 0.91 }] });
    if (path === '/conversations/4/messages' && method === 'GET') return json([]);
    if (path === '/papers/update' && method === 'POST') return json({ running: true }, 202);
    if (path === '/papers/update/status') return json({ running: false, error: null });
    return json({ detail: `Unmocked route: ${method} ${path}` }, 404);
  });
});

test('research library -> save -> saved page -> unsave', async ({ page }) => {
  await page.goto('/');
  await expect(page.getByText('A Test Research Paper')).toBeVisible();
  await page.getByRole('button', { name: 'Save', exact: true }).click();
  await page.getByRole('button', { name: 'Saved Papers' }).click();
  await expect(page.getByText('A Test Research Paper')).toBeVisible();
  await page.getByRole('button', { name: 'Saved', exact: true }).click();
  await expect(page.getByText('No saved papers yet.')).toBeVisible();
});

test('research library -> summary -> summary history', async ({ page }) => {
  await page.goto('/');
  await page.getByRole('button', { name: 'Summarize' }).click();
  await page.getByRole('button', { name: 'Generate summary' }).click();
  await expect(page.getByText('Structured findings')).toBeVisible();
  await page.getByRole('button', { name: 'Close' }).click();
  await page.getByRole('button', { name: 'Summaries', exact: true }).click();
  await expect(page.getByText('Structured findings')).toBeVisible();
});

test('research library -> ask AI -> response and sources', async ({ page }) => {
  await page.goto('/');
  await page.getByRole('button', { name: 'Ask AI' }).click();
  await expect(page.getByText('RAG index ready')).toBeVisible();
  await page.getByRole('textbox', { name: 'Ask about this paper' }).fill('What did they find?');
  await page.locator('.chat-compose button[type=submit]').click();
  await expect(page.getByText('Evidence-based answer')).toBeVisible();
  await expect(page.getByText('Sources used (1)')).toBeVisible();
});
