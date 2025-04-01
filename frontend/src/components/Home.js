import React from 'react';
import { Box, Typography, Container, Grid, Card, CardContent, CardActions, Button, Paper } from '@mui/material';
import { Link as RouterLink } from 'react-router-dom';

const Home = () => {
  return (
    <Box>
      {/* Hero Section */}
      <Paper 
        elevation={0}
        sx={{ 
          bgcolor: 'primary.main', 
          color: 'white', 
          py: 8, 
          mb: 6,
          borderRadius: 0
        }}
      >
        <Container maxWidth="md">
          <Typography variant="h2" component="h1" gutterBottom align="center">
            Assistant Juridique IA
          </Typography>
          <Typography variant="h5" align="center" paragraph>
            Votre expert juridique en droit des affaires et fiscal français, disponible 24/7
          </Typography>
          <Box sx={{ mt: 4, display: 'flex', justifyContent: 'center' }}>
            <Button 
              variant="contained" 
              color="secondary" 
              size="large"
              component={RouterLink}
              to="/register"
              sx={{ mx: 1 }}
            >
              Essayer gratuitement
            </Button>
            <Button 
              variant="outlined" 
              color="inherit" 
              size="large"
              component={RouterLink}
              to="/login"
              sx={{ mx: 1 }}
            >
              Se connecter
            </Button>
          </Box>
        </Container>
      </Paper>

      {/* Features Section */}
      <Container maxWidth="lg" sx={{ mb: 6 }}>
        <Typography variant="h4" component="h2" gutterBottom align="center" sx={{ mb: 4 }}>
          Fonctionnalités principales
        </Typography>
        <Grid container spacing={4}>
          <Grid item xs={12} md={4}>
            <Card sx={{ height: '100%' }}>
              <CardContent>
                <Typography variant="h5" component="h3" gutterBottom>
                  Recherche juridique intelligente
                </Typography>
                <Typography variant="body1">
                  Posez vos questions en langage naturel et obtenez des réponses précises basées sur les textes de loi français, la jurisprudence et la doctrine.
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} md={4}>
            <Card sx={{ height: '100%' }}>
              <CardContent>
                <Typography variant="h5" component="h3" gutterBottom>
                  Spécialisation en droit des affaires
                </Typography>
                <Typography variant="body1">
                  Obtenez des conseils sur la création d'entreprise, les statuts juridiques, les obligations légales et toutes vos questions de droit commercial.
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} md={4}>
            <Card sx={{ height: '100%' }}>
              <CardContent>
                <Typography variant="h5" component="h3" gutterBottom>
                  Expertise en droit fiscal
                </Typography>
                <Typography variant="body1">
                  Comprenez vos obligations fiscales, optimisez légalement votre imposition et restez informé des dernières évolutions de la législation fiscale.
                </Typography>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      </Container>

      {/* Pricing Section */}
      <Container maxWidth="lg" sx={{ mb: 6 }}>
        <Typography variant="h4" component="h2" gutterBottom align="center" sx={{ mb: 4 }}>
          Nos offres
        </Typography>
        <Grid container spacing={4}>
          <Grid item xs={12} md={4}>
            <Card sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
              <CardContent sx={{ flexGrow: 1 }}>
                <Typography variant="h5" component="h3" gutterBottom>
                  Freemium
                </Typography>
                <Typography variant="h3" color="primary" gutterBottom>
                  Gratuit
                </Typography>
                <Typography variant="body1" paragraph>
                  Idéal pour découvrir le service
                </Typography>
                <Typography variant="body2" component="ul" sx={{ pl: 2 }}>
                  <li>10 requêtes par mois</li>
                  <li>Domaines juridiques limités</li>
                  <li>Réponses basiques</li>
                </Typography>
              </CardContent>
              <CardActions>
                <Button 
                  fullWidth 
                  variant="outlined" 
                  component={RouterLink}
                  to="/register"
                >
                  S'inscrire gratuitement
                </Button>
              </CardActions>
            </Card>
          </Grid>
          <Grid item xs={12} md={4}>
            <Card sx={{ 
              height: '100%', 
              display: 'flex', 
              flexDirection: 'column',
              border: '2px solid',
              borderColor: 'primary.main'
            }}>
              <CardContent sx={{ flexGrow: 1 }}>
                <Typography variant="h5" component="h3" gutterBottom>
                  Standard
                </Typography>
                <Typography variant="h3" color="primary" gutterBottom>
                  19,99 €/mois
                </Typography>
                <Typography variant="body1" paragraph>
                  Pour les particuliers et entrepreneurs
                </Typography>
                <Typography variant="body2" component="ul" sx={{ pl: 2 }}>
                  <li>100 requêtes par mois</li>
                  <li>Tous les domaines juridiques</li>
                  <li>Réponses détaillées</li>
                  <li>Historique des consultations</li>
                </Typography>
              </CardContent>
              <CardActions>
                <Button 
                  fullWidth 
                  variant="contained" 
                  component={RouterLink}
                  to="/register"
                >
                  Choisir Standard
                </Button>
              </CardActions>
            </Card>
          </Grid>
          <Grid item xs={12} md={4}>
            <Card sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
              <CardContent sx={{ flexGrow: 1 }}>
                <Typography variant="h5" component="h3" gutterBottom>
                  Pro
                </Typography>
                <Typography variant="h3" color="primary" gutterBottom>
                  49,99 €/mois
                </Typography>
                <Typography variant="body1" paragraph>
                  Pour les professionnels du droit
                </Typography>
                <Typography variant="body2" component="ul" sx={{ pl: 2 }}>
                  <li>1000 requêtes par mois</li>
                  <li>Tous les domaines juridiques</li>
                  <li>Réponses techniques avancées</li>
                  <li>Export PDF et citations</li>
                  <li>Support prioritaire</li>
                </Typography>
              </CardContent>
              <CardActions>
                <Button 
                  fullWidth 
                  variant="outlined" 
                  component={RouterLink}
                  to="/register"
                >
                  Choisir Pro
                </Button>
              </CardActions>
            </Card>
          </Grid>
        </Grid>
      </Container>

      {/* CTA Section */}
      <Paper 
        elevation={0}
        sx={{ 
          bgcolor: 'secondary.main', 
          color: 'white', 
          py: 6, 
          mb: 6,
          borderRadius: 0
        }}
      >
        <Container maxWidth="md">
          <Typography variant="h4" align="center" gutterBottom>
            Prêt à simplifier vos recherches juridiques ?
          </Typography>
          <Typography variant="body1" align="center" paragraph>
            Inscrivez-vous dès maintenant et posez votre première question juridique gratuitement.
          </Typography>
          <Box sx={{ display: 'flex', justifyContent: 'center', mt: 3 }}>
            <Button 
              variant="contained" 
              color="primary" 
              size="large"
              component={RouterLink}
              to="/register"
            >
              Commencer maintenant
            </Button>
          </Box>
        </Container>
      </Paper>
    </Box>
  );
};

export default Home;
