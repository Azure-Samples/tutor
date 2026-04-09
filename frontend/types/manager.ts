import type { Specialist } from "@/types/specialist";

export type Manager = {
  id?: string;
  name: string;
  role?: string;
  assistants?: Specialist[];
  specialists: Specialist[];
  [key: string]: unknown;
};
