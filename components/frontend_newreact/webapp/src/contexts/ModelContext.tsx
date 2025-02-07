import React, { createContext, useContext, useState, ReactNode } from 'react';
import { ChatModel } from '../lib/types';

interface ModelContextType {
  selectedModel: ChatModel;
  setSelectedModel: (model: ChatModel) => void;
}

const ModelContext = createContext<ModelContextType | undefined>(undefined);

const DEFAULT_MODEL: ChatModel = {
  id: 'VertexAI-Chat',
  name: 'Gemini',
  description: 'Gemini chat model from Vertex AI',
  purposes: ['General purpose chat'],
  isNew: false,
  isMultimodal: true
};

export function ModelProvider({ children }: { children: ReactNode }) {
  const [selectedModel, setSelectedModel] = useState<ChatModel>(DEFAULT_MODEL);

  return (
    <ModelContext.Provider value={{ selectedModel, setSelectedModel }}>
      {children}
    </ModelContext.Provider>
  );
}

export function useModel() {
  const context = useContext(ModelContext);
  if (context === undefined) {
    throw new Error('useModel must be used within a ModelProvider');
  }
  return context;
} 