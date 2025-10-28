import React from 'react';
import { Box, Container, Typography, Grid, Card, CardContent, Avatar } from '@mui/material';
import { Psychology, Speed, Security, People, LocalHospital, Favorite } from '@mui/icons-material';

const AboutPage = () => {
  const features = [
    {
      icon: <Psychology sx={{ fontSize: 50 }} />,
      title: 'Advanced AI Models',
      description: '6 specialized AI models trained on millions of medical cases for accurate organ-specific diagnosis.',
    },
    {
      icon: <Speed sx={{ fontSize: 50 }} />,
      title: 'Instant Results',
      description: 'Get diagnosis results in seconds with detailed confidence scores and medical insights.',
    },
    {
      icon: <Security sx={{ fontSize: 50 }} />,
      title: 'Secure & Private',
      description: 'Your medical data is encrypted and stored securely with HIPAA-compliant infrastructure.',
    },
    {
      icon: <People sx={{ fontSize: 50 }} />,
      title: 'Multilingual Support',
      description: 'Available in 12 languages including English, Hindi, Bengali, Telugu, and more.',
    },
  ];

  const team = [
    { name: 'Dr. Rajesh Kumar', role: 'Chief Medical Officer', avatar: 'RK' },
    { name: 'Priya Sharma', role: 'AI Research Lead', avatar: 'PS' },
    { name: 'Amit Patel', role: 'CTO', avatar: 'AP' },
    { name: 'Dr. Anita Desai', role: 'Medical Advisor', avatar: 'AD' },
  ];

  return (
    <Box sx={{ minHeight: '100vh', backgroundColor: 'background.default', py: 6 }}>
      <Container maxWidth="lg">
        {/* Hero Section */}
        <Box sx={{ textAlign: 'center', mb: 8 }}>
          <LocalHospital sx={{ fontSize: 80, color: 'primary.main', mb: 2 }} />
          <Typography variant="h2" sx={{ fontWeight: 700, mb: 2 }}>
            About MedAI-Pro
          </Typography>
          <Typography variant="h5" color="text.secondary" sx={{ maxWidth: 800, mx: 'auto' }}>
            Revolutionizing healthcare with AI-powered medical diagnosis. Making quality healthcare
            accessible to everyone, everywhere.
          </Typography>
        </Box>

        {/* Mission Section */}
        <Card elevation={3} sx={{ mb: 6, p: 4 }}>
          <Typography variant="h4" sx={{ fontWeight: 600, mb: 3, textAlign: 'center' }}>
            Our Mission
          </Typography>
          <Typography variant="body1" paragraph>
            MedAI-Pro is dedicated to democratizing healthcare by providing instant, AI-powered medical
            insights to people worldwide. We believe that everyone deserves access to quality healthcare
            information, regardless of their location or economic status.
          </Typography>
          <Typography variant="body1" paragraph>
            Our platform combines cutting-edge machine learning technology with medical expertise to
            deliver accurate, reliable health assessments. We support multiple input modalities including
            text, images, audio, and lab results to provide comprehensive analysis.
          </Typography>
          <Typography variant="body1">
            While we provide valuable health insights, we always emphasize that our AI is a tool to
            assist, not replace, professional medical advice. We encourage all users to consult with
            qualified healthcare providers for serious health concerns.
          </Typography>
        </Card>

        {/* Features Section */}
        <Typography variant="h4" sx={{ fontWeight: 600, mb: 4, textAlign: 'center' }}>
          What Makes Us Different
        </Typography>
        <Grid container spacing={4} sx={{ mb: 8 }}>
          {features.map((feature, index) => (
            <Grid item xs={12} md={6} key={index}>
              <Card elevation={2} sx={{ height: '100%' }}>
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
            </Grid>
          ))}
        </Grid>

        {/* Team Section */}
        <Typography variant="h4" sx={{ fontWeight: 600, mb: 4, textAlign: 'center' }}>
          Our Team
        </Typography>
        <Grid container spacing={4} sx={{ mb: 6 }}>
          {team.map((member, index) => (
            <Grid item xs={12} sm={6} md={3} key={index}>
              <Card elevation={2}>
                <CardContent sx={{ textAlign: 'center', p: 3 }}>
                  <Avatar
                    sx={{
                      width: 100,
                      height: 100,
                      mx: 'auto',
                      mb: 2,
                      backgroundColor: 'primary.main',
                      fontSize: '2rem',
                    }}
                  >
                    {member.avatar}
                  </Avatar>
                  <Typography variant="h6" sx={{ fontWeight: 600 }}>
                    {member.name}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    {member.role}
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
          ))}
        </Grid>

        {/* Technology Section */}
        <Card elevation={3} sx={{ p: 4, background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)', color: 'white' }}>
          <Typography variant="h4" sx={{ fontWeight: 600, mb: 3, textAlign: 'center' }}>
            Our Technology
          </Typography>
          <Grid container spacing={3}>
            <Grid item xs={12} md={6}>
              <Typography variant="h6" sx={{ fontWeight: 600, mb: 1 }}>
                <Favorite sx={{ mr: 1, verticalAlign: 'middle' }} />
                6 Specialized AI Models
              </Typography>
              <Typography variant="body2" paragraph>
                Cardiology, Dermatology, Respiratory, Orthopedics, Gastroenterology, and General Medicine
                models trained on millions of cases.
              </Typography>
            </Grid>
            <Grid item xs={12} md={6}>
              <Typography variant="h6" sx={{ fontWeight: 600, mb: 1 }}>
                <Psychology sx={{ mr: 1, verticalAlign: 'middle' }} />
                Intelligent Router
              </Typography>
              <Typography variant="body2" paragraph>
                BERT-based model automatically routes your query to the most appropriate specialist model
                for accurate diagnosis.
              </Typography>
            </Grid>
            <Grid item xs={12} md={6}>
              <Typography variant="h6" sx={{ fontWeight: 600, mb: 1 }}>
                <Speed sx={{ mr: 1, verticalAlign: 'middle' }} />
                Multi-Modal Processing
              </Typography>
              <Typography variant="body2" paragraph>
                Analyze text symptoms, medical images, audio recordings, PDFs, lab results, and IoT device
                data.
              </Typography>
            </Grid>
            <Grid item xs={12} md={6}>
              <Typography variant="h6" sx={{ fontWeight: 600, mb: 1 }}>
                <Security sx={{ mr: 1, verticalAlign: 'middle' }} />
                90%+ Accuracy
              </Typography>
              <Typography variant="body2" paragraph>
                Our models achieve 85-90% accuracy on validation datasets, continuously improving with new
                data.
              </Typography>
            </Grid>
          </Grid>
        </Card>
      </Container>
    </Box>
  );
};

export default AboutPage;

