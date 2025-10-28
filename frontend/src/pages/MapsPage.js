import React, { useState, useEffect } from 'react';
import { Box, Container, Typography, Card, CardContent, TextField, Button, Grid, List, ListItem, ListItemText, Chip } from '@mui/material';
import { GoogleMap, LoadScript, Marker } from '@react-google-maps/api';
import { Search, MyLocation } from '@mui/icons-material';
import { getNearbyFacilities } from '../services/api';

const MapsPage = () => {
  const [userLocation, setUserLocation] = useState(null);
  const [facilities, setFacilities] = useState([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [loading, setLoading] = useState(false);

  const mapContainerStyle = {
    width: '100%',
    height: '500px',
  };

  const defaultCenter = {
    lat: 12.9716,
    lng: 77.5946, // Bangalore
  };

  useEffect(() => {
    getUserLocation();
  }, []);

  const getUserLocation = () => {
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        (position) => {
          const location = {
            lat: position.coords.latitude,
            lng: position.coords.longitude,
          };
          setUserLocation(location);
          searchNearbyFacilities(location);
        },
        (error) => {
          console.error('Error getting location:', error);
        }
      );
    }
  };

  const searchNearbyFacilities = async (location) => {
    setLoading(true);
    try {
      const response = await getNearbyFacilities(location, 'hospital');
      setFacilities(response.data.facilities || []);
    } catch (error) {
      console.error('Error fetching facilities:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Box sx={{ minHeight: '100vh', backgroundColor: 'background.default', py: 4 }}>
      <Container maxWidth="xl">
        <Typography variant="h3" sx={{ fontWeight: 700, mb: 2 }}>
          Find Nearby Hospitals
        </Typography>
        <Typography variant="h6" color="text.secondary" sx={{ mb: 4 }}>
          Locate healthcare facilities near you
        </Typography>

        <Grid container spacing={4}>
          <Grid item xs={12} md={8}>
            <Card elevation={3}>
              <LoadScript googleMapsApiKey={process.env.REACT_APP_GOOGLE_MAPS_API_KEY || ''}>
                <GoogleMap
                  mapContainerStyle={mapContainerStyle}
                  center={userLocation || defaultCenter}
                  zoom={13}
                >
                  {userLocation && <Marker position={userLocation} label="You" />}
                  {facilities.map((facility, index) => (
                    <Marker
                      key={index}
                      position={{ lat: facility.lat, lng: facility.lng }}
                      label={facility.name}
                    />
                  ))}
                </GoogleMap>
              </LoadScript>
            </Card>
          </Grid>

          <Grid item xs={12} md={4}>
            <Card elevation={3}>
              <CardContent>
                <Typography variant="h6" sx={{ fontWeight: 600, mb: 2 }}>
                  Search Facilities
                </Typography>
                <TextField
                  fullWidth
                  placeholder="Search hospitals, clinics..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  sx={{ mb: 2 }}
                />
                <Button
                  variant="contained"
                  fullWidth
                  startIcon={<Search />}
                  onClick={() => searchNearbyFacilities(userLocation)}
                  disabled={loading}
                >
                  Search
                </Button>
                <Button
                  variant="outlined"
                  fullWidth
                  startIcon={<MyLocation />}
                  onClick={getUserLocation}
                  sx={{ mt: 1 }}
                >
                  Use My Location
                </Button>

                <Typography variant="subtitle2" sx={{ mt: 3, mb: 1 }}>
                  Nearby Facilities ({facilities.length})
                </Typography>
                <List>
                  {facilities.map((facility, index) => (
                    <ListItem key={index} divider>
                      <ListItemText
                        primary={facility.name}
                        secondary={`${facility.distance} km away`}
                      />
                      <Chip label={facility.type} size="small" />
                    </ListItem>
                  ))}
                </List>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      </Container>
    </Box>
  );
};

export default MapsPage;

