import React, { useEffect } from 'react';
import { Navigate, useNavigate } from 'react-router-dom';
import { useUser } from '@clerk/clerk-react';
import { useAuth } from '../context/AuthContext';
import { Box, CircularProgress, Typography } from '@mui/material';

const ProtectedRoute = ({ children, requireProfile = false }) => {
  const { isLoaded, isSignedIn } = useUser();
  const { hasCompletedProfile, profileLoading } = useAuth();
  const navigate = useNavigate();

  useEffect(() => {
    if (isLoaded && isSignedIn && requireProfile && !profileLoading) {
      if (!hasCompletedProfile) {
        navigate('/onboarding');
      }
    }
  }, [isLoaded, isSignedIn, hasCompletedProfile, profileLoading, requireProfile, navigate]);

  // Show loading while checking authentication
  if (!isLoaded || profileLoading) {
    return (
      <Box
        sx={{
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center',
          minHeight: '100vh',
          gap: 2,
        }}
      >
        <CircularProgress size={60} />
        <Typography variant="h6" color="text.secondary">
          Loading...
        </Typography>
      </Box>
    );
  }

  // Redirect to landing page if not signed in
  if (!isSignedIn) {
    return <Navigate to="/" replace />;
  }

  // Redirect to onboarding if profile not completed and required
  if (requireProfile && !hasCompletedProfile) {
    return <Navigate to="/onboarding" replace />;
  }

  return children;
};

export default ProtectedRoute;

