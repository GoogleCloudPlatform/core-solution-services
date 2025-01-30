import { useState } from 'react';
import { Box, Typography, IconButton, Paper, InputBase, Avatar, Select, MenuItem } from '@mui/material';
import AddIcon from '@mui/icons-material/Add';
import KeyboardArrowDownIcon from '@mui/icons-material/KeyboardArrowDown';

interface ChatMessage {
  text: string;
  isUser: boolean;
}

const ChatScreen = () => {
  const [prompt, setPrompt] = useState('');

  const chatMessages: ChatMessage[] = [
    {
      text: 'Nec lacus vestibulum at scelerisque aenean ultricies nascetur libero vestibulum fusce cum a sem suscipit dignissim senectus suspendisse suspendisse consectetur cubilia fringilla at adipiscing sem fermentum libero a a adipiscing.Ad duis malesuada scelerisque ipsum ac integer parturient blandit ac gravida mus dui quis. When was Google founded?',
      isUser: true
    },
    {
      text: 'Google was founded on September 4, 1998, by Larry Page and Sergey Brin in Menlo Park, California',
      isUser: false
    }
  ];

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
        {chatMessages.map((message, index) => (
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
            fullWidth
          />
          <IconButton>
            <AddIcon />
          </IconButton>
        </Paper>
      </Box>
    </Box>
  );
};

export default ChatScreen; 