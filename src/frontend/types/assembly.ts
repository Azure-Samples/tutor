import type { Grader } from "./grader";

export type Assembly = {
  id: string;
  agents: Grader[];
  topic_name: string;
};
