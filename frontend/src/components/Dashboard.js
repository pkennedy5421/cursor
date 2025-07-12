import React, { useState, useEffect } from 'react';
import {
  Container,
  Paper,
  TextField,
  Button,
  Typography,
  List,
  ListItem,
  ListItemText,
  ListItemSecondaryAction,
  IconButton,
  Box,
  Divider,
} from '@mui/material';
import DeleteIcon from '@mui/icons-material/Delete';
import axios from 'axios';

function Dashboard() {
  const [searchQuery, setSearchQuery] = useState('');
  const [searchRequests, setSearchRequests] = useState([]);
  const [error, setError] = useState('');

  useEffect(() => {
    fetchSearchRequests();
  }, []);

  const fetchSearchRequests = async () => {
    try {
      const response = await axios.get('http://localhost:8000/search-requests');
      setSearchRequests(response.data);
    } catch (error) {
      console.error('Error fetching search requests:', error);
      setError('Failed to load search requests');
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');

    if (!searchQuery.trim()) {
      setError('Please enter a search query');
      return;
    }

    try {
      await axios.post('http://localhost:8000/search-requests', {
        search_query: searchQuery,
      });
      setSearchQuery('');
      fetchSearchRequests();
    } catch (error) {
      console.error('Error creating search request:', error);
      setError('Failed to create search request');
    }
  };

  const handleDelete = async (id) => {
    try {
      await axios.delete(`http://localhost:8000/search-requests/${id}`);
      fetchSearchRequests();
    } catch (error) {
      console.error('Error deleting search request:', error);
      setError('Failed to delete search request');
    }
  };

  return (
    <Container maxWidth="md">
      <Box sx={{ mt: 4 }}>
        <Paper elevation={3} sx={{ p: 4, mb: 4 }}>
          <Typography variant="h5" component="h2" gutterBottom>
            Create New Search Request
          </Typography>
          {error && (
            <Typography color="error" gutterBottom>
              {error}
            </Typography>
          )}
          <form onSubmit={handleSubmit}>
            <TextField
              fullWidth
              label="Search Query"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              margin="normal"
              required
              placeholder="e.g., blue 1977 Scout international with automatic transmission"
            />
            <Button
              type="submit"
              variant="contained"
              color="primary"
              sx={{ mt: 2 }}
            >
              Create Search Request
            </Button>
          </form>
        </Paper>

        <Paper elevation={3} sx={{ p: 4 }}>
          <Typography variant="h5" component="h2" gutterBottom>
            Your Search Requests
          </Typography>
          <List>
            {searchRequests.map((request) => (
              <React.Fragment key={request.id}>
                <ListItem>
                  <ListItemText
                    primary={request.search_query}
                    secondary={`Created: ${new Date(
                      request.created_at
                    ).toLocaleString()}`}
                  />
                  <ListItemSecondaryAction>
                    <IconButton
                      edge="end"
                      aria-label="delete"
                      onClick={() => handleDelete(request.id)}
                    >
                      <DeleteIcon />
                    </IconButton>
                  </ListItemSecondaryAction>
                </ListItem>
                <Divider />
              </React.Fragment>
            ))}
            {searchRequests.length === 0 && (
              <ListItem>
                <ListItemText
                  primary="No search requests yet"
                  secondary="Create a new search request to get started"
                />
              </ListItem>
            )}
          </List>
        </Paper>
      </Box>
    </Container>
  );
}

export default Dashboard; 