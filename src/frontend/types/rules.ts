export type SubCriteria = {
    topic: string;
    description: string;
  };
  
export type Criteria = {
  topic: string;
  description: string;
  businessRules: string[];
  subCriteria: SubCriteria[];
};