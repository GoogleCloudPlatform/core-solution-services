import { Box, Paper, Typography } from '@mui/material';
import ChatIcon from '@mui/icons-material/Chat';
import StorageIcon from '@mui/icons-material/Storage';

interface Feature {
  icon: React.ReactNode;
  title: string;
  subtitle: string;
  action: string;
  onClick: () => void;
}

interface WelcomeFeaturesProps {
  username: string;
  onChatStart: () => void;
  onSourcesView: () => void;
}

export const WelcomeFeatures = ({ username, onChatStart, onSourcesView }: WelcomeFeaturesProps) => {
  const features: Feature[] = [
    {
      icon: <ChatIcon />,
      title: 'Chat',
      subtitle: 'Latest Topical Gist',
      action: 'Resume',
      onClick: onChatStart
    },
    {
      icon: <StorageIcon />,
      title: 'Knowledge Sources',
      subtitle: 'Browse your sources',
      action: 'View',
      onClick: onSourcesView
    },
  ];

  return (
    <Box sx={{ 
      position: 'absolute',
      top: '50%',
      left: '50%',
      transform: 'translate(-50%, -50%)',
      width: '100%',
      display: 'flex',
      flexDirection: 'column',
      gap: 4,
    }}>
      <Typography variant="h4" className="greeting" sx={{ textAlign: 'center' }}>
        <span className="hello">Hello, {username}</span>
      </Typography>

      <Box className="features-grid">
        {features.map((feature, index) => (
          <Paper 
            key={index} 
            className="feature-card"
            onClick={feature.onClick}
            sx={{ 
              cursor: 'pointer',
              backgroundColor: '#1E1E1E !important',
              border: '1px solid rgba(255, 255, 255, 0.12)',
              borderRadius: '8px !important',
            }}
          >
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5 }}>
              {feature.icon}
              <Typography variant="h6" sx={{ fontSize: '16px', fontWeight: 400 }}>
                {feature.title}
              </Typography>
            </Box>
            <Typography 
              variant="body2" 
              className="subtitle"
              sx={{ 
                color: 'rgba(255, 255, 255, 0.7)',
                mt: 1
              }}
            >
              {feature.subtitle}
            </Typography>
            <Box 
              sx={{ 
                mt: 'auto', 
                pt: 2,
                display: 'flex',
                justifyContent: 'flex-start'
              }}
            >
              <Box
                sx={{
                  bgcolor: 'rgba(147, 176, 255, 0.16)',
                  color: '#93B0FF',
                  px: 2,
                  py: 0.5,
                  borderRadius: '16px',
                  fontSize: '14px',
                  fontWeight: 500
                }}
              >
                {feature.action}
              </Box>
            </Box>
          </Paper>
        ))}
      </Box>
    </Box>
  );
}; 