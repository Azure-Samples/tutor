import React, { createContext, useState, useContext, ReactNode } from "react";
import { Transcription } from "@/types/transcription";

interface TranscriptionContextProps {
  transcriptions: { [specialistId: string]: Transcription[] }; // Armazenar as transcrições por especialista
  selectedTranscription: Transcription | null;
  setTranscriptions: (specialistId: string, transcriptions: Transcription[]) => void;
  setSelectedTranscription: (transcription: Transcription | null) => void;
}

// Criando o contexto com valores padrão
const TranscriptionContext = createContext<TranscriptionContextProps>({
  transcriptions: {}, // Inicialmente vazio
  selectedTranscription: null,
  setTranscriptions: () => {},
  setSelectedTranscription: () => {},
});

// Função para acessar o contexto
export const useTranscriptionContext = () => useContext(TranscriptionContext);

// Componente que fornece o contexto
export const TranscriptionProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [transcriptions, setAllTranscriptions] = useState<{ [specialistId: string]: Transcription[] }>({});
  const [selectedTranscription, setSelectedTranscription] = useState<Transcription | null>(null);

  // Função para definir transcrições para um especialista específico
  const setTranscriptions = (specialistId: string, transcriptions: Transcription[]) => {
    setAllTranscriptions((prev) => ({
      ...prev,
      [specialistId]: transcriptions, // Atualiza ou adiciona as transcrições para o especialista
    }));
  };

  return (
    <TranscriptionContext.Provider value={{ transcriptions, setTranscriptions, selectedTranscription, setSelectedTranscription }}>
      {children}
    </TranscriptionContext.Provider>
  );
};
