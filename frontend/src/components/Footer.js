import React from 'react';
import { Link } from 'react-router-dom';
import {
  Box,
  Container,
  Grid,
  Typography,
  IconButton,
  Divider,
  Alert,
  AlertTitle,
} from '@mui/material';
import {
  Facebook,
  Twitter,
  LinkedIn,
  Instagram,
  LocalHospital,
  Email,
  Phone,
  LocationOn,
} from '@mui/icons-material';
import { useTheme } from '../context/ThemeContext';

const Footer = () => {
  const { darkMode } = useTheme();

  const footerLinks = {
    product: [
      { label: 'Features', path: '/#features' },
      { label: 'How It Works', path: '/#how-it-works' },
      { label: 'Pricing', path: '/pricing' },
      { label: 'FAQ', path: '/faq' },
    ],
    company: [
      { label: 'About Us', path: '/about' },
      { label: 'Contact', path: '/contact' },
      { label: 'Careers', path: '/careers' },
      { label: 'Blog', path: '/blog' },
    ],
    legal: [
      { label: 'Terms of Service', path: '/terms' },
      { label: 'Privacy Policy', path: '/privacy' },
      { label: 'Disclaimer', path: '/disclaimer' },
      { label: 'Cookie Policy', path: '/cookies' },
    ],
    support: [
      { label: 'Help Center', path: '/help' },
      { label: 'Documentation', path: '/docs' },
      { label: 'API Reference', path: '/api-docs' },
      { label: 'Status', path: '/status' },
    ],
  };

  const socialLinks = [
    { icon: <Facebook />, url: 'https://facebook.com/medaipro', label: 'Facebook' },
    { icon: <Twitter />, url: 'https://twitter.com/medaipro', label: 'Twitter' },
    { icon: <LinkedIn />, url: 'https://linkedin.com/company/medaipro', label: 'LinkedIn' },
    { icon: <Instagram />, url: 'https://instagram.com/medaipro', label: 'Instagram' },
  ];

  return (
    <Box
      component="footer"
      sx={{
        backgroundColor: darkMode ? '#1a1a1a' : '#f8f9fa',
        borderTop: `1px solid ${darkMode ? 'rgba(255, 255, 255, 0.1)' : 'rgba(0, 0, 0, 0.1)'}`,
        mt: 'auto',
        py: 6,
      }}
    >
      <Container maxWidth="xl">
        {/* Critical Medical Disclaimer */}
        <Alert
          severity="error"
          sx={{
            mb: 4,
            backgroundColor: darkMode ? 'rgba(211, 47, 47, 0.2)' : 'rgba(211, 47, 47, 0.1)',
            border: '2px solid',
            borderColor: 'error.main',
          }}
        >
          <AlertTitle sx={{ fontWeight: 700, fontSize: '1.1rem' }}>
            IMPORTANT MEDICAL DISCLAIMER
          </AlertTitle>
          <Typography variant="body1" sx={{ fontWeight: 600, mb: 1 }}>
            THIS IS JUST AN AI APPLICATION WHICH WILL PREDICT YOUR DISEASES BASED ON PAST DATA. IF
            ANYTHING IS SERIOUS PLEASE CONSULT A DOCTOR. WE ARE NOT RESPONSIBLE FOR YOUR LOSS.
          </Typography>
          <Typography variant="body2" sx={{ mt: 1 }}>
            MedAI-Pro is not a substitute for professional medical advice, diagnosis, or treatment.
            Always seek the advice of your physician or other qualified health provider with any
            questions you may have regarding a medical condition. Never disregard professional
            medical advice or delay in seeking it because of something you have read on this
            application.
          </Typography>
        </Alert>

        {/* Footer Content */}
        <Grid container spacing={4} sx={{ mb: 4 }}>
          {/* Company Info */}
          <Grid item xs={12} md={4}>
            <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
              <LocalHospital sx={{ fontSize: 40, color: 'primary.main', mr: 1 }} />
              <Typography variant="h5" sx={{ fontWeight: 700 }}>
                MedAI-Pro
              </Typography>
            </Box>
            <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
              AI-powered medical diagnosis platform providing instant health insights through
              multi-modal analysis. Empowering healthcare with artificial intelligence.
            </Typography>
            <Box sx={{ display: 'flex', gap: 1 }}>
              {socialLinks.map((social) => (
                <IconButton
                  key={social.label}
                  component="a"
                  href={social.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  size="small"
                  sx={{
                    color: 'text.secondary',
                    '&:hover': {
                      color: 'primary.main',
                    },
                  }}
                  aria-label={social.label}
                >
                  {social.icon}
                </IconButton>
              ))}
            </Box>
          </Grid>

          {/* Product Links */}
          <Grid item xs={6} sm={3} md={2}>
            <Typography variant="h6" sx={{ fontWeight: 600, mb: 2 }}>
              Product
            </Typography>
            {footerLinks.product.map((link) => (
              <Typography
                key={link.label}
                variant="body2"
                component={Link}
                to={link.path}
                sx={{
                  display: 'block',
                  color: 'text.secondary',
                  textDecoration: 'none',
                  mb: 1,
                  '&:hover': {
                    color: 'primary.main',
                  },
                }}
              >
                {link.label}
              </Typography>
            ))}
          </Grid>

          {/* Company Links */}
          <Grid item xs={6} sm={3} md={2}>
            <Typography variant="h6" sx={{ fontWeight: 600, mb: 2 }}>
              Company
            </Typography>
            {footerLinks.company.map((link) => (
              <Typography
                key={link.label}
                variant="body2"
                component={Link}
                to={link.path}
                sx={{
                  display: 'block',
                  color: 'text.secondary',
                  textDecoration: 'none',
                  mb: 1,
                  '&:hover': {
                    color: 'primary.main',
                  },
                }}
              >
                {link.label}
              </Typography>
            ))}
          </Grid>

          {/* Legal Links */}
          <Grid item xs={6} sm={3} md={2}>
            <Typography variant="h6" sx={{ fontWeight: 600, mb: 2 }}>
              Legal
            </Typography>
            {footerLinks.legal.map((link) => (
              <Typography
                key={link.label}
                variant="body2"
                component={Link}
                to={link.path}
                sx={{
                  display: 'block',
                  color: 'text.secondary',
                  textDecoration: 'none',
                  mb: 1,
                  '&:hover': {
                    color: 'primary.main',
                  },
                }}
              >
                {link.label}
              </Typography>
            ))}
          </Grid>

          {/* Contact Info */}
          <Grid item xs={6} sm={3} md={2}>
            <Typography variant="h6" sx={{ fontWeight: 600, mb: 2 }}>
              Contact
            </Typography>
            <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
              <Email sx={{ fontSize: 18, mr: 1, color: 'text.secondary' }} />
              <Typography variant="body2" color="text.secondary">
                support@medaipro.com
              </Typography>
            </Box>
            <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
              <Phone sx={{ fontSize: 18, mr: 1, color: 'text.secondary' }} />
              <Typography variant="body2" color="text.secondary">
                +91 1800 123 4567
              </Typography>
            </Box>
            <Box sx={{ display: 'flex', alignItems: 'flex-start', mb: 1 }}>
              <LocationOn sx={{ fontSize: 18, mr: 1, color: 'text.secondary' }} />
              <Typography variant="body2" color="text.secondary">
                Bangalore, Karnataka, India
              </Typography>
            </Box>
          </Grid>
        </Grid>

        <Divider sx={{ my: 3 }} />

        {/* Emergency Helpline */}
        <Alert severity="warning" sx={{ mb: 3 }}>
          <AlertTitle sx={{ fontWeight: 600 }}>Emergency Medical Helpline</AlertTitle>
          <Typography variant="body2">
            For medical emergencies, please call <strong>108</strong> (India) or your local
            emergency number immediately. Do not rely on this application for emergency medical
            situations.
          </Typography>
        </Alert>

        {/* Bottom Bar */}
        <Box
          sx={{
            display: 'flex',
            flexDirection: { xs: 'column', sm: 'row' },
            justifyContent: 'space-between',
            alignItems: 'center',
            gap: 2,
          }}
        >
          <Typography variant="body2" color="text.secondary">
            © {new Date().getFullYear()} MedAI-Pro. All rights reserved.
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Made with ❤️ for better healthcare
          </Typography>
        </Box>
      </Container>
    </Box>
  );
};

export default Footer;

