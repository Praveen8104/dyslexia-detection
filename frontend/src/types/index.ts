export interface User {
  id: number;
  name: string;
  age: number;
  gender?: string;
  parent_email?: string;
  created_at: string;
}

export interface HandwritingResult {
  id: number;
  prediction: string;
  confidence: number;
  markers: string[];
  risk_score: number;
}

export interface SpeechResult {
  id: number;
  prediction: string;
  confidence: number;
  reading_speed_wpm: number;
  hesitation_count: number;
  silence_ratio: number;
  risk_score: number;
}

export interface CombinedResult {
  session_id: number;
  combined_score: number;
  risk_level: string;
  recommendation: string;
  disclaimer: string;
}

export interface TestSession {
  id: number;
  user_id: number;
  combined_score: number | null;
  risk_level: string | null;
  created_at: string;
  handwriting_tests: HandwritingTestRecord[];
  speech_tests: SpeechTestRecord[];
  user_name?: string;
  user_age?: number | null;
}

export interface HandwritingTestRecord {
  id: number;
  session_id: number;
  image_path: string;
  prediction: string;
  confidence: number;
  markers: string;
  created_at: string;
}

export interface SpeechTestRecord {
  id: number;
  session_id: number;
  audio_path: string;
  transcript: string | null;
  expected_text: string;
  prediction: string;
  confidence: number;
  reading_speed_wpm: number;
  hesitation_count: number;
  silence_ratio: number;
  created_at: string;
}

export interface CreateUserPayload {
  name: string;
  age: number;
  gender?: string;
  parent_email?: string;
}
