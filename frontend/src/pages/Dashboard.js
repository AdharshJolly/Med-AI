import React, { useEffect, useState } from 'react';
import { useUser } from '@clerk/clerk-react';
import {
  Container,
  Grid,
  Paper,
  Typography,
  Card,
  CardContent,
  Button,
  Box,
  LinearProgress,
} from '@mui/material';
import {
  LocalHospital,
  TrendingUp,
  Assessment,
  Favorite,
} from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
import { getDashboardInsights, getHealthStats } from '../services/api';
import { Line } from 'react-chartjs-2';
import { Chart as ChartJS, CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend } from 'chart.js';

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend);

const Dashboard = () => {
  const { user } = useUser();
  const navigate = useNavigate();
  const [insights, setInsights] = useState(null);
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchDashboardData();
  }, [user]);

  const fetchDashboardData = async () => {
    try {
      setLoading(true);
      const [insightsRes, statsRes] = await Promise.all([
        getDashboardInsights(user.id),
        getHealthStats(user.id),
      ]);
      setInsights(insightsRes.data);
      setStats(statsRes.data);
    } catch (error) {
      console.error('Error fetching dashboard data:', error);
    } finally {
      setLoading(false);
    }
  };

  const chartData = {
    labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
    datasets: [
      {
        label: 'Health Score',
        data: [75, 78, 80, 77, 82, 85],
        borderColor: 'rgb(75, 192, 192)',
        tension: 0.1,
      },
    ],
  };

  const quickActions = [
    {
      title: 'New Diagnosis',
      description: 'Get AI-powered medical diagnosis',
      icon: <LocalHospital sx={{ fontSize: 40 }} />,
      color: '#2196f3',
      path: '/diagnose',
    },
  ];

  return (
    <Box sx={{ minHeight: '100vh', backgroundColor: 'background.default', py: 4 }}>
      <Container maxWidth="lg">
        <Typography variant="h3" sx={{ fontWeight: 700, mb: 2 }}>
          Health Dashboard
        </Typography>
        <Typography variant="h6" color="text.secondary" sx={{ mb: 4 }}>
          Your comprehensive health overview and AI insights
        </Typography>

        {loading ? (
          <LinearProgress />
        ) : (
          <>
            {/* Stats */}
            <Grid container spacing={3} sx={{ mb: 4 }}>
              <Grid item xs={12} sm={6} md={3}>
                <Card elevation={2}>
                  <CardContent>
                    <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                      <Assessment sx={{ color: 'primary.main', mr: 1 }} />
                      <Typography variant="h6">Total Diagnoses</Typography>
                    </Box>
                    <Typography variant="h3" sx={{ fontWeight: 700 }}>
                      {stats?.total_diagnoses || 0}
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
                      {stats?.health_score || 'N/A'}
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
                      {stats?.trend || 'Stable'}
                    </Typography>
                  </CardContent>
                </Card>
              </Grid>
              <Grid item xs={12} sm={6} md={3}>
                <Card elevation={2}>
                  <CardContent>
                    <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                      <LocalHospital sx={{ color: 'warning.main', mr: 1 }} />
                      <Typography variant="h6">Last Check</Typography>
                    </Box>
                    <Typography variant="body1" sx={{ fontWeight: 600 }}>
                      {stats?.last_diagnosis_date
                        ? new Date(stats.last_diagnosis_date).toLocaleDateString()
                        : 'Never'}
                    </Typography>
                  </CardContent>
                </Card>
              </Grid>
            </Grid>

            {/* Health Trends Chart */}
            <Card elevation={3} sx={{ mb: 4 }}>
              <CardContent>
                <Typography variant="h6" sx={{ fontWeight: 600, mb: 3 }}>
                  Health Trends
                </Typography>
                <Line data={chartData} options={{ responsive: true }} />
              </CardContent>
            </Card>

            {/* AI Insights */}
            {insights && (
              <Card elevation={3} sx={{ mb: 4 }}>
                <CardContent>
                  <Typography variant="h6" sx={{ fontWeight: 600, mb: 2 }}>
                    AI Health Insights
                  </Typography>
                  <Typography variant="body1" paragraph>
                    {insights.summary || 'No insights available yet. Complete a diagnosis to get personalized health insights.'}
                  </Typography>
                  <Button variant="outlined">View Detailed Insights</Button>
                </CardContent>
              </Card>
            )}

            {/* Quick Actions */}
            <Typography variant="h6" sx={{ fontWeight: 600, mb: 2 }}>
              Quick Actions
            </Typography>
            <Grid container spacing={3}>
              {quickActions.map((action, index) => (
                <Grid item xs={12} sm={6} md={4} key={index}>
                  <Card
                    elevation={2}
                    sx={{
                      cursor: 'pointer',
                      '&:hover': { boxShadow: 6 },
                    }}
                    onClick={() => navigate(action.path)}
                  >
                    <CardContent>
                      <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                        <Box sx={{ color: action.color, mr: 2 }}>{action.icon}</Box>
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
                  </Card>
                </Grid>
              ))}
            </Grid>
          </>
        )}
      </Container>
    </Box>
  );
};

export default Dashboard;

