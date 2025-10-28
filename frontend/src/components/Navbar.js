import React, { useState } from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import {
  AppBar,
  Toolbar,
  Typography,
  Button,
  IconButton,
  Box,
  Menu,
  MenuItem,
  useMediaQuery,
  useTheme as useMuiTheme,
  Container,
} from '@mui/material';
import {
  Menu as MenuIcon,
  Brightness4,
  Brightness7,
  Language,
  LocalHospital,
} from '@mui/icons-material';
import { SignInButton, SignUpButton, UserButton, useUser } from '@clerk/clerk-react';
import { useTheme } from '../context/ThemeContext';

const Navbar = () => {
  const { isSignedIn } = useUser();
  const { darkMode, toggleDarkMode } = useTheme();
  const muiTheme = useMuiTheme();
  const isMobile = useMediaQuery(muiTheme.breakpoints.down('md'));
  const navigate = useNavigate();
  const location = useLocation();
  const [mobileMenuAnchor, setMobileMenuAnchor] = useState(null);
  const [languageAnchor, setLanguageAnchor] = useState(null);

  const publicLinks = [
    { label: 'Home', path: '/' },
    { label: 'About', path: '/about' },
    { label: 'Contact', path: '/contact' },
  ];

  const authenticatedLinks = [
    { label: 'Dashboard', path: '/dashboard' },
    { label: 'Diagnose', path: '/diagnose' },
    { label: 'History', path: '/history' },
    { label: 'Maps', path: '/maps' },
    { label: 'Profile', path: '/profile' },
  ];

  const languages = [
    { code: 'en', name: 'English' },
    { code: 'hi', name: 'हिंदी' },
    { code: 'bn', name: 'বাংলা' },
    { code: 'te', name: 'తెలుగు' },
    { code: 'mr', name: 'मराठी' },
    { code: 'ta', name: 'தமிழ்' },
    { code: 'gu', name: 'ગુજરાતી' },
    { code: 'kn', name: 'ಕನ್ನಡ' },
    { code: 'ml', name: 'മലയാളം' },
    { code: 'pa', name: 'ਪੰਜਾਬੀ' },
    { code: 'or', name: 'ଓଡ଼ିଆ' },
  ];

  const handleMobileMenuOpen = (event) => {
    setMobileMenuAnchor(event.currentTarget);
  };

  const handleMobileMenuClose = () => {
    setMobileMenuAnchor(null);
  };

  const handleLanguageMenuOpen = (event) => {
    setLanguageAnchor(event.currentTarget);
  };

  const handleLanguageMenuClose = () => {
    setLanguageAnchor(null);
  };

  const handleLanguageChange = (languageCode) => {
    localStorage.setItem('language', languageCode);
    handleLanguageMenuClose();
    // Trigger language change event
    window.dispatchEvent(new CustomEvent('languageChange', { detail: languageCode }));
  };

  const isActive = (path) => location.pathname === path;

  const links = isSignedIn ? authenticatedLinks : publicLinks;

  return (
    <AppBar
      position="sticky"
      elevation={2}
      sx={{
        backgroundColor: darkMode ? 'rgba(30, 30, 30, 0.95)' : 'rgba(255, 255, 255, 0.95)',
        backdropFilter: 'blur(10px)',
        borderBottom: `1px solid ${darkMode ? 'rgba(255, 255, 255, 0.1)' : 'rgba(0, 0, 0, 0.1)'}`,
      }}
    >
      <Container maxWidth="xl">
        <Toolbar disableGutters>
          {/* Logo */}
          <LocalHospital sx={{ display: { xs: 'none', md: 'flex' }, mr: 1, color: 'primary.main' }} />
          <Typography
            variant="h6"
            noWrap
            component={Link}
            to="/"
            sx={{
              mr: 2,
              display: { xs: 'none', md: 'flex' },
              fontWeight: 700,
              color: 'text.primary',
              textDecoration: 'none',
              background: 'linear-gradient(45deg, #2196f3 30%, #21cbf3 90%)',
              WebkitBackgroundClip: 'text',
              WebkitTextFillColor: 'transparent',
            }}
          >
            MedAI-Pro
          </Typography>

          {/* Mobile Menu Icon */}
          {isMobile && (
            <Box sx={{ flexGrow: 1, display: { xs: 'flex', md: 'none' } }}>
              <IconButton
                size="large"
                aria-label="menu"
                aria-controls="mobile-menu"
                aria-haspopup="true"
                onClick={handleMobileMenuOpen}
                color="inherit"
              >
                <MenuIcon />
              </IconButton>
              <Menu
                id="mobile-menu"
                anchorEl={mobileMenuAnchor}
                anchorOrigin={{
                  vertical: 'bottom',
                  horizontal: 'left',
                }}
                keepMounted
                transformOrigin={{
                  vertical: 'top',
                  horizontal: 'left',
                }}
                open={Boolean(mobileMenuAnchor)}
                onClose={handleMobileMenuClose}
                sx={{
                  display: { xs: 'block', md: 'none' },
                }}
              >
                {links.map((link) => (
                  <MenuItem
                    key={link.path}
                    onClick={() => {
                      navigate(link.path);
                      handleMobileMenuClose();
                    }}
                    selected={isActive(link.path)}
                  >
                    {link.label}
                  </MenuItem>
                ))}
              </Menu>
            </Box>
          )}

          {/* Mobile Logo */}
          <LocalHospital sx={{ display: { xs: 'flex', md: 'none' }, mr: 1, color: 'primary.main' }} />
          <Typography
            variant="h6"
            noWrap
            component={Link}
            to="/"
            sx={{
              mr: 2,
              display: { xs: 'flex', md: 'none' },
              flexGrow: 1,
              fontWeight: 700,
              color: 'text.primary',
              textDecoration: 'none',
            }}
          >
            MedAI-Pro
          </Typography>

          {/* Desktop Navigation Links */}
          <Box sx={{ flexGrow: 1, display: { xs: 'none', md: 'flex' }, gap: 1 }}>
            {links.map((link) => (
              <Button
                key={link.path}
                component={Link}
                to={link.path}
                sx={{
                  color: 'text.primary',
                  display: 'block',
                  fontWeight: isActive(link.path) ? 600 : 400,
                  borderBottom: isActive(link.path) ? '2px solid' : 'none',
                  borderColor: 'primary.main',
                  borderRadius: 0,
                  '&:hover': {
                    backgroundColor: 'action.hover',
                  },
                }}
              >
                {link.label}
              </Button>
            ))}
          </Box>

          {/* Right Side Actions */}
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            {/* Language Selector */}
            <IconButton onClick={handleLanguageMenuOpen} color="inherit" size="small">
              <Language />
            </IconButton>
            <Menu
              anchorEl={languageAnchor}
              open={Boolean(languageAnchor)}
              onClose={handleLanguageMenuClose}
            >
              {languages.map((lang) => (
                <MenuItem key={lang.code} onClick={() => handleLanguageChange(lang.code)}>
                  {lang.name}
                </MenuItem>
              ))}
            </Menu>

            {/* Dark Mode Toggle */}
            <IconButton onClick={toggleDarkMode} color="inherit" size="small">
              {darkMode ? <Brightness7 /> : <Brightness4 />}
            </IconButton>

            {/* Auth Buttons */}
            {!isSignedIn ? (
              <>
                <SignInButton mode="modal">
                  <Button variant="outlined" size="small" sx={{ display: { xs: 'none', sm: 'inline-flex' } }}>
                    Sign In
                  </Button>
                </SignInButton>
                <SignUpButton mode="modal">
                  <Button variant="contained" size="small">
                    Get Started
                  </Button>
                </SignUpButton>
              </>
            ) : (
              <UserButton
                afterSignOutUrl="/"
                appearance={{
                  elements: {
                    avatarBox: 'w-10 h-10',
                  },
                }}
              />
            )}
          </Box>
        </Toolbar>
      </Container>
    </AppBar>
  );
};

export default Navbar;

