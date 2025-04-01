import React from 'react';
import { Box, Typography, Container, Paper, Button } from '@mui/material';
import { Link as RouterLink } from 'react-router-dom';

const Footer = () => {
  return (
    <Paper 
      component="footer" 
      square 
      variant="outlined" 
      sx={{ 
        py: 3, 
        mt: 'auto',
        borderTop: '1px solid',
        borderColor: 'divider'
      }}
    >
      <Container maxWidth="lg">
        <Box sx={{ display: 'flex', flexDirection: { xs: 'column', md: 'row' }, justifyContent: 'space-between', alignItems: 'center' }}>
          <Typography variant="body2" color="text.secondary">
            © {new Date().getFullYear()} Assistant Juridique IA. Tous droits réservés.
          </Typography>
          
          <Box sx={{ display: 'flex', mt: { xs: 2, md: 0 } }}>
            <Button color="inherit" size="small" component={RouterLink} to="/">
              Accueil
            </Button>
            <Button color="inherit" size="small" component={RouterLink} to="/query">
              Poser une question
            </Button>
            <Button color="inherit" size="small" component={RouterLink} to="/subscription">
              Abonnements
            </Button>
          </Box>
        </Box>
        
        <Box sx={{ mt: 2, textAlign: 'center' }}>
          <Typography variant="caption" color="text.secondary">
            Les réponses générées par l'Assistant Juridique IA ne constituent pas un avis juridique professionnel. 
            Pour des conseils juridiques personnalisés, veuillez consulter un avocat ou un professionnel du droit qualifié.
          </Typography>
        </Box>
      </Container>
    </Paper>
  );
};

export default Footer;
