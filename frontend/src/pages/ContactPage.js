import React, { useState } from 'react';
import {
  Box,
  Container,
  Typography,
  TextField,
  Button,
  Grid,
  Card,
  CardContent,
  Alert,
  CircularProgress,
} from '@mui/material';
import { Email, Phone, LocationOn, Send } from '@mui/icons-material';
import { submitContactForm } from '../services/api';

const ContactPage = () => {
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    subject: '',
    message: '',
  });
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState(false);
  const [error, setError] = useState('');

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    setSuccess(false);

    try {
      await submitContactForm(formData);
      setSuccess(true);
      setFormData({ name: '', email: '', subject: '', message: '' });
    } catch (err) {
      setError('Failed to send message. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const contactInfo = [
    {
      icon: <Email sx={{ fontSize: 40 }} />,
      title: 'Email',
      value: 'support@medaipro.com',
      link: 'mailto:support@medaipro.com',
    },
    {
      icon: <Phone sx={{ fontSize: 40 }} />,
      title: 'Phone',
      value: '+91 1800 123 4567',
      link: 'tel:+911800123456 7',
    },
    {
      icon: <LocationOn sx={{ fontSize: 40 }} />,
      title: 'Address',
      value: 'Bangalore, Karnataka, India',
      link: null,
    },
  ];

  return (
    <Box sx={{ minHeight: '100vh', backgroundColor: 'background.default', py: 6 }}>
      <Container maxWidth="lg">
        <Typography variant="h2" sx={{ fontWeight: 700, mb: 2, textAlign: 'center' }}>
          Contact Us
        </Typography>
        <Typography variant="h6" color="text.secondary" sx={{ mb: 6, textAlign: 'center' }}>
          Have questions? We'd love to hear from you.
        </Typography>

        <Grid container spacing={4}>
          {/* Contact Info */}
          <Grid item xs={12} md={4}>
            {contactInfo.map((info, index) => (
              <Card key={index} elevation={2} sx={{ mb: 3 }}>
                <CardContent sx={{ textAlign: 'center', p: 3 }}>
                  <Box sx={{ color: 'primary.main', mb: 2 }}>{info.icon}</Box>
                  <Typography variant="h6" sx={{ fontWeight: 600, mb: 1 }}>
                    {info.title}
                  </Typography>
                  {info.link ? (
                    <Typography
                      component="a"
                      href={info.link}
                      variant="body1"
                      sx={{ color: 'text.secondary', textDecoration: 'none' }}
                    >
                      {info.value}
                    </Typography>
                  ) : (
                    <Typography variant="body1" color="text.secondary">
                      {info.value}
                    </Typography>
                  )}
                </CardContent>
              </Card>
            ))}

            <Card elevation={2} sx={{ background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)', color: 'white' }}>
              <CardContent sx={{ p: 3 }}>
                <Typography variant="h6" sx={{ fontWeight: 600, mb: 2 }}>
                  Emergency?
                </Typography>
                <Typography variant="body2" paragraph>
                  For medical emergencies, please call 108 (India) or your local emergency number immediately.
                </Typography>
                <Typography variant="body2">
                  Do not use this form for urgent medical situations.
                </Typography>
              </CardContent>
            </Card>
          </Grid>

          {/* Contact Form */}
          <Grid item xs={12} md={8}>
            <Card elevation={3}>
              <CardContent sx={{ p: 4 }}>
                <Typography variant="h5" sx={{ fontWeight: 600, mb: 3 }}>
                  Send us a Message
                </Typography>

                {success && (
                  <Alert severity="success" sx={{ mb: 3 }}>
                    Thank you for contacting us! We'll get back to you soon.
                  </Alert>
                )}

                {error && (
                  <Alert severity="error" sx={{ mb: 3 }}>
                    {error}
                  </Alert>
                )}

                <form onSubmit={handleSubmit}>
                  <Grid container spacing={3}>
                    <Grid item xs={12} sm={6}>
                      <TextField
                        fullWidth
                        label="Name"
                        name="name"
                        value={formData.name}
                        onChange={handleChange}
                        required
                      />
                    </Grid>
                    <Grid item xs={12} sm={6}>
                      <TextField
                        fullWidth
                        label="Email"
                        name="email"
                        type="email"
                        value={formData.email}
                        onChange={handleChange}
                        required
                      />
                    </Grid>
                    <Grid item xs={12}>
                      <TextField
                        fullWidth
                        label="Subject"
                        name="subject"
                        value={formData.subject}
                        onChange={handleChange}
                        required
                      />
                    </Grid>
                    <Grid item xs={12}>
                      <TextField
                        fullWidth
                        label="Message"
                        name="message"
                        value={formData.message}
                        onChange={handleChange}
                        multiline
                        rows={6}
                        required
                      />
                    </Grid>
                    <Grid item xs={12}>
                      <Button
                        type="submit"
                        variant="contained"
                        size="large"
                        fullWidth
                        disabled={loading}
                        startIcon={loading ? <CircularProgress size={20} /> : <Send />}
                      >
                        {loading ? 'Sending...' : 'Send Message'}
                      </Button>
                    </Grid>
                  </Grid>
                </form>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      </Container>
    </Box>
  );
};

export default ContactPage;

