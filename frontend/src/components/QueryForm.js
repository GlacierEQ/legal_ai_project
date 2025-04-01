import React, { useState } from 'react';
import { 
  Box, 
  Typography, 
  TextField, 
  Button, 
  Paper, 
  FormControl, 
  FormControlLabel, 
  RadioGroup, 
  Radio, 
  CircularProgress,
  Divider,
  Alert
} from '@mui/material';
import axios from 'axios';
import { useAuth } from '../contexts/AuthContext';

const QueryForm = () => {
  const { currentUser } = useAuth();
  const [query, setQuery] = useState('');
  const [domain, setDomain] = useState('auto');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [response, setResponse] = useState(null);
  const [remainingQueries, setRemainingQueries] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!query.trim()) {
      setError('Veuillez saisir une question juridique');
      return;
    }
    
    setLoading(true);
    setError('');
    setResponse(null);
    
    try {
      const response = await axios.post(`${process.env.REACT_APP_API_URL}/queries/`, {
        query_text: query,
        domain: domain === 'auto' ? '' : domain
      });
      
      setResponse(response.data.response);
      setRemainingQueries(response.data.remaining_queries);
      setLoading(false);
    } catch (error) {
      console.error('Error submitting query', error);
      setError(error.response?.data?.detail || 'Une erreur est survenue lors du traitement de votre question');
      setLoading(false);
    }
  };

  return (
    <Box>
      <Typography variant="h4" component="h1" gutterBottom>
        Assistant Juridique IA
      </Typography>
      
      <Typography variant="body1" paragraph>
        Posez votre question juridique ci-dessous et notre assistant IA vous fournira une réponse précise basée sur le droit français.
      </Typography>
      
      <Paper elevation={3} sx={{ p: 3, mb: 4 }}>
        <form onSubmit={handleSubmit}>
          <TextField
            label="Votre question juridique"
            variant="outlined"
            fullWidth
            multiline
            rows={4}
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Ex: Comment créer une SAS en France ? Quelles sont les obligations fiscales pour une micro-entreprise ?"
            sx={{ mb: 3 }}
          />
          
          <FormControl component="fieldset" sx={{ mb: 3 }}>
            <Typography variant="subtitle1" gutterBottom>
              Domaine juridique
            </Typography>
            <RadioGroup
              row
              value={domain}
              onChange={(e) => setDomain(e.target.value)}
            >
              <FormControlLabel value="auto" control={<Radio />} label="Détection automatique" />
              <FormControlLabel value="business" control={<Radio />} label="Droit des affaires" />
              <FormControlLabel value="tax" control={<Radio />} label="Droit fiscal" />
            </RadioGroup>
          </FormControl>
          
          {error && (
            <Alert severity="error" sx={{ mb: 3 }}>
              {error}
            </Alert>
          )}
          
          <Button
            type="submit"
            variant="contained"
            color="primary"
            size="large"
            disabled={loading || !query.trim()}
            startIcon={loading && <CircularProgress size={20} color="inherit" />}
          >
            {loading ? 'Traitement en cours...' : 'Obtenir une réponse juridique'}
          </Button>
          
          {remainingQueries !== null && (
            <Typography variant="body2" sx={{ mt: 1, color: 'text.secondary' }}>
              Requêtes restantes ce mois-ci : {remainingQueries}
            </Typography>
          )}
        </form>
      </Paper>
      
      {response && (
        <Paper elevation={3} sx={{ p: 3 }}>
          <Typography variant="h5" gutterBottom>
            Réponse juridique
          </Typography>
          
          <Divider sx={{ mb: 2 }} />
          
          <Typography variant="body1" component="div" sx={{ whiteSpace: 'pre-line' }}>
            {response}
          </Typography>
        </Paper>
      )}
    </Box>
  );
};

export default QueryForm;
