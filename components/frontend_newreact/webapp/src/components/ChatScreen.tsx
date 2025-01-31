import { useState } from 'react';
import { Box, Typography, IconButton, Paper, InputBase, Avatar, Select, MenuItem } from '@mui/material';
import AddIcon from '@mui/icons-material/Add';
import KeyboardArrowDownIcon from '@mui/icons-material/KeyboardArrowDown';
import { useAuth } from '../contexts/AuthContext';
import { createChat } from '../lib/api';

interface ChatMessage {
  text: string;
  isUser: boolean;
}

const ChatScreen = () => {
  const [prompt, setPrompt] = useState('');
  const [messages, setMessages] = useState<ChatMessage[]>([]);
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
      // Make API call to create chat
      const response = await createChat(user.token)({
        userInput: prompt,
        llmType: 'chat-bison', // You may want to make this configurable
        uploadFile: null,
        fileUrl: '',
        stream: false
      });

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
      console.error('Error creating chat:', error);
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
        <Typography variant="h6">Topical Gist</Typography>
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