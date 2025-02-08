import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { ChatModel } from '../lib/types';
import { fetchAllChatModels } from '../lib/api';
import { useAuth } from './AuthContext';

interface ModelContextType {
  selectedModel: ChatModel;
  setSelectedModel: (model: ChatModel) => void;
  loading: boolean;
}

const ModelContext = createContext<ModelContextType | undefined>(undefined);

// Default model ID that matches what's returned by the API
const DEFAULT_MODEL_ID = 'VertexAI-Chat';

// Temporary model used during loading
const LOADING_MODEL: ChatModel = {
  id: DEFAULT_MODEL_ID,
  name: 'Loading...',
  description: 'Loading model details...',
  purposes: [],
  isNew: false,
  isMultimodal: false
};

export function ModelProvider({ children }: { children: ReactNode }) {
  const [selectedModel, setSelectedModel] = useState<ChatModel>(LOADING_MODEL);
  const [loading, setLoading] = useState(true);
  const { user } = useAuth();

  useEffect(() => {
    const initializeModel = async () => {
      if (!user) return;

      try {
        const models = await fetchAllChatModels(user.token)();
        if (models && models.length > 0) {
          // Find the default model by ID, or fall back to first available model
          const defaultModel = models.find(m => m.id === DEFAULT_MODEL_ID) || models[0];
          setSelectedModel(defaultModel);
        }
      } catch (error) {
        console.error('Error loading initial model:', error);
      } finally {
        setLoading(false);
      }
    };

    initializeModel();
  }, [user]);

  return (
    <ModelContext.Provider value={{ selectedModel, setSelectedModel, loading }}>
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