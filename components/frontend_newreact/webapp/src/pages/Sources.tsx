import { useCallback, useEffect, useState } from 'react'; // Import necessary hooks for state management and side effects
import {  // Import Material-UI components for building the UI
  Box,
  Typography,
  Table,
  TableCell,
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
  SelectChangeEvent,
} from '@mui/material';
import { styled } from '@mui/material/styles'; // Import styling utilities from Material-UI
import { QueryEngine, QUERY_ENGINE_TYPES } from '../lib/types'; // Import types for query engines
import { useAuth } from '../contexts/AuthContext'; // Import authentication context
import { deleteQueryEngine, fetchAllEngines, fetchAllEngineJobs, updateQueryEngine } from '../lib/api';
import { jobsEndpoint } from '../lib/api'
import AddIcon from '@mui/icons-material/Add'; // Import icons from Material-UI
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import ErrorIcon from '@mui/icons-material/Error';
import SyncIcon from '@mui/icons-material/Sync';
import KeyboardArrowDownIcon from '@mui/icons-material/KeyboardArrowDown';
import { useNavigate } from 'react-router-dom'; // Import navigation hook
import { ChevronLeft, ChevronRight, EditNote, FirstPage, Info, LastPage, Close } from '@mui/icons-material';
import DeleteIcon from "@mui/icons-material/Delete";
import ContentCopyIcon from "@mui/icons-material/ContentCopy";
import { Dialog, DialogActions, DialogContent, DialogContentText, DialogTitle, List, ListItem, ListItemText, TextField } from "@mui/material";
import axios from 'axios';
import ClearIcon from '@mui/icons-material/Clear';
import SourcesTable from '../components/SourcesTable';
import CloseIcon from '@mui/icons-material/Close';


const STYLED_WHITE = 'white';

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
  onEditClick: (sourceId: string) => void;
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

const Sources = ({ onAddSourceClick, onEditClick }: SourcesProps) => {
  const [sources, setSources] = useState<QueryEngineWithStatus[]>([]);// State for storing the list of sources
  const { user } = useAuth(); // Get the authenticated user from context
  const [loading, setLoading] = useState(true); // Loading state
  const [error, setError] = useState<string | null>(null); // Error state
  const [selectedSources, setSelectedSources] = useState<string[]>([]); // State for tracking selected sources
  const [typeFilter, setTypeFilter] = useState('all'); // State for the type filter
  const [jobStatusFilter, setJobStatusFilter] = useState('all'); // State for the job status filter
  const navigate = useNavigate(); // For navigation
  const [menuAnchor, setMenuAnchor] = useState<null | HTMLElement>(null);
  const [selectedSource, setSelectedSource] = useState<null | string>(null);
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [sourcesToDelete, setSourcesToDelete] = useState<string[]>([]);
  const [isEditModalOpen, setIsEditModalOpen] = useState(false);
  const [sourceToEdit, setSourceToEdit] = useState<QueryEngine | null>(null);
  const [editedName, setEditedName] = useState('');
  const [editedDescription, setEditedDescription] = useState('');
  const [currentPage, setCurrentPage] = useState(1);
  const [rowsPerPage, setRowsPerPage] = useState(10); // Default value
  const [isViewModalOpen, setIsViewModalOpen] = useState(false);
  const [sourceToView, setSourceToView] = useState<QueryEngine | null>(null);
  const [isEditDisabled, setIsEditDisabled] = useState(false);

  const handleMenuClose = () => {
    setMenuAnchor(null);
    setSelectedSource(null);
  };

  const handleEditClick = (sourceId: string) => {
    const source = sources.find(s => s.id === sourceId);
    // Disable edit when source is active
    if (source && source.status === "active") {
      return;
    }
    if (source) {
      setSourceToEdit(source);
      setEditedName(source.name);
      setEditedDescription(source.description || ''); // Ensure a default empty string
      setIsEditModalOpen(true);
    }
    handleMenuClose(); // Close the menu after clicking
  };

  const handleViewClick = (sourceId: string) => {
    const source = sources.find(s => s.id === sourceId);
    if (source) {
      setSourceToView(source);
      setIsViewModalOpen(true);
    }
    handleMenuClose();
  };
  const handleViewModalClose = () => {
    setIsViewModalOpen(false); // Close the modal
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

  const handleEditModalClose = () => {
    setIsEditModalOpen(false); // Close the modal
  };

  const handleSaveEdit = async () => {
    if (!user?.token || !sourceToEdit) {
      console.error("User token or source to edit is missing.");
      return;
    }

    const updatedSource: QueryEngine = {
      ...sourceToEdit,
      name: editedName.trim(),
      description: editedDescription.trim(),
    };

    console.log("Updating Source:", updatedSource);

    try {
      await updateQueryEngine(user.token)(updatedSource);
      setSources((prevSources) =>
        prevSources.map(s => s.id === updatedSource.id ? { ...s, name: updatedSource.name, description: updatedSource.description } : s)
      );

      setIsEditModalOpen(false);
    } catch (error) {
      console.error("Error updating source:", error);
    }
  };

  const handleNameChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    setEditedName(event.target.value);
  };

  const confirmDeleteSources = async () => {
    if (!user?.token) return;

    try {
      setDeleteDialogOpen(false);
      console.log("delete modal should go away:");
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
      console.log('should be closing dialog');
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
    let refreshIntervalId: number | null = null;

    /**
     * Fetch all query engines and initialize them with status.
     */
    const loadSources = async () => {
      try {
        setLoading(true);
        setError(null);

        // Fetch both existing engines and build jobs
        const [engines, buildJobs] = await Promise.all([
          fetchAllEngines(user.token)(),
          fetchAllEngineJobs(user.token)()
        ]);

        console.log("Fetched sources:", engines);
        console.log("Fetched build jobs:", buildJobs);

        let combinedSources: QueryEngineWithStatus[] = [];

        // First process existing engines
        if (engines) {
          combinedSources = engines.map((engine) => {
            // Check if there's an active build job for this engine
            const activeJob = buildJobs?.find(job =>
              job.status === "active" &&
              job.input_data.query_engine === engine.name
            );

            return {
              ...engine,
              // If there's an active job, status should be "active", otherwise "success"
              status: activeJob ? "active" : "success",
            };
          });
        }

        // Add active build jobs that aren't already in the engines list
        if (buildJobs) {
          const activeJobs = buildJobs.filter(job =>
            job.status === "active" &&
            (!engines || !engines.some(engine => engine.name === job.input_data.query_engine))
          );

          // Convert build jobs to QueryEngine format and add to sources
          activeJobs.forEach(job => {
            // Create a temporary QueryEngine object from the job data
            const tempEngine: QueryEngineWithStatus = {
              id: job.id, // Use job ID temporarily
              name: job.input_data.query_engine,
              description: job.input_data.description || "",
              query_engine_type: job.input_data.query_engine_type,
              doc_url: job.input_data.doc_url,
              embedding_type: job.input_data.embedding_type,
              vector_store: job.input_data.vector_store,
              created_time: job.created_time,
              created_by: job.created_by,
              last_modified_time: job.last_modified_time,
              last_modified_by: job.last_modified_by,
              archived_at_timestamp: null,
              archived_by: "",
              deleted_at_timestamp: null,
              deleted_by: "",
              llm_type: null,
              parent_engine_id: "",
              user_id: job.input_data.user_id,
              is_public: false,
              index_id: null,
              index_name: null,
              endpoint: null,
              manifest_url: job.input_data.params?.manifest_url || null,
              is_multimodal: false,
              params: {
                is_multimodal: "false",
                ...job.input_data.params
              },
              depth_limit: parseInt(job.input_data.params?.depth_limit || "3"),
              chunk_size: parseInt(job.input_data.params?.chunk_size || "1024"),
              agents: job.input_data.params?.agents ? JSON.parse(job.input_data.params.agents) : [],
              child_engines: job.input_data.params?.associated_engines ? JSON.parse(job.input_data.params.associated_engines) : [],
              //is_multimodal: job.input_data.params?.is_multimodal === "True",
              status: "active"  // Always set active jobs as "active"
            };

            combinedSources.push(tempEngine);
          });
        }

        setSources(combinedSources);

        // If there are active jobs, start polling
        const hasActiveJobs = buildJobs && buildJobs.some(job => job.status === "active");
        if (hasActiveJobs) {
          console.log("Starting polling")
          startPolling();
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

        const jobsData = response.data.data;
        console.log("Fetched job statuses:", jobsData);

        // Check if any jobs have completed
        const completedJobs = jobsData.filter(job =>
          (job.status === "succeeded" || job.status === "failed") &&
          sources.some(source => source.name === job.input_data.query_engine && source.status === "active")
        );

        // If any jobs completed, refresh the entire source list
        if (completedJobs.length > 0) {
          console.log("Jobs completed, refreshing source list:", completedJobs);
          loadSources();
          return;
        }

        setSources((prevSources) =>
          prevSources.map((source) => {
            // Find the job for this engine
            const job = jobsData.find(
              (j: JobStatusResponse) => j.input_data.query_engine === source.name
            );

            if (job) {
              jobRunning = job.status === "active" || jobRunning;

              // If job is active, always show as active
              if (job.status === "active") {
                return {
                  ...source,
                  status: "active"
                };
              }

              return {
                ...source,
                status: job.status === "succeeded" ? "success" : "failed"
              };
            }

            // If no job found but source was previously active, keep as active
            if (source.status === "active") {
              return source;
            }

            return source; // Keep existing status
          })
        );

      } catch (error) {
        console.error("Error updating job statuses:", error);
      }
    };

    /**
     * Starts polling job statuses every second.
     */
    const startPolling = () => {
      if (!pollIntervalId) {
        // Clear any existing interval first to prevent duplicates
        if (pollIntervalId !== null) {
          clearInterval(pollIntervalId);
        }
        pollIntervalId = window.setInterval(updateJobStatuses, 5000);
        console.log("Started polling for job status updates");
      }
    };

    /**
     * Start periodic refresh of all sources
     * This ensures we catch new sources created by other users
     * and completed jobs that might have been missed
     */
    const startPeriodicRefresh = () => {
      if (!refreshIntervalId) {
        // Clear any existing interval first
        if (refreshIntervalId !== null) {
          clearInterval(refreshIntervalId);
        }
        // Refresh every 10 seconds
        refreshIntervalId = window.setInterval(() => {
          console.log("Performing periodic refresh of all sources");
          loadSources();
        }, 10000); // 10 seconds
        console.log("Started periodic refresh of all sources");
      }
    };

    // Initial load of sources
    loadSources();

    // Set up polling immediately to check for any active jobs
    startPolling();

    // Start periodic refresh to catch new sources and completed jobs
    startPeriodicRefresh();

    return () => {
      // Clean up all intervals when component unmounts
      if (pollIntervalId !== null) {
        clearInterval(pollIntervalId);
        console.log("Stopped polling for job status updates");
      }

      if (refreshIntervalId !== null) {
        clearInterval(refreshIntervalId);
        console.log("Stopped periodic refresh of all sources");
      }
    };
  }, [user]);


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

  // Generate a list of unique job statuses present in the table
  const getUniqueJobStatuses = (): string[] => {
    const uniqueStatuses = new Set<string>();
    sources.forEach(source => uniqueStatuses.add(source.status));
    return Array.from(uniqueStatuses);
  };

  // Generate a list of unique query engine types present in the table
  const getUniqueEngineTypes = (): string[] => {
    const uniqueTypes = new Set<string>();
    sources.forEach(source => uniqueTypes.add(source.query_engine_type));
    return Array.from(uniqueTypes);
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
        ) : (
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
                    <MenuItem key={key} value={key} disabled={!getUniqueEngineTypes().includes(key)}>
                      {value}
                    </MenuItem>
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
                  <MenuItem value="success" disabled={!getUniqueJobStatuses().includes('success')}>
                    Success</MenuItem>
                  <MenuItem value="failed" disabled={!getUniqueJobStatuses().includes('failed')}>
                    Failed</MenuItem>
                  <MenuItem value="active" disabled={!getUniqueJobStatuses().includes('active')}>Active</MenuItem>
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
            value={totalRows === 0 ? 10 : rowsPerPage}  // Reset to 10 if no rows exist
            onChange={handleRowsPerPageChange}
            IconComponent={KeyboardArrowDownIcon}
            MenuProps={{ PaperProps: { sx: { backgroundColor: "#242424" } } }}
            disabled={totalRows === 0} // Disable dropdown when no rows exist
          >
            <MenuItem value={10}>10</MenuItem>
            <MenuItem value={20}>20</MenuItem>
            <MenuItem value={50}>50</MenuItem>
          </StyledSelect>

          <Typography sx={{ color: 'white' }}>
            {totalRows === 0
              ? "0 of 0"
              : `${(currentPage - 1) * rowsPerPage + 1} - ${Math.min(currentPage * rowsPerPage, totalRows)} of ${totalRows}`}
          </Typography>

          {/* First Page Button */}
          <IconButton
            sx={{ color: '#C4C7C5', '&.Mui-disabled': { color: '#333' } }}
            onClick={onClickFirstPage}
            disabled={currentPage === 1 || totalRows === 0} // Disable if no rows exist
          >
            <FirstPage />
          </IconButton>

          {/* Previous Page Button */}
          <IconButton
            sx={{ color: '#C4C7C5', '&.Mui-disabled': { color: '#333' } }}
            onClick={onClickPreviousPage}
            disabled={currentPage === 1 || totalRows === 0} // Disable if no rows exist
          >
            <ChevronLeft />
          </IconButton>

          {/* Next Page Button */}
          <IconButton
            sx={{ color: '#C4C7C5', '&.Mui-disabled': { color: '#333' } }}
            onClick={onClickNextPage}
            disabled={currentPage === totalPages || totalRows === 0} // Disable if no rows exist
          >
            <ChevronRight />
          </IconButton>

          {/* Last Page Button */}
          <IconButton
            sx={{ color: '#C4C7C5', '&.Mui-disabled': { color: '#333' } }}
            onClick={onClickLastPage}
            disabled={currentPage === totalPages || totalRows === 0} // Disable if no rows exist
          >
            <LastPage />
          </IconButton>
        </Box>
      </Box>

      {/* Table to display Sources */}
      <SourcesTable
        sources={sources}
        selectedSources={selectedSources}
        onSelectAll={handleSelectAll}
        onSelectSource={handleSelectSource}
        onEditClick={handleEditClick}
        onViewClick={handleViewClick}
        onDeleteClick={handleDeleteClick}
        typeFilter={typeFilter}
        jobStatusFilter={jobStatusFilter}
        currentPage={currentPage}
        rowsPerPage={rowsPerPage}
        isEditDisabled={isEditDisabled}
      />

      {/* Delete Confirmation Dialog */}
      <Dialog
        open={deleteDialogOpen}
        onClose={() => { setDeleteDialogOpen(false); setSourcesToDelete([]); setSelectedSource(null); }}
        PaperProps={{ sx: { backgroundColor: '#333537', position: 'relative' } }}
      >
        {/* Close Button */}
        <IconButton
          onClick={() => setDeleteDialogOpen(false)}
          sx={{ position: 'absolute', top: 8, right: 8, color: 'white' }}
        >
          <CloseIcon />
        </IconButton>

        <DialogTitle sx={{ color: STYLED_WHITE }}>Confirm Deletion</DialogTitle>
        <DialogContent>
          <DialogContentText sx={{ color: 'white' }}>
            Are you sure you want to delete the following source(s)? This action cannot be undone.
          </DialogContentText>
          {sourcesToDelete.length === 1 && (
            <Box sx={{ backgroundColor: '#242424', p: 2, mt: 2, borderRadius: 1 }}>
              <Typography sx={{ color: '#888', mb: 1, display: 'block' }}>Source Name:</Typography>
              <Typography sx={{ color: 'white' }}>{sources.find((s) => s.id === sourcesToDelete[0])?.name}</Typography>
            </Box>
          )}
          {sourcesToDelete.length > 1 && (
            <Box sx={{ backgroundColor: '#242424', p: 2, mt: 2, borderRadius: 1 }}>
              <Typography sx={{ color: '#888', mb: 1, display: 'block' }}>Source Names:</Typography>
              <List sx={{ color: STYLED_WHITE }}>
                {sourcesToDelete.map((sourceId) => {
                  const sourceName = sources.find(s => s.id === sourceId)?.name || sourceId;
                  return (
                    <ListItem key={sourceId} sx={{ borderBottom: '1px solid #888' }}>
                      <ListItemText primary={sourceName} />
                    </ListItem>
                  );
                })}
              </List>
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button
            onClick={() => { setDeleteDialogOpen(false); setSourcesToDelete([]); setSelectedSource(null); }}
            sx={{
              backgroundColor: '#242424',
              color: '#A8C7FA',
              borderRadius: '20px',
              textTransform: 'none',
              '&:hover': { backgroundColor: '#3A3B3C' } // Darker background on hover
            }}
          >
            Cancel
          </Button>
          <Button
            onClick={confirmDeleteSources}
            color="error"
            startIcon={<DeleteIcon />}
            variant="contained"
            sx={{ backgroundColor: '#F2B8B5', borderRadius: '20px', textTransform: 'none', color: '#601410' }}
          >
            Delete {sourcesToDelete.length} {sourcesToDelete.length === 1 ? 'Source' : 'Sources'}
          </Button>
        </DialogActions>
      </Dialog>
      <Dialog open={isEditModalOpen} onClose={handleEditModalClose} PaperProps={{ sx: { width: '100%', maxWidth: '800px', backgroundColor: '#333537' } }}>
        <DialogTitle sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', color: STYLED_WHITE }}>
          Edit Source
          <IconButton onClick={handleEditModalClose}>
            <Close sx={{ color: STYLED_WHITE }} />
          </IconButton>
        </DialogTitle>
        <DialogContent>
          <Box sx={{ mb: 1 }}>
            <Typography variant="caption" sx={{ color: STYLED_WHITE, mb: 1, display: 'block', }}>
              Name
            </Typography>
            <TextField
              fullWidth
              placeholder="Input"
              value={editedName}
              onChange={(e: React.ChangeEvent<HTMLInputElement>) => {
                if (e.target.value.length <= 50) {
                  handleNameChange(e);
                }
              }}
              required
              error={!editedName}
              helperText={!editedName && "Required"}
              InputProps={{
                endAdornment: editedName && (
                  <IconButton size="small" onClick={() => setEditedName('')}>
                    <ClearIcon fontSize="small" sx={{ color: "white" }} />
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
          <Typography variant="caption" sx={{ color: '#888', mb: 4, display: 'block' }}>Name of the Query Engine (can include spaces). {editedName?.length || 0}/50 characters left.</Typography>

          {/* Add Description Field Here */}
          <Box sx={{ mb: 1 }}>
            <Typography variant="caption" sx={{ color: STYLED_WHITE, mb: 1, display: 'block' }}>
              Description
            </Typography>
            <TextField
              fullWidth
              placeholder="Enter a brief description"
              value={editedDescription}
              onChange={(e) => {
                if (e.target.value.length <= 75) {
                  setEditedDescription(e.target.value);
                }
              }}
              InputProps={{
                endAdornment: (
                  <Typography sx={{ color: '#888', mr: 1 }}>
                    {editedDescription?.length || 0}/75
                  </Typography>
                ),
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
          <Typography variant="caption" sx={{ color: '#888', mb: 1, display: 'block' }}>A brief description of this source.</Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleEditModalClose} color="primary">
            Cancel
          </Button>
          <Button onClick={handleSaveEdit} color="primary"
            sx={{
              backgroundColor: '#4a90e2',
              '&:hover': { backgroundColor: '#357abd' },
              borderRadius: '20px',
              textTransform: 'none'
            }}
            className="font-poppins capitalize p-3 rounded-3xl bg-blue-300 text-blue-900">
            Save
          </Button>
        </DialogActions>
      </Dialog>
      <Dialog open={isViewModalOpen} onClose={handleViewModalClose} PaperProps={{ sx: { width: '100%', maxWidth: '800px', backgroundColor: '#333537' } }}>
        <DialogTitle sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', color: STYLED_WHITE }}>
          View Source
          <IconButton onClick={handleViewModalClose}>
            <Close sx={{ color: STYLED_WHITE }} />
          </IconButton>
        </DialogTitle>
        <DialogContent>
          <List sx={{ color: STYLED_WHITE }}>
            <ListItem sx={{ borderBottom: '1px solid #888' }}>
              <ListItemText primary="Name:" secondary={sourceToView?.name} sx={{ color: STYLED_WHITE, '& .MuiListItemText-secondary': { color: STYLED_WHITE } }} />
            </ListItem>
            <ListItem sx={{ borderBottom: '1px solid #888' }}>
              <ListItemText primary="Created:" secondary={sourceToView?.created_time} sx={{ color: STYLED_WHITE, '& .MuiListItemText-secondary': { color: STYLED_WHITE } }} />
            </ListItem>
            <ListItem sx={{ borderBottom: '1px solid #888' }}>
              <ListItemText primary="Data URL:" secondary={sourceToView?.doc_url} sx={{ color: STYLED_WHITE, '& .MuiListItemText-secondary': { color: STYLED_WHITE } }} />
              <IconButton onClick={() => navigator.clipboard.writeText(sourceToView?.doc_url || '')}><ContentCopyIcon sx={{ color: STYLED_WHITE }} /></IconButton>
            </ListItem>
            <ListItem sx={{ display: 'flex', alignItems: 'center', gap: 2, borderBottom: '1px solid #888' }}>
              <Box sx={{ flex: 1 }}>
                <ListItemText primary="Type:" secondary={QUERY_ENGINE_TYPES[sourceToView?.query_engine_type as keyof typeof QUERY_ENGINE_TYPES] || sourceToView?.query_engine_type} sx={{ color: STYLED_WHITE, '& .MuiListItemText-secondary': { color: STYLED_WHITE } }} />
              </Box>
              <Box sx={{ flex: 1 }}>
                <ListItemText primary="MultiModal:" secondary={sourceToView ? (typeof sourceToView.is_multimodal === 'boolean' ? sourceToView.is_multimodal.toString() : "false") : 'N/A'} sx={{ color: STYLED_WHITE, '& .MuiListItemText-secondary': { color: STYLED_WHITE } }} />
              </Box>
            </ListItem>
            <ListItem sx={{ display: 'flex', alignItems: 'center', gap: 2, borderBottom: '1px solid #888' }}>
              <Box sx={{ flex: 1 }}>
                <ListItemText primary="Vector Store:" secondary={sourceToView?.vector_store === 'langchain_pgvector' ? 'PG Vector' : 'Vertex Matching Engine'} sx={{ color: STYLED_WHITE, '& .MuiListItemText-secondary': { color: STYLED_WHITE } }} />
              </Box>
              <Box sx={{ flex: 1 }}>
                <ListItemText primary="Embedding Type:" secondary={sourceToView?.embedding_type.toString()} sx={{ color: STYLED_WHITE, '& .MuiListItemText-secondary': { color: STYLED_WHITE } }} />
              </Box>
            </ListItem>
            <ListItem sx={{ display: 'flex', alignItems: 'center', gap: 2, borderBottom: '1px solid #888' }}>
              <Box sx={{ flex: 1 }}>
                <ListItemText
                  primary="Depth Limit:"
                  secondary={sourceToView ? sourceToView.params?.depth_limit?.toString() : "N/A"}
                  sx={{ color: STYLED_WHITE, '& .MuiListItemText-secondary': { color: STYLED_WHITE } }}
                />
              </Box>
              <Box sx={{ flex: 1 }}>
                <ListItemText
                  primary="Chunk Size:"
                  secondary={sourceToView ? sourceToView.params?.chunk_size?.toString() : "N/A"}
                  sx={{ color: STYLED_WHITE, '& .MuiListItemText-secondary': { color: STYLED_WHITE } }}
                />
              </Box>
            </ListItem>
            <ListItem sx={{ borderBottom: '1px solid #888' }}>
              <ListItemText
                sx={{ color: sourceToView?.agents && sourceToView.agents.length > 0 ? STYLED_WHITE : '#888', '& .MuiListItemText-secondary': { color: sourceToView?.agents && sourceToView.agents.length > 0 ? STYLED_WHITE : '#888' } }}
                primary="Agents:" secondary={sourceToView?.agents?.join(", ") || 'N/A'}
              />
            </ListItem>
            <ListItem sx={{ borderBottom: '0px' }}>
              <ListItemText primary="Child Engines:" secondary={sourceToView?.child_engines?.join(", ") || 'N/A'} sx={{ color: sourceToView?.child_engines && sourceToView.child_engines.length > 0 ? STYLED_WHITE : '#888', '& .MuiListItemText-secondary': { color: sourceToView?.child_engines && sourceToView.child_engines.length > 0 ? STYLED_WHITE : '#888' } }} />
            </ListItem>
          </List>
        </DialogContent>
      </Dialog>
    </Box>
  );
};

export default Sources; // Export the component
