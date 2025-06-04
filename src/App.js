import React, { useState } from 'react';
import OpenAI from "openai";

import { 
  AppBar, 
  Toolbar, 
  Typography, 
  Container, 
  Box, 
  Paper,
  TextField,
  Button,
  List,
  ListItem,
  ListItemText,
  ThemeProvider,
  createTheme,
  FormControlLabel,
  Checkbox
} from '@mui/material';
import SendIcon from '@mui/icons-material/Send';

const OPENAI_API_KEY = process.env.REACT_APP_OPENAI_API_KEY;

const client = new OpenAI({ 
  apiKey: OPENAI_API_KEY,
  dangerouslyAllowBrowser: true
});

const theme = createTheme({
  palette: {
    primary: {
      main: '#1976d2',
    },
    secondary: {
      main: '#dc004e',
    },
  },
});

function App() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [generateImage, setGenerateImage] = useState(false);

  const handleSend = async () => {
    if (!input.trim()) return;

    // Add user message
    const userMessage = { text: input, sender: 'user' };
    setMessages(prev => [...prev, userMessage]);
    setInput('');

    try {
      const response = await client.responses.create({
          model: "gpt-4.1",
          input: [{ role: "user", content: input }],
          tools: generateImage ? [{type: "image_generation"}] : undefined
      });

      if (generateImage && response.images && response.images.length > 0) {
        // Handle image response
        const imageData = response.images[0];
        const imageBlob = new Blob([imageData], { type: 'image/png' });
        const imageUrl = URL.createObjectURL(imageBlob);
        
        // Add image message to chat
        const imageMessage = { 
          text: 'Generated Image:', 
          sender: 'bot',
          imageUrl: imageUrl
        };
        setMessages(prev => [...prev, imageMessage]);

        // Create download link
        const downloadLink = document.createElement('a');
        downloadLink.href = imageUrl;
        downloadLink.download = `generated-image-${Date.now()}.png`;
        downloadLink.click();
        
        // Clean up the URL object
        URL.revokeObjectURL(imageUrl);
      } else {
        // Handle text response
        const botMessage = { text: response.output_text, sender: 'bot' };
        setMessages(prev => [...prev, botMessage]);
      }

    } catch (error) {
      console.error('Error:', error);
      const errorMessage = { text: 'Sorry, there was an error processing your request.', sender: 'bot' };
      setMessages(prev => [...prev, errorMessage]);
    }
  };

  return (
    <ThemeProvider theme={theme}>
      <Box sx={{ flexGrow: 1 }}>
        <AppBar position="static">
          <Toolbar>
            <Box
              component="img"
              sx={{
                height: 40,
                marginRight: 2,
                backgroundColor: 'white',
                padding: '4px',
                borderRadius: '4px',
              }}
              alt="Logo placeholder"
              src="https://via.placeholder.com/150x40?text=LOGO"
            />
            <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
              AI Chat Assistant
            </Typography>
          </Toolbar>
        </AppBar>

        <Container maxWidth="md" sx={{ mt: 4, mb: 4 }}>
          <Paper
            elevation={3}
            sx={{
              height: '60vh',
              display: 'flex',
              flexDirection: 'column',
              overflow: 'hidden',
            }}
          >
            <List sx={{ flexGrow: 1, overflow: 'auto', p: 2 }}>
              {messages.map((message, index) => (
                <ListItem
                  key={index}
                  sx={{
                    justifyContent: message.sender === 'user' ? 'flex-end' : 'flex-start',
                  }}
                >
                  <Paper
                    elevation={1}
                    sx={{
                      p: 2,
                      backgroundColor: message.sender === 'user' ? 'primary.light' : 'grey.100',
                      color: message.sender === 'user' ? 'white' : 'text.primary',
                      maxWidth: '70%',
                      display: 'flex',
                      flexDirection: 'column',
                      gap: 1
                    }}
                  >
                    {message.text && <ListItemText primary={message.text} />}
                    {message.imageUrl && (
                      <Box 
                        sx={{ 
                          mt: 1,
                          width: '100%',
                          display: 'flex',
                          justifyContent: 'center',
                          '& img': {
                            maxWidth: '100%',
                            height: 'auto',
                            borderRadius: '8px',
                            boxShadow: '0 2px 4px rgba(0,0,0,0.1)'
                          }
                        }}
                      >
                        <img 
                          src={message.imageUrl} 
                          alt="Generated" 
                          style={{ maxWidth: '100%', height: 'auto' }} 
                        />
                      </Box>
                    )}
                  </Paper>
                </ListItem>
              ))}
            </List>

            <Box sx={{ p: 2, backgroundColor: 'background.paper' }}>
              <Box sx={{ display: 'flex', gap: 1, flexDirection: 'column' }}>
                <Box sx={{ display: 'flex', gap: 1 }}>
                  <TextField
                    fullWidth
                    variant="outlined"
                    placeholder="Type your message..."
                    value={input}
                    onChange={(e) => setInput(e.target.value)}
                    onKeyPress={(e) => e.key === 'Enter' && handleSend()}
                  />
                  <Button
                    variant="contained"
                    color="primary"
                    endIcon={<SendIcon />}
                    onClick={handleSend}
                  >
                    Send
                  </Button>
                </Box>
                <FormControlLabel
                  control={
                    <Checkbox
                      checked={generateImage}
                      onChange={(e) => setGenerateImage(e.target.checked)}
                    />
                  }
                  label="Generate Image"
                />
              </Box>
            </Box>
          </Paper>
        </Container>
      </Box>
    </ThemeProvider>
  );
}

export default App; 