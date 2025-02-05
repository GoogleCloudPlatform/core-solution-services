import { useEffect, useState } from 'react';
import { 
  Box, 
  Typography, 
  Table, 
  TableBody, 
  TableCell, 
  TableContainer, 
  TableHead, 
  TableRow,
  IconButton,
  Button,
  Select,
  MenuItem,
  Checkbox,
  FormControl
} from '@mui/material';
import { styled } from '@mui/material/styles';
import { QueryEngine, QUERY_ENGINE_TYPES } from '../lib/types';
import { useAuth } from '../contexts/AuthContext';
import { fetchAllEngines } from '../lib/api';
import AddIcon from '@mui/icons-material/Add';
import MoreVertIcon from '@mui/icons-material/MoreVert';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import ErrorIcon from '@mui/icons-material/Error';
import SyncIcon from '@mui/icons-material/Sync';
import KeyboardArrowDownIcon from '@mui/icons-material/KeyboardArrowDown';

const StyledTableCell = styled(TableCell)(({ theme }) => ({
  borderBottom: '1px solid #333',
  color: 'white',
  padding: '16px',
  '&.MuiTableCell-head': {
    backgroundColor: 'transparent',
    fontWeight: 500,
  }
}));

const StyledTableRow = styled(TableRow)({
  '&:hover': {
    backgroundColor: 'rgba(255, 255, 255, 0.1)',
  },
});

const StyledSelect = styled(Select)({
  backgroundColor: '#242424',
  color: 'white',
  '& .MuiSelect-icon': { color: 'white' },
  height: '36px',
  minWidth: '120px',
  borderRadius: '4px',
  '&.MuiOutlinedInput-root': {
    '& fieldset': {
      borderColor: '#333',
    },
    '&:hover fieldset': {
      borderColor: '#444',
    },
  },
});

const Sources = () => {
  const [sources, setSources] = useState<QueryEngine[]>([]);
  const { user } = useAuth();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedSources, setSelectedSources] = useState<string[]>([]);
  const [typeFilter, setTypeFilter] = useState('all');
  const [jobStatusFilter, setJobStatusFilter] = useState('all');
  const [rowsPerPage, setRowsPerPage] = useState(3);

  useEffect(() => {
    const loadSources = async () => {
      if (!user?.token) return;
      
      try {
        const engines = await fetchAllEngines(user.token)();
        if (engines) {
          setSources(engines);
        }
      } catch (err) {
        setError('Failed to load sources');
        console.error('Error loading sources:', err);
      } finally {
        setLoading(false);
      }
    };

    loadSources();
  }, [user]);

  const handleSelectAll = (event: React.ChangeEvent<HTMLInputElement>) => {
    if (event.target.checked) {
      setSelectedSources(sources.map(source => source.id));
    } else {
      setSelectedSources([]);
    }
  };

  const handleSelectSource = (id: string) => {
    setSelectedSources(prev => {
      if (prev.includes(id)) {
        return prev.filter(sourceId => sourceId !== id);
      } else {
        return [...prev, id];
      }
    });
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'Success':
        return <CheckCircleIcon sx={{ color: '#4CAF50' }} />;
      case 'Failed':
        return <ErrorIcon sx={{ color: '#f44336' }} />;
      case 'Active':
        return <SyncIcon sx={{ color: '#2196F3' }} />;
      default:
        return null;
    }
  };

  return (
    <Box sx={{ p: 3, height: '100%', backgroundColor: '#1a1a1a' }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Box>
          <Typography variant="h5" sx={{ color: 'white', mb: 1 }}>Sources</Typography>
          <Typography variant="body2" sx={{ color: '#888' }}>
            Brief description of what Sources means and how they're used
          </Typography>
        </Box>
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          sx={{ 
            backgroundColor: '#4a90e2',
            '&:hover': { backgroundColor: '#357abd' },
            borderRadius: '20px',
            textTransform: 'none'
          }}
        >
          Add Source
        </Button>
      </Box>

      <Box sx={{ display: 'flex', gap: 2, mb: 2 }}>
        <FormControl size="small">
          <StyledSelect
            value={typeFilter}
            onChange={(e) => setTypeFilter(e.target.value as string)}
            IconComponent={KeyboardArrowDownIcon}
            displayEmpty
          >
            <MenuItem value="all">Type</MenuItem>
            {Object.entries(QUERY_ENGINE_TYPES).map(([key, value]) => (
              <MenuItem key={key} value={key}>{value}</MenuItem>
            ))}
          </StyledSelect>
        </FormControl>

        <FormControl size="small">
          <StyledSelect
            value={jobStatusFilter}
            onChange={(e) => setJobStatusFilter(e.target.value as string)}
            IconComponent={KeyboardArrowDownIcon}
            displayEmpty
          >
            <MenuItem value="all">Job Status</MenuItem>
            <MenuItem value="success">Success</MenuItem>
            <MenuItem value="failed">Failed</MenuItem>
            <MenuItem value="active">Active</MenuItem>
          </StyledSelect>
        </FormControl>

        <FormControl size="small">
          <StyledSelect
            value="created"
            IconComponent={KeyboardArrowDownIcon}
            displayEmpty
          >
            <MenuItem value="created">Created</MenuItem>
          </StyledSelect>
        </FormControl>

        <Box sx={{ marginLeft: 'auto', display: 'flex', alignItems: 'center', gap: 2 }}>
          <Typography sx={{ color: 'white' }}>Rows per page</Typography>
          <StyledSelect
            value={rowsPerPage}
            onChange={(e) => setRowsPerPage(Number(e.target.value))}
            IconComponent={KeyboardArrowDownIcon}
          >
            <MenuItem value={3}>3</MenuItem>
            <MenuItem value={5}>5</MenuItem>
            <MenuItem value={10}>10</MenuItem>
          </StyledSelect>
          <Typography sx={{ color: 'white' }}>1-3 of 3</Typography>
        </Box>
      </Box>

      <TableContainer sx={{ backgroundColor: 'transparent' }}>
        <Table>
          <TableHead>
            <TableRow>
              <StyledTableCell padding="checkbox">
                <Checkbox
                  checked={selectedSources.length === sources.length}
                  indeterminate={selectedSources.length > 0 && selectedSources.length < sources.length}
                  onChange={handleSelectAll}
                  sx={{ color: 'white' }}
                />
              </StyledTableCell>
              <StyledTableCell>Name</StyledTableCell>
              <StyledTableCell>Job Status</StyledTableCell>
              <StyledTableCell>Type</StyledTableCell>
              <StyledTableCell>Created</StyledTableCell>
              <StyledTableCell align="right"></StyledTableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {sources.map((source) => (
              <StyledTableRow key={source.id}>
                <StyledTableCell padding="checkbox">
                  <Checkbox
                    checked={selectedSources.includes(source.id)}
                    onChange={() => handleSelectSource(source.id)}
                    sx={{ color: 'white' }}
                  />
                </StyledTableCell>
                <StyledTableCell>{source.name}</StyledTableCell>
                <StyledTableCell>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    {getStatusIcon('Success')}
                    Success
                  </Box>
                </StyledTableCell>
                <StyledTableCell>
                  {QUERY_ENGINE_TYPES[source.query_engine_type as keyof typeof QUERY_ENGINE_TYPES] || source.query_engine_type}
                </StyledTableCell>
                <StyledTableCell>{new Date(source.created_time).toLocaleDateString()}</StyledTableCell>
                <StyledTableCell align="right">
                  <IconButton size="small" sx={{ color: 'white' }}>
                    <MoreVertIcon />
                  </IconButton>
                </StyledTableCell>
              </StyledTableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>
    </Box>
  );
};

export default Sources; 