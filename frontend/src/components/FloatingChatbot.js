import React, { useState, useEffect, useRef } from 'react';
import { useUser } from '@clerk/clerk-react';
import {
  Box,
  Paper,
  IconButton,
  TextField,
  Typography,
  Avatar,
  Fab,
  Badge,
  Menu,
  MenuItem,
  Tooltip,
  CircularProgress,
} from '@mui/material';
import {
  Chat,
  Close,
  Send,
  Mic,
  MicOff,
  VolumeUp,
  Translate,
  SentimentSatisfied,
  SentimentNeutral,
  SentimentDissatisfied,
} from '@mui/icons-material';
import { motion, AnimatePresence } from 'framer-motion';
import {
  sendChatMessage,
  getChatHistory,
  speechToText,
  textToSpeech,
  translateMessage,
  analyzeSentiment,
} from '../services/api';

const FloatingChatbot = () => {
  const { user } = useUser();
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState('');
  const [loading, setLoading] = useState(false);
  const [isRecording, setIsRecording] = useState(false);
  const [unreadCount, setUnreadCount] = useState(0);
  const [languageAnchor, setLanguageAnchor] = useState(null);
  const [selectedLanguage, setSelectedLanguage] = useState('en');
  const messagesEndRef = useRef(null);
  const mediaRecorderRef = useRef(null);
  const audioChunksRef = useRef([]);

  const languages = [
    { code: 'en', name: 'English' },
    { code: 'hi', name: 'हिंदी' },
    { code: 'bn', name: 'বাংলা' },
    { code: 'te', name: 'తెలుగు' },
    { code: 'mr', name: 'मराठी' },
    { code: 'ta', name: 'தமிழ்' },
  ];

  useEffect(() => {
    if (isOpen && messages.length === 0) {
      loadChatHistory();
    }
  }, [isOpen]);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const loadChatHistory = async () => {
    try {
      const response = await getChatHistory(user.id);
      setMessages(response.data.messages || []);
    } catch (error) {
      console.error('Error loading chat history:', error);
      // Add welcome message
      setMessages([
        {
          text: `Hello ${user.firstName}! I'm your AI health assistant. How can I help you today?`,
          isUser: false,
          timestamp: new Date().toISOString(),
        },
      ]);
    }
  };

  const handleSendMessage = async () => {
    if (!inputMessage.trim()) return;

    const userMessage = {
      text: inputMessage,
      isUser: true,
      timestamp: new Date().toISOString(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInputMessage('');
    setLoading(true);

    try {
      // Send message to backend
      const response = await sendChatMessage(inputMessage, user.id);
      
      // Get sentiment
      const sentimentRes = await analyzeSentiment(inputMessage);
      
      const botMessage = {
        text: response.data.response,
        isUser: false,
        timestamp: new Date().toISOString(),
        sentiment: sentimentRes.data.sentiment,
      };

      setMessages((prev) => [...prev, botMessage]);
    } catch (error) {
      console.error('Error sending message:', error);
      const errorMessage = {
        text: 'Sorry, I encountered an error. Please try again.',
        isUser: false,
        timestamp: new Date().toISOString(),
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      mediaRecorderRef.current = new MediaRecorder(stream);
      audioChunksRef.current = [];

      mediaRecorderRef.current.ondataavailable = (event) => {
        audioChunksRef.current.push(event.data);
      };

      mediaRecorderRef.current.onstop = async () => {
        const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/wav' });
        await handleVoiceInput(audioBlob);
        stream.getTracks().forEach((track) => track.stop());
      };

      mediaRecorderRef.current.start();
      setIsRecording(true);
    } catch (error) {
      console.error('Error starting recording:', error);
      alert('Microphone access denied');
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
    }
  };

  const handleVoiceInput = async (audioBlob) => {
    setLoading(true);
    try {
      const response = await speechToText(audioBlob);
      setInputMessage(response.data.text);
    } catch (error) {
      console.error('Error converting speech to text:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleTextToSpeech = async (text) => {
    try {
      const response = await textToSpeech(text, selectedLanguage);
      const audioUrl = URL.createObjectURL(response.data);
      const audio = new Audio(audioUrl);
      audio.play();
    } catch (error) {
      console.error('Error converting text to speech:', error);
    }
  };

  const handleTranslate = async (text) => {
    try {
      const response = await translateMessage(text, selectedLanguage);
      return response.data.translated_text;
    } catch (error) {
      console.error('Error translating message:', error);
      return text;
    }
  };

  const getSentimentIcon = (sentiment) => {
    if (!sentiment) return null;
    const icons = {
      positive: <SentimentSatisfied sx={{ color: 'success.main', fontSize: 16 }} />,
      neutral: <SentimentNeutral sx={{ color: 'warning.main', fontSize: 16 }} />,
      negative: <SentimentDissatisfied sx={{ color: 'error.main', fontSize: 16 }} />,
    };
    return icons[sentiment.toLowerCase()];
  };

  return (
    <>
      {/* Floating Button */}
      <Fab
        color="primary"
        sx={{
          position: 'fixed',
          bottom: 20,
          right: 20,
          width: 60,
          height: 60,
          zIndex: 1000,
        }}
        onClick={() => setIsOpen(!isOpen)}
      >
        <Badge badgeContent={unreadCount} color="error">
          {isOpen ? <Close /> : <Chat />}
        </Badge>
      </Fab>

      {/* Chat Panel */}
      <AnimatePresence>
        {isOpen && (
          <motion.div
            initial={{ opacity: 0, y: 20, scale: 0.95 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: 20, scale: 0.95 }}
            transition={{ duration: 0.2 }}
            style={{
              position: 'fixed',
              bottom: 90,
              right: 20,
              width: 350,
              height: 500,
              zIndex: 999,
            }}
          >
            <Paper
              elevation={8}
              sx={{
                height: '100%',
                display: 'flex',
                flexDirection: 'column',
                borderRadius: 2,
                overflow: 'hidden',
              }}
            >
              {/* Header */}
              <Box
                sx={{
                  background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                  color: 'white',
                  p: 2,
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'space-between',
                }}
              >
                <Box sx={{ display: 'flex', alignItems: 'center' }}>
                  <Avatar sx={{ mr: 1, bgcolor: 'white', color: 'primary.main' }}>
                    <Chat />
                  </Avatar>
                  <Box>
                    <Typography variant="subtitle1" sx={{ fontWeight: 600 }}>
                      AI Health Assistant
                    </Typography>
                    <Typography variant="caption">Online</Typography>
                  </Box>
                </Box>
                <IconButton
                  size="small"
                  onClick={(e) => setLanguageAnchor(e.currentTarget)}
                  sx={{ color: 'white' }}
                >
                  <Translate />
                </IconButton>
              </Box>

              {/* Messages */}
              <Box
                sx={{
                  flex: 1,
                  overflowY: 'auto',
                  p: 2,
                  backgroundColor: 'background.default',
                }}
              >
                {messages.map((message, index) => (
                  <Box
                    key={index}
                    sx={{
                      display: 'flex',
                      justifyContent: message.isUser ? 'flex-end' : 'flex-start',
                      mb: 2,
                    }}
                  >
                    <Paper
                      elevation={1}
                      sx={{
                        p: 1.5,
                        maxWidth: '75%',
                        backgroundColor: message.isUser ? 'primary.main' : 'background.paper',
                        color: message.isUser ? 'white' : 'text.primary',
                      }}
                    >
                      <Typography variant="body2">{message.text}</Typography>
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mt: 0.5 }}>
                        <Typography variant="caption" sx={{ opacity: 0.7 }}>
                          {new Date(message.timestamp).toLocaleTimeString([], {
                            hour: '2-digit',
                            minute: '2-digit',
                          })}
                        </Typography>
                        {!message.isUser && message.sentiment && getSentimentIcon(message.sentiment)}
                        {!message.isUser && (
                          <IconButton
                            size="small"
                            onClick={() => handleTextToSpeech(message.text)}
                            sx={{ p: 0, ml: 'auto' }}
                          >
                            <VolumeUp sx={{ fontSize: 16 }} />
                          </IconButton>
                        )}
                      </Box>
                    </Paper>
                  </Box>
                ))}
                {loading && (
                  <Box sx={{ display: 'flex', justifyContent: 'flex-start', mb: 2 }}>
                    <Paper elevation={1} sx={{ p: 1.5 }}>
                      <CircularProgress size={20} />
                    </Paper>
                  </Box>
                )}
                <div ref={messagesEndRef} />
              </Box>

              {/* Input */}
              <Box sx={{ p: 2, backgroundColor: 'background.paper', borderTop: 1, borderColor: 'divider' }}>
                <Box sx={{ display: 'flex', gap: 1 }}>
                  <TextField
                    fullWidth
                    size="small"
                    placeholder="Type your message..."
                    value={inputMessage}
                    onChange={(e) => setInputMessage(e.target.value)}
                    onKeyPress={handleKeyPress}
                    disabled={loading}
                    multiline
                    maxRows={3}
                  />
                  <Tooltip title={isRecording ? 'Stop Recording' : 'Voice Input'}>
                    <IconButton
                      color={isRecording ? 'error' : 'default'}
                      onClick={isRecording ? stopRecording : startRecording}
                      disabled={loading}
                    >
                      {isRecording ? <MicOff /> : <Mic />}
                    </IconButton>
                  </Tooltip>
                  <IconButton color="primary" onClick={handleSendMessage} disabled={loading || !inputMessage.trim()}>
                    <Send />
                  </IconButton>
                </Box>
              </Box>
            </Paper>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Language Menu */}
      <Menu
        anchorEl={languageAnchor}
        open={Boolean(languageAnchor)}
        onClose={() => setLanguageAnchor(null)}
      >
        {languages.map((lang) => (
          <MenuItem
            key={lang.code}
            selected={selectedLanguage === lang.code}
            onClick={() => {
              setSelectedLanguage(lang.code);
              setLanguageAnchor(null);
            }}
          >
            {lang.name}
          </MenuItem>
        ))}
      </Menu>
    </>
  );
};

export default FloatingChatbot;

