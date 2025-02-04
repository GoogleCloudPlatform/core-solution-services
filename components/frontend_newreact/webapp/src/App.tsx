import { useState } from 'react';
import { Box, Typography, IconButton, Paper, InputBase, Drawer, Avatar, Select, MenuItem, styled } from '@mui/material';
import CloseIcon from '@mui/icons-material/Close';
import AddIcon from '@mui/icons-material/Add';
import ChatIcon from '@mui/icons-material/Chat';
import HistoryIcon from '@mui/icons-material/History';
import FolderIcon from '@mui/icons-material/Folder';
import ImageIcon from '@mui/icons-material/Image';
import SettingsIcon from '@mui/icons-material/Settings'; // Import the settings icon
import KeyboardArrowDownIcon from '@mui/icons-material/KeyboardArrowDown';
import './App.css';
import ChatScreen from './components/ChatScreen';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './contexts/AuthContext';
import SignIn from './pages/SignIn';
import { useAuth } from './contexts/AuthContext';
import ChatHistory from './components/ChatHistory';
import { Chat } from './lib/types';
import SettingsDrawer from './components/SettingsDrawer'; // Import the SettingsDrawer component
import { useSidebarStore } from './lib/sidebarStore';
import { ProfileMenu } from './components/profile-menu';
import MenuIcon from '@mui/icons-material/Menu';
import { Sidebar } from './components/Sidebar';


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

const MainContainer = styled(Box)(({ theme }) => ({
  minHeight: '100vh',
  backgroundColor: theme.palette.background.default,
  display: "flex",
  background: "#1a1a1a",
  color: "white",
}));

const Header = styled(Box, {
  shouldForwardProp: (prop) => prop !== "sidebarWidth" && prop !== "panelWidth",
})<{ sidebarWidth: number, panelWidth: number }>(({ theme, sidebarWidth, panelWidth }) => ({
  position: 'fixed',
  zIndex: 50,
  padding: theme.spacing(2),
  display: 'flex',
  justifyContent: 'space-between',
  alignItems: 'center',
  background: `linear-gradient(to bottom, ${theme.palette.background.default}CC, ${theme.palette.background.default}00)`,
  right: 0,
  left: `${sidebarWidth + panelWidth}px`,
  transition: 'left 0.3s ease-in-out',
}));

const Title = styled(Box)({
  fontSize: '22px',
  fontWeight: 500,
  fontFamily: 'Google Sans',
  display: 'flex',
  alignItems: 'center',
  gap: '8px',
  '& .primary': {
    color: '#E3E3E3',
  },
  '& .gradient': {
    background: 'linear-gradient(to right, #4C8DF6, #FF0000)',
    WebkitBackgroundClip: 'text',
    WebkitTextFillColor: 'transparent',
  },
});

const Main = styled(Box, {
  shouldForwardProp: (prop) => prop !== "sidebarWidth" && prop !== "panelWidth",
})<{ sidebarWidth: number, panelWidth: number }>(({ sidebarWidth, panelWidth }) => ({
  transition: 'margin-left 0.3s ease-in-out',
  paddingTop: '64px',
  paddingLeft: '16px',
  paddingRight: '16px',
  marginLeft: `${sidebarWidth + panelWidth}px`,
  flexGrow: 1,
  display: "flex",
  flexDirection: "column",
}));

const MainApp = () => {
  const [prompt, setPrompt] = useState('');
  const [historyOpen, setHistoryOpen] = useState(false);
  const [showChat, setShowChat] = useState(false);
  const [currentChat, setCurrentChat] = useState<Chat | undefined>();
  const [settingsOpen, setSettingsOpen] = useState(false); // Add state for settings drawer

  const { isOpen, activePanel, toggle } = useSidebarStore();

  const hasActivePanel = activePanel === 'history' || activePanel === 'settings';
  const sidebarWidth = isOpen ? 150 : 52;
  const panelWidth = hasActivePanel ? 300 : 0;

  const { user } = useAuth();

  const username = user.displayName || 'User';
  const email = user.email || 'user@example.com';
  const photoURL = user.photoURL; // Get photoURL
  const initials = username
    .split(' ')
    .map(n => n[0])
    .join('')
    .toUpperCase();

  const toggleHistory = () => {
    setHistoryOpen(!historyOpen);
  };

  const toggleSettings = () => {  // Add function to toggle settings drawer
    setSettingsOpen(!settingsOpen);
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
    <MainContainer>
      {/* <Drawer
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
        <SettingsDrawer
          open={settingsOpen}
          onClose={toggleSettings}
        />
        <ChatHistory
          onClose={toggleHistory}
          onSelectChat={handleSelectChat}
          selectedChatId={currentChat?.id}
          isOpen={historyOpen}
        /> 
      </Drawer>*/}
      {/* <Box className="sidebar">
        <IconButton
          onClick={toggle}
          sx={{
            color: 'rgba(255, 255, 255, 0.7)',
            '&:hover': {
              backgroundColor: 'rgba(255, 255, 255, 0.06)',
            },
          }}
        >
          <MenuIcon />
        </IconButton>
        <IconButton className="menu-button" onClick={() => setShowChat(true)}>
          <AddIcon />
        </IconButton>
        <IconButton className="menu-button history-button" onClick={toggleHistory}>
          <HistoryIcon />
        </IconButton>
        <IconButton className="menu-button settings-button" onClick={toggleSettings}>
          <SettingsIcon />
        </IconButton>
        <IconButton className="menu-button settings-button" onClick={toggleSettings}> 
          <SettingsIcon />
        </IconButton>
      </Box> */}
      <Sidebar setShowChat={setShowChat} />
      <Header sidebarWidth={sidebarWidth} panelWidth={panelWidth}>
        <Title>
          <span className="primary">genAI</span>
          <span className="gradient">for Public Sector</span>
        </Title>
        <ProfileMenu />
      </Header>
      <Main sidebarWidth={sidebarWidth} panelWidth={panelWidth}>
        {showChat ? (
          <ChatScreen currentChat={currentChat} />
        ) : (
          <>
            <Typography variant="h4" className="greeting">
              <span className="hello">Hello, {username}</span>
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
      </Main>
    </MainContainer>
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
