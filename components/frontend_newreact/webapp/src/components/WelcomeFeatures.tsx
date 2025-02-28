import { Box, Paper, Typography } from '@mui/material';
import ChatIcon from '@mui/icons-material/Chat';
import StorageIcon from '@mui/icons-material/Storage';
import ChatInterfaceIcon from '../assets/chat-icon.svg'; // Import your SVG
import SourceIcon from '../assets/source-icon.svg'; // Import your SVG

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
  headerHeight: number;
}

export const WelcomeFeatures = ({ username, onChatStart, onSourcesView, headerHeight }: WelcomeFeaturesProps) => {
  const features: Feature[] = [
    {
      icon: <img src={ChatInterfaceIcon} style={{ width: '24px', height: '24px' }} alt="Chat icon"/>,
      title: 'Chat',
      subtitle: 'Latest Topical Gist',
      action: 'Resume',
      onClick: ()=> {
        onChatStart();
      }   
    },
    {
      icon: <img src={SourceIcon} style={{ width: '24px', height: '24px' }} alt="Knowledge source icon"/>,
      title: 'Knowledge Sources',
      subtitle: 'Knowledge Source Name',
      action: 'Query',
      onClick: () => {
        onSourcesView();
      }
    },
  ];

  return (
    <Box sx={{
      width: '100%',
      display: 'flex',
      flexDirection: 'column',
      gap: 4,
      justifyContent: 'center',
      alignItems: 'center',
      px: 3,
      flexGrow: 1,  // Takes up available space but allows input box to stay
      minHeight: `calc(100vh - ${headerHeight + 150}px)`,  // Leaves room for input
      overflowY: 'auto', // Ensures scrolling if needed
    }}>
      <Typography
        variant="h4"
        className="greeting"
        sx={{
          textAlign: 'center',
          fontSize: '32px',
          mb: 2
        }}
      >
        <span className="font-poppins bg-gradient-to-r from-blue-500 to-red-500 bg-clip-text text-transparent">Hello, {username}</span>
      </Typography>

      <Box className="features-grid" sx={{
        maxWidth: '700px',
        width: '100%',
      }}>
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
              p: 3,
              minHeight: '180px'
            }}
          >
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5 }}>
              {feature.icon}
              <Typography variant="h1" sx={{ fontSize: '16px', fontWeight: 400 }}>
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
                  bgcolor: '#A8C7FA',
                  color: '#062E6F',
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