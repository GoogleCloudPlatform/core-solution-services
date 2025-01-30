import { useState } from 'react';
import { Box, Typography, IconButton, Paper, InputBase, Drawer, Avatar, Select, MenuItem } from '@mui/material';
import CloseIcon from '@mui/icons-material/Close';
import AddIcon from '@mui/icons-material/Add';
import ChatIcon from '@mui/icons-material/Chat';
import HistoryIcon from '@mui/icons-material/History';
import FolderIcon from '@mui/icons-material/Folder';
import ImageIcon from '@mui/icons-material/Image';
import KeyboardArrowDownIcon from '@mui/icons-material/KeyboardArrowDown';
import './App.css';
import ChatScreen from './components/ChatScreen';

export default function App() {
  const [prompt, setPrompt] = useState('');
  const [historyOpen, setHistoryOpen] = useState(false);
  const [showChat, setShowChat] = useState(false);
  const username = 'Ian';

  const toggleHistory = () => {
    setHistoryOpen(!historyOpen);
  };

  const toggleChat = () => {
    setShowChat(!showChat);
  };

  const features = [
    { icon: <ChatIcon />, title: 'Chat', subtitle: 'Latest Topical Gist', action: 'Resume' },
    { icon: <FolderIcon />, title: 'Knowledge Sources', subtitle: 'Knowledge Source Name', action: 'Query' },
    { icon: <HistoryIcon />, title: 'Latest Gem', subtitle: 'Plug-in Title', action: 'Run again' },
    { icon: <ImageIcon />, title: 'Create Images', subtitle: 'Generate custom images using Imagen 3', action: 'Try it' },
  ];

  return (
    <Box className="app">
      <Drawer
        anchor="left"
        open={historyOpen}
        variant="persistent"
        className="history-drawer"
        classes={{
          paper: 'history-drawer-paper'
        }}
      >
        <Box className="history-header">
          <Typography variant="h6">History</Typography>
          <IconButton onClick={toggleHistory}>
            <CloseIcon />
          </IconButton>
        </Box>
        <Box className="history-content">
          {[1, 2].map((_, index) => (
            <Box key={index} className="history-item">
              <Typography variant="body2" className="history-time">4y ago</Typography>
              <Typography variant="body1">Topical Gist</Typography>
            </Box>
          ))}
        </Box>
      </Drawer>
      <Box className="sidebar">
        <IconButton className="menu-button" onClick={toggleChat}>
          <AddIcon />
        </IconButton>
        <IconButton className="menu-button history-button" onClick={toggleHistory}>
          <HistoryIcon />
        </IconButton>
      </Box>
      
      <Box className="main-content">
        {showChat ? (
          <ChatScreen />
        ) : (
          <>
            <Typography variant="h4" className="greeting">
              <span className="hello">Hello,</span> <span className="name">{username}</span>
            </Typography>

            <Box className="features-grid">
              {features.map((feature, index) => (
                <Paper key={index} className="feature-card">
                  {feature.icon}
                  <Typography variant="h6">{feature.title}</Typography>
                  <Typography variant="body2" className="subtitle">{feature.subtitle}</Typography>
                  <Typography variant="button" className="action">{feature.action}</Typography>
                </Paper>
              ))}
            </Box>
          </>
        )}
      </Box>
    </Box>
  );
}
