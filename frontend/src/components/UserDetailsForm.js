import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Box,
  Container,
  Paper,
  Typography,
  TextField,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Button,
  Checkbox,
  FormControlLabel,
  FormHelperText,
  Grid,
  LinearProgress,
  Alert,
  Stepper,
  Step,
  StepLabel,
} from '@mui/material';
import { CheckCircle, LocalHospital } from '@mui/icons-material';
import { useAuth } from '../context/AuthContext';
import { useUser } from '@clerk/clerk-react';

const UserDetailsForm = () => {
  const { user } = useUser();
  const { createProfile } = useAuth();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [activeStep, setActiveStep] = useState(0);

  const [formData, setFormData] = useState({
    name: user?.fullName || '',
    age: '',
    gender: '',
    blood_group: '',
    height: '',
    weight: '',
    previous_medical_records: '',
    present_medications: '',
    allergies: '',
    family_history: '',
    terms_accepted: false,
    disclaimer_accepted: false,
  });

  const [errors, setErrors] = useState({});

  const steps = ['Personal Information', 'Medical Details', 'Terms & Conditions'];

  const bloodGroups = ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-'];
  const genders = ['Male', 'Female', 'Other', 'Prefer not to say'];

  const handleChange = (e) => {
    const { name, value, checked, type } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value,
    }));
    // Clear error for this field
    if (errors[name]) {
      setErrors((prev) => ({ ...prev, [name]: '' }));
    }
  };

  const validateStep = (step) => {
    const newErrors = {};

    if (step === 0) {
      if (!formData.name.trim()) newErrors.name = 'Name is required';
      if (!formData.age || formData.age < 1 || formData.age > 120) {
        newErrors.age = 'Please enter a valid age (1-120)';
      }
      if (!formData.gender) newErrors.gender = 'Gender is required';
    }

    if (step === 1) {
      if (!formData.blood_group) newErrors.blood_group = 'Blood group is required';
      if (!formData.height || formData.height < 50 || formData.height > 250) {
        newErrors.height = 'Please enter a valid height in cm (50-250)';
      }
      if (!formData.weight || formData.weight < 10 || formData.weight > 300) {
        newErrors.weight = 'Please enter a valid weight in kg (10-300)';
      }
    }

    if (step === 2) {
      if (!formData.terms_accepted) {
        newErrors.terms_accepted = 'You must accept the Terms and Conditions';
      }
      if (!formData.disclaimer_accepted) {
        newErrors.disclaimer_accepted = 'You must acknowledge the medical disclaimer';
      }
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleNext = () => {
    if (validateStep(activeStep)) {
      setActiveStep((prev) => prev + 1);
    }
  };

  const handleBack = () => {
    setActiveStep((prev) => prev - 1);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!validateStep(2)) {
      return;
    }

    setLoading(true);
    setError('');

    try {
      await createProfile(formData);
      navigate('/home');
    } catch (err) {
      setError(err.response?.data?.message || 'Failed to create profile. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const renderStepContent = (step) => {
    switch (step) {
      case 0:
        return (
          <Grid container spacing={3}>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Full Name"
                name="name"
                value={formData.name}
                onChange={handleChange}
                error={!!errors.name}
                helperText={errors.name}
                required
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Age"
                name="age"
                type="number"
                value={formData.age}
                onChange={handleChange}
                error={!!errors.age}
                helperText={errors.age}
                required
                inputProps={{ min: 1, max: 120 }}
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <FormControl fullWidth error={!!errors.gender} required>
                <InputLabel>Gender</InputLabel>
                <Select name="gender" value={formData.gender} onChange={handleChange} label="Gender">
                  {genders.map((gender) => (
                    <MenuItem key={gender} value={gender}>
                      {gender}
                    </MenuItem>
                  ))}
                </Select>
                {errors.gender && <FormHelperText>{errors.gender}</FormHelperText>}
              </FormControl>
            </Grid>
          </Grid>
        );

      case 1:
        return (
          <Grid container spacing={3}>
            <Grid item xs={12} sm={4}>
              <FormControl fullWidth error={!!errors.blood_group} required>
                <InputLabel>Blood Group</InputLabel>
                <Select
                  name="blood_group"
                  value={formData.blood_group}
                  onChange={handleChange}
                  label="Blood Group"
                >
                  {bloodGroups.map((group) => (
                    <MenuItem key={group} value={group}>
                      {group}
                    </MenuItem>
                  ))}
                </Select>
                {errors.blood_group && <FormHelperText>{errors.blood_group}</FormHelperText>}
              </FormControl>
            </Grid>
            <Grid item xs={12} sm={4}>
              <TextField
                fullWidth
                label="Height (cm)"
                name="height"
                type="number"
                value={formData.height}
                onChange={handleChange}
                error={!!errors.height}
                helperText={errors.height}
                required
                inputProps={{ min: 50, max: 250 }}
              />
            </Grid>
            <Grid item xs={12} sm={4}>
              <TextField
                fullWidth
                label="Weight (kg)"
                name="weight"
                type="number"
                value={formData.weight}
                onChange={handleChange}
                error={!!errors.weight}
                helperText={errors.weight}
                required
                inputProps={{ min: 10, max: 300 }}
              />
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Previous Medical Records"
                name="previous_medical_records"
                value={formData.previous_medical_records}
                onChange={handleChange}
                multiline
                rows={3}
                placeholder="List any past surgeries, chronic conditions, hospitalizations..."
              />
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Present Medications"
                name="present_medications"
                value={formData.present_medications}
                onChange={handleChange}
                multiline
                rows={2}
                placeholder="List current medications with dosage..."
              />
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Allergies"
                name="allergies"
                value={formData.allergies}
                onChange={handleChange}
                multiline
                rows={2}
                placeholder="List any known allergies (medications, food, environmental)..."
              />
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Family Medical History"
                name="family_history"
                value={formData.family_history}
                onChange={handleChange}
                multiline
                rows={2}
                placeholder="List any hereditary conditions or family medical history..."
              />
            </Grid>
          </Grid>
        );

      case 2:
        return (
          <Box>
            <Alert severity="info" sx={{ mb: 3 }}>
              <Typography variant="body2">
                Please read and accept the following terms to continue using MedAI-Pro.
              </Typography>
            </Alert>

            <Paper
              variant="outlined"
              sx={{
                p: 3,
                mb: 2,
                backgroundColor: errors.terms_accepted ? 'error.light' : 'background.paper',
                border: errors.terms_accepted ? '2px solid' : '1px solid',
                borderColor: errors.terms_accepted ? 'error.main' : 'divider',
              }}
            >
              <FormControlLabel
                control={
                  <Checkbox
                    name="terms_accepted"
                    checked={formData.terms_accepted}
                    onChange={handleChange}
                    color="primary"
                  />
                }
                label={
                  <Typography variant="body1" sx={{ fontWeight: 500 }}>
                    I agree to the Terms and Conditions and am aware of the risks associated with
                    using this AI-powered medical application
                  </Typography>
                }
              />
              {errors.terms_accepted && (
                <FormHelperText error sx={{ ml: 4 }}>
                  {errors.terms_accepted}
                </FormHelperText>
              )}
            </Paper>

            <Paper
              variant="outlined"
              sx={{
                p: 3,
                backgroundColor: errors.disclaimer_accepted ? 'error.light' : 'background.paper',
                border: errors.disclaimer_accepted ? '2px solid' : '1px solid',
                borderColor: errors.disclaimer_accepted ? 'error.main' : 'divider',
              }}
            >
              <FormControlLabel
                control={
                  <Checkbox
                    name="disclaimer_accepted"
                    checked={formData.disclaimer_accepted}
                    onChange={handleChange}
                    color="primary"
                  />
                }
                label={
                  <Typography variant="body1" sx={{ fontWeight: 500 }}>
                    I AM AWARE THAT THIS IS AN AI DISEASE PREDICTION APPLICATION AND IF ANYTHING
                    SEVERE WITH MY HEALTH CONDITION I WILL MEET A DOCTOR AND THIS APPLICATION IS NOT
                    RESPONSIBLE FOR THAT
                  </Typography>
                }
              />
              {errors.disclaimer_accepted && (
                <FormHelperText error sx={{ ml: 4 }}>
                  {errors.disclaimer_accepted}
                </FormHelperText>
              )}
            </Paper>
          </Box>
        );

      default:
        return null;
    }
  };

  return (
    <Box
      sx={{
        minHeight: '100vh',
        display: 'flex',
        alignItems: 'center',
        py: 4,
        backgroundColor: 'background.default',
      }}
    >
      <Container maxWidth="md">
        <Paper elevation={3} sx={{ p: 4 }}>
          {/* Header */}
          <Box sx={{ textAlign: 'center', mb: 4 }}>
            <LocalHospital sx={{ fontSize: 60, color: 'primary.main', mb: 2 }} />
            <Typography variant="h4" gutterBottom sx={{ fontWeight: 700 }}>
              Complete Your Medical Profile
            </Typography>
            <Typography variant="body1" color="text.secondary">
              Help us personalize your healthcare experience
            </Typography>
          </Box>

          {/* Stepper */}
          <Stepper activeStep={activeStep} sx={{ mb: 4 }}>
            {steps.map((label) => (
              <Step key={label}>
                <StepLabel>{label}</StepLabel>
              </Step>
            ))}
          </Stepper>

          {/* Error Alert */}
          {error && (
            <Alert severity="error" sx={{ mb: 3 }}>
              {error}
            </Alert>
          )}

          {/* Form */}
          <form onSubmit={handleSubmit}>
            {renderStepContent(activeStep)}

            {/* Navigation Buttons */}
            <Box sx={{ display: 'flex', justifyContent: 'space-between', mt: 4 }}>
              <Button disabled={activeStep === 0 || loading} onClick={handleBack}>
                Back
              </Button>
              <Box sx={{ display: 'flex', gap: 2 }}>
                {activeStep < steps.length - 1 ? (
                  <Button variant="contained" onClick={handleNext} disabled={loading}>
                    Next
                  </Button>
                ) : (
                  <Button
                    type="submit"
                    variant="contained"
                    disabled={loading || !formData.terms_accepted || !formData.disclaimer_accepted}
                    startIcon={loading ? null : <CheckCircle />}
                  >
                    {loading ? 'Creating Profile...' : 'Complete Profile'}
                  </Button>
                )}
              </Box>
            </Box>

            {loading && <LinearProgress sx={{ mt: 2 }} />}
          </form>
        </Paper>
      </Container>
    </Box>
  );
};

export default UserDetailsForm;

