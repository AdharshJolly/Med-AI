import React, { useState } from 'react';
import { useUser } from '@clerk/clerk-react';
import {
  Box,
  Container,
  Typography,
  Card,
  CardContent,
  Tabs,
  Tab,
  TextField,
  Button,
  Grid,
  Alert,
  CircularProgress,
  Chip,
  LinearProgress,
} from '@mui/material';
import { CloudUpload, Mic, Description, Biotech, Devices } from '@mui/icons-material';
import { useDropzone } from 'react-dropzone';
import { submitDiagnosis, uploadDiagnosisFile } from '../services/api';

const DiagnosisPage = () => {
  const { user } = useUser();
  const [activeTab, setActiveTab] = useState(0);
  const [symptoms, setSymptoms] = useState('');
  const [uploadedFiles, setUploadedFiles] = useState([]);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState('');

  const { getRootProps, getInputProps } = useDropzone({
    accept: {
      'image/*': ['.png', '.jpg', '.jpeg'],
      'application/pdf': ['.pdf'],
      'audio/*': ['.mp3', '.wav'],
    },
    onDrop: (acceptedFiles) => {
      setUploadedFiles([...uploadedFiles, ...acceptedFiles]);
    },
  });

  const handleSubmit = async () => {
    setLoading(true);
    setError('');
    setResult(null);

    try {
      // Upload files if any
      const fileUrls = [];
      for (const file of uploadedFiles) {
        const formData = new FormData();
        formData.append('file', file);
        const response = await uploadDiagnosisFile(formData);
        fileUrls.push(response.data.url);
      }

      // Submit diagnosis
      const diagnosisData = {
        user_id: user.id,
        symptoms,
        files: fileUrls,
        input_type: activeTab === 0 ? 'text' : activeTab === 1 ? 'image' : 'audio',
      };

      const response = await submitDiagnosis(diagnosisData);
      setResult(response.data);
    } catch (err) {
      setError(err.response?.data?.message || 'Failed to analyze. Please try again.');
    } finally {
      setLoading(false);
    }
  };

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
      <Container maxWidth="lg">
        <Typography variant="h3" sx={{ fontWeight: 700, mb: 2 }}>
          AI Diagnosis
        </Typography>
        <Typography variant="h6" color="text.secondary" sx={{ mb: 4 }}>
          Describe your symptoms or upload medical data for AI-powered analysis
        </Typography>

        <Alert severity="warning" sx={{ mb: 4 }}>
          <Typography variant="body2" sx={{ fontWeight: 600 }}>
            IMPORTANT: This is an AI-powered tool for preliminary assessment only. Always consult a
            qualified healthcare professional for accurate diagnosis and treatment.
          </Typography>
        </Alert>

        <Grid container spacing={4}>
          {/* Input Section */}
          <Grid item xs={12} md={8}>
            <Card elevation={3}>
              <CardContent sx={{ p: 4 }}>
                <Tabs value={activeTab} onChange={(e, v) => setActiveTab(v)} sx={{ mb: 3 }}>
                  <Tab label="Text Symptoms" icon={<Description />} />
                  <Tab label="Upload Images" icon={<CloudUpload />} />
                  <Tab label="Voice Input" icon={<Mic />} />
                  <Tab label="Lab Results" icon={<Biotech />} />
                  <Tab label="IoT Data" icon={<Devices />} />
                </Tabs>

                {activeTab === 0 && (
                  <TextField
                    fullWidth
                    multiline
                    rows={8}
                    label="Describe your symptoms"
                    placeholder="E.g., I have been experiencing chest pain, shortness of breath, and fatigue for the past 3 days..."
                    value={symptoms}
                    onChange={(e) => setSymptoms(e.target.value)}
                  />
                )}

                {(activeTab === 1 || activeTab === 2 || activeTab === 3 || activeTab === 4) && (
                  <Box
                    {...getRootProps()}
                    sx={{
                      border: '2px dashed',
                      borderColor: 'primary.main',
                      borderRadius: 2,
                      p: 4,
                      textAlign: 'center',
                      cursor: 'pointer',
                      '&:hover': {
                        backgroundColor: 'action.hover',
                      },
                    }}
                  >
                    <input {...getInputProps()} />
                    <CloudUpload sx={{ fontSize: 60, color: 'primary.main', mb: 2 }} />
                    <Typography variant="h6" gutterBottom>
                      Drag & drop files here, or click to select
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      Supported: Images (JPG, PNG), PDFs, Audio (MP3, WAV)
                    </Typography>
                  </Box>
                )}

                {uploadedFiles.length > 0 && (
                  <Box sx={{ mt: 2 }}>
                    <Typography variant="subtitle2" gutterBottom>
                      Uploaded Files:
                    </Typography>
                    {uploadedFiles.map((file, index) => (
                      <Chip
                        key={index}
                        label={file.name}
                        onDelete={() => setUploadedFiles(uploadedFiles.filter((_, i) => i !== index))}
                        sx={{ mr: 1, mb: 1 }}
                      />
                    ))}
                  </Box>
                )}

                {error && (
                  <Alert severity="error" sx={{ mt: 3 }}>
                    {error}
                  </Alert>
                )}

                <Button
                  variant="contained"
                  size="large"
                  fullWidth
                  onClick={handleSubmit}
                  disabled={loading || (!symptoms && uploadedFiles.length === 0)}
                  sx={{ mt: 3 }}
                >
                  {loading ? <CircularProgress size={24} /> : 'Analyze with AI'}
                </Button>
              </CardContent>
            </Card>
          </Grid>

          {/* Results Section */}
          <Grid item xs={12} md={4}>
            <Card elevation={3}>
              <CardContent sx={{ p: 3 }}>
                <Typography variant="h6" sx={{ fontWeight: 600, mb: 2 }}>
                  Diagnosis Result
                </Typography>

                {loading && (
                  <Box sx={{ textAlign: 'center', py: 4 }}>
                    <CircularProgress />
                    <Typography variant="body2" color="text.secondary" sx={{ mt: 2 }}>
                      Analyzing your data...
                    </Typography>
                  </Box>
                )}

                {result && (
                  <Box>
                    <Box sx={{ mb: 3 }}>
                      <Typography variant="subtitle2" color="text.secondary" gutterBottom>
                        Primary Diagnosis
                      </Typography>
                      <Typography variant="h6" sx={{ fontWeight: 600 }}>
                        {result.primary_diagnosis}
                      </Typography>
                    </Box>

                    <Box sx={{ mb: 3 }}>
                      <Typography variant="subtitle2" color="text.secondary" gutterBottom>
                        Confidence
                      </Typography>
                      <LinearProgress
                        variant="determinate"
                        value={result.confidence * 100}
                        sx={{ height: 10, borderRadius: 5, mb: 1 }}
                      />
                      <Typography variant="body2">{(result.confidence * 100).toFixed(1)}%</Typography>
                    </Box>

                    <Box sx={{ mb: 3 }}>
                      <Typography variant="subtitle2" color="text.secondary" gutterBottom>
                        Severity
                      </Typography>
                      <Chip label={result.severity} color={getSeverityColor(result.severity)} />
                    </Box>

                    <Box sx={{ mb: 3 }}>
                      <Typography variant="subtitle2" color="text.secondary" gutterBottom>
                        Organ System
                      </Typography>
                      <Typography variant="body2">{result.organ_system}</Typography>
                    </Box>

                    {result.treatment_recommendations && (
                      <Box>
                        <Typography variant="subtitle2" color="text.secondary" gutterBottom>
                          Recommendations
                        </Typography>
                        <Typography variant="body2">{result.treatment_recommendations}</Typography>
                      </Box>
                    )}

                    <Button variant="outlined" fullWidth sx={{ mt: 3 }}>
                      View AI Insights
                    </Button>
                    <Button variant="outlined" fullWidth sx={{ mt: 1 }}>
                      Find Nearby Hospitals
                    </Button>
                  </Box>
                )}

                {!loading && !result && (
                  <Typography variant="body2" color="text.secondary" sx={{ textAlign: 'center', py: 4 }}>
                    Submit your symptoms or upload medical data to get AI-powered diagnosis
                  </Typography>
                )}
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      </Container>
    </Box>
  );
};

export default DiagnosisPage;

