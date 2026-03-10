export type Grader = {
  agent_id: string;
  dimension: string;
  deployment: string;
};

export type GraderDefinition = {
  agent_id?: string;
  name: string;
  instructions: string;
  deployment: string;
  dimension: string;
};
