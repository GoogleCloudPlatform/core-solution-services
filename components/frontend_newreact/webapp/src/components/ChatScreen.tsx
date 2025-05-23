import { SourceSelector } from './SourceSelector'; // Import the component
import { QueryEngine } from '../lib/types'; // Import the type
import { useState, useEffect, useLayoutEffect, useRef } from 'react';
import { Box, Typography, IconButton, Paper, InputBase, Avatar, Modal, Chip, Button, Snackbar, Tooltip } from '@mui/material';
import AttachFileIcon from '@mui/icons-material/AttachFile';
import AddIcon from '@mui/icons-material/Add';
import CloseIcon from '@mui/icons-material/Close';
import DeleteIcon from '@mui/icons-material/Delete';
import UploadIcon from '@mui/icons-material/Upload';
import ContentCopyIcon from '@mui/icons-material/ContentCopy';
import BarChartIcon from '@mui/icons-material/BarChart'; // Icon for the "Create a graph" toggle
import { useAuth } from '../contexts/AuthContext';
import { generateChatResponse, createEmptyChat, createChat, resumeChat, fetchChat, createQuery, generateChatSummary } from '../lib/api';
import { Chat, QueryReference } from '../lib/types';
import { useModel } from '../contexts/ModelContext';
import UploadModal from './UploadModal';
import '../styles/ChatScreen.css';
import ReactMarkdown from 'react-markdown';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { oneDark } from 'react-syntax-highlighter/dist/esm/styles/prism';
import type { SyntaxHighlighterProps } from 'react-syntax-highlighter';
import { LoadingSpinner } from "../../src/components/LoadingSpinner";
import DocumentModal from './DocumentModal';
import ReferenceChip from "../../src/components/ReferenceChip";
import '@/styles/ChatScreen.css';
import { getStorage, ref, getDownloadURL } from "firebase/storage";

interface ChatMessage {
  text: string;
  isUser: boolean;
  title?: string;
  uploadedFile?: string;
  references?: QueryReference[];
  fileUrl?: string; // Add fileUrl property
  fileType?: string // Add fileType Property
  imageBase64?: string; // To store the base64-encoded image
  showFile?: File;
  attachId?: string;
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
  isTest?: boolean;
}

const ChatScreen: React.FC<ChatScreenProps> = ({
  currentChat,
  hideHeader = false,
  onChatStart,
  isNewChat = false,
  showWelcome = true,
  isTest = false,
}) => {
  const [prompt, setPrompt] = useState('');
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
  const [showDocumentViewer, setShowDocumentViewer] = useState(false);
  const { user } = useAuth();
  const [isLoading, setIsLoading] = useState(false);
  // Removed global showCopyIcon state
  const [hoveredMessageIndex, setHoveredMessageIndex] = useState<number | null>(null); // New state for tracking hovered message index
  const [tooltipOpen, setTooltipOpen] = useState(false);   // State for tooltip
  const [iconClicked, setIconClicked] = useState(false);   // State for click effect
  const [graphEnabled, setGraphEnabled] = useState<boolean>(isTest ? true : false);
  const [copiedMessageIndex, setCopiedMessageIndex] = useState<number | null>(null);

  // Ref for the scrollable container
  const chatMessagesRef = useRef<HTMLDivElement | null>(null);
  // Ref for the last rendered message element
  const messagesEndRef = useRef<HTMLDivElement | null>(null);
  const fileToBase64 = (file: File): Promise<string> => {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.readAsDataURL(file);
      reader.onload = () => {
        const base64String = (reader.result as string).split(',')[1]; // remove data:...;base64,
        resolve(base64String);
      };
      reader.onerror = error => reject(error);
    });
  };
  const handleCopyClick = (text: string, index: number) => {
    navigator.clipboard.writeText(text)
      .then(() => {
        // Set the index of the message that was copied
        setCopiedMessageIndex(index);

        // Clear the copied message index after a brief delay (e.g., 2 seconds)
        setTimeout(() => {
          setCopiedMessageIndex(null);
        }, 2000);
      })
      .catch(err => {
        console.error('Failed to copy: ', err);
      });
  };
  // Add effect to fetch full chat details when currentChat changes
  useEffect(() => {
    const loadChat = async () => {
      if (currentChat?.id && user && !showWelcome) {
        setIsLoading(true);
        try {
          const fullChat = await fetchChat(user.token, currentChat.id)();
          if (fullChat) {
            let newMessages = messagesFromHistory(fullChat.history);
            setMessages(newMessages);
            setChatId(fullChat.id);
          }
        } catch (error) {
          console.error('Error loading chat:', error);
        } finally {
          setIsLoading(false);
        }
      } else {
        // For new chats (no currentChat id), do not reset messages.
      }
    };

    loadChat();
  }, [currentChat?.id, user, showWelcome]);

  const [selectedSource, setSelectedSource] = useState<QueryEngine | null>(null);
  const { selectedModel } = useModel();
  const [temperature, setTemperature] = useState(1.0);
  const [isUploadModalOpen, setIsUploadModalOpen] = useState(false);
  const [uploadedFiles, setUploadedFiles] = useState<FileUpload[]>([]);
  const [importUrl, setImportUrl] = useState('');
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [selectedFileDisplay, setSelectedFileDisplay] = useState<File | null>(null);
  const [openModalId, setOpenModalId] = useState<string | null>(null);
  const [showError, setShowError] = useState<Record<string, boolean>>({}); // State to track error visibility for each file

  const handleSelectSource = (source: QueryEngine) => {
    setSelectedSource(source);
  };

  const handleSubmit = async () => {
    if (!prompt.trim() || !user) return;

    if (onChatStart) {
      onChatStart();
    }

    // Capture current state values for submission
    const currentPrompt = prompt.trim();
    const currentSelectedFile = selectedFile;
    setSelectedFileDisplay(selectedFile);
    const currentImportUrl = importUrl;

    let uploadedFileName = currentSelectedFile?.name;
    if (currentImportUrl) {
      uploadedFileName = currentImportUrl.split('/').pop();
      if (currentImportUrl.startsWith("gs://")) {
        uploadedFileName = currentImportUrl.replace("gs://", "").split("/").pop();
      }
    }

    const userMessage: ChatMessage = {
      text: currentPrompt.trim(),
      isUser: true,
      uploadedFile: currentSelectedFile?.name || '',
      fileUrl: currentImportUrl || '',
      showFile: currentSelectedFile ?? undefined
    };
    setMessages(prev => [...prev, userMessage]);

    // Immediately clear prompt and attachment inputs so URL disappears from input box
    setPrompt('');
    setSelectedFile(null);
    setImportUrl('');

    setIsLoading(true);

    // Determine if this is a new chat (i.e. no existing chatId)
    const wasNewChat = !chatId;

    try {
      let response: Chat | null | undefined;

      // Common parameters
      const chatParams = {
        userInput: currentPrompt.trim(),
        llmType: selectedModel.id,
        stream: true,  // Set stream to true for streaming output
        temperature: temperature,
        uploadFile: currentSelectedFile || undefined,
        fileUrl: currentImportUrl,
        // Pass toolNames if "Create a graph" is enabled
        toolNames: graphEnabled ? ["vertex_code_interpreter_tool"] : []
      };

      if (chatId) {
        // Continue existing chat
        const chatResponse = await generateChatResponse(user.token, chatId)({
          ...chatParams,
          uploadFile: currentSelectedFile || undefined,
          fileUrl: currentImportUrl,
        });

        if (chatResponse instanceof ReadableStream) {
          // Handle the streaming response separately
          await handleStream(chatResponse);
        } else {
          // Only assign to response if it's a Chat object
          response = chatResponse;
        }
      } else if (selectedSource && selectedSource.id !== "default-chat") {
        // Create new chat via query endpoint
        const emptyChat = await createEmptyChat(user.token);
        let newChatId;
        if (emptyChat && emptyChat.id) {
          newChatId = emptyChat.id;
          //setChatId(newChatId); // Update the state

        } else {
          console.error("Error creating new chat or missing chat ID:", emptyChat);
          newChatId = 'garbage'; // Or handle the error in another way
        }

        const queryResponse = await generateChatResponse(user.token, newChatId)({
          queryEngineId: selectedSource.id,
          userInput: currentPrompt.trim(),
          llmType: selectedModel.id,
          fileUrl: currentImportUrl,
          stream: false
        });
        if (queryResponse instanceof ReadableStream) {
          // Handle the streaming response separately
          await handleStream(queryResponse);
        } else {
          // Only assign to response if it's a Chat object
          response = queryResponse;
        }
      } else {

        // Create new regular chat
        const emptyChat = await createEmptyChat(user.token);
        let newChatId;
        if (emptyChat && emptyChat.id) {
          newChatId = emptyChat.id;
          setChatId(newChatId); // Update the state

          // If this was a new chat, dispatch an event to update the chat history
          if (wasNewChat) {
            window.dispatchEvent(new Event("chatHistoryUpdated"));
          }
        } else {
          console.error("Error creating new chat or missing chat ID:", emptyChat);
          newChatId = 'garbage'; // Or handle the error in another way
        }

        const chatResponse = await generateChatResponse(user.token, newChatId)({
          ...chatParams,
          uploadFile: currentSelectedFile || undefined,
          fileUrl: currentImportUrl,
        });
        if (chatResponse instanceof ReadableStream) {
          // Handle the streaming response separately
          await handleStream(chatResponse);
        } else {
          // Only assign to response if it's a Chat object
          response = chatResponse;
        }

        if (chatResponse instanceof ReadableStream) {
          // Handle the streaming response separately
          await handleStream(chatResponse);
        } else {
          // Only assign to response if it's a Chat object
          response = chatResponse;
        }
        const updatedChat = await generateChatSummary(newChatId, user.token);
        window.dispatchEvent(new Event("chatHistoryUpdated"));
      }

      // Only proceed if we got a valid Chat object
      if (response && 'id' in response) {
        setChatId(response.id);
        // If this was a new chat, dispatch an event to update the chat history
        if (wasNewChat) {
          window.dispatchEvent(new Event("chatHistoryUpdated"));
        }
      }
      if (response?.history) {
        let history = response.history;
        let newMessages = messagesFromHistory(history);
        setMessages(newMessages);
      } else {
        console.error("API response does not contain 'history' property:", response);
      }
    } catch (error) {
      console.error('Error in chat:', error);
      const errorMessage: ChatMessage = {
        text: 'An error occurred while processing your request.',
        isUser: false
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
      // Clear the prompt and attachment inputs only after processing the response
      setPrompt('');
      setSelectedFile(null);
      setImportUrl('');
    }
  };
  const handleChatResponse = async (chatResponse: Chat) => {
    if (chatResponse?.history) {
      let history = chatResponse.history;
      let newMessages = messagesFromHistory(history);
      setMessages(newMessages);
    } else {
      console.error("Chat response does not contain 'history' property:", chatResponse);
    }
  };
  // Helper function to handle streaming response
  const handleStream = async (streamOrString: ReadableStream | string) => {
    let accumulatedResponse = "";

    if (typeof streamOrString === "string") {
      // Static response
      accumulatedResponse = streamOrString;
    } else {
      // Streamed response
      const reader = streamOrString.getReader();
      const decoder = new TextDecoder();

      try {
        while (true) {
          const { done, value } = await reader.read();
          if (done) break;

          const chunk = decoder.decode(value);
          accumulatedResponse += chunk;

          setMessages(prev => {
            const updatedMessages = [...prev];
            const lastMessage = updatedMessages[updatedMessages.length - 1];

            if (lastMessage && !lastMessage.isUser) {
              updatedMessages[updatedMessages.length - 1] = {
                ...lastMessage,
                text: accumulatedResponse
              };
            } else {
              updatedMessages.push({ text: accumulatedResponse, isUser: false });
            }

            return updatedMessages;
          });
        }


        // ✅ Handle Create a Graph case or any static post-processing
        let parsed: any;
        try {
          parsed = JSON.parse(accumulatedResponse);
        } catch {
          parsed = null;
        }

        if (parsed?.data?.history) {
          const newMessages = messagesFromHistory(parsed.data.history);
          setMessages(newMessages);
        }
      } finally {
        reader.releaseLock();
      }
    }
  };
  // useLayoutEffect to scroll the container so that the last message aligns with the top
  useLayoutEffect(() => {
    if (chatMessagesRef.current && messagesEndRef.current) {
      const container = chatMessagesRef.current;
      const lastMessage = messagesEndRef.current;
      const containerRect = container.getBoundingClientRect();
      const messageRect = lastMessage.getBoundingClientRect();
      const offset = messageRect.top - containerRect.top;
      container.scrollTo({ top: container.scrollTop + offset, behavior: 'smooth' });
    }
  }, [messages]);

  const messagesFromHistory = (history: any[]) => {
    if (!history || history.length === 0) {
      return [{
        text: 'Generating code...',
        isUser: false
      }];
    }
    let newMessages: ChatMessage[] = [];
    let pendingFileUrl: string | undefined = undefined;
    for (let i = 0; i < history.length; i++) {
      const historyItem = history[i];
      if (historyItem.HumanInput) {
        let uploadedFile: string | undefined = undefined;
        let fileUrl: string | undefined = undefined;

        // Attach the pending fileUrl only to the next HumanInput
        if (pendingFileUrl) {
          fileUrl = pendingFileUrl;
          uploadedFile = fileUrl?.split('/').pop() || undefined;
          pendingFileUrl = undefined;

        }
        newMessages.push({
          text: historyItem.HumanInput,
          isUser: true,
          //title: historyItem.Title,
          uploadedFile: uploadedFile,
          fileUrl: fileUrl,
          attachId: ("" + i + chatId)
        });
      } else if (historyItem.AIOutput || historyItem.FileContentsBase64) {
        newMessages.push({
          text: historyItem.AIOutput || "",
          isUser: false,
          imageBase64: historyItem.FileContentsBase64 || ""
        });
      } else if (historyItem.QueryReferences) {
        newMessages.push({
          text: "",
          isUser: false,
          references: historyItem.QueryReferences
        });
      } else if (historyItem.UploadedFile) {
        continue;
      } else if (historyItem.FileURL) {
        //Store the file URL to attach to the next HumanInput
        pendingFileUrl = historyItem.FileURL;
        continue;
      }
    }
    return newMessages;
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  const handleAttachClick = (fileOrPath: File | string, attachId: string, chatId: string) => {
    const modalId = fileOrPath instanceof File
      ? `${fileOrPath.name}-${chatId}`
      : `${attachId}-${chatId}`;

    setOpenModalId(modalId);
  };
  const handleCloseUploadModal = () => {
    setIsUploadModalOpen(false);
    setUploadedFiles([]);
    setSelectedFile(null); // Clear the selected file
    setImportUrl(''); // Clear the import URL
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
    setShowError?.((prevErrors) => {
      const newErrors = { ...prevErrors };
      delete newErrors[fileName];
      return newErrors;
    });
  };

  const handleAddFiles = () => {
    setIsUploadModalOpen(false);
    setUploadedFiles([]);
  };

  const handleRemoveSelectedFile = () => {
    setSelectedFile(null);
    setImportUrl('');
  };

  // Function to handle toggling the "Create a graph" feature
  const toggleGraph = () => {
    setGraphEnabled(prevState => !prevState);
    //window.location.reload();
    const resetChat = () => {
      setPrompt(''); // Clear the input prompt
      setSelectedFile(null); // Clear the selected file
      setImportUrl(''); // Clear the import URL
      // Reset any other state variables as needed
    };
    resetChat();
  };

  return (
    <Box className="chat-screen">
      {(!hideHeader && !graphEnabled) && (
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
            {/* Only show the source selector if no chat ID exists (i.e. new chat) */}
            {!chatId && (
              <SourceSelector
                onSelectSource={handleSelectSource}
                chatId={chatId}
              />
            )}
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
        {(!showWelcome || messages.length > 0) && (
          <Box ref={chatMessagesRef} className="chat-messages" sx={{
            flexGrow: 1,
            mx: 2,
            overflowY: 'auto'
          }}>
            {messages.map((message, index) => {
              const isLastItem = index === messages.length - 1;
              return (
                <Box key={index}
                  onMouseEnter={() => setHoveredMessageIndex(index)}
                  onMouseLeave={() => { setHoveredMessageIndex(null); setTooltipOpen(false); }}
                  sx={{
                    position: 'relative',
                    marginRight: 'auto'
                  }}
                >
                  <Box
                    className={message.isUser ? 'user-message' : 'assistant-message'}
                    sx={{
                      backgroundColor: message.isUser ? '#343541' : 'transparent',
                      borderRadius: message.isUser ? '0.5rem 0.5rem 0 0.5rem' : '0.5rem 0.5rem 0.5rem 0rem',
                      padding: '0.75rem 1rem',
                      marginBottom: '0.5rem',
                      justifyContent: message.isUser ? 'flex-end' : 'flex-start',
                      alignSelf: message.isUser ? 'flex-end' : 'flex-start',
                      textAlign: 'left',
                      maxWidth: message.isUser ? '50%' : '100%',
                      marginLeft: message.isUser ? 'auto' : '0',
                      display: 'flex',
                      flexDirection: message.isUser ? 'row-reverse' : 'row',
                      alignItems: message.isUser ? 'flex-end' : 'flex-start',
                      gap: '0.5rem',
                    }}
                    ref={isLastItem ? messagesEndRef : null}
                  >
                    {message.isUser ? (
                      <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-start', color: '#fff' }}>
                        {message.uploadedFile !== undefined && message.uploadedFile !== '' && (
                          /* Render the image if it exists in the userMessage */
                          <Box sx={{ mb: 2, display: 'flex', alignItems: 'center' }}> {/* Add margin below the image */}
                            <Typography variant="body2" style={{ marginRight: '8px' }}>
                              {message.uploadedFile}
                            </Typography>
                            <AttachFileIcon
                              color="primary"
                              fontSize="small"
                              style={{
                                margin: '0px',
                                transform: 'rotate(90deg)',
                                color: 'white',
                                cursor: 'pointer',
                              }}
                              onClick={() => {
                                const fileToShow = message.showFile || message.fileUrl;
                                if (fileToShow) {
                                  const attachId = message.attachId ?? '';
                                  handleAttachClick(fileToShow, attachId, chatId ?? ''); // pass chatId here
                                } else {
                                  console.warn("No file to show.");
                                }
                              }}
                            />
                            {/* Conditionally render the DocumentModal */}
                            {(() => {
                              const modalId = message.showFile instanceof File
                                ? `${message.showFile.name}-${chatId}`
                                : `${message.attachId ?? ''}-${chatId}`;

                              return (
                                <DocumentModal
                                  open={openModalId === modalId}
                                  onClose={() => setOpenModalId(null)}
                                  selectedFile={message.showFile ?? null}
                                  fileURL={message.fileUrl ?? null}
                                />
                              );
                            })()}

                          </Box>
                        )}
                        <Typography sx={{ textAlign: 'left' }}>
                          {message.text}
                        </Typography>
                      </Box>
                    ) : (
                      <>
                        <Avatar src="/assets/images/gemini-icon.png" className="message-avatar" />
                        <Box sx={{ flex: 1 }}>
                          <ReactMarkdown
                            components={{
                              code({ node, className, children }) {
                                const match = /language-(\w+)/.exec(className || '');
                                const language = match ? match[1] : '';
                                if (!match) {
                                  return <code className={className}>{children}</code>;
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

                          {/* If there's an image in the same AI message, display it below the text */}
                          {message.imageBase64 && (
                            <Box sx={{ mt: 2 }}>
                              <img
                                src={`data:image/png;base64,${message.imageBase64}`}
                                alt="Graph"
                                style={{ width: '100%' }}
                              />
                            </Box>
                          )}
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
                                <ReferenceChip key={idx} reference={reference} />
                              ))}
                            </Box>
                          )}
                        </Box>
                      </>
                    )}
                  </Box>
                  <DocumentModal open={showDocumentViewer} onClose={() => setShowDocumentViewer(false)} selectedFile={selectedFile} />
                  <Box key={index} className={`message ${message.isUser ? 'user-message' : 'assistant-message'}`}
                    onClick={() => { if (!message.isUser && message.text) handleCopyClick(message.text, index); }}
                    sx={{
                      alignSelf: 'flex-end',
                      maxWidth: '100%',
                      display: 'flex',
                      flexDirection: message.isUser ? 'column' : 'row-reverse',
                      alignItems: 'flex-start',
                    }}>
                    {/* Conditionally render the chip ONLY if message.uploadedFile exists */}
                    {(message.isUser && message.fileUrl && !message.fileUrl.startsWith('gs://')) && (
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

                    {hoveredMessageIndex === index && !message.isUser && !message.references && !message.imageBase64 && (
                      <Tooltip
                        open={copiedMessageIndex === index} // Tooltip only opens if this message was copied
                        arrow
                        title="Copied!"
                        placement="top"
                        leaveDelay={200}
                      >
                        <IconButton
                          onClick={() => handleCopyClick(message.text, index)}
                          aria-label="copy"
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
              );
            })}
            {isLoading && <LoadingSpinner />}
          </Box>
        )}

        {/* Chat input container */}
        <Box
          className={`chat-input-container ${showWelcome ? 'welcome-mode' : ''}`}
          sx={{
            p: 2,
            flexShrink: 0,
            position: 'sticky',
            bottom: 0,
            zIndex: 99
          }}
        >
          {/* Render the "Create a graph" button only if no source is selected or the selected source is "default-chat" */}
          {(!selectedSource || selectedSource.id === "default-chat") && (
            <Box
              onClick={toggleGraph}
              sx={{
                display: 'flex',
                height: '32px',
                justifyContent: 'center',
                alignItems: 'center',
                gap: 1,
                cursor: 'pointer',
                marginTop: 2,
                marginBottom: 1,
                padding: '8px 12px',
                borderRadius: '8px',
                border: '1px solid #C4C7C5',
                width: 'fit-content',
                userSelect: 'none',
                ...(graphEnabled
                  ? {
                    backgroundColor: '#004A77',
                    color: '#C2E7FF',
                  }
                  : {
                    backgroundColor: 'transparent',
                    color: '#cccccc',
                  }
                ),
              }}
            >
              <BarChartIcon
                data-testid={isTest ? "bar-chart-icon" : undefined}  // Conditionally add data-testid
                sx={{
                  ...(graphEnabled
                    ? { color: '#A8C7FA' }
                    : { color: '#cccccc' }
                  )
                }}
              />
              <Typography
                sx={{
                  fontWeight: 500,
                }}
              >
                {graphEnabled ? 'Create a graph ✓' : 'Create a graph'}
              </Typography>
            </Box>
          )}
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
            <IconButton onClick={() => setIsUploadModalOpen(true)} aria-label="add">
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
            setUploadedFiles={setUploadedFiles}
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