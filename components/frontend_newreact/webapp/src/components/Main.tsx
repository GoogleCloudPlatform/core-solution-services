import { useState } from 'react';
import { Box, styled } from '@mui/material';
import { useAuth } from '../contexts/AuthContext';
import { useModel } from '../contexts/ModelContext';
import { Chat, Query } from '../lib/types';
import { useSidebarStore } from '../lib/sidebarStore';
import ChatScreen from './ChatScreen';
import Sources from '../pages/Sources';
import { CustomHeader } from "./Header";
import { WelcomeFeatures } from './WelcomeFeatures';
import { Sidebar } from './Sidebar';
import { fetchLatestChat, resumeChat } from '@/lib/api';

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
  const [currentQuery, setCurrentQuery] = useState<Query | undefined>();
  const [showChat, setShowChat] = useState(true);
  const [showSources, setShowSources] = useState(false);
  const [showWelcome, setShowWelcome] = useState(true);

  const { isOpen, activePanel } = useSidebarStore();
  const { user } = useAuth();
  const { selectedModel } = useModel();

  const hasActivePanel = activePanel === 'history' || activePanel === 'settings';
  const sidebarWidth = isOpen ? 150 : 52;
  const panelWidth = hasActivePanel ? 300 : 0;

  const username = user?.displayName || 'User';

  const handleSelectChat = (chat: Chat) => {
    setCurrentChat(chat);
    setShowChat(true);
    setShowWelcome(false);
    setShowSources(false);
  };

  const handleSelectQuery = (query: Query) => {
    setCurrentQuery(query);
    setShowChat(true);
    setShowWelcome(false);
    setShowSources(false);
  };

  const handleChatStart = () => {
    setShowWelcome(false);
    setShowChat(true);
  };

  const handleNewChat = () => {
    // Create a new empty chat object
    const newChat: Chat = {
      id: undefined,  // undefined for new chat
      title: 'New Chat',
      created_time: new Date().toISOString(),
      created_by: user?.uid || '',
      last_modified_time: new Date().toISOString(),
      last_modified_by: user?.uid || '',
      archived_at_timestamp: null,
      archived_by: '',
      deleted_at_timestamp: null,
      deleted_by: '',
      prompt: '',
      llm_type: selectedModel.id,
      user_id: user?.uid || '',
      agent_name: null,
      history: []
    };

    setCurrentChat(newChat);
    setShowChat(true);
    setShowWelcome(false);
    setShowSources(false);
  };

  return (
    <MainContainer>
      <Sidebar
        setShowChat={setShowChat}
        onSelectChat={handleSelectChat}
        selectedChatId={currentChat?.id}
        onSelectQuery={handleSelectQuery}
        selectedQueryId={currentQuery?.id}
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
              onChatStart={() => {
                setShowChat(true)

                if (!user?.token) {
                  return;
                }

                fetchLatestChat(user.token)().then(chat => {
                  if (chat) {
                    // console.log(chat)
                    setCurrentChat(chat);
                    handleChatStart();
                  }
                })

                // resumeChat(user.token)({
                //   chatId,
                //   userInput: prompt,
                //   llmType: selectedModel.id,
                //   stream: false,
                //   temperature: temperature
                // });
              }}
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
            hideHeader={showWelcome}
            isNewChat={!currentChat}
            onChatStart={handleChatStart}
          />
        )}
        {showSources && <Sources />}
      </Main>
    </MainContainer>
  );
}; 