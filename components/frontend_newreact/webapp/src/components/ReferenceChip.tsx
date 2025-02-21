import { useState } from 'react';
import { Box, Typography, Button } from '@mui/material';
import { QueryReference } from '../lib/types';

const ReferenceChip: React.FC<{ reference: QueryReference }> = ({ reference }) => {
  const [showDetails, setShowDetails] = useState(false);

  return (
    <Box sx={{ mb: 1 }}>
      <Button 
        onClick={() => setShowDetails(!showDetails)}
        sx={{ 
          textTransform: 'none',
          p: 1,
          borderRadius: 1,
          border: '1px solid #4a4a4a',
          display: 'flex',
          alignItems: 'center',
          width: '100%',
          justifyContent: 'flex-start',
          color: 'text.primary',
          '&:hover': {
            backgroundColor: 'rgba(255, 255, 255, 0.05)'
          }
        }}
      >
        <Box sx={{ 
          display: 'flex', 
          flexDirection: 'column',
          alignItems: 'flex-start',
          width: '100%'
        }}>
          <Typography variant="body2" sx={{ mb: 0.5 }}>
            {reference.document_url.split('/').pop()}
          </Typography>
          {showDetails && (
            <Typography 
              variant="body2" 
              sx={{ 
                color: 'text.secondary',
                whiteSpace: 'pre-wrap',
                width: '100%',
                textAlign: 'left'
              }}
            >
              {reference.document_text}
            </Typography>
          )}
        </Box>
      </Button>
    </Box>
  );
};

export default ReferenceChip;
