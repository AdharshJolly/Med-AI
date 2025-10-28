import React, { createContext, useContext, useState, useEffect } from 'react';
import { useUser, useClerk } from '@clerk/clerk-react';
import api from '../services/api';

const AuthContext = createContext();

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider');
  }
  return context;
};

export const AuthProvider = ({ children }) => {
  const { user, isLoaded, isSignedIn } = useUser();
  const { signOut } = useClerk();
  const [userProfile, setUserProfile] = useState(null);
  const [profileLoading, setProfileLoading] = useState(false);
  const [hasCompletedProfile, setHasCompletedProfile] = useState(false);

  useEffect(() => {
    if (isSignedIn && user) {
      fetchUserProfile();
    } else {
      setUserProfile(null);
      setHasCompletedProfile(false);
    }
  }, [isSignedIn, user]);

  const fetchUserProfile = async () => {
    try {
      setProfileLoading(true);
      const response = await api.get(`/api/profile/${user.id}`);
      setUserProfile(response.data);
      setHasCompletedProfile(true);
    } catch (error) {
      if (error.response?.status === 404) {
        setHasCompletedProfile(false);
      } else {
        console.error('Error fetching profile:', error);
      }
    } finally {
      setProfileLoading(false);
    }
  };

  const createProfile = async (profileData) => {
    try {
      const response = await api.post('/api/profile/create', {
        ...profileData,
        clerk_user_id: user.id,
        email: user.primaryEmailAddress?.emailAddress,
      });
      setUserProfile(response.data.profile);
      setHasCompletedProfile(true);
      return response.data;
    } catch (error) {
      console.error('Error creating profile:', error);
      throw error;
    }
  };

  const updateProfile = async (profileData) => {
    try {
      const response = await api.put('/api/profile/update', {
        ...profileData,
        clerk_user_id: user.id,
      });
      setUserProfile(response.data.profile);
      return response.data;
    } catch (error) {
      console.error('Error updating profile:', error);
      throw error;
    }
  };

  const logout = async () => {
    await signOut();
    setUserProfile(null);
    setHasCompletedProfile(false);
  };

  const value = {
    user,
    isLoaded,
    isSignedIn,
    userProfile,
    profileLoading,
    hasCompletedProfile,
    createProfile,
    updateProfile,
    fetchUserProfile,
    logout,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

