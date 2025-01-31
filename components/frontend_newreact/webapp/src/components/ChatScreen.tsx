import { useState } from 'react';
import { Box, Typography, IconButton, Paper, InputBase, Avatar, Select, MenuItem } from '@mui/material';
import AddIcon from '@mui/icons-material/Add';
import KeyboardArrowDownIcon from '@mui/icons-material/KeyboardArrowDown';
import { useAuth } from '../contexts/AuthContext';
import { createChat, resumeChat } from '../lib/api';
import { Chat } from '../lib/types';

interface ChatMessage {
  text: string;
  isUser: boolean;
}

interface ChatScreenProps {
  currentChat?: Chat;
}

const ChatScreen = ({ currentChat }: ChatScreenProps) => {
  const [prompt, setPrompt] = useState('');
  const [messages, setMessages] = useState<ChatMessage[]>(() => 
    // Initialize messages from currentChat if it exists
    currentChat?.history.map(h => ({
      text: h.HumanInput || h.AIOutput || '',
      isUser: !!h.HumanInput
    })) || []
  );
  const [chatId, setChatId] = useState<string | undefined>(currentChat?.id);
  const { user } = useAuth();

  const handleSubmit = async () => {
    if (!prompt.trim() || !user) return;

    // Add user message to chat
    const userMessage: ChatMessage = {
      text: prompt,
      isUser: true
    };
    setMessages(prev => [...prev, userMessage]);

    try {
      let response;
      
      if (chatId) {
        // Continue existing chat
        response = await resumeChat(user.token)({
          chatId,
          userInput: prompt,
          llmType: 'chat-bison', // You may want to make this configurable
          stream: false
        });
      } else {
        // Create new chat
        response = await createChat(user.token)({
          userInput: prompt,
          llmType: 'chat-bison',
          uploadFile: null,
          fileUrl: '',
          stream: false
        });

        // Store the chat ID for future messages
        if (response && 'id' in response) {
          setChatId(response.id);
        }
      }

      // Add AI response to chat
      if (response && 'history' in response) {
        const aiMessage: ChatMessage = {
          text: response.history[response.history.length - 1]?.AIOutput || 'No response',
          isUser: false
        };
        setMessages(prev => [...prev, aiMessage]);
      }

      // Clear prompt
      setPrompt('');
    } catch (error) {
      console.error('Error in chat:', error);
      // You might want to show an error message to the user here
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  return (
    <Box className="chat-screen">
      <Box className="chat-header">
        <Typography variant="h6">
          {currentChat?.title || 'New Chat'}
        </Typography>
        <Select
          value="Default Chat"
          variant="standard"
          IconComponent={KeyboardArrowDownIcon}
          className="chat-type-select"
        >
          <MenuItem value="Default Chat">Default Chat</MenuItem>
        </Select>
      </Box>
      <Box className="chat-messages">
        {messages.map((message, index) => (
          <Box key={index} className={`message ${message.isUser ? 'user-message' : 'assistant-message'}`}>
            <Avatar className="message-avatar" />
            <Typography>{message.text}</Typography>
          </Box>
        ))}
      </Box>
      <Box className="chat-input-container">
        <Paper className="chat-input">
          <InputBase
            placeholder="Enter your prompt"
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
            onKeyPress={handleKeyPress}
            fullWidth
            multiline
          />
          <IconButton onClick={handleSubmit}>
            <AddIcon />
          </IconButton>
        </Paper>
      </Box>
    </Box>
  );
};

export default ChatScreen; 