// src/store/slices/authSlice.js
import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import authService from '../../services/authService';

export const login = createAsyncThunk('auth/login', async (credentials, { rejectWithValue }) => {
  try {
    const response = await authService.login(credentials);
    localStorage.setItem('token', response.access_token);
    localStorage.setItem('refreshToken', response.refresh_token);
    // Also fetch user data after login
    const user = await authService.getCurrentUser();
    return { ...response, user };
  } catch (error) {
    return rejectWithValue(error.response?.data?.detail || 'Login failed');
  }
});

export const register = createAsyncThunk('auth/register', async (userData, { rejectWithValue }) => {
  try {
    const response = await authService.register(userData);
    return response;
  } catch (error) {
    return rejectWithValue(error.response?.data?.detail || 'Registration failed');
  }
});

export const logout = createAsyncThunk('auth/logout', async () => {
  await authService.logout();
  localStorage.removeItem('token');
  localStorage.removeItem('refreshToken');
});

export const checkAuth = createAsyncThunk('auth/checkAuth', async (_, { rejectWithValue }) => {
  try {
    const token = localStorage.getItem('token');
    if (!token) throw new Error('No token');
    const user = await authService.getCurrentUser();
    return user;
  } catch (error) {
    return rejectWithValue(error.message);
  }
});

export const updateUser = createAsyncThunk('auth/updateUser', async (userData, { rejectWithValue }) => {
  try {
    const user = await authService.updateUser(userData);
    return user;
  } catch (error) {
    return rejectWithValue(error.response?.data?.detail || 'Failed to update user');
  }
});

const authSlice = createSlice({
  name: 'auth',
  initialState: {
    user: null,
    isAuthenticated: false,
    loading: true,
    error: null,
  },
  reducers: {
    clearError: (state) => {
      state.error = null;
    },
    setUser: (state, action) => {
      state.user = action.payload;
      state.isAuthenticated = true;
    },
  },
  extraReducers: (builder) => {
    builder
      // Login
      .addCase(login.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(login.fulfilled, (state, action) => {
        state.user = action.payload.user;
        state.isAuthenticated = true;
        state.loading = false;
        state.error = null;
      })
      .addCase(login.rejected, (state, action) => {
        state.error = action.payload;
        state.loading = false;
        state.isAuthenticated = false;
      })
      // Register
      .addCase(register.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(register.fulfilled, (state) => {
        state.loading = false;
        state.error = null;
      })
      .addCase(register.rejected, (state, action) => {
        state.error = action.payload;
        state.loading = false;
      })
      // Check Auth
      .addCase(checkAuth.pending, (state) => {
        state.loading = true;
      })
      .addCase(checkAuth.fulfilled, (state, action) => {
        state.user = action.payload;
        state.isAuthenticated = true;
        state.loading = false;
      })
      .addCase(checkAuth.rejected, (state) => {
        state.user = null;
        state.isAuthenticated = false;
        state.loading = false;
      })
      // Logout
      .addCase(logout.fulfilled, (state) => {
        state.user = null;
        state.isAuthenticated = false;
        state.loading = false;
        state.error = null;
      })
      // Update User
      .addCase(updateUser.pending, (state) => {
        state.loading = true;
      })
      .addCase(updateUser.fulfilled, (state, action) => {
        state.user = action.payload;
        state.loading = false;
      })
      .addCase(updateUser.rejected, (state, action) => {
        state.error = action.payload;
        state.loading = false;
      });
  },
});

export const { clearError, setUser } = authSlice.actions;
export default authSlice.reducer;