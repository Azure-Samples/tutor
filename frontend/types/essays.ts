export type Essay = {
  id?: string;
  topic: string;
  theme?: string;
  content: string;
  explanation?: string;
  file_url?: string | null;
  content_file_location?: string | null;
  assembly_id?: string | null;
};

export type EssayEvaluationResult = {
  strategy: string;
  verdict: string;
  strengths: string[];
  improvements: string[];
};

export type EssayResource = {
  id: string;
  essay_id: string;
  objective: string[];
  content?: string | null;
  url?: string | null;
  file_name?: string | null;
  content_type?: string | null;
  encoded_content?: string | null;
  metadata?: Record<string, unknown> | null;
  submittedAt?: string;
};

export type AgentRef = {
  agent_id: string;
  role: string;
  deployment: string;
};

export type AgentDefinition = {
  agent_id?: string;
  name: string;
  instructions: string;
  deployment: string;
  role: string;
  temperature?: number;
};

export type AssemblyDefinition = {
  id: string;
  topic_name: string;
  essay_id: string;
  agents: AgentDefinition[];
};

export type Assembly = {
  id: string;
  topic_name: string;
  essay_id: string;
  agents: AgentRef[];
};
