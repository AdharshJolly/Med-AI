import React, { useState, useEffect } from 'react';
import { useUser } from '@clerk/clerk-react';
import { Box, Container, Typography, Card, CardContent, Tabs, Tab, TextField, Button, Grid, Avatar } from '@mui/material';
import { Person, MedicalServices, Settings, Save } from '@mui/icons-material';
import { getUserProfile, updateUserProfile } from '../services/api';

const ProfilePage = () => {
  const { user } = useUser();
  const [activeTab, setActiveTab] = useState(0);
  const [profile, setProfile] = useState(null);
  const [formData, setFormData] = useState({
    name: '',
    age: '',
    gender: '',
    blood_group: '',
    height: '',
    weight: '',
    previous_medical_records: '',
    present_medications: '',
    allergies: '',
    family_history: '',
  });

  useEffect(() => {
    fetchProfile();
  }, []);

  const fetchProfile = async () => {
    try {
      const response = await getUserProfile(user.id);
      setProfile(response.data);
      setFormData(response.data);
    } catch (error) {
      console.error('Error fetching profile:', error);
    }
  };

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSave = async () => {
    try {
      await updateUserProfile(formData);
      alert('Profile updated successfully!');
    } catch (error) {
      console.error('Error updating profile:', error);
      alert('Failed to update profile');
    }
  };

  return (
    <Box sx={{ minHeight: '100vh', backgroundColor: 'background.default', py: 4 }}>
      <Container maxWidth="lg">
        <Card elevation={3} sx={{ mb: 4 }}>
          <CardContent sx={{ display: 'flex', alignItems: 'center', p: 4 }}>
            <Avatar sx={{ width: 100, height: 100, mr: 3, fontSize: '2.5rem' }}>
              {user?.firstName?.[0]}
            </Avatar>
            <Box>
              <Typography variant="h4" sx={{ fontWeight: 700 }}>
                {user?.fullName}
              </Typography>
              <Typography variant="body1" color="text.secondary">
                {user?.primaryEmailAddress?.emailAddress}
              </Typography>
            </Box>
          </CardContent>
        </Card>

        <Card elevation={3}>
          <Tabs value={activeTab} onChange={(e, v) => setActiveTab(v)} sx={{ borderBottom: 1, borderColor: 'divider' }}>
            <Tab label="Personal Info" icon={<Person />} />
            <Tab label="Medical History" icon={<MedicalServices />} />
            <Tab label="Settings" icon={<Settings />} />
          </Tabs>

          <CardContent sx={{ p: 4 }}>
            {activeTab === 0 && (
              <Grid container spacing={3}>
                <Grid item xs={12} sm={6}>
                  <TextField fullWidth label="Name" name="name" value={formData.name} onChange={handleChange} />
                </Grid>
                <Grid item xs={12} sm={6}>
                  <TextField fullWidth label="Age" name="age" type="number" value={formData.age} onChange={handleChange} />
                </Grid>
                <Grid item xs={12} sm={6}>
                  <TextField fullWidth label="Gender" name="gender" value={formData.gender} onChange={handleChange} />
                </Grid>
                <Grid item xs={12} sm={6}>
                  <TextField fullWidth label="Blood Group" name="blood_group" value={formData.blood_group} onChange={handleChange} />
                </Grid>
                <Grid item xs={12} sm={6}>
                  <TextField fullWidth label="Height (cm)" name="height" type="number" value={formData.height} onChange={handleChange} />
                </Grid>
                <Grid item xs={12} sm={6}>
                  <TextField fullWidth label="Weight (kg)" name="weight" type="number" value={formData.weight} onChange={handleChange} />
                </Grid>
              </Grid>
            )}

            {activeTab === 1 && (
              <Grid container spacing={3}>
                <Grid item xs={12}>
                  <TextField
                    fullWidth
                    label="Previous Medical Records"
                    name="previous_medical_records"
                    value={formData.previous_medical_records}
                    onChange={handleChange}
                    multiline
                    rows={4}
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
                    rows={3}
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
                  />
                </Grid>
                <Grid item xs={12}>
                  <TextField
                    fullWidth
                    label="Family History"
                    name="family_history"
                    value={formData.family_history}
                    onChange={handleChange}
                    multiline
                    rows={3}
                  />
                </Grid>
              </Grid>
            )}

            {activeTab === 2 && (
              <Box>
                <Typography variant="h6" gutterBottom>
                  Account Settings
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Manage your account settings and preferences here.
                </Typography>
              </Box>
            )}

            <Button variant="contained" startIcon={<Save />} onClick={handleSave} sx={{ mt: 3 }}>
              Save Changes
            </Button>
          </CardContent>
        </Card>
      </Container>
    </Box>
  );
};

export default ProfilePage;

