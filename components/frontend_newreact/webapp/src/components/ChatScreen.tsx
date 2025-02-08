import { SourceSelector } from './SourceSelector'; // Import the component
import { QueryEngine } from '../lib/types'; // Import the type
import { useState, useEffect } from 'react';
import { Box, Typography, IconButton, Paper, InputBase, Avatar, Select, MenuItem, Modal, Chip } from '@mui/material';
import AddIcon from '@mui/icons-material/Add';
import CloseIcon from '@mui/icons-material/Close';
import DeleteIcon from '@mui/icons-material/Delete';
import UploadIcon from '@mui/icons-material/Upload';
import { useAuth } from '../contexts/AuthContext';
import { createChat, resumeChat, fetchChat } from '../lib/api';
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
  hideHeader?: boolean;
  onChatStart?: () => void;
  isNewChat?: boolean;
}

const ChatScreen: React.FC<ChatScreenProps> = ({ currentChat, hideHeader = false, onChatStart, isNewChat = false }) => {
  const [prompt, setPrompt] = useState('');
  const [chatId, setChatId] = useState<string | undefined>(currentChat?.id);
  const [messages, setMessages] = useState<ChatMessage[]>(() =>
    currentChat?.history?.map(h => ({
      text: h.HumanInput || h.AIOutput || '',
      isUser: !!h.HumanInput
    })) || []
  );

  const { user } = useAuth();

  // Add effect to fetch full chat details when currentChat changes
  useEffect(() => {
    const loadChat = async () => {
      if (currentChat?.id && user) {
        try {
          const fullChat = await fetchChat(user.token, currentChat.id)();
          if (fullChat) {
            setMessages(
              fullChat.history.map(h => ({
                text: h.HumanInput || h.AIOutput || '',
                isUser: !!h.HumanInput
              }))
            );
            setChatId(fullChat.id);
          }
        } catch (error) {
          console.error('Error loading chat:', error);
        }
      }
    };

    loadChat();
  }, [currentChat?.id, user]);

  // #TODO use selected source for query calls when selected by user
  const [selectedKnowledgeSource, setSelectedKnowledgeSource] = useState<QueryEngine | null>(null);
  const { selectedModel } = useModel();
  const [temperature, setTemperature] = useState(1.0);
  const [isUploadModalOpen, setIsUploadModalOpen] = useState(false);
  const [uploadedFiles, setUploadedFiles] = useState<FileUpload[]>([]);
  const [importUrl, setImportUrl] = useState('');
  const [selectedFile, setSelectedFile] = useState<File | null>(null);

  const handleSelectSource = (source: QueryEngine) => {
    console.log("Selected source:", source);  // Or whatever logic you need
    setSelectedKnowledgeSource(source); // Update the selected source
  };

  const handleSubmit = async () => {
    if (!prompt.trim() || !user) return;

    // Call onChatStart callback when chat begins
    if (onChatStart) {
      onChatStart();
    }

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
          llmType: selectedModel.id,
          stream: false,
          temperature: temperature
        });
      } else {
        // Create new chat
        response = await createChat(user.token)({
          userInput: prompt,
          llmType: selectedModel.id,
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
  };

  const handleFileSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
    const files = event.target.files;
    if (files && files[0]) {
      console.log('File selected:', files[0].name);
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

  const handleAddFiles = () => {
    handleCloseUploadModal();
  };

  const handleRemoveSelectedFile = () => {
    setSelectedFile(null);
    setImportUrl('');
  };

  return (
    <Box className="chat-screen">
      {!hideHeader && (
        <Box className="chat-header" sx={{
          display: 'flex',
          alignItems: 'center',
          p: 2,
          width: '100%',
          borderBottom: '1px solid #2f2f2f',
        }}>
          <Box sx={{ 
            display: 'flex',
            alignItems: 'center',
            gap: 2,
          }}>
            <Typography variant="h6">
              {currentChat?.title || 'New Chat'}
            </Typography>
            <SourceSelector
              onSelectSource={handleSelectSource}
            />
          </Box>
        </Box>
      )}
      
      {/* Chat content container with width constraint */}
      <Box sx={{
        width: '100%',
        maxWidth: '800px',
        margin: '0 auto',
        height: '100%',
        display: 'flex',
        flexDirection: 'column',
      }}>
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
            {(selectedFile || importUrl) && (
              <Box className="file-chip-container">
                <Chip
                  label={selectedFile ? selectedFile.name : importUrl}
                  onDelete={handleRemoveSelectedFile}
                  size="small"
                  variant="outlined"
                />
              </Box>
            )}
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
      </Box>

      <Modal
        open={isUploadModalOpen}
        onClose={handleCloseUploadModal}
        aria-labelledby="upload-modal-title"
      >
        <Box>
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
        </Box>
      </Modal>
    </Box>
  );
};

export default ChatScreen; 