import axios from 'axios';

const api = axios.create({ baseURL: import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000', timeout: 180000 });
export interface Paper { id: number; arxiv_id: string; title: string; published: string | null; pdf_link: string | null; received_at: string | null }
export interface Summary { id: number; paper_id: number; title: string; content: string; language: string; model_name: string }
export interface Conversation { id: number; paper_id: number; title: string | null; created_at: string; updated_at: string }
export interface Message { id: number; conversation_id: number; role: 'user' | 'assistant'; content: string; created_at: string }
export interface Source { chunk_index: number; content: string; score: number }
export interface ChatAnswer { conversation_id: number; paper_id: number; answer: string; sources: Source[] }
export const getPapers = async () => (await api.get<Paper[]>('/papers/')).data;
export const getSaved = async () => (await api.get<Paper[]>('/papers/saved')).data;
export const savePaper = async (id: number) => (await api.put(`/papers/${id}/saved`)).data;
export const unsavePaper = async (id: number) => (await api.delete(`/papers/${id}/saved`)).data;
export const getSummaries = async () => (await api.get<Summary[]>('/papers/summaries')).data;
export const summarize = async (id: number, language: 'Arabic' | 'English') => (await api.post<{paper_id:number;content:string;language:string}>(`/papers/${id}/summarize`, { language })).data;
export const startUpdate = async () => (await api.post('/papers/update')).data;
export const updateStatus = async () => (await api.get<{running:boolean;error:string|null}>('/papers/update/status')).data;
export const indexStatus = async (id: number) => (await api.get<{indexed:boolean}>(`/papers/${id}/index-status`)).data;
export const indexPaper = async (id: number) => (await api.post(`/papers/${id}/index`)).data;
export const getConversations = async (id: number) => (await api.get<Conversation[]>(`/conversations/paper/${id}`)).data;
export const createConversation = async (paper_id: number) => (await api.post<Conversation>('/conversations/', {paper_id})).data;
export const getMessages = async (id: number) => (await api.get<Message[]>(`/conversations/${id}/messages`)).data;
export const askPaper = async (conversationId: number, paper_id: number, question: string) => (await api.post<ChatAnswer>(`/conversations/${conversationId}/messages`, {paper_id, question})).data;
export const errorText = (err: unknown) => axios.isAxiosError(err) ? (typeof err.response?.data?.detail === 'string' ? err.response.data.detail : err.message) : err instanceof Error ? err.message : 'Something went wrong.';
