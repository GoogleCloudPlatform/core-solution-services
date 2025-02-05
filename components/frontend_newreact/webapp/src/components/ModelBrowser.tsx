import { 
    Dialog, 
    DialogTitle, 
    DialogContent, 
    IconButton, 
    InputBase, 
    Box, 
    Typography, 
    Chip,
    Button,
    styled
} from '@mui/material';
import CloseIcon from '@mui/icons-material/Close';
import SearchIcon from '@mui/icons-material/Search';
import CheckIcon from '@mui/icons-material/Check';
import { useEffect, useState } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { fetchAllChatModels } from '../lib/api';
import { ChatModel } from '../lib/types';

interface ModelBrowserProps {
    open: boolean;
    onClose: () => void;
    onSelectModel: (modelName: string) => void;
    selectedModel: string;
}

const SearchBox = styled(Box)(({ theme }) => ({
    display: 'flex',
    alignItems: 'center',
    backgroundColor: '#2A2A2A',
    borderRadius: 24,
    padding: '4px 16px',
    marginBottom: theme.spacing(3),
}));

const ModelCard = styled(Box)(({ theme }) => ({
    padding: theme.spacing(2),
    borderBottom: '1px solid rgba(255, 255, 255, 0.1)',
    '&:last-child': {
        borderBottom: 'none',
    },
}));

const ModelBrowser: React.FC<ModelBrowserProps> = ({ 
    open, 
    onClose, 
    onSelectModel,
    selectedModel 
}) => {
    const [models, setModels] = useState<ChatModel[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const { user } = useAuth();

    useEffect(() => {
        const loadModels = async () => {
            if (!user) return;
            
            try {
                setLoading(true);
                const modelNames = await fetchAllChatModels(user.token)();
                if (modelNames) {
                    // Transform the model names into ChatModel objects
                    const chatModels: ChatModel[] = modelNames.map(name => ({
                        name,
                        description: "Advanced language model capable of understanding and generating human-like text.",
                        purposes: ['Chat', 'Text Generation', 'Analysis'],
                        isNew: false // You might want to determine this based on some criteria
                    }));
                    setModels(chatModels);
                }
            } catch (err) {
                console.error('Error loading models:', err);
                setError('Failed to load models');
            } finally {
                setLoading(false);
            }
        };

        if (open) {
            loadModels();
        }
    }, [open, user]);

    return (
        <Dialog 
            open={open} 
            onClose={onClose}
            maxWidth="md"
            fullWidth
            PaperProps={{
                sx: {
                    backgroundColor: '#1A1A1A',
                    color: 'white',
                    minHeight: '80vh',
                }
            }}
        >
            <DialogTitle sx={{ 
                display: 'flex', 
                justifyContent: 'space-between',
                alignItems: 'center',
                p: 3,
            }}>
                <Typography variant="h5">Browse Models</Typography>
                <IconButton onClick={onClose} sx={{ color: 'white' }}>
                    <CloseIcon />
                </IconButton>
            </DialogTitle>

            <DialogContent>
                <SearchBox>
                    <InputBase
                        placeholder="Hinted search text"
                        sx={{ 
                            flex: 1,
                            color: 'white',
                            '& input::placeholder': {
                                color: 'rgba(255, 255, 255, 0.5)',
                            }
                        }}
                    />
                    <SearchIcon sx={{ color: 'rgba(255, 255, 255, 0.7)' }} />
                </SearchBox>

                {loading ? (
                    <Box sx={{ p: 3, textAlign: 'center' }}>
                        <Typography>Loading models...</Typography>
                    </Box>
                ) : error ? (
                    <Box sx={{ p: 3, textAlign: 'center', color: '#E57373' }}>
                        <Typography>{error}</Typography>
                    </Box>
                ) : (
                    models.map((model, index) => (
                        <ModelCard key={index}>
                            <Box sx={{ 
                                display: 'flex', 
                                justifyContent: 'space-between',
                                alignItems: 'flex-start',
                                mb: 1
                            }}>
                                <Box>
                                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                                        <Typography variant="h6">{model.name}</Typography>
                                        {model.isNew && (
                                            <Chip 
                                                label="New" 
                                                size="small"
                                                sx={{ 
                                                    backgroundColor: '#E57373',
                                                    color: 'white',
                                                    height: 20,
                                                    fontSize: '0.75rem'
                                                }} 
                                            />
                                        )}
                                    </Box>
                                    <Typography 
                                        variant="body2" 
                                        sx={{ color: 'rgba(255, 255, 255, 0.7)', mb: 2 }}
                                    >
                                        {model.description}
                                    </Typography>
                                    <Box sx={{ display: 'flex', gap: 1 }}>
                                        {model.purposes.map((purpose, i) => (
                                            <Chip
                                                key={i}
                                                label={purpose}
                                                sx={{
                                                    backgroundColor: 'rgba(255, 255, 255, 0.1)',
                                                    color: 'white',
                                                    '&:hover': {
                                                        backgroundColor: 'rgba(255, 255, 255, 0.15)',
                                                    }
                                                }}
                                            />
                                        ))}
                                    </Box>
                                </Box>
                                {selectedModel === model.name ? (
                                    <Box sx={{ 
                                        display: 'flex', 
                                        alignItems: 'center',
                                        color: '#90CAF9',
                                        gap: 0.5 
                                    }}>
                                        <CheckIcon fontSize="small" />
                                        <Typography variant="button">Selected</Typography>
                                    </Box>
                                ) : (
                                    <Button
                                        variant="contained"
                                        onClick={() => onSelectModel(model.name)}
                                        sx={{
                                            backgroundColor: '#90CAF9',
                                            color: 'black',
                                            '&:hover': {
                                                backgroundColor: '#64B5F6'
                                            }
                                        }}
                                    >
                                        Use Model
                                    </Button>
                                )}
                            </Box>
                        </ModelCard>
                    ))
                )}
            </DialogContent>
        </Dialog>
    );
};

export default ModelBrowser; 