import { useState, useEffect } from 'react';
import { Box, Typography, IconButton, CircularProgress } from '@mui/material';
import CloseIcon from '@mui/icons-material/Close';
import { useAuth } from '../contexts/AuthContext';
import { fetchChatHistory, fetchQuery, fetchQueryHistory } from '../lib/api';
import { Chat, Query } from '../lib/types';

interface ChatHistoryProps {
  onClose: () => void;
  onSelectChat: (chat: Chat) => void;
  selectedChatId?: string;
  onSelectQuery: (query: Query) => void;
  selectedQueryId?: string;
  isOpen: boolean;
}

const ChatHistory = ({ onClose, onSelectChat, selectedChatId, onSelectQuery, selectedQueryId, isOpen }: ChatHistoryProps) => {
  const [chats, setChats] = useState<Chat[]>([]);
  const [queries, setQueries] = useState<Query[]>([]);
  const [loading, setLoading] = useState(true);
  const { user } = useAuth();

  useEffect(() => {
    if (!isOpen || !user) return;

    const loadHistory = async () => {
      setLoading(true);
      try {
        Promise.all([fetchChatHistory(user.token)().then(res => {
          if (res) {
            setChats(res);
          }
        }), fetchQueryHistory(user.token)().then((res) => {
          if (res) {
            setQueries(res);
          }
        })]);
      } catch (error) {
        console.error('Error loading chat and query history:', error);
      } finally {
        setLoading(false);
      }
    };

    loadHistory();
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

  const handleQueryClick = (query: Query) => {
    console.log('Query clicked:', query);
    onSelectQuery(query);
  };

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
            {chats.map((chat) => (
              <Box
                key={chat.id}
                onClick={() => handleChatClick(chat)}
                sx={{
                  padding: '16px',
                  cursor: 'pointer',
                  borderBottom: '1px solid rgba(255, 255, 255, 0.1)',
                  backgroundColor: chat.id === selectedChatId ? 'rgba(255, 255, 255, 0.1)' : 'transparent',
                  '&:hover': {
                    backgroundColor: 'rgba(255, 255, 255, 0.05)'
                  }
                }}
              >
                <Typography
                  variant="body2"
                  sx={{
                    color: 'rgba(255, 255, 255, 0.5)',
                    fontSize: '12px',
                    mb: '8px'
                  }}
                >
                  {formatTimestamp(chat.created_time)}
                </Typography>
                <Typography
                  variant="body1"
                  sx={{
                    color: 'rgba(255, 255, 255, 0.87)',
                    fontSize: '14px',
                    lineHeight: '20px'
                  }}
                >
                  {chat.title || 'Untitled Chat'}
                </Typography>
              </Box>
            ))}
            {queries.map((query) => (
              <Box
                key={query.id}
                onClick={() => handleQueryClick(query)}
                sx={{
                  padding: '16px',
                  cursor: 'pointer',
                  borderBottom: '1px solid rgba(255, 255, 255, 0.1)',
                  backgroundColor: query.id === selectedQueryId ? 'rgba(255, 255, 255, 0.1)' : 'transparent',
                  '&:hover': {
                    backgroundColor: 'rgba(255, 255, 255, 0.05)'
                  }
                }}
              >
                <Typography
                  variant="body2"
                  sx={{
                    color: 'rgba(255, 255, 255, 0.5)',
                    fontSize: '12px',
                    mb: '8px'
                  }}
                >
                  {formatTimestamp(query.created_time)}
                </Typography>
                <Typography
                  variant="body1"
                  sx={{
                    color: 'rgba(255, 255, 255, 0.87)',
                    fontSize: '14px',
                    lineHeight: '20px'
                  }}
                >
                  {query.title || 'Untitled Chat'}
                </Typography>
              </Box>
            ))}
          </>
        )}
      </Box>
    </Box>
  );
};

export default ChatHistory; 