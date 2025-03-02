import {
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  IconButton,
  Tooltip,
  Checkbox,
  Box,
  Typography,
  styled
} from '@mui/material';
import { EditNote, Info, DeleteIcon } from '@mui/icons-material';
import { QueryEngine, QUERY_ENGINE_TYPES } from '../lib/types';

// Styled components
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

interface SourcesTableProps {
  sources: QueryEngine[];
  selectedSources: string[];
  onSelectAll: (event: React.ChangeEvent<HTMLInputElement>) => void;
  onSelectSource: (id: string) => void;
  onEditClick: (id: string) => void;
  onViewClick: (id: string) => void;
  onDeleteClick: (id: string) => void;
  typeFilter: string;
  jobStatusFilter: string;
  currentPage: number;
  rowsPerPage: number;
}

const SourcesTable: React.FC<SourcesTableProps> = ({
  sources,
  selectedSources,
  onSelectAll,
  onSelectSource,
  onEditClick,
  onViewClick,
  onDeleteClick,
  typeFilter,
  jobStatusFilter,
  currentPage,
  rowsPerPage
}) => {
  const getStatusIcon = (status: string | undefined) => {
    switch (status) {
      case 'success':
        return <CheckCircleIcon sx={{ color: '#4CAF50' }} />;
      case 'failed':
        return <ErrorIcon sx={{ color: '#f44336' }} />;
      case 'active':
        return <SyncIcon sx={{ color: '#2196F3' }} />;
      default:
        return null;
    }
  };

  // Filter sources based on type and status filters
  const filteredSources = sources.filter(source => 
    (typeFilter === 'all' || source.query_engine_type === typeFilter) &&
    (jobStatusFilter === 'all' || source.status === jobStatusFilter)
  );

  // Get paginated data
  const paginatedSources = filteredSources.slice(
    (currentPage - 1) * rowsPerPage,
    currentPage * rowsPerPage
  );

  return (
    <TableContainer sx={{ backgroundColor: 'transparent' }}>
      <Table>
        <TableHead>
          <TableRow>
            <StyledTableCell padding="checkbox">
              <Checkbox
                checked={selectedSources.length === sources.length && sources.length > 0}
                indeterminate={selectedSources.length > 0 && selectedSources.length < sources.length}
                onChange={onSelectAll}
                sx={{ color: 'white' }}
              />
            </StyledTableCell>
            <StyledTableCell>Name</StyledTableCell>
            <StyledTableCell>Description</StyledTableCell>
            <StyledTableCell>Job Status</StyledTableCell>
            <StyledTableCell>Type</StyledTableCell>
            <StyledTableCell>Created</StyledTableCell>
            <StyledTableCell align="right"></StyledTableCell>
          </TableRow>
        </TableHead>
        <TableBody>
          {paginatedSources.map((source) => (
            <StyledTableRow key={source.id}>
              <StyledTableCell padding="checkbox">
                <Checkbox
                  checked={selectedSources.includes(source.id)}
                  onChange={() => onSelectSource(source.id)}
                  sx={{ color: 'white' }}
                />
              </StyledTableCell>
              <StyledTableCell>{source.name}</StyledTableCell>
              <StyledTableCell>{source.description}</StyledTableCell>
              <StyledTableCell>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  {getStatusIcon(source.status)}
                  {source.status ?? "unknown"}
                </Box>
              </StyledTableCell>
              <StyledTableCell>
                {QUERY_ENGINE_TYPES[source.query_engine_type as keyof typeof QUERY_ENGINE_TYPES] ||
                  source.query_engine_type}
              </StyledTableCell>
              <StyledTableCell>{new Date(source.created_time).toLocaleDateString()}</StyledTableCell>
              <StyledTableCell align="left">
                <Tooltip title="Edit Source">
                  <IconButton onClick={() => onEditClick(source.id)}>
                    <EditNote sx={{ color: "white" }} />
                  </IconButton>
                </Tooltip>
                <Tooltip title="View Source">
                  <IconButton onClick={() => onViewClick(source.id)}>
                    <Info sx={{ color: "white" }} />
                  </IconButton>
                </Tooltip>
                <Tooltip title="Delete Source">
                  <IconButton onClick={() => onDeleteClick(source.id)}>
                    <DeleteIcon sx={{ color: "red" }} />
                  </IconButton>
                </Tooltip>
              </StyledTableCell>
            </StyledTableRow>
          ))}
        </TableBody>
      </Table>
    </TableContainer>
  );
};

export default SourcesTable; 