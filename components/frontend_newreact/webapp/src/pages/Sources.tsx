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
  Tooltip,
  Button,
  Select,
  MenuItem,
  Checkbox,
  FormControl,
  Icon,
  Menu,
  ListItemIcon,
  SelectChangeEvent
} from '@mui/material';
import { styled } from '@mui/material/styles'; // Import styling utilities from Material-UI
import { QueryEngine, QUERY_ENGINE_TYPES } from '../lib/types'; // Import types for query engines
import { useAuth } from '../contexts/AuthContext'; // Import authentication context
import { deleteQueryEngine, fetchAllEngines, getEngineJobStatus } from '../lib/api'; // Import API function for fetching engine
import { jobsEndpoint } from '../lib/api'
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
import { Dialog, DialogActions, DialogContent, DialogContentText, DialogTitle, List, ListItem, ListItemText} from "@mui/material";
import axios from 'axios';



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

interface SourcesProps {
  onAddSourceClick: () => void;
  onEditSourceClick: (sourceId: string) => void;
}

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

const Sources = ({ onAddSourceClick, onEditSourceClick }: SourcesProps) => {
  const [sources, setSources] = useState<QueryEngineWithStatus[]>([]);// State for storing the list of sources
  const { user } = useAuth(); // Get the authenticated user from context
  const [loading, setLoading] = useState(true); // Loading state
  const [error, setError] = useState<string | null>(null); // Error state
  const [selectedSources, setSelectedSources] = useState<string[]>([]); // State for tracking selected sources
  const [typeFilter, setTypeFilter] = useState('all'); // State for the type filter
  const [jobStatusFilter, setJobStatusFilter] = useState('all'); // State for the job status filter
  // const [jobStatus, setJobStatus] = useState('); // State for the job status filter
  const navigate = useNavigate(); // For navigation
  const [menuAnchor, setMenuAnchor] = useState<null | HTMLElement>(null);
  const [selectedSource, setSelectedSource] = useState<null | string>(null);
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [sourcesToDelete, setSourcesToDelete] = useState<string[]>([]);
  const [updateSourceId, setUpdateSourceId] = useState<string | null>(null);


  const handleMenuOpen = (event: React.MouseEvent<HTMLButtonElement>, sourceId: string) => {
    setMenuAnchor(event.currentTarget);
    setSelectedSource(sourceId);
  };
  
  const handleMenuClose = () => {
    setMenuAnchor(null);
    setSelectedSource(null);
  };

  const handleEditClick = (sourceId: string) => {
    onEditSourceClick(sourceId); // Call the onEditSourceClick prop
    handleMenuClose(); // Close the menu after clicking
};

  const handleDeleteClick = (sourceId: string) => {
    if (selectedSources.includes(sourceId)) {
        setSourcesToDelete([...selectedSources]); // Bulk delete from checkbox selection
    } else {
        setSourcesToDelete([sourceId]); // Single delete from menu
    }
    setDeleteDialogOpen(true);
  };

  const handleBulkDeleteClick = () => {
    setSourcesToDelete([...selectedSources]); // Set sources to delete
    setDeleteDialogOpen(true);                  // Open the dialog
  };

  const confirmDeleteSources = async () => {
    if (!user?.token) return;

    try {

      const deletePromises = sourcesToDelete.map(async (sourceId) => {
        const success = await deleteQueryEngine(user.token)({ id: sourceId } as QueryEngine);
        if (!success) {
          console.error(`Failed to delete source: ${sourceId}`);
        }
        return success; // Return true if success, false if failed
      });
  
      const results = await Promise.all(deletePromises); // Wait for all deletions
      const allSuccessful = results.every(result => result); // Check if all were successful


      if (allSuccessful) {
        setSources((prevSources) => prevSources.filter((s) => !sourcesToDelete.includes(s.id))); // Remove deleted sources
        setSelectedSources([]);
        console.log(`Deleted sources: ${sourcesToDelete.join(", ")}`);
      } else {
          console.error("Some sources could not be deleted.");
      }
    } catch (err) {
      console.error("Error deleting sources:", err);
    } finally {
      setDeleteDialogOpen(false);
      setSourcesToDelete([]);
      setSelectedSource(null);
    }
  };

interface QueryEngineWithStatus extends QueryEngine {
  status: "active" | "success" | "failed" | "unknown";
}

interface JobStatusResponse {
  name: string;
  status: "active" | "succeeded" | "failed";
  input_data: {
    query_engine: string;
  };
}

useEffect(() => {
  if (!user?.token) return;

  let pollIntervalId: number | null = null;

  /**
   * Fetch all query engines and initialize them with "unknown" status.
   */
  const loadSources = async () => {
    try {
      const engines = await fetchAllEngines(user.token)();
      console.log("Fetched sources:", engines);

      if (engines) {
        setSources((prevSources) =>
          engines.map((engine) => {
            const existingSource = prevSources.find((s) => s.id === engine.id);
            return {
              ...engine,
              status: existingSource?.status ?? "unknown",
            };
          })
        );
      }
    } catch (error) {
      setError("Failed to load sources");
      console.error("Error loading sources:", error);
    } finally {
      setLoading(false);
    }
  };

  /**
   * Fetch job statuses and update sources.
   */
  const updateJobStatuses = async () => {
    let jobRunning = false;

    try {
      // Fetch all job statuses in one API call
      const response = await axios.get<{ data: JobStatusResponse[] }>(
        `${jobsEndpoint}/jobs/query_engine_build`,
        {
          headers: { Authorization: `Bearer ${user.token}` },
        }
      );

      const jobsData = response.data.data; // Ensure correct data extraction
      console.log("Fetched job statuses:", jobsData);

      setSources((prevSources) =>
        prevSources.map((source) => {
          // Find the job for this engine using the correct ID field
          const job = jobsData.find(
            (j: JobStatusResponse) => j.input_data.query_engine === source.name
          );

          if (job) {
            jobRunning = job.status === "active"; // If any job is still running, continue polling
            return {
              ...source,
              status:
                job.status === "succeeded"
                  ? "success"
                  : job.status === "failed"
                  ? "failed"
                  : job.status, // Preserve existing statuses
            };
          } else {
            console.warn(`No job found for ${source.name} (${source.id}).`);
            return { ...source, status: "failed" }; // Mark missing jobs as "failed"
          }
        })
      );

      // Stop polling if no jobs are running
      if (!jobRunning && pollIntervalId !== null) {
        clearInterval(pollIntervalId);
        pollIntervalId = null;
      }
    } catch (error) {
      console.error("Error updating job statuses:", error);
    }
  };

  /**
   * Starts polling job statuses every second.
   */
  const startPolling = () => {
    if (!pollIntervalId) {
      pollIntervalId = window.setInterval(updateJobStatuses, 1000);
    }
  };

  loadSources().then(startPolling);

  return () => {
    if (pollIntervalId !== null) {
      clearInterval(pollIntervalId);
      pollIntervalId = null;
    }
  };
}, [user]); // Dependency: Only runs when user changes



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

  const getStatusIcon = (status: string | undefined) => {
    switch (status) {
      case 'success':
        return <CheckCircleIcon sx={{ color: '#4CAF50' }} />;
      case 'failed':
        return <ErrorIcon sx={{ color: '#f44336' }} />;
      case 'active':
        return <SyncIcon sx={{ color: '#2196F3' }} />;
      default: // Handle "unknown" and undefined
        return null; 
    }
  };

  const [currentPage, setCurrentPage] = useState(1);
  const [rowsPerPage, setRowsPerPage] = useState(3); // Default value

  const totalRows = sources.length;
  const totalPages = Math.ceil(totalRows / rowsPerPage);

  // Get paginated data
  const paginatedSources = sources.slice(
    (currentPage - 1) * rowsPerPage,
    currentPage * rowsPerPage
  );

  // Page navigation handlers
  const onClickFirstPage = () => setCurrentPage(1);
  const onClickPreviousPage = () => setCurrentPage((prev) => Math.max(prev - 1, 1));
  const onClickNextPage = () => setCurrentPage((prev) => Math.min(prev + 1, totalPages));
  const onClickLastPage = () => setCurrentPage(totalPages);

  // Handle change in rows per page
  const handleRowsPerPageChange = (event: SelectChangeEvent<unknown>) => {
    setRowsPerPage(Number(event.target.value)); // Explicitly cast value to number
    setCurrentPage(1); // Reset to first page when rows per page changes
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
          <Typography variant="h5" sx={{ color: 'white', mb: 1 }} className="font-poppins">Sources</Typography>
          {/* <Typography variant="body2" sx={{ color: '#888' }}>
            Brief description of what Sources means and how they're used
          </Typography> */}
        </Box>
        {/* Add source button */}
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={onAddSourceClick} // Call the prop function passed from Main.tsx
          sx={{
            backgroundColor: '#4a90e2',
            '&:hover': { backgroundColor: '#357abd' },
            borderRadius: '20px',
            textTransform: 'none'
          }}
          className="font-poppins capitalize p-3 rounded-3xl bg-blue-300 text-blue-900"
        >
          Add Source
        </Button>
      </Box>

      {/* Filtering/Bulk Delete Options */}
      <Box sx={{ display: 'flex', gap: 2, mb: 2 }}>
        {selectedSources.length > 0 ? ( // Conditionally render bulk delete button
          <Button
            variant="contained"
            color="error"
            startIcon={<DeleteIcon />}
            onClick={handleBulkDeleteClick}
            sx={{ borderRadius: '20px', textTransform: 'none' }}
          >
            Delete
          </Button>
        ): (
          <>
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
          </>
        )}

        {/* Pagination Controls */}
          <Box sx={{ marginLeft: 'auto', display: 'flex', alignItems: 'center', gap: 2 }}>
            <Typography sx={{ color: 'white' }}>Rows per page</Typography>
            <StyledSelect
              value={rowsPerPage}
              onChange={handleRowsPerPageChange}
              IconComponent={KeyboardArrowDownIcon}
              MenuProps={{ PaperProps: { sx: { backgroundColor: "#242424" } } }}
            >
              <MenuItem value={3}>3</MenuItem>
              <MenuItem value={5}>5</MenuItem>
              <MenuItem value={10}>10</MenuItem>
            </StyledSelect>
            <Typography sx={{ color: 'white' }}>
              {`${(currentPage - 1) * rowsPerPage + 1} - ${Math.min(currentPage * rowsPerPage, totalRows)} of ${totalRows}`}
            </Typography>
            <IconButton sx={{ color: 'white' }} onClick={onClickFirstPage} disabled={currentPage === 1}>
              <FirstPage />
            </IconButton>
            <IconButton sx={{ color: 'white' }} onClick={onClickPreviousPage} disabled={currentPage === 1}>
              <ChevronLeft />
            </IconButton>
            <IconButton sx={{ color: 'white' }} onClick={onClickNextPage} disabled={currentPage === totalPages}>
              <ChevronRight />
            </IconButton>
            <IconButton sx={{ color: 'white' }} onClick={onClickLastPage} disabled={currentPage === totalPages}>
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
              .filter((source) =>
                (jobStatusFilter === "all" || source.status === jobStatusFilter) &&
                (typeFilter === "all" || source.query_engine_type === typeFilter)
            )
            
              .slice((currentPage - 1) * rowsPerPage, currentPage * rowsPerPage) // ⬅️ Pagination applied here
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
                      {getStatusIcon(source.status)}
                      {source.status ?? "unknown"} {/* Display text as well (handle undefined) */}
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
                        anchorOrigin={{
                          vertical: "top",
                          horizontal: "right",
                        }}
                        transformOrigin={{
                          vertical: "top",
                          horizontal: "right",
                        }}
                      >
                        <MenuItem
                          onClick={() => {
                            const docUrl = source?.doc_url ?? undefined; // Convert null to undefined
                            if (docUrl) {
                              window.open(docUrl, "_blank");
                            } else {
                              console.warn("No valid document URL available.");
                            }
                          }}
                        >
                          <ListItemIcon>
                            <VisibilityIcon sx={{ color: "white" }} />
                          </ListItemIcon>
                          View Source
                        </MenuItem>
                        <MenuItem onClick={() => handleEditClick(source.id)}> {/* Call handleEditClick */}
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
        <Dialog open={deleteDialogOpen} onClose={() => {setDeleteDialogOpen(false); setSourcesToDelete([]); setSelectedSource(null);}}>
        <DialogTitle>Confirm Deletion</DialogTitle>
        <DialogContent>
          <DialogContentText>
            Are you sure you want to delete the following source(s)? This action cannot be undone.
          </DialogContentText>
          <List>
            {sourcesToDelete.map((sourceId) => {
              const sourceName = sources.find(s => s.id === sourceId)?.name || sourceId;
              return (
                <ListItem key={sourceId}>
                  <ListItemText primary={sourceName} />
                </ListItem>
              );
            })}
          </List>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => {setDeleteDialogOpen(false); setSourcesToDelete([]); setSelectedSource(null);}} color="primary">
            Cancel
          </Button>
          <Button onClick={confirmDeleteSources} color="error">
            Confirm
          </Button>
        </DialogActions>
      </Dialog>
        </TableContainer>
      </Box>
  );
};

export default Sources; // Export the component
