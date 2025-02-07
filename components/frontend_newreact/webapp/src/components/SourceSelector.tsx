import { useState, useEffect } from 'react'; // Import useEffect
import { Box, Button, Menu, MenuItem, Typography, CircularProgress } from '@mui/material';
import { ChevronDown, Search, Check } from 'lucide-react';
import { useAuth } from '../contexts/AuthContext'; // Import useAuth
import { fetchAllEngines } from '../lib/api';  // Import your API call
import { QueryEngine } from '../lib/types';  // Import your types

interface SourceSelectorProps {
    className?: string;
    onSelectSource: (source: QueryEngine) => void; // Add onSelectSource prop
}

export function SourceSelector({ className, onSelectSource }: SourceSelectorProps) {
    const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);
    const [selectedSource, setSelectedSource] = useState<QueryEngine | null>(null);  // Store the selected source object
    const open = Boolean(anchorEl);
    const { user } = useAuth();
    const [sources, setSources] = useState<QueryEngine[]>([]); // State to store fetched sources
    const [loading, setLoading] = useState(true); // Loading state
    const [error, setError] = useState<string | null>(null); // Error state

    const handleClick = (event: React.MouseEvent<HTMLElement>) => {
        setAnchorEl(event.currentTarget);
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
                const fetchedSources = await fetchAllEngines(user.token)();
                if (fetchedSources) {
                    setSources(fetchedSources);
                }
            } catch (err) {
                setError("Error fetching sources");
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
                sx={{
                    color: 'white',
                    textTransform: 'none',
                    fontSize: '1rem',
                    padding: '6px 8px',
                    minWidth: '200px',
                    justifyContent: 'space-between',
                    '&:hover': {
                        backgroundColor: 'rgba(255, 255, 255, 0.1)',
                    },
                }}
            >
                {selectedSource ? selectedSource.name : "Select Source"}
            </Button>
            <Menu
                anchorEl={anchorEl}
                open={open}
                onClose={handleClose}
                PaperProps={{
                    sx: {
                        width: '250px',
                        maxHeight: '400px',
                        backgroundColor: '#1f1f1f',
                        border: '1px solid #2f2f2f',
                        boxShadow: '0 4px 6px rgba(0, 0, 0, 0.1)',
                        '.MuiMenu-list': {
                            padding: 0,
                        },
                    },
                }}
            >
                {/* Selected Source with Checkmark */}
                <MenuItem
                    sx={{
                        backgroundColor: '#1f1f1f',
                        borderBottom: '1px solid #2f2f2f',
                        py: 1.5,
                        display: 'flex',
                        justifyContent: 'space-between',
                        alignItems: 'center',
                        '&:hover': { backgroundColor: '#1f1f1f' },
                    }}
                >
                    <Typography
                        sx={{
                            color: 'white',
                            fontSize: '0.875rem',
                        }}
                    >
                        {selectedSource?.name || "Select Source"}
                    </Typography>
                    {selectedSource && <Check className="h-4 w-4 text-white" />} {/* Conditional checkmark */}       </MenuItem>

                {/* Sources Title with Search Icon */}
                <MenuItem
                    sx={{
                        borderBottom: '1px solid #2f2f2f',
                        py: 1.5,
                        display: 'flex',
                        alignItems: 'center',
                        gap: 1,
                        '&:hover': { backgroundColor: '#1f1f1f' },
                    }}
                >
                    <Search className="h-4 w-4 text-white/70" />
                    <Typography
                        sx={{
                            color: 'white',
                            fontSize: '0.875rem',
                            fontWeight: 500,
                        }}
                    >
                        Sources
                    </Typography>
                </MenuItem>
                {/* Scrollable Sources List */}
                <Box sx={{ maxHeight: '300px', overflowY: 'auto' }}>
                    {loading ? ( // Loading indicator
                        <MenuItem sx={{ /* ... */ }}>
                            <CircularProgress size={20} color="inherit" />
                        </MenuItem>
                    ) : error ? ( // Error message
                        <MenuItem sx={{ /* ... */ }}>Error loading sources</MenuItem>
                    ) : sources.length === 0 ? ( // "No sources found"
                        <MenuItem sx={{ /* ... */ }}>No sources found</MenuItem>
                    ) : (
                        // Display sources if fetched successfully
                        sources.map((source) => (
                            <MenuItem
                                key={source.id} // Use source ID as key
                                onClick={() => handleSourceSelect(source)} // Pass the source object
                                sx={{
                                    color: 'rgba(255, 255, 255, 0.9)',
                                    fontSize: '0.875rem',
                                    py: 1.5,
                                    '&:hover': { backgroundColor: 'rgba(255, 255, 255, 0.1)' },
                                }}
                            >
                                {source.name} {/* Display the source name */}
                            </MenuItem>
                        ))
                    )}
                </Box>
            </Menu>
        </Box>
    );
}