import { useState } from 'react';
import { Box, Typography, Button, IconButton, Tooltip } from '@mui/material';
import { QueryReference } from '../lib/types';
import ContentCopyIcon from '@mui/icons-material/ContentCopy';

interface ReferenceChipProps {
  reference: QueryReference;
  onCopy?: (text: string, references?: QueryReference[]) => void;
}

const ReferenceChip: React.FC<ReferenceChipProps> = ({ reference, onCopy }) => {

  const [showDetails, setShowDetails] = useState(false);
  const [tooltipOpen, setTooltipOpen] = useState(false);
  const [iconClicked, setIconClicked] = useState(false);

  const handleCopy = () => {
    if (onCopy) {
      onCopy(reference.document_text, [reference]);
      setTooltipOpen(true);
      setIconClicked(true);
      setTimeout(() => {
        setIconClicked(false);
      }, 200);
    }
  };

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
            {reference.document_url.split('/').pop()}
          </Typography>
          {showDetails && (
            <Typography
              variant="body2"
              sx={{
                color: '#fff',
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
      {onCopy && (
        <Tooltip
          open={tooltipOpen}
          onClose={() => setTooltipOpen(false)}
          title="Copied!"
          placement="top"
          leaveDelay={200}
        >
          <IconButton
            sx={{
              position: 'absolute',
              left: -4,
              top: -4,
              backgroundColor: iconClicked ? '#2979ff' : 'transparent',
              borderRadius: '50%',
              transition: 'background-color 0.2s ease',
              padding: '4px',
              '&:hover': {
                backgroundColor: '#e3f2fd',
              },
            }}
            onClick={handleCopy}
          >
            <ContentCopyIcon
              sx={{ color: iconClicked ? 'white' : '#9e9e9e', fontSize: '16px' }}
            />
          </IconButton>
        </Tooltip>
      )}
    </Box>
  );
};

export default ReferenceChip;
