import axios from 'axios';
import type {
  User,
  CreateUserPayload,
  HandwritingResult,
  SpeechResult,
  CombinedResult,
  TestSession,
} from '../types';

const api = axios.create({
  baseURL: '/api',
});

// Users
export async function createUser(data: CreateUserPayload): Promise<{ user: User; session_id: number }> {
  const res = await api.post('/users', data);
  return res.data;
}

export async function getUser(userId: number): Promise<User> {
  const res = await api.get(`/users/${userId}`);
  return res.data;
}

export async function listUsers(): Promise<User[]> {
  const res = await api.get('/users');
  return res.data;
}

// Handwriting
export async function analyzeHandwriting(
  sessionId: number,
  imageFile: File,
): Promise<HandwritingResult> {
  const formData = new FormData();
  formData.append('image', imageFile);
  formData.append('session_id', String(sessionId));
  const res = await api.post('/handwriting/analyze', formData);
  return res.data;
}

// Speech
export async function analyzeSpeech(
  sessionId: number,
  audioBlob: Blob,
  expectedText: string,
): Promise<SpeechResult> {
  const formData = new FormData();
  formData.append('audio', audioBlob, 'recording.wav');
  formData.append('session_id', String(sessionId));
  formData.append('expected_text', expectedText);
  const res = await api.post('/speech/analyze', formData);
  return res.data;
}

// Results
export async function combineResults(
  sessionId: number,
  handwritingScore: number | null,
  speechScore: number | null,
): Promise<CombinedResult> {
  const res = await api.post('/results/combine', {
    session_id: sessionId,
    handwriting_score: handwritingScore,
    speech_score: speechScore,
  });
  return res.data;
}

export async function getResults(sessionId: number): Promise<TestSession> {
  const res = await api.get(`/results/${sessionId}`);
  return res.data;
}

export async function getHistory(userId: number): Promise<TestSession[]> {
  const res = await api.get(`/results/history/${userId}`);
  return res.data;
}
