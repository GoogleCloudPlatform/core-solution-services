import { useState, useEffect } from 'react'; // Import useEffect
import { Box, Button, Menu, MenuItem, Typography, CircularProgress } from '@mui/material';
import { ChevronDown, Search, Check } from 'lucide-react';
import { useAuth } from '../contexts/AuthContext'; // Import useAuth
import { fetchAllEngines } from '../lib/api';  // Import your API call
import { QueryEngine } from '../lib/types';  // Import your types

interface SourceSelectorProps {
    className?: string;
    onSelectSource: (source: QueryEngine) => void; // Add onSelectSource prop
    disabled?: boolean;
}

export function SourceSelector({ className, onSelectSource, disabled = false }: SourceSelectorProps) {
    const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);
    const [selectedSource, setSelectedSource] = useState<QueryEngine | null>(null);  // Store the selected source object
    const open = Boolean(anchorEl);
    const { user } = useAuth();
    const [sources, setSources] = useState<QueryEngine[]>([]); // State to store fetched sources
    const [loading, setLoading] = useState(true); // Loading state
    const [error, setError] = useState<string | null>(null); // Error state

    const handleClick = (event: React.MouseEvent<HTMLElement>) => {
        if (!disabled) {
            setAnchorEl(event.currentTarget);
        }
    };

    const handleClose = () => {
        setAnchorEl(null);
    };

    const handleSourceSelect = (source: QueryEngine) => {
        setSelectedSource(source);
        onSelectSource(source);
        handleClose();
    };

    useEffect(() => {  // Fetch sources when component mounts and user is logged in
        const loadSources = async () => {
            if (!user?.token) return; // Do nothing if no user or token

            try {
                setLoading(true);
                setError(null);
                const fetchedSources = await fetchAllEngines(user.token)();
                if (fetchedSources) {
                    setSources(fetchedSources);
                }
            } catch (err) {
                setError("Failed to load sources");
                console.error(err);
            } finally {
                setLoading(false);
            }
        };

        loadSources();
    }, [user]);

    return (
        <Box className={className}>
            <Button
                onClick={handleClick}
                endIcon={<ChevronDown className="h-4 w-4" />}
                disabled={disabled || loading}
                sx={{
                    color: '#fff',
                    textTransform: 'none',
                    fontSize: '0.875rem',
                    padding: '6px 12px',
                    minWidth: '200px',
                    justifyContent: 'space-between',
                    backgroundColor: 'rgba(255, 255, 255, 0.1)',
                    '&:hover': {
                        backgroundColor: disabled ? 'rgba(255, 255, 255, 0.1)' : 'rgba(255, 255, 255, 0.15)',
                    },
                    '&.Mui-disabled': {
                        color: 'rgba(255, 255, 255, 0.5)',
                    }
                }}
            >
                {loading ? (
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                        <CircularProgress size={16} sx={{ color: 'inherit' }} />
                        <span>Loading sources...</span>
                    </Box>
                ) : selectedSource ? selectedSource.name : "Select Source"}
            </Button>
            <Menu
                anchorEl={anchorEl}
                open={open}
                onClose={handleClose}
                PaperProps={{
                    sx: {
                        width: '250px',
                        maxHeight: '400px',
                        backgroundColor: '#2A2A2A',
                        border: '1px solid rgba(255, 255, 255, 0.1)',
                        borderRadius: '8px',
                        boxShadow: '0 4px 6px rgba(0, 0, 0, 0.1)',
                        '.MuiMenu-list': {
                            padding: '4px',
                        },
                    },
                }}
            >
                {/* Selected Source with Checkmark */}
                {selectedSource && (
                    <MenuItem
                        sx={{
                            backgroundColor: '#2A2A2A',
                            borderRadius: '4px',
                            py: 1,
                            px: 1.5,
                            display: 'flex',
                            justifyContent: 'space-between',
                            alignItems: 'center',
                            mb: 1,
                            '&:hover': { backgroundColor: 'rgba(255, 255, 255, 0.1)' },
                        }}
                    >
                        <Typography
                            sx={{
                                color: '#fff',
                                fontSize: '0.875rem',
                            }}
                        >
                            {selectedSource.name}
                        </Typography>
                        <Check className="h-4 w-4 text-white" />
                    </MenuItem>
                )}

                {/* Sources Title with Search Icon */}
                <MenuItem
                    sx={{
                        py: 1,
                        px: 1.5,
                        display: 'flex',
                        alignItems: 'center',
                        gap: 1,
                        borderRadius: '4px',
                        '&:hover': { backgroundColor: 'rgba(255, 255, 255, 0.1)' },
                    }}
                >
                    <Search className="h-4 w-4 text-white/70" />
                    <Typography
                        sx={{
                            color: '#fff',
                            fontSize: '0.875rem',
                            fontWeight: 500,
                        }}
                    >
                        Sources
                    </Typography>
                </MenuItem>

                {/* Error State */}
                {error && (
                    <MenuItem
                        sx={{
                            color: '#ff6b6b',
                            py: 1,
                            px: 1.5,
                            borderRadius: '4px',
                            justifyContent: 'center',
                        }}
                    >
                        {error}
                    </MenuItem>
                )}

                {/* Loading State */}
                {loading && (
                    <MenuItem
                        sx={{
                            justifyContent: 'center',
                            py: 1,
                            px: 1.5,
                            borderRadius: '4px',
                        }}
                    >
                        <CircularProgress size={20} sx={{ color: '#fff' }} />
                    </MenuItem>
                )}

                {/* Sources List */}
                {!loading && !error && sources.length === 0 && (
                    <MenuItem
                        sx={{
                            color: '#fff',
                            py: 1,
                            px: 1.5,
                            borderRadius: '4px',
                            justifyContent: 'center',
                        }}
                    >
                        No sources available
                    </MenuItem>
                )}

                {!loading && !error && sources.map((source) => (
                    <MenuItem
                        key={source.id}
                        onClick={() => handleSourceSelect(source)}
                        sx={{
                            color: '#fff',
                            fontSize: '0.875rem',
                            py: 1,
                            px: 1.5,
                            borderRadius: '4px',
                            '&:hover': { backgroundColor: 'rgba(255, 255, 255, 0.1)' },
                        }}
                    >
                        {source.name}
                    </MenuItem>
                ))}
            </Menu>
        </Box>
    );
}