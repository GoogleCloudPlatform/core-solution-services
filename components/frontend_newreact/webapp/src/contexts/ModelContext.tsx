import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { ChatModel } from '../lib/types';
import { fetchAllChatModels } from '../lib/api';
import { useAuth } from './AuthContext';

interface ModelContextType {
    selectedModel: ChatModel | null;
    setSelectedModel: (model: ChatModel) => void;
    loading: boolean;
}

const ModelContext = createContext<ModelContextType | undefined>(undefined);

const DEFAULT_MODEL_ID = 'VertexAI-Chat';

export function ModelProvider({ children }: { children: ReactNode }) {
    const [selectedModel, setSelectedModel] = useState<ChatModel | null>(null);
    const [loading, setLoading] = useState(true);
    const { user } = useAuth();

    useEffect(() => {
        const initializeModel = async () => {
            if (!user) return;

            setLoading(true);

            try {
                const models = await fetchAllChatModels(user.token)();
                if (models && models.length > 0) {
                    const storedModelId = localStorage.getItem('selectedModelId');
                    let initialModel = null;

                    if (storedModelId) {
                        initialModel = models.find(m => m.id === storedModelId);
                    }

                    if (!initialModel) {
                        initialModel = models.find(m => m.id === DEFAULT_MODEL_ID) || models[0];
                    }
                    setSelectedModel(initialModel);
                } else {
                    setSelectedModel(null);
                }
            } catch (error) {
                console.error('ModelContext Error loading initial model:', error);
                setSelectedModel(null);
            } finally {
                setLoading(false);
            }
        };

        initializeModel();
    }, [user]);

    const handleSetSelectedModel = (model: ChatModel) => {
        setSelectedModel(model);
        localStorage.setItem('selectedModelId', model.id);
    };

    return (
        <ModelContext.Provider value={{ selectedModel, setSelectedModel: handleSetSelectedModel, loading }}>
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