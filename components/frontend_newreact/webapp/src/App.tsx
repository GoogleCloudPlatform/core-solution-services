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
import { ModelProvider } from './contexts/ModelContext';
import Sources from './pages/Sources';
import StorageIcon from '@mui/icons-material/Storage';
import CloudIcon from '@mui/icons-material/Cloud';
import AddSource from './pages/AddSource';
import PasswordReset from '@/pages/PasswordReset';


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
  margin: 0,
  padding: 0,
  width: '100%',
  overflow: 'hidden',
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
  left: `${60 + panelWidth}px`,
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
  paddingTop: 0,
  paddingLeft: '16px',
  paddingRight: '16px',
  marginLeft: `${60 + panelWidth}px`,
  flexGrow: 1,
  display: "flex",
  flexDirection: "column",
  justifyContent: "center",
  alignItems: "center",
  minHeight: "100vh",
}));

const MainApp = () => {
  const [prompt, setPrompt] = useState('');
  const [historyOpen, setHistoryOpen] = useState(false);
  const [showChat, setShowChat] = useState(false);
  const [currentChat, setCurrentChat] = useState<Chat | undefined>();
  const [settingsOpen, setSettingsOpen] = useState(false);
  const [showSources, setShowSources] = useState(false);

  const { isOpen, activePanel, toggle } = useSidebarStore();

  const hasActivePanel = activePanel === 'history' || activePanel === 'settings';
  const sidebarWidth = isOpen ? 150 : 52;
  const panelWidth = hasActivePanel ? 300 : 0;

  const { user } = useAuth();

  const username = user?.displayName || 'User';
  const email = user?.email || 'user@example.com';
  const photoURL = user?.photoURL || ''; // Get photoURL
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
    { icon: <StorageIcon />, title: 'Knowledge Sources', subtitle: 'Browse your sources', action: 'View', onClick: () => setShowSources(true) },
  ];

  return (
    <MainContainer>
      <Sidebar 
        setShowChat={setShowChat} 
        onSelectChat={handleSelectChat} 
        selectedChatId={currentChat?.id}
        setShowSources={setShowSources}
      />
      <Header sidebarWidth={sidebarWidth} panelWidth={panelWidth}>
        <Title>
          <span className="primary">genAI</span>
          <span className="gradient">for Public Sector</span>
        </Title>
        <ProfileMenu />
      </Header>
      <Main sidebarWidth={sidebarWidth} panelWidth={panelWidth}>
        {showChat ? (
          <ChatScreen 
            currentChat={currentChat}
          />
        ) : showSources ? (
          <Sources />
        ) : (
          <>
            <Typography variant="h4" className="greeting">
              <span className="hello">Hello, {username}</span>
            </Typography>

            <Box className="features-grid">
              {features.map((feature, index) => (
                <Paper 
                  key={index} 
                  className="feature-card"
                  onClick={feature.onClick}
                  sx={{ cursor: feature.onClick ? 'pointer' : 'default' }}
                >
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
      <ModelProvider>
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
            <Route path="/sources/add" element={<AddSource />} />
            <Route path="/password-reset" element={<PasswordReset />} />
          </Routes>
        </BrowserRouter>
      </ModelProvider>
    </AuthProvider>
  );
}
