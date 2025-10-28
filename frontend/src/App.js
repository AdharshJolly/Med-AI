/**
 * MedAI-Pro Main Application Component with Clerk Authentication
 * React Router setup with Clerk auth, theme management, and protected routes
 */

import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { ClerkProvider, SignedIn, SignedOut } from '@clerk/clerk-react';
import { CssBaseline, Box } from '@mui/material';

// Import styles
import './styles/globals.css';
import './styles/components.css';

// Import context providers
import { ThemeProvider } from './context/ThemeContext';
import { AuthProvider } from './context/AuthContext';

// Import components
import Navbar from './components/Navbar';
import Footer from './components/Footer';
import ProtectedRoute from './components/ProtectedRoute';
import UserDetailsForm from './components/UserDetailsForm';
import FloatingChatbot from './components/FloatingChatbot';

// Import pages
import LandingPage from './pages/LandingPage';
import HomePage from './pages/HomePage';
import Dashboard from './pages/Dashboard';
import DiagnosisPage from './pages/DiagnosisPage';
import DiagnosisHistory from './pages/DiagnosisHistory';
import MapsPage from './pages/MapsPage';
import ProfilePage from './pages/ProfilePage';
import AboutPage from './pages/AboutPage';
import ContactPage from './pages/ContactPage';

// Get Clerk publishable key from environment
const clerkPubKey = process.env.REACT_APP_CLERK_PUBLISHABLE_KEY;

if (!clerkPubKey) {
  throw new Error('Missing Clerk Publishable Key');
}

function App() {
  return (
    <ClerkProvider publishableKey={clerkPubKey}>
      <ThemeProvider>
        <AuthProvider>
          <CssBaseline />
          <Router>
            <Box sx={{ display: 'flex', flexDirection: 'column', minHeight: '100vh' }}>
              <Navbar />

              <Box component="main" sx={{ flex: 1 }}>
                <Routes>
                  {/* Public Routes */}
                  <Route path="/" element={<LandingPage />} />
                  <Route path="/about" element={<AboutPage />} />
                  <Route path="/contact" element={<ContactPage />} />

                  {/* Onboarding Route - Requires Auth */}
                  <Route
                    path="/onboarding"
                    element={
                      <ProtectedRoute>
                        <UserDetailsForm />
                      </ProtectedRoute>
                    }
                  />

                  {/* Protected Routes - Require Auth + Profile */}
                  <Route
                    path="/home"
                    element={
                      <ProtectedRoute requireProfile>
                        <HomePage />
                      </ProtectedRoute>
                    }
                  />
                  <Route
                    path="/dashboard"
                    element={
                      <ProtectedRoute requireProfile>
                        <Dashboard />
                      </ProtectedRoute>
                    }
                  />
                  <Route
                    path="/diagnose"
                    element={
                      <ProtectedRoute requireProfile>
                        <DiagnosisPage />
                      </ProtectedRoute>
                    }
                  />
                  <Route
                    path="/history"
                    element={
                      <ProtectedRoute requireProfile>
                        <DiagnosisHistory />
                      </ProtectedRoute>
                    }
                  />
                  <Route
                    path="/maps"
                    element={
                      <ProtectedRoute requireProfile>
                        <MapsPage />
                      </ProtectedRoute>
                    }
                  />
                  <Route
                    path="/profile"
                    element={
                      <ProtectedRoute requireProfile>
                        <ProfilePage />
                      </ProtectedRoute>
                    }
                  />

                  {/* Fallback Route */}
                  <Route path="*" element={<Navigate to="/" replace />} />
                </Routes>
              </Box>

              <Footer />

              {/* Floating Chatbot - Only on authenticated pages */}
              <SignedIn>
                <FloatingChatbot />
              </SignedIn>
            </Box>
          </Router>
        </AuthProvider>
      </ThemeProvider>
    </ClerkProvider>
}

export default App;

