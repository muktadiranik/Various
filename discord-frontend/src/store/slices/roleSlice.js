// src/store/slices/roleSlice.js
import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import roleService from '../../services/roleService';

export const fetchRoles = createAsyncThunk('roles/fetch', async (guildId, { rejectWithValue }) => {
  try {
    return await roleService.getGuildRoles(guildId);
  } catch (error) {
    return rejectWithValue(error.response?.data?.detail || 'Failed to fetch roles');
  }
});

export const createRole = createAsyncThunk('roles/create', async ({ guildId, roleData }, { rejectWithValue }) => {
  try {
    return await roleService.createRole(guildId, roleData);
  } catch (error) {
    return rejectWithValue(error.response?.data?.detail || 'Failed to create role');
  }
});

export const updateRole = createAsyncThunk('roles/update', async ({ roleId, roleData }, { rejectWithValue }) => {
  try {
    return await roleService.updateRole(roleId, roleData);
  } catch (error) {
    return rejectWithValue(error.response?.data?.detail || 'Failed to update role');
  }
});

export const deleteRole = createAsyncThunk('roles/delete', async (roleId, { rejectWithValue }) => {
  try {
    await roleService.deleteRole(roleId);
    return roleId;
  } catch (error) {
    return rejectWithValue(error.response?.data?.detail || 'Failed to delete role');
  }
});

export const assignRole = createAsyncThunk('roles/assign', async ({ guildId, userId, roleId }, { rejectWithValue }) => {
  try {
    await roleService.assignRole(guildId, userId, roleId);
    return { userId, roleId };
  } catch (error) {
    return rejectWithValue(error.response?.data?.detail || 'Failed to assign role');
  }
});

export const removeRole = createAsyncThunk('roles/remove', async ({ guildId, userId, roleId }, { rejectWithValue }) => {
  try {
    await roleService.removeRole(guildId, userId, roleId);
    return { userId, roleId };
  } catch (error) {
    return rejectWithValue(error.response?.data?.detail || 'Failed to remove role');
  }
});

export const fetchUserRoles = createAsyncThunk('roles/fetchUserRoles', async ({ guildId, userId }, { rejectWithValue }) => {
  try {
    return await roleService.getUserRoles(guildId, userId);
  } catch (error) {
    return rejectWithValue(error.response?.data?.detail || 'Failed to fetch user roles');
  }
});

const roleSlice = createSlice({
  name: 'roles',
  initialState: {
    list: [],
    userRoles: {},
    loading: false,
    error: null,
  },
  reducers: {
    clearError: (state) => {
      state.error = null;
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(fetchRoles.pending, (state) => {
        state.loading = true;
      })
      .addCase(fetchRoles.fulfilled, (state, action) => {
        state.list = action.payload;
        state.loading = false;
      })
      .addCase(fetchRoles.rejected, (state, action) => {
        state.error = action.payload;
        state.loading = false;
      })
      .addCase(createRole.fulfilled, (state, action) => {
        state.list.push(action.payload);
      })
      .addCase(updateRole.fulfilled, (state, action) => {
        const index = state.list.findIndex(r => r.id === action.payload.id);
        if (index !== -1) state.list[index] = action.payload;
      })
      .addCase(deleteRole.fulfilled, (state, action) => {
        state.list = state.list.filter(r => r.id !== action.payload);
      })
      .addCase(assignRole.fulfilled, (state, action) => {
        // Update will be handled by refetching
      })
      .addCase(removeRole.fulfilled, (state, action) => {
        // Update will be handled by refetching
      })
      .addCase(fetchUserRoles.fulfilled, (state, action) => {
        const { userId, roles } = action.meta.arg;
        state.userRoles[userId] = roles;
      });
  },
});

export const { clearError } = roleSlice.actions;
export default roleSlice.reducer;