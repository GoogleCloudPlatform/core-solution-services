import { Box, Typography, Button, Slider, Paper } from '@mui/material';
import KeyboardArrowDownIcon from '@mui/icons-material/KeyboardArrowDown';
import React, { useState, useEffect } from 'react';
import ModelBrowser from './ModelBrowser';
import { useModel } from '../contexts/ModelContext';
import { ChatModel } from '../lib/types';

interface SettingsDrawerProps {
    open: boolean;
    onClose: () => void;
}

const SettingsDrawer: React.FC<SettingsDrawerProps> = ({ 
    open
}) => {
    const [temperature, setTemperature] = useState(0.2);
    const [modelBrowserOpen, setModelBrowserOpen] = useState(false);
    const { selectedModel, setSelectedModel, loading } = useModel();

    useEffect(() => {
        if (selectedModel?.modelParams?.temperature !== undefined) {
            setTemperature(selectedModel.modelParams.temperature);
        }
    }, [selectedModel]);

    const handleModelSelect = (model: ChatModel) => {
        setSelectedModel(model);
        setModelBrowserOpen(false);
        if (model.modelParams?.temperature !== undefined) {
            setTemperature(model.modelParams.temperature);
        }
    };

    const handleTemperatureChange = (event: Event, newValue: number | number[]) => {
        setTemperature(newValue as number);
        if (selectedModel) {
            const updatedModel = {
                ...selectedModel,
                modelParams: {
                    ...selectedModel.modelParams,
                    temperature: newValue as number
                }
            };
            setSelectedModel(updatedModel);
        }
    };

    if (!open) return null;

    return (
        <Box sx={{ 
            p: 3, 
            height: '100%', 
            color: 'white',
            backgroundColor: '#1f1f1f',
        }}>
            <Typography variant="subtitle1" sx={{ mb: 2 }}>
                Model
            </Typography>
            
            <Button
                onClick={() => setModelBrowserOpen(true)}
                fullWidth
                endIcon={<KeyboardArrowDownIcon />}
                disabled={loading}
                sx={{
                    mb: 3,
                    backgroundColor: '#242424',
                    color: 'white',
                    justifyContent: 'space-between',
                    padding: '14px',
                    textAlign: 'left',
                    border: '1px solid rgba(255, 255, 255, 0.1)',
                    '&:hover': {
                        backgroundColor: '#2a2a2a',
                        border: '1px solid rgba(255, 255, 255, 0.2)',
                    }
                }}
            >
                {loading ? 'Loading...' : selectedModel.name}
            </Button>

            <Paper 
                sx={{ 
                    p: 2, 
                    mb: 3, 
                    backgroundColor: '#242424',
                    color: 'rgba(255, 255, 255, 0.7)',
                    border: '1px solid rgba(255, 255, 255, 0.1)'
                }}
            >
                <Typography variant="body2" sx={{ mb: 1 }}>
                    {selectedModel.description}
                </Typography>
            </Paper>

            <Box sx={{ mb: 2 }}>
                <Box sx={{ 
                    display: 'flex', 
                    justifyContent: 'space-between', 
                    alignItems: 'center',
                    mb: 2 
                }}>
                    <Typography variant="subtitle1">
                        Temperature
                    </Typography>
                    <Typography variant="body2" sx={{ color: 'rgba(255, 255, 255, 0.7)' }}>
                        {temperature.toFixed(1)}
                    </Typography>
                </Box>
                <Slider
                    value={temperature}
                    onChange={handleTemperatureChange}
                    min={0}
                    max={2}
                    step={0.1}
                    disabled={selectedModel?.modelParams?.temperature === undefined}
                    sx={{
                        color: '#4a90e2',
                        '& .MuiSlider-rail': {
                            backgroundColor: 'rgba(255, 255, 255, 0.1)',
                        },
                        '& .MuiSlider-track': {
                            backgroundColor: '#4a90e2',
                        },
                        '& .MuiSlider-thumb': {
                            backgroundColor: '#4a90e2',
                        }
                    }}
                />
                {selectedModel?.modelParams?.temperature === undefined && (
                    <Typography variant="caption" sx={{ color: 'rgba(255, 255, 255, 0.5)' }}>
                        Temperature control not available for this model
                    </Typography>
                )}
            </Box>

            <ModelBrowser
                open={modelBrowserOpen}
                onClose={() => setModelBrowserOpen(false)}
                onSelectModel={handleModelSelect}
                selectedModel={selectedModel}
            />
        </Box>
    );
};

export default SettingsDrawer;

