import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { createQueryEngine } from '../lib/api';
import { QUERY_ENGINE_TYPES, QUERY_ENGINE_DEFAULT_TYPE, QueryEngine } from '../lib/types';
import {
  Box,
  Typography,
  TextField,
  Select,
  MenuItem,
  Button,
  IconButton,
  Collapse,
  Slider,
} from '@mui/material';
import NavigateNextIcon from '@mui/icons-material/NavigateNext';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import ClearIcon from '@mui/icons-material/Clear';
import styled from '@emotion/styled';

const StyledSelect = styled(Select)({
  backgroundColor: '#242424',
  color: 'white',
  '& .MuiOutlinedInput-notchedOutline': { borderColor: '#333' },
  '&:hover .MuiOutlinedInput-notchedOutline': { borderColor: '#444' },
});

const StyledSlider = styled(Slider)({
  color: '#4a90e2',
  '& .MuiSlider-rail': {
    backgroundColor: '#333',
  },
  '& .MuiSlider-track': {
    backgroundColor: '#4a90e2',
  },
  '& .MuiSlider-thumb': {
    backgroundColor: '#4a90e2',
  },
  '& .MuiSlider-mark': {
    backgroundColor: '#666',
  },
  '& .MuiSlider-markLabel': {
    color: '#888',
  },
});

const StyledMenuItem = styled(MenuItem)({
  backgroundColor: '#242424',
  color: 'white',
  '&:hover': {
    backgroundColor: '#333',
  },
  '&.Mui-selected': {
    backgroundColor: '#2a2a2a',
    '&:hover': {
      backgroundColor: '#333',
    }
  }
});

const AddSource = () => {
  const navigate = useNavigate();
  const { user } = useAuth();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [showAdvanced, setShowAdvanced] = useState(false);

  const [formData, setFormData] = useState<Partial<QueryEngine>>({
    name: '',
    description: '',
    query_engine_type: QUERY_ENGINE_DEFAULT_TYPE,
    doc_url: '',
    embedding_type: 'text-embedding-ada-002',
    vector_store: 'vertex_matching_engine',
    depth_limit: 100,
    chunk_size: 500,
    is_multimodal: false,
  });

  const handleChange = (field: keyof QueryEngine, value: any) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const handleSubmit = async () => {
    if (!user?.token) return;

    setLoading(true);
    setError(null);

    try {
      const response = await createQueryEngine(user.token)(formData as QueryEngine);
      if (response) {
        navigate('/sources');
      }
    } catch (err: any) {
      setError(err.message || 'Failed to create source');
    } finally {
      setLoading(false);
    }
  };

  const handleDepthLimitChange = (_event: Event, newValue: number | number[]) => {
    handleChange('depth_limit', newValue as number);
  };

  const handleChunkSizeChange = (_event: Event, newValue: number | number[]) => {
    handleChange('chunk_size', newValue as number);
  };

  return (
    <Box sx={{ 
      height: '100vh',
      backgroundColor: '#1a1a1a',
      color: 'white'
    }}>
      {/* Header */}
      <Box sx={{ 
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        p: 2,
        borderBottom: '1px solid #333'
      }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <Typography 
            component="span" 
            sx={{ color: '#888', cursor: 'pointer' }}
            onClick={() => navigate('/sources')}
          >
            Sources
          </Typography>
          <NavigateNextIcon sx={{ color: '#888' }} />
          <Typography>Add New</Typography>
        </Box>
        <Box sx={{ display: 'flex', gap: 2 }}>
          <Button
            variant="text"
            onClick={() => navigate('/sources')}
            sx={{ color: 'white' }}
          >
            Cancel
          </Button>
          <Button
            variant="contained"
            onClick={handleSubmit}
            disabled={loading}
            sx={{ 
              backgroundColor: '#4a90e2',
              '&:hover': { backgroundColor: '#357abd' }
            }}
          >
            Save
          </Button>
        </Box>
      </Box>

      {/* Form Content */}
      <Box sx={{ p: 3, maxWidth: '800px', mx: 'auto' }}>
        <Box sx={{ mb: 4 }}>
          <Typography variant="caption" sx={{ color: '#888', mb: 1, display: 'block' }}>
            Name
          </Typography>
          <TextField
            fullWidth
            placeholder="Input"
            value={formData.name}
            onChange={(e) => handleChange('name', e.target.value)}
            required
            error={!formData.name}
            helperText={!formData.name && "Required"}
            InputProps={{
              endAdornment: formData.name && (
                <IconButton size="small" onClick={() => handleChange('name', '')}>
                  <ClearIcon fontSize="small" />
                </IconButton>
              )
            }}
            sx={{
              '& .MuiOutlinedInput-root': {
                backgroundColor: '#242424',
                color: 'white',
                '& fieldset': { borderColor: '#333' },
                '&:hover fieldset': { borderColor: '#444' },
              }
            }}
          />
        </Box>

        <Box sx={{ mb: 4 }}>
          <Typography variant="caption" sx={{ color: '#888', mb: 1, display: 'block' }}>
            Data URL
          </Typography>
          <TextField
            fullWidth
            placeholder="Input"
            value={formData.doc_url}
            onChange={(e) => handleChange('doc_url', e.target.value)}
            required
            error={!formData.doc_url}
            helperText={!formData.doc_url && "Required"}
            InputProps={{
              endAdornment: formData.doc_url && (
                <IconButton size="small" onClick={() => handleChange('doc_url', '')}>
                  <ClearIcon fontSize="small" />
                </IconButton>
              )
            }}
            sx={{
              '& .MuiOutlinedInput-root': {
                backgroundColor: '#242424',
                color: 'white',
                '& fieldset': { borderColor: '#333' },
                '&:hover fieldset': { borderColor: '#444' },
              }
            }}
          />
        </Box>

        <Button
          onClick={() => setShowAdvanced(!showAdvanced)}
          startIcon={<ExpandMoreIcon sx={{ transform: showAdvanced ? 'rotate(180deg)' : 'none' }} />}
          sx={{ color: 'white', textTransform: 'none' }}
        >
          {showAdvanced ? 'Hide' : 'Show'} Advanced Settings
        </Button>

        <Collapse in={showAdvanced}>
          <Box sx={{ mt: 3 }}>
            <Box sx={{ mb: 4 }}>
              <Typography variant="caption" sx={{ color: '#888', mb: 1, display: 'block' }}>
                Type
              </Typography>
              <StyledSelect
                fullWidth
                value={formData.query_engine_type}
                onChange={(e) => handleChange('query_engine_type', e.target.value)}
                required
                MenuProps={{
                  PaperProps: {
                    sx: {
                      backgroundColor: '#242424',
                      border: '1px solid #333',
                      borderRadius: '4px',
                      boxShadow: '0 4px 8px rgba(0, 0, 0, 0.5)',
                      maxHeight: '300px',
                    }
                  }
                }}
              >
                {Object.entries(QUERY_ENGINE_TYPES).map(([key, value]) => (
                  <StyledMenuItem key={key} value={key}>
                    {value}{key === QUERY_ENGINE_DEFAULT_TYPE ? ' (Default)' : ''}
                  </StyledMenuItem>
                ))}
              </StyledSelect>
            </Box>

            <Box sx={{ display: 'flex', gap: 2, mb: 4 }}>
              <Box sx={{ flex: 1 }}>
                <Typography variant="caption" sx={{ color: '#888', mb: 1, display: 'block' }}>
                  Vector Store
                </Typography>
                <StyledSelect
                  fullWidth
                  value={formData.vector_store}
                  onChange={(e) => handleChange('vector_store', e.target.value)}
                >
                  <MenuItem value="vertex_matching_engine">Vertex Matching Engine</MenuItem>
                </StyledSelect>
              </Box>

              <Box sx={{ flex: 1 }}>
                <Typography variant="caption" sx={{ color: '#888', mb: 1, display: 'block' }}>
                  Embedding Type
                </Typography>
                <StyledSelect
                  fullWidth
                  value={formData.embedding_type}
                  onChange={(e) => handleChange('embedding_type', e.target.value)}
                >
                  <MenuItem value="text-embedding-ada-002">text-embedding-ada-002</MenuItem>
                </StyledSelect>
              </Box>
            </Box>

            <Box sx={{ mb: 3 }}>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
                <Typography variant="caption" sx={{ color: '#888' }}>
                  Depth Limit
                </Typography>
                <Typography variant="caption" sx={{ color: 'white' }}>
                  {formData.depth_limit}
                </Typography>
              </Box>
              <StyledSlider
                value={formData.depth_limit ?? undefined}
                onChange={handleDepthLimitChange}
                min={1}
                max={10}
                step={1}
                marks
                sx={{ mb: 4 }}
              />

              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
                <Typography variant="caption" sx={{ color: '#888' }}>
                  Chunk Size
                </Typography>
                <Typography variant="caption" sx={{ color: 'white' }}>
                  {formData.chunk_size}
                </Typography>
              </Box>
              <StyledSlider
                value={formData.chunk_size ?? undefined}
                onChange={handleChunkSizeChange}
                min={100}
                max={1000}
                step={100}
                marks
              />
            </Box>

            <Box sx={{ mb: 3 }}>
              <Typography variant="caption" sx={{ color: '#888', mb: 1, display: 'block' }}>
                Agents
              </Typography>
              <TextField
                fullWidth
                placeholder="Placeholder"
                value={formData.agents?.join(', ') || ''}
                onChange={(e) => handleChange('agents', e.target.value.split(',').map(s => s.trim()))}
                InputProps={{
                  endAdornment: formData.agents?.length ? (
                    <IconButton size="small" onClick={() => handleChange('agents', [])}>
                      <ClearIcon fontSize="small" />
                    </IconButton>
                  ) : null
                }}
                sx={{
                  '& .MuiOutlinedInput-root': {
                    backgroundColor: '#242424',
                    color: 'white',
                    '& fieldset': { borderColor: '#333' },
                    '&:hover fieldset': { borderColor: '#444' },
                  }
                }}
              />
            </Box>

            <Box sx={{ mb: 3 }}>
              <Typography variant="caption" sx={{ color: '#888', mb: 1, display: 'block' }}>
                Child Sources
              </Typography>
              <TextField
                fullWidth
                placeholder="Placeholder"
                value={formData.child_engines?.join(', ') || ''}
                onChange={(e) => handleChange('child_engines', e.target.value.split(',').map(s => s.trim()))}
                InputProps={{
                  endAdornment: formData.child_engines?.length ? (
                    <IconButton size="small" onClick={() => handleChange('child_engines', [])}>
                      <ClearIcon fontSize="small" />
                    </IconButton>
                  ) : null
                }}
                sx={{
                  '& .MuiOutlinedInput-root': {
                    backgroundColor: '#242424',
                    color: 'white',
                    '& fieldset': { borderColor: '#333' },
                    '&:hover fieldset': { borderColor: '#444' },
                  }
                }}
              />
            </Box>
          </Box>
        </Collapse>

        {error && (
          <Typography color="error" sx={{ mt: 2 }}>
            {error}
          </Typography>
        )}
      </Box>
    </Box>
  );
};

export default AddSource; 