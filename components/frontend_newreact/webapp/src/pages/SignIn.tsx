import { Box, Container, Paper, Typography } from '@mui/material';
import SignInForm from '@/components/SignInForm';
import { AppConfig } from '@/lib/auth';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '@/contexts/AuthContext';
import { useEffect } from 'react';

const SignIn = () => {
  const navigate = useNavigate();
  const { user } = useAuth();

  useEffect(() => {
    if (user) {
      navigate('/');
    }
  }, [user, navigate]);

  return (
    <Container maxWidth="sm">
      <Box sx={{ mt: 8, display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
        <Paper elevation={3} sx={{ p: 4, width: '100%' }}>
          <Box sx={{ mb: 3, display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
            <img src={AppConfig.logoPath} alt="Logo" style={{ height: 60, marginBottom: 16 }} />
            <Typography component="h1" variant="h5">
              Sign in to {AppConfig.siteName}
            </Typography>
          </Box>
          <SignInForm authOptions={AppConfig.authProviders} />
        </Paper>
      </Box>
    </Container>
  );
};

export default SignIn; 