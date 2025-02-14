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
  FormControl,
  Icon,
  Menu,
  ListItemIcon
} from '@mui/material';
import { styled } from '@mui/material/styles'; // Import styling utilities from Material-UI
import { QueryEngine, QUERY_ENGINE_TYPES } from '../lib/types'; // Import types for query engines
import { useAuth } from '../contexts/AuthContext'; // Import authentication context
import { deleteQueryEngine, fetchAllEngines } from '../lib/api'; // Import API function for fetching engines
import AddIcon from '@mui/icons-material/Add'; // Import icons from Material-UI
import MoreVertIcon from '@mui/icons-material/MoreVert';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import ErrorIcon from '@mui/icons-material/Error';
import SyncIcon from '@mui/icons-material/Sync';
import KeyboardArrowDownIcon from '@mui/icons-material/KeyboardArrowDown';
import { useNavigate } from 'react-router-dom'; // Import navigation hook
import { ChevronLeft, ChevronRight, FirstPage, LastPage } from '@mui/icons-material';
import VisibilityIcon from "@mui/icons-material/Visibility";
import EditIcon from "@mui/icons-material/Edit";
import DeleteIcon from "@mui/icons-material/Delete";
import ContentCopyIcon from "@mui/icons-material/ContentCopy";
import { Dialog, DialogActions, DialogContent, DialogContentText, DialogTitle} from "@mui/material";



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
  // const [jobStatus, setJobStatus] = useState('); // State for the job status filter
  const [rowsPerPage, setRowsPerPage] = useState(3); // Rows per page state (not used for actual pagination yet)
  const navigate = useNavigate(); // For navigation
  const [menuAnchor, setMenuAnchor] = useState<null | HTMLElement>(null);
  const [selectedSource, setSelectedSource] = useState<null | string>(null);


  const handleMenuOpen = (event: React.MouseEvent<HTMLButtonElement>, sourceId: string) => {
    setMenuAnchor(event.currentTarget);
    setSelectedSource(sourceId);
  };
  
  const handleMenuClose = () => {
    setMenuAnchor(null);
    setSelectedSource(null);
  };

  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);

const handleDeleteClick = (sourceId: string) => {
  setSelectedSource(sourceId); // Store only the source ID
  setDeleteDialogOpen(true); // Open confirmation dialog
};

const confirmDeleteSource = async () => {
  if (!user?.token || !selectedSource) return;

  try {
    const success = await deleteQueryEngine(user.token)({ id: selectedSource } as QueryEngine);
    if (success) {
      setSources((prevSources) => prevSources.filter((s) => s.id !== selectedSource)); // ✅ Remove deleted source
      console.log(`Deleted source: ${selectedSource}`);
    } else {
      console.error("Failed to delete source");
    }
  } catch (err) {
    console.error("Error deleting source:", err);
  } finally {
    setDeleteDialogOpen(false); // Close the dialog
    setSelectedSource(null); // Clear selected source
  }
};

  
  
  useEffect(() => {
    const loadSources = async () => {
      if (!user?.token) return;
  
      try {
        const engines = await fetchAllEngines(user.token)();
        console.log("Fetched sources:", engines); // Debugging
  
        if (engines) {
          setSources(engines);
        }
      } catch (err) {
        setError("Failed to load sources");
        console.error("Error loading sources:", err);
      } finally {
        setLoading(false);
      }
    };
  
    loadSources();
  }, [user]); // Dependency array
  

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

  const onClickFirstPage = () => { }
  const onClickPreviousPage = () => { }
  const onClickNextPage = () => { }
  const onClickLastPage = () => { }

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
          {/* <Typography variant="body2" sx={{ color: '#888' }}>
            Brief description of what Sources means and how they're used
          </Typography> */}
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
          {/* Type Filter */}
          <Box>
            <Typography variant="body2" sx={{ color: "white", mb: 0.5 }}>
              Type
            </Typography>
            <FormControl size="small">
              <StyledSelect
                value={typeFilter}
                onChange={(e) => setTypeFilter(e.target.value as string)}
                IconComponent={KeyboardArrowDownIcon}
                displayEmpty
                MenuProps={{
                  PaperProps: {
                    sx: {
                      backgroundColor: "#242424",
                    },
                  },
                }}
              >
                <MenuItem value="all">All</MenuItem>
                {Object.entries(QUERY_ENGINE_TYPES).map(([key, value]) => (
                  <MenuItem key={key} value={key}>{value}</MenuItem>
                ))}
              </StyledSelect>
            </FormControl>
          </Box>

          {/* Job Status Filter */}
          <Box>
            <Typography variant="body2" sx={{ color: "white", mb: 0.5 }}>
              Job Status
            </Typography>
            <FormControl size="small">
              <StyledSelect
                value={jobStatusFilter || "Job Status"}
                onChange={(e) => setJobStatusFilter(e.target.value as string)}
                IconComponent={KeyboardArrowDownIcon}
                displayEmpty
                MenuProps={{
                  PaperProps: {
                    sx: {
                      backgroundColor: "#242424",
                    },
                  },
                }}
              >
                <MenuItem value="all">All</MenuItem>
                <MenuItem value="success">Success</MenuItem>
                <MenuItem value="failed">Failed</MenuItem>
                <MenuItem value="active">Active</MenuItem>
              </StyledSelect>
            </FormControl>
          </Box>

          {/* Created Date Filter */}
          <Box>
            <Typography variant="body2" sx={{ color: "white", mb: 0.5 }}>
              Created Date
            </Typography>
            <FormControl size="small">
              <StyledSelect
                value="created"
                IconComponent={KeyboardArrowDownIcon}
                displayEmpty
                MenuProps={{
                  PaperProps: {
                    sx: {
                      backgroundColor: "#242424",
                    },
                  },
                }}
              >
                <MenuItem value="created">Created</MenuItem>
              </StyledSelect>
            </FormControl>
          </Box>
        {/* Rows per page and count (currently not functional) */}
        <Box sx={{ marginLeft: 'auto', display: 'flex', alignItems: 'center', gap: 2 }}>
          <Typography sx={{ color: 'white' }}>Rows per page</Typography>
          <StyledSelect
            value={rowsPerPage}
            onChange={(e) => setRowsPerPage(Number(e.target.value))}
            IconComponent={KeyboardArrowDownIcon}
            MenuProps={{
              PaperProps: {
                sx: {
                  backgroundColor: "#242424",
                },
              },
            }}
          >
            <MenuItem value={3}>3</MenuItem>
            <MenuItem value={5}>5</MenuItem>
            <MenuItem value={10}>10</MenuItem>
          </StyledSelect>
          <Typography sx={{ color: 'white' }}>1-3 of 3</Typography>
          <IconButton sx={{ color: 'white' }} onClick={onClickFirstPage}>
            <FirstPage />
          </IconButton>
          <IconButton sx={{ color: 'white' }} onClick={onClickPreviousPage}>
            <ChevronLeft />
          </IconButton>
          <IconButton sx={{ color: 'white' }} onClick={onClickNextPage}>
            <ChevronRight />
          </IconButton>
          <IconButton sx={{ color: 'white' }} onClick={onClickLastPage}>
            <LastPage />
          </IconButton>
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
              <StyledTableCell align="left"></StyledTableCell> {/* Placeholder for actions/menu */}

            </TableRow>
          </TableHead>
          <TableBody>
              {sources
                .filter((source) => {
                  // Apply job status filtering
                  const jobStatusMatches =
                    jobStatusFilter === "all" || jobStatusFilter === "success" || jobStatusFilter === "failed" || jobStatusFilter === "active";
            
                  // Apply type filtering
                  const typeMatches =
                    typeFilter === "all" ||
                    QUERY_ENGINE_TYPES[source.query_engine_type as keyof typeof QUERY_ENGINE_TYPES] === typeFilter;
            
                  return jobStatusMatches && typeMatches; // Ensure both filters apply
                })
              .map((source) => (
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
                      {/* {getStatusIcon(source.status)} */}
                      {/* {source.status} */}
                    </Box>
                  </StyledTableCell>
                  <StyledTableCell>
                    {QUERY_ENGINE_TYPES[source.query_engine_type as keyof typeof QUERY_ENGINE_TYPES] ||
                      source.query_engine_type}
                  </StyledTableCell>
                  <StyledTableCell>{new Date(source.created_time).toLocaleDateString()}</StyledTableCell>
                  
                  {/* Three-dot menu */}
                    <StyledTableCell align="left">
                      <IconButton
                        size="small"
                        sx={{ color: "white" }}
                        onClick={(e) => handleMenuOpen(e, source.id)}
                      >
                        <MoreVertIcon />
                      </IconButton>

                      {/* Dropdown Menu */}
                      <Menu
                        anchorEl={menuAnchor}
                        open={Boolean(menuAnchor) && selectedSource === source.id}
                        onClose={handleMenuClose}
                        PaperProps={{
                          sx: {
                            backgroundColor: "#242424",
                            color: "white",
                          },
                        }}
                      >
                        <MenuItem onClick={() => console.log("Copy Job Status", typeFilter)}>
                          <ListItemIcon>
                            <ContentCopyIcon sx={{ color: "white" }} />
                          </ListItemIcon>
                          Copy Job Status
                        </MenuItem>
                        <MenuItem onClick={() => console.log("View Source", source.id)}>
                          <ListItemIcon>
                            <VisibilityIcon sx={{ color: "white" }} />
                          </ListItemIcon>
                          View Source
                        </MenuItem>
                        <MenuItem onClick={() => console.log("Edit Source", source.id)}>
                          <ListItemIcon>
                            <EditIcon sx={{ color: "white" }} />
                          </ListItemIcon>
                          Edit Source
                        </MenuItem>
                        <MenuItem onClick={() => handleDeleteClick(source.id)}>
                          <ListItemIcon>
                            <DeleteIcon sx={{ color: "red" }} />
                          </ListItemIcon>
                          Delete Source
                        </MenuItem>

                      </Menu>
                    </StyledTableCell>
                </StyledTableRow>
              ))}
          </TableBody>
        </Table>
        {/* 🔹 Delete Confirmation Dialog - Add This Here */}
    <Dialog open={deleteDialogOpen} onClose={() => setDeleteDialogOpen(false)}>
      <DialogTitle>Confirm Deletion</DialogTitle>
      <DialogContent>
        <DialogContentText>
          Are you sure you want to delete this source? This action cannot be undone.
        </DialogContentText>
      </DialogContent>
      <DialogActions>
        <Button onClick={() => setDeleteDialogOpen(false)} color="primary">
          Cancel
        </Button>
        <Button onClick={confirmDeleteSource} color="error">
          Confirm
        </Button>
      </DialogActions>
    </Dialog>
      </TableContainer>
    </Box>
  );
};

export default Sources; // Export the component
