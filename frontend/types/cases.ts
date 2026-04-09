import type { Profile } from "@/types/profile";
import type { CaseStep } from "@/types/steps";

export type Case = {
  id?: string;
  name: string;
  role: string;
  steps: CaseStep[];
  profile?: Profile;
  history?: Record<string, unknown>;
};
