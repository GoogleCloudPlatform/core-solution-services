import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { createQueryEngine } from '../lib/api';
import { QUERY_ENGINE_TYPES, QueryEngine } from '../lib/types';
import {
  Box,
  Typography,
  TextField,
  Select,
  MenuItem,
  Button,
  IconButton,
  Collapse,
} from '@mui/material';
import NavigateNextIcon from '@mui/icons-material/NavigateNext';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import ClearIcon from '@mui/icons-material/Clear';

const AddSource = () => {
  const navigate = useNavigate();
  const { user } = useAuth();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [showAdvanced, setShowAdvanced] = useState(false);

  const [formData, setFormData] = useState<Partial<QueryEngine>>({
    name: '',
    description: '',
    query_engine_type: 'qe_integrated_search', // default to Integrated Search
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

        <Box sx={{ mb: 4 }}>
          <Typography variant="caption" sx={{ color: '#888', mb: 1, display: 'block' }}>
            Type
          </Typography>
          <Select
            fullWidth
            value={formData.query_engine_type}
            onChange={(e) => handleChange('query_engine_type', e.target.value)}
            required
            sx={{
              backgroundColor: '#242424',
              color: 'white',
              '& .MuiOutlinedInput-notchedOutline': { borderColor: '#333' },
              '&:hover .MuiOutlinedInput-notchedOutline': { borderColor: '#444' },
            }}
          >
            {Object.entries(QUERY_ENGINE_TYPES).map(([key, value]) => (
              <MenuItem key={key} value={key}>{value}</MenuItem>
            ))}
          </Select>
        </Box>

        <Button
          onClick={() => setShowAdvanced(!showAdvanced)}
          startIcon={<ExpandMoreIcon sx={{ transform: showAdvanced ? 'rotate(180deg)' : 'none' }} />}
          sx={{ color: 'white', textTransform: 'none' }}
        >
          Show Advanced Settings
        </Button>

        <Collapse in={showAdvanced}>
          <Box sx={{ mt: 3 }}>
            {/* Add your advanced settings fields here */}
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