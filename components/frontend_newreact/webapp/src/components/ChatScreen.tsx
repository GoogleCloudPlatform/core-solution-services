import { SourceSelector } from './SourceSelector'; // Import the component
import { QueryEngine } from '../lib/types'; // Import the type
import { useState, useEffect } from 'react';
import { Box, Typography, IconButton, Paper, InputBase, Avatar, Select, MenuItem, Modal, Chip, Button } from '@mui/material';
import AddIcon from '@mui/icons-material/Add';
import CloseIcon from '@mui/icons-material/Close';
import DeleteIcon from '@mui/icons-material/Delete';
import UploadIcon from '@mui/icons-material/Upload';
import { useAuth } from '../contexts/AuthContext';
import { createChat, resumeChat, fetchChat, createQuery } from '../lib/api';
import { Chat, QueryReference } from '../lib/types';
import { useModel } from '../contexts/ModelContext';
import UploadModal from './UploadModal';
import '../styles/ChatScreen.css';
import ReactMarkdown from 'react-markdown';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { oneDark } from 'react-syntax-highlighter/dist/esm/styles/prism';
import type { SyntaxHighlighterProps } from 'react-syntax-highlighter';
import { LoadingSpinner } from "@/components/LoadingSpinner"
import DocumentModal from './DocumentModal';

interface ChatMessage {
  text: string;
  isUser: boolean;
  uploadedFile?: string;
  references?: QueryReference[];
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

const ReferenceChip: React.FC<{ reference: QueryReference }> = ({ reference }) => {
  const [showDetails, setShowDetails] = useState(false);

  return (
    <Box sx={{ mb: 1 }}>
      <Button 
        onClick={() => setShowDetails(!showDetails)}
        sx={{ 
          textTransform: 'none',
          p: 1,
          borderRadius: 1,
          border: '1px solid #4a4a4a',
          display: 'flex',
          alignItems: 'center',
          width: '100%',
          justifyContent: 'flex-start',
          color: 'text.primary',
          '&:hover': {
            backgroundColor: 'rgba(255, 255, 255, 0.05)'
          }
        }}
      >
        <Box sx={{ 
          display: 'flex', 
          flexDirection: 'column',
          alignItems: 'flex-start',
          width: '100%'
        }}>
          <Typography variant="body2" sx={{ mb: 0.5 }}>
            {reference.document_url.split('/').pop()}
          </Typography>
          {showDetails && (
            <Typography 
              variant="body2" 
              sx={{ 
                color: 'text.secondary',
                whiteSpace: 'pre-wrap',
                width: '100%',
                textAlign: 'left'
              }}
            >
              {reference.document_text}
            </Typography>
          )}
        </Box>
      </Button>
    </Box>
  );
};

const ChatScreen: React.FC<ChatScreenProps> = ({ currentChat, hideHeader = false, onChatStart, isNewChat = false }) => {
  const [prompt, setPrompt] = useState('');
  const [chatId, setChatId] = useState<string | undefined>(currentChat?.id);
  const [messages, setMessages] = useState<ChatMessage[]>(() =>
    currentChat?.history?.map(h => ({
      text: h.HumanInput || h.AIOutput || '',
      isUser: !!h.HumanInput
    })) || []
  );
  const [showDocumentViewer, setShowDocumentViewer] = useState(false)

  const { user } = useAuth();
  const [isLoading, setIsLoading] = useState(false);

  // Add effect to fetch full chat details when currentChat changes
  useEffect(() => {
    const loadChat = async () => {
      if (currentChat?.id && user) {
        setIsLoading(true);
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
        } finally {
          setIsLoading(false);
        }
      } else {
        // Reset messages when there's no current chat or it's a new chat
        setMessages([]);
        setChatId(undefined);
      }
    };

    loadChat();
  }, [currentChat?.id, user]);

  const [selectedSource, setSelectedSource] = useState<QueryEngine | null>(null);
  const { selectedModel } = useModel();
  const [temperature, setTemperature] = useState(1.0);
  const [isUploadModalOpen, setIsUploadModalOpen] = useState(false);
  const [uploadedFiles, setUploadedFiles] = useState<FileUpload[]>([]);
  const [importUrl, setImportUrl] = useState('');
  const [selectedFile, setSelectedFile] = useState<File | null>(null);

  const handleSelectSource = (source: QueryEngine) => {
    console.log("Selected source:", source);  // Or whatever logic you need
    setSelectedSource(source); // Update the selected source
  };

  const handleSubmit = async () => {
    if (!prompt.trim() || !user) return;

    if (onChatStart) {
      onChatStart();
    }

    const userMessage: ChatMessage = {
      text: prompt,
      isUser: true,
      uploadedFile: selectedFile?.name,
    };
    setMessages(prev => [...prev, userMessage]);
    setIsLoading(true);

    try {
      let response: Chat | undefined;

      // Common parameters
      const chatParams = {
        userInput: prompt,
        llmType: selectedModel.id,
        stream: false,
        temperature: temperature,
        uploadFile: selectedFile || undefined,
        fileUrl: importUrl
      };

      if (chatId) {
        // Continue existing chat
        const chatResponse = await resumeChat(user.token)({
          chatId,
          ...chatParams,
          queryEngineId: selectedSource?.id
        });

        // Only assign if it's a Chat object
        if (chatResponse && !isReadableStream(chatResponse)) {
          response = chatResponse;
        }

      } else if (selectedSource) {
        // Create new chat via query endpoint
        const queryResponse = await createQuery(user.token)({
          engine: selectedSource.id,
          userInput: prompt,
          llmType: selectedModel.id,
          chatMode: true  // Always true - we always want a Chat back
        });

        // Type guard to ensure we have a Chat object
        if (isChat(queryResponse)) {
          response = queryResponse;
        }

      } else {
        // Create new regular chat
        const chatResponse = await createChat(user.token)({
          ...chatParams,
          uploadFile: selectedFile || undefined,
          fileUrl: importUrl,
        });

        // Only assign if it's a Chat object
        if (chatResponse && !isReadableStream(chatResponse)) {
          response = chatResponse;
        }
      }

      // Only proceed if we got a valid Chat object
      if (response?.id) {
        setChatId(response.id);
      }

      if (response?.history) {
        let newMessages: ChatMessage[] = [];
        for (let i = 0; i < response.history.length; i++) {
          const historyItem = response.history[i];
          if (historyItem.HumanInput) {
            let uploadedFile: string | undefined;

            if (i + 2 < response.history.length) {
              if (response.history[i + 2].UploadedFile) {
                uploadedFile = response.history[i + 2].UploadedFile;
              }
            }

            newMessages = [...newMessages, {
              text: historyItem.HumanInput,
              isUser: true,
              uploadedFile: uploadedFile,
            }];
          } else if (historyItem.AIOutput) {
            newMessages = [...newMessages, {
              text: historyItem.AIOutput,
              isUser: false,
              references: historyItem.QueryReferences || [],
            }];
          } else if (historyItem.UploadedFile) {
            continue;
          }
        }

        setMessages(newMessages);
      } else {
        // Handle the case where there's no history in the response (e.g., an error occurred)
        console.error("API response does not contain 'history' property:", response)
      }

      setSelectedFile(null); // Reset file
      setImportUrl('');      // Reset URL
      setPrompt('');
    } catch (error) {
      console.error('Error in chat:', error);
      const errorMessage: ChatMessage = {
        text: 'An error occurred while processing your request.',
        isUser: false
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
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

  //console.log({ messages })

  return (
    <Box className="chat-screen">
      {!hideHeader && (
        <Box className="chat-header" sx={{
          display: 'flex',
          alignItems: 'center',
          p: 2,
          width: '100%',
          borderBottom: '1px solid #2f2f2f',
          flexShrink: 0,
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

      <Box sx={{
        width: '100%',
        maxWidth: '800px',
        margin: '0 auto',
        height: '100%',
        display: 'flex',
        flexDirection: 'column',
        flexGrow: 1,
        minHeight: 0,
      }}>
        <Box className="chat-messages" sx={{
          flexGrow: 1,
          overflowY: 'auto',
          minHeight: 0,
        }}>
          {messages.map((message, index) => (
            <Box key={index}>
              <Box
                className={`message ${message.isUser ? 'user-message' : 'assistant-message'}`}
                sx={{
                  backgroundColor: message.isUser ? '#343541' : 'transparent',
                  borderRadius: message.isUser ? '0.5rem 0.5rem 0 0.5rem' : '0.5rem 0.5rem 0.5rem 0',
                  padding: '0.75rem 1rem',
                  marginBottom: '0.5rem',
                  alignSelf: message.isUser ? 'flex-end' : 'flex-start',
                  maxWidth: '70%',
                  display: 'flex',
                  flexDirection: message.isUser ? 'row-reverse' : 'row',
                  alignItems: 'flex-start',
                  gap: '0.5rem',
                }}
              >
                {message.isUser ? (
                  <Typography sx={{ color: '#fff', textAlign: 'right' }}>
                    {message.text}
                  </Typography>
                ) : (
                  <>
                    <Avatar
                      src="/assets/images/gemini-icon.png"
                      className="message-avatar"
                      sx={{ backgroundColor: 'transparent' }}
                    />
                    <Box sx={{ flex: 1 }}>
                      <ReactMarkdown
                        components={{
                          code({ node, className, children }) {
                            const match = /language-(\w+)/.exec(className || '');
                            const language = match ? match[1] : '';

                            if (!match) {
                              return (
                                <code className={className}>
                                  {children}
                                </code>
                              );
                            }

                            return (
                              <SyntaxHighlighter
                                style={oneDark}
                                language={language}
                                PreTag="div"
                              >
                                {String(children).replace(/\n$/, '')}
                              </SyntaxHighlighter>
                            );
                          },
                          p: ({ children }) => (
                            <Typography component="p" sx={{ mb: 1 }}>
                              {children}
                            </Typography>
                          ),
                          h1: ({ children }) => (
                            <Typography variant="h5" sx={{ mb: 2, mt: 2 }}>
                              {children}
                            </Typography>
                          ),
                          h2: ({ children }) => (
                            <Typography variant="h6" sx={{ mb: 2, mt: 2 }}>
                              {children}
                            </Typography>
                          ),
                          ul: ({ children }) => (
                            <Box component="ul" sx={{ pl: 2, mb: 2 }}>
                              {children}
                            </Box>
                          ),
                          ol: ({ children }) => (
                            <Box component="ol" sx={{ pl: 2, mb: 2 }}>
                              {children}
                            </Box>
                          ),
                          li: ({ children }) => (
                            <Box component="li" sx={{ mb: 1 }}>
                              {children}
                            </Box>
                          ),
                        }}
                      >
                        {message.text}
                      </ReactMarkdown>
                      
                      {/* Add references display */}
                      {!message.isUser && message.references && message.references.length > 0 && (
                        <Box sx={{ 
                          mt: 2, 
                          pt: 2, 
                          borderTop: '1px solid #4a4a4a'
                        }}>
                          <Typography variant="subtitle2" sx={{ mb: 1, color: 'text.secondary' }}>
                            References:
                          </Typography>
                          {message.references.map((reference, idx) => (
                            <ReferenceChip key={idx} reference={reference} />
                          ))}
                        </Box>
                      )}
                    </Box>
                  </>
                )}
                <DocumentModal open={showDocumentViewer} onClose={() => setShowDocumentViewer(false)} selectedFile={selectedFile} />
              </Box>
              <Box key={index} className={`message ${message.isUser ? 'user-message' : 'assistant-message'}`} sx={{
                alignSelf: 'flex-end',
                maxWidth: '70%',
                display: 'flex',
                flexDirection: 'row-reverse',
                alignItems: 'flex-start',
              }}>
                {/* ... existing JSX (Avatar, Typography for message.text) */}

                {/* Conditionally render the chip ONLY if message.uploadedFile exists */}
                {message.isUser && message.uploadedFile && ( //  Only render if uploadedFile is present
                  <Box className="file-chip-container" sx={{
                    alignSelf: 'flex-end',
                    display: 'flex',
                    flexDirection: 'row-reverse',
                    alignItems: 'flex-start',
                  }}>
                    <Button onClick={() => setShowDocumentViewer(true)}>
                      <Chip
                        label={message.uploadedFile}
                        size="small"
                        variant="outlined"
                      />
                    </Button>
                    {/* <DocumentModal open={showDocumentViewer} onClose={() => setShowDocumentViewer(false)} selectedFile={selectedFile} /> */}
                  </Box>
                )}
              </Box>
            </Box>
          ))}
          {isLoading && (
            <LoadingSpinner />
          )}
        </Box>

        <Box className="chat-input-container" sx={{
          p: 2,
          flexShrink: 0,
          position: 'sticky',
          bottom: 0
        }}>
          <Paper className="chat-input">
            {(selectedFile || importUrl) && (
              <>
                <Box className="file-chip-container">
                  <Button onClick={() => setShowDocumentViewer(true)}>
                    <Chip
                      label={selectedFile ? selectedFile.name : importUrl}
                      onDelete={handleRemoveSelectedFile}
                      size="small"
                      variant="outlined"
                    />
                  </Button>
                </Box>
                <DocumentModal open={showDocumentViewer} onClose={() => setShowDocumentViewer(false)} selectedFile={selectedFile} />
              </>
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

// Helper functions to check response types
const isReadableStream = (value: any): value is ReadableStream => {
  return value instanceof ReadableStream;
};

const isChat = (value: any): value is Chat => {
  return value &&
    typeof value === 'object' &&
    'id' in value &&
    'history' in value;
};

export default ChatScreen; 