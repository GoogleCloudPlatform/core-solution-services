import { useState, useEffect, useRef, useMemo } from 'react';
import { Box, Typography, CircularProgress, ListItemButton } from '@mui/material';
import { useAuth } from '../contexts/AuthContext';
import { fetchChatHistory } from '../lib/api';
import { Chat } from '../lib/types';

interface ChatHistoryProps {
  onClose: () => void;
  onSelectChat: (chat: Chat) => void;
  selectedChatId?: string;
  isOpen: boolean;
}

const ChatHistory = ({ onClose, onSelectChat, selectedChatId, isOpen }: ChatHistoryProps) => {
  const [chats, setChats] = useState<Chat[]>([]);
  const [loading, setLoading] = useState(true);
  const { user } = useAuth();
  const chatRefs = useRef<(HTMLDivElement | null)[]>([]);

  const loadHistory = async () => {
    if (!user) return;
    setLoading(true);
    try {
      const chatHistory = await fetchChatHistory(user.token)();
      if (chatHistory) {
        setChats(chatHistory);
      }
    } catch (error) {
      console.error('Error loading chat history:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (!isOpen || !user) return;
    loadHistory();
  }, [user, isOpen]);

  useEffect(() => {
    const handleHistoryUpdate = () => {
      loadHistory();
    };
    window.addEventListener('chatHistoryUpdated', handleHistoryUpdate);
    return () => window.removeEventListener('chatHistoryUpdated', handleHistoryUpdate);
  }, [user, isOpen]);

  const formatTimestamp = (timestamp: string) => {
    const date = new Date(timestamp);
    const now = new Date();
    const diffInSeconds = Math.floor((now.getTime() - date.getTime()) / 1000);

    if (diffInSeconds < 60) return 'just now';
    if (diffInSeconds < 3600) return `${Math.floor(diffInSeconds / 60)}m ago`;
    if (diffInSeconds < 86400) return `${Math.floor(diffInSeconds / 3600)}h ago`;
    if (diffInSeconds < 31536000) return `${Math.floor(diffInSeconds / 86400)}d ago`;
    return `${Math.floor(diffInSeconds / 31536000)}y ago`;
  };

  const handleChatClick = (chat: Chat) => {
    console.log('Chat clicked:', chat);
    onSelectChat(chat);
  };

  // Group chats by id (with fallback to previous id if missing)
  const groupedChats = useMemo(() => {
    const groups: { [chatId: string]: Chat[] } = {};
    let lastValidId: string | undefined;

    chats.forEach(chat => {
      const currentId = chat.id ?? lastValidId;
      if (!currentId) return; // If even fallback is missing, skip
      lastValidId = currentId;

      if (!groups[currentId]) {
        groups[currentId] = [];
      }
      groups[currentId].push(chat);
    });

    return Object.entries(groups).map(([chatId, chats]) => ({
      chatId,
      chats,
      latestChat: chats.sort((a, b) => new Date(b.created_time).getTime() - new Date(a.created_time).getTime())[0]
    }));
  }, [chats]);

  useEffect(() => {
    chatRefs.current = Array(groupedChats.length).fill(null);
  }, [groupedChats]);

  return (
    <Box className="history-drawer">
      <Box className="history-content" sx={{
        overflowY: 'auto',
        height: 'calc(100vh - 64px)'
      }}>
        {loading ? (
          <Box sx={{ display: 'flex', justifyContent: 'center', p: 3 }}>
            <CircularProgress size={24} />
          </Box>
        ) : (
          <>
            {groupedChats.map((group, index) => (
              <ListItemButton
                key={group.chatId}
                onClick={() => handleChatClick(group.latestChat)}
                ref={ref => chatRefs.current[index] = ref}
                sx={{
                  padding: '16px',
                  cursor: 'pointer',
                  borderBottom: '1px solid rgba(255, 255, 255, 0.1)',
                  backgroundColor: group.latestChat.id === selectedChatId ? 'rgba(255, 255, 255, 0.1)' : 'transparent',
                  '&:hover': {
                    backgroundColor: 'rgba(255, 255, 255, 0.05)'
                  },
                  '&:focus-visible': {
                    boxShadow: '0 0 0 2px #4a90e2',
                    border: '1px solid #4a90e2',
                    borderRadius: '4px'
                  },
                  display: 'block'
                }}
              >
                <Box sx={{ display: 'flex', flexDirection: 'column', textAlign: 'left', width: '100%' }}>
                  <Typography
                    variant="body2"
                    sx={{
                      color: 'rgba(255, 255, 255, 0.5)',
                      fontSize: '12px',
                      mb: '8px'
                    }}
                  >
                    {formatTimestamp(group.latestChat.created_time)}
                  </Typography>
                  <Typography
                    variant="body1"
                    sx={{
                      color: 'rgba(255, 255, 255, 0.87)',
                      fontSize: '14px',
                      lineHeight: '20px'
                    }}
                  >
                    {group.latestChat.title || 'Untitled Chat'}
                  </Typography>
                </Box>
              </ListItemButton>
            ))}
          </>
        )}
      </Box>
    </Box>
  );
};

export default ChatHistory;