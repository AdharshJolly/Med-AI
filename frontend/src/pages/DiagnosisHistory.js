import React, { useEffect, useState } from 'react';
import { useUser } from '@clerk/clerk-react';
import { Box, Container, Typography, Grid, Card, CardContent, Chip, Button, LinearProgress } from '@mui/material';
import { getDiagnosisHistory } from '../services/api';

const DiagnosisHistory = () => {
  const { user } = useUser();
  const [diagnoses, setDiagnoses] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchHistory();
  }, []);

  const fetchHistory = async () => {
    try {
      const response = await getDiagnosisHistory(user.id);
      setDiagnoses(response.data.diagnoses || []);
    } catch (error) {
      console.error('Error fetching history:', error);
    } finally {
      setLoading(false);
    }
  };

  const getSeverityColor = (severity) => {
    const colors = { mild: 'success', moderate: 'warning', severe: 'error' };
    return colors[severity?.toLowerCase()] || 'default';
  };

  return (
    <Box sx={{ minHeight: '100vh', backgroundColor: 'background.default', py: 4 }}>
      <Container maxWidth="lg">
        <Typography variant="h3" sx={{ fontWeight: 700, mb: 4 }}>
          Diagnosis History
        </Typography>

        {loading ? (
          <LinearProgress />
        ) : diagnoses.length === 0 ? (
          <Card elevation={2}>
            <CardContent sx={{ textAlign: 'center', py: 8 }}>
              <Typography variant="h6" color="text.secondary">
                No diagnosis history yet. Start by getting a new diagnosis.
              </Typography>
              <Button variant="contained" sx={{ mt: 2 }} href="/diagnose">
                New Diagnosis
              </Button>
            </CardContent>
          </Card>
        ) : (
          <Grid container spacing={3}>
            {diagnoses.map((diagnosis, index) => (
              <Grid item xs={12} md={6} key={index}>
                <Card elevation={2}>
                  <CardContent>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 2 }}>
                      <Typography variant="caption" color="text.secondary">
                        {new Date(diagnosis.created_at).toLocaleDateString()}
                      </Typography>
                      <Chip label={diagnosis.severity} size="small" color={getSeverityColor(diagnosis.severity)} />
                    </Box>
                    <Typography variant="h6" sx={{ fontWeight: 600, mb: 1 }}>
                      {diagnosis.primary_diagnosis}
                    </Typography>
                    <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                      Confidence: {(diagnosis.confidence * 100).toFixed(1)}%
                    </Typography>
                    <LinearProgress variant="determinate" value={diagnosis.confidence * 100} sx={{ mb: 2 }} />
                    <Button size="small">View Details</Button>
                    <Button size="small">AI Insights</Button>
                  </CardContent>
                </Card>
              </Grid>
            ))}
          </Grid>
        )}
      </Container>
    </Box>
  );
};

export default DiagnosisHistory;

