import { createContext, useContext, useState, ReactNode } from 'react';

interface HumanEvaluationContextType {
  humanEvaluation: Record<string, number>;
  updateHumanEvaluation: (criterion: string, value: number) => void;
}

const HumanEvaluationContext = createContext<HumanEvaluationContextType | undefined>(undefined);

export const useHumanEvaluation = () => {
  const context = useContext(HumanEvaluationContext);
  if (!context) {
    throw new Error('useHumanEvaluation must be used within a HumanEvaluationProvider');
  }
  return context;
};

export const HumanEvaluationProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [humanEvaluation, setHumanEvaluation] = useState<Record<string, number>>({});

  const updateHumanEvaluation = (criterion: string, value: number) => {
    setHumanEvaluation((prev) => ({ ...prev, [criterion]: value }));
  };

  return (
    <HumanEvaluationContext.Provider value={{ humanEvaluation, updateHumanEvaluation }}>
      {children}
    </HumanEvaluationContext.Provider>
  );
};
