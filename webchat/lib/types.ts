export type ChatRole = "user" | "assistant";

export type ChatMessage = {
  role: ChatRole;
  content: string;
};

export type ChatRequest = {
  studentId: string;
  className: string;
  topic: string;
  profile?: string;
  message: string;
  history?: ChatMessage[];
  notes?: string;
  satisfaction?: number;
  difficulty?: number;
  gpsTruth?: "G" | "P" | "S" | "";
  stream?: boolean;
};

export type ChatResponse = {
  ok: boolean;
  reply?: string;
  error?: string;
  messageId?: string;
  logged?: boolean;
  logError?: string;
};
