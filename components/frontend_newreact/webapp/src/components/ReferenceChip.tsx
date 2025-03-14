import { useState } from 'react';
import { Box, Typography, Button, IconButton, Tooltip } from '@mui/material';
import { QueryReference } from '../lib/types';
import ContentCopyIcon from '@mui/icons-material/ContentCopy';

interface ReferenceChipProps {
  reference: QueryReference;
}

const ReferenceChip: React.FC<ReferenceChipProps> = ({ reference }) => {

  const [showDetails, setShowDetails] = useState(false);
  const [tooltipOpen, setTooltipOpen] = useState(false);


  //New function to create the title
  const createReferenceTitle = (url: string): string => {
    const parts = url.split('/');
    let title = parts.pop(); // Get the last part
    if (!title || title.trim() === "") {
      title = parts.pop(); // if the last part is empty, get the one before.
    }
    return title || "Unknown Document"; // return a default value if we did not find a title.
  };

  const referenceTitle = createReferenceTitle(reference.document_url)


  return (
    <Box sx={{ mb: 1, position: 'relative' }}>
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
          color: '#fff',
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
            {referenceTitle}
          </Typography>
          {showDetails && (
            <Typography
              variant="body2"
              sx={{
                color: '#fff',
                whiteSpace: 'pre-wrap',
                width: '100%',
                textAlign: 'left',
                userSelect: 'text', // Crucial for making the text selectable
                cursor: 'text',    // Changes cursor to text select cursor
                overflowWrap: 'break-word' //prevent words from overflowing the box
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
