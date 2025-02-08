import { useState } from 'react';
import { Box, styled } from '@mui/material';
import { useAuth } from '../contexts/AuthContext';
import { Chat } from '../lib/types';
import { useSidebarStore } from '../lib/sidebarStore';
import ChatScreen from './ChatScreen';
import Sources from '../pages/Sources';
import { CustomHeader } from "./Header";
import { WelcomeFeatures } from './WelcomeFeatures';
import { Sidebar } from './Sidebar';

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

const Title = styled(Box)({
  fontSize: '22px',
  fontWeight: 50,
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
  }
});

const Main = styled(Box, {
  shouldForwardProp: (prop) => prop !== "sidebarWidth" && prop !== "panelWidth",
})<{ sidebarWidth: number, panelWidth: number }>(({ sidebarWidth, panelWidth }) => ({
  transition: 'margin-left 0.3s ease-in-out',
  paddingTop: 0,
  paddingLeft: '0',
  paddingRight: '0',
  marginLeft: `${60 + panelWidth}px`,
  flexGrow: 1,
  display: "flex",
  flexDirection: "column",
  height: "100vh",
  marginTop: 0,
  overflow: 'hidden',
  position: 'relative'
}));

export const MainApp = () => {
  const [currentChat, setCurrentChat] = useState<Chat | undefined>();
  const [showChat, setShowChat] = useState(true);
  const [showSources, setShowSources] = useState(false);
  const [showWelcome, setShowWelcome] = useState(true);

  const { isOpen, activePanel } = useSidebarStore();
  const { user } = useAuth();

  const hasActivePanel = activePanel === 'history' || activePanel === 'settings';
  const sidebarWidth = isOpen ? 150 : 52;
  const panelWidth = hasActivePanel ? 300 : 0;

  const username = user?.displayName || 'User';

  const handleSelectChat = (chat: Chat) => {
    setCurrentChat(chat);
    setShowChat(true);
  };

  const handleChatStart = () => {
    setShowWelcome(false);
    setShowChat(true);
  };

  const handleNewChat = () => {
    setCurrentChat(undefined);
    setShowWelcome(false);
    setShowChat(true);
    setShowSources(false);
  };

  return (
    <MainContainer>
      <Sidebar
        setShowChat={setShowChat}
        onSelectChat={handleSelectChat}
        selectedChatId={currentChat?.id}
        setShowSources={setShowSources}
        setShowWelcome={setShowWelcome}
        onNewChat={handleNewChat}
      />
      {(showWelcome || showSources) && (
        <CustomHeader sidebarWidth={sidebarWidth} panelWidth={panelWidth} title={
          <Title sx={{ marginLeft: '-20px' }}>
            <span className="primary">genAI</span>
            <span>for</span>
            <span className="gradient">Public Sector</span>
          </Title>
        }>
        </CustomHeader>
      )}
      <Main sidebarWidth={sidebarWidth} panelWidth={panelWidth}>
        {showWelcome && (
          <Box sx={{ 
            display: 'flex', 
            flexDirection: 'column',
            width: '100%',
            height: 'calc(100vh - 64px)',
            justifyContent: 'center',
            alignItems: 'center'
          }}>
            <WelcomeFeatures 
              username={username}
              onChatStart={() => setShowChat(true)}
              onSourcesView={() => {
                setShowSources(true);
                setShowWelcome(false);
                setShowChat(false);
              }}
            />
          </Box>
        )}         
        {showChat && (
          <ChatScreen
            currentChat={currentChat}
            hideHeader={!!currentChat || showWelcome}
            isNewChat={!currentChat}
            onChatStart={handleChatStart}
          />
        )}
        {showSources && <Sources />}
      </Main>
    </MainContainer>
  );
}; 