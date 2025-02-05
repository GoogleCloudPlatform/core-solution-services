import { Box, Typography, Button, Slider, Paper } from '@mui/material';
import KeyboardArrowDownIcon from '@mui/icons-material/KeyboardArrowDown';
import React, { useState } from 'react';
import ModelBrowser from './ModelBrowser';

interface SettingsDrawerProps {
    open: boolean;
    onClose: () => void;
    selectedModel: string;
    onModelChange: (modelName: string) => void;
}

const SettingsDrawer: React.FC<SettingsDrawerProps> = ({ 
    open, 
    selectedModel,
    onModelChange 
}) => {
    const [temperature, setTemperature] = useState(1.0);
    const [modelBrowserOpen, setModelBrowserOpen] = useState(false);

    const handleModelSelect = (modelName: string) => {
        onModelChange(modelName);
        setModelBrowserOpen(false);
    };

    const handleTemperatureChange = (event: Event, newValue: number | number[]) => {
        setTemperature(newValue as number);
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
                {selectedModel}
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
                    Model description suspendisse ad a fusce himenaeos condimentum hendrerit vehicula faucibus nam sem malesuada vestibulum fermentum nam ultrices accumsan convallis parturient.
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

