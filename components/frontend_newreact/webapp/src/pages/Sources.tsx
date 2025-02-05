import { useEffect, useState } from 'react';
import { Box, Typography, Paper, IconButton, Tooltip } from '@mui/material';
import { styled } from '@mui/material/styles';
import { QueryEngine, QUERY_ENGINE_TYPES } from '../lib/types';
import { useAuth } from '../contexts/AuthContext';
import { fetchAllEngines } from '../lib/api';
import StorageIcon from '@mui/icons-material/Storage';
import CloudIcon from '@mui/icons-material/Cloud';
import MoreVertIcon from '@mui/icons-material/MoreVert';

const SourcesContainer = styled(Box)(({ theme }) => ({
  padding: theme.spacing(3),
  width: '100%',
  height: '100%',
  overflowY: 'auto',
}));

const SourcesGrid = styled(Box)(({ theme }) => ({
  display: 'grid',
  gridTemplateColumns: 'repeat(auto-fill, minmax(300px, 1fr))',
  gap: theme.spacing(3),
  marginTop: theme.spacing(3),
}));

const SourceCard = styled(Paper)(({ theme }) => ({
  padding: theme.spacing(2),
  backgroundColor: '#2A2A2A',
  border: '1px solid #3A3A3A',
  borderRadius: theme.spacing(1),
  '&:hover': {
    backgroundColor: '#303030',
    cursor: 'pointer',
  },
}));

const SourceHeader = styled(Box)({
  display: 'flex',
  justifyContent: 'space-between',
  alignItems: 'center',
  marginBottom: '8px',
});

const SourceTitle = styled(Typography)({
  fontWeight: 500,
  color: '#E3E3E3',
});

const SourceType = styled(Typography)({
  color: '#888',
  fontSize: '0.875rem',
});

const SourceDescription = styled(Typography)({
  color: '#B0B0B0',
  fontSize: '0.875rem',
  marginTop: '8px',
  display: '-webkit-box',
  WebkitLineClamp: 2,
  WebkitBoxOrient: 'vertical',
  overflow: 'hidden',
});

const EmptyState = styled(Box)(({ theme }) => ({
  display: 'flex',
  flexDirection: 'column',
  alignItems: 'center',
  justifyContent: 'center',
  padding: theme.spacing(4),
  color: '#888',
  textAlign: 'center',
  marginTop: theme.spacing(4),
}));

const Sources = () => {
  const [sources, setSources] = useState<QueryEngine[]>([]);
  const { user } = useAuth();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

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

  return (
    <SourcesContainer>
      <Typography variant="h4" sx={{ color: '#E3E3E3', mb: 2 }}>
        Knowledge Sources
      </Typography>
      
      <Typography variant="body1" sx={{ color: '#B0B0B0' }}>
        Browse and manage your knowledge sources
      </Typography>

      {loading ? (
        <EmptyState>
          <Typography>Loading sources...</Typography>
        </EmptyState>
      ) : error ? (
        <EmptyState>
          <Typography color="error">{error}</Typography>
        </EmptyState>
      ) : sources.length === 0 ? (
        <EmptyState>
          <StorageIcon sx={{ fontSize: 48, color: '#666', mb: 2 }} />
          <Typography variant="h6" sx={{ color: '#888', mb: 1 }}>
            No Knowledge Sources Available
          </Typography>
          <Typography variant="body2" sx={{ color: '#666', maxWidth: 400 }}>
            There are currently no knowledge sources configured. Knowledge sources allow you to query specific data collections.
          </Typography>
        </EmptyState>
      ) : (
        <SourcesGrid>
          {sources.map((source) => (
            <SourceCard key={source.id}>
              <SourceHeader>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  {source.query_engine_type.includes('vertex') ? (
                    <CloudIcon sx={{ color: '#4C8DF6' }} />
                  ) : (
                    <StorageIcon sx={{ color: '#4C8DF6' }} />
                  )}
                  <SourceTitle variant="h6">
                    {source.name}
                  </SourceTitle>
                </Box>
                <Tooltip title="More options">
                  <IconButton size="small" sx={{ color: '#888' }}>
                    <MoreVertIcon />
                  </IconButton>
                </Tooltip>
              </SourceHeader>
              
              <SourceType>
                {QUERY_ENGINE_TYPES[source.query_engine_type as keyof typeof QUERY_ENGINE_TYPES] || source.query_engine_type}
              </SourceType>
              
              <SourceDescription>
                {source.description || 'No description available'}
              </SourceDescription>
            </SourceCard>
          ))}
        </SourcesGrid>
      )}
    </SourcesContainer>
  );
};

export default Sources; 