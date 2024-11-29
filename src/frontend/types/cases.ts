import { CaseStep } from "@/types/steps";
import { Profile } from "@/types/profile";


export type Case = {
  id?: string;
  name: string;
  role: string;
  steps: CaseStep[];
  profile?: Profile;
  history?: Object;
};
