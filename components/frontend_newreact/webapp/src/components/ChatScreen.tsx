import { useState } from 'react';
import { Box, Typography, IconButton, Paper, InputBase, Avatar, Select, MenuItem, Modal } from '@mui/material';
import AddIcon from '@mui/icons-material/Add';
import KeyboardArrowDownIcon from '@mui/icons-material/KeyboardArrowDown';
import CloseIcon from '@mui/icons-material/Close';
import DeleteIcon from '@mui/icons-material/Delete';
import UploadIcon from '@mui/icons-material/Upload';
import { useAuth } from '../contexts/AuthContext';
import { createChat, resumeChat } from '../lib/api';
import { Chat } from '../lib/types';
import { useModel } from '../contexts/ModelContext';
import UploadModal from './UploadModal';
import '../styles/ChatScreen.css';

interface ChatMessage {
  text: string;
  isUser: boolean;
}

interface FileUpload {
  name: string;
  progress?: number;
  error?: string;
}

interface ChatScreenProps {
  currentChat?: Chat;
}

const ChatScreen: React.FC<ChatScreenProps> = ({ currentChat }) => {
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
  const { selectedModel } = useModel();
  const [temperature, setTemperature] = useState(1.0);
  const [isUploadModalOpen, setIsUploadModalOpen] = useState(false);
  const [uploadedFiles, setUploadedFiles] = useState<FileUpload[]>([]);
  const [importUrl, setImportUrl] = useState('');
  const [selectedFile, setSelectedFile] = useState<File | null>(null);

  const handleSubmit = async () => {
    if (!prompt.trim() || !user) return;

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
          llmType: selectedModel.name,
          stream: false,
          temperature: temperature
        });
      } else {
        // Create new chat
        response = await createChat(user.token)({
          userInput: prompt,
          llmType: selectedModel.name,
          uploadFile: selectedFile || undefined,
          fileUrl: importUrl,
          stream: false,
          temperature: temperature
        });

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

      setPrompt('');
    } catch (error) {
      console.error('Error in chat:', error);
      // Add error message to chat
      const errorMessage: ChatMessage = {
        text: 'An error occurred while processing your request.',
        isUser: false
      };
      setMessages(prev => [...prev, errorMessage]);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  const handleCloseUploadModal = () => {
    setIsUploadModalOpen(false);
    setUploadedFiles([]);
    setImportUrl('');
    setSelectedFile(null);
  };

  const handleFileSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
    const files = event.target.files;
    if (files && files[0]) {
      setSelectedFile(files[0]);
      const newFiles = Array.from(files).map(file => ({
        name: file.name,
        progress: 0
      }));
      setUploadedFiles(prev => [...prev, ...newFiles]);
    }
  };

  const handleRemoveFile = (fileName: string) => {
    setUploadedFiles(prev => prev.filter(file => file.name !== fileName));
  };

  const handleAddFiles = async () => {
    if (!user) return;

    try {
      // Create a new chat with the file or URL
      const response = await createChat(user.token)({
        userInput: "I've uploaded a new file. Please help me analyze it.",
        llmType: selectedModel.name,
        uploadFile: selectedFile || undefined,
        fileUrl: importUrl,
        stream: false,
        temperature: temperature
      });

      // If we get a successful response, update the chat ID
      if (response && 'id' in response) {
        setChatId(response.id);
        
        // Add system message about file upload
        const systemMessage: ChatMessage = {
          text: `File ${selectedFile ? selectedFile.name : importUrl} has been uploaded successfully.`,
          isUser: false
        };
        setMessages(prev => [...prev, systemMessage]);
      }

      // Clear the upload state
      handleCloseUploadModal();
      setSelectedFile(null);
    } catch (error) {
      console.error('Error uploading file:', error);
      // Update the file status to show error
      if (selectedFile) {
        setUploadedFiles(prev => 
          prev.map(file => 
            file.name === selectedFile.name 
              ? { ...file, error: 'Upload failed' }
              : file
          )
        );
      }
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
            onKeyDown={handleKeyDown}
            fullWidth
            multiline
          />
          <IconButton onClick={() => setIsUploadModalOpen(true)}>
            <AddIcon />
          </IconButton>
        </Paper>
      </Box>

      <Modal
        open={isUploadModalOpen}
        onClose={handleCloseUploadModal}
        aria-labelledby="upload-modal-title"
      >
        <UploadModal
          open={isUploadModalOpen}
          onClose={handleCloseUploadModal}
          uploadedFiles={uploadedFiles}
          onFileSelect={handleFileSelect}
          onRemoveFile={handleRemoveFile}
          importUrl={importUrl}
          onImportUrlChange={(url) => setImportUrl(url)}
          onAdd={handleAddFiles}
        />
      </Modal>
    </Box>
  );
};

export default ChatScreen; 