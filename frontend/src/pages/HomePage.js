import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useUser } from '@clerk/clerk-react';
import {
  Box,
  Container,
  Typography,
  Grid,
  Card,
  CardContent,
  CardActions,
  Button,
  Avatar,
  LinearProgress,
  Chip,
} from '@mui/material';
import {
  Dashboard as DashboardIcon,
  LocalHospital,
  History,
  Map,
  Person,
  TrendingUp,
  Favorite,
  Assessment,
} from '@mui/icons-material';
import { motion } from 'framer-motion';
import { getHealthStats, getRecentDiagnoses } from '../services/api';

const HomePage = () => {
  const { user } = useUser();
  const navigate = useNavigate();
  const [stats, setStats] = useState(null);
  const [recentDiagnoses, setRecentDiagnoses] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchData();
  }, [user]);

  const fetchData = async () => {
    try {
      setLoading(true);
      const [statsRes, diagnosesRes] = await Promise.all([
        getHealthStats(user.id),
        getRecentDiagnoses(user.id, 3),
      ]);
      setStats(statsRes.data);
      setRecentDiagnoses(diagnosesRes.data);
    } catch (error) {
      console.error('Error fetching data:', error);
    } finally {
      setLoading(false);
    }
  };

  const quickActions = [
    {
      title: 'New Diagnosis',
      description: 'Get AI-powered health analysis',
      icon: <LocalHospital sx={{ fontSize: 40 }} />,
      color: '#2196f3',
      path: '/diagnose',
    },
    {
      title: 'Dashboard',
      description: 'View your health overview',
      icon: <DashboardIcon sx={{ fontSize: 40 }} />,
      color: '#4caf50',
      path: '/dashboard',
    },
    {
      title: 'History',
      description: 'View past diagnoses',
      icon: <History sx={{ fontSize: 40 }} />,
      color: '#ff9800',
      path: '/history',
    },
    {
      title: 'Find Hospitals',
      description: 'Locate nearby facilities',
      icon: <Map sx={{ fontSize: 40 }} />,
      color: '#f44336',
      path: '/maps',
    },
    {
      title: 'Profile',
      description: 'Manage your health profile',
      icon: <Person sx={{ fontSize: 40 }} />,
      color: '#9c27b0',
      path: '/profile',
    },
    {
      title: 'Health Trends',
      description: 'Track your health metrics',
      icon: <TrendingUp sx={{ fontSize: 40 }} />,
      color: '#00bcd4',
      path: '/dashboard',
    },
  ];

  const getSeverityColor = (severity) => {
    const colors = {
      mild: 'success',
      moderate: 'warning',
      severe: 'error',
    };
    return colors[severity?.toLowerCase()] || 'default';
  };

  return (
    <Box sx={{ minHeight: '100vh', backgroundColor: 'background.default', py: 4 }}>
      <Container maxWidth="xl">
        {/* Welcome Section */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
        >
          <Box sx={{ mb: 4 }}>
            <Typography variant="h3" sx={{ fontWeight: 700, mb: 1 }}>
              Welcome back, {user?.firstName || 'User'}! 👋
            </Typography>
            <Typography variant="h6" color="text.secondary">
              Here's your health overview for today
            </Typography>
          </Box>
        </motion.div>

        {/* Quick Stats */}
        {loading ? (
          <LinearProgress sx={{ mb: 4 }} />
        ) : stats ? (
          <Grid container spacing={3} sx={{ mb: 4 }}>
            <Grid item xs={12} sm={6} md={3}>
              <Card elevation={2}>
                <CardContent>
                  <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                    <Assessment sx={{ color: 'primary.main', mr: 1 }} />
                    <Typography variant="h6">Total Diagnoses</Typography>
                  </Box>
                  <Typography variant="h3" sx={{ fontWeight: 700 }}>
                    {stats.total_diagnoses || 0}
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
              <Card elevation={2}>
                <CardContent>
                  <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                    <Favorite sx={{ color: 'error.main', mr: 1 }} />
                    <Typography variant="h6">Health Score</Typography>
                  </Box>
                  <Typography variant="h3" sx={{ fontWeight: 700 }}>
                    {stats.health_score || 'N/A'}
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
              <Card elevation={2}>
                <CardContent>
                  <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                    <History sx={{ color: 'warning.main', mr: 1 }} />
                    <Typography variant="h6">Last Check</Typography>
                  </Box>
                  <Typography variant="h6" sx={{ fontWeight: 600 }}>
                    {stats.last_diagnosis_date
                      ? new Date(stats.last_diagnosis_date).toLocaleDateString()
                      : 'Never'}
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
              <Card elevation={2}>
                <CardContent>
                  <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                    <TrendingUp sx={{ color: 'success.main', mr: 1 }} />
                    <Typography variant="h6">Trend</Typography>
                  </Box>
                  <Typography variant="h6" sx={{ fontWeight: 600, color: 'success.main' }}>
                    {stats.trend || 'Stable'}
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
          </Grid>
        ) : null}

        {/* Quick Actions */}
        <Typography variant="h5" sx={{ fontWeight: 600, mb: 3 }}>
          Quick Actions
        </Typography>
        <Grid container spacing={3} sx={{ mb: 4 }}>
          {quickActions.map((action, index) => (
            <Grid item xs={12} sm={6} md={4} key={index}>
              <motion.div
                initial={{ opacity: 0, scale: 0.9 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ duration: 0.3, delay: index * 0.05 }}
                whileHover={{ scale: 1.03 }}
              >
                <Card
                  elevation={2}
                  sx={{
                    height: '100%',
                    cursor: 'pointer',
                    transition: 'all 0.3s',
                    '&:hover': {
                      boxShadow: 6,
                    },
                  }}
                  onClick={() => navigate(action.path)}
                >
                  <CardContent>
                    <Box
                      sx={{
                        display: 'flex',
                        alignItems: 'center',
                        mb: 2,
                      }}
                    >
                      <Avatar
                        sx={{
                          backgroundColor: action.color,
                          width: 60,
                          height: 60,
                          mr: 2,
                        }}
                      >
                        {action.icon}
                      </Avatar>
                      <Box>
                        <Typography variant="h6" sx={{ fontWeight: 600 }}>
                          {action.title}
                        </Typography>
                        <Typography variant="body2" color="text.secondary">
                          {action.description}
                        </Typography>
                      </Box>
                    </Box>
                  </CardContent>
                  <CardActions>
                    <Button size="small" sx={{ ml: 'auto' }}>
                      Go →
                    </Button>
                  </CardActions>
                </Card>
              </motion.div>
            </Grid>
          ))}
        </Grid>

        {/* Recent Diagnoses */}
        {recentDiagnoses.length > 0 && (
          <>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
              <Typography variant="h5" sx={{ fontWeight: 600 }}>
                Recent Diagnoses
              </Typography>
              <Button onClick={() => navigate('/history')}>View All</Button>
            </Box>
            <Grid container spacing={3}>
              {recentDiagnoses.map((diagnosis, index) => (
                <Grid item xs={12} md={4} key={index}>
                  <Card elevation={2}>
                    <CardContent>
                      <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 2 }}>
                        <Typography variant="caption" color="text.secondary">
                          {new Date(diagnosis.created_at).toLocaleDateString()}
                        </Typography>
                        <Chip
                          label={diagnosis.severity || 'Unknown'}
                          size="small"
                          color={getSeverityColor(diagnosis.severity)}
                        />
                      </Box>
                      <Typography variant="h6" sx={{ fontWeight: 600, mb: 1 }}>
                        {diagnosis.primary_diagnosis}
                      </Typography>
                      <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                        Confidence: {(diagnosis.confidence * 100).toFixed(1)}%
                      </Typography>
                      <LinearProgress
                        variant="determinate"
                        value={diagnosis.confidence * 100}
                        sx={{ mb: 2 }}
                      />
                      <Button
                        size="small"
                        onClick={() => navigate(`/history?id=${diagnosis.id}`)}
                      >
                        View Details
                      </Button>
                    </CardContent>
                  </Card>
                </Grid>
              ))}
            </Grid>
          </>
        )}

        {/* Health Tips */}
        <Box sx={{ mt: 4 }}>
          <Card
            elevation={2}
            sx={{
              background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
              color: 'white',
            }}
          >
            <CardContent sx={{ p: 4 }}>
              <Typography variant="h5" sx={{ fontWeight: 600, mb: 2 }}>
                💡 Health Tip of the Day
              </Typography>
              <Typography variant="body1">
                Regular health check-ups are essential for early detection of potential health issues.
                Consider scheduling a comprehensive health screening at least once a year.
              </Typography>
            </CardContent>
          </Card>
        </Box>
      </Container>
    </Box>
  );
};

export default HomePage;

