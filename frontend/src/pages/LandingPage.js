import React from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Box,
  Container,
  Typography,
  Button,
  Grid,
  Card,
  CardContent,
  Avatar,
  Rating,
  useTheme,
} from '@mui/material';
import {
  LocalHospital,
  Psychology,
  Speed,
  Security,
  Language,
  CloudUpload,
  SignUpButton,
} from '@clerk/clerk-react';
import {
  Favorite,
  Visibility,
  Healing,
  Assessment,
  Chat,
  Map,
} from '@mui/icons-material';
import { motion } from 'framer-motion';

const LandingPage = () => {
  const theme = useTheme();
  const navigate = useNavigate();

  const features = [
    {
      icon: <Psychology sx={{ fontSize: 50 }} />,
      title: 'AI-Powered Diagnosis',
      description: 'Advanced machine learning models trained on millions of medical cases for accurate predictions.',
    },
    {
      icon: <CloudUpload sx={{ fontSize: 50 }} />,
      title: 'Multi-Modal Input',
      description: 'Upload images, audio, PDFs, lab results, or describe symptoms in text for comprehensive analysis.',
    },
    {
      icon: <Speed sx={{ fontSize: 50 }} />,
      title: 'Instant Results',
      description: 'Get diagnosis results in seconds with confidence scores and detailed medical insights.',
    },
    {
      icon: <Chat sx={{ fontSize: 50 }} />,
      title: 'AI Chatbot',
      description: '24/7 medical chatbot with voice support, sentiment analysis, and multilingual capabilities.',
    },
    {
      icon: <Map sx={{ fontSize: 50 }} />,
      title: 'Hospital Finder',
      description: 'Locate nearby hospitals, clinics, and pharmacies with Google Maps integration.',
    },
    {
      icon: <Language sx={{ fontSize: 50 }} />,
      title: '12 Languages',
      description: 'Support for English, Hindi, Bengali, Telugu, Marathi, Tamil, and 6 more Indian languages.',
    },
  ];

  const howItWorks = [
    {
      step: '1',
      title: 'Sign Up',
      description: 'Create your account and complete your medical profile with health history.',
    },
    {
      step: '2',
      title: 'Input Symptoms',
      description: 'Describe symptoms, upload medical images, or provide lab results.',
    },
    {
      step: '3',
      title: 'AI Analysis',
      description: 'Our AI models analyze your data and route to the appropriate specialist model.',
    },
    {
      step: '4',
      title: 'Get Results',
      description: 'Receive detailed diagnosis with treatment recommendations and AI insights.',
    },
  ];

  const testimonials = [
    {
      name: 'Dr. Rajesh Kumar',
      role: 'General Physician',
      rating: 5,
      comment: 'MedAI-Pro has revolutionized how I provide preliminary assessments. The accuracy is impressive!',
      avatar: 'RK',
    },
    {
      name: 'Priya Sharma',
      role: 'Patient',
      rating: 5,
      comment: 'Got instant insights about my symptoms. The chatbot is incredibly helpful and available 24/7.',
      avatar: 'PS',
    },
    {
      name: 'Dr. Anita Desai',
      role: 'Dermatologist',
      rating: 4,
      comment: 'The skin condition detection is remarkably accurate. A great tool for initial screening.',
      avatar: 'AD',
    },
  ];

  const stats = [
    { value: '1M+', label: 'Diagnoses Performed' },
    { value: '90%', label: 'Accuracy Rate' },
    { value: '12', label: 'Languages Supported' },
    { value: '24/7', label: 'AI Availability' },
  ];

  return (
    <Box>
      {/* Hero Section */}
      <Box
        sx={{
          background: `linear-gradient(135deg, ${theme.palette.primary.main} 0%, ${theme.palette.primary.dark} 100%)`,
          color: 'white',
          py: { xs: 8, md: 12 },
          position: 'relative',
          overflow: 'hidden',
        }}
      >
        <Container maxWidth="lg">
          <Grid container spacing={4} alignItems="center">
            <Grid item xs={12} md={6}>
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.8 }}
              >
                <Typography variant="h2" sx={{ fontWeight: 700, mb: 2 }}>
                  AI-Powered Medical Diagnosis
                </Typography>
                <Typography variant="h5" sx={{ mb: 4, opacity: 0.9 }}>
                  Get instant health insights with advanced machine learning. Your personal AI health assistant.
                </Typography>
                <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap' }}>
                  <SignUpButton mode="modal">
                    <Button
                      variant="contained"
                      size="large"
                      sx={{
                        backgroundColor: 'white',
                        color: 'primary.main',
                        px: 4,
                        py: 1.5,
                        fontSize: '1.1rem',
                        '&:hover': {
                          backgroundColor: 'rgba(255, 255, 255, 0.9)',
                        },
                      }}
                    >
                      Get Started Free
                    </Button>
                  </SignUpButton>
                  <Button
                    variant="outlined"
                    size="large"
                    onClick={() => navigate('/about')}
                    sx={{
                      borderColor: 'white',
                      color: 'white',
                      px: 4,
                      py: 1.5,
                      fontSize: '1.1rem',
                      '&:hover': {
                        borderColor: 'white',
                        backgroundColor: 'rgba(255, 255, 255, 0.1)',
                      },
                    }}
                  >
                    Learn More
                  </Button>
                </Box>
              </motion.div>
            </Grid>
            <Grid item xs={12} md={6}>
              <motion.div
                initial={{ opacity: 0, scale: 0.8 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ duration: 0.8, delay: 0.2 }}
              >
                <Box
                  sx={{
                    display: 'flex',
                    justifyContent: 'center',
                    alignItems: 'center',
                  }}
                >
                  <LocalHospital sx={{ fontSize: { xs: 200, md: 300 }, opacity: 0.2 }} />
                </Box>
              </motion.div>
            </Grid>
          </Grid>
        </Container>
      </Box>

      {/* Stats Section */}
      <Container maxWidth="lg" sx={{ mt: -4, position: 'relative', zIndex: 1 }}>
        <Grid container spacing={2}>
          {stats.map((stat, index) => (
            <Grid item xs={6} md={3} key={index}>
              <Card
                elevation={4}
                sx={{
                  textAlign: 'center',
                  py: 3,
                  background: theme.palette.mode === 'dark' ? 'rgba(255, 255, 255, 0.05)' : 'white',
                }}
              >
                <Typography variant="h3" color="primary" sx={{ fontWeight: 700 }}>
                  {stat.value}
                </Typography>
                <Typography variant="body1" color="text.secondary">
                  {stat.label}
                </Typography>
              </Card>
            </Grid>
          ))}
        </Grid>
      </Container>

      {/* Features Section */}
      <Container maxWidth="lg" sx={{ py: 10 }}>
        <Typography variant="h3" align="center" sx={{ fontWeight: 700, mb: 2 }}>
          Powerful Features
        </Typography>
        <Typography variant="h6" align="center" color="text.secondary" sx={{ mb: 6 }}>
          Everything you need for comprehensive health analysis
        </Typography>
        <Grid container spacing={4}>
          {features.map((feature, index) => (
            <Grid item xs={12} sm={6} md={4} key={index}>
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5, delay: index * 0.1 }}
                viewport={{ once: true }}
              >
                <Card
                  elevation={2}
                  sx={{
                    height: '100%',
                    transition: 'transform 0.3s, box-shadow 0.3s',
                    '&:hover': {
                      transform: 'translateY(-8px)',
                      boxShadow: 6,
                    },
                  }}
                >
                  <CardContent sx={{ textAlign: 'center', p: 4 }}>
                    <Box sx={{ color: 'primary.main', mb: 2 }}>{feature.icon}</Box>
                    <Typography variant="h6" sx={{ fontWeight: 600, mb: 1 }}>
                      {feature.title}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      {feature.description}
                    </Typography>
                  </CardContent>
                </Card>
              </motion.div>
            </Grid>
          ))}
        </Grid>
      </Container>

      {/* How It Works Section */}
      <Box sx={{ backgroundColor: 'background.default', py: 10 }}>
        <Container maxWidth="lg">
          <Typography variant="h3" align="center" sx={{ fontWeight: 700, mb: 2 }}>
            How It Works
          </Typography>
          <Typography variant="h6" align="center" color="text.secondary" sx={{ mb: 6 }}>
            Get started in 4 simple steps
          </Typography>
          <Grid container spacing={4}>
            {howItWorks.map((item, index) => (
              <Grid item xs={12} sm={6} md={3} key={index}>
                <Box sx={{ textAlign: 'center' }}>
                  <Avatar
                    sx={{
                      width: 80,
                      height: 80,
                      backgroundColor: 'primary.main',
                      fontSize: '2rem',
                      fontWeight: 700,
                      mx: 'auto',
                      mb: 2,
                    }}
                  >
                    {item.step}
                  </Avatar>
                  <Typography variant="h6" sx={{ fontWeight: 600, mb: 1 }}>
                    {item.title}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    {item.description}
                  </Typography>
                </Box>
              </Grid>
            ))}
          </Grid>
        </Container>
      </Box>

      {/* Testimonials Section */}
      <Container maxWidth="lg" sx={{ py: 10 }}>
        <Typography variant="h3" align="center" sx={{ fontWeight: 700, mb: 2 }}>
          What People Say
        </Typography>
        <Typography variant="h6" align="center" color="text.secondary" sx={{ mb: 6 }}>
          Trusted by healthcare professionals and patients
        </Typography>
        <Grid container spacing={4}>
          {testimonials.map((testimonial, index) => (
            <Grid item xs={12} md={4} key={index}>
              <Card elevation={2} sx={{ height: '100%' }}>
                <CardContent sx={{ p: 4 }}>
                  <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                    <Avatar sx={{ width: 60, height: 60, mr: 2, backgroundColor: 'primary.main' }}>
                      {testimonial.avatar}
                    </Avatar>
                    <Box>
                      <Typography variant="h6" sx={{ fontWeight: 600 }}>
                        {testimonial.name}
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        {testimonial.role}
                      </Typography>
                    </Box>
                  </Box>
                  <Rating value={testimonial.rating} readOnly sx={{ mb: 2 }} />
                  <Typography variant="body2" color="text.secondary">
                    "{testimonial.comment}"
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
          ))}
        </Grid>
      </Container>

      {/* CTA Section */}
      <Box
        sx={{
          background: `linear-gradient(135deg, ${theme.palette.primary.main} 0%, ${theme.palette.primary.dark} 100%)`,
          color: 'white',
          py: 8,
        }}
      >
        <Container maxWidth="md">
          <Typography variant="h3" align="center" sx={{ fontWeight: 700, mb: 2 }}>
            Ready to Get Started?
          </Typography>
          <Typography variant="h6" align="center" sx={{ mb: 4, opacity: 0.9 }}>
            Join thousands of users who trust MedAI-Pro for their health insights
          </Typography>
          <Box sx={{ display: 'flex', justifyContent: 'center' }}>
            <SignUpButton mode="modal">
              <Button
                variant="contained"
                size="large"
                sx={{
                  backgroundColor: 'white',
                  color: 'primary.main',
                  px: 6,
                  py: 2,
                  fontSize: '1.2rem',
                  '&:hover': {
                    backgroundColor: 'rgba(255, 255, 255, 0.9)',
                  },
                }}
              >
                Start Your Free Trial
              </Button>
            </SignUpButton>
          </Box>
        </Container>
      </Box>
    </Box>
  );
};

export default LandingPage;

