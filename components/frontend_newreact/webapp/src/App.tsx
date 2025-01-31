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
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './contexts/AuthContext';
import SignIn from './pages/SignIn';
import { useAuth } from './contexts/AuthContext';
import ChatHistory from './components/ChatHistory';
import { Chat } from './lib/types';

const PrivateRoute = ({ children }: { children: React.ReactNode }) => {
  const { user, loading } = useAuth();
  
  if (loading) {
    return <div>Loading...</div>;
  }
  
  if (!user) {
    return <Navigate to="/signin" />;
  }

  return <>{children}</>;
};

const MainApp = () => {
  const [prompt, setPrompt] = useState('');
  const [historyOpen, setHistoryOpen] = useState(false);
  const [showChat, setShowChat] = useState(false);
  const [currentChat, setCurrentChat] = useState<Chat | undefined>();
  const username = 'Ian';

  const toggleHistory = () => {
    setHistoryOpen(!historyOpen);
  };

  const handleSelectChat = (chat: Chat) => {
    setCurrentChat(chat);
    setShowChat(true);
    setHistoryOpen(false);
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
        sx={{
          '& .MuiDrawer-paper': {
            width: 240,
            boxSizing: 'border-box',
            bgcolor: 'background.paper'
          }
        }}
      >
        <ChatHistory 
          onClose={toggleHistory}
          onSelectChat={handleSelectChat}
          selectedChatId={currentChat?.id}
          isOpen={historyOpen}
        />
      </Drawer>
      <Box className="sidebar">
        <IconButton className="menu-button" onClick={() => setShowChat(true)}>
          <AddIcon />
        </IconButton>
        <IconButton className="menu-button history-button" onClick={toggleHistory}>
          <HistoryIcon />
        </IconButton>
      </Box>
      
      <Box className="main-content">
        {showChat ? (
          <ChatScreen currentChat={currentChat} />
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
};

export default function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/signin" element={<SignIn />} />
          <Route
            path="/*"
            element={
              <PrivateRoute>
                <MainApp />
              </PrivateRoute>
            }
          />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  );
}
