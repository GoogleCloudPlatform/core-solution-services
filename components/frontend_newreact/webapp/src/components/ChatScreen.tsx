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
import { Snackbar } from '@mui/material'; // Import Snackbar for notifications
import ContentCopyIcon from '@mui/icons-material/ContentCopy';
import Tooltip from '@mui/material/Tooltip';
import ReferenceChip from "@/components/ReferenceChip"
import { useRef } from 'react';

interface ChatMessage {
  text: string;
  isUser: boolean;
  uploadedFile?: string;
  references?: QueryReference[];
  fileUrl?: string // Add fileUrl property
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
  showWelcome: boolean;
}

const ChatScreen: React.FC<ChatScreenProps> = ({ currentChat, hideHeader = false, onChatStart, isNewChat = false, showWelcome = true }) => {
  const [prompt, setPrompt] = useState('');
  console.log({ currentChat })
  const [chatId, setChatId] = useState<string | undefined>(currentChat?.id);
  const [messages, setMessages] = useState<ChatMessage[]>(() =>
    currentChat?.history?.map(h => ({
      text: h.HumanInput || h.AIOutput || '',
      isUser: !!h.HumanInput,
      references: h.QueryReferences || [],
      uploadedFile: h.UploadedFile || '',
      fileUrl: h.FileURL || ''
    })) || []
  );
  const [showDocumentViewer, setShowDocumentViewer] = useState(false)

  const { user } = useAuth();
  const [isLoading, setIsLoading] = useState(false);
  const [showCopyIcon, setShowCopyIcon] = useState(false); // State for icon visibility
  const [tooltipOpen, setTooltipOpen] = useState(false);   // State for tooltip
  const [iconClicked, setIconClicked] = useState(false);    // State for click effect

  const handleCopyClick = (text: string) => {
    navigator.clipboard.writeText(text)
      .then(() => {
        setTooltipOpen(true);
        setIconClicked(true);
        setTimeout(() => {
          setIconClicked(false);
        }, 200);
      })
      .catch(err => {
        console.error('Failed to copy: ', err);
      });
  };

  const messagesEndRef = useRef<HTMLDivElement | null>(null);
  const inputRef = useRef<HTMLInputElement>(null);


  // Add effect to fetch full chat details when currentChat changes
  useEffect(() => {
    const loadChat = async () => {
      if (currentChat?.id && user && !showWelcome) {
        setIsLoading(true);
        try {
          const fullChat = await fetchChat(user.token, currentChat.id)();
          if (fullChat) {
            setMessages(
              fullChat.history.map(h => ({
                text: h.HumanInput || h.AIOutput || '',
                isUser: !!h.HumanInput,
                references: h.QueryReferences || []
              }))
            );
            console.log("Setting 1")
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
  const [showError, setShowError] = useState<Record<string, boolean>>({}); // State to track error visibility for each file

  const handleSelectSource = (source: QueryEngine) => {
    console.log("Selected source:", source);  // Or whatever logic you need
    setSelectedSource(source); // Update the selected source
  };

  const handleSubmit = async () => {
    if (!prompt.trim() || !user) return;

    if (onChatStart) {
      onChatStart();
    }

    let uploadedFileName = selectedFile?.name;
    if (importUrl) {
      uploadedFileName = importUrl.split('/').pop()
      if (importUrl.startsWith("gs://")) {
        uploadedFileName = importUrl.replace("gs://", "").split("/").pop()
      }
    }


    const userMessage: ChatMessage = {
      text: prompt,
      isUser: true,
      uploadedFile: selectedFile?.name,
      fileUrl: importUrl
    };
    setMessages(prev => [...prev, userMessage]);
    setPrompt('');
    setTimeout(() => {
      messagesEndRef.current?.scrollIntoView({ behavior: 'smooth', block: 'center' });
    }, 100);


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
          queryEngineId: selectedSource?.id || undefined
        });

        // Only assign if it's a Chat object
        if (chatResponse && !isReadableStream(chatResponse)) {
          response = chatResponse;
        }

      } else if (selectedSource && selectedSource.id != "default-chat") {
        // Create new chat via query endpoint
        const queryResponse = await createQuery(user.token)({
          engine: selectedSource.id,
          userInput: prompt,
          llmType: selectedModel.id,
          chatMode: true  // Always true - we always want a Chat back
        });
        response = queryResponse
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

      console.log("api response", response)

      // Only proceed if we got a valid Chat object
      if (response?.id) {
        console.log("Setting 2")
        setChatId(response.id);
      }

      if (response?.history) {
        let newMessages: ChatMessage[] = [];

        for (let i = 0; i < response.history.length; i++) {
          const historyItem = response.history[i];
          if (historyItem.HumanInput) {
            let uploadedFile: string | undefined;
            let fileUrl: string | undefined;

            if (i + 2 < response.history.length) {
              if (response.history[i + 2].UploadedFile) {
                uploadedFile = response.history[i + 2].UploadedFile;
              } else if (response.history[i + 2].FileURL) {
                fileUrl = response.history[i + 2].FileURL;
              }
            }
            newMessages.push(
              {
                text: historyItem.HumanInput,
                isUser: true,
                uploadedFile: uploadedFile,
                fileUrl: fileUrl
              })
          } else if (historyItem.AIOutput) {
            newMessages.push(
              {
                text: historyItem.AIOutput,
                isUser: false,
              })
          } else if (historyItem.QueryReferences) {
            newMessages.push(
              {
                text: "",
                isUser: false,
                references: historyItem.QueryReferences
              })
          } else if (historyItem.UploadedFile) {
            continue;
          } else if (historyItem.FileURL) {
            continue;
          }
        }


        console.log("new messages", newMessages)

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
      // TODO: Make api call for error handling
      const newFiles = Array.from(files).map(file => ({
        name: file.name,
        // Simulating error comment when not testing
        //error: 'simulated error',
        progress: 0
      }));
      setUploadedFiles(prev => [...prev, ...newFiles]);
    }
  };

  const handleRemoveFile = (fileName: string) => {
    setUploadedFiles(prev => prev.filter(file => file.name !== fileName));

    // Add this line to clear the corresponding error message in UploadModal:
    setShowError?.((prevErrors) => {   // Use optional chaining in case setShowError isn't immediately available
      const newErrors = { ...prevErrors };
      delete newErrors[fileName];  // Remove the error for the deleted file
      return newErrors;
    });
  };

  const handleAddFiles = () => {
    handleCloseUploadModal();
  };

  const handleRemoveSelectedFile = () => {
    setSelectedFile(null);
    setImportUrl('');
  };

  //console.log({ messages })
  console.log({ hideHeader, showWelcome })
  console.log({ messages })

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
        justifyContent: 'flex-end'
      }}>
        {!showWelcome && (
          <Box className="chat-messages" sx={{
            flexGrow: 1,
            // overflowY: 'auto',
            // minHeight: '100vh',
            mx: 2
          }}>
            {messages.map((message, index) => {
              console.log({ message, index })
              return (
                <Box key={index}
                  onMouseEnter={() => setShowCopyIcon(true)}  // Show icon on hover
                  onMouseLeave={() => { setShowCopyIcon(false); setTooltipOpen(false); }}  // Hide icon and close tooltip when mouse leaves
                  onClick={() => { if (!message.isUser && message.text) handleCopyClick(message.text); }} // Removed inline onMouseEnter/Leave
                  sx={{
                    // other styles
                    position: 'relative', // Needed for Tooltip positioning
                    marginRight: 'auto'
                  }}

                >
                  <Box
                    className={message.isUser ? 'user-message' : 'assistant-message'}
                    sx={{
                      backgroundColor: message.isUser ? '#343541' : 'transparent',
                      borderRadius: message.isUser ? '0.5rem 0.5rem 0 0.5rem' : '0.5rem 0.5rem 0.5rem 0',
                      padding: '0.75rem 1rem',
                      marginBottom: '0.5rem',
                      alignSelf: message.isUser ? 'flex-end' : 'flex-start',
                      textAlign: message.isUser ? 'right' : 'left',
                      maxWidth: '100%',
                      display: 'flex',
                      flexDirection: message.isUser ? 'row-reverse' : 'row',
                      alignItems: 'flex-start',
                      gap: '0.5rem',
                    }}
                  // ref={index === messages.length - 1 && message.isUser ? messagesEndRef : null} // Attach reference to the last user messsage
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
                              <Typography variant="subtitle2" sx={{ mb: 1 }}>
                                References:
                              </Typography>
                              {message.references.map((reference, idx) => (
                                <ReferenceChip key={idx} reference={reference} onCopy={handleCopyClick} />
                              ))}
                            </Box>
                          )}
                        </Box>
                      </>
                    )}
                    <DocumentModal open={showDocumentViewer} onClose={() => setShowDocumentViewer(false)} selectedFile={selectedFile} />
                  </Box>
                  <Box key={index} className={`message ${message.isUser ? 'user-message' : 'assistant-message'}`}
                    onClick={() => { if (!message.isUser && message.text) handleCopyClick(message.text); }} // Call handleCopyClick with message text

                    sx={{
                      alignSelf: 'flex-end',
                      maxWidth: '100%',
                      display: 'flex',
                      flexDirection: 'row-reverse',
                      alignItems: 'flex-start',
                    }}>
                    {/* ... existing JSX (Avatar, Typography for message.text) */}

                    {/* Conditionally render the chip ONLY if message.uploadedFile exists */}
                    {(message.isUser && (message.uploadedFile || message.fileUrl)) && (
                      <Box className="file-chip-container" sx={{
                        alignSelf: 'flex-end',
                        display: 'flex',
                        flexDirection: 'row-reverse',
                        alignItems: 'flex-start',
                      }}>
                        <Button onClick={() => setShowDocumentViewer(true)}>
                          <Chip
                            label={message.uploadedFile || message.fileUrl}
                            size="small"
                            variant="outlined"
                          />
                        </Button>
                      </Box>
                    )}


                    {showCopyIcon && !message.isUser && !message.references && (
                      <Tooltip
                        open={tooltipOpen}
                        onClose={() => setTooltipOpen(false)}
                        title="Copied!"
                        placement="top"
                        leaveDelay={200} // Adjust as needed
                      >
                        <IconButton
                          sx={{
                            position: 'absolute',
                            left: -4,
                            bottom: -4,
                            backgroundColor: iconClicked ? '#2979ff' : 'transparent', // Blue background on click
                            borderRadius: '50%', // Make it circular
                            transition: 'background-color 0.2s ease', // Smooth transition
                            padding: '4px',
                            "&:hover": {
                              backgroundColor: '#e3f2fd' // light blue on hover
                            }

                          }}
                        >
                          <ContentCopyIcon sx={{ color: iconClicked ? 'white' : '#9e9e9e', fontSize: '16px' }} />
                        </IconButton>

                      </Tooltip>
                    )}
                  </Box>
                </Box>
              )
            })}
            {isLoading && (
              <LoadingSpinner />
            )}
          </Box>
        )}

        <Box className={`chat-input-container ${showWelcome ? 'welcome-mode' : ''}`} sx={{
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
            setUploadedFiles={setUploadedFiles} // 
            showError={showError}
            setShowError={setShowError}
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

export default ChatScreen; 