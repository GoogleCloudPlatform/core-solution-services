import { useEffect, useState } from 'react'; // Import necessary hooks for state management and side effects
import {  // Import Material-UI components for building the UI
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
import { styled } from '@mui/material/styles'; // Import styling utilities from Material-UI
import { QueryEngine, QUERY_ENGINE_TYPES } from '../lib/types'; // Import types for query engines
import { useAuth } from '../contexts/AuthContext'; // Import authentication context
import { fetchAllEngines } from '../lib/api'; // Import API function for fetching engines
import AddIcon from '@mui/icons-material/Add'; // Import icons from Material-UI
import MoreVertIcon from '@mui/icons-material/MoreVert';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import ErrorIcon from '@mui/icons-material/Error';
import SyncIcon from '@mui/icons-material/Sync';
import KeyboardArrowDownIcon from '@mui/icons-material/KeyboardArrowDown';
import { useNavigate } from 'react-router-dom'; // Import navigation hook


// Styled components for table cells and rows using Material-UI's styling solution
const StyledTableCell = styled(TableCell)(({ theme }) => ({
  borderBottom: '1px solid #333', // Bottom border for table cells
  color: 'white', // Text color
  padding: '16px', // Cell padding
  '&.MuiTableCell-head': { // Styles for header cells
    backgroundColor: 'transparent', // Transparent background for header
    fontWeight: 500, // Font weight for header text
  }
}));

const StyledTableRow = styled(TableRow)({ // Styles for table rows
  '&:hover': {
    backgroundColor: 'rgba(255, 255, 255, 0.1)', // Background color on hover
  },
});

const StyledSelect = styled(Select)({ // Styles for select dropdowns
  backgroundColor: '#242424', // Background color
  color: 'white', // Text color
  '& .MuiSelect-icon': { color: 'white' }, // Icon color
  height: '36px', // Height
  minWidth: '120px', // Minimum width
  borderRadius: '4px', // Border radius
  '&.MuiOutlinedInput-root': { // Styles for outlined variant
    '& fieldset': {
      borderColor: '#333', // Border color
    },
    '&:hover fieldset': {
      borderColor: '#444', // Border color on hover
    },
  },
});

const Sources = () => {
  const [sources, setSources] = useState<QueryEngine[]>([]); // State for storing the list of sources
  const { user } = useAuth(); // Get the authenticated user from context
  const [loading, setLoading] = useState(true); // Loading state
  const [error, setError] = useState<string | null>(null); // Error state
  const [selectedSources, setSelectedSources] = useState<string[]>([]); // State for tracking selected sources
  const [typeFilter, setTypeFilter] = useState('all'); // State for the type filter
  const [jobStatusFilter, setJobStatusFilter] = useState('all'); // State for the job status filter
  const [rowsPerPage, setRowsPerPage] = useState(3); // Rows per page state (not used for actual pagination yet)
  const navigate = useNavigate(); // For navigation

  useEffect(() => { // useEffect hook to fetch sources when the component mounts or user changes
    const loadSources = async () => {
      if (!user?.token) return; // Return early if user or token is not available

      try {
        const engines = await fetchAllEngines(user.token)(); // Fetch all engines using the API call
        if (engines) {
          setSources(engines); // Set the sources state with the fetched engines
        }
      } catch (err) {
        setError('Failed to load sources'); // Set error message if fetching fails
        console.error('Error loading sources:', err); // Log the error to the console
      } finally {
        setLoading(false); // Set loading to false after fetching, regardless of success or failure
      }
    };

    loadSources(); // Call the loadSources function
  }, [user]); // Run the effect whenever the user changes

  const handleSelectAll = (event: React.ChangeEvent<HTMLInputElement>) => { // Handler for "Select All" checkbox
    if (event.target.checked) {  // If checked, select all sources
      setSelectedSources(sources.map(source => source.id));
    } else {  // Otherwise, deselect all
      setSelectedSources([]);
    }
  };

  const handleSelectSource = (id: string) => { // Handler for selecting/deselecting individual source
    setSelectedSources(prev => { // Update selectedSources state based on current selection status
      if (prev.includes(id)) { // If already selected, remove
        return prev.filter(sourceId => sourceId !== id);
      } else { // Otherwise, add to selection
        return [...prev, id];
      }
    });
  };

  const getStatusIcon = (status: string) => { // Helper function to determine status icon
    switch (status) {
      case 'Success':
        return <CheckCircleIcon sx={{ color: '#4CAF50' }} />; // Green icon for success
      case 'Failed':
        return <ErrorIcon sx={{ color: '#f44336' }} />;     // Red icon for failure
      case 'Active':
        return <SyncIcon sx={{ color: '#2196F3' }} />;       // Blue icon for active
      default:
        return null;  // No icon for other statuses
    }
  };


  return ( // Main JSX return for the component
    <Box sx={{ 
      p: 3, 
      height: 'calc(100vh - 64px)', // Subtract header height
      backgroundColor: '#1a1a1a',
      marginTop: '64px', // Add margin to account for header
      width: '100%',
      overflow: 'auto'
    }}> 
      {/* Title and description */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Box>
          <Typography variant="h5" sx={{ color: 'white', mb: 1 }}>Sources</Typography>
          <Typography variant="body2" sx={{ color: '#888' }}>
            Brief description of what Sources means and how they're used
          </Typography>
        </Box>
        {/* Add source button */}
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={() => navigate('/sources/add')} // Navigate to add source page
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

      {/* Filtering Options  */}
      <Box sx={{ display: 'flex', gap: 2, mb: 2 }}>
        <FormControl size="small"> {/* Type filter dropdown */}
          <StyledSelect
            value={typeFilter}
            onChange={(e) => setTypeFilter(e.target.value as string)}
            IconComponent={KeyboardArrowDownIcon}
            displayEmpty
          >
            <MenuItem value="all">Type</MenuItem>
            {Object.entries(QUERY_ENGINE_TYPES).map(([key, value]) => (  // Map through types to create menu items
              <MenuItem key={key} value={key}>{value}</MenuItem>
            ))}
          </StyledSelect>
        </FormControl>

        <FormControl size="small"> {/* Job status filter dropdown */}
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


        <FormControl size="small"> {/* Created date filter dropdown (currently placeholder) */}
          <StyledSelect
            value="created"
            IconComponent={KeyboardArrowDownIcon}
            displayEmpty
          >
            <MenuItem value="created">Created</MenuItem>
          </StyledSelect>
        </FormControl>

        {/* Rows per page and count (currently not functional) */}
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

      {/* Table to display Sources */}
      <TableContainer sx={{ backgroundColor: 'transparent' }}>
        <Table>
          <TableHead> {/* Table header */}
            <TableRow>
              <StyledTableCell padding="checkbox"> {/* Checkbox for selecting all */}
                <Checkbox
                  checked={selectedSources.length === sources.length} // Check if all sources are selected
                  indeterminate={selectedSources.length > 0 && selectedSources.length < sources.length} // Show indeterminate state if some are selected
                  onChange={handleSelectAll} // Handle select all
                  sx={{ color: 'white' }}
                />
              </StyledTableCell>
              <StyledTableCell>Name</StyledTableCell> {/* Header cells */}
              <StyledTableCell>Job Status</StyledTableCell>
              <StyledTableCell>Type</StyledTableCell>
              <StyledTableCell>Created</StyledTableCell>
              <StyledTableCell align="right"></StyledTableCell> {/* Placeholder for actions/menu */}

            </TableRow>
          </TableHead>
          <TableBody> {/* Table body */}
            {sources.map((source) => (  // Map over sources to create rows
              <StyledTableRow key={source.id}>
                <StyledTableCell padding="checkbox"> {/* Checkbox for individual selection */}
                  <Checkbox
                    checked={selectedSources.includes(source.id)}
                    onChange={() => handleSelectSource(source.id)}
                    sx={{ color: 'white' }}

                  />
                </StyledTableCell>
                <StyledTableCell>{source.name}</StyledTableCell> {/* Data cells */}
                <StyledTableCell>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    {getStatusIcon('Success')} {/* Get the status icon based on 'success' state */}
                    Success {/* Currently hardcoded to success */}
                  </Box>
                </StyledTableCell>
                <StyledTableCell>
                  {QUERY_ENGINE_TYPES[source.query_engine_type as keyof typeof QUERY_ENGINE_TYPES] || source.query_engine_type}  {/* Display query engine type */}
                </StyledTableCell>
                <StyledTableCell>{new Date(source.created_time).toLocaleDateString()}</StyledTableCell> {/* Format and display the date */}

                <StyledTableCell align="right">
                  <IconButton size="small" sx={{ color: 'white' }}> {/* More options menu (currently placeholder) */}
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

export default Sources; // Export the component
